# extended stats based on the xsearch example
# $Id: xstats.py 2749 2014-11-29 18:15:24Z tkeffer $
# Copyright 2013 Matthew Wall, all rights reserved

"""This search list extension offers extra tags:

  'alltime':    All time statistics.

  'seven_day':  Statistics for the last seven days. 

  'thirty_day': Statistics for the last thirty days.

You can then use tags such as $alltime.outTemp.max for the all-time max
temperature, or $seven_day.rain.sum for the total rainfall in the last seven
days, or $thirty_day.wind.max for maximum wind speed in the past thirty days.
"""
import datetime
import time

from weewx.cheetahgenerator import SearchList
from weewx.tags import TimespanBinder
from weeutil.weeutil import TimeSpan
from weewx.units import ValueHelper

class ExtendedStatistics(SearchList):
    
    def __init__(self, generator):
        SearchList.__init__(self, generator)
  
    def get_extension_list(self, timespan, db_lookup):
        """Returns a search list extension with additions.

        timespan: An instance of weeutil.weeutil.TimeSpan. This holds
                  the start and stop times of the domain of valid times.

        db_lookup: Function that returns a database manager given a
                   data binding.
        """

        # First, create a TimespanBinder object for all time. This one is easy
        # because the object timespan already holds all valid times to be
        # used in the report.
        all_stats = TimespanBinder(timespan,
                                   db_lookup,
                                   context='alltime',
                                   formatter=self.generator.formatter,
                                   converter=self.generator.converter)
        
        # Now create a TimespanBinder for the last seven days. This one we
        # will have to calculate. First, calculate the time at midnight, seven
        # days ago. The variable week_dt will be an instance of datetime.date.
        week_dt = datetime.date.fromtimestamp(timespan.stop) - datetime.timedelta(weeks=1)
        # Now convert it to unix epoch time:
        week_ts = time.mktime(week_dt.timetuple())
        # Now form a TimeSpanStats object, using the time span just calculated:
        seven_day_stats = TimespanBinder(TimeSpan(week_ts, timespan.stop),
                                         db_lookup,
                                         context='seven_day',
                                         formatter=self.generator.formatter,
                                         converter=self.generator.converter)

        # Now use a similar process to get statistics for the last 30 days.
        days_dt = datetime.date.fromtimestamp(timespan.stop) - datetime.timedelta(days=30)
        days_ts = time.mktime(days_dt.timetuple())
        thirty_day_stats = TimespanBinder(TimeSpan(days_ts, timespan.stop),
                                          db_lookup,
                                          context='thirty_day',
                                          formatter=self.generator.formatter,
                                          converter=self.generator.converter)

        # Now use a similar process to get statistics for the last 30 days.
        year14_day_stats = TimespanBinder(TimeSpan(1388530804, 1419980404),
                                          db_lookup,
                                          context='year14_day',
                                          formatter=self.generator.formatter,
                                          converter=self.generator.converter)

        year13_day_stats = TimespanBinder(TimeSpan(1356994806,  1388530799),
                                          db_lookup,
                                          context='year13_day',
                                          formatter=self.generator.formatter,
                                          converter=self.generator.converter)

        # Get ts for day of last rain from archive_day_rain
        # Value returned is ts for midnight on the day the rain occurred
        _row = db_lookup().getSql("SELECT MAX(dateTime) FROM archive_day_rain WHERE sum > 0")
        lastrain_ts = _row[0]
        # Now if we found a ts then use it to limit our search on the archive
        # so we can find the last archive record during which it rained. Wrap
        # in a try statement just in case
        if lastrain_ts is not None:
            try:
                _row = db_lookup().getSql("SELECT MAX(dateTime) FROM archive WHERE rain > 0 AND dateTime > ? AND dateTime <= ?", (lastrain_ts, lastrain_ts + 86400))
                lastrain_ts = _row[0]
            except:
                lastrain_ts = None
        # Wrap our ts in a ValueHelper
        lastrain_vt = (lastrain_ts, 'unix_epoch', 'group_time')
        lastrain_vh = ValueHelper(lastrain_vt, formatter=self.generator.formatter, converter=self.generator.converter)

	# next idea stolen with thanks from weewx station.py
        # note this is delta time from 'now' not the last weewx db time
        delta_time = time.time() - lastrain_ts if lastrain_ts else None

        # Wrap our ts in a ValueHelper
        delta_time_vt = (delta_time, 'second', 'group_deltatime')
        delta_time_vh = ValueHelper(delta_time_vt, formatter=self.generator.formatter, converter=self.generator.converter)
        

        
        return [{'alltime': all_stats,
                 'seven_day': seven_day_stats,
                 'thirty_day': thirty_day_stats,
                 'lastrain_day': lastrain_vh,
                 'lastrain_delta_time': delta_time_vh,
                 'year14_day': year14_day_stats,
                 'year13_day': year13_day_stats}]


# For backwards compatibility:
ExtStats = ExtendedStatistics
