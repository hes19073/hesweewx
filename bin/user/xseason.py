#
#    Copyright (c) 2009-2015 Tom Keffer <tkeffer@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#
"""Extended stats based on the xsearch example

   This search list extension offers extra tags:

   'alltime':    All time statistics.

You can then use tags such as $alltime.outTemp.max for the all-time max
temperature, or $seven_day.rain.sum for the total rainfall in the last seven
days, or $thirty_day.wind.max for maximum wind speed in the past thirty days.

Fruehling = spring, Sommer = summer, Herbst = autumm, Winter = winter
"""
import datetime
import time
import os
import sys
import syslog

from weewx.cheetahgenerator import SearchList
from weewx.tags import TimespanBinder
from weeutil.weeutil import TimeSpan

class MyXSeason(SearchList):
    
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
        anop = ano

        if today < datetime.date(ano, 3, 21):
            anop = ano - 1
          
        spring_start = datetime.date(anop, 3, 21)
        spring_end = datetime.date(anop, 6, 20)
        spring_start_ts = time.mktime(spring_start.timetuple())
        spring_end_ts = time.mktime(spring_end.timetuple())

        spring = TimespanBinder(TimeSpan(spring_start_ts, spring_end_ts),
                                          db_lookup,
                                          context='spring',
                                          formatter=self.generator.formatter,
                                          converter=self.generator.converter,
                                          skin_dict=self.generator.skin_dict)



        anov = ano

        if today < datetime.date(ano, 6, 21):
            anov = ano - 1

        summer_start = datetime.date(anov, 6, 21)
        summer_end = datetime.date(anov, 9, 20)
        summer_start_ts = time.mktime(summer_start.timetuple())
        summer_end_ts = time.mktime(summer_end.timetuple())

        summer = TimespanBinder(TimeSpan(summer_start_ts, summer_end_ts),
                                          db_lookup,
                                          context='summer',
                                          formatter=self.generator.formatter,
                                          converter=self.generator.converter,
                                          skin_dict=self.generator.skin_dict)

        anoo = ano

        if today < datetime.date(ano, 9, 21):
            anoo = ano - 1

        autumm_start = datetime.date(anoo, 9, 21)
        autumm_end = datetime.date(anoo, 12, 20)
        autumm_start_ts = time.mktime(autumm_start.timetuple())
        autumm_end_ts = time.mktime(autumm_end.timetuple())

        autumm = TimespanBinder(TimeSpan(autumm_start_ts, autumm_end_ts),
                                          db_lookup,
                                          context='autumm',
                                          formatter=self.generator.formatter,
                                          converter=self.generator.converter,
                                          skin_dict=self.generator.skin_dict)

        anoi = ano

        if today < datetime.date(ano, 12, 21):
            anoi = ano - 1

        winter_start = datetime.date(anoi, 12, 21)
        winter_end = datetime.date(anoi+1, 3, 20)
        winter_start_ts = time.mktime(winter_start.timetuple())
        winter_end_ts = time.mktime(winter_end.timetuple())        

        winter = TimespanBinder(TimeSpan(winter_start_ts, winter_end_ts),
                                          db_lookup,
                                          context='winter',
                                          formatter=self.generator.formatter,
                                          converter=self.generator.converter,
                                          skin_dict=self.generator.skin_dict)

        return [{'winter' : winter,
                 'spring' : spring,
                 'summer' : summer,
                 'autumm' : autumm}]
