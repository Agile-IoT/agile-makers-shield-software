
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
AGILE DBus Protocol XBee ZigBee.

Description: Class of the Protocol defined in the
             in the AGILE API with the implementation of the
             XBee ZigBee protocol.
Author: David Palomares <d.palomares@libelium.com>
Version: 0.3
Date: May 2017
"""


# --- Imports -----------
import dbus
import dbus.service
import signal
from agile_makers_shield.buses.serial import serial_bus as serial
from agile_makers_shield.buses.dbus import protocol_base as dbP
from agile_makers_shield.buses.dbus import constants as db_cons
import xbee
import time
# -----------------------


# --- Variables ---------
PROTOCOL_NAME = "XBee_ZigBee"
BAUDRATE = "baudrate"
DEF_BAUDRATE = 9600
APIMODE2 = "apiMode2"
DEF_APIMODE2 = False
ATCMDS = "atCmds"
APITXCMDS = [
    "at",
    "queued_at",
    "remote_at",
    "tx_long_addr",
    "tx",
    "tx_explicit"
]
CMDWRITE = b"WR"
TIMEOUT = 2
GUARDTIME = 0.3
# -----------------------


# --- Classes -----------
class XBee_ZigBee(dbP.Protocol):
    """Expose the XBee ZigBee over DBus."""

    def __init__(self):
        """Init method."""
        super().__init__()
        self._protocol_name = PROTOCOL_NAME
        self._objS0 = XBee_ZigBee_Obj(self._socket0)
        self._objS1 = XBee_ZigBee_Obj(self._socket1)


class XBee_ZigBee_Exception(dbP.ProtocolException):
    """Exceptions for XBee ZigBee."""

    def __init__(self, msg=""):
        """Init method."""
        super().__init__(PROTOCOL_NAME, msg)


class XBee_ZigBee_Obj(dbP.ProtocolObj):
    """DBus object for XBee ZigBee."""

    def __init__(self, socket):
        """Init method."""
        super().__init__(PROTOCOL_NAME, socket)
        self._setup = {
            BAUDRATE: DEF_BAUDRATE,
            APIMODE2: DEF_APIMODE2,
            ATCMDS: []
        }
        self._received_data = []

    # FIXME: To use as callback function for XBee, but multithread
    # doesn't work well with DBus, so instead a blocking function
    # will be called, and killed if timeouts with a signal.
    # See also _get_module_data
    def _update_data(self, data):
        self._logger("{}@Data: {}".format(self._full_path), data)
        self._received_data.append(data)

    # FIXME: This function should get the new data from the module,
    # instead _get_module_data will be used
    def _get_module_data_callback(self):
        data = {}
        limit = time.time() + TIMEOUT
        while (time.time() < limit) and not data:
            try:
                data = self._received_data.pop(0)
            except IndexError:
                pass
        return data

    def _timeout_handler(self, signum, frame):
        raise IOError("Timeout reading from the XBee module.")

    def _get_module_data(self):
        data = {}
        signal.signal(signal.SIGALRM, self._timeout_handler)
        signal.alarm(TIMEOUT)
        try:
            data = self._module.wait_read_frame()
        except IOError:
            pass
        finally:
            signal.alarm(0)
        return data

    # Override DBus object methods

    @dbus.service.method(
        db_cons.BUS_NAME["Protocol"],
        in_signature="",
        out_signature=""
    )
    def Connect(self):
        """Connect to the XBee ZigBee module."""
        self._logger.debug("{}@Connect: Connect INIT".format(self._full_path))
        if self._getConnected():
            self._logger.debug("{}@Connect: Module is already "
                               "connected".format(self._full_path))
            raise XBee_ZigBee_Exception("Module is already connected.")
        self._serial = serial.Serial(
            self._getSocketDev(self._socket),
            self._setup[BAUDRATE]
        )
        time.sleep(GUARDTIME)
        self._serial.flush()
        # FIXME: See _update_data
        # self._module = xbee.ZigBee(
        #     self._serial,
        #     escaped=self._setup[APIMODE2],
        #     callback=self._update_data
        # )
        self._module = xbee.ZigBee(self._serial, escaped=self._setup[APIMODE2])
        writeChanges = False
        for option in self._setup[ATCMDS]:
            cmd = list(option.keys())[0]
            param = list(option.values())[0]
            cmdEnc = cmd.encode("UTF-8")
            if (cmdEnc == CMDWRITE):
                writeChanges = True
                break
            paramEnc = b"\x00"
            blen = (param.bit_length() + 7) // 8
            if blen != 0:
                paramEnc = param.to_bytes(blen, byteorder="big")
            time.sleep(GUARDTIME)
            self._logger.debug(
                "{}@Connect: Sending AT command={}, parameter={}".format(
                    self._full_path,
                    cmdEnc,
                    paramEnc
                )
            )
            self._module.send(
                "at",
                frame_id=b"R",
                command=cmdEnc,
                parameter=paramEnc
            )
            rx = self._get_module_data()
            if not rx or not rx["status"]:
                self._logger.debug("{}@Connect: Did not receive response from "
                                   "AT command".format(self._full_path))
                self._serial.close()
                raise XBee_ZigBee_Exception(
                    "Did not receive response from AT command"
                )
            if rx["status"] != b"\x00":
                self._logger.debug(
                    "{}@Connect: Wrong AT command/parameter ({}/{})".format(
                        self._full_path,
                        cmd,
                        param
                    )
                )
                self._serial.close()
                raise XBee_ZigBee_Exception(
                    "Wrong AT command/parameter ({}/{})".format(cmd, param)
                )
        if writeChanges:
            self._logger.debug(
                "{}@Connect: Writting changes".format(self._full_path)
            )
            self._module.send("at", frame_id=b"R", command=CMDWRITE)
            rx = self._get_module_data()
            if not rx or not rx["status"]:
                self._logger.debug("{}@Connect: Did not receive response from "
                                   "AT command".format(self._full_path))
                raise XBee_ZigBee_Exception(
                    "Did not receive response from AT command"
                )
        self._setConnected(True)
        self._logger.debug("{}@Connect: Connect OK".format(self._full_path))

    @dbus.service.method(
        db_cons.BUS_NAME["Protocol"],
        in_signature="",
        out_signature=""
    )
    def Disconnect(self):
        """Disconnect from the XBee ZigBee module."""
        self._logger.debug(
            "{}@Disconnect: Disconnect INIT".format(self._full_path)
        )
        if not self._getConnected():
            self._logger.debug("{}@Disconnect: Module is already "
                               "disconnected".format(self._full_path))
            raise XBee_ZigBee_Exception("Module is already disconnected.")
        self._setConnected(False)
        self._module.halt()
        self._serial.close()
        self._logger.debug(
            "{}@Disconnect: Disconnect OK".format(self._full_path)
        )

    @dbus.service.method(
        db_cons.BUS_NAME["Protocol"],
        in_signature="a{sv}",
        out_signature=""
    )
    def Setup(self, args):
        """Configure the XBee ZigBee module."""
        self._logger.debug("{}@Setup: Setup INIT".format(self._full_path))
        self._setup.clear()
        self._setup = {
            BAUDRATE: DEF_BAUDRATE,
            APIMODE2: DEF_APIMODE2,
            ATCMDS: []
        }
        for key in args.keys():
            if key == BAUDRATE:
                self._setup[BAUDRATE] = int(args[BAUDRATE])
            elif key == APIMODE2:
                self._setup[APIMODE2] = bool(args[APIMODE2])
            else:
                try:
                    param = int(args[key], 16)
                except ValueError:
                    param = 0x00
                finally:
                    self._setup[ATCMDS].append({str(key): param})
        self._logger.debug("{}@Setup: Setup OK".format(self._full_path))

    @dbus.service.method(
        db_cons.BUS_NAME["Protocol"],
        in_signature="a{sv}",
        out_signature=""
    )
    def Send(self, args):
        """Send using the XBee ZigBee module."""
        self._logger.debug("{}@Send: Send INIT".format(self._full_path))
        if not self._getConnected():
            self._logger.debug(
                "{}@Send: Module is not connected".format(self._full_path)
            )
            raise XBee_ZigBee_Exception("Module is not connected.")
        cmd = args.pop("api_command", "")
        if cmd not in APITXCMDS:
            self._logger.debug("{}@Send: A valid API command must be "
                               "provided".format(self._full_path))
            raise XBee_ZigBee_Exception(
                "A valid API command must be provided {}.".format(APITXCMDS)
            )
        params = {}
        for key in args.keys():
            if type(args[key]) == dbus.Array:
                params[key] = bytes(args[key])
        self._logger.debug("{}@Send: Sending {} with params "
                           "{}".format(self._full_path, cmd, params))
        self._module.send(cmd, **params)
        self._logger.debug("{}@Send: Send OK".format(self._full_path))

    @dbus.service.method(
        db_cons.BUS_NAME["Protocol"],
        in_signature="",
        out_signature="a{sv}"
    )
    def Receive(self):
        """Receive using the XBee ZigBee module."""
        self._logger.debug("{}@Receive: Receive INIT".format(self._full_path))
        if not self._getConnected():
            self._logger.debug(
                "{}@Receive: Module is not connected".format(self._full_path)
            )
            raise XBee_ZigBee_Exception("Module is not connected.")
        rx = self._get_module_data()
        result = {}
        for key in rx.keys():
            result[key] = []
            for byte in rx[key]:
                result[key].append(byte)
        self._logger.debug(
            "{}@Receive: Received {}".format(self._full_path, result)
        )
        self._logger.debug("{}@Receive: Receive OK".format(self._full_path))
        return dbus.Dictionary(result, signature="sv")
# -----------------------
