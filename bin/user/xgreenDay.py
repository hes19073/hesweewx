#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# Version: 0.0.4                                    Date: 06 April 2017
#
import datetime
import time
import os
import weewx
import weedb
import weeutil.weeutil
import weewx.units
import syslog
import weewx.tags

from weewx.cheetahgenerator import SearchList
from weewx.tags import TimeBinder, TimespanBinder
from weeutil.weeutil import TimeSpan, genDaySpans, startOfDay
from weewx.units import ValueHelper, getStandardUnitType, ValueTuple
from datetime import date

green_VERSION = '0.0.4'

def logmsg(level, msg):
    syslog.syslog(level, 'xGreenDay: %s' % msg)

def logdbg(msg):
    logmsg(syslog.LOG_DEBUG, msg)

def loginf(msg):
    logmsg(syslog.LOG_INFO, msg)

def logerr(msg):
    logmsg(syslog.LOG_ERR, msg)

class xGreenDay(SearchList):

    def __init__(self, generator):
        SearchList.__init__(self, generator)

    def get_extension_list(self, timespan, db_lookup):
        """Returns green Day dateTime and green Day Temp Sum.

           For day in year get green_temp > 200
           If the day.outTemp.avg > 0.0 degree C and the Sum of day.outTemp.avg
           is more than 200 get the Datetime.

        Parameters:
          timespan: An instance of weeutil.weeutil.TimeSpan. This will
                    hold the start and stop times of the domain of
                    valid times.

          db_lookup: This is a function that, given a data binding
                     as its only parameter, will return a database manager
                     object.

        Returns:
          GreenLaTe:   Growing greenLandDay, Numeric value only, not a ValueTuple.
          Green_day:   Get the datetime for the Days to date this year where
                        greenLaTe > 200 as datetime.
          coolTemp:    Kaeltesumme day.outTemp.avg < 0 Nov bis Mar
          warmTemp:    Waermesumme day.outTemp.avg > 20 jun aug
        """

        t1 = time.time()

        # Get year for today
        today = datetime.date.today()
        ano = today.year
        jan_ano = datetime.date(ano, 1, 1)
        feb_ano = datetime.date(ano, 2, 1)
        mae_ano = datetime.date(ano, 3, 1)
        maee_ano = datetime.date(ano, 3, 31)
        nov_ano = datetime.date(ano-1, 11, 1)
        maie_ano = datetime.date(ano, 5, 31)
        auge_ano = datetime.date(ano, 8, 31)
        jan_ano_ts = time.mktime(jan_ano.timetuple())
        feb_ano_ts = time.mktime(feb_ano.timetuple())
        jane_ano_ts = feb_ano_ts - 86400
        mae_ano_ts = time.mktime(mae_ano.timetuple())
        febe_ano_ts = mae_ano_ts - 86400
        maee_ano_ts = time.mktime(maee_ano.timetuple())
        nov_ano_ts = time.mktime(nov_ano.timetuple())
        maie_ano_ts = time.mktime(maie_ano.timetuple())
        jun_ano_ts = maie_ano_ts + 86400
        auge_ano_ts = time.mktime(auge_ano.timetuple())

        _tavg = []
        _cooS = []
        _warmS = []
        tavgS = 0.0
        tavg0 = 0.0
        warmS = 0.0
        cooSG = 0.0
        _glt_ts = None

        try:
            for tspan in weeutil.weeutil.genDaySpans(jan_ano_ts, jane_ano_ts):
                _row = db_lookup().getSql("SELECT dateTime,wsum,sumtime FROM archive_day_outTemp WHERE dateTime>? AND dateTime<=?", (tspan.start, tspan.stop))
                if _row is None or _row[1] is None or _row[2] is None:
                    continue

                glt_ts = _row[0]             # _row['dateTime']
                aa1 = _row[1]                # _row['max'] neu wsum
                aa2 = _row[2]                # _row['min']     sumtime for day.outTemp.avg
                #_tavg.append((aa1 + aa2) / 2)
                _tavg.append(aa1 / aa2)
                #tavg0 = (aa1 + aa2) / 2
                tavg0 = aa1 / aa2
                if tavg0 > 0.0:
                    tavg0 = tavg0 * 0.5
                    tavgS = tavgS + tavg0
                    if tavgS >= 200.0 and _glt_ts is None:
                        _glt_ts = glt_ts


            for tspan in weeutil.weeutil.genDaySpans(feb_ano_ts, febe_ano_ts):
                _row = db_lookup().getSql("SELECT dateTime,wsum,sumtime FROM archive_day_outTemp WHERE dateTime>? AND dateTime<=?", (tspan.start, tspan.stop))
                if _row is None or _row[1] is None or _row[2] is None:
                    continue

                glt_ts = _row[0]             # _row['dateTime']
                aa1 = _row[1]                # _row['max']
                aa2 = _row[2]                # _row['min']
                #_tavg.append((aa1 + aa2) / 2)
                _tavg.append(aa1 / aa2)
                #tavg0 = (aa1 + aa2) / 2
                tavg0 = aa1 / aa2
                if tavg0 > 0.0:
                    tavg0 = tavg0 * 0.75
                    tavgS = tavgS + tavg0
                    if tavgS >= 200.0 and _glt_ts is None:
                        _glt_ts = glt_ts


            for tspan in weeutil.weeutil.genDaySpans(mae_ano_ts, maie_ano_ts):
                _row = db_lookup().getSql("SELECT dateTime,wsum,sumtime FROM archive_day_outTemp WHERE dateTime>? AND dateTime<=?", (tspan.start, tspan.stop))
                if _row is None or _row[1] is None or _row[2] is None:
                    continue

                glt_ts = _row[0]             # _row['dateTime']
                aa1 = _row[1]                # _row['max']
                aa2 = _row[2]                # _row['min']
                #_tavg.append((aa1 + aa2) / 2)
                _tavg.append(aa1 / aa2)
                #tavg0 = (aa1 + aa2) / 2
                tavg0 = aa1 / aa2
                if tavg0 > 0.0:
                    tavgS = tavgS + tavg0
                    if tavgS >= 200.0 and _glt_ts is None:
                        _glt_ts = glt_ts

            for tspan in weeutil.weeutil.genDaySpans(nov_ano_ts,  maee_ano_ts):
                _row = db_lookup().getSql("SELECT dateTime,wsum,sumtime FROM archive_day_outTemp WHERE dateTime>? AND dateTime<=?", (tspan.start, tspan.stop))
                if _row is None or _row[1] is None or _row[2] is None:
                    continue

                aa1 = _row[1]                # _row['max']
                aa2 = _row[2]                # _row['min']
                #_cooS.append((aa1 + aa2) / 2)
                _cooS.append(aa1 / aa2)

            cooSG = sum(i for i in _cooS if i < 0)
            cooSG = abs(cooSG)

            for tspan in weeutil.weeutil.genDaySpans(jun_ano_ts, auge_ano_ts):
                _row = db_lookup().getSql("SELECT dateTime,wsum,sumtime FROM archive_day_outTemp WHERE dateTime>? AND dateTime<=?", (tspan.start, tspan.stop))
                if _row is None or _row[1] is None or _row[2] is None:
                    continue

                aa1 = _row[1]                # _row['max']
                aa2 = _row[2]                # _row['min']

                _warmS.append(aa1 / aa2)

            warmS = sum(i for i in _warmS if i > 20.0)


        except weedb.DatabaseError:
            pass

        # Wrap our ts in a ValueHelper
        _glt_vt = (_glt_ts, 'unix_epoch', 'group_time')
        glt_vh = ValueHelper(_glt_vt, formatter=self.generator.formatter, converter=self.generator.converter)

        search_list_extension = {'greenLaTe': tavgS,
                                 'green_day': glt_vh,
                                 'coolTemp': cooSG,
                                 'warmTemp': warmS,
                                }

        t2 = time.time()
        logdbg("xGreenDay SLE executed in %0.3f seconds" % (t2-t1))

        return [search_list_extension]
