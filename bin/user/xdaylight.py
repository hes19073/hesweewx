# extended stats based on the xsearch example
# $Id: xdaylight.py 2749 2017-10-12 11:15:24 hes $
# original xstats.py
# Copyright 2013 Matthew Wall, all rights reserved

"""This search list extension offers extra tags:
  'daylight_max':    as string   9 Stunden und 34 Minuten.
  'daylight_day':    as string 34 Minuten
                             or 9 Stunden und 34 Minuten.
  'daylight_day':    can be None if night.
"""

import datetime
import time

from dateutil.relativedelta import relativedelta
from weewx.cheetahgenerator import SearchList
from weewx.tags import TimespanBinder
from weeutil.weeutil import TimeSpan
from weewx.units import ValueHelper

class Daylight(SearchList):

    def __init__(self, generator):
        SearchList.__init__(self, generator)

    def get_extension_list(self, timespan, db_lookup):
        """Returns a search list extension with additions.
        timespan: An instance of weeutil.weeutil.TimeSpan. This holds
                  the start and stop times of the domain of valid times.
        db_lookup: Function that returns a database manager given a
                   data binding.
        """

        sunrise_ts = almanac.sun.rise.raw                       # Sonnenauf
        sunset_ts = almanac.sun.set.raw                         # Sonnenunter
        now_ts = time.time()                                    # akt Zeit

        daylight_s = sunset_ts - sunrise_ts
        daylight_hours = int(daylight_s / 3600)
        daylight_minutes = int((daylight_s % 3600) / 60)

        #daylight_h_str = "%02d" % daylight_hours
        #daylight_m_str = "%02d" % daylight_minutes
        daylight_max = "%02d Stunden und %02d Minuten" % (daylight_hours, daylight_minues)

        # daylight_day is now – sunrise Tageslicht aktuell
        if sunrise_ts < now_ts < sunset_ts:
            daylight_s_day = now_ts – sunrise_ts

            daylight_h_day = int(daylight_s_day / 3600)
            daylight_m_day = int((daylight_s_day % 3600) / 60)
            if day_s_day < 3600:
                daylight_day = "%02d  Minuten" % daylight_m_day
            else:
                daylight_day = "%02d Stunden und %02d Minuten" % (daylight_h_day, daylight_m_day)

        else:
            daylight_day = None

        return [{'daylightmax': daylight_max,
                 'daylightday': daylight_day}]


