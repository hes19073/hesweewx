#
#    Copyright (c) 2009-2015 Tom Keffer <tkeffer@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#
"""Extended stats based on the xsearch example

This search list extension offers extra tags:

  'alltime':    All time statistics.

  'seven_day':  Statistics for the last seven days. 

  'thirty_day': Statistics for the last thirty days.

You can then use tags such as $alltime.outTemp.max for the all-time max
temperature, or $seven_day.rain.sum for the total rainfall in the last seven
days, or $thirty_day.wind.max for maximum wind speed in the past thirty days.

Jahr -1 = Vorjahr = year1, das Jahr vor dem Vorjahr = year2
"""
import datetime
import time
import os
import sys
import syslog

from weewx.cheetahgenerator import SearchList
from weewx.tags import TimespanBinder
from weeutil.weeutil import TimeSpan

class MyXYearYear(SearchList):
    
    def __init__(self, generator):
        SearchList.__init__(self, generator)
  
    def get_extension_list(self, timespan, db_lookup):
        """Returns a search list extension with additions.

        timespan: An instance of weeutil.weeutil.TimeSpan. This holds
                  the start and stop times of the domain of valid times.

        db_lookup: Function that returns a database manager given a
                   data binding.
        """

        today = datetime.date.today()

        ano = today.year

        anoy = ano - 1

        year1_start = datetime.date(anoy, 1, 1)
        year1_end = datetime.date(anoy, 12, 31)

        year1_start_ts = time.mktime(year1_start.timetuple())
        year1_end_ts = time.mktime(year1_end.timetuple())        

        year1_stats = TimespanBinder(TimeSpan(year1_start_ts, year1_end_ts),
                                     db_lookup,
                                     context='year1',
                                     formatter=self.generator.formatter,
                                     converter=self.generator.converter)



        anoyy = ano - 2

        year2_start = datetime.date(anoyy, 1, 1)
        year2_end = datetime.date(anoyy, 12, 31)

        year2_start_ts = time.mktime(year2_start.timetuple())
        year2_end_ts = time.mktime(year2_end.timetuple())        

        year2_stats = TimespanBinder(TimeSpan(year2_start_ts, year2_end_ts),
                                     db_lookup,
                                     context='year2',
                                     formatter=self.generator.formatter,
                                     converter=self.generator.converter)

        return [{'year1' : year1_stats,
                 'year2' : year2_stats}]

