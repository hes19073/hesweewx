#    Copyright (c) 2009-2015 Tom Keffer <tkeffer@gmail.com>
#    See the file LICENSE.txt for your rights.

"""Example of how to extend the search list used by the Cheetah generator.
*******************************************************************************
This search list extension offers two extra tags:
    'alletime':   All time statistics.
                 For example, "what is the all time high temperature?"

*******************************************************************************
To use this search list extension:
1) copy this file to the user directory
2) modify the option search_list in the skin.conf configuration file, adding
the name of this extension.  When you're done, it will look something like
this:
[CheetahGenerator]
    search_list_extensions = user.wd_alltime.wd_AlleTime
You can then use tags such as $alletime.outTemp.max for the all-time max
temperature.
*******************************************************************************
"""

import datetime
import time
import os.path
import itertools
#import user.wdTaggedStats3
import weewx
import weeutil.weeutil
import weewx.almanac
import weewx.units
import syslog
import math
import calendar
import weewx.tags

from weewx.cheetahgenerator import SearchList
from weewx.tags import TimeBinder, TimespanBinder
from weeutil.weeutil import TimeSpan, archiveDaySpan, genMonthSpans, genDaySpans, startOfDay, option_as_list, isMidnight
from weewx.units import ValueHelper, getStandardUnitType, ValueTuple
from datetime import date

from dateutil.relativedelta import relativedelta

WEEWXWD_SLE_VERSION = '1.2.0b1'

def logmsg(level, msg):
    syslog.syslog(level, 'WD_AlleTime: %s' % msg)

def logdbg(msg):
    logmsg(syslog.LOG_DEBUG, msg)

def loginf(msg):
    logmsg(syslog.LOG_INFO, msg)

def logerr(msg):
    logmsg(syslog.LOG_ERR, msg)

class wd_AlleTime(SearchList):

    def __init__(self, generator):
        SearchList.__init__(self, generator)

    def get_extension_list(self, timespan, db_lookup):
        """ Returns a search list extension with all time and last seven days
            stats.

        Parameters:
          timespan: An instance of weeutil.weeutil.TimeSpan. This will
                    hold the start and stop times of the domain of
                    valid times.

          db_lookup: This is a function that, given a data binding
                     as its only parameter, will return a database manager
                     object.

        Returns:
          tspan_binder: A TimespanBinder object that allows a data binding to
                        be specified (default to None) when calling $alletime
                        eg $alletime.outTemp.max for the all time high outside
                           temp.
                           $alletime($data_binding='wd_binding').humidex.max
                           for the all time high humidex where humidex
                           resides in the 'wd_binding' database.

                        Standard Weewx unit conversion and formatting options
                        are available.
        """

        t1 = time.time()

        class wdBinder(TimeBinder):

            def __init__(self, db_lookup, report_time,
                         formatter=weewx.units.Formatter(), converter=weewx.units.Converter(), **option_dict):
                """Initialize an instance of wdBinder.

                db_lookup: A function with call signature db_lookup(data_binding), which
                returns a database manager and where data_binding is an optional binding
                name. If not given, then a default binding will be used.

                report_time: The time for which the report should be run.

                formatter: An instance of weewx.units.Formatter() holding the formatting
                information to be used. [Optional. If not given, the default
                Formatter will be used.]

                converter: An instance of weewx.units.Converter() holding the target unit
                information to be used. [Optional. If not given, the default
                Converter will be used.]

                option_dict: Other options which can be used to customize calculations.
                [Optional.]
                """
                self.db_lookup    = db_lookup
                self.report_time  = report_time
                self.formatter    = formatter
                self.converter    = converter
                self.option_dict  = option_dict

            # Give it a method "alletime", with optional parameter data_binding
            def alletime(self, data_binding=None):
                # to avoid problems where our data_binding might have a first
                # good timestamp that is different to timespan.start (and thus
                # change which manager is used) we need to reset our
                # timespan.start to the first good timestamp of our data_binding

                # get a manager
                db_manager = db_lookup(data_binding)
                # get our first good timestamp
                start_ts = db_manager.firstGoodStamp()
                # reset our timespan
                alletime_tspan = TimeSpan(start_ts, timespan.stop)

                return TimespanBinder(alletime_tspan,
                                      self.db_lookup, context='alletime',
                                      data_binding=data_binding, # overrides the default
                                      formatter=self.formatter,
                                      converter=self.converter)


        tspan_binder = wdBinder(db_lookup, timespan.stop, self.generator.formatter, self.generator.converter)

        t2 = time.time()
        logdbg("wd_AlleTime SLE executed in %0.3f seconds" % (t2-t1))

        return [tspan_binder]

