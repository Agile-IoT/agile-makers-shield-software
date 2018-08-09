
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
AGILE DBus Constants.

Description: Constant variables of the AGILE
             DBus Protocol API.
Author: David Palomares <d.palomares@libelium.com>
Version: 0.1
Date: November 2016
"""


# --- Imports -----------
from agile_makers_shield.buses.i2c import atmega
# -----------------------


# --- Variables ---------
LOGGER_NAME = "AGILE_DBus"
BUS_NAME = {
    "Base": "iot.agile.MakersShield",
    "Protocol": "iot.agile.Protocol",
    "Feature": "iot.agile.Feature"
}
OBJ_PATH = {
    "Base": "/iot/agile/MakersShield",
    "Protocol": "/iot/agile/Protocol",
    "Feature": "/iot/agile/Feature"
}
SOCKET0 = "socket0"
SOCKET1 = "socket1"
SOCKET0DEV = atmega.SOCKET_0
SOCKET1DEV = atmega.SOCKET_1
SOCKETDEV = {SOCKET0: SOCKET0DEV, SOCKET1: SOCKET1DEV}
# -----------------------
