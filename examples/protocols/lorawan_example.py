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
#                    LoRaWAN Example                    #
#                                                       #
#    Description: Example of the AGILE LoRaWAN module   #
#       with the DBus AGILE Protocol API.               #
#    Author: David Palomares <d.palomares@libelium.com> #
#    Version: 1.0                                       #
#    Date: November 2016                                #
#########################################################

# --- Imports -----------
import sys
import signal
import time
import dbus
# -----------------------


# --- Variables ---------
# DBus
BUS_NAME = "iot.agile.Protocol"
OBJ_PATH = "/iot/agile/Protocol"
SOCKET0 = "socket0"
SOCKET1 = "socket1"
PROTOCOL_NAME = "LoRaWAN"
protocol = None
# LoRaWAN
setup_lorawan = {
   "baudrate": 57600,
   "mode": "LoRaWAN",
   "save": False,
   "join": "OTAA",
   "deveui": "0102030405060708",
   "appeui": "0102030405060708",
   "appkey": "0102030405060708090A0B0C0D0E0F00"
   #"devaddr": "01020304",
   #"nwkskey": "0102030405060708090A0B0C0D0E0F00",
   #"appskey": "0102030405060708090A0B0C0D0E0F00"
}
send_lorawan = {
   "type": "uncnf",
   "port": 3,
   "data": "4C6F526157414E20444275732074657374" # "LoRaWAN DBus test" in HEX
}
# LoRa
setup_lora = {
   "baudrate": 57600,
   "mode": "LoRa",
   "freq": "868100000",
   "sf": "sf12",
   "cr": "4/5",
   "bw": "125",
   "crc": "on"
}
send_lora = {
   "data": "4C6F526120444275732074657374" # "LoRa DBus test" in HEX
}
# -----------------------


# --- Functions ---------
def run_example_lorawan():
   """
   Connect the module and send a message to a base station.
   """
   print("*** Testing LoRaWAN ***")
   try:
      print("Setting the device parameters... ", end="")
      sys.stdout.flush()
      protocol.Setup(dbus.Dictionary(setup_lorawan, signature="sv"))
      print("OK")
      try:
         print("Connecting the module... ", end="")
         sys.stdout.flush()
         protocol.Connect()
         print("OK")
         try:
            print("Sending the message... ", end="")
            sys.stdout.flush()
            protocol.Send(dbus.Dictionary(send_lorawan, signature="sv"))
            print("OK")
         except Exception as err:
            print("Error\n{}".format(err))
         try:
            print("Disconnecting the module... ", end="")
            sys.stdout.flush()
            protocol.Disconnect()
            print("OK")
         except Exception as err:
            print("Error\n{}".format(err))
      except Exception as err:
         print("Error\n{}".format(err))
   except Exception as err:
      print("Error\n{}".format(err))

def run_example_lora():
   """
   Connect the module and send and receive a message point to point.
   """
   print("\n*** Testing LoRa ***")
   try:
      print("Setting the device parameters... ", end="")
      sys.stdout.flush()
      protocol.Setup(dbus.Dictionary(setup_lora, signature="sv"))
      print("OK")
      try:
         print("Connecting the module... ", end="")
         sys.stdout.flush()
         protocol.Connect()
         print("OK")
         try:
            print("Sending the message... ", end="")
            sys.stdout.flush()
            protocol.Send(dbus.Dictionary(send_lora, signature="sv"))
            print("OK")
         except Exception as err:
            print("Error\n{}".format(err))
         try:
            print("(Send a message with another module. The timeout is 15 seconds.)")
            print("Receiving the message... ", end="")
            sys.stdout.flush()
            msg = protocol.Receive()
            print("OK")
            if msg:
               print("Message received: {}".format(msg["data"]))
            else:
               print("No message received")
         except Exception as err:
            print("Error\n{}".format(err))
         try:
            print("Disconnecting the module... ", end="")
            sys.stdout.flush()
            protocol.Disconnect()
            print("OK")
         except Exception as err:
            print("Error\n{}".format(err))
      except Exception as err:
         print("Error\n{}".format(err))
   except Exception as err:
      print("Error\n{}".format(err))

def setup():
   """
   Sets the default parameters of the program.
   """
   global protocol
   # Signal handler (Ctrl+C exit)
   signal.signal(signal.SIGINT, signal_handler)
   # DBus
   session_bus = dbus.SessionBus()
   obj = session_bus.get_object(BUS_NAME, OBJ_PATH + "/" + PROTOCOL_NAME + "/" + SOCKET0)
   protocol = dbus.Interface(obj, dbus_interface=BUS_NAME)

def signal_handler(signal, frame):
   """
   Handles the SIGINT signal.
   """
   print()
   try:
      print("Disconnecting the module... ", end="")
      protocol.Disconnect()
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

   # LoRaWAN example
   run_example_lorawan()

   # LoRa example
   run_example_lora()

   endProgram(0)
# -----------------------
