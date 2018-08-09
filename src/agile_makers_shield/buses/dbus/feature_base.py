
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
AGILE DBus Feature Base.

Description: Base class for the features of the
             AGILE Maker's Shield over DBus.
Author: David Palomares <d.palomares@libelium.com>
Version: 0.1
Date: April 2017
"""


# --- Imports -----------
import dbus
import dbus.service
from agile_makers_shield.buses.dbus import constants as db_cons
import logging
# -----------------------


# --- Classes -----------
class FeatureException(dbus.DBusException):
    """Base class for feature exceptions."""

    def __init__(self, feature_name, msg=""):
        """Init method."""
        if msg == "":
            super().__init__("Exception")
        else:
            super().__init__(msg)
        self._dbus_error_name = db_cons.BUS_NAME["Feature"] + \
            "." + feature_name


class FeatureObj(dbus.service.Object):
    """Base class for the DBus feature objects."""

    def __init__(self, feature_name):
        """Init method."""
        self._logger = logging.getLogger(db_cons.LOGGER_NAME)
        self._bus_name = db_cons.BUS_NAME["Feature"]
        self._obj_path = db_cons.OBJ_PATH["Feature"]
        self._feature_name = feature_name
        self._connected = False
        self._full_path = self._obj_path + "/" + feature_name
        super().__init__(dbus.SessionBus(), self._full_path)

    # AGILE API Methods

    @dbus.service.method(
        db_cons.BUS_NAME["Feature"],
        in_signature="",
        out_signature="s"
    )
    def Name(self):
        """Return the name of the feature."""
        return self._feature_name


class Feature():
    """Base class for the features of the Maker's Shield."""

    def __init__(self):
        """Init method."""
        self._name = dbus.service.BusName(
            db_cons.BUS_NAME["Feature"],
            dbus.SessionBus()
        )
# -----------------------
