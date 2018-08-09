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
GPS Example.

Description: Example of usage of the GPS included
             in the AGILE Maker's Shield with DBus.
Author: David Palomares <d.palomares@libelium.com>
Version: 1.0
Date: April 2017
"""


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
FEATURE_NAME = "GPS"
feature = None
# GPS
DELAY = 4.5
# -----------------------


# --- Functions ---------
def run_example():
    """Update the GPS and show the last GGA and RMC frames."""
    print("\x1b[1;37;39m" + "GPS Example" + "\x1b[0m")
    print("(Use Control+C to exit)")

    while(True):

        try:
            feature.updateGPS()
            gga = feature.getLastGGA()
            rmc = feature.getLastRMC()
        except:
            print("Problem reading from the AGILE Maker's Shield.")
            print("Is the shield connected and the DBus server running?")

        print("New GPS data")

        # GGA
        print("   GGA Frame: ")
        gga_utc = {}
        gga_utc["h"] = 0
        gga_utc["m"] = 0
        gga_utc["s"] = 0
        if gga["utc"]:
            gga_utc["h"] = int(float(gga["utc"]) // 10000)
            gga_utc["m"] = int((float(gga["utc"]) % 10000) // 100)
            gga_utc["s"] = int(float(gga["utc"]) % 100)
        print("\tUTC: {:02d}:{:02d}:{:02d}".format(
            gga_utc["h"],
            gga_utc["m"],
            gga_utc["s"])
        )
        print("\tFix quality: {}; Number of satellites: {}".format(
            gga["fix"],
            gga["nsat"])
        )
        print("\tLatitude / Longitude: {}{} / {}{}".format(
            gga["latitude"],
            gga["latitudeDir"],
            gga["longitude"],
            gga["longitudeDir"])
        )
        print("\tAltitude: {}{}".format(
            gga["altitude"],
            gga["altitudeUnit"])
        )
        print("\tHorizontal dilution of position: {}".format(
            gga["hdop"])
        )
        print("\tHeight of geoid: {}{}".format(
            gga["hog"],
            gga["hogUnit"])
        )

        # RMC
        print("   RMC Frame")
        rmc_utc = {}
        rmc_utc["h"] = 0
        rmc_utc["m"] = 0
        rmc_utc["s"] = 0
        if rmc["utc"]:
            rmc_utc["h"] = int(float(rmc["utc"]) // 10000)
            rmc_utc["m"] = int((float(rmc["utc"]) % 10000) // 100)
            rmc_utc["s"] = int(float(rmc["utc"]) % 100)
        rmc_date = {}
        rmc_date["y"] = 0
        rmc_date["m"] = 0
        rmc_date["d"] = 0
        if rmc["date"]:
            rmc_date["y"] = 2000 + int(int(rmc["date"]) % 100)
            rmc_date["m"] = int((int(rmc["date"]) % 10000) // 100)
            rmc_date["d"] = int(int(rmc["date"]) // 10000)
        print("\tUTC: {:02d}:{:02d}:{:02d}".format(
            rmc_utc["h"],
            rmc_utc["m"],
            rmc_utc["s"])
        )
        print("\tDate: {:04d}/{:02d}/{:02d}".format(
            rmc_date["y"],
            rmc_date["m"],
            rmc_date["d"])
        )
        print("\tFix: {}; Status: {}".format(
            rmc["fix"],
            rmc["status"])
        )
        print("\tLatitude / Longitude: {}{} / {}{}".format(
            rmc["latitude"],
            rmc["latitudeDir"],
            rmc["longitude"],
            rmc["longitudeDir"])
        )
        print("\tSpeed over the ground in knots: {}".format(
            rmc["spkn"])
        )
        print("\tTrack angle in degrees: {}".format(
            rmc["angle"])
        )
        print("\tMagnetic variation: {}{}".format(
            rmc["magneticVar"],
            rmc["magneticVarDir"])
        )

        print()
        time.sleep(DELAY)


def setup():
    """Set the default parameters of the program."""
    global feature
    # Signal handler (Ctrl+C exit)
    signal.signal(signal.SIGINT, signal_handler)
    # DBus
    session_bus = dbus.SessionBus()
    obj = session_bus.get_object(BUS_NAME, OBJ_PATH + "/" + FEATURE_NAME)
    feature = dbus.Interface(obj, dbus_interface=BUS_NAME)


def signal_handler(signal, frame):
    """Handle the SIGINT signal."""
    print()
    end_program(0)


def end_program(status):
    """Exit the program."""
    sys.exit(status)
# -----------------------


# --- Main program ------
if __name__ == "__main__":
    setup()
    run_example()
    end_program(0)
# -----------------------
