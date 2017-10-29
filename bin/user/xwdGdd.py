#
#    Copyright (c) 2009-2015 Tom Keffer <tkeffer@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#
"""Extended stats based on the xsearch example

              GDD Tage
"""
import datetime
import time
import os
import sys
import syslog
import weewx
import weewx.units
import weeutil.weeutil

from weewx.cheetahgenerator import SearchList
from weewx.tags import TimespanBinder
from weeutil.weeutil import TimeSpan, genDaySpans
from weewx.units import ValueHelper, getStandardUnitType
from datetime import date, timedelta


def logmsg(level, msg):
    syslog.syslog(level, 'xwdGdd: %s' % msg)

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

class wdGdDays(SearchList):

    def __init__(self, generator):
        SearchList.__init__(self, generator)
        # Get temperature group - determines whether we return GDD in F or C
        # Enclose in try..except just in case. Default to degree_C if any errors
        try:
            self.temp_group = generator.skin_dict['Units']['Groups'].get('group_temperature', 'degree_C')
        except KeyError:
            self.temp_group = 'degree_C'
        # Get GDD base temp and save as a ValueTuple
        # Enclose in try..except just in case. Default to 10 deg C if any errors
        try:
            _base_t = weeutil.weeutil.option_as_list(generator.skin_dict['Extras']['GDD'].get('base', (10, 'degree_C')))
            self.gdd_base_vt = (float(_base_t[0]), _base_t[1], 'group_temperature')
        except KeyError:
            self.gdd_base_vt = (10.0, 'degree_C', 'group_temperature')

    def get_extension_list(self, timespan, db_lookup):
        """Returns Growing Degree Days tags.

           Returns a number representing to date Growing Degree Days (GDD) for
           various periods. GDD can be represented as GGD Fahrenheit (GDD F) or
           GDD Celsius (GDD C), 5 GDD C = 9 GDD F. As the standard
           Fahrenheit/Celsius conversion formula cannot be used to convert
           between GDD F and GDD C Weew ValueTuples cannot be used for the
           results and hence the results are returned in the group_temperature
           units specified in the associated skin.conf.

           The base temperature used in calculating GDD can be set using the
           'base' parameter under [Extras][[GDD]] in the associated skin.conf
           file. The base parameter consists of a numeric value followed by a
           unit string eg 10, degree_C or 50, degree_F. If the parameter is
           omitted or cannot be decoded then a default of 10, degree_C is used.

        Parameters:
          timespan: An instance of weeutil.weeutil.TimeSpan. This will
                    hold the start and stop times of the domain of
                    valid times.

          db_lookup: This is a function that, given a data binding
                     as its only parameter, will return a database manager
                     object.

        Returns:
          month_gdd:    Growing Degree Days to date this month. Numeric value
                        only, not a ValueTuple.
          year_gdd:     Growing Degree Days to date this year. Numeric value
                        only, not a ValueTuple.
        """

        t1 = time.time()

        ##
        ## Get units for use later with ValueHelpers
        ##
        
        # Get current record from the archive
        if not self.generator.gen_ts:
            self.generator.gen_ts = db_lookup().lastGoodStamp()
        current_rec = db_lookup().getRecord(self.generator.gen_ts)
        # Get the unit in use for each group
        (outTemp_type, outTemp_group) = getStandardUnitType(current_rec['usUnits'], 'outTemp')

        ##
        ## Get timestamps we need for the periods of interest
        ##
        # Get ts for midnight at the end of period
        _mn_stop_ts = weeutil.weeutil.startOfDay(timespan.stop)
        # Get time obj for midnight
        _mn_t = datetime.time(0)
        # Get datetime obj for now
        _today_dt = datetime.datetime.today()
        # Get midnight 1st of the month as a datetime object and then get it as a
        # timestamp
        first_of_month_dt = get_first_day(_today_dt)
        _mn_first_of_month_dt = datetime.datetime.combine(first_of_month_dt, _mn_t)
        _mn_first_of_month_ts = time.mktime(_mn_first_of_month_dt.timetuple())
        # Get midnight 1st of the year as a datetime object and then get it as a
        # timestamp
        _first_of_year_dt = get_first_day(_today_dt, 0, 1-_today_dt.month)
        _mn_first_of_year_dt = datetime.datetime.combine(_first_of_year_dt, _mn_t)
        _mn_first_of_year_ts = time.mktime(_mn_first_of_year_dt.timetuple())

        interDict = {'start' : _mn_first_of_month_ts,
                     'stop'  : _mn_stop_ts-1}
        _row = db_lookup().getSql("SELECT SUM(max), SUM(min), COUNT(*) FROM archive_day_outTemp WHERE dateTime >= ? AND dateTime < ?", (_mn_first_of_month_ts, _mn_stop_ts-1))
        try:
            _t_max_sum = _row[0]
            _t_min_sum = _row[1]
            _count = _row[2]
            _month_gdd = (_t_max_sum + _t_min_sum)/2 - weewx.units.convert(self.gdd_base_vt, outTemp_type)[0] * _count
            if outTemp_type == self.temp_group:  # so our input is in the same units as our output
                _month_gdd = round(_month_gdd, 1)
            elif self.temp_group == 'degree_C':     # input if deg F and but want output in deg C
                _month_gdd = round(_month_gdd * 1.8, 1)
            else:   # input if deg C and but want output in deg F
                _month_gdd = round(_month_gdd * 5 / 9, 1)
            if _month_gdd < 0.0:
                _month_gdd = 0.0
        except:
            _month_gdd = None


        interDict = {'start' : _mn_first_of_year_ts,
                     'stop'  : _mn_stop_ts-1}

        _row = db_lookup().getSql("SELECT SUM(max), SUM(min), COUNT(*) FROM archive_day_outTemp WHERE dateTime >= ? AND dateTime < ?", (_mn_first_of_year_ts, _mn_stop_ts-1))

        try:
            _t_max_sum = _row[0]
            _t_min_sum = _row[1]
            _count = _row[2]
            _year_gdd = (_t_max_sum + _t_min_sum)/2 - weewx.units.convert(self.gdd_base_vt, outTemp_type)[0] * _count
            #_year_gdd = (_t_max_sum + _t_min_sum)/2 - 10.0 * _count
            #if outTemp_type == self.temp_group:  # so our input is in the same units as our output
            _year_gdd = round(_year_gdd, 1)

            #loginf("wdGdDays Month,Year: %s: %s" % (_month_gdd, _year_gdd))

            #elif self.temp_group == 'degree_C':     # input if deg F and but want output in deg C
            #    _year_gdd = round(_year_gdd * 1.8, 1)
            #else:   # input if deg C and but want output in deg F
            #    _year_gdd = round(_year_gdd * 5 / 9, 1)
            if _year_gdd < 0.0:
                _year_gdd = 0.0
        except:
            _year_gdd = None
        
        # Create a small dictionary with the tag names (keys) we want to use
        search_list_extension = {'month_gdd': _month_gdd,
                                 'year_gdd': _year_gdd,
                                }
                                 
        t2 = time.time()
        logdbg("wdGdDays SLE executed in %0.3f seconds" % (t2-t1))
        
        return [search_list_extension]

