
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

Description: Abstract class that implements
             an Observer pattern with a property.
Author: David Palomares <d.palomares@libelium.com>
Version: 0.1
Date: May 2017
"""


# --- Imports -----------
from abc import ABCMeta, abstractmethod
# -----------------------


# --- Classes -----------
class Observer(object):
    """Class to be extended by the methods that want to subscribe."""

    __metaclass__ = ABCMeta

    @abstractmethod
    def update(self):
        """Abstract method for update an obersver."""
        pass

    @property
    @abstractmethod
    def attribute(self):
        """Abstract property to subscribe an obersver."""
        return None
# -----------------------
