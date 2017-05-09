#!/usr/bin/env python3

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
#                XBee 802.15.4 Example                  #
#                                                       #
#    Description: Example of the AGILE XBee 802.15.4    #
#       module with the DBus AGILE Protocol API.        #
#       Two XBee modules are needed, one for each       #
#       socket. The module in the socket 0 will send    #
#       frames to the module in the socket 1.           #
#    Author: David Palomares <d.palomares@libelium.com> #
#    Version: 1.0                                       #
#    Date: May 2017                                     #
#########################################################

# --- Imports -----------
import sys
import signal
import time
import dbus
import threading
# -----------------------


# --- Variables ---------
# DBus
BUS_NAME = "iot.agile.Protocol"
OBJ_PATH = "/iot/agile/Protocol"
SOCKET0 = "socket0"
SOCKET1 = "socket1"
PROTOCOL_NAME = "XBee_802_15_4"
# XBee 802.15.4 Parameters
BAUDRATE = 9600
API_MODE_2 = True
DEST_ADDRESS = [0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07] #XXX: MAC Address of the Socket 1 Module
msg = list(b"Test frame")
PAN_ID = "1234"
CHANNEL = "0F"
ENCRYPTION_MODE = "0"
ENCRYPTION_KEY = "0102030405060708"
DELAY = 2 # Time between frames sent in seconds
NUM_FRAMES = 5 # Number of frames sent
# XBee 802.15.4 Commands
setup_params = {
   "baudrate": BAUDRATE,
   "apiMode2": API_MODE_2,
   "ID": PAN_ID,
   "CH": CHANNEL,
   "EE": ENCRYPTION_MODE,
   "KY": ENCRYPTION_KEY
}
tx_long_addr_command = {
   "api_command": "tx_long_addr",
   "frame_id": [0],
   "dest_addr": DEST_ADDRESS,
   "options": [0],
   "data": msg
}
# Thread
threadSocket0 = None
threadSocket1 = None
# -----------------------


# --- Classes -----------
class StoppableThread(threading.Thread):
   """Thread class with a stop() method. The thread itself has to check
   regularly for the stopped() condition."""

   def __init__(self, socket, protocol):
      super(StoppableThread, self).__init__()
      self._stopper = threading.Event()
      self._socket = socket
      self._protocol = protocol
      self._frame_id = 1

   def run(self):
      print("[{}] Setup".format(self._socket))
      self._protocol.Setup(dbus.Dictionary(setup_params, signature="sv"))
      print("[{}] Connect".format(self._socket))
      try:
         self._protocol.Connect()
      except dbus.exceptions.DBusException:
         print("[{}] Error connecting".format(self._socket))
         self.stop()
         return
      if self._socket == SOCKET0:
         # Send to the module in Socket 1
         for frame_id in range(1, (NUM_FRAMES + 1)):
            time.sleep(DELAY)
            data = tx_long_addr_command
            data["frame_id"] = [frame_id]
            print("[{}] Sending: {}".format(self._socket, data))
            self._protocol.Send(dbus.Dictionary(data, signature="sv"))
         self.stop()
      else:
         # Receive data
         while True:
            if self.stopped():
               break
            data = self._protocol.Receive()
            if data:
                print("[{}] Received: {}".format(self._socket, data))
      print("[{}] Disconnect".format(self._socket))
      self._protocol.Disconnect()

   def stop(self):
      self._stopper.set()

   def stopped(self):
      return self._stopper.isSet()
# -----------------------


# --- Functions ---------
def run_example():
   """
   Connect the modules and send messages between them.
   """
   print("\x1b[1;37;39m" + "XBee 802.15.4 Example" + "\x1b[0m")
   # Start threads
   threadSocket0.start()
   threadSocket1.start()
   # Wait for thread 0 to finish
   threadSocket0.join()
   time.sleep(DELAY)
   threadSocket1.stop()
   threadSocket1.join()

def setup():
   """
   Sets the default parameters of the program.
   """
   global threadSocket0, threadSocket1
   # Signal handler (Ctrl+C exit)
   signal.signal(signal.SIGINT, signal_handler)
   # DBus
   session_bus = dbus.SessionBus()
   obj_0 = session_bus.get_object(BUS_NAME, OBJ_PATH + "/" + PROTOCOL_NAME + "/" + SOCKET0)
   obj_1 = session_bus.get_object(BUS_NAME, OBJ_PATH + "/" + PROTOCOL_NAME + "/" + SOCKET1)
   protocol_0 = dbus.Interface(obj_0, dbus_interface=BUS_NAME)
   protocol_1 = dbus.Interface(obj_1, dbus_interface=BUS_NAME)
   # Threads
   threadSocket0 = StoppableThread(SOCKET0, protocol_0)
   threadSocket1 = StoppableThread(SOCKET1, protocol_1)

def signal_handler(signal, frame):
   """
   Handles the SIGINT signal.
   """
   print()
   try:
      print("Stopping the modules... ", end="")
      if threadSocket0.is_alive():
         threadSocket0.stop()
         threadSocket0.join()
      if threadSocket1.is_alive():
         threadSocket1.stop()
         threadSocket1.join()
      print("OK")
   except Exception as err:
      print("Error\n{}").format(err)
   endProgram(0)

def endProgram(status):
   """
   Exists the program.
   """
   sys.exit(status)
# -----------------------


# --- Main program ------
if __name__ == "__main__":

   # Setup
   setup()

   # XBee 802.15.4 example
   run_example()

   endProgram(0)
# -----------------------
