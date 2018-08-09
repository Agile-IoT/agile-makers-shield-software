
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
AGILE Serial Interruptions.

Description: Class to implement the Singleton
             pattern. Use it as a metaclass:
                 class TheClass(metaclass=Singleton)
Author: David Palomares <d.palomares@libelium.com>
Version: 0.1
Date: May 2017
"""


# --- Classes -----------
class Singleton(type):
    """Singleton metaclass."""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """Return a new instance if not any or return a existing one."""
        if cls not in cls._instances:
            cls._instances[cls] = \
                super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
# -----------------------
