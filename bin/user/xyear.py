#
#    Copyright (c) 2009-2015 Tom Keffer <tkeffer@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#
"""Extended stats based on the xsearch example


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
from datetime import date
from weewx.units import ValueHelper, getStandardUnitType, ValueTuple

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

class xMyEaster(SearchList):
        
    def __init__(self, generator):
        SearchList.__init__(self, generator)

    def get_extension_list(self, timespan, db_lookup):
        """ Returns various tags.
       
        Parameters:
          timespan: An instance of weeutil.weeutil.TimeSpan. This will
                    hold the start and stop times of the domain of
                    valid times.
            
          db_lookup: This is a function that, given a data binding
                     as its only parameter, will return a database manager
                     object.
        Returns:
          Easter:         A ValueHelper containing the date of the next Easter
                          Sunday. The time represented is midnight at the start
                          of Easter Sunday.
        """
        #
        # Easter. Calculate date for Easter Sunday this year
        #
        def calcEaster(years):

            g = years % 19
            e = 0
            century = years / 100
            h = (century - century / 4 - (8 * century + 13) / 25 + 19 * g + 15) % 30
            i = h - (h / 28) * (1 - (h / 28) * (29 / (h + 1)) * ((21 - g) / 11))
            j = (years + years / 4 + i + 2 - century + century / 4) % 7
            p = i - j + e
            _days = 1 + (p + 27 + (p + 6) / 40) % 31
            _months = 3 + (p + 26) / 30
            Easter_dt = datetime.datetime(year=years, month=_months, day=_days)
            Easter_ts = time.mktime(Easter_dt.timetuple())
            return Easter_ts

        _years = date.today().year
        Easter_ts = calcEaster(_years)
        # Check to see if we have past this calculated date
        # If so we want next years date so increment year and recalculate
        if date.fromtimestamp(Easter_ts) < date.today():
            Easter_ts = calcEaster(_years + 1)
        Easter_vt = ValueTuple(Easter_ts, 'unix_epoch', 'group_time')
        Easter_vh = ValueHelper(Easter_vt,
                                formatter=self.generator.formatter,
                                converter=self.generator.converter)

        # Create a small dictionary with the tag names (keys) we want to use
        search_list_extension = {'Easter'        : Easter_vh,}


        return [search_list_extension]
