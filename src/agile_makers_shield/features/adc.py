
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
AGILE DBus Feature ADC.

Description: Class that exposes the control of
             the ADC of the AGILE Maker's Shield over DBus.
Author: David Palomares <d.palomares@libelium.com>
Version: 0.1
Date: April 2017
"""


# --- Imports -----------
import dbus
import dbus.service
from agile_makers_shield.buses.dbus import feature_base as dbF
from agile_makers_shield.buses.dbus import constants as db_cons
from agile_makers_shield.buses.i2c import mcp3424
# -----------------------


# --- Variables ---------
FEATURE_NAME = "ADC"
ADC_PARAMS = {
    "CHANNEL": "channel",
    "MODE": "mode",
    "RESOLUTION": "resolution",
    "PGA": "pga",
    "VALUE": "value"
}
ADC_DEFAULTS = {
    "MODE": "one_shoot",
    "RESOLUTION": 18,
    "PGA": 1
}
ADC_CHANNELS = {
    1: mcp3424.MCP3424_CHANNEL_1,
    2: mcp3424.MCP3424_CHANNEL_2,
    3: mcp3424.MCP3424_CHANNEL_3,
    4: mcp3424.MCP3424_CHANNEL_4
}
ADC_MODES = {
    "one_shoot": mcp3424.MCP3424_MODE_ONE_SHOOT,
    "continuous": mcp3424.MCP3424_MODE_CONTINUOUS
}
ADC_RESOLUTIONS = {
    12: mcp3424.MCP3424_RESOLUTION_12,
    14: mcp3424.MCP3424_RESOLUTION_14,
    16: mcp3424.MCP3424_RESOLUTION_16,
    18: mcp3424.MCP3424_RESOLUTION_18
}
ADC_PGAS = {
    1: mcp3424.MCP3424_PGA_1,
    2: mcp3424.MCP3424_PGA_2,
    4: mcp3424.MCP3424_PGA_4,
    8: mcp3424.MCP3424_PGA_8
}
# -----------------------


# --- Classes -----------
class ADC(dbF.Feature):
    """Expose the ADC over DBus."""

    def __init__(self):
        """Init method."""
        super().__init__()
        self.feature_name = FEATURE_NAME
        self._exception = ADC_Exception()
        self._obj = ADC_Obj()


class ADC_Exception(dbF.FeatureException):
    """Exceptions for the ADC."""

    def __init__(self, msg=""):
        """Init method."""
        super().__init__(FEATURE_NAME, msg)


class ADC_Obj(dbF.FeatureObj):
    """DBus object for the ADC."""

    def __init__(self):
        """Init method."""
        super().__init__(FEATURE_NAME)
        self._mcp3424 = mcp3424.MCP3424()

    # Override DBus object methods

    @dbus.service.method(
        db_cons.BUS_NAME["Feature"],
        in_signature="a{sv}",
        out_signature="a{sv}"
    )
    def readADC(self, args):
        """Read the ADC and return the result over DBus."""
        self._logger.debug("{}@readADC: INIT".format(self._full_path))
        try:
            channel = args.pop(ADC_PARAMS["CHANNEL"])
        except KeyError:
            self._logger.debug(
                "{}@readADC: Channel not specified".format(self._full_path)
            )
            raise ADC_Exception("Channel not specified.")
        if channel not in ADC_CHANNELS.keys():
            self._logger.debug(
                "{}@readADC: Invalid channel".format(self._full_path)
            )
            raise ADC_Exception("Invalid channel.")
        mode = args.pop(ADC_PARAMS["MODE"], ADC_DEFAULTS["MODE"])
        if mode not in ADC_MODES.keys():
            self._logger.debug(
                "{}@readADC: Invalid mode".format(self._full_path)
            )
            raise ADC_Exception("Invalid mode.")
        resolution = args.pop(
            ADC_PARAMS["RESOLUTION"],
            ADC_DEFAULTS["RESOLUTION"]
        )
        if resolution not in ADC_RESOLUTIONS.keys():
            self._logger.debug(
                "{}@readADC: Invalid resolution".format(self._full_path)
            )
            raise ADC_Exception("Invalid resolution.")
        pga = args.pop(ADC_PARAMS["PGA"], ADC_DEFAULTS["PGA"])
        if pga not in ADC_PGAS.keys():
            self._logger.debug(
                "{}@readADC: Invalid pga".format(self._full_path)
            )
            raise ADC_Exception("Invalid pga.")
        try:
            value = self._mcp3424.read(
                ADC_CHANNELS[channel],
                ADC_MODES[mode],
                ADC_RESOLUTIONS[resolution],
                ADC_PGAS[pga]
            )
        except:
            self._logger.debug("{}@readADC: Problem reading from the "
                               "AGILE Maker's Shield".format(self._full_path))
            raise ADC_Exception("Problem reading from "
                                "the AGILE Maker's Shield.")
        result = {}
        result[ADC_PARAMS["CHANNEL"]] = channel
        result[ADC_PARAMS["VALUE"]] = value
        self._logger.debug("{}@readADC: OK".format(self._full_path))
        return dbus.Dictionary(result, signature="sv")
# -----------------------
