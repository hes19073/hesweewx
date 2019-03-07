# coding=utf-8
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
import weewx

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
                                   converter=self.generator.converter,
                                   skin_dict=self.generator.skin_dict)

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
                                         converter=self.generator.converter,
                                         skin_dict=self.generator.skin_dict)

        # Now use a similar process to get statistics for the last 30 days.
        days_dt = datetime.date.fromtimestamp(timespan.stop) - datetime.timedelta(days=30)
        days_ts = time.mktime(days_dt.timetuple())
        thirty_day_stats = TimespanBinder(TimeSpan(days_ts, timespan.stop),
                                          db_lookup,
                                          context='thirty_day',
                                          formatter=self.generator.formatter,
                                          converter=self.generator.converter,
                                          skin_dict=self.generator.skin_dict)


        # Now use a similar process to get statistics for last year.
        year = datetime.date.today().year
        start_ts = time.mktime((year - 1, 1, 1, 0, 0, 0, 0, 0, 0))
        stop_ts = time.mktime((year, 1, 1, 0, 0, 0, 0, 0, 0))
        last_year_stats = TimespanBinder(TimeSpan(start_ts, stop_ts),
                                          db_lookup,
                                          context='last_year',
                                          formatter=self.generator.formatter,
                                          converter=self.generator.converter)

        # Now use a similar process to get statistics for last year to date.
        year = datetime.date.today().year
        month = datetime.date.today().month
        day = datetime.date.today().day
        start_ts = time.mktime((year - 1, 1, 1, 0, 0, 0, 0, 0, 0))
        stop_ts = time.mktime((year - 1, month, day, 0, 0, 0, 0, 0, 0))
        last_year_todate_stats = TimespanBinder(TimeSpan(start_ts, stop_ts),
                                                db_lookup,
                                                context='last_year_todate',
                                                formatter=self.generator.formatter,
                                                converter=self.generator.converter)

        # Now use a similar process to get statistics for last calendar month.
        start_ts = time.mktime((year, month - 1, 1, 0, 0, 0, 0, 0, 0))
        stop_ts = time.mktime((year, month, 1, 0, 0, 0, 0, 0, 0)) - 1
        last_month_stats = TimespanBinder(TimeSpan(start_ts, stop_ts),
                                          db_lookup,
                                          context='last_month',
                                          formatter=self.generator.formatter,
                                          converter=self.generator.converter)

        ## Get ts Weewx was launched
        ##
        starttime = 1383254340
        # Start Datenbank
        starttime_vt = (starttime, 'unix_epoch', 'group_time')
        starttime_vh = ValueHelper(starttime_vt,
                                   formatter=self.generator.formatter,
                                   converter=self.generator.converter)

        """Lazy evaluation of weewx uptime."""
        delta_time = time.time() -  1383254340

        db_sta_end = ValueHelper(value_t=(delta_time, "second", "group_deltatime"),
                                       formatter=self.generator.formatter,
                                       converter=self.generator.converter)

        return [{'alltime': all_stats,
                 'seven_day': seven_day_stats,
                 'thirty_day': thirty_day_stats,
                 'last_month': last_month_stats,
                 'start_time': starttime_vh,
                 'db_uptime': db_sta_end,
                 'last_year': last_year_stats,
                 'last_year_today': last_year_todate_stats,
               }]


# For backwards compatibility:
ExtStats = ExtendedStatistics
