
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
AGILE DBus Protocol Base.

Description: Base class of the Protocol defined
             in the AGILE API with all the operations. Other
             classes can inherit and extend this class to
             implement the different protocols.
Author: David Palomares <d.palomares@libelium.com>
Version: 0.1
Date: June 2016
"""


# --- Imports -----------
import dbus
import dbus.service
from agile_makers_shield.buses.dbus import constants as db_cons
import logging
# -----------------------


# --- Classes -----------
class ProtocolException(dbus.DBusException):
    """Base class for protocol exceptions."""

    def __init__(self, protocol_name, msg=""):
        """Init method."""
        if msg == "":
            super().__init__("Exception")
        else:
            super().__init__(msg)
        self._dbus_error_name = db_cons.BUS_NAME["Protocol"] + \
            "." + protocol_name


class ProtocolObj(dbus.service.Object):
    """Base class for the DBus protocol objects."""

    def __init__(self, protocol_name, socket):
        """Init method."""
        self._logger = logging.getLogger(db_cons.LOGGER_NAME)
        self._bus_name = db_cons.BUS_NAME["Protocol"]
        self._obj_path = db_cons.OBJ_PATH["Protocol"]
        self._socket = socket
        self._protocol_name = protocol_name
        self._connected = False
        self._full_path = self._obj_path + "/" + protocol_name + "/" + socket
        super().__init__(dbus.SessionBus(), self._full_path)

    def _getConnected(self):
        return self._connected

    def _setConnected(self, status):
        if status:
            self._connected = True
        else:
            self._connected = False

    def _getSocketDev(self, socket):
        return db_cons.SOCKETDEV[socket]

    # AGILE API Methods

    @dbus.service.method(
        db_cons.BUS_NAME["Protocol"],
        in_signature="",
        out_signature="b"
    )
    def Connected(self):
        """Return the connection status."""
        return self._getConnected()

    @dbus.service.method(
        db_cons.BUS_NAME["Protocol"],
        in_signature="",
        out_signature="s"
    )
    def Driver(self):
        """Return the driver used."""
        return "No driver."

    @dbus.service.method(
        db_cons.BUS_NAME["Protocol"],
        in_signature="",
        out_signature="s"
    )
    def Name(self):
        """Return the name of the protocol."""
        return self._protocol_name

    @dbus.service.method(
        db_cons.BUS_NAME["Protocol"],
        in_signature="",
        out_signature=""
    )
    def Connect(self):
        """Connect method of the protocol."""
        raise ProtocolException(self._protocol_name, "Function not supported.")

    @dbus.service.method(
        db_cons.BUS_NAME["Protocol"],
        in_signature="",
        out_signature=""
    )
    def Disconnect(self):
        """Disconnect method of the protocol."""
        raise ProtocolException(self._protocol_name, "Function not supported.")

    @dbus.service.method(
        db_cons.BUS_NAME["Protocol"],
        in_signature="a{sv}",
        out_signature=""
    )
    def Discover(self, args):
        """Discover method of the protocol."""
        raise ProtocolException(self._protocol_name, "Function not supported.")

    @dbus.service.method(
        db_cons.BUS_NAME["Protocol"],
        in_signature="sa{sv}",
        out_signature=""
    )
    def Exec(self, op, args):
        """Exec method of the protocol."""
        raise ProtocolException(self._protocol_name, "Function not supported.")

    @dbus.service.method(
        db_cons.BUS_NAME["Protocol"],
        in_signature="a{sv}",
        out_signature=""
    )
    def Setup(self, args):
        """Setup method of the protocol."""
        raise ProtocolException(self._protocol_name, "Function not supported.")

    @dbus.service.method(
        db_cons.BUS_NAME["Protocol"],
        in_signature="a{sv}",
        out_signature=""
    )
    def Send(self, args):
        """Send method of the protocol."""
        raise ProtocolException(self._protocol_name, "Function not supported.")

    @dbus.service.method(
        db_cons.BUS_NAME["Protocol"],
        in_signature="",
        out_signature="a{sv}"
    )
    def Receive(self):
        """Receive method of the protocol."""
        raise ProtocolException(self._protocol_name, "Function not supported.")

    @dbus.service.method(
        db_cons.BUS_NAME["Protocol"],
        in_signature="a{sv}",
        out_signature=""
    )
    def Subscribe(self, args):
        """Subscribe method of the protocol."""
        raise ProtocolException(self._protocol_name, "Function not supported.")


class Protocol():
    """Base class for the protocols of the Maker's Shield."""

    def __init__(self):
        """Init method."""
        self._socket0 = db_cons.SOCKET0
        self._socket1 = db_cons.SOCKET1
        self._name = dbus.service.BusName(
            db_cons.BUS_NAME["Protocol"],
            dbus.SessionBus()
        )
# -----------------------
