
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
AGILE DBus Feature LEDs.

Description: Class that exposes the control of
             the LEDs of the AGILE Maker's Shield over DBus.
Author: David Palomares <d.palomares@libelium.com>
Version: 0.1
Date: April 2017
"""


# --- Imports -----------
import dbus
import dbus.service
from agile_makers_shield.buses.dbus import feature_base as dbF
from agile_makers_shield.buses.dbus import constants as db_cons
from agile_makers_shield.buses.i2c import atmega
# -----------------------


# --- Variables ---------
FEATURE_NAME = "LEDs"
LED_PARAMS = {
    "LED": "led",
    "COLOR": "color",
    "BRIGHT": "bright"
}
LED_NAMES = {
    "0": atmega.SOCKET_0,
    "LED0": atmega.SOCKET_0,
    "S0": atmega.SOCKET_0,
    "1": atmega.SOCKET_1,
    "LED1": atmega.SOCKET_1,
    "S1": atmega.SOCKET_1,
    "2": atmega.LED_AUX_2,
    "LED2": atmega.LED_AUX_2,
    "A2": atmega.LED_AUX_2,
    "3": atmega.LED_AUX_3,
    "LED3": atmega.LED_AUX_3,
    "A3": atmega.LED_AUX_3,
    "4": atmega.LED_AUX_4,
    "LED4": atmega.LED_AUX_4,
    "A4": atmega.LED_AUX_4
}
# -----------------------


# --- Classes -----------
class LEDs(dbF.Feature):
    """Expose the LEDs over DBus."""

    def __init__(self):
        """Init method."""
        super().__init__()
        self.feature_name = FEATURE_NAME
        self._exception = LEDs_Exception()
        self._obj = LEDs_Obj()


class LEDs_Exception(dbF.FeatureException):
    """Exceptions for the LEDs."""

    def __init__(self, msg=""):
        """Init method."""
        super().__init__(FEATURE_NAME, msg)


class LEDs_Obj(dbF.FeatureObj):
    """DBus object for the LEDs."""

    def __init__(self):
        """Init method."""
        super().__init__(FEATURE_NAME)
        self._atmega = atmega.ATMega()

    # Override DBus object methods

    @dbus.service.method(
        db_cons.BUS_NAME["Feature"],
        in_signature="a{sv}",
        out_signature="a{sv}"
    )
    def getLedStatus(self, args):
        """Get the status of a given LED."""
        self._logger.debug("{}@getLedStatus: INIT".format(self._full_path))
        try:
            led = args.pop(LED_PARAMS["LED"])
        except KeyError:
            self._logger.debug(
                "{}@getLedStatus: LED not specified.".format(self._full_path)
            )
            raise LEDs_Exception("LED not specified.")
        if led not in LED_NAMES.keys():
            self._logger.debug(
                "{}@getLedStatus: Not recognized LED.".format(self._full_path)
            )
            raise LEDs_Exception("Not recognized LED.")
        result = {}
        result[LED_PARAMS["LED"]] = led
        try:
            if led == "S0" or led == "S1":
                color = self._atmega.getLedSocket(LED_NAMES[led])
                result[LED_PARAMS["COLOR"]] = color
            else:
                bright = self._atmega.getLedAux(LED_NAMES[led])
                result[LED_PARAMS["BRIGHT"]] = bright
        except:
            self._logger.debug("{}@getLedStatus: Problem reading from the "
                               "AGILE Maker's Shield.".format(self._full_path))
            raise LEDs_Exception(
                "Problem reading from the AGILE Maker's Shield."
            )
        self._logger.debug("{}@getLedStatus: OK".format(self._full_path))
        return dbus.Dictionary(result, signature="sv")

    @dbus.service.method(
        db_cons.BUS_NAME["Feature"],
        in_signature="a{sv}",
        out_signature=""
    )
    def setLedStatus(self, args):
        """Set the status of a given LED."""
        self._logger.debug("{}@setLedStatus: INIT".format(self._full_path))
        try:
            led = args.pop(LED_PARAMS["LED"])
        except KeyError:
            self._logger.debug(
                "{}@setLedStatus: LED not specified.".format(self._full_path)
            )
            raise LEDs_Exception("LED not specified.")
        if led not in LED_NAMES.keys():
            self._logger.debug(
                "{}@setLedStatus: Not recognized LED.".format(self._full_path)
            )
            raise LEDs_Exception("Not recognized LED.")
        if led == "S0" or led == "S1":
            try:
                color_dbus = args.pop(LED_PARAMS["COLOR"])
                color = []
                color.append(int(color_dbus[0]) & 0xFF)
                color.append(int(color_dbus[1]) & 0xFF)
                color.append(int(color_dbus[2]) & 0xFF)
            except KeyError:
                self._logger.debug("{}@setLedStatus: Color value not "
                                   "specified.".format(self._full_path))
                raise LEDs_Exception("Color value not specified.")
            try:
                self._atmega.setLedSocket(LED_NAMES[led], color)
            except:
                self._logger.debug(
                    "{}@setLedStatus: Problem writing to the AGILE "
                    "Maker's Shield.".format(self._full_path)
                )
                raise LEDs_Exception(
                    "Problem writing to the AGILE Maker's Shield."
                )
        else:
            try:
                bright = int(args.pop(LED_PARAMS["BRIGHT"])) & 0xFF
            except KeyError:
                self._logger.debug("{}@setLedStatus: Bright value not "
                                   "specified.".format(self._full_path))
                raise LEDs_Exception("Bright value not specified.")
            try:
                self._atmega.setLedAux(LED_NAMES[led], bright)
            except:
                self._logger.debug(
                    "{}@setLedStatus: Problem writing to the AGILE "
                    "Maker's Shield.".format(self._full_path)
                )
                raise LEDs_Exception(
                    "Problem writing to the AGILE Maker's Shield."
                )
        self._logger.debug("{}@setLedStatus: OK".format(self._full_path))
# -----------------------
