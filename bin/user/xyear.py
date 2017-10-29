#
#    Copyright (c) 2009-2015 Tom Keffer <tkeffer@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#
"""Extended stats based on the xsearch example

This search list extension offers extra tags:

  'Easter':    this year or next year.

  'day00':  hollyday. 

Jahr -1 = Vorjahr = year1, das Jahr vor dem Vorjahr = year2
"""
import datetime
import time
import os
import sys
import syslog

from weewx.cheetahgenerator import SearchList
from weewx.tags import TimespanBinder
from weeutil.weeutil import TimeSpan
from datetime import date
from datetime import timedelta
from weewx.units import ValueHelper, getStandardUnitType, ValueTuple

class xMyYear(SearchList):
    
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

        anoy = ano - 1

        year1_start = datetime.date(anoy, 1, 1)
        year1_end = datetime.date(anoy, 12, 31)

        year1_start_ts = time.mktime(year1_start.timetuple())
        year1_end_ts = time.mktime(year1_end.timetuple())        

        year1_stats = TimespanBinder(TimeSpan(year1_start_ts, year1_end_ts),
                                     db_lookup,
                                     context='year1',
                                     formatter=self.generator.formatter,
                                     converter=self.generator.converter,
                                     skin_dict=self.generator.skin_dict)


        anoyy = ano - 2

        year2_start = datetime.date(anoyy, 1, 1)
        year2_end = datetime.date(anoyy, 12, 31)

        year2_start_ts = time.mktime(year2_start.timetuple())
        year2_end_ts = time.mktime(year2_end.timetuple())        

        year2_stats = TimespanBinder(TimeSpan(year2_start_ts, year2_end_ts),
                                     db_lookup,
                                     context='year2',
                                     formatter=self.generator.formatter,
                                     converter=self.generator.converter,
                                     skin_dict=self.generator.skin_dict)

        return [{'year1' : year1_stats,
                 'year2' : year2_stats}]

class xMyEaster(SearchList):
        
    def __init__(self, generator):
        SearchList.__init__(self, generator)

    def get_extension_list(self, timespan, db_lookup):
        """ Returns various tags.
          Returns:
          Easter:         A ValueHelper containing the date of the next Easter
                          Sunday. The time represented is midnight at the start
                          of Easter Sunday.
          day00:          Feiertag Deutschland M-V 
        """
        #
        # Easter. Calculate date for Easter Sunday this year
        #
        def calcEaster(years):

            g = years % 19
            e = 0
            century = years / 100
            h = (century - century / 4 - (8 * century + 13) / 25 + 19 * g + 15) % 30
            i = h - (h / 28) * (1 - (h / 28) * (29 / (h + 1)) * ((21 - g) / 11))
            j = (years + years / 4 + i + 2 - century + century / 4) % 7
            p = i - j + e
            _days = 1 + (p + 27 + (p + 6) / 40) % 31
            _months = 3 + (p + 26) / 30
            Easter_dt = datetime.datetime(year=years, month=_months, day=_days)
            Easter_ts = time.mktime(Easter_dt.timetuple())
            return Easter_ts

        def calcEasterD(years):

            g = years % 19
            e = 0
            century = years / 100
            h = (century - century / 4 - (8 * century + 13) / 25 + 19 * g + 15) % 30
            i = h - (h / 28) * (1 - (h / 28) * (29 / (h + 1)) * ((21 - g) / 11))
            j = (years + years / 4 + i + 2 - century + century / 4) % 7
            p = i - j + e
            _days = 1 + (p + 27 + (p + 6) / 40) % 31
            _months = 3 + (p + 26) / 30
            Easter_dt = datetime.datetime(year=years, month=_months, day=_days)
            return Easter_dt


        _years = date.today().year
        Easter_ts = calcEaster(_years)
        Easter_dt = calcEasterD(_years)

        today = datetime.date.today()

        if today == datetime.date(_years, 1, 1):
            # feste Feiertage:
            #day01 = datetime.date(self.year, 1, 1)
            #self.holiday_list.append([newyear, u'Neujahr'])
            day00 = u'Neujahr'
        elif today == datetime.date(_years, 5, 1):
            day00 = u'1. Mai'
        elif today == datetime.date(_years, 10, 3):
            day00 = u'Tag der deutschen Einheit'
        elif today == datetime.date(_years, 10, 31):
            day00 = u'Reformationstag'
        elif today == datetime.date(_years, 11, 11):
            day00 = u'Heute um 11:11 Uhr'
        elif today == datetime.date(_years, 12, 24):
            day00 = u'Weihnachtstag'
        elif today == datetime.date(_years, 12, 25):
            day00 = u'Erster Weihnachtsfeiertag'
        elif today == datetime.date(_years, 12, 26):
            day00 = u'Zweiter Weihnachtsfeiertag'
        elif today == datetime.date(_years, 12, 31):
            day00 = u'Silvester'
            #bewegliche Feiertage:
        elif today == (Easter_dt - datetime.timedelta(days=52)):
            day00 =  u'Weiberfastnacht'
        elif today == (Easter_dt - datetime.timedelta(days=48)):
            day00 =  u'Rosenmontag'
        elif today == (Easter_dt - datetime.timedelta(days=47)):
            day00 =  u'Fastnachts'
        elif today == (Easter_dt - datetime.timedelta(days=46)):
            day00 =  u'Aschermittwoch'
        elif today == (Easter_dt - datetime.timedelta(days=2)):
            day00 =  u'Karfreitag'
        elif today == Easter_dt:
            day00 = u'Ostersonntag'
        elif today == (Easter_dt + datetime.timedelta(days=1)):
            day00 = u'Ostermontag'
        elif today == (Easter_dt + datetime.timedelta(days=39)):
            day00 = u'Christi Himmelfahrt'
        elif today == (Easter_dt + datetime.timedelta(days=49)):
            day00 = u'Pfingstsonntag'
        elif today == (Easter_dt + datetime.timedelta(days=50)):
            day00 = u'Pfingstmontag'
        else:
            day00 = u' '

        # Check to see if we have past this calculated date
        # If so we want next years date so increment year and recalculate
        if date.fromtimestamp(Easter_ts) < date.today():
            Easter_ts = calcEaster(_years + 1)
        Easter_vt = ValueTuple(Easter_ts, 'unix_epoch', 'group_time')
        Easter_vh = ValueHelper(Easter_vt,
                                formatter=self.generator.formatter,
                                converter=self.generator.converter)

        # Create a small dictionary with the tag names (keys) we want to use
        search_list_extension = {'Easter' : Easter_vh,
                                 'day00': day00,
                                }

        return [search_list_extension]

