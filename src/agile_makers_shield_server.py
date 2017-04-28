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
#            AGILE DBus Protocol Server                 #
#                                                       #
#    Description: Runs the AGILE DBus Protocol defined  #
#       in the AGILE API for the XBee 802.15.4 and XBee #
#       ZigBee protocols.                               #
#    Author: David Palomares <d.palomares@libelium.com> #
#    Version: 0.2                                       #
#    Date: November 2016                                #
#########################################################

# --- Imports -----------
import sys
from gi.repository import GLib
import dbus
import dbus.service
import dbus.mainloop.glib
from agile_makers_shield.buses.dbus import constants as db_cons
from agile_makers_shield.protocols import xbee_802_15_4
from agile_makers_shield.protocols import xbee_zigbee
from agile_makers_shield.protocols import lorawan
from agile_makers_shield.features import leds
from agile_makers_shield.features import gps
from agile_makers_shield.features import adc

import logging
# -----------------------


# --- Variables ---------
LOGLEVEL = logging.DEBUG # DEBUG, INFO, WARNING, ERROR, CRITICAL
mainloop = GLib.MainLoop()
# -----------------------


# --- Classes -----------
class DBusProtocol(dbus.service.Object):

   def __init__(self):
      super().__init__(dbus.SessionBus(), db_cons.OBJ_PATH["Protocol"])

   @dbus.service.method(db_cons.BUS_NAME["Protocol"], in_signature="", out_signature="")
   def Exit(self):
      mainloop.quit()


class DBusFeature(dbus.service.Object):

   def __init__(self):
      super().__init__(dbus.SessionBus(), db_cons.OBJ_PATH["Feature"])

   @dbus.service.method(db_cons.BUS_NAME["Feature"], in_signature="", out_signature="")
   def Exit(self):
      mainloop.quit()
# -----------------------


# --- Functions ---------
def dbusService():
   dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
   protocol_dbus = DBusProtocol()
   feature_dbus = DBusFeature()
   xbee_802_15_4_dbus = xbee_802_15_4.XBee_802_15_4()
   xbee_zigbee_dbus = xbee_zigbee.XBee_ZigBee()
   lorawan_dbus = lorawan.LoRaWAN()
   leds_dbus = leds.LEDs()
   gps_dbus = gps.GPS()
   adc_bus = adc.ADC()
   logger.info("Running AGILE DBus service.")
   try:
      mainloop.run()
   except KeyboardInterrupt:
      print()
      try:
         mainloop.quit()
      except dbus.exceptions.DBusException:
         pass
      endProgram(0)

def endProgram(status):
   logger.info("AGILE DBus service stopped.")
   sys.exit(status)
# -----------------------


# --- Main program ------
if __name__ == "__main__":
   # Start logging
   logging.basicConfig(
      filemode="a",
      format="%(asctime)s [%(levelname)s] %(message)s",
      datefmt="%Y-%m-%d %H:%M:%S",
      level=LOGLEVEL
   )
   logger = logging.getLogger(db_cons.LOGGER_NAME)
   # Start DBus
   dbusService()
   endProgram(0)
# -----------------------
