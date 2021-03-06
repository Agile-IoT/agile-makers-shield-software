
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
AGILE I2C Bus.

Description: Class to read from and write to
             the I2C bus of the Raspberry Pi.
Author: David Palomares <d.palomares@libelium.com>
Version: 0.1
Date: February 2016
"""


# --- Imports -----------
import io
import fcntl
import time
# -----------------------


# --- Variables ---------
I2C_SLAVE = 0x0703
I2C_DEVICE = "/dev/i2c-1"
BUFFER_SIZE = 32
TRIES = 10
GUARDTIME = 0.1
ERROR = []
# -----------------------


# --- Classes -----------
class I2C_Bus:
    """Read from and write to the I2C bus."""

    def __init__(self, device):
        """Init method."""
        self._fr = io.open(I2C_DEVICE, "rb", buffering=0)
        self._fw = io.open(I2C_DEVICE, "wb", buffering=0)
        fcntl.ioctl(self._fr, I2C_SLAVE, device)
        fcntl.ioctl(self._fw, I2C_SLAVE, device)

    def _readRaw(self, size):
        """Read a list of bytes of the specified size from the device."""
        for i in range(TRIES):
            try:
                data = self._fr.read(size)
            except IOError:
                time.sleep(GUARDTIME)
            else:
                return list(data)
        return ERROR

    def _writeRaw(self, data):
        """Write a list of bytes to the device."""
        for i in range(TRIES):
            try:
                self._fw.write(bytes(data))
            except IOError:
                time.sleep(GUARDTIME)
            else:
                return True
        return False

    def read(self, reg, size):
        """Read a list of bytes from a register of the device."""
        if self._writeRaw([reg]):
            data = []
            for i in range(size // BUFFER_SIZE):
                chunk = self._readRaw(BUFFER_SIZE)
                if not chunk:
                    return ERROR
                data = data + chunk
            if not ((size % BUFFER_SIZE) == 0):
                chunk = self._readRaw(size % BUFFER_SIZE)
                if not chunk:
                    return ERROR
                data = data + chunk
            return data
        else:
            return ERROR

    def write(self, reg, data):
        """Write a list of bytes to the register of the device."""
        for i in range(len(data) // BUFFER_SIZE):
            if not self._writeRaw(
                [reg] + data[(i * BUFFER_SIZE):((i + 1) * BUFFER_SIZE)]
            ):
                return False
            if not self._readRaw(1):
                return False
        if not ((len(data) % BUFFER_SIZE) == 0):
            if not self._writeRaw([reg] + data[-(len(data) % BUFFER_SIZE):]):
                return False
            if not self._readRaw(1):
                return False
        return True

    def close(self):
        """Close the I2C communication."""
        self._fw.close()
        self._fr.close()
# -----------------------
