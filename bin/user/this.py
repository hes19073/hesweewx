"""
this.py

A WeeWX Search List Extension (SLE) to allow iteration over 'this' period.

Copyright (C) 2017-2019 Gary Roderick             gjroderick<at>gmail.com

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program.  If not, see http://www.gnu.org/licenses/.

Version: 0.1.0                                      Date: 12 May 2019

Revision History
    12 May 2019         v0.1.0
        - initial release


This SLE allows iteration over a time span calculating statistics for the same
period (day, week or month) in each year. The default time span over which
iteration occurs is all records in the WeeWX archive and the default period
over which the statistics are calculated is the current day of the year.

Consider a WeeWX installation that has data from 1 January 2010 to 12 May 2019,
the following code used in a template, and run on 12 May 2019, would display the
maximum temperature and the time that it occurred on 12 May each year from 2010
to 2019:

    #for $day in $this_span.periods
    $day.outTemp.max at $day.outTemp.maxtime
    #end for

If run on the following day, it would display data for each 13 May from 2010 to
2019.

.periods supports time spans of the current week and current month by including
the optional $period parameter, for example:

    #for $week in $this_span.periods($period='week')
    $week.outTemp.max at $week.outTemp.maxtime
    #end for

    and

    #for $month in $this_span.periods($period='month')
    $month.outTemp.max at $month.outTemp.maxtime
    #end for

would display the maximum temperature and the time that it occurred on the
current week and month each year from 2010 to 2019 respectively.

By default this day, this week and this month use day, week and month spans
based on the current report time. This time can be changed by use of one or
more of the optional $day_delta, $week_delta, $year_delta and $timestamp
parameters. For example, instead of displaying data for the current day in all
years, data can be displayed for yesterday for all years by using $day_delta=1:

    #for $day in $this_span.periods($day_delta=1)
    $day.outTemp.max at $day.outTemp.maxtime
    #end for

Similarly an absolute timestamp can be used through use of the $timestamp
parameter, for example:

    #import time
    #set $now=time.time()

    #for $day in $this_span.periods($timestamp=$now-86400)
    $day.outTemp.max at $day.outTemp.maxtime
    #end for

would also display data for yesterday over all years.

Use of $this_span will iterate over the entire archive. This period can be
limited by use of one or more of the optional time_delta, hour_delta,
day_delta, week_delta, month_delta or year_delta parameters with the $this_span
tag. For example, the following code would display maximum temperature data for
this day over the last two years only:

    #for $day in $this_span($year_delta=2).periods
    $day.outTemp.max at $day.outTemp.maxtime
    #end for

Data can also be obtained from any database for which a database binding has
been defined through use of the $data_binding parameter with the $this_span tag:

    #for $day in $this_span($data_binding='my_binding').periods
    $day.outTemp.max at $day.outTemp.maxtime
    #end for

The $data_binding operates exactly the same as implemented elsewhere in the
WeeWX tag system.

All WeeWX tag options (eg aggregates, unit conversion ,formatting etc) are
supported.

Some additional example usage:

    maximum ouTemp and time it occurred on this day over all recorded years:

        #for $day in $this_span.periods
        $day.outTemp.max at $day.outTemp.maxtime
        #end for

    year and total daily rainfall on this day over all recorded years:

        #for $day in $this_span.periods
        $day.dateTime.format("%Y"): $day.rain.sum
        #end for

    maximum outTemp in Fahrenheit and time it occurred in this month over all
    recorded years:

        #for $month in $this_span.periods($period='month')
        $month.outTemp.max.degree_F at $month.outTemp.maxtime
        #end for

    maximum ouTemp and time it occurred on this day over all recorded years:

        #for $day in $this_span.periods($timestamp=123456789)
        $day.outTemp.max at $day.outTemp.maxtime
        #end for

Abbreviated instructions for use:

1.  Download the file this.py to the WeeWX machine and save to the
$BIN_ROOT/user directory:

    for a setup.py install:

    $ wget -P /home/weewx/bin/user https://raw.githubusercontent.com/gjr80/weewx_utilities/master/search%20list%20extensions/this/bin/user/this.py

    otherwise:

    $ wget -P /usr/share/weewx/user https://raw.githubusercontent.com/gjr80/weewx_utilities/master/search%20list%20extensions/this/bin/user/this.py

2.  Add the following line to the skin config file [CheetahGenerator] stanza
for the skin in which the SLE is to be used:

    search_list_extensions = user.this.ThisSLE

    if the search_list_extensions config option already exists add
    user.this.ThisSLE to the end of the option using a comma as a separator, eg:

    search_list_extensions = user.another.SLE, user.this.ThisSLE

3.  Add the required $this_span.periods code to the template concerned.

4.  After the next report cycle is complete confirm there are no errors in the
log and the report has been generated as expected.
"""

# python imports
import datetime
import time

# WeeWX imports
import weewx.cheetahgenerator
import weewx.tags
import weewx.units
import weeutil.weeutil
from weeutil.weeutil import TimeSpan


# ==============================================================================
#                                class ThisSLE
# ==============================================================================

class ThisSLE(weewx.cheetahgenerator.SearchList):
    """SLE to allow iteration over this day/week/month."""

    def __init__(self, generator):
        # call our parent's initialisation
        super(ThisSLE, self).__init__(generator)

    def get_extension_list(self, timespan, db_lookup):
        """Returns a search list containing a ThisTimeBinder object.

        A ThisTimeBinder allows iteration over this day/week/month in a time
        span. Iteration may be performed over the time span covering all
        records in the archive or over a user specified time span.

        Parameters:
            timespan: An instance of weeutil.weeutil.TimeSpan. This will hold
                      the start and stop times of the domain of valid times.

            db_lookup: This is a function that, given a data binding as its
                       only parameter, returns a database manager object.

        Returns:
            A list containing a single ThisTimeBinder object.
        """

        this = ThisTimeBinder(db_lookup,
                              timespan.stop,
                              formatter=self.generator.formatter,
                              converter=self.generator.converter,
                              week_start=self.generator.stn_info.week_start,
                              rain_year_start=self.generator.stn_info.rain_year_start,
                              skin_dict=self.generator.skin_dict)

        return [this]


# ==============================================================================
#                            class ThisTimeBinder
# ==============================================================================

class ThisTimeBinder(object):
    """ Binds to a specific time.

    Specialised version of weewx.tags.TimeBinder to support 'this' tags.

    Supports time period 'this_span'. When a time period is given as an
    attribute to it the next item in the chain is returned, in this case an
    instance of ThisTimespanBinder, which binds to a timespan.

    this_span defaults to a universe of all records in the WeeWX archive. This
    universe may be limited by use of one or more xxxx_delta parameters,
    for example:

        #for $day in $this_span($year_delta=2)

    to use the period exactly two years ago to the current report timestamp.
    """

    def __init__(self, db_lookup, report_time, formatter=weewx.units.Formatter(),
                 converter=weewx.units.Converter(), **option_dict):

        # store various parameters received for later use
        self.db_lookup = db_lookup
        self.report_time = report_time
        self.formatter = formatter
        self.converter = converter
        self.option_dict = option_dict

    def this_span(self, data_binding=None, time_delta=0, hour_delta=0, day_delta=0,
                  week_delta=0, month_delta=0, year_delta=0):
        """Return a ThisTimespanBinder bound to a user specified time span."""

        # determine what time span is our universe of data, if no xxx_deltas
        # are specified then we use all records
        if any([time_delta, hour_delta, day_delta,
                week_delta, month_delta, year_delta]):
            # we have at least one delta setting so use it
            _span = weeutil.weeutil.archiveSpanSpan(self.report_time,
                                                    time_delta=time_delta,
                                                    hour_delta=hour_delta,
                                                    day_delta=day_delta,
                                                    week_delta=week_delta,
                                                    month_delta=month_delta,
                                                    year_delta=year_delta)
        else:
            # all deltas are zero (or None) so assume an alltime span
            # obtain a db_manager object
            db_manager = self.db_lookup(data_binding)
            # obtain the earliest and latest timestamps in the archive
            start_ts = db_manager.firstGoodStamp()
            end_ts = db_manager.lastGoodStamp()
            # construct a TimeSpan object to cover the entire time span covered
            # by the archive
            _span = TimeSpan(start_ts, end_ts)
        # return the next object in the chain
        return ThisTimespanBinder(_span,
                                  self.report_time,
                                  self.db_lookup,
                                  data_binding=data_binding,
                                  context='day',
                                  formatter=self.formatter,
                                  converter=self.converter,
                                  **self.option_dict)


# ==============================================================================
#                          class ThisTimespanBinder
# ==============================================================================

class ThisTimespanBinder(object):
    """ Holds a binding between a database and a timespan.

    Modified version of weewx.tags.TimespanBinder to support 'this' tags.

    This class is the next class in the chain of helper classes. When an
    observation type is given as an attribute to it (such as 'obj.outTemp'), the
    next item in the chain is returned, in this case an instance of
    ObservationBinder, which binds the database, the time period, and the
    statistical type all together.
    """
    def __init__(self, timespan, report_time, db_lookup, data_binding=None,
                 context='day', formatter=weewx.units.Formatter(),
                 converter=weewx.units.Converter(), **option_dict):

        self.timespan = timespan
        self.report_time = report_time
        self.db_lookup = db_lookup
        self.data_binding = data_binding
        self.context = context
        self.formatter = formatter
        self.converter = converter
        self.option_dict = option_dict

    def periods(self, period='day', timestamp=None, day_delta=0, week_delta=0,
                month_delta=0, year_delta=0):

        # determine the span calculation function and context to be
        # used
        if period.lower() == 'month':
            span_func = weeutil.weeutil.archiveMonthSpan
            context = 'month'
        elif period.lower() == 'week':
            span_func = weeutil.weeutil.archiveWeekSpan
            context = 'week'
        else:
            # default to 'day'
            span_func = weeutil.weeutil.archiveDaySpan
            context = 'day'
        # was an explicit timestamp set by the user, if so ue it, otherwise use
        # the report timestamp with any deltas applied
        if timestamp:
            ts = timestamp
        else:
            ts = calc_delta_ts(self.report_time,
                               day_delta=day_delta,
                               week_delta=week_delta,
                               month_delta=month_delta,
                               year_delta=year_delta)

        # iterate over 'this' period in the time period
        return ThisTimespanBinder._seq_generator(period_span,
                                                 self.timespan,
                                                 ts,
                                                 span_func,
                                                 self.db_lookup,
                                                 self.data_binding,
                                                 context,
                                                 self.formatter,
                                                 self.converter,
                                                 **self.option_dict)

    @staticmethod
    def _seq_generator(gen_span_func, timespan, report_time, span_func,
                       *args, **option_dict):
        """ Generator function that returns ThisTimespanBinder objects.

        Uses gen_span_func to obtain the appropriate timespans.
        """

        for span in gen_span_func(timespan.start, timespan.stop,
                                  report_time, span_func):
            yield ThisTimespanBinder(span, report_time, *args, **option_dict)

    @property
    def start(self):
        """Return the start time of a time period as a ValueHelper."""

        val = weewx.units.ValueTuple(self.timespan.start,
                                     'unix_epoch',
                                     'group_time')
        return weewx.units.ValueHelper(val,
                                       self.context,
                                       self.formatter,
                                       self.converter)

    @property
    def end(self):
        """Return the end time of a time period as a ValueHelper."""

        val = weewx.units.ValueTuple(self.timespan.stop,
                                     'unix_epoch',
                                     'group_time')
        return weewx.units.ValueHelper(val,
                                       self.context,
                                       self.formatter,
                                       self.converter)

    # alias for the start time:
    dateTime = start

    def __getattr__(self, obs_type):
        """Return a the next helper in the chain.

        Returns a helper object that binds the database, a time period,
        and the given observation type.

        obs_type: An observation type, such as 'outTemp', or 'heatDeg'

        returns: An instance of class weewx.tags.ObservationBinder.
        """

        # this is to get around bugs in the Python version of Cheetah's
        # namemapper
        if obs_type in ['__call__', 'has_key']:
            raise AttributeError

        # return a weewx.tags.ObservationBinder object, if an attribute is
        # requested from it, an aggregation value will be returned
        return weewx.tags.ObservationBinder(obs_type,
                                            self.timespan,
                                            self.db_lookup,
                                            self.data_binding,
                                            self.context,
                                            self.formatter,
                                            self.converter,
                                            **self.option_dict)


# ==============================================================================
#                              Utility Functions
# ==============================================================================

def period_span(start_ts, stop_ts, ts, span_func):
    """ Generator function to return timespans over a period."""

    # obtain the year to start from
    start_year = time.localtime(start_ts).tm_year
    # obtain the year to end at
    stop_year = time.localtime(stop_ts).tm_year
    # get the report time as a datetime object
    dt = datetime.datetime.fromtimestamp(ts)
    # iterate over each year from start to end and calculate the timespan of
    # interest
    for year_no in range(start_year, stop_year + 1):
        # replace the year in the datetime object representing the report time,
        # be prepared to catch the error if it is 29 February and we try to
        # change the year to a non-leap year
        try:
            year_dt = dt.replace(year=year_no)
        except ValueError:
            # it's 29 February and we tried to use a non-leap year, just skip
            # this year and continue to the next
            continue
        # convert the modified datetime object to an epoch timestamp
        year_ts = time.mktime(year_dt.timetuple())
        # if year_ts is not in our timespan of interest then skip it
        if year_ts < start_ts or year_ts > stop_ts:
            continue
        # yield the timespan for the day containing hte modified timestamp
        yield span_func(year_ts)


def calc_delta_ts(ts, day_delta=0, week_delta=0, month_delta=0, year_delta=0):
    """Calculate an offset timestamp given a timestamp and a series of deltas.

    Based on the calculations in weeutil.weeutil.archiveSpanSpan
    """

    # use a datetime.timedelta so that it can take DST into account
    _ts_dt = datetime.datetime.fromtimestamp(ts)
    # apply the day and week deltas
    _ts_dt -= datetime.timedelta(weeks=week_delta, days=day_delta)
    # Now add the deltas for months and years. Because these can be variable in
    # length, some special arithmetic is needed. Start by calculating the
    # number of months since 0 AD.
    total_months = 12 * _ts_dt.year + _ts_dt.month - 1 - 12 * year_delta - month_delta
    # convert back from total months since 0 AD to year and month
    year = total_months // 12
    month = total_months % 12 + 1
    # apply the delta to our datetime object
    _ts_dt = _ts_dt.replace(year=year, month=month)
    # finally return a timestamp
    return int(time.mktime(_ts_dt.timetuple()))
