# -*- coding: utf-8 -*-
# $Id: xgreen.py  2017-11-20 12:10:37 hes $
# Copyright 2017 Hartmut Schweidler
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
# Version: 0.0.5                                    Date: 23 November 2017
#
from __future__ import absolute_import

import logging
import datetime
import time
import os
import pickle
import weewx
import weedb

import weeutil.config
import weeutil.logger
import weeutil.weeutil
import weewx.units
import weewx.tags

from weewx.cheetahgenerator import SearchList
from weewx.tags import TimeBinder, TimespanBinder
from weeutil.weeutil import TimeSpan, genDaySpans
from weewx.units import ValueHelper, ValueTuple
from datetime import date
#from weeutil.log import logdbg, loginf, logerr, logcrt

log = logging.getLogger(__name__)

GREEN_VERSION = '0.0.5'

class xGreenDay(SearchList):

     def __init__(self, generator):
         SearchList.__init__(self, generator)

     def get_extension_list(self, timespan, db_lookup):
         """Returns green_day as dateTime, green_sum, warmTemp and coolTemp.

         Parameters:
           genDaySpans: An instance of weeutil.weeutil.genDaySpans. This will
                        take the start and stop times of the domain of
                        given times.

           db_lookup: This is a function that, given a data binding
                      as its only parameter, will return a database manager
                      object.

         Returns:
           green_sum: Growing green_sum, Numeric value only, not a ValueTuple.
                      if day.outTemp.avg > 0.0 get for
                              Jan day.outTemp.avg * 0.5
                              Feb day.outTemp.avg * 0.75
                              Mae day.outTemp.avg * 1
                              Summe as green_sum
           green_day: Get the datetime for the Day to date this year where
                      green_sum > 200 as datetime.
           coolT_sum: Kaeltesumme day.outTemp.avg less than 0 degree C from Nov year before to Mar this year
           warmT_sum: Waermesumme day.outTemp.avg more than 20 degree C from Jun to Aug of this year
         """

         t1 = time.time()

         # Get year and month for today
         today = datetime.date.today()
         ano = today.year
         anomo = today.month

         jan_ano = datetime.date(ano, 1, 1)
         feb_ano = datetime.date(ano, 2, 1)
         mae_ano = datetime.date(ano, 3, 1)
         maee_ano = datetime.date(ano, 3, 31)
         jun_ano = datetime.date(ano, 6, 1)
         auge_ano = datetime.date(ano, 8, 31)
         nov_ano = datetime.date(ano, 11, 1)
         novA_ano = datetime.date(ano-1, 11, 1)

         # get timetuple of the days per year
         dat_ts = time.mktime(today.timetuple())
         jan_ano_ts = time.mktime(jan_ano.timetuple())
         feb_ano_ts = time.mktime(feb_ano.timetuple())
         jane_ano_ts = feb_ano_ts - 86400
         mae_ano_ts = time.mktime(mae_ano.timetuple())
         febe_ano_ts = mae_ano_ts - 86400
         maee_ano_ts = time.mktime(maee_ano.timetuple())
         jun_ano_ts = time.mktime(jun_ano.timetuple())
         maie_ano_ts = jun_ano_ts - 86400
         auge_ano_ts = time.mktime(auge_ano.timetuple())
         nov_ano_ts = time.mktime(nov_ano.timetuple())
         novA_ano_ts = time.mktime(novA_ano.timetuple())
         tavg_ts = None
         tavgS = 0.0
         warmS = 0.0
         coolS = 0.0

         # call green_sum as sum of day.outTemp.avg more than 0 degree C
         #      green_day as datetime were green_sum more then 200
         if anomo > 5:
             self.filename = '/home/weewx/bin/user/zzgreenDay'
             self.filename1 = '/home/weewx/bin/user/zzgreenSum'
             try:
                 with open(self.filename1) as f1:
                     tavgS = f1.read()
                     tavgS = float(tavgS)
                 with open(self.filename) as f:
                     tavg_ts = f.read()
                     tavg_ts = float(tavg_ts)

             except Exception as e:
                 log.error("greenDay cannot read green: %s", e)

         else:
             tavgS = 0.0
             tavg_ts = None
             try:
                 for tspan in weeutil.weeutil.genDaySpans(jan_ano_ts, jane_ano_ts):
                     _row = db_lookup().getSql("SELECT dateTime,wsum,sumtime FROM archive_day_outTemp WHERE dateTime>? AND dateTime<=?", (tspan.start, tspan.stop))
                     if _row is None or _row[1] is None or _row[2] is None:
                         continue

                     tavg0 = _row[1] / _row[2]
                     if tavg0 > 0.0:
                         tavg0 = tavg0 * 0.5
                         tavgS = tavgS + tavg0
                         if tavgS >= 200.0 and tavg_ts is None:
                             tavg_ts = _row[0]

                 for tspan in weeutil.weeutil.genDaySpans(feb_ano_ts, febe_ano_ts):
                     _row = db_lookup().getSql("SELECT dateTime,wsum,sumtime FROM archive_day_outTemp WHERE dateTime>? AND dateTime<=?", (tspan.start, tspan.stop))
                     if _row is None or _row[1] is None or _row[2] is None:
                         continue

                     tavg0 = _row[1] / _row[2]
                     if tavg0 > 0.0:
                         tavg0 = tavg0 * 0.75
                         tavgS = tavgS + tavg0
                         if tavgS >= 200.0 and tavg_ts is None:
                             tavg_ts = _row[0]

                 for tspan in weeutil.weeutil.genDaySpans(mae_ano_ts, maie_ano_ts):
                     _row = db_lookup().getSql("SELECT dateTime,wsum,sumtime FROM archive_day_outTemp WHERE dateTime>? AND dateTime<=?", (tspan.start, tspan.stop))
                     if _row is None or _row[1] is None or _row[2] is None:
                         continue

                     tavg0 = _row[1] / _row[2]
                     if tavg0 > 0.0:
                         tavgS = tavgS + tavg0
                         if tavgS >= 200.0 and tavg_ts is None:
                            tavg_ts = _row[0]

             except weedb.DatabaseError:
                 pass

             dat_gs = open("/home/weewx/bin/user/zzgreenSum", "w")
             dat_gs.write(str(tavgS))
             dat_gs.close()

             dat_gd = open("/home/weewx/bin/user/zzgreenDay", "w")
             dat_gd.write(str(tavg_ts))
             dat_gd.close()

         # call warmT_sum as sum of day.outTemp.avg if more than 20 degree C
         if 5 < anomo < 9:
             _warmS = []
             try:
                 for tspan in weeutil.weeutil.genDaySpans(jun_ano_ts, auge_ano_ts):
                     _row = db_lookup().getSql("SELECT dateTime,wsum,sumtime FROM archive_day_outTemp WHERE dateTime>? AND dateTime<=?", (tspan.start, tspan.stop))
                     if _row is None or _row[1] is None or _row[2] is None:
                         continue

                     _warmS.append(_row[1] / _row[2])

                 warmS = sum(i for i in _warmS if i > 20.0)

             except weedb.DatabaseError:
                 pass

             dat_ws = open("/home/weewx/bin/user/zzwarmSum", "w")
             dat_ws.write(str(warmS))
             dat_ws.close()

         else:
             self.filename = '/home/weewx/bin/user/zzwarmSum'
             try:
                 with open(self.filename) as f:
                     warmS = f.read()
                     warmS = float(warmS)
             except Exception as e:
                 log.error("warmSum cannot read zzwarmSum: %s", e)

         # call coolT_sum as sum of day.outTemp.avg less than 0 degree C
         #if maee_ano_ts < dat_ts < nov_ano_ts:
         if 3 < anomo < 11:
             self.filename = '/home/weewx/bin/user/zzcoolSum'
             try:
                 with open(self.filename) as f:
                     coolS = f.read()
                     coolS = float(coolS)
             except Exception as e:
                 log.error("coolSum cannot read zzcoolSum: %s", e)

         else:
             if anomo > 10:
                 coolsta = nov_ano_ts
                 coolend = dat_ts
             else:
                 coolsta = novA_ano_ts
                 coolend = maee_ano_ts

             _cooS = []
             try:
                 for tspan in weeutil.weeutil.genDaySpans(coolsta, coolend):
                     _row = db_lookup().getSql("SELECT dateTime,wsum,sumtime FROM archive_day_outTemp WHERE dateTime>? AND dateTime<=?", (tspan.start, tspan.stop))
                     if _row is None or _row[1] is None or _row[2] is None:
                         continue

                     _cooS.append(_row[1] / _row[2])

                 coolS = sum(i for i in _cooS if i < 0.0)
                 coolS = abs(coolS)

             except weedb.DatabaseError:
                 pass

             dat_cs = open("/home/weewx/bin/user/zzcoolSum", "w")
             dat_cs.write(str(coolS))
             dat_cs.close()


         # Wrap our ts in a ValueHelper
         tavg_vt = (tavg_ts, 'unix_epoch', 'group_time')
         tavg_vh = ValueHelper(tavg_vt, formatter=self.generator.formatter, converter=self.generator.converter)

         search_list_extension = {'green_sum': tavgS,
                                  'green_day': tavg_vh,
                                  'coolT_sum': coolS,
                                  'warmT_sum': warmS,
                                 }

         t2 = time.time()
         log.debug("xGreenDay SLE executed in %0.3f seconds", t2 - t1)
         #log.info("xGreenDay SLE executed in %0.3f seconds", t2 - t1)

         return [search_list_extension]

