# -*- coding: utf-8 -*-
#
# Portions Copyright 2014 Matthew Wall
# Portions taken from the pond.py example on the "add sensor" page
# on the weewx wiki, edited by Tom Keffer
#
# weewx service that reads data from a file as key value pairs and
# adds it to every loop packet
#
# This driver will read data from a file.  Each line of the file
# for example:
# /home/weewx/archive/0verbrauch
#
# 50.323,32.2,109.4,75.887,009.8
# was   ,wasA,ele  ,gas   ,eleA
#
# The names must match the weewx database schema,
# but the schema can be extended for new fields
#
# Add this service to weewx.conf, then restart weewx
#[Engine]
#[[Services]]
#    data_services = ..., user.xhand0.HandService
#
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.
#
# See http://www.gnu.org/licenses/

import logging
import weewx
import weedb
import weewx.manager
import weeutil.weeutil

from weewx.wxengine import StdService

log = logging.getLogger(__name__)

class HandService(StdService):
    def __init__(self, engine, config_dict):
        super(HandService, self).__init__(engine, config_dict)
        self._last_ele = 0.0
        self._last_eleA = 0.0
        self._last_was = 0.0
        self._last_wasA = 0.0
        self._last_gas = 0.0

        d = config_dict.get('HandService', {})
        self.filename = d.get('filename', '/home/weewx/archive/0verbrauch')
        log.info("Hand Zaehler: using %s" % self.filename)
        self.bind(weewx.NEW_ARCHIVE_RECORD, self.lese_file)

    def lese_file(self, event):

        try:
            with open(self.filename) as f:
                line = f.readline()
                values = line.split(',')

            was_val = float(values[0])
            was_Zahl = weewx.wxformulas.calculate_rain(was_val, self._last_was)
            self._last_was = float(was_val)

            wasA_val = float(values[1])
            wasA_Zahl = weewx.wxformulas.calculate_rain(wasA_val, self._last_wasA)
            self._last_wasA = float(wasA_val)

            ele_val = float(values[2])
            ele_Zahl = weewx.wxformulas.calculate_rain(ele_val, self._last_ele)
            self._last_ele = float(ele_val)

            gas_val = float(values[3])
            gas_Zahl = weewx.wxformulas.calculate_rain(gas_val, self._last_gas)
            self._last_gas = float(gas_val)

            eleA_val = float(values[4])
            eleA_Zahl = weewx.wxformulas.calculate_rain(eleA_val, self._last_eleA)
            self._last_eleA = float(eleA_val)


            event.record['wasZahl'] = float(values[0])
            event.record['wasTotal'] = float(was_Zahl)
            event.record['wasAZahl'] = float(values[1])
            event.record['wasATotal'] = float(wasA_Zahl)
            event.record['eleZahl'] = float(values[2])
            event.record['eleTotal'] = float(ele_Zahl)
            event.record['gasZahl'] = float(values[3])
            event.record['gasTotal'] = float(gas_Zahl)
            event.record['eleAZahl'] = float(values[4])
            event.record['eleATotal'] = float(eleA_Zahl)

        except Exception as e:
            log.error("read failed: %s" % e)



    def calculate_rain(newtotal, oldtotal):
        """Calculate the rain differential given two cumulative measurements."""
        if newtotal is not None and oldtotal is not None:
            if newtotal >= oldtotal:
                delta = newtotal - oldtotal
            else:
                log.info("Rain counter reset detected: new=%s old=%s", newtotal, oldtotal)
                delta = None
        else:
            delta = None

        return delta
