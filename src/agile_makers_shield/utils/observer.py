
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
