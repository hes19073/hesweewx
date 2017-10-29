# -*- coding: utf-8 -*-
# $Id: dwdmon.py 1651 2017-04-17 12:10:37Z hes $
# Copyright 2017 Hartmut Schweidler

import calendar
import configobj
import hashlib
import os, errno
import re
import socket
import string
import subprocess
import syslog
import threading
import datetime
import time
import xml.etree.ElementTree as etree
import xml.etree.cElementTree

import weewx
import weedb
import weewx.manager
import weeutil.weeutil
from weewx.engine import StdService
from weewx.cheetahgenerator import SearchList


VERSION = "0.1.3"

def logmsg(level, msg):
    syslog.syslog(level, 'DWD-Pollen-forecast: %s: %s' % 
                  (threading.currentThread().getName(), msg))

def logdbg(msg):
    logmsg(syslog.LOG_DEBUG, msg)

def loginf(msg):
    logmsg(syslog.LOG_INFO, msg)

def logerr(msg):
    logmsg(syslog.LOG_ERR, msg)

def mkdir_p(path):
    """equivalent to 'mkdir -p'"""
    try:
        os.makedirs(path)
    except OSError, e:
        if e.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


schema = [('method',     'VARCHAR(10) NOT NULL'),
          ('dateTime',   'INTEGER NOT NULL'),
          ('usUnits',    'INTEGER NOT NULL'),  # weewx.US
          ('issued_ts',  'INTEGER NOT NULL'),  # epoch
          ('event_ts',   'INTEGER NOT NULL'),  # epoch
          ('duration',   'INTEGER'),           # seconds
          ('region',     'VARCHAR(64)'),
          ('up_date',    'VARCHAR(25)'),
          ('next_date',  'VARCHAR(25)'),
          ('hasel_h',    'VARCHAR(4)'),
          ('erle_h',     'VARCHAR(4)'),
          ('esche_h',    'VARCHAR(4)'),
          ('birke_h',    'VARCHAR(4)'),
          ('graeser_h',  'VARCHAR(4)'),
          ('roggen_h',   'VARCHAR(4)'),
          ('beifuss_h',  'VARCHAR(4)'),
          ('ambrosia_h', 'VARCHAR(4)'),
          ('hasel_m',    'VARCHAR(4)'),
          ('erle_m',     'VARCHAR(4)'),
          ('esche_m',    'VARCHAR(4)'),
          ('birke_m',    'VARCHAR(4)'),
          ('graeser_m',  'VARCHAR(4)'),
          ('roggen_m',   'VARCHAR(4)'),
          ('beifuss_m',  'VARCHAR(4)'),
          ('ambrosia_m', 'VARCHAR(4)'),
          ('hasel_n',    'VARCHAR(4)'),
          ('erle_n',     'VARCHAR(4)'),
          ('esche_n',    'VARCHAR(4)'),
          ('birke_n',    'VARCHAR(4)'),
          ('graeser_n',  'VARCHAR(4)'),
          ('roggen_n',   'VARCHAR(4)'),
          ('beifuss_n',  'VARCHAR(4)'),
          ('ambrosia_n', 'VARCHAR(4)'),
          ]


DEFAULT_BINDING_DICT = {
    'database': 'dwd_sqlite',
    'manager': 'weewx.manager.Manager',
    'table_name': 'archive',
    'schema': 'user.dwdmon.schema'}

class ForecastThread(threading.Thread):
    def __init__(self, target, *args):
        self._target = target
        self._args = args
        threading.Thread.__init__(self)

    def run(self):
        self._target(*self._args)

class Forecast(StdService):
    """Base class for forecasting services."""

    def __init__(self, engine, config_dict, fid,
                 interval=1800, max_age=604800):
        super(Forecast, self).__init__(engine, config_dict)
        loginf('%s: DWDPollen version %s' % (fid, VERSION))
        self.method_id = fid
        
        # single database for all different types of forecasts
        d = config_dict.get('DWD', {})
        self.binding = d.get('data_binding', 'dwd_binding')

        # these options can be different for each forecast method

        # how often to do the forecast
        self.interval = self._get_opt(d, fid, 'interval', interval)
        self.interval = int(self.interval)
        # how long to keep forecast records
        self.max_age = self._get_opt(d, fid, 'max_age', max_age)
        self.max_age = self.toint('max_age', self.max_age, None, fid)
        # option to vacuum the sqlite database
        self.vacuum = self._get_opt(d, fid, 'vacuum', False)
        self.vacuum = weeutil.weeutil.tobool(self.vacuum)
        # how often to retry database failures
        self.db_max_tries = self._get_opt(d, fid, 'database_max_tries', 1)
        self.db_max_tries = int(self.db_max_tries)
        # how long to wait between retries, in seconds
        self.db_retry_wait = self._get_opt(d, fid, 'database_retry_wait', 10)
        self.db_retry_wait = int(self.db_retry_wait)
        # use single_thread for debugging
        self.single_thread = self._get_opt(d, fid, 'single_thread', False)
        self.single_thread = weeutil.weeutil.tobool(self.single_thread)
        # option to save raw forecast to disk
        self.save_raw = self._get_opt(d, fid, 'save_raw', False)
        self.save_raw = weeutil.weeutil.tobool(self.save_raw)
        # option to save failed foreast to disk for diagnosis
        self.save_failed = self._get_opt(d, fid, 'save_failed', False)
        self.save_failed = weeutil.weeutil.tobool(self.save_failed)
        # where to save the raw forecasts
        self.diag_dir = self._get_opt(d, fid, 'diagnostic_dir', '/var/tmp/fc')

        self.last_ts = 0
        self.updating = False
        self.last_raw_digest = None
        self.last_fail_digest = None

        # setup database
        dbm_dict = weewx.manager.get_manager_dict(
            config_dict['DataBindings'], config_dict['Databases'], self.binding,
            default_binding_dict=DEFAULT_BINDING_DICT)
        with weewx.manager.open_manager(dbm_dict, initialize=True) as dbm:
            # ensure schema on disk matches schema in memory
            dbcol = dbm.connection.columnsOf(dbm.table_name)
            memcol = [x[0] for x in dbm_dict['schema']]
            if dbcol != memcol:
                raise Exception('%s: schema mismatch: %s != %s' %
                                (self.method_id, dbcol, memcol))
            # find out when the last forecast happened
            self.last_ts = Forecast.get_last_forecast_ts(dbm, self.method_id)

    def _bind(self):
        # ensure that the forecast has a chance to update on each new record
        self.bind(weewx.NEW_ARCHIVE_RECORD, self.update_forecast)

    def _get_opt(self, d, fid, label, default_v):
        """get an option from dict, prefer specialized value if one exists"""
        v = d.get(label, default_v)
        dd = d.get(fid, {})
        v = dd.get(label, v)
        return v

    @staticmethod
    def get_loc_from_station(config_dict):
        # FIXME: get this from station object, not the config_dict
        lat = config_dict['Station'].get('latitude', None)
        lon = config_dict['Station'].get('longitude', None)
        if lat is not None and lon is not None:
            return '%s,%s' % (lat, lon)
        return None

    @staticmethod
    def obfuscate(s):
        return 'X' * (len(s) - 4) + s[-4:]

    @staticmethod
    def get_masked_url(url, api_key):
        """look for specified key in the url and mask all but 4 characters"""
        masked = list(url)
        idx = url.find(api_key)
        if idx >= 0:
            for i in range(len(api_key)-4):
                masked[idx+i] = 'X'
        return ''.join(masked)

    @staticmethod
    def toint(label, value, default_value, method):
        """convert to integer but also permit a value of None"""
        if isinstance(value, str) and value.lower() == 'none':
            value = None
        if value is not None:
            try:
                value = int(value)
            except ValueError:
                logerr("%s: bad value '%s' for %s" %
                       (method, value, label))
                value = default_value
        return value

    @staticmethod
    def str2int(n, s, method):
        if s is not None and s != '':
            try:
                return int(s)
            except (ValueError, TypeError), e:
                logerr("%s: conversion error for %s from '%s': %s" %
                       (method, n, s, e))
        return None

    @staticmethod
    def str2float(n, s, method):
        if s is not None and s != '':
            try:
                return float(s)
            except (ValueError, TypeError), e:
                logerr("%s: conversion error for %s from '%s': %s" %
                       (method, n, s, e))
        return None

    @staticmethod
    def save_fc_data(fc, dirname, basename='forecast-data', msgs=None):
        """save raw forecast data to disk, typically for diagnostics"""
        ts = int(time.time())
        tstr = time.strftime('%Y%m%d%H%M', time.localtime(ts))
        mkdir_p(dirname)
        fn = '%s/%s-%s' % (dirname, basename, tstr)
        with open(fn, 'w') as f:
            if msgs is not None:
                for m in msgs:
                    f.write("%s\n" % m)
            f.write(fc)

    def save_raw_forecast(self, fc, basename='raw', msgs=None):
        m = hashlib.md5()
        m.update(fc)
        digest = m.hexdigest()
        if self.last_raw_digest == digest:
            return
        Forecast.save_fc_data(fc, self.diag_dir, basename=basename, msgs=msgs)
        self.last_raw_digest = digest

    def save_failed_forecast(self, fc, basename='fail', msgs=None):
        m = hashlib.md5()
        m.update(fc)
        digest = m.hexdigest()
        if self.last_fail_digest == digest:
            return
        Forecast.save_fc_data(fc, self.diag_dir, basename=basename, msgs=msgs)
        self.last_fail_digest = digest

    def update_forecast(self, event):
        if self.single_thread:
            self.do_forecast(event)
        elif self.updating:
            logdbg('%s: update thread already running' % self.method_id)
        elif time.time() - self.interval > self.last_ts:
            t = ForecastThread(self.do_forecast, event)
            t.setName(self.method_id + 'Thread')
            logdbg('%s: starting thread' % self.method_id)
            t.start()
        else:
            logdbg('%s: not yet time to do the forecast' % self.method_id)

    def do_forecast(self, event):
        self.updating = True
        try:
            records = self.get_forecast(event)
            if records is None:
                return
            dbm_dict = weewx.manager.get_manager_dict(
                self.config_dict['DataBindings'],
                self.config_dict['Databases'],
                self.binding,
                default_binding_dict=DEFAULT_BINDING_DICT)
            with weewx.manager.open_manager(dbm_dict) as dbm:
                Forecast.save_forecast(dbm, records, self.method_id,
                                       self.db_max_tries, self.db_retry_wait)
                self.last_ts = int(time.time())
                if self.max_age is not None:
                    Forecast.prune_forecasts(dbm, self.method_id,
                                             self.last_ts - self.max_age,
                                             self.db_max_tries,
                                             self.db_retry_wait)
                if self.vacuum:
                    Forecast.vacuum_database(dbm, self.method_id)
        except Exception, e:
            logerr('%s: forecast failure: %s' % (self.method_id, e))
            weeutil.weeutil.log_traceback()
        finally:
            logdbg('%s: terminating thread' % self.method_id)
            self.updating = False

    def get_forecast(self, event):
        """get the forecast, return an array of forecast records."""
        return None

    @staticmethod
    def get_last_forecast_ts(dbm, method_id):
        sql = "SELECT dateTime,issued_ts FROM %s WHERE method = '%s' AND dateTime = (SELECT MAX(dateTime) FROM %s WHERE method = '%s') LIMIT 1" % (dbm.table_name, method_id, dbm.table_name, method_id)
#        sql = "select max(dateTime),issued_ts from %s where method = '%s'" % (table, method_id)
        r = dbm.getSql(sql)
        if r is None:
            return None
        logdbg('%s: last forecast issued %s, requested %s' % 
               (method_id,
                weeutil.weeutil.timestamp_to_string(r[1]),
                weeutil.weeutil.timestamp_to_string(r[0])))
        return int(r[0])

    @staticmethod
    def save_forecast(dbm, records, method_id, max_tries=3, retry_wait=10):
        for count in range(max_tries):
            try:
                logdbg('%s: saving %d forecast records' %
                       (method_id, len(records)))
                dbm.addRecord(records, log_level=syslog.LOG_DEBUG)
                loginf('%s: saved %d forecast records' %
                       (method_id, len(records)))
                break
            except Exception, e:
                logerr('%s: save failed (attempt %d of %d): %s' %
                       (method_id, (count + 1), max_tries, e))
                logdbg('%s: waiting %d seconds before retry' %
                       (method_id, retry_wait))
                time.sleep(retry_wait)
        else:
            raise Exception('save failed after %d attempts' % max_tries)

    @staticmethod
    def prune_forecasts(dbm, method_id, ts, max_tries=3, retry_wait=10):
        """remove forecasts older than ts from the database"""

        sql = "delete from %s where method = '%s' and dateTime < %d" % (
            dbm.table_name, method_id, ts)
        for count in range(max_tries):
            try:
                logdbg('%s: deleting forecasts prior to %d' % (method_id, ts))
                dbm.getSql(sql)
                loginf('%s: deleted forecasts prior to %d' % (method_id, ts))
                break
            except Exception, e:
                logerr('%s: prune failed (attempt %d of %d): %s' %
                       (method_id, (count + 1), max_tries, e))
                logdbg('%s: waiting %d seconds before retry' %
                       (method_id, retry_wait))
                time.sleep(retry_wait)
        else:
            raise Exception('prune failed after %d attemps' % max_tries)

    @staticmethod
    def vacuum_database(dbm, method_id):
        # vacuum will only work on sqlite databases.  it will compact the
        # database file.  if we do not do this, the file grows even though
        # we prune records from the database.  it should be ok to run this
        # on a mysql database - it will silently fail.
        try:
            logdbg('%s: vacuuming the database' % method_id)
            dbm.getSql('vacuum')
        except Exception, e:
            logdbg('%s: vacuuming failed: %s' % (method_id, e))

    # this method is used only by the unit tests
    @staticmethod
    def get_saved_forecasts(dbm, method_id, since_ts=None):
        """return saved forecasts since the indicated timestamp

        since_ts - timestamp, in seconds.  a value of None will return all.
        """
        sql = "select * from %s where method = '%s'" % (
            dbm.table_name, method_id)
        if since_ts is not None:
            sql += " and dateTime > %d" % since_ts
        records = []
        for r in dbm.genSql(sql):
            records.append(r)
        return records


# -----------------------------------------------------------------------------
# DWD POllen Forecaster
# -----------------------------------------------------------------------------
        
Z_KEY = 'Pollen'
            
class DWDPollen(Forecast):
    """calculate zambretti code"""
  
    def __init__(self, engine, config_dict):
        super(DWDPollen, self).__init__(engine, config_dict, Z_KEY,
                                                interval=600)
        d = config_dict.get('DWD', {}).get(Z_KEY, {})
        # keep track of the last time for which we issued a forecast
        self.last_event_ts = 0
        loginf('%s: interval=%s max_age=%s ' %
               (Z_KEY, self.interval, self.max_age))
        self._bind()

    def get_forecast(self, event):
        """Generate a zambretti forecast using data from 11:00 (39600 12=43200s).  If the
        current time is before 11:00, use the data from the previous day."""
        now = event.record['dateTime']
        ts = weeutil.weeutil.startOfDay(now) + 40200
        if now < ts:
            ts -= 86400
        if self.last_event_ts == ts:
            logdbg('%s: forecast was already calculated for %s' %
                   (Z_KEY, weeutil.weeutil.timestamp_to_string(ts)))
            return None

        filename = '/home/dwd/filelist/pollen0.xml'

        #self.tz = dateutil.tz.gettz('Europe/Berlin')

        #fxp = etree.parse(filename, etree.XMLParser(encoding='ISO-8859-1'))
        #root = fxp.getroot()

        #date = root.attrib['last_update'].split()[0].split('-')
        #day0 = datetime.datetime(int(date[0]), int(date[1]), int(date[2]), 12, 0, 0, 0, tzinfo=self.tz)

        fxp_parser = etree.XMLParser(encoding='ISO-8859-1')
        root = etree.parse(filename, parser=fxp_parser).getroot()
        #fxp = xml.etree.cElementTree.fromstring(filename)

        self.last_event_ts = ts

        for reg in root.findall('region'):

            if reg.attrib['ID'] == '20':

                record = {}
                record['method'] = Z_KEY
                record['dateTime'] = now
                record['usUnits'] = weewx.METRIC
                record['issued_ts'] = now
                record['event_ts'] = ts
                record['duration'] = 43210
                record['region'] = reg.attrib['name']
                record['up_date'] = root.attrib['last_update']
                record['next_date'] = root.attrib['next_update']
                record['hasel_h'] = reg.find("Hasel/today").text
                record['hasel_m'] = reg.find("Hasel/tomorrow").text
                record['erle_h'] = reg.find("Erle/today").text
                record['erle_m'] = reg.find("Erle/tomorrow").text
                record['esche_h'] = reg.find("Esche/today").text
                record['esche_m'] = reg.find("Esche/tomorrow").text
                record['birke_h'] = reg.find("Birke/today").text
                record['birke_m'] = reg.find("Birke/tomorrow").text
                record['graeser_h'] = reg.find("Graeser/today").text
                record['graeser_m'] = reg.find("Graeser/tomorrow").text
                record['roggen_h'] = reg.find("Roggen/today").text
                record['roggen_m'] = reg.find("Roggen/tomorrow").text
                record['beifuss_h'] = reg.find("Beifuss/today").text
                record['beifuss_m'] = reg.find("Beifuss/tomorrow").text
                record['ambrosia_h'] = reg.find("Ambrosia/today").text
                record['ambrosia_m'] = reg.find("Ambrosia/tomorrow").text

            loginf('%s: generated 1 forecast record' % Z_KEY)
            #return record
        return [record]

#                r['event_ts'] = AerisForecast.str2int(p, 'timestamp')



