############################################################################
# Copyright (c) 2016-2018 Libelium Comunicaciones Distribuidas S.L.        #
#                                                                          #
# This program and the accompanying materials are made                     #
# available under the terms of the Eclipse Public License 2.0              #
# which is available at https://www.eclipse.org/legal/epl-2.0/             #
#                                                                          #
# SPDX-License-Identifier: EPL-2.0                                         #
#                                                                          #
# Contributors:                                                            #
#    David Palomares - Initial API and implementation                      #
############################################################################


"""
AGILE Serial Bus.

Description: Class to implement Hotswap: XBee 802.15.4, Zigbee and LoRaWAN
Author: Jorge Learte <j.learte@libelium.com>
Version: 0.1
Date: Nov 2018
"""

# --- Imports -----------
from agile_makers_shield.utils import observer
from agile_makers_shield.buses.i2c import atmega
from agile_makers_shield.buses.serial import interruptions
from agile_makers_shield.buses.dbus import constants as db_cons
import time
import dbus
import logging
# -----------------------

BUS_NAME = "iot.agile.Protocol"
OBJ_PATH = "/iot/agile/Protocol"


# Interrupts
INT_UART_0 = 0b0001
INT_UART_1 = 0b0010
INT_BUTTON_0 = 0b0100
INT_BUTTON_1 = 0b1000

# Serial communication
DEFAULT_BAUDRATE = atmega.UART_BAUD_9600
DEFAULT_DATABITS = atmega.UART_DATABITS_8
DEFAULT_STOPBITS = atmega.UART_STOPBITS_1
DEFAULT_PARITY = atmega.UART_PARITY_NONE
DEFAULT_TIMEOUT = 2

# Configuration parameters: baudrates
baudrates = [atmega.UART_BAUD_115200,atmega.UART_BAUD_9600, atmega.UART_BAUD_57600, atmega.UART_BAUD_38400, atmega.UART_BAUD_19200, atmega.UART_BAUD_4800, atmega.UART_BAUD_2400, atmega.UART_BAUD_1800, atmega.UART_BAUD_1200,atmega.UART_BAUD_600]

# AT, XBee and LoRaWAN commands for detection
XBee_DATA = bytes([0x7E, 0x00, 0x04, 0x08, 0x01, 0x56, 0x52, 0x4E])
LoRaWAN_DATA = bytes("sys get ver\r\n", 'utf-8')
AT_ST = bytes("+++", 'utf-8')
AT = bytes("AT\r\n", 'utf-8')
AT_API2 = bytes("ATBD3,AP2,WR,CN\r\n", 'utf-8')

class Timeout():
    """Class to control timeouts."""
    def __init__(self, timeout=DEFAULT_TIMEOUT, raises_timeout=False):
        """Init method."""
        self._timeout = timeout
        self._raises_timeout = raises_timeout
        self._limit = time.time() + self._timeout

    def check(self):
        """Raise a timeout exception if time limit has passed."""
        if time.time() > self._limit:
            if self._raises_timeout:
                raise SerialTimeoutException()
            return True
        return False

class Signal(dbus.service.Object):
    def __init__(self, object_path):
        dbus.service.Object.__init__(self, dbus.SessionBus(), object_path)
        self._logger = logging.getLogger(db_cons.LOGGER_NAME)
            
    @dbus.service.signal(dbus_interface = BUS_NAME)
    def SignalSend(self,baudrate, stopbits, databits, parity):
        self._logger.info("Signal emitted!")

class Button(observer.Observer):
        def __init__(self, port=None, baudrate=DEFAULT_BAUDRATE,
                databits=DEFAULT_DATABITS, stopbits=DEFAULT_STOPBITS,
                parity=DEFAULT_PARITY, timeout=DEFAULT_TIMEOUT,
                raises_timeout=False):
                """Init method."""
                self._atmega = atmega.ATMega()
                self._logger = logging.getLogger(db_cons.LOGGER_NAME)
                self._socket = port
                self.baudrate = 0
                self.databits = databits
                self.stopbits = stopbits
                self.parity = parity
                self.timeout = timeout
                self.raises_timeout = raises_timeout
                self._open = False
                self._buffer = []
                ''' Configuration of the interruptions '''
                self._interrupts = 0
                self._interrupts = interruptions.INT_BUTTON_0 | interruptions.INT_BUTTON_1
                self._interruptions = interruptions.Interruptions()
                self._interruptions.register(self)
                self._sXBee802 = None
                self._sZigbee = None
                self._sLW = None
                self._logger.debug("Button's interruptions are configured")

        @property
        def port(self):
                """Return the serial port."""
                return self._socket

        def update(self):
                """Override observer.update method."""
                if (self._interruptions._int == INT_BUTTON_0):
                    self._socket = atmega.SOCKET_0
                elif (self._interruptions._int == INT_BUTTON_1):
                    self._socket = atmega.SOCKET_1
                self._logger.debug("Interruption in button " + str(self._socket) + " detected")
                
                if self._open:
                    self._logger.debug("Socket already open. Closing...")
                    self.close()
                
                for baudrate in baudrates:
                    self.baudrate = baudrate
                    self._logger.info("Baudrate: "+str(self.baudrate))
                   
                    start_time = time.time()
                    self.open()
                    time.sleep(0.1)
                    
                    # Send AT command:
                    data_tx = self._atmega.sendData(self._socket, list(AT_ST))
                    time.sleep(1)        
                    data_AT = self._atmega.getData(self._socket)
                    data_AT = ''.join(str(chr(e)) for e in data_AT)
                    self._logger.debug("Sent data:" + str(AT_ST) + " / Received data:" + str(data_AT))
                    # Detection of LoRaWAN:
                    if ("RN2483" in data_AT)|("RN2903" in data_AT):
                        self._logger.info("LoRaWAN detected")
                        if self._sLW is None:
                                self._sLW = Signal(OBJ_PATH + '/LoRaWAN/SOCKET_' + str(self._socket))
                        self._sLW.SignalSend(self.baudrate, self.databits, self.stopbits, self.parity)
                        return
                        
                    time.sleep(0.1)
                    self._atmega.sendData(self._socket, list(AT))
                    time.sleep(0.1)        
                    data_AT = self._atmega.getData(self._socket)
                    data_AT = ''.join(str(chr(e)) for e in data_AT)
                    self._logger.debug("Sent data:" + str(AT) + " / Received data:" + str(data_AT))
                    
                    # Detection of XBee 802.15.4 or Zigbee:
                    if ("OK" in data_AT):
                        if(self.xbeeSelection() == 0):
                                self.close()    
                                time.sleep(0.1)  
                                self.open()
                                time.sleep(0.1)
                                # AT command to change API0->API2
                                data_tx = self._atmega.sendData(self._socket, list(AT_ST))
                                time.sleep(1)        
                                data_AT = self._atmega.getData(self._socket)
                                data_AT = ''.join(str(chr(e)) for e in data_AT)
                                time.sleep(0.1)
                                self._atmega.sendData(self._socket, list(AT_API2))
                                time.sleep(0.1)        
                                data_AT = self._atmega.getData(self._socket)
                                data_AT = ''.join(str(chr(e)) for e in data_AT)
                                self._logger.debug("Sent data:" + str(AT_API2) + " / Received data:" + str(data_AT))
                                self.baudrate = atmega.UART_BAUD_9600
                                if(self.xbeeSelection() == 1): return
                        else: return
                    self.close()    
                    time.sleep(0.1)      
                   
                self._logger.info("No module detected in socket " + str(self._socket))
                if self._open:
                    self.close()
                self._logger.info("Socket closed.")
        
        def xbeeSelection(self):
                self.close()
                time.sleep(0.1)
                self.open()
                data = self._atmega.getData(self._socket)
                time.sleep(0.1)
                data_tx = self._atmega.sendData(self._socket, list(XBee_DATA))
                time.sleep(0.1)
                data = ""        
                data = self._atmega.getData(self._socket)
                data_hex = ''.join(hex(i) for i in data)
                self._logger.debug("Sent data:" + str(XBee_DATA) + " / Received data:" + str(data_hex))          
                if(len(data)>=9):
                        data = data[max(loc for loc, val in enumerate(data) if val == 126):] 
                        ''' Response should be: 7E00078801565200xxxx '''
                        if ((data[0] == 0x7E) & (data[1] == 0x00) & (data[3] == 0x88)
                           & (data[4] == 0x01) & (data[5] == 0x56)
                           & (data[6] == 0x52) & (data[7]==0x00)):
                            if ((data[8] < 0x20) & (data[9] > 0x80)):
                                    ''' XBee 802.15.4 module'''
                                    self._logger.info("XBee 802.15.4 module detected")
                                    ## Sent signal to DBus Address ##
                                    if self._sXBee802 is None:
                                        self._sXBee802 = Signal(OBJ_PATH + '/XBee_802_15_4/SOCKET_' + str(self._socket))
                                    self._sXBee802.SignalSend(self.baudrate, self.databits, self.stopbits, self.parity)
                                    return 1
                            elif ((data[8] < 0x20) & (data[9] > 0x00)):
                                    ''' XBee 868 - 900 MHz module'''
                                    if self._sZigbee is None:
                                        self._sZigbee = Signal(OBJ_PATH + '/XBee_ZigBee/SOCKET_' + str(self._socket))
                                    self._sZigbee.SignalSend(self.baudrate, self.databits, self.stopbits, self.parity)
                                    self._logger.info("Zigbee module detected")
                                    return 1 
                return 0

        @property
        def attribute(self):
                """Override observer.attribute method."""
                return self._interrupts

        def isOpen(self):
                """Return the status of the serial port."""
                return self._open

        def open(self):
                """Open the serial port."""
                if self._open:
                    raise SerialException(
                        "Socket {} is already open".format(self._socket)
                    )
                self._interruptions.register(self)
                self._interrupts = self._interrupts 
                self._atmega.uartON(self._socket, self.baudrate, self.databits,
                                    self.stopbits, self.parity)
                self._buffer = []
                self._open = True

        def close(self):
                """Close the serial port."""
                if not self._open:
                    raise SerialException(
                        "Socket {} is already closed".format(self._socket)
                    )
                self._atmega.uartOFF(self._socket)
                '''self._interruptions.unregister(self)'''
                self._buffer = []
                self._open = False

        def write(self, data):
                """Write to the serial port."""
                if not self._open:
                    raise SerialException("Socket {} is closed".format(self._socket))
                self._atmega.sendData(self._socket, list(data))

        def read(self, size=1):
                """Read N bytes from the serial port."""
                if not self._open:
                    raise SerialException("Socket {} is closed".format(self._socket))
                data = []
                current_size = size
                timeout = Timeout(self.timeout, self.raises_timeout)
                while (len(data) < current_size):
                    buffer_size = len(self._buffer)
                    if buffer_size >= current_size:
                        data.extend(self._buffer[0:current_size])
                        self._buffer = self._buffer[current_size:]
                        current_size = 0
                    else:
                        data.extend(self._buffer[0:buffer_size])
                        self._buffer = []
                        current_size = current_size - buffer_size
                    if timeout.check() and (len(data) < current_size):
                        break
                return bytes(data)
