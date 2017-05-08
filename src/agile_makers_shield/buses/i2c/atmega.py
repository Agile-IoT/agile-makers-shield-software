
############################################################################
# Copyright (c) 2016, 2017 Libelium Comunicaciones Distribuidas S.L.       #
#                                                                          #
# All rights reserved. This program and the accompanying materials         #
# are made available under the terms of the Eclipse Public License v1.0    #
# and Eclipse Distribution License v1.0 which accompany this distribution. #
#                                                                          #
# The Eclipse Public License is available at                               #
#    http://www.eclipse.org/legal/epl-v10.html                             #
# and the Eclipse Distribution License is available at                     #
#   http://www.eclipse.org/org/documents/edl-v10.php.                      #
#                                                                          #
# Contributors:                                                            #
#    David Palomares - Initial API and implementation                      #
############################################################################

#########################################################
#                  AGILE I2C ATMega                     #
#                                                       #
#    Description: Class to communicate with the ATMega  #
#       in the AGILE Maker's Shield. This allows to     #
#       control several features as the sockets, the    #
#       GPS and the LEDs. Only one instance of this     #
#       class can be created and most of its methods    #
#       will lock the class when transmitting over I2C. #
#    Author: David Palomares <d.palomares@libelium.com> #
#    Version: 0.2                                       #
#    Date: May 2017                                     #
#########################################################

# --- Imports -----------
from agile_makers_shield.buses.i2c import i2c_bus
from agile_makers_shield.utils import singleton
import threading
# -----------------------


# --- Variables ---------
# AT Mega
ATMEGA_ADDRESS = 0x14
ATMEGA_CHECK_BYTE = 0xDA
DUMMY_DATA = [0x00]
# Sockets
SOCKET_0 = 0x00
SOCKET_1 = 0x01
SOCKET_GPS = 0x02
SOCKET_LEDS = 0x03
SOCKETS = [SOCKET_0, SOCKET_1]
SOCKET_SHIFT = 0x04 # Shifts the socket to the high part of the byte
MODE_OFF = 0
MODE_ON = 1
ERROR = []
# I2C Addresses
ATMEGA_CHECK = 0xFF
FIFO_TX = 0x00
FIFO_RX = 0x01
FIFO_AVAILABLE = 0x02
SOCKET_BAUDRATE = 0x06
SOCKET_DATABITS = 0x0A
SOCKET_STOPBITS = 0x0B
SOCKET_PARITY = 0x0C
SOCKET_STATUS = 0x0D
INT_UART = 0x0E
INT_BUTTON = 0x0F
GPS_UPDATE = 0x00
GPS_READ_BUFFER_SIZE = 0x01
GPS_READ_GGA = 0x02
GPS_READ_RMC = 0x03
# LEDs
LED_S0_R = 0x0A
LED_S0_G = 0x0B
LED_S0_B = 0x0C
LED_S1_R = 0x0D
LED_S1_G = 0x0E
LED_S1_B = 0x0F
LED_AUX_2 = 0x02
LED_AUX_3 = 0x03
LED_AUX_4 = 0x04
LED_AUX_2_DIR = 0x02
LED_AUX_3_DIR = 0x03
LED_AUX_4_DIR = 0x04
LEDS_SOCKET_R = { SOCKET_0: LED_S0_R, SOCKET_1: LED_S1_R }
LEDS_SOCKET_G = { SOCKET_0: LED_S0_G, SOCKET_1: LED_S1_G }
LEDS_SOCKET_B = { SOCKET_0: LED_S0_B, SOCKET_1: LED_S1_B }
LEDS_AUX = {
   LED_AUX_2: LED_AUX_2_DIR,
   LED_AUX_3: LED_AUX_3_DIR,
   LED_AUX_4: LED_AUX_4_DIR
}
# UART
UART_BAUD_0 = 0
UART_BAUD_50 = 50
UART_BAUD_75 = 75
UART_BAUD_110 = 110
UART_BAUD_134 = 134
UART_BAUD_150 = 150
UART_BAUD_200 = 200
UART_BAUD_300 = 300
UART_BAUD_600 = 600
UART_BAUD_1200 = 1200
UART_BAUD_1800 = 1800
UART_BAUD_2400 = 2400
UART_BAUD_4800 = 4800
UART_BAUD_9600 = 9600
UART_BAUD_19200 = 19200
UART_BAUD_38400 = 38400
UART_BAUD_57600 = 57600
UART_BAUD_115200 = 115200
UART_BAUD_230400 = 230400
UART_BAUD_460800 = 460800
UART_BAUD_576000 = 576000
UART_BAUD_921600 = 921600
UART_DATABITS_5 = 0x00
UART_DATABITS_6 = 0x02
UART_DATABITS_7 = 0x04
UART_DATABITS_8 = 0x06
UART_STOPBITS_1 = 0x00
UART_STOPBITS_2 = 0x08
UART_PARITY_NONE = 0x00
UART_PARITY_EVEN = 0x20
UART_PARITY_ODD = 0x30
BAUDRATES = {
   UART_BAUD_0: "0",
   UART_BAUD_50: "50",
   UART_BAUD_75: "75",
   UART_BAUD_110: "110",
   UART_BAUD_134: "134",
   UART_BAUD_150: "150",
   UART_BAUD_200: "200",
   UART_BAUD_300: "300",
   UART_BAUD_600: "600",
   UART_BAUD_1200: "1200",
   UART_BAUD_1800: "1800",
   UART_BAUD_2400: "2400",
   UART_BAUD_4800: "4800",
   UART_BAUD_9600: "9600",
   UART_BAUD_19200: "19200",
   UART_BAUD_38400: "38400",
   UART_BAUD_57600: "57600",
   UART_BAUD_115200: "115200",
   UART_BAUD_230400: "230400",
   UART_BAUD_460800: "460800",
   UART_BAUD_576000: "576000",
   UART_BAUD_921600: "921600"
}
DATABITS = {
   UART_DATABITS_5: "5",
   UART_DATABITS_6: "6",
   UART_DATABITS_7: "7",
   UART_DATABITS_8: "8"
}
STOPBITS = {
   UART_STOPBITS_1: "1",
   UART_STOPBITS_2: "2"
}
PARITIES = {
   UART_PARITY_NONE: "none",
   UART_PARITY_EVEN: "even",
   UART_PARITY_ODD: "odd"
}
# -----------------------


# --- Classes -----------
class ATMega(metaclass=singleton.Singleton):
   """Class that implements methods to read from
   and write to the AT Mega via I2C."""

   def __init__(self):
      self._bus = i2c_bus.I2C_Bus(ATMEGA_ADDRESS)
      self._lock = threading.Lock()
      if not self._check:
         raise IOError("Could not connect to the I2C Bus")
      self._gpsBufferSize = self._getGPSBufferSize()

   def lock_decorator(func):
      def lock_wrapper(self, *args, **kwargs):
         result = func(self, *args, **kwargs)
         return result

      return lock_wrapper

   def close(self):
      self._bus.close()

   @lock_decorator
   def _check(self):
      """Checks if the I2C bus is working."""
      reg = ATMEGA_CHECK
      try:
         if self._bus.read(reg, 1)[0] == ATMEGA_CHECK_BYTE:
            return True
      except:
         return False
      return False

   @lock_decorator
   def _getGPSBufferSize(self):
      """Returns the size of the GPS buffer in the ATMega."""
      reg = (SOCKET_GPS << SOCKET_SHIFT) | GPS_READ_BUFFER_SIZE
      return self._bus.read(reg, 1)[0]

   def uartON(self, socket, baudrate=UART_BAUD_9600, databits=UART_DATABITS_8,
         stopbits=UART_STOPBITS_1, parity=UART_PARITY_NONE):
      """Turns on the UART of the specified socket."""
      if not socket in SOCKETS:
         raise ValueError("Wrong socket")
      reg = (socket << SOCKET_SHIFT) | SOCKET_STATUS
      if not self._setBaudrate(socket, baudrate):
         return False
      if not self._setDatabits(socket, databits):
         return False
      if not self._setStopbits(socket, stopbits):
         return False
      if not self._setParity(socket, parity):
         return False
      return self._bus.write(reg, [MODE_ON])

   @lock_decorator
   def uartOFF(self, socket):
      """Turns on the UART of the specified socket."""
      if not socket in SOCKETS:
         raise ValueError("Wrong socket")
      reg = (socket << SOCKET_SHIFT) | SOCKET_STATUS
      return self._bus.write(reg, [MODE_OFF])

   @lock_decorator
   def uartStatus(self, socket):
      """Returns the status of the UART in the specified socket."""
      if not socket in SOCKETS:
         raise ValueError("Wrong socket")
      reg = (socket << SOCKET_SHIFT) | SOCKET_STATUS
      return self._bus.read(reg, 1)[0]

   @lock_decorator
   def sendData(self, socket, data):
      """Sends an array of bytes to the UART of the specified socket."""
      if not socket in SOCKETS:
         raise ValueError("Wrong socket")
      reg = (socket << SOCKET_SHIFT) | FIFO_TX
      return self._bus.write(reg, data)

   @lock_decorator
   def getData(self, socket):
      """Reads all the available bytes of the UART of the specified socket."""
      if not socket in SOCKETS:
         raise ValueError("Wrong socket")
      # Get the available data
      reg = (socket << SOCKET_SHIFT) | FIFO_AVAILABLE
      lengthBytes = self._bus.read(reg, 2)
      if len(lengthBytes) != 2:
         return ERROR
      length = (lengthBytes[0] << 8) | (lengthBytes[1])
      # Read that data
      if length > 0:
         reg = (socket << SOCKET_SHIFT) | FIFO_RX
         return self._bus.read(reg, length)
      return ERROR

   @lock_decorator
   def getBaudrate(self, socket):
      """Returns the baudrate of the UART in the specified socket."""
      if not socket in SOCKETS:
         raise ValueError("Wrong socket")
      reg = (socket << SOCKET_SHIFT) | SOCKET_BAUDRATE
      baud = self._bus.read(reg, 4)
      if len(baud) != 4:
         return 0
      baudrate = (baud[0] << 32) | (baud[1] << 16) | (baud[2] << 8) | (baud[3])
      return baudrate

   @lock_decorator
   def _setBaudrate(self, socket, baudrate):
      """Sets the baudrate of the UART in the specified socket."""
      if not socket in SOCKETS:
         raise ValueError("Wrong socket")
      if not baudrate in BAUDRATES:
         raise ValueError("Wrong baudrate")
      reg = (socket << SOCKET_SHIFT) | SOCKET_BAUDRATE
      baud = [
         (baudrate & 0xFF000000) >> 32,
         (baudrate & 0x00FF0000) >> 16,
         (baudrate & 0x0000FF00) >> 8,
         (baudrate & 0x000000FF)
      ]
      return self._bus.write(reg, baud)

   @lock_decorator
   def getDatabits(self, socket):
      """Returns the databits of the UART in the specified socket."""
      if not socket in SOCKETS:
         raise ValueError("Wrong socket")
      reg = (socket << SOCKET_SHIFT) | SOCKET_DATABITS
      return self._bus.read(reg, 1)[0]

   @lock_decorator
   def _setDatabits(self, socket, databits):
      """Sets the databits of the UART in the specified socket."""
      if not socket in SOCKETS:
         raise ValueError("Wrong socket")
      if not databits in DATABITS:
         raise ValueError("Wrong databits")
      reg = (socket << SOCKET_SHIFT) | SOCKET_DATABITS
      return self._bus.write(reg, [databits])

   @lock_decorator
   def getStopbits(self, socket):
      """Returns the stopbits of the UART in the specified socket."""
      if not socket in SOCKETS:
         raise ValueError("Wrong socket")
      reg = (socket << SOCKET_SHIFT) | SOCKET_STOPBITS
      return self._bus.read(reg, 1)[0]

   @lock_decorator
   def _setStopbits(self, socket, stopbits):
      """Sets the stopbits of the UART in the specified socket."""
      if not socket in SOCKETS:
         raise ValueError("Wrong socket")
      if not stopbits in STOPBITS:
         raise ValueError("Wrong stopbits")
      reg = (socket << SOCKET_SHIFT) | SOCKET_STOPBITS
      return self._bus.write(reg, [stopbits])

   @lock_decorator
   def getParity(self, socket):
      """Returns the parity of the UART in the specified socket."""
      if not socket in SOCKETS:
         raise ValueError("Wrong socket")
      reg = (socket << SOCKET_SHIFT) | SOCKET_PARITY
      return self._bus.read(reg, 1)[0]

   @lock_decorator
   def _setParity(self, socket, parity):
      """Sets the parity of the UART in the specified socket."""
      if not socket in SOCKETS:
         raise ValueError("Wrong socket")
      if not parity in PARITIES:
         raise ValueError("Wrong parity")
      reg = (socket << SOCKET_SHIFT) | SOCKET_PARITY
      return self._bus.write(reg, [parity])

   @lock_decorator
   def getUartInterrupt(self, socket):
      """Returns if the UART of the specified socket has new data."""
      if not socket in SOCKETS:
         raise ValueError("Wrong socket")
      reg = (socket << SOCKET_SHIFT) | INT_UART
      if self._bus.read(reg, 1)[0] == 1:
         return True
      return False

   @lock_decorator
   def getButtonInterrupt(self, socket):
      """Returns if the button of the specified socket was pressed."""
      if not socket in SOCKETS:
         raise ValueError("Wrong socket")
      reg = (socket << SOCKET_SHIFT) | INT_BUTTON
      if self._bus.read(reg, 1)[0] == 1:
         return True
      return False

   @lock_decorator
   def updateGPS(self):
      """Updates the GGA and RMC buffers in the ATMega with the last data."""
      reg = (SOCKET_GPS << SOCKET_SHIFT) | GPS_UPDATE
      if self._bus.write(reg, DUMMY_DATA):
         return True
      return False

   @lock_decorator
   def getGPSGGA(self):
      """Returns the last NMEA GGA sentence stored."""
      reg = (SOCKET_GPS << SOCKET_SHIFT) | GPS_READ_GGA
      return self._bus.read(reg, self._gpsBufferSize)

   @lock_decorator
   def getGPSRMC(self):
      """Returns the last NMEA RMC sentece stored."""
      reg = (SOCKET_GPS << SOCKET_SHIFT) | GPS_READ_RMC
      return self._bus.read(reg, self._gpsBufferSize)

   @lock_decorator
   def getLedSocket(self, socket):
      """Returns the RGB brightness of the specified socket LED."""
      if not socket in SOCKETS:
         raise ValueError("Wrong socket LED")
      reg = (SOCKET_LEDS << SOCKET_SHIFT) | LEDS_SOCKET_R[socket]
      bright_R = self._bus.read(reg, 1)[0]
      reg = (SOCKET_LEDS << SOCKET_SHIFT) | LEDS_SOCKET_G[socket]
      bright_G = self._bus.read(reg, 1)[0]
      reg = (SOCKET_LEDS << SOCKET_SHIFT) | LEDS_SOCKET_B[socket]
      bright_B = self._bus.read(reg, 1)[0]
      return [bright_R, bright_G, bright_B]

   @lock_decorator
   def setLedSocket(self, socket, rgb_bright):
      """Sets the RGB brightness of the specified socket LED."""
      if not socket in SOCKETS:
         raise ValueError("Wrong socket LED")
      if len(rgb_bright) != 3:
         raise ValueError("Expected a list with R, G and B")
      for i, bright in enumerate(rgb_bright):
         rgb_bright[i] = bright & 0xFF
      reg = (SOCKET_LEDS << SOCKET_SHIFT) | LEDS_SOCKET_R[socket]
      if not self._bus.write(reg, [rgb_bright[0]]):
         return False
      reg = (SOCKET_LEDS << SOCKET_SHIFT) | LEDS_SOCKET_G[socket]
      if not self._bus.write(reg, [rgb_bright[1]]):
         return False
      reg = (SOCKET_LEDS << SOCKET_SHIFT) | LEDS_SOCKET_B[socket]
      return self._bus.write(reg, [rgb_bright[2]])

   @lock_decorator
   def getLedAux(self, aux):
      """Returns the brightness of the specified auxiliar LED."""
      if not aux in LEDS_AUX:
         raise ValueError("Wrong auxiliar LED")
      reg = (SOCKET_LEDS << SOCKET_SHIFT) | LEDS_AUX[aux]
      return self._bus.read(reg, 1)[0]

   @lock_decorator
   def setLedAux(self, aux, bright):
      """Sets the brightness of the specified auxiliar LED."""
      if not aux in LEDS_AUX:
         raise ValueError("Wrong auxiliar LED")
      bright = bright & 0xFF
      reg = (SOCKET_LEDS << SOCKET_SHIFT) | LEDS_AUX[aux]
      return self._bus.write(reg, [bright])
# -----------------------
