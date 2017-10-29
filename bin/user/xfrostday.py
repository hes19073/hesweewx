#
#    Copyright (c) 2009-2015 Tom Keffer <tkeffer@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#
"""Extended stats based on the xsearch example

              Frosttage
"""
import datetime
import time
import calendar
import os
import sys
import syslog
import itertools
import weewx
import weewx.units
import weeutil.weeutil

from weewx.cheetahgenerator import SearchList
from weewx.tags import TimespanBinder
from weeutil.weeutil import TimeSpan, genDaySpans
from weewx.units import ValueHelper, getStandardUnitType
from datetime import date, timedelta


def logmsg(level, msg):
    syslog.syslog(level, 'MyFrostDays: %s' % msg)

def logdbg(msg):
    logmsg(syslog.LOG_DEBUG, msg)

def loginf(msg):
    logmsg(syslog.LOG_INFO, msg)

def logerr(msg):
    logmsg(syslog.LOG_ERR, msg)

WEEWX_FROST_DAYS_VERSION = '0.0.1'

def get_first_day(dt, d_years=0, d_months=0):
    """Function to return date object holding 1st of month containing dt
       d_years, d_months are offsets that may be applied to dt
    """

    # Get year number and month number applying offset as required
    _y, _m = dt.year + d_years, dt.month + d_months
    # Calculate actual month number taking into account EOY rollover
    _a, _m = divmod(_m-1, 12)
    # Calculate and return date object
    return date(_y+_a, _m+1, 1)


class MyFrostDays(SearchList):

    def __init__(self, generator):
        SearchList.__init__(self, generator)

    def get_extension_list(self, timespan, db_lookup):
        """Returns various tags related to longest periods of outTemp min<0 days.

        Parameters:
          timespan: An instance of weeutil.weeutil.TimeSpan. This will
                    hold the start and stop times of the domain of
                    valid times.

          db_lookup: This is a function that, given a data binding
                     as its only parameter, will return a database manager
                     object.

        Returns:
          lastfrost_day                 last day of the year if outTemp MIN < 0
          lastfrost_delta_time          days, horas, mins lastfrost_day to now 

          year_frost_minE_days:         Length of longest run of consecutive min<0
                                        days in current year
          year_frost_minE_days_time:    End dateTime of longest run of
                                        consecutive min<0 days in current year
          year_frost_minS_days_time:    Start dateTime of longest run of
                                        consecutive min<0 days in current year
          alltime_frost_minE_days:      Length of alltime longest run of
                                        consecutive min<0 days
          alltime_frost_minE_days_time: End dateTime of alltime longest run of
                                        consecutive min<0 days
          alltime_frost_minS_days_time: Start dateTime of alltime longest run of
                                        consecutive min<0 days

          year_frost_maxE_days:         Length of longest run of consecutive max<0
                                        days in current year
          year_frost_maxE_days_time:    End dateTime of longest run of
          year_frost_maxS_days_time:    Start dateTime of longest run of
                                        consecutive max<0 days in current year
          alltime_frost_maxE_days:      Length of alltime longest run of
                                        consecutive max<0 days
          alltime_frost_maxE_days_time: End dateTime of alltime longest run of
          alltime_frost_maxS_days_time: Start dateTime of alltime longest run of
                                        consecutive max<0 days

        """

        t1= time.time()

        # Get current record from the archive
        if not self.generator.gen_ts:
            self.generator.gen_ts = db_lookup().lastGoodStamp()
        current_rec = db_lookup().getRecord(self.generator.gen_ts)
        # Get our time unit
        (dateTime_type, dateTime_group) = getStandardUnitType(current_rec['usUnits'], 'dateTime')

        ##
        ## Get timestamps we need for the periods of interest
        ##
        # Get time obj for midnight
        _mn_t = datetime.time(0)
        # Get date obj for now
        _today_d = datetime.datetime.today()
        # Get midnight 1st of the year as a datetime object and then get it as a
        # timestamp
        _first_of_year_dt = get_first_day(_today_d, 0, 1-_today_d.month)
        _mn_first_of_year_dt = datetime.datetime.combine(_first_of_year_dt, _mn_t)
        _mn_first_of_year_ts = time.mktime(_mn_first_of_year_dt.timetuple())
        _year_ts = TimeSpan(_mn_first_of_year_ts, timespan.stop)


        # First, create a TimespanBinder object for all time. 
        _row = db_lookup().getSql("SELECT MAX(dateTime) FROM archive_day_outTemp WHERE min < 0")
        lastfrost_ts = _row[0]

        if lastfrost_ts is not None:
            try:
                _row = db_lookup().getSql("SELECT MAX(dateTime) FROM archive WHERE outTemp < 0 AND dateTime > ? AND dateTime <= ?", (lastfrost_ts, lastfrost_ts + 86400))
                _lastfrost_ts = _row[0]
            except:
                _lastfrost_ts = None


        # Get our year stats vectors
        _outTemp_vector = []
        _time_vector = []
        for tspan in weeutil.weeutil.genDaySpans(_mn_first_of_year_ts, timespan.stop):
            _row = db_lookup().getSql("SELECT dateTime, min FROM archive_day_outTemp WHERE dateTime >= ? AND dateTime < ? ORDER BY dateTime", (tspan.start, tspan.stop))
            if _row is not None:
                _time_vector.append(_row[0])
                _outTemp_vector.append(_row[1])
        # Get our run of year min0 days
        _interim = []   # List to hold details of any runs we might find
        _index = 0      # Placeholder so we can track the start dateTime of any runs
        # Use itertools groupby method to make our search for a run easier
        # Step through each of the groups itertools has found
        for k,g in itertools.groupby(_outTemp_vector):
            _length = len(list(g))
            if k < 0:   # If we have a run of les then 0 degree C (ie no outTemp) add it to our
                        # list of runs
                _interim.append((k, _length, _index))
            _index += _length
        if _interim != []:
            # If we found a run (we want the longest one) then get our results
            (_temp, _year_minE_run, _position) = max(_interim, key=lambda a:a[1])
            # Our 'time' is the day the run ends so we need to add on run-1 days
            _year_minE_time_ts = _time_vector[_position] + (_year_minE_run - 1) * 86400
            _year_minS_time_ts = _year_minE_time_ts - (86400 * _year_minE_run)
        else:
            # If we did not find a run then set our results accordingly
            _year_minE_run = 0
            _year_minE_time_ts = None
            _year_minS_time_ts = None

        # Get our year stats vectors
        _outTemp_vector = []
        _time_vector = []
        for tspan in weeutil.weeutil.genDaySpans(_mn_first_of_year_ts, timespan.stop):
            _row = db_lookup().getSql("SELECT dateTime, max FROM archive_day_outTemp WHERE dateTime >= ? AND dateTime < ? ORDER BY dateTime", (tspan.start, tspan.stop))
            if _row is not None:
                _time_vector.append(_row[0])
                _outTemp_vector.append(_row[1])
        # Get our run of year max0 days
        _interim = []   # List to hold details of any runs we might find
        _index = 0      # Placeholder so we can track the start dateTime of any runs
        # Use itertools groupby method to make our search for a run easier
        # Step through each of the groups itertools has found
        for k,g in itertools.groupby(_outTemp_vector):
            _length = len(list(g))
            if k < 0:   # If we have a run of les then 0 degree C (ie no outTemp) add it to our
                        # list of runs
                _interim.append((k, _length, _index))
            _index += _length
        if _interim != []:
            # If we found a run (we want the longest one) then get our results
            (_temp, _year_maxE_run, _position) = max(_interim, key=lambda a:a[1])
            # Our 'time' is the day the run ends so we need to add on run-1 days
            _year_maxE_time_ts = _time_vector[_position] + (_year_maxE_run - 1) * 86400
            _year_maxS_time_ts = _year_minE_time_ts - (86400 * _year_maxE_run)
        else:
            # If we did not find a run then set our results accordingly
            _year_maxE_run = 0
            _year_maxE_time_ts = None
            _year_maxS_time_ts = None

        # Get our alltime stats vectors
        _outTemp_vector = []
        _time_vector = []
        for tspan in weeutil.weeutil.genDaySpans(timespan.start, timespan.stop):
            _row = db_lookup().getSql("SELECT dateTime, min FROM archive_day_outTemp WHERE dateTime >= ? AND dateTime < ? ORDER BY dateTime", (tspan.start, tspan.stop))
            if _row is not None:
                _time_vector.append(_row[0])
                _outTemp_vector.append(_row[1])
        # Get our run of alltime min0 days
        _interim = []   # List to hold details of any runs we might find
        _index = 0      # Placeholder so we can track the start dateTime of any runs
        # Use itertools groupby method to make our search for a run easier
        # Step through each of the groups itertools has found
        for k,g in itertools.groupby(_outTemp_vector):
            _length = len(list(g))
            if k < 0:  # If we have a run of 0s (ie no outTemp) add it to our
                        # list of runs
                _interim.append((k, _length, _index))
            _index += _length
        if _interim != []:
            # If we found a run (we want the longest one) then get our results
            (_temp, _alltime_minE_run, _position) = max(_interim, key=lambda a:a[1])
            # Our 'time' is the day the run ends so we need to add on run-1 days
            _alltime_minE_time_ts = _time_vector[_position] + (_alltime_minE_run - 1) * 86400
            _alltime_minS_time_ts = _alltime_minE_time_ts - (86400 * _alltime_minE_run)

        else:
            # If we did not find a run then set our results accordingly
            _alltime_minE_run = 0
            _alltime_minE_time_ts = None
            _alltime_minS_time_ts = None

        # Get our alltime stats vectors
        _outTemp_vector = []
        _time_vector = []
        for tspan in weeutil.weeutil.genDaySpans(timespan.start, timespan.stop):
            _row = db_lookup().getSql("SELECT dateTime, max FROM archive_day_outTemp WHERE dateTime >= ? AND dateTime < ? ORDER BY dateTime", (tspan.start, tspan.stop))
            if _row is not None:
                _time_vector.append(_row[0])
                _outTemp_vector.append(_row[1])
        # Get our run of alltime min0 days
        _interim = []   # List to hold details of any runs we might find
        _index = 0      # Placeholder so we can track the start dateTime of any runs
        # Use itertools groupby method to make our search for a run easier
        # Step through each of the groups itertools has found
        for k,g in itertools.groupby(_outTemp_vector):
            _length = len(list(g))
            if k < 0:  # If we have a run of 0s (ie no outTemp) add it to our
                        # list of runs
                _interim.append((k, _length, _index))
            _index += _length
        if _interim != []:
            # If we found a run (we want the longest one) then get our results
            (_temp, _alltime_maxE_run, _position) = max(_interim, key=lambda a:a[1])
            # Our 'time' is the day the run ends so we need to add on run-1 days
            _alltime_maxE_time_ts = _time_vector[_position] + (_alltime_maxE_run - 1) * 86400
            _alltime_maxS_time_ts = _alltime_maxE_time_ts - (86400 * _alltime_maxE_run)

        else:
            # If we did not find a run then set our results accordingly
            _alltime_maxE_run = 0
            _alltime_maxE_time_ts = None
            _alltime_maxS_time_ts = None

        # Make our timestamps ValueHelpers to give more flexibility in how we can format them in our reports
        _lastfrost_vt = (_lastfrost_ts, dateTime_type, dateTime_group)
        _lastfrost_vh = ValueHelper(_lastfrost_vt, formatter=self.generator.formatter, converter=self.generator.converter)

        _delta_time = time.time() - _lastfrost_ts if _lastfrost_ts else None
        _delta_time_vt = (_delta_time, 'second', 'group_deltatime')
        _delta_time_vh = ValueHelper(_delta_time_vt, formatter=self.generator.formatter, converter=self.generator.converter)

        _year_minE_time_vt = (_year_minE_time_ts, dateTime_type, dateTime_group)
        _year_minE_time_vh = ValueHelper(_year_minE_time_vt, formatter=self.generator.formatter, converter=self.generator.converter)
        _year_minS_time_vt = (_year_minS_time_ts, dateTime_type, dateTime_group)
        _year_minS_time_vh = ValueHelper(_year_minS_time_vt, formatter=self.generator.formatter, converter=self.generator.converter)

        _year_maxE_time_vt = (_year_maxE_time_ts, dateTime_type, dateTime_group)
        _year_maxE_time_vh = ValueHelper(_year_maxE_time_vt, formatter=self.generator.formatter, converter=self.generator.converter)
        _year_maxS_time_vt = (_year_maxS_time_ts, dateTime_type, dateTime_group)
        _year_maxS_time_vh = ValueHelper(_year_maxS_time_vt, formatter=self.generator.formatter, converter=self.generator.converter)

        _alltime_minE_time_vt = (_alltime_minE_time_ts, dateTime_type, dateTime_group)
        _alltime_minE_time_vh = ValueHelper(_alltime_minE_time_vt, formatter=self.generator.formatter, converter=self.generator.converter)
        _alltime_minS_time_vt = (_alltime_minS_time_ts, dateTime_type, dateTime_group)
        _alltime_minS_time_vh = ValueHelper(_alltime_minS_time_vt, formatter=self.generator.formatter, converter=self.generator.converter)

        _alltime_maxE_time_vt = (_alltime_maxE_time_ts, dateTime_type, dateTime_group)
        _alltime_maxE_time_vh = ValueHelper(_alltime_maxE_time_vt, formatter=self.generator.formatter, converter=self.generator.converter)
        _alltime_maxS_time_vt = (_alltime_maxS_time_ts, dateTime_type, dateTime_group)
        _alltime_maxS_time_vh = ValueHelper(_alltime_maxS_time_vt, formatter=self.generator.formatter, converter=self.generator.converter)

        # Create a small dictionary with the tag names (keys) we want to use
        search_list_extension = {'lastfrost_day': _lastfrost_vh,
                                 'lastfrost_delta_time': _delta_time_vh, 
                                 'year_frost_minE_days': _year_minE_run,
                                 'year_frost_minE_days_time': _year_minE_time_vh,
                                 'year_frost_minS_days_time': _year_minS_time_vh,
                                 'year_frost_maxE_days': _year_maxE_run,
                                 'year_frost_maxE_days_time': _year_maxE_time_vh,
                                 'year_frost_maxS_days_time': _year_maxS_time_vh,

                                 'alltime_frost_minE_days': _alltime_minE_run,
                                 'alltime_frost_minE_days_time': _alltime_minE_time_vh,
                                 'alltime_frost_minS_days_time': _alltime_minS_time_vh,
                                 'alltime_frost_maxE_days': _alltime_maxE_run,
                                 'alltime_frost_maxE_days_time': _alltime_maxE_time_vh,
                                 'alltime_frost_maxS_days_time': _alltime_maxS_time_vh}


        t2= time.time()
        logdbg("MyFrostDays SLE executed in %0.3f seconds" % (t2-t1))

        return [search_list_extension]


