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
# /home/weewx/archive/0ZahlStand
#
# 50.323,32.2,109.4,75.887,009.8,1546.45
# was   ,wasA,ele  ,gas   ,eleA ,elePV
#
# The names must match the weewx database schema,
# but the schema can be extended for new fields
#
# Add this service to weewx.conf, then restart weewx
#[Engine]
#[[Services]]
#    data_services = ..., user.xZahl.HandService
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


def calculate_delta(newtotal, oldtotal):
    """Calculate the zahl differential given two cumulative measurements."""
    if newtotal is not None and oldtotal is not None:
        if newtotal >= oldtotal:
            delta = newtotal - oldtotal
        else:
             delta = 0.0
    else:
        delta = 0.0

    return delta

class HandService(StdService):
    def __init__(self, engine, config_dict):
        super(HandService, self).__init__(engine, config_dict)

        d = config_dict.get('HandService', {})
        self.filename = d.get('filename', '/home/weewx/archive/0ZahlStand')
        log.info("Hand Zaehler eingaben: using %s" % self.filename)
        self.bind(weewx.NEW_ARCHIVE_RECORD, self.lese_file)

    def lese_file(self, event):

        """ first read old data from '/home/weewx/archive/0ZahlAlt' """
        try:
            with open('/home/weewx/archive/0ZahlAlt') as f:
                line = f.readline()
                values = line.split(',')

            # was, wasA, ele, gas, eleA, elePV Werte aus = 0ZahlAlt
            last_was = float(values[0])
            last_waa = float(values[1])
            last_ele = float(values[2])
            last_gas = float(values[3])
            last_ela = float(values[4])
            last_elp = float(values[5])

            f.close()

        except Exception as e:
            log.error("Zahl cannot read old value: %s", e)

        """ then read data from hand in to database 
            input new value by hand in '/home/weewx/archive/0ZahlStand'
            now read values, get difference and save in to database 'haus' """
        try:
            with open(self.filename) as ff:
                line = ff.readline()
                values = line.split(',')

            was_new = float(values[0])
            was_dif = calculate_delta(was_new, last_was)

            waa_new = float(values[1])
            waa_dif = calculate_delta(waa_new, last_waa)

            ele_new = float(values[2])
            ele_dif = calculate_delta(ele_new, last_ele)

            gas_new = float(values[3])
            gas_dif = calculate_delta(gas_new, last_gas)

            ela_new = float(values[4])
            ela_dif = calculate_delta(ela_new, last_ela)

            elp_new = float(values[5])
            elp_dif = calculate_delta(elp_new, last_elp)

            event.record['wasZahl'] = float(values[0])
            event.record['wasTotal'] = float(was_dif)
            event.record['wasAZahl'] = float(values[1])
            event.record['wasATotal'] = float(waa_dif)
            event.record['eleZahl'] = float(values[2])
            event.record['eleTotal'] = float(ele_dif)
            event.record['gasZahl'] = float(values[3])
            event.record['gasTotal'] = float(gas_dif)
            event.record['eleAZahl'] = float(values[4])
            event.record['eleATotal'] = float(ela_dif)
            event.record['elePVZahl'] = float(values[5])
            event.record['elePVTotal'] = float(elp_dif)

            ff.close()

            # save new data to '/home/weewx/archive/0ZahlAlt'
            dat_old = open("/home/weewx/archive/0ZahlAlt", "w")
            dat_new = str(was_new) + "," + str(waa_new) + "," + str(ela_new) + "," + str(gas_new) + "," + str(ela_new) + "," + str(elp_new)
            dat_old.write(dat_new)

            dat_old.close()

        except Exception as e:
            log.error("read failed: %s" % e)


    def calculate_delta(newtotal, oldtotal):
        """Calculate the zahl differential given two cumulative measurements."""
        if newtotal is not None and oldtotal is not None:
            if newtotal >= oldtotal:
                delta = newtotal - oldtotal
            else:

                delta = 0.0
        else:
            delta = 0.0

        return delta


