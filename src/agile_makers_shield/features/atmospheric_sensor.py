
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
#         AGILE DBus Feature Atmospheric Sensor         #
#                                                       #
#    Description: Class that exposes the control of     #
#       the Atmospheric Sensor of the AGILE Maker's     #
#       Shield over DBus.                               #
#    Author: David Palomares <d.palomares@libelium.com> #
#    Version: 0.1                                       #
#    Date: April 2017                                   #
#########################################################

# --- Imports -----------
import dbus
import dbus.service
from agile_makers_shield.buses.dbus import feature_base as dbF
from agile_makers_shield.buses.dbus import constants as db_cons
from agile_makers_shield.buses.i2c import bme280
import logging
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

   def __init__(self):
      super().__init__()
      self.feature_name = FEATURE_NAME
      self._exception = Atmospheric_Sensor_Exception()
      self._obj = Atmospheric_Sensor_Obj()


class Atmospheric_Sensor_Exception(dbF.FeatureException):

   def __init__(self, msg=""):
      super().__init__(FEATURE_NAME, msg)


class Atmospheric_Sensor_Obj(dbF.FeatureObj):

   def __init__(self):
      super().__init__(FEATURE_NAME)
      self._bme280 = bme280.BME280()

   # Override DBus object methods
   @dbus.service.method(db_cons.BUS_NAME["Feature"], in_signature="", out_signature="a{sv}")
   def readAtmosphericSensor(self):
      self._logger.debug("{}@readAtmosphericSensor: INIT".format(self._full_path))
      try:
         temperature = self._bme280.getTemperature()
         humidity = self._bme280.getHumidity()
         pressure = self._bme280.getPressure()
      except:
         self._logger.debug("{}@readAtmosphericSensor: Problem reading from the AGILE Maker's Shield".format(self._full_path))
         raise LEDs_Exception("Problem reading from the AGILE Maker's Shield.")
      result = {}
      result[SENSOR_PARAMS["TEMPERATURE"]] = temperature
      result[SENSOR_PARAMS["HUMIDITY"]] = humidity
      result[SENSOR_PARAMS["PRESSURE"]] = pressure
      self._logger.debug("{}@readAtmosphericSensor: OK".format(self._full_path))
      return dbus.Dictionary(result, signature="sv")
# -----------------------
