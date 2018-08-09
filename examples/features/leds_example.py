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


"""
LEDs Example.

Description: Example of usage of the LEDS included
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
FEATURE_NAME = "LEDs"
feature = None
# LEDs colors
on = 128
off = 0
red = [on, off, off]
green = [off, on, off]
blue = [off, off, on]
cyan = [off, on, on]
magenta = [on, off, on]
yellow = [on, on, off]
white = [on, on, on]
black = [off, off, off]
# -----------------------


# --- Functions ---------
def run_example():
    """Play with the LEDs of the shield."""
    print("\x1b[1;37;39m" + "LEDs Example" + "\x1b[0m")

    try:

        print("Get status")
        led_S0 = feature.getLedStatus(
            dbus.Dictionary({"led": "S0"}, signature="sv")
        )
        led_S1 = feature.getLedStatus(
            dbus.Dictionary({"led": "S1"}, signature="sv")
        )
        led_A2 = feature.getLedStatus(
            dbus.Dictionary({"led": "A2"}, signature="sv")
        )
        led_A3 = feature.getLedStatus(
            dbus.Dictionary({"led": "A3"}, signature="sv")
        )
        led_A4 = feature.getLedStatus(
            dbus.Dictionary({"led": "A4"}, signature="sv")
        )
        print("\S0: {}".format(led_S0["color"]))
        print("\S1: {}".format(led_S1["color"]))
        print("\A2: {}".format(led_A2["bright"]))
        print("\A3: {}".format(led_A3["bright"]))
        print("\A4: {}".format(led_A4["bright"]))

        print("Turn all off")
        feature.setLedStatus(
            dbus.Dictionary({"led": "S0", "color": black}, signature="sv")
        )
        feature.setLedStatus(
            dbus.Dictionary({"led": "S1", "color": black}, signature="sv")
        )
        feature.setLedStatus(
            dbus.Dictionary({"led": "A2", "bright": off}, signature="sv")
        )
        feature.setLedStatus(
            dbus.Dictionary({"led": "A3", "bright": off}, signature="sv")
        )
        feature.setLedStatus(
            dbus.Dictionary({"led": "A4", "bright": off}, signature="sv")
        )

        print("Quick blink all")
        for i in range(50):
            feature.setLedStatus(
                dbus.Dictionary({"led": "S0", "color": white}, signature="sv")
            )
            feature.setLedStatus(
                dbus.Dictionary({"led": "S1", "color": white}, signature="sv")
            )
            feature.setLedStatus(
                dbus.Dictionary({"led": "A2", "bright": on}, signature="sv")
            )
            feature.setLedStatus(
                dbus.Dictionary({"led": "A3", "bright": on}, signature="sv")
            )
            feature.setLedStatus(
                dbus.Dictionary({"led": "A4", "bright": on}, signature="sv")
            )
            time.sleep(0.01)
            feature.setLedStatus(
                dbus.Dictionary({"led": "S0", "color": black}, signature="sv")
            )
            feature.setLedStatus(
                dbus.Dictionary({"led": "S1", "color": black}, signature="sv")
            )
            feature.setLedStatus(
                dbus.Dictionary({"led": "A2", "bright": off}, signature="sv")
            )
            feature.setLedStatus(
                dbus.Dictionary({"led": "A3", "bright": off}, signature="sv")
            )
            feature.setLedStatus(
                dbus.Dictionary({"led": "A4", "bright": off}, signature="sv")
            )
            time.sleep(0.01)

        print("Slow blink all")
        for i in range(10):
            feature.setLedStatus(
                dbus.Dictionary({"led": "S0", "color": white}, signature="sv")
            )
            feature.setLedStatus(
                dbus.Dictionary({"led": "S1", "color": white}, signature="sv")
            )
            feature.setLedStatus(
                dbus.Dictionary({"led": "A2", "bright": on}, signature="sv")
            )
            feature.setLedStatus(
                dbus.Dictionary({"led": "A3", "bright": on}, signature="sv")
            )
            feature.setLedStatus(
                dbus.Dictionary({"led": "A4", "bright": on}, signature="sv")
            )
            time.sleep(0.1)
            feature.setLedStatus(
                dbus.Dictionary({"led": "S0", "color": black}, signature="sv")
            )
            feature.setLedStatus(
                dbus.Dictionary({"led": "S1", "color": black}, signature="sv")
            )
            feature.setLedStatus(
                dbus.Dictionary({"led": "A2", "bright": off}, signature="sv")
            )
            feature.setLedStatus(
                dbus.Dictionary({"led": "A3", "bright": off}, signature="sv")
            )
            feature.setLedStatus(
                dbus.Dictionary({"led": "A4", "bright": off}, signature="sv")
            )
            time.sleep(0.1)

        print("Cycle through all")
        for i in range(4):
            feature.setLedStatus(
                dbus.Dictionary({"led": "A2", "bright": on}, signature="sv")
            )
            time.sleep(0.1)
            feature.setLedStatus(
                dbus.Dictionary({"led": "A2", "bright": off}, signature="sv")
            )
            feature.setLedStatus(
                dbus.Dictionary({"led": "A3", "bright": on}, signature="sv")
            )
            time.sleep(0.1)
            feature.setLedStatus(
                dbus.Dictionary({"led": "A3", "bright": off}, signature="sv")
            )
            feature.setLedStatus(
                dbus.Dictionary({"led": "A4", "bright": on}, signature="sv")
            )
            time.sleep(0.1)
            feature.setLedStatus(
                dbus.Dictionary({"led": "A4", "bright": off}, signature="sv")
            )
            feature.setLedStatus(
                dbus.Dictionary({"led": "S0", "color": white}, signature="sv")
            )
            time.sleep(0.1)
            feature.setLedStatus(
                dbus.Dictionary({"led": "S0", "color": black}, signature="sv")
            )
            feature.setLedStatus(
                dbus.Dictionary({"led": "S1", "color": white}, signature="sv")
            )
            time.sleep(0.1)
            feature.setLedStatus(
                dbus.Dictionary({"led": "S1", "color": black}, signature="sv")
            )
            feature.setLedStatus(
                dbus.Dictionary({"led": "S0", "color": white}, signature="sv")
            )
            time.sleep(0.1)
            feature.setLedStatus(
                dbus.Dictionary({"led": "S0", "color": black}, signature="sv")
            )
            feature.setLedStatus(
                dbus.Dictionary({"led": "A4", "bright": on}, signature="sv")
            )
            time.sleep(0.1)
            feature.setLedStatus(dbus.Dictionary(
                {"led": "A4", "bright": off}, signature="sv")
            )
            feature.setLedStatus(dbus.Dictionary(
                {"led": "A3", "bright": on}, signature="sv")
            )
            time.sleep(0.1)
            feature.setLedStatus(
                dbus.Dictionary({"led": "A3", "bright": off}, signature="sv")
            )
        feature.setLedStatus(
            dbus.Dictionary({"led": "A2", "bright": on}, signature="sv")
        )
        time.sleep(0.1)
        feature.setLedStatus(
            dbus.Dictionary({"led": "A2", "bright": off}, signature="sv")
        )
        time.sleep(0.1)

        print("Colors")
        for i in range(2):
            feature.setLedStatus(
                dbus.Dictionary({"led": "S0", "color": red}, signature="sv")
            )
            feature.setLedStatus(
                dbus.Dictionary({"led": "S1", "color": red}, signature="sv")
            )
            time.sleep(0.5)
            feature.setLedStatus(
                dbus.Dictionary({"led": "S0", "color": green}, signature="sv")
            )
            feature.setLedStatus(
                dbus.Dictionary({"led": "S1", "color": green}, signature="sv")
            )
            time.sleep(0.5)
            feature.setLedStatus(
                dbus.Dictionary({"led": "S0", "color": blue}, signature="sv")
            )
            feature.setLedStatus(
                dbus.Dictionary({"led": "S1", "color": blue}, signature="sv")
            )
            time.sleep(0.5)
            feature.setLedStatus(
                dbus.Dictionary({"led": "S0", "color": yellow}, signature="sv")
            )
            feature.setLedStatus(
                dbus.Dictionary({"led": "S1", "color": yellow}, signature="sv")
            )
            time.sleep(0.5)
            feature.setLedStatus(dbus.Dictionary(
                {"led": "S0", "color": magenta},
                signature="sv"
            ))
            feature.setLedStatus(dbus.Dictionary(
                {"led": "S1", "color": magenta},
                signature="sv"
            ))
            time.sleep(0.5)
            feature.setLedStatus(
                dbus.Dictionary({"led": "S0", "color": cyan}, signature="sv")
            )
            feature.setLedStatus(
                dbus.Dictionary({"led": "S1", "color": cyan}, signature="sv")
            )
            time.sleep(0.5)
            feature.setLedStatus(
                dbus.Dictionary({"led": "S0", "color": white}, signature="sv")
            )
            feature.setLedStatus(
                dbus.Dictionary({"led": "S1", "color": white}, signature="sv")
            )
            time.sleep(0.5)
            feature.setLedStatus(
                dbus.Dictionary({"led": "S0", "color": black}, signature="sv")
            )
            feature.setLedStatus(
                dbus.Dictionary({"led": "S1", "color": black}, signature="sv")
            )
            time.sleep(0.5)

        print("Dim")
        for i in range(2):
            for j in range(255):
                feature.setLedStatus(dbus.Dictionary(
                    {"led": "S0", "color": [j, j, j]}, signature="sv")
                )
                feature.setLedStatus(dbus.Dictionary(
                    {"led": "S1", "color": [j, j, j]}, signature="sv")
                )
                feature.setLedStatus(dbus.Dictionary(
                    {"led": "A2", "bright": j}, signature="sv")
                )
                feature.setLedStatus(dbus.Dictionary(
                    {"led": "A3", "bright": j}, signature="sv")
                )
                feature.setLedStatus(dbus.Dictionary(
                    {"led": "A4", "bright": j}, signature="sv")
                )
                time.sleep(0.01)
            for j in reversed(range(255)):
                feature.setLedStatus(dbus.Dictionary(
                    {"led": "S0", "color": [j, j, j]},
                    signature="sv"
                ))
                feature.setLedStatus(dbus.Dictionary(
                    {"led": "S1", "color": [j, j, j]},
                    signature="sv"
                ))
                feature.setLedStatus(
                    dbus.Dictionary({"led": "A2", "bright": j}, signature="sv")
                )
                feature.setLedStatus(
                    dbus.Dictionary({"led": "A3", "bright": j}, signature="sv")
                )
                feature.setLedStatus(
                    dbus.Dictionary({"led": "A4", "bright": j}, signature="sv")
                )
                time.sleep(0.01)

    except:
        print("Problem reading from the AGILE Maker's Shield.")
        print("Is the shield connected and the DBus server running?")


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
