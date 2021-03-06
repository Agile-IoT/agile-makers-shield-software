
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
AGILE DBus Protocol ProtocolTemplate.

Description: Class of the Protocol defined in the
             in the AGILE API with the implementation of the
             ProtocolTemplate protocol.
Author: David Palomares <d.palomares@libelium.com>
Version: 0.1
Date: June 2016
"""


# --- Imports -----------
# TODO: Uncomment
# import dbus
# import dbus.service
from agile_makers_shield.buses.dbus import protocol_base as dbP
# TODO: Uncomment
# from agile_makers_shield.buses.dbus import constants as db_cons
# import logging
# -----------------------


# --- Variables ---------
PROTOCOL_NAME = "ProtocolTemplate"  # TODO: Search and replace
# -----------------------


# --- Classes -----------
class ProtocolTemplate(dbP.Protocol):
    """Expose the Protocol over DBus."""

    def __init__(self):
        """Init method."""
        super().__init__()
        self._protocol_name = PROTOCOL_NAME
        self._exception = ProtocolTemplate_Exception()
        self._objS0 = ProtocolTemplate_Obj(self._socket0)
        self._objS1 = ProtocolTemplate_Obj(self._socket1)


class ProtocolTemplate_Exception(dbP.ProtocolException):
    """Exceptions for the Protocol."""

    def __init__(self, msg=""):
        """Init method."""
        super().__init__(PROTOCOL_NAME, msg)


class ProtocolTemplate_Obj(dbP.ProtocolObj):
    """DBus object for the Protocol."""

    def __init__(self, socket):
        """Init method."""
        super().__init__(PROTOCOL_NAME, socket)

    # Override DBus object methods

    # TODO
# -----------------------
