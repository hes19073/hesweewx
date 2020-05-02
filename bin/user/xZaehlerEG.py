# -*- coding: utf-8 -*-
#
# Portions Copyright 2014 Matthew Wall
#
# This service will read data from a file.  Each line of the file
# for example:
# /var/tmp/hauseg.txt
#
# 50.323,32.2,109.4,75.887,009.8,1546.45
# values[0], ... value[n]
#
# The names must match the weewx database schema,
# but the schema can be extended for new fields
#
# Put this file in the bin/user directory
#
# Add this service to weewx.conf, then restart weewx
#[Engine]
#    [[Services]]
#        data_services = ..., user.xZaehlerEG.HausEG
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
# See http://www.gnu.org/licenses/# coding=utf-8

""" Service Configuration 


 data /var/tmp/hauseg.txt
         0 1   2    3          4           5           6           7           8
# dateTime,ele,eleA,extraTemp1,extraTemp10,extraTemp11,extraTemp12,extraTemp13,extraTemp14,
9          10         11         12         13         14         15         16         17  18      19
extraTemp2,extraTemp3,extraTemp4,extraTemp5,extraTemp6,extraTemp7,extraTemp8,extraTemp9,gas,usUnits,was

 0         1         2          3      4       5       6       7       8      9    10    11      12      13     14      15      16      17         18 19  20
1582136144,1379284.0,16844122.0,45.875,25.1875,23.0625,22.4375,35.8125,21.875,56.0,52.75,44.5625,32.9375,25.375,23.1875,22.9375,23.4375,16792915.0,16,0.0,0.0

"""

import logging
import weewx
import weedb
import weewx.manager
import weeutil.weeutil

from weewx.wxengine import StdService

log = logging.getLogger(__name__)

class HausEG(StdService):
    def __init__(self, engine, config_dict):
        super(HausEG, self).__init__(engine, config_dict)
        d = config_dict.get('HausEG', {})
        self.filename_haus = d.get('filename_haus', '/var/tmp/hauseg.txt')
        log.info("DataHausEG: using %s", self.filename_haus)
        self.bind(weewx.NEW_ARCHIVE_RECORD, self.read_file)

    def read_file(self, event):
        """ read old data from file '0ImpulsZahl' for calculate_delta """
        try:
            with open('/home/weewx/archive/0ImpulsZahl') as f:
                line_imp = f.readline()
                values_i = line_imp.split(',')

            gas_val = float(values_i[0])
            self._gas_val = gas_val
            was_val = float(values_i[1])
            self._was_val = was_val
            waa_val = float(values_i[2])
            self._waa_val = waa_val
            ele_val = float(values_i[3])
            self._ele_val = ele_val
            ela_val = float(values_i[4])
            self._ela_val = ela_val
            elp_val = float(values_i[5])
            self._elp_val = elp_val

            f.close()

        except Exception as e:
            log.error("ImpulZahl cannot read old value: %s", e)

            """ then read data from hesbaEG server in to database """
            # input new value from hesbaEG server file '/var/tmp/hauseg.txt'
            # read values, get difference and save in to database 'haus'

        try:
            with open(self.filename_haus) as ff:
                line = ff.readline()
                values = line.split(',')

            #log.debug("HausEG: found value of %s", values)

            ele_new = float(values[1])
            ela_new = float(values[2])

            event.record['ele'] = ele_new
            event.record['eleA'] = ela_new
            event.record['extraTemp1'] = float(values[3])
            event.record['extraTemp10'] = float(values[4])
            event.record['extraTemp11'] = float(values[5])
            event.record['extraTemp12'] = float(values[6])
            event.record['extraTemp13'] = float(values[7])
            event.record['extraTemp14'] = float(values[8])
            event.record['extraTemp2'] = float(values[9])
            event.record['extraTemp3'] = float(values[10])
            event.record['extraTemp4'] = float(values[11])
            event.record['extraTemp5'] = float(values[12])
            event.record['extraTemp6'] = float(values[13])
            event.record['extraTemp7'] = float(values[14])
            event.record['extraTemp8'] = float(values[15])
            event.record['extraTemp9'] = float(values[16])
            gas_new = float(values[17])
            was_new = float(values[19])
            waa_new = float(values[20])
            elp_new = float(values[1])
            event.record['gas'] = gas_new
            event.record['was'] = was_new
            event.record['wasA'] = waa_new
            event.record['elePV'] = elp_new
            event.record['gasDelta'] = calculate_delta(gas_new, self._gas_val)
            #event.record['wasDelta'] = calculate_delta(was_new, self._was_val)
            event.record['wasADelta'] = calculate_delta(waa_new, self._waa_val)
            event.record['eleDelta'] = calculate_delta(ele_new, self._ele_val)
            event.record['eleADelta'] = calculate_delta(ela_new, self._ela_val)
            event.record['elePVDelta'] = calculate_delta(elp_new, self._elp_val)

            # save values for impulse in /home/weewx/archive/0ImpulsZahl
            #        gas                     was              wasA                 ele                  eleA                 elePV
            #stand = str(values[17]) + ','+ str(values[19])+',0.0,'+str(values[1])+','+str(values[2])+','+str(values[1])
            stand = str(gas_new) + ',' + str(was_new) + ',' + str(waa_new) + ',' + str(ele_new) + ',' + str(ela_new) + ',' + str(elp_new)

            ff.close()

            data_x = open('/home/weewx/archive/0ImpulsZahl', 'w')
            data_x.write(stand)
            data_x.close()

        except Exception as e:
            log.error("HausEG: cannot read value: %s", e)

def calculate_delta(newtotal, oldtotal):
    """Calculate the rain differential given two cumulative measurements."""
    if newtotal is not None and oldtotal is not None:
        if newtotal >= oldtotal:
            delta = newtotal - oldtotal
        else:
            log.info("Data counter reset detected: new=%s old=%s", newtotal, oldtotal)
            delta = 0.0
    else:
        delta = 0.0

    return delta


