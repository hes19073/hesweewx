# coding=utf-8

"""weewx module that records sun altitude and moon altitude.

Put this file in the bin/user directory.

Service Configuration

Add the following to weewx.conf:

[sunmonMonitor]
    data_binding = sunmon_binding

[DataBindings]
    [[sunmon_binding]]
        database = sunmon_sqlite
        manager = weewx.manager.DaySummaryManager
        table_name = archive
        schema = user.sunmon.schema

[Databases]
    [[sunmon_sqlite]]
        database_name = archive/sunmon.sdb
        driver = weedb.sqlite

[Engine]
    [[Services]]
        archive_services = ..., user.sunmon.sunmonMonitor

"""



import os
import platform
import re
import syslog
import time
import math

import weecfg
import weewx
import weewx.uwxutils
import weeutil.weeutil

from weewx.engine import StdService
from weewx.almanac import Almanac


VERSION = "0.2"

if weewx.__version__ < "3":
    raise weewx.UnsupportedFeature("weewx 3 is required, found %s" %
                                   weewx.__version__)
schema = [
    ('dateTime', 'INTEGER NOT NULL PRIMARY KEY'),
    ('usUnits', 'INTEGER NOT NULL'),
    ('interval', 'INTEGER NOT NULL'),
    ('hor_alt','REAL'),
    ('son_alt','REAL'),
    ('sun_alt','REAL'),
    ('mon_alt','REAL'),
    ('mer_alt','REAL'),
    ('ven_alt','REAL'),
    ('mar_alt','REAL'),
    ('jup_alt','REAL'),
    ('sat_alt','REAL'),
    ('ura_alt','REAL'),
    ('nep_alt','REAL'),
    ('plu_alt','REAL'),
    ]

def logmsg(level, msg):
    syslog.syslog(level, 'SunMon_weewx: %s' % msg)

def logdbg(msg):
    logmsg(syslog.LOG_DEBUG, msg)

def loginf(msg):
    logmsg(syslog.LOG_INFO, msg)

def logerr(msg):
    logmsg(syslog.LOG_ERR, msg)


class sunmonMonitor(StdService):
    """Collect Sensor Air information."""

    def __init__(self, engine, config_dict):
        super(sunmonMonitor, self).__init__(engine, config_dict)
        loginf("SunMon-Service version is %s" % VERSION)

        d = config_dict.get('sunmon', {})

        # get the database parameters we need to function
        binding = d.get('data_binding', 'sunmon_binding')
        self.dbm = self.engine.db_binder.get_manager(data_binding=binding,
                                                     initialize=True)

        # be sure schema in database matches the schema we have
        dbcol = self.dbm.connection.columnsOf(self.dbm.table_name)
        dbm_dict = weewx.manager.get_manager_dict(
            config_dict['DataBindings'], config_dict['Databases'], binding)
        memcol = [x[0] for x in dbm_dict['schema']]
        if dbcol != memcol:
            raise Exception('sunmon schema mismatch: %s != %s' % (dbcol, memcol))

        self.last_ts = None

        self.bind(weewx.NEW_ARCHIVE_RECORD, self.new_archive_record)

    def shutDown(self):
        try:
            self.dbm.close()
        except:
            pass

    def new_archive_record(self, event):
        """save data to database then prune old records as needed"""
        now = int(time.time() + 0.5)
        delta = now - event.record['dateTime']
        if delta > event.record['interval'] * 60:
            logdbg("Skipping record: time difference %s too big" % delta)
            return
        if self.last_ts is not None:
            self.save_data(self.get_data(now, self.last_ts))
        self.last_ts = now

    def save_data(self, record):
        """save data to database"""
        self.dbm.addRecord(record)

    def get_data(self, now_ts, last_ts):
        """ read data from almanac """
        try:
            alm = Almanac(time.time(), 53.605963, 11.341407, 53.2)

            son_alt = alm.sun.earth_distance
            sun_alt = alm.sun.alt
            mon_alt = alm.moon.alt
            mer_alt = alm.mercury.alt
            ven_alt = alm.venus.alt
            mar_alt = alm.mars.alt
            jup_alt = alm.jupiter.alt
            sat_alt = alm.saturn.alt
            ura_alt = alm.uranus.alt
            nep_alt = alm.neptune.alt
            plu_alt = alm.pluto.alt

        except:
            sr = None


        record = {}
        record['dateTime'] = now_ts                       # required
        record['usUnits'] = weewx.METRIC                  # required
        record['interval'] = int((now_ts - last_ts) / 60) # required
        record['hor_alt'] = 0.0
        record['son_alt'] = son_alt
        record['sun_alt'] = sun_alt
        record['mon_alt'] = mon_alt
        record['mer_alt'] = mer_alt
        record['ven_alt'] = ven_alt
        record['mar_alt'] = mar_alt
        record['jup_alt'] = jup_alt
        record['sat_alt'] = sat_alt
        record['ura_alt'] = ura_alt
        record['nep_alt'] = nep_alt
        record['plu_alt'] = plu_alt

        return record


