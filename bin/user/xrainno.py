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

regentage
"""
import datetime
import time
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
    syslog.syslog(level, 'xrainno: %s' % msg)

def logdbg(msg):
    logmsg(syslog.LOG_DEBUG, msg)

def loginf(msg):
    logmsg(syslog.LOG_INFO, msg)

def logerr(msg):
    logmsg(syslog.LOG_ERR, msg)



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


class MyXRainNo(SearchList):

    def __init__(self, generator):
        SearchList.__init__(self, generator)

    def get_extension_list(self, timespan, db_lookup):
        """Returns various tags related to longest periods of rainy/dry days.
        
           This SLE uses the stats database daily rainfall totals to determine
           the longest runs of consecutive dry or wet days over various periods
           (month, year, alltime). The SLE also determines the start date of 
           each run.
           
           Period (xxx_days) tags are returned as integer numbers of days.
           Times (xx_time) tags are returned as dateTime ValueHelpers set to 
           midnight (at start) of the first day of the run concerned. If the 
           length of the run is 0 then the corresponding start time of the run
           is returned as None.

        Parameters:
          timespan: An instance of weeutil.weeutil.TimeSpan. This will
                    hold the start and stop times of the domain of 
                    valid times.

          db_lookup: This is a function that, given a data binding
                     as its only parameter, will return a database manager
                     object.

        Returns:
          month_con_dry_days:        Length of longest run of consecutive dry
                                     days in current month
          month_con_dry_days_time:   Start dateTime of longest run of 
                                     consecutive dry days in current month
          month_con_wet_days:        Length of longest run of consecutive wet 
                                     days in current month
          month_con_wet_days_time:   Start dateTime of longest run of 
                                     consecutive wet days in current month
          year_con_dry_days:         Length of longest run of consecutive dry 
                                     days in current year
          year_con_dry_days_time:    Start dateTime of longest run of 
                                     consecutive dry days in current year
          year_con_wet_days:         Length of longest run of consecutive wet 
                                     days in current year
          year_con_wet_days_time:    Start dateTime of longest run of 
                                     consecutive wet days in current year
          alltime_con_dry_days:      Length of alltime longest run of 
                                     consecutive dry days
          alltime_con_dry_days_time: Start dateTime of alltime longest run of 
                                     consecutive dry days
          alltime_con_wet_days:      Length of alltime longest run of 
                                     consecutive wet days
          alltime_con_wet_days_time: Start dateTime of alltime longest run of
                                     consecutive wet days

        """

        t1= time.time()

        ##
        ## Get units for use later with ValueHelpers
        ##
        # Get current record from the archive
        if not self.generator.gen_ts:
            self.generator.gen_ts = db_lookup().lastGoodStamp()
        current_rec = db_lookup().getRecord(self.generator.gen_ts)
        # Get our time unit
        (dateTime_type, dateTime_group) = getStandardUnitType(current_rec['usUnits'], 'dateTime')
        #dateTime_type = unix_epoch
        #dateTime_group = dateTime
        
        ##
        ## Get timestamps we need for the periods of interest
        ##
        # Get time obj for midnight
        _mn_t = datetime.time(0)
        # Get date obj for now
        _today_d = datetime.datetime.today()
        # Get midnight 1st of the month as a datetime object and then get it as a
        # timestamp
        first_of_month_dt = get_first_day(_today_d)
        _mn_first_of_month_dt = datetime.datetime.combine(first_of_month_dt, _mn_t)
        _mn_first_of_month_ts = time.mktime(_mn_first_of_month_dt.timetuple())
        _month_ts = TimeSpan(_mn_first_of_month_ts, timespan.stop)
        # Get midnight 1st of the year as a datetime object and then get it as a
        # timestamp
        _first_of_year_dt = get_first_day(_today_d, 0, 1-_today_d.month)
        _mn_first_of_year_dt = datetime.datetime.combine(_first_of_year_dt, _mn_t)
        _mn_first_of_year_ts = time.mktime(_mn_first_of_year_dt.timetuple())
        _year_ts = TimeSpan(_mn_first_of_year_ts, timespan.stop)
        
        # Get vectors of our month stats
        _rain_vector = []
        _time_vector = []
        # Step through each day in our month timespan and get our daily rain 
        # total and timestamp. This is a day_archive version of the archive 
        # getSqlVectors method.
        for tspan in weeutil.weeutil.genDaySpans(_mn_first_of_month_ts, timespan.stop):
            _row = db_lookup().getSql("SELECT dateTime, sum FROM archive_day_rain WHERE dateTime >= ? AND dateTime < ? ORDER BY dateTime", (tspan.start, tspan.stop))
            if _row is not None:
                _time_vector.append(_row[0])
                _rain_vector.append(_row[1])
        # As an aside lets get our number of rainy days this month
        _month_rainy_days = sum(1 for i in _rain_vector if i > 0)
        # Get our run of month dry days
        _interim = []   # List to hold details of any runs we might find
        _index = 0      # Placeholder so we can track the start dateTime of any runs
        # Use itertools groupby method to make our search for a run easier
        # Step through each of the groups itertools has found
        for k,g in itertools.groupby(_rain_vector):
            _length = len(list(g))
            if k == 0:  # If we have a run of 0s (ie no rain) add it to our 
                        # list of runs
                _interim.append((k, _length, _index))
            _index += _length
        if _interim != []:
            # If we found a run (we want the longest one) then get our results
            (_temp, _month_dry_run, _position) = max(_interim, key=lambda a:a[1])
            # Our 'time' is the day the run ends so we need to add on run-1 days
            _month_dry_time_ts = _time_vector[_position] + (_month_dry_run - 1) * 86400
        else:
            # If we did not find a run then set our results accordingly
            _month_dry_run = 0
            _month_dry_time_ts = None
        
        # Get our run of month rainy days
        _interim = []   # List to hold details of any runs we might find
        _index = 0      # Placeholder so we can track the start dateTime of any runs
        # Use itertools groupby method to make our search for a run easier
        # Step through each of the groups itertools has found
        for k,g in itertools.groupby(_rain_vector, key=lambda r:1 if r > 0 else 0):
            _length = len(list(g))
            if k > 0:   # If we have a run of something > 0 (ie some rain) add
                        # it to our list of runs
                _interim.append((k, _length, _index))
            _index += _length
        if _interim != []:
            # If we found a run (we want the longest one) then get our results
            (_temp, _month_wet_run, _position) = max(_interim, key=lambda a:a[1])
            # Our 'time' is the day the run ends so we need to add on run-1 days
            _month_wet_time_ts = _time_vector[_position] + (_month_wet_run - 1) * 86400
        else:
            # If we did not find a run then set our results accordingly
            _month_wet_run = 0
            _month_wet_time_ts = None

        # Get our year stats vectors
        _rain_vector = []
        _time_vector = []
        for tspan in weeutil.weeutil.genDaySpans(_mn_first_of_year_ts, timespan.stop):
            _row = db_lookup().getSql("SELECT dateTime, sum FROM archive_day_rain WHERE dateTime >= ? AND dateTime < ? ORDER BY dateTime", (tspan.start, tspan.stop))
            if _row is not None:
                _time_vector.append(_row[0])
                _rain_vector.append(_row[1])
        # Get our run of year dry days
        _interim = []   # List to hold details of any runs we might find
        _index = 0      # Placeholder so we can track the start dateTime of any runs
        # Use itertools groupby method to make our search for a run easier
        # Step through each of the groups itertools has found
        for k,g in itertools.groupby(_rain_vector):
            _length = len(list(g))
            if k == 0:  # If we have a run of 0s (ie no rain) add it to our 
                        # list of runs
                _interim.append((k, _length, _index))
            _index += _length
        if _interim != []:
            # If we found a run (we want the longest one) then get our results
            (_temp, _year_dry_run, _position) = max(_interim, key=lambda a:a[1])
            # Our 'time' is the day the run ends so we need to add on run-1 days
            _year_dry_time_ts = _time_vector[_position] + (_year_dry_run - 1) * 86400
        else:
            # If we did not find a run then set our results accordingly
            _year_dry_run = 0
            _year_dry_time_ts = None

        # Get our run of year rainy days
        _interim = []   # List to hold details of any runs we might find
        _index = 0      # Placeholder so we can track the start dateTime of any runs
        # Use itertools groupby method to make our search for a run easier
        # Step through each of the groups itertools has found
        for k,g in itertools.groupby(_rain_vector, key=lambda r:1 if r > 0 else 0):
            _length = len(list(g))
            if k > 0:   # If we have a run of something > 0 (ie some rain) add
                        # it to our list of runs
                _interim.append((k, _length, _index))
            _index += _length
        if _interim != []:
            # If we found a run (we want the longest one) then get our results
            (_temp, _year_wet_run, _position) = max(_interim, key=lambda a:a[1])
            # Our 'time' is the day the run ends so we need to add on run-1 days
            _year_wet_time_ts = _time_vector[_position] + (_year_wet_run - 1) * 86400
        else:
            # If we did not find a run then set our results accordingly
            _year_wet_run = 0
            _year_wet_time_ts = None

        # Get our alltime stats vectors
        _rain_vector = []
        _time_vector = []
        for tspan in weeutil.weeutil.genDaySpans(timespan.start, timespan.stop):
            _row = db_lookup().getSql("SELECT dateTime, sum FROM archive_day_rain WHERE dateTime >= ? AND dateTime < ? ORDER BY dateTime", (tspan.start, tspan.stop))
            if _row is not None:
                _time_vector.append(_row[0])
                _rain_vector.append(_row[1])
        # Get our run of alltime dry days
        _interim = []   # List to hold details of any runs we might find
        _index = 0      # Placeholder so we can track the start dateTime of any runs
        # Use itertools groupby method to make our search for a run easier
        # Step through each of the groups itertools has found
        for k,g in itertools.groupby(_rain_vector):
            _length = len(list(g))
            if k == 0:  # If we have a run of 0s (ie no rain) add it to our 
                        # list of runs
                _interim.append((k, _length, _index))
            _index += _length
        if _interim != []:
            # If we found a run (we want the longest one) then get our results
            (_temp, _alltime_dry_run, _position) = max(_interim, key=lambda a:a[1])
            # Our 'time' is the day the run ends so we need to add on run-1 days
            _alltime_dry_time_ts = _time_vector[_position] + (_alltime_dry_run - 1) * 86400
        else:
            # If we did not find a run then set our results accordingly
            _alltime_dry_run = 0
            _alltime_dry_time_ts = None

        # Get our run of alltime rainy days
        _interim = []   # List to hold details of any runs we might find
        _index = 0      # Placeholder so we can track the start dateTime of any runs
        # Use itertools groupby method to make our search for a run easier
        # Step through each of the groups itertools has found
        for k,g in itertools.groupby(_rain_vector, key=lambda r:1 if r > 0 else 0):
            _length = len(list(g))
            if k > 0:   # If we have a run of something > 0 (ie some rain) add
                        # it to our list of runs
                _interim.append((k, _length, _index))
            _index += _length
        if _interim != []:
            # If we found a run (we want the longest one) then get our results
            (_temp, _alltime_wet_run, _position) = max(_interim, key=lambda a:a[1])
            # Our 'time' is the day the run ends so we need to add on run-1 days
            _alltime_wet_time_ts = _time_vector[_position] + (_alltime_wet_run - 1) * 86400
        else:
            # If we did not find a run then set our results accordingly
            _alltime_wet_run = 0
            _alltime_wet_time_ts = None
        
        # Make our timestamps ValueHelpers to give more flexibility in how we can format them in our reports
        _month_dry_time_vt = (_month_dry_time_ts, dateTime_type, dateTime_group)
        _month_dry_time_vh = ValueHelper(_month_dry_time_vt, formatter=self.generator.formatter, converter=self.generator.converter)
        _month_wet_time_vt = (_month_wet_time_ts, dateTime_type, dateTime_group)
        _month_wet_time_vh = ValueHelper(_month_wet_time_vt, formatter=self.generator.formatter, converter=self.generator.converter)
        _year_dry_time_vt = (_year_dry_time_ts, dateTime_type, dateTime_group)
        _year_dry_time_vh = ValueHelper(_year_dry_time_vt, formatter=self.generator.formatter, converter=self.generator.converter)
        _year_wet_time_vt = (_year_wet_time_ts, dateTime_type, dateTime_group)
        _year_wet_time_vh = ValueHelper(_year_wet_time_vt, formatter=self.generator.formatter, converter=self.generator.converter)
        _alltime_dry_time_vt = (_alltime_dry_time_ts, dateTime_type, dateTime_group)
        _alltime_dry_time_vh = ValueHelper(_alltime_dry_time_vt, formatter=self.generator.formatter, converter=self.generator.converter)
        _alltime_wet_time_vt = (_alltime_wet_time_ts, dateTime_type, dateTime_group)
        _alltime_wet_time_vh = ValueHelper(_alltime_wet_time_vt, formatter=self.generator.formatter, converter=self.generator.converter)
        
        # Create a small dictionary with the tag names (keys) we want to use
        search_list_extension = {'month_con_dry_days': _month_dry_run,
                                 'month_con_dry_days_time': _month_dry_time_vh,
                                 'year_con_dry_days': _year_dry_run,
                                 'year_con_dry_days_time': _year_dry_time_vh,
                                 'alltime_con_dry_days': _alltime_dry_run,
                                 'alltime_con_dry_days_time': _alltime_dry_time_vh,
                                 'month_con_wet_days': _month_wet_run,
                                 'month_con_wet_days_time': _month_wet_time_vh,
                                 'year_con_wet_days': _year_wet_run,
                                 'year_con_wet_days_time': _year_wet_time_vh,
                                 'alltime_con_wet_days': _alltime_wet_run,
                                 'alltime_con_wet_days_time': _alltime_wet_time_vh,
                                 'month_rainy_days': _month_rainy_days}
        t2= time.time()
        logdbg("MyXRainNo SLE executed in %0.3f seconds" % (t2-t1))

        return [search_list_extension]
