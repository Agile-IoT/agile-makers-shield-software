
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
AGILE I2C MCP3424.

Description: Class to communicate with the MCP3424
             in the AGILE Maker's Shield. This allows to
             read the different channels of the ADC.
Author: David Palomares <d.palomares@libelium.com>
Version: 0.1
Date: March 2017
"""


# --- Imports -----------
from agile_makers_shield.buses.i2c import i2c_bus
import time
# -----------------------


# --- Variables ---------
# MCP3424 addresses
MCP3424_ADDRESS = 0x6C
MCP3424_REG = 0x00
DUMMY_DATA = [0x00]
MCP3424_TIMEOUT = 0.5
# MCP3424 configuration
MCP3424_ACTION_RDY = 0x01
MCP3424_SHIFT_ACTION = 7
MCP3424_MASK_RDY = 0x7F
MCP3424_CHANNEL_1 = 0x00
MCP3424_CHANNEL_2 = 0x01
MCP3424_CHANNEL_3 = 0x02
MCP3424_CHANNEL_4 = 0x03
MCP3424_CHANNELS = [
    MCP3424_CHANNEL_1,
    MCP3424_CHANNEL_2,
    MCP3424_CHANNEL_3,
    MCP3424_CHANNEL_4
]
MCP3424_SHIFT_CHANNEL = 5
MCP3424_MODE_ONE_SHOOT = 0x00
MCP3424_MODE_CONTINUOUS = 0x01
MCP3424_MODES = [
    MCP3424_MODE_ONE_SHOOT,
    MCP3424_MODE_CONTINUOUS
]
MCP3424_SHIFT_MODE = 4
MCP3424_RESOLUTION_12 = 0x00
MCP3424_RESOLUTION_14 = 0x01
MCP3424_RESOLUTION_16 = 0x02
MCP3424_RESOLUTION_18 = 0x03
MCP3424_RESOLUTIONS = [
    MCP3424_RESOLUTION_12,
    MCP3424_RESOLUTION_14,
    MCP3424_RESOLUTION_16,
    MCP3424_RESOLUTION_18
]
MCP3424_RESOLUTION_BITS = {  # Read this number of bytes rounded up + 1 byte
    MCP3424_RESOLUTION_12: 12,
    MCP3424_RESOLUTION_14: 14,
    MCP3424_RESOLUTION_16: 16,
    MCP3424_RESOLUTION_18: 18
}
MCP3424_SHIFT_RESOLUTION = 2
MCP3424_PGA_1 = 0x00
MCP3424_PGA_2 = 0x01
MCP3424_PGA_4 = 0x02
MCP3424_PGA_8 = 0x03
MCP3424_PGAS = [
    MCP3424_PGA_1,
    MCP3424_PGA_2,
    MCP3424_PGA_4,
    MCP3424_PGA_8
]
MCP3424_SHIFT_PGA = 0
# -----------------------


# --- Classes -----------
class MCP3424():
    """Read from and write to the MCP3424 via I2C."""

    def __init__(self):
        """Init method."""
        self._bus = i2c_bus.I2C_Bus(MCP3424_ADDRESS)

    def close(self):
        """Close the I2C communication."""
        self._bus.close()

    def read(self, channel, mode=MCP3424_MODE_ONE_SHOOT,
             resolution=MCP3424_RESOLUTION_18, pga=MCP3424_PGA_1):
        """Read the specified channel from the MCP3424."""
        # Check params
        if channel not in MCP3424_CHANNELS:
            raise ValueError("Invalid channel")
        if mode not in MCP3424_MODES:
            raise ValueError("Invalid mode")
        if resolution not in MCP3424_RESOLUTIONS:
            raise ValueError("Invalid resolution")
        if pga not in MCP3424_PGAS:
            raise ValueError("Invalid pga")
        # Configure the MCP3424
        configuration = (MCP3424_ACTION_RDY << MCP3424_SHIFT_ACTION)
        configuration = configuration | (channel << MCP3424_SHIFT_CHANNEL)
        configuration = configuration | (mode << MCP3424_SHIFT_MODE)
        configuration = configuration | \
            (resolution << MCP3424_SHIFT_RESOLUTION)
        configuration = configuration | (pga << MCP3424_SHIFT_PGA)
        # Read the data
        size_bits = MCP3424_RESOLUTION_BITS[resolution]
        size = (size_bits // 8) + ((size_bits % 8) > 0) + 1
        data = self._bus.read(configuration, size)
        if (mode == MCP3424_MODE_ONE_SHOOT):
            ts = time.time()
            while ((data[-1] != (configuration & MCP3424_MASK_RDY)) and
                   ((time.time() - ts) < MCP3424_TIMEOUT)):
                data = self._bus._readRaw(size)
        # Convert the data
        data[0] = data[0] & ((1 << (size_bits % 8)) - 1)
        value = 0
        for byte in data[0:-1]:
            value = (value << 8) | byte
        divisor = 1 << ((resolution * 2) + pga)
        return (value / divisor)
# -----------------------
