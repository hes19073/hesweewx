#!/usr/bin/env python
# coding=utf-8
# datei jahre Monate Tag und Stunden mit Minuten 
# Laufzeit der Datenbank bei weewx     xxyear.py
# einsatz in weewx.conf als Erweiterung von cheetcheat unter
#                user.xxyear.xyear
# Wert 12 Jahre, 2 Monate, 13 Tage, 10 Stunden und 34 Minuten 
# ist der String zur Anzeige

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
from calendar import monthrange


class xxyear(SearchList):

    def __init__(self, generator):
        SearchList.__init__(self, generator)

    def get_extension_list(self, timespan, db_lookup):

        # get a manager
        db_manager = db_lookup()
        # get our first good timestamp
        _start_ts = db_manager.firstGoodStamp()
        _start_dt = datetime.datetime.fromtimestamp(_start_ts)

        y_start = _start_dt.year
        m_start = _start_dt.month
        d_start = _start_dt.day
        H_start = _start_dt.hour
        M_start = _start_dt.minute

        endEnd = datetime.datetime.now()

        y_end = endEnd.year
        m_end = endEnd.month
        d_end = endEnd.day
        H_end = endEnd.hour
        M_end = endEnd.minute

        M_start += H_start * 60
        M_end += H_end * 60

        con_M = M_end - M_start
        if M_start > M_end:
            con_M += 1440
            d_end -= 1

        con_H = con_M // 60
        con_M = con_M % 60
        if d_start > d_end:
            con_DD = monthrange(y_start,m_start)[1] - d_start
            con_DD += d_end
        else:
            con_DD = (d_end - d_start)

        con_MM = 0
        if d_start > d_end:
            con_MM -= 1
    
        con_YY = y_end - y_start
        if m_start > m_end + con_MM:
            con_YY -= 1
            con_MM += 12 - m_start + m_end
        else:
            con_MM += m_end - m_start

        year00 = "%d Jahre, %d Monate, %d Tage, %d Stunden und %d Minuten" % (con_YY,con_MM,con_DD,con_H,con_M)

        return [{'year00': year00}]


