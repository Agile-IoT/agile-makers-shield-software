
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
#              AGILE Serial Interruptions               #
#                                                       #
#    Description: Class that uses an Observer pattern   #
#       to watch for interruptions sent from            #
#       the AT Mega. Only one instance of this will     #
#       be created.                                     #
#    Author: David Palomares <d.palomares@libelium.com> #
#    Version: 0.1                                       #
#    Date: May 2017                                     #
#########################################################

# --- Imports -----------
from agile_makers_shield.utils import singleton
from agile_makers_shield.buses.i2c import atmega
import RPi.GPIO as GPIO
import time
# -----------------------


# --- Variables ---------
# GPIOs
PININT = 7 #GPIO4
# Interrupts
INT_UART_0   = 0b0001
INT_UART_1   = 0b0010
INT_BUTTON_0 = 0b0100
INT_BUTTON_1 = 0b1000
# -----------------------


# --- Classes -----------
class Interruptions(metaclass=singleton.Singleton):
   """
   Class that handles interruptions and notify
   its subscribed methods. This class will be
   instantiated once.
   """

   def __init__(self):
      self._observers = []
      self._interrupts = {INT_UART_0: False, INT_UART_1: False,
                          INT_BUTTON_0: False, INT_BUTTON_1: False}
      self._atmega = atmega.ATMega()
      GPIO.setmode(GPIO.BOARD)
      GPIO.setwarnings(False)
      GPIO.setup(PININT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
      GPIO.add_event_detect(PININT, GPIO.RISING,
            callback=self._interruption_handler, bouncetime=250)

   def _interruption_handler(self, channel):
      if channel == PININT:
         interrupt = 0
         if self._atmega.getUartInterrupt(atmega.SOCKET_0):
            interrupt = interrupt | INT_UART_0
         if self._atmega.getUartInterrupt(atmega.SOCKET_1):
            interrupt = interrupt | INT_UART_1
         if self._atmega.getButtonInterrupt(atmega.SOCKET_0):
            interrupt = interrupt | INT_BUTTON_0
         if self._atmega.getButtonInterrupt(atmega.SOCKET_1):
            interrupt = interrupt | INT_BUTTON_1
         self._update_observers(interrupt)

   def _update_observers(self, interrupt):
      for observer in self._observers:
         if (observer.attribute & interrupt):
            observer.update()

   def register(self, observer):
      if (observer.attribute & INT_UART_0) and self._interrupts[INT_UART_0]:
         raise IOError("Socket 0 already in use")
      if (observer.attribute & INT_UART_1) and self._interrupts[INT_UART_1]:
         raise IOError("Socket 1 already in use")
      if not observer in self._observers:
         if (observer.attribute & INT_UART_0):
            self._interrupts[INT_UART_0] = True
         if (observer.attribute & INT_UART_1):
            self._interrupts[INT_UART_1] = True
         self._observers.append(observer)

   def unregister(self, observer):
         if observer in self._observers:
            if (observer.attribute & INT_UART_0):
               self._interrupts[INT_UART_0] = False
            if (observer.attribute & INT_UART_1):
               self._interrupts[INT_UART_1] = False
            self._observers.remove(observer)

   def close(self):
      GPIO.remove_event_detect(PININT)
      GPIO.cleanup()
# -----------------------
