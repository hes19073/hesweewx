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
        self.filename_hand = d.get('filename_hand', '/home/weewx/archive/0ZahlStand')
        log.info("Hand Zaehler eingaben: using %s" % self.filename_hand)
        self.bind(weewx.NEW_ARCHIVE_RECORD, self.lese_file)

    def lese_file(self, event):

        """ first read old data from '/home/weewx/archive/0ZahlAlt' """
        try:
            with open('/home/weewx/archive/0ZahlAlt') as f:
                line_hand = f.readline()
                values_ha = line_hand.split(',')

            # was, wasA, ele, gas, eleA, elePV Werte aus = 0ZahlAlt
            last_was = float(values_ha[0])
            self._last_was = last_was
            last_waa = float(values_ha[1])
            self._last_waa = last_waa
            last_ele = float(values_ha[2])
            self._last_ele = last_ele
            last_gas = float(values_ha[3])
            self._last_gas = last_gas
            last_ela = float(values_ha[4])
            self._last_ela = last_ela
            last_elp = float(values_ha[5])
            self._last_elp = last_elp

            f.close()

        except Exception as e:
            log.error("Zahl cannot read old value: %s", e)

        """ then read data from hand in to database
            input new value by hand in '/home/weewx/archive/0ZahlStand'
            now read values, get difference and save in to database 'haus' """
        try:
            with open(self.filename_hand) as ff:
                line_old = ff.readline()
                values_o = line_old.split(',')

            was_new = float(values_o[0])
            waa_new = float(values_o[1])
            ele_new = float(values_o[2])
            gas_new = float(values_o[3])
            ela_new = float(values_o[4])
            elp_new = float(values_o[5])

            ff.close()

            was_dif = calculate_delta(was_new, self._last_was)
            waa_dif = calculate_delta(waa_new, self._last_waa)
            ele_dif = calculate_delta(ele_new, self._last_ele)
            gas_dif = calculate_delta(gas_new, self._last_gas)
            ela_dif = calculate_delta(ela_new, self._last_ela)
            elp_dif = calculate_delta(elp_new, self._last_elp)

            event.record['wasZahl'] = float(was_new)
            event.record['wasTotal'] = float(was_dif)
            event.record['wasAZahl'] = float(waa_new)
            event.record['wasATotal'] = float(waa_dif)
            event.record['eleZahl'] = float(ele_new)
            event.record['eleTotal'] = float(ele_dif)
            event.record['gasZahl'] = float(gas_new)
            event.record['gasTotal'] = float(gas_dif)
            event.record['eleAZahl'] = float(ela_new)
            event.record['eleATotal'] = float(ela_dif)
            event.record['elePVZahl'] = float(elp_new)
            event.record['elePVTotal'] = float(elp_dif)

            # save new data to '/home/weewx/archive/0ZahlAlt'
            dat_old = open("/home/weewx/archive/0ZahlAlt", "w")
            dat_new = str(was_new) + "," + str(waa_new) + "," + str(ele_new) + "," + str(gas_new) + "," + str(ela_new) + "," + str(elp_new)
            dat_old.write(dat_new)

            dat_old.close()

        except Exception as e:
            log.error("read failed: %s" % e)



