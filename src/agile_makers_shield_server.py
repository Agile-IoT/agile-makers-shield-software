#!/usr/bin/env python3


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
AGILE Maker's Shield DBus Server.

Description: Server that exposes protocols and
             features of the AGILE Maker's Shield over DBus.
Author: David Palomares <d.palomares@libelium.com>
Version: 0.3
Date: May 2017
"""


# --- Imports -----------
import sys
from gi.repository import GLib
import dbus
import dbus.service
import dbus.mainloop.glib
import argparse
# from agile_makers_shield.buses.serial import interruptions
from agile_makers_shield.buses.dbus import constants as db_cons
from agile_makers_shield.protocols import xbee_802_15_4
from agile_makers_shield.protocols import xbee_zigbee
from agile_makers_shield.protocols import lorawan
from agile_makers_shield.features import leds
from agile_makers_shield.features import gps
from agile_makers_shield.features import adc
from agile_makers_shield.features import atmospheric_sensor
import logging
# -----------------------

dbus.mainloop.glib.threads_init()
GLib.threads_init()


# --- Variables ---------
# Log
LOGLEVEL_DEFAULT = "INFO"
LOGLEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
# Interruptions
# isr = interruptions.Interruptions()
# DBus
mainloop = GLib.MainLoop()
# -----------------------


# --- Classes -----------
class DBusBase(dbus.service.Object):
    """Base clase for DBus server."""

    def __init__(self):
        """Init method."""
        super().__init__(dbus.SessionBus(), db_cons.OBJ_PATH["Base"])

    @dbus.service.method(
        db_cons.BUS_NAME["Base"],
        in_signature="",
        out_signature=""
    )
    def Exit(self):
        """Exit DBus server."""
        mainloop.quit()
# -----------------------


# --- Functions ---------
def dbus_service():
    """Start the different DBus services and run the server."""
    GLib.threads_init()
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    # Base
    DBusBase()
    # Protocols
    xbee_802_15_4.XBee_802_15_4()
    xbee_zigbee.XBee_ZigBee()
    lorawan.LoRaWAN()
    # Features
    leds.LEDs()
    gps.GPS()
    adc.ADC()
    atmospheric_sensor.Atmospheric_Sensor()
    logger.info("Running AGILE DBus service.")
    try:
        mainloop.run()
    except KeyboardInterrupt:
        print()
        try:
            mainloop.quit()
        except dbus.exceptions.DBusException:
            pass
        end_program(0)


def end_program(status):
    """Exit the program."""
    # isr.close()
    logger.info("AGILE DBus service stopped.")
    sys.exit(status)
# -----------------------


# --- Main program ------
if __name__ == "__main__":
    # Parse the args
    parser = argparse.ArgumentParser(
        description="Reads the value of the pollen sensor and "
                    "stores it in a log file"
    )
    parser.add_argument(
        "-l",
        "--loglevel",
        nargs="?",
        type=str,
        default=LOGLEVEL_DEFAULT,
        help="Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL. "
             "Default: {}".format(LOGLEVEL_DEFAULT))
    args = parser.parse_args()
    if args.loglevel in LOGLEVELS:
        if (args.loglevel == "DEBUG") or \
                (args.loglevel == "debug") or \
                (args.loglevel == "Debug"):
            log_level = logging.DEBUG
        elif (args.loglevel == "INFO") or \
                (args.loglevel == "info") or \
                (args.loglevel == "Info"):
            log_level = logging.INFO
        elif (args.loglevel == "WARNING") or \
                (args.loglevel == "warning") or \
                (args.loglevel == "Warning"):
            log_level = logging.WARNING
        elif (args.loglevel == "ERROR") or \
                (args.loglevel == "error") or \
                (args.loglevel == "Error"):
            log_level = logging.ERROR
        elif (args.loglevel == "CRITICAL") or \
                (args.loglevel == "critical") or \
                (args.loglevel == "Critical"):
            log_level = logging.CRITICAL
    else:
        log_level = logging.INFO
    # Start logging
    logging.basicConfig(
        filemode="a",
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=log_level
    )
    logger = logging.getLogger(db_cons.LOGGER_NAME)
    # Start DBus
    dbus_service()
    end_program(0)
# -----------------------
