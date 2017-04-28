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
#            Atmospheric Sensor Example                 #
#                                                       #
#    Description: Example of usage of the Atmospheric   #
#       Sensor included in the AGILE Maker's Shield     #
#       with DBus.                                      #
#    Author: David Palomares <d.palomares@libelium.com> #
#    Version: 1.0                                       #
#    Date: April 2017                                   #
#########################################################

# --- Imports -----------
import sys
import signal
import time
import dbus
# -----------------------


# --- Variables ---------
# DBus
BUS_NAME = "iot.agile.Feature"
OBJ_PATH = "/iot/agile/Feature"
FEATURE_NAME = "Atmospheric_Sensor"
feature = None
# -----------------------


# --- Functions ---------
def run_example():
   """
   Read the temperature, humidity and pressure from the
   sensor over DBus.
   """
   print("\x1b[1;37;39m" + "Atmospheric Sensor Example" + "\x1b[0m")
   try:
      data = feature.readAtmosphericSensor()
      print("Temperature: {} ºC".format(data["temperature"]))
      print("Humidity: {} %".format(data["humidity"]))
      print("Pressure: {} Pa".format(data["pressure"]))
   except:
      print("Problem reading from the AGILE Maker's Shield.")
      print("Is the shield connected and the DBus server running?")

def setup():
   """
   Sets the default parameters of the program.
   """
   global feature
   # Signal handler (Ctrl+C exit)
   signal.signal(signal.SIGINT, signal_handler)
   # DBus
   session_bus = dbus.SessionBus()
   obj = session_bus.get_object(BUS_NAME, OBJ_PATH + "/" + FEATURE_NAME)
   feature = dbus.Interface(obj, dbus_interface=BUS_NAME)

def signal_handler(signal, frame):
   """
   Handles the SIGINT signal.
   """
   print()
   endProgram(0)

def endProgram(status):
   """
   Exists the program.
   """
   sys.exit(status)
# -----------------------


# --- Main program ------
if __name__ == "__main__":

   setup()

   run_example()

   endProgram(0)
# -----------------------
