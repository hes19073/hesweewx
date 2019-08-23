# -*- coding: utf-8 -*-
# snow.py 1396 2017-01-01 09:08:45Z hes $
#
# Copyright 2017 Hartmut Schweidler
# Thanks to Tom Keffer for "add sensor" and Gary
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.
#
# See http://www.gnu.org/licenses/
"""Put this file, snow.py, in the weewx 'user' directory, then modify weewx.conf
with something like this:

the file 'snow' only 1.5

[SnowDepth]
    filename = /home/weewx/archive/snow

To use as a service:

[Engine]
    [[Service]]
        data_services = user.snowhes.SnowDepth
"""
from __future__ import absolute_import
import logging

import weewx
import weeutil.logger

from weewx.engine import StdService
from weewx.units import ValueTuple, convertStd

log = logging.getLogger(__name__)

VERSION = "0.2"

class SnowDepth(StdService):
    def __init__(self, engine, config_dict):
        super(SnowDepth, self).__init__(engine, config_dict)
        self._last_snow = 0.0
        d = config_dict.get('SnowDepth', {})
        self.filename  = d.get('filename', '/home/weewx/archive/snow')
        log.info("Snow using %s",  self.filename)
        self.bind(weewx.NEW_ARCHIVE_RECORD, self.newArchiveRecord)

    def newArchiveRecord(self, event):
        try:
            with open(self.filename) as f:
                snow_val = f.read()
            log.debug("Snowdepth found value of %s", snow_val)
            # Convert our value to a type ValueTuple. We know it is in cm and
            # let's use group_snow (could use group_length too)
            value_vt = ValueTuple(float(snow_val), 'cm', 'group_snow')
            # Now convert the cm value to the same units as used in our record
            # The unit system of the record is in the records 'usUnits' field
            snow_total = convertStd(value_vt, event.record['usUnits']).value
            delta = weewx.wxformulas.calculate_rain(snow_total, self._last_snow)
            # calculate_rain is correct it is only the delta function used
            self._last_snow = float(snow_total)

            event.record['snowTotal'] = float(self._last_snow)
            event.record['snow'] = float(delta)
        except Exception as e:
            log.error("Snowdepth cannot read value: %s", e)
