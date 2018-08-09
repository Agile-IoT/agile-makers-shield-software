
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
AGILE DBus Feature Atmospheric Sensor.

Description: Class that exposes the control of
             the Atmospheric Sensor of the AGILE Maker's
             Shield over DBus.
Author: David Palomares <d.palomares@libelium.com>
Version: 0.1
Date: April 2017
"""


# --- Imports -----------
import dbus
import dbus.service
from agile_makers_shield.buses.dbus import feature_base as dbF
from agile_makers_shield.buses.dbus import constants as db_cons
from agile_makers_shield.buses.i2c import bme280
# -----------------------


# --- Variables ---------
FEATURE_NAME = "Atmospheric_Sensor"
SENSOR_PARAMS = {
    "TEMPERATURE": "temperature",
    "HUMIDITY": "humidity",
    "PRESSURE": "pressure"
}
# -----------------------


# --- Classes -----------
class Atmospheric_Sensor(dbF.Feature):
    """Expose the Atmospheric Sensor over DBus."""

    def __init__(self):
        """Init method."""
        super().__init__()
        self.feature_name = FEATURE_NAME
        self._exception = Atmospheric_Sensor_Exception()
        self._obj = Atmospheric_Sensor_Obj()


class Atmospheric_Sensor_Exception(dbF.FeatureException):
    """Exceptions for the Atmospheric Sensor."""

    def __init__(self, msg=""):
        """Init method."""
        super().__init__(FEATURE_NAME, msg)


class Atmospheric_Sensor_Obj(dbF.FeatureObj):
    """DBus object for the Atmospheric Sensor."""

    def __init__(self):
        """Init method."""
        super().__init__(FEATURE_NAME)
        self._bme280 = bme280.BME280()

    # Override DBus object methods

    @dbus.service.method(
        db_cons.BUS_NAME["Feature"],
        in_signature="",
        out_signature="a{sv}"
    )
    def readAtmosphericSensor(self):
        """Read the Atmospheric Sensor and return the result over DBus."""
        self._logger.debug(
            "{}@readAtmosphericSensor: INIT".format(self._full_path)
        )
        try:
            temperature = self._bme280.getTemperature()
            humidity = self._bme280.getHumidity()
            pressure = self._bme280.getPressure()
        except:
            self._logger.debug(
                "{}@readAtmosphericSensor: Problem reading "
                "from the AGILE Maker's Shield".format(self._full_path)
            )
            raise Atmospheric_Sensor_Exception(
                "Problem reading from the AGILE Maker's Shield."
            )
        result = {}
        result[SENSOR_PARAMS["TEMPERATURE"]] = temperature
        result[SENSOR_PARAMS["HUMIDITY"]] = humidity
        result[SENSOR_PARAMS["PRESSURE"]] = pressure
        self._logger.debug(
            "{}@readAtmosphericSensor: OK".format(self._full_path)
        )
        return dbus.Dictionary(result, signature="sv")
# -----------------------
