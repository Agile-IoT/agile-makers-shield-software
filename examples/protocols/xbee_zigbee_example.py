#!/usr/bin/env python3


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
GE Link Bulb Control.

Description: Program to control a GE Link Bulb
             via a XBee ZigBee module with the AGILE Maker's
             Shield. Functions allow to turn on, of, toggle
             dim or blink the bulb
Author: David Palomares <d.palomares@libelium.com>
Version: 2.0
Date: May 2016
"""


# --- Imports -----------
import sys
import signal
import time
import tkinter as tk
import dbus
# -----------------------


# --- Variables ---------
# GE Link Bulb
# XXX: Your bulb's MAC here
GE_LINK_BULB_MAC = [0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07]
# DBus
BUS_NAME = "iot.agile.Protocol"
OBJ_PATH = "/iot/agile/Protocol"
SOCKET0 = "socket0"
SOCKET1 = "socket1"
XBEE_ZB = "XBee_ZigBee"
zb = None
# ZigBee
setup_params = {
    "baudrate": 9600,
    "apiMode2": False,
    "NJ": "FF",
    "ZS": "02",
    "EE": "01"
}
zb_explicit_command = {
    "api_command": "tx_explicit",
    "frame_id": [0x04],
    "dest_addr_long": [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFF, 0xFF],
    "dest_addr": [0xFF, 0xFE],
    "src_endpoint": [0x00],
    "dest_endpoint": [0x01],
    "cluster": [0x00, 0x00],
    "profile": [0x01, 0x04],
    "broadcast_radius": [0x00],
    "options": [0x00],
    "data": [0x00]
}
CLUSTER_A = [0x00, 0x06]
CLUSTER_B = [0x00, 0x08]
DATA_ON = [0x01, 0x00, 0x01, 0x00, 0x10]
DATA_OFF = [0x01, 0x00, 0x00, 0x00, 0x10]
DATA_TOGGLE = [0x01, 0x00, 0x02, 0x00, 0x10]
DATA_DIM = [0x01, 0x00, 0x04, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x10]
DATA_DIM_PARAM = 3
# -----------------------


# --- Functions ---------
def bulb_on():
    """Turn the GE Link Bulb On."""
    tx = zb_explicit_command
    tx["dest_addr_long"] = GE_LINK_BULB_MAC
    tx["cluster"] = CLUSTER_A
    tx["data"] = DATA_ON
    zb.Send(tx)


def bulb_off():
    """Turn the GE Link Bulb On."""
    tx = zb_explicit_command
    tx["dest_addr_long"] = GE_LINK_BULB_MAC
    tx["cluster"] = CLUSTER_A
    tx["data"] = DATA_OFF
    zb.Send(tx)


def bulb_toggle():
    """Toggle the GE Link Bulb."""
    tx = zb_explicit_command
    tx["dest_addr_long"] = GE_LINK_BULB_MAC
    tx["cluster"] = CLUSTER_A
    tx["data"] = DATA_TOGGLE
    zb.Send(tx)


def bulb_dim(bright):
    """Set the bright of the GE Link Bulb between 100% (0xFF) and 0% (0x00)."""
    bright = bright & 0xFF
    data = DATA_DIM
    data[DATA_DIM_PARAM] = bright
    tx = zb_explicit_command
    tx["dest_addr_long"] = GE_LINK_BULB_MAC
    tx["cluster"] = CLUSTER_B
    tx["data"] = data
    zb.Send(tx)


def bulb_dim_call():
    """Call to bulb_dim with the bright set in the slider."""
    bright = int((dimSlider.get() * 0xFF) / 100)
    bulb_dim(bright)


def bulb_blink(times=5, speed=0.25):
    """Blink the GE Link Bulb the specified number of times."""
    for i in range(times):
        bulb_toggle()
        time.sleep(speed)
        bulb_toggle()
        time.sleep(speed)


def bulb_blink_call():
    """Call to bulb_dim with the times and the speed set."""
    times = blinkSlider.get()
    bulb_blink(times)


def setup():
    """Set the default parameters of the program."""
    global zb
    # Signal handler (Ctrl+C exit)
    signal.signal(signal.SIGINT, signal_handler)
    # DBus
    session_bus = dbus.SessionBus()
    objXBZB = session_bus.get_object(
        BUS_NAME,
        OBJ_PATH + "/" + XBEE_ZB + "/" + SOCKET0
    )
    zb = dbus.Interface(objXBZB, dbus_interface=BUS_NAME)
    # ZigBee
    zb.Setup(dbus.Dictionary(setup_params, signature="sv"))
    zb.Connect()


def signal_handler(signal, frame):
    """Handle the SIGINT signal."""
    print()
    end_program(0)


def end_program(status):
    """Exit the program."""
    zb.Disconnect()
    sys.exit(status)
# -----------------------


# --- Main program ------
if __name__ == "__main__":

    setup()

    # Root window
    root = tk.Tk()
    root.wm_title("GE Link Bulb Control")
    root.rowconfigure(1, weight=1)
    root.columnconfigure(0, weight=1)
    root.minsize(width=270, height=95)
    root.maxsize(width=270, height=95)
    root.resizable(width=tk.FALSE, height=tk.FALSE)

    # Frames
    frameOnOff = tk.Frame(root)
    frameOnOff.grid(row=0, column=0, sticky=tk.N+tk.S+tk.E+tk.W)
    frameOnOff.columnconfigure(0, weight=1)
    frameOnOff.columnconfigure(1, weight=1)
    frameOnOff.columnconfigure(2, weight=1)
    frameDimBlink = tk.Frame(root)
    frameDimBlink.grid(row=1, column=0, sticky=tk.N+tk.S+tk.E+tk.W)
    frameDimBlink.rowconfigure(0, weight=1)
    frameDimBlink.columnconfigure(0, weight=1)
    frameDimBlink.columnconfigure(1, weight=1)
    frameSliders = tk.Frame(root)
    frameSliders.grid(row=2, column=0, sticky=tk.N+tk.S+tk.E+tk.W)
    frameSliders.rowconfigure(0, weight=1)
    frameSliders.columnconfigure(0, weight=1)
    frameSliders.columnconfigure(1, weight=1)

    # On/Off/Toggle
    onButton = tk.Button(frameOnOff, text="Turn ON", command=bulb_on)
    onButton.grid(row=0, column=0, sticky=tk.N+tk.S+tk.E+tk.W)
    offButton = tk.Button(frameOnOff, text="Turn OFF", command=bulb_off)
    offButton.grid(row=0, column=1, sticky=tk.N+tk.S+tk.E+tk.W)
    toggleButton = tk.Button(frameOnOff, text="Toggle", command=bulb_toggle)
    toggleButton.grid(row=0, column=2, sticky=tk.N+tk.S+tk.E+tk.W)

    # Dim/Blink
    dimButton = tk.Button(frameDimBlink, text="Dim", command=bulb_dim_call)
    dimButton.grid(row=1, column=0, sticky=tk.N+tk.S+tk.E+tk.W)
    blinkButton = tk.Button(
        frameDimBlink,
        text="Blink",
        command=bulb_blink_call
    )
    blinkButton.grid(row=1, column=1, sticky=tk.N+tk.S+tk.E+tk.W)

    # Sliders
    dimSlider = tk.Scale(frameSliders, from_=0, to=100, orient=tk.HORIZONTAL)
    dimSlider.set(100)
    dimSlider.grid(row=2, column=0, sticky=tk.N+tk.S+tk.E+tk.W)
    blinkSlider = tk.Scale(frameSliders, from_=1, to=10, orient=tk.HORIZONTAL)
    blinkSlider.set(5)
    blinkSlider.grid(row=2, column=1, sticky=tk.N+tk.S+tk.E+tk.W)

    root.mainloop()

    end_program(0)
# -----------------------
