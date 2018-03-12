#-------------------------------------------------------------------------------
# Copyright (C) 2017 Create-Net / FBK.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# 
# Contributors:
#     Create-Net / FBK - initial API and implementation
#-------------------------------------------------------------------------------

ARG BASEIMAGE_BUILD=resin/raspberrypi3-python:3.4-20180216
#ARG BASEIMAGE_BUILD=resin/intel-nuc-python:3.4-20180222
FROM $BASEIMAGE_BUILD

# resin-sync will always sync to /usr/src/app, so code needs to be here.
WORKDIR /usr/src/app

RUN apt-get update && apt-get install --no-install-recommends -y \
    python3-gi \
    libdbus-1-dev \
    libdbus-glib-1-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt

RUN python3 -m pip install -r requirements.txt

COPY src src
COPY examples examples

CMD src/agile_makers_shield_server.py