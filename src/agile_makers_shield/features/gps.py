
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
AGILE DBus Feature GPS.

Description: Class that exposes the control of
             the GPS of the AGILE Maker's Shield over DBus.
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
FEATURE_NAME = "GPS"
GPS_FRAME = {
    "GGA": {
        "type": "GGA",
        "header": "$GPGGA",
        "length": 15,  # Match fields length
        "fields": ["type", "utc", "latitude", "latitudeDir", "longitude",
                   "longitudeDir", "fix", "nsat", "hdop", "altitude",
                   "altitudeUnit", "hog", "hogUnit", "dgpsLast", "dgpsId"]
    },
    "RMC": {
        "type": "RMC",
        "header": "$GPRMC",
        "length": 13,  # Match fields length
        "fields": ["type", "utc", "status", "latitude", "latitudeDir",
                   "longitude", "longitudeDir", "spkn", "angle", "date",
                   "magneticVar", "magneticVarDir", "fix"]
    }
}
# -----------------------


# --- Classes -----------
class GPS(dbF.Feature):
    """Expose the GPS over DBus."""

    def __init__(self):
        """Init method."""
        super().__init__()
        self.feature_name = FEATURE_NAME
        self._exception = GPS_Exception()
        self._obj = GPS_Obj()


class GPS_Exception(dbF.FeatureException):
    """Exceptions for the GPS."""

    def __init__(self, msg=""):
        """Init method."""
        super().__init__(FEATURE_NAME, msg)


class GPS_Obj(dbF.FeatureObj):
    """DBus object for the GPS."""

    def __init__(self):
        """Init method."""
        super().__init__(FEATURE_NAME)
        self._atmega = atmega.ATMega()

    def _frameToArray(self, frame):
        """Parse the GPS frame and convert it to bytearray."""
        return bytearray(frame).decode("utf-8").strip("\x00")[0:-3].split(",")

    def _checkFrame(self, frame, nmeaType):
        """Check if the GPS NMEA frame is valid."""
        length = 0
        while length < len(frame):
            if frame[length] == 0x00:
                break
            length = length + 1
        if length < 10:
            self._logger.debug("{}@getLast{}: Frame is too "
                               "short".format(self._full_path, nmeaType))
            return False
        if frame[0] != ord("$"):
            self._logger.debug("{}@getLast{}: Invalid start of "
                               "frame".format(self._full_path, nmeaType))
            return False
        if frame[length-3] != ord("*"):
            self._logger.debug("{}@getLast{}: Invalid end of "
                               "frame".format(self._full_path, nmeaType))
            return False
        checksum = 0
        for char in frame[1:(length-3)]:
            checksum = checksum ^ char
        checkFrame = (int(chr(frame[length-2]), 16) << 4) | \
            int(chr(frame[length-1]), 16)
        if checksum != checkFrame:
            # self._logger.warning("Checksum failed")
            return False
        return True

    def _getGPSFrame(self, nmeaType, getFrameFunction):
        """Return a dict with the GPS NMEA sentence from the GPS."""
        nmea = GPS_FRAME[nmeaType]
        # Create an empty frame
        gpsFrame = {}
        for field in nmea["fields"]:
            gpsFrame[field] = ""
        gpsFrame["type"] = nmea["type"]
        # Get the frame from the GPS
        frame = getFrameFunction()
        # Check the frame and save the data if it is correct
        if self._checkFrame(frame, nmeaType):
            data = self._frameToArray(frame)
            if (data[0] != nmea["header"]) or (len(data) != nmea["length"]):
                self._logger.debug(
                    "{}@getLast{}: Frame does not match {} "
                    "frame".format(self._full_path, nmeaType, nmeaType)
                )
            else:
                for i, field in enumerate(nmea["fields"]):
                    gpsFrame[field] = data[i]
                gpsFrame["type"] = nmea["type"]
        return gpsFrame

    # Override DBus object methods

    @dbus.service.method(
        db_cons.BUS_NAME["Feature"],
        in_signature="",
        out_signature=""
    )
    def updateGPS(self):
        """Update the GPS with new information."""
        self._logger.debug("{}@updateGPS: INIT".format(self._full_path))
        try:
            self._atmega.updateGPS()
        except:
            self._logger.debug("{}@updateGPS: Problem writing to the AGILE "
                               "Maker's Shield.".format(self._full_path))
            raise GPS_Exception("Problem writing to the AGILE Maker's Shield.")
        self._logger.debug("{}@updateGPS: OK".format(self._full_path))

    @dbus.service.method(
        db_cons.BUS_NAME["Feature"],
        in_signature="",
        out_signature="a{sv}"
    )
    def getLastGGA(self):
        """Return the last GGA frame stored after updating the GPS."""
        self._logger.debug("{}@getLastGGA: INIT".format(self._full_path))
        try:
            result = self._getGPSFrame("GGA", self._atmega.getGPSGGA)
        except:
            self._logger.debug("{}@getLastGGA: Problem reading from the AGILE "
                               "Maker's Shield.".format(self._full_path))
            raise GPS_Exception("Problem reading from the AGILE "
                                "Maker's Shield.")
        self._logger.debug("{}@getLastGGA: OK".format(self._full_path))
        return dbus.Dictionary(result, signature="sv")

    @dbus.service.method(
        db_cons.BUS_NAME["Feature"],
        in_signature="",
        out_signature="a{sv}"
    )
    def getLastRMC(self):
        """Return the last RMC frame stored after updating the GPS."""
        self._logger.debug("{}@getLastRMC: INIT".format(self._full_path))
        try:
            result = self._getGPSFrame("RMC", self._atmega.getGPSGGA)
        except:
            self._logger.debug("{}@getLastRMC: Problem reading from the AGILE "
                               "Maker's Shield.".format(self._full_path))
            raise GPS_Exception("Problem reading from the AGILE "
                                "Maker's Shield.")
        self._logger.debug("{}@getLastRMC: OK".format(self._full_path))
        return dbus.Dictionary(result, signature="sv")
# -----------------------
