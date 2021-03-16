# coding=utf-8
#
#    Copyright (c) 2009-2015 Tom Keffer <tkeffer@gmail.com>
#    new by 2021 by Hartmut Schweidler
#    See the file LICENSE.txt for your full rights.
#
"""Extended stats based on the xsearch example

   This search list extension offers extra tags:

  'Easter':    this year or next year.

  'day00':  hollyday.

"""
from __future__ import absolute_import

import datetime
import time
import os
import sys

from weewx.cheetahgenerator import SearchList
from weewx.tags import TimespanBinder
from weeutil.weeutil import TimeSpan
from datetime import date, tzinfo
from datetime import timedelta
from weewx.units import ValueHelper, getStandardUnitType, ValueTuple


class xMyEaster(SearchList):
    """calc easter for year"""
    def __init__(self, generator):
        SearchList.__init__(self, generator)

    def get_extension_list(self, timespan, db_lookup):
        """ Returns various tags.
          Returns:
          Easter:         A ValueHelper containing the date of the next Easter
                          Sunday. The time represented is midnight at the start
                          of Easter Sunday.
        """
        #
        # Easter. Calculate date for Easter Sunday this year
        #
        def calc_easter(year):
            """Calculate Easter date.
            Uses a modified version of Butcher's Algorithm.
            Refer New Scientist, 30 March 1961 pp 828-829
            https://books.google.co.uk/books?id=zfzhCoOHurwC&printsec=frontcover&source=gbs_ge_summary_r&cad=0#v=onepage&q&f=false
            """

            a = year % 19
            b = year // 100
            c = year % 100
            d = b // 4
            e = b % 4
            g = (8 * b + 13) // 25
            h = (19 * a + b - d - g + 15) % 30
            i = c // 4
            k = c % 4
            l = (2 * e + 2 * i - h - k + 32) % 7
            m = (a + 11 * h + 19 * l) // 433
            n = (h + l - 7 * m + 90) // 25
            p = (h + l - 7 * m + 33 * n + 19) % 32
            _dt = datetime.datetime(year=year, month=n, day=p)
            _ts = time.mktime(_dt.timetuple())
            return _ts

        _year = date.today().year
        easter_ts = calc_easter(_year)
        # check to see if we have past this calculated date, if so we want next
        # years date so increment year and recalculate
        if date.fromtimestamp(easter_ts) < date.today():
            easter_ts = calc_easter(_year + 1)
        easter_vt = ValueTuple(easter_ts, 'unix_epoch', 'group_time')
        easter_vh = ValueHelper(easter_vt,
                                formatter=self.generator.formatter,
                                converter=self.generator.converter)

        # Create a small dictionary with the tag names (keys) we want to use
        search_list_extension = {'Easter' : easter_vh,
                                }

        return [search_list_extension]

class xMyFeier(SearchList):
    """Holyday for the year"""
    def __init__(self, generator):
        SearchList.__init__(self, generator)

    def get_extension_list(self, timespan, db_lookup):
        """ Returns various tags.
          Returns:
          day00:          Feiertag Deutschland M-V
        """

        def calc_easter_day(year):
            """Calculate Easter date.
            Uses a modified version of Butcher's Algorithm.
            Refer New Scientist, 30 March 1961 pp 828-829
            https://books.google.co.uk/books?id=zfzhCoOHurwC&printsec=frontcover&source=gbs_ge_summary_r&cad=0#v=onepage&q&f=false
            """

            a = year % 19
            b = year // 100
            c = year % 100
            d = b // 4
            e = b % 4
            g = (8 * b + 13) // 25
            h = (19 * a + b - d - g + 15) % 30
            i = c // 4
            k = c % 4
            l = (2 * e + 2 * i - h - k + 32) % 7
            m = (a + 11 * h + 19 * l) // 433
            n = (h + l - 7 * m + 90) // 25
            p = (h + l - 7 * m + 33 * n + 19) % 32
            _dt = datetime.date(year=year, month=n, day=p)

            return _dt


        today = datetime.date.today()
        _years = today.year
        easter_year = calc_easter_day(_years)

        if today == datetime.date(_years, 1, 1):
            # feste Feiertage:
            #day01 = datetime.date(self.year, 1, 1)
            # day00 =  u'Neujahr'
            day00 = u'Neujahr'
        elif today == datetime.date(_years, 2, 14):
            day00 = u'Valentinstag'
        elif today == datetime.date(_years, 5, 1):
            day00 = u'1. Mai'
        elif today == datetime.date(_years, 5, 11):
            day00 = u'Eisheilige Mamertus'
        elif today == datetime.date(_years, 5, 12):
            day00 = u'Eisheilige Pankratius'
        elif today == datetime.date(_years, 5, 13):
            day00 = u'Eisheilige Servatius'
        elif today == datetime.date(_years, 5, 14):
            day00 = u'Eisheilige Bonifatius'
        elif today == datetime.date(_years, 5, 15):
            day00 = u'Eisheilige Sophia'
        elif today == datetime.date(_years, 6, 4):
            day00 = u'Beginn Schafskälte'
        elif today == datetime.date(_years, 6, 27):
            day00 = u'Siebenschläfer'
        elif today == datetime.date(_years, 7, 23):
            day00 = u'Beginn Hundstage'
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
        elif today == (easter_year - datetime.timedelta(days=52)):
            day00 =  u'Weiberfastnacht'
        elif today == (easter_year - datetime.timedelta(days=48)):
            day00 =  u'Rosenmontag'
        elif today == (easter_year - datetime.timedelta(days=47)):
            day00 =  u'Fastnacht'
        elif today == (easter_year - datetime.timedelta(days=46)):
            day00 =  u'Aschermittwoch'
        elif today == (easter_year - datetime.timedelta(days=2)):
            day00 =  u'Karfreitag'
        elif today == easter_year:
            day00 = u'Ostersonntag'
        elif today == (easter_year + datetime.timedelta(days=1)):
            day00 = u'Ostermontag'
        elif today == (easter_year + datetime.timedelta(days=39)):
            day00 = u'Christi Himmelfahrt'
        elif today == (easter_year + datetime.timedelta(days=49)):
            day00 = u'Pfingstsonntag'
        elif today == (easter_year + datetime.timedelta(days=50)):
            day00 = u'Pfingstmontag'
        else:
            day00 = u' '

        # Create a small dictionary with the tag names (keys) we want to use
        search_list_extension = {'day00': day00,
                                }

        return [search_list_extension]

class xSternzeit(SearchList):
    """calc sternzeit for year"""
    def __init__(self, generator):
        SearchList.__init__(self, generator)

    def get_extension_list(self, timespan, db_lookup):

        # now = datetime.utcnow()
        now = datetime.datetime.now()
        year = now.year
        month = now.month
        day = now.day
        utc = now.hour + now.minute / 60 + now.second / 3600
        long = 53.605963

        def JulianDate(year, month, day, utc=0):
            """
            Returns the Julian date, number of days since 1 January 4713 BC 12:00.
            utc is UTC in decimal hours. If utc=0, returns the date at 12:00 UTC.
            """
            if month > 2:
                y = year
                m = month
            else:
                y = year - 1
                m = month + 12

            d = day
            h = utc / 24

            if year <= 1582 and month <= 10 and day <= 4:
                # Julian calendar
                b = 0
            elif year == 1582 and month == 10 and day > 4 and day < 15:
                # Gregorian calendar reform: 10 days (5 to 14 October 1582) were skipped.
                # In 1582 after 4 October follows the 15 October.
                d = 15
                b = -10
            else:
                # Gregorian Calendar
                a = int(y / 100)
                b = 2 - a + int(a / 4)

            jd = int(365.25 * (y + 4716)) + int(30.6001 *(m + 1)) + d + h + b - 1524.5

            return(jd)

        def SiderialTime(year, month, day, utc=0, long=0):
            """
            Returns the siderial time in decimal hours. Longitude (long) is in decimal degrees.
            If long=0, return value is Greenwich Mean Siderial Time (GMST).
            """
            jd = JulianDate(year, month, day)
            t = (jd - 2451545.0) / 36525
            # Greenwich siderial time at 0h UTC (hours)
            st = (24110.54841 + 8640184.812866 * t + 0.093104 * t **2 - 0.0000062 * t **3) / 3600
            # Greenwich siderial time at given UTC
            st = st + 1.00273790935 * utc
            # Local siderial time at given UTC (longitude in degrees)
            st = st + long / 15
            st = st % 24

            return(st)

        jd     = JulianDate(year, month, day)
        jd_utc = JulianDate(year, month, day, utc)
        gmst   = SiderialTime(year, month, day, utc, 0)
        lmst   = SiderialTime(year, month, day, utc, long)


        search_list_extension = {'jd00' : jd,
                                 'jdutc': jd_utc,
                                 'gmst' : gmst,
                                 'lmst' : lmst,
                                 'utc00': utc,
                                }

        return [search_list_extension]

