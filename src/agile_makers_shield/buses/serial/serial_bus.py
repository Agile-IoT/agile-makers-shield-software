
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
#                   AGILE Serial Bus                    #
#                                                       #
#    Description: Class to read from and write to       #
#       the ATMega serial buses via I2C.                #
#    Author: David Palomares <d.palomares@libelium.com> #
#    Version: 0.1                                       #
#    Date: May 2017                                     #
#########################################################

# --- Imports -----------
from agile_makers_shield.utils import observer
from agile_makers_shield.buses.i2c import atmega
from agile_makers_shield.buses.serial import interruptions
import RPi.GPIO as GPIO
import time
# -----------------------


# --- Variables ---------
# GPIOS
PININT = 7 #GPIO4
# Serial
DEFAULT_BAUDRATE = atmega.UART_BAUD_9600
DEFAULT_DATABITS = atmega.UART_DATABITS_8
DEFAULT_STOPBITS = atmega.UART_STOPBITS_1
DEFAULT_PARITY = atmega.UART_PARITY_NONE
DEFAULT_TIMEOUT = 2
CHAR_NEWLINE = 0x0A
#FIXME: Sometimes the available data readed from the I2C bus is 0xFF, although
#       the ATMega sends 0x00. When this happens, the following 255 bytes
#       are always the following sequence. Why? This sequence will be filtered
#       in the Serial_Bus._updateBuffer() function.
NOISE_DATA = [0x00, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
              0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
              0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
              0xff, 0xff, 0x00, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
              0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
              0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
              0xff, 0xff, 0xff, 0xff, 0x00, 0xff, 0xff, 0xff, 0xff, 0xff,
              0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
              0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
              0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0x00, 0xff, 0xff, 0xff,
              0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
              0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
              0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0x00, 0xff,
              0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
              0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
              0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
              0x00, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
              0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
              0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
              0xff, 0xff, 0x00, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
              0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
              0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
              0xff, 0xff, 0xff, 0xff, 0x00, 0xff, 0xff, 0xff, 0xff, 0xff,
              0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
              0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
              0xff, 0xff, 0xff, 0xff, 0xff]
# -----------------------


# --- Classes -----------
class SerialException(IOError):
    """Base class for serial port related exceptions."""

class SerialTimeoutException(SerialException):
   """Write timeouts give an exception."""

class Timeout():
   """Class to control timeouts."""

   def __init__(self, timeout=DEFAULT_TIMEOUT, raises_timeout=False):
      self._timeout = timeout
      self._raises_timeout = raises_timeout
      self._limit = time.time() + self._timeout

   def check(self):
      if time.time() > self._limit:
         if self._raises_timeout:
            raise SerialTimeoutException()
         return True
      return False

class Serial(observer.Observer):
   """Class that implements methods to read from
   and write to the  the ATMega serial buses via I2C."""

   def __init__(self, port=None, baudrate=DEFAULT_BAUDRATE, databits=DEFAULT_DATABITS,
         stopbits=DEFAULT_STOPBITS, parity=DEFAULT_PARITY, timeout=DEFAULT_TIMEOUT,
         raises_timeout=False):
      self._atmega = atmega.ATMega()
      self._socket = port
      self.baudrate = baudrate
      self.databits = databits
      self.stopbits = stopbits
      self.parity = parity
      self.timeout = timeout
      self.raises_timeout = raises_timeout
      self._open = False
      self._buffer = []
      self._interrupts = 0
      if self._socket == atmega.SOCKET_0:
         self._interrupts = interruptions.INT_UART_0
      if self._socket == atmega.SOCKET_1:
         self._interrupts = interruptions.INT_UART_1
      self._interruptions = interruptions.Interruptions()
      if self._socket is not None:
         self.open()

   @property
   def port(self):
      return self._socket

   @port.setter
   def port(self, value):
      if value == atmega.SOCKET_0:
         self._interrupts = interruptions.INT_UART_0
      if value == atmega.SOCKET_1:
         self._interrupts = interruptions.INT_UART_1
      self._socket = value

   def update(self):
      """Overrides observer.update() method."""
      self._updateBuffer()

   @property
   def attribute(self):
      """Overrides observer.attribute() method."""
      return self._interrupts

   def _updateBuffer(self):
      data = self._atmega.getData(self._socket)
      #FIXME: If the noise data from the I2C is fixed, remove this
      if len(data) == 255:
         if data == NOISE_DATA:
            return
      self._buffer.extend(data)

   def _check_timeout(self, limit):
      if time.time() > limit:
         raise SerialTimeoutException()

   @property
   def in_waiting(self):
      return len(self._buffer)

   def inWaiting(self):
      return self.in_waiting

   def isOpen(self):
      return self._open

   def open(self):
      if self._open:
         raise SerialException("Socket {} is already open".format(self._socket))
      self._interruptions.register(self)
      self._atmega.uartON(self._socket, self.baudrate, self.databits,
                          self.stopbits, self.parity)
      self._buffer = []
      self._open = True

   def close(self):
      if not self._open:
         raise SerialException("Socket {} is already closed".format(self._socket))
      self._interruptions.unregister(self)
      self._atmega.uartOFF(self._socket)
      self._buffer = []
      self._open = False

   def write(self, data):
      if not self._open:
         raise SerialException("Socket {} is closed".format(self._socket))
      self._atmega.sendData(self._socket, list(data))

   def read(self, size=1):
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

   def readline(self):
      if not self._open:
         raise SerialException("Socket {} is closed".format(self._socket))
      line = []
      timeout = Timeout(self.timeout, self.raises_timeout)
      while not line:
         try:
            index = self._buffer.index(CHAR_NEWLINE)
            line = self._buffer[0:(index+1)]
            self._buffer = self._buffer[(index+1):]
         except ValueError:
            pass
         if timeout.check() and not line:
            break
      return bytes(line)

   def readlines(self):
      if not self._open:
         raise SerialException("Socket {} is closed".format(self._socket))
      lines = []
      timeout = Timeout(self.timeout, self.raises_timeout)
      while True:
         while (len(self._buffer) > 0):
            try:
               index = self._buffer.index(CHAR_NEWLINE)
               line = self._buffer[0:(index+1)]
               self._buffer = self._buffer[(index+1):]
               lines.append(bytes(line))
            except ValueError:
               break
         if timeout.check():
            break
      return lines

   def flush(self):
      if not self._open:
         raise SerialException("Socket {} is closed".format(self._socket))
      self._buffer = []
# -----------------------
