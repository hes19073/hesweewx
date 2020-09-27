# coding=utf-8

"""weewx module that records ppm.

Put this file in the bin/user directory.

Service Configuration

Add the following to weewx.conf:

[AQIMonitor]
    data_binding = AerisAqi_binding

[DataBindings]
    [[AerisAqi_binding]]
        database = aerisaqi_sqlite
        manager = weewx.manager.DaySummaryManager
        table_name = archive
        schema = schemas.aerisaqi.schema

[Databases]
    [[aerisaqi_sqlite]]
        database_name = archive/weewxAerisAqi.sdb
        driver = weedb.sqlite

[Engine]
    [[Services]]
        archive_services = ..., user.aqiIndex.AerisAqiMonitor

"""

from __future__ import absolute_import
from __future__ import print_function

import datetime
import logging
import time
import json
import os

import weewx
import weecfg
import weeutil.weeutil
import weeutil.config
from weeutil.weeutil import to_int
from weewx.engine import StdService

log = logging.getLogger(__name__)

VERSION = "0.2"

if weewx.__version__ < "3":
    raise weewx.UnsupportedFeature("weewx 3 is required, found %s" %
                                   weewx.__version__)
"""schema = [
    ('dateTime', 'INTEGER NOT NULL PRIMARY KEY'),
    ('usUnits', 'INTEGER NOT NULL'),
    ('interval', 'INTEGER NOT NULL'),
    ('o3','REAL'),
    ('co','REAL'),
    ('no2', 'REAL'),
    ('so2', 'REAL'),
    ('pm25', 'REAL'),
    ('pm10', 'REAL'),
    ('aqi', 'INTEGER'),
    ('aqitime', 'INTEGER'),
    ('aqicategory', 'VARCHAR(12)'),
    ('aqicolor', 'VARCHAR(12)'),
    ('aqimethod', 'VARCHAR(12)'),
    ('aqidominats', 'VARCHAR(12)'),
    ]"""

class AerisAqiMonitor(StdService):
    """Collect Sensor Air information."""

    def __init__(self, engine, config_dict):
        super(AerisAqiMonitor, self).__init__(engine, config_dict)
        log.info("AQI-Service version is %s", VERSION)

        d = config_dict.get('AerisAqiMonitor', {})
        # get Aeris AQI
        #aqiIndex_file = "/home/weewx/archive/aeris_aqi.json"
        #aqiIndex_json_url = "/home/weewx/archive/aerisIndex.json"
        #aeris_id_key = self.generator.skin_dict['Extras']['aeris_id_key']
        #aeris_secret_key = self.generator.skin_dict['Extras']['aeris_secret_key']
        #latitude = self.generator.config_dict['Station']['latitude']
        #longitude = self.generator.config_dict['Station']['longitude']
        #aqiIndex_stale_timer = self.generator.skin_dict['Extras']['aqiIndex_stale']
        #aqiIndex_url = "https://api.aerisapi.com/airquality/%s,%s?client_id=%s&client_secret=%s" % (latitude, longitude, aeris_id_key, aeris_secret_key)

        # get the database parameters we need to function
        binding = d.get('data_binding', 'aerisaqi_binding')
        self.dbm = self.engine.db_binder.get_manager(data_binding=binding,
                                                     initialize=True)

        # be sure schema in database matches the schema we have
        dbcol = self.dbm.connection.columnsOf(self.dbm.table_name)
        dbm_dict = weewx.manager.get_manager_dict(
            config_dict['DataBindings'], config_dict['Databases'], binding)
        memcol = [x[0] for x in dbm_dict['schema']]
        if dbcol != memcol:
            raise Exception('AerisAQI schema mismatch: %s != %s' % (dbcol, memcol))

        # provide info about the system on which we are running

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
            log.debug("Skipping record: time difference %s too big", delta)
            return
        if self.last_ts is not None:
            self.save_data(self.get_data(now, self.last_ts))
        self.last_ts = now

    def save_data(self, record):
        """save data to database"""
        self.dbm.addRecord(record)

    def get_data(self, now_ts, last_ts):
        record = {}
        record['dateTime'] = now_ts
        record['usUnits'] = weewx.METRIC
        record['interval'] = int((now_ts - last_ts) / 60)

        aqiIndex_file = "/home/weewx/archive/aeris_aqi.json"

        try:

            with open(aqiIndex_file, encoding="utf8") as read_file:
                data = json.loads(read_file.read())

            sxtime = data['response'][0]['periods'][0]['timestamp']
            sxaqi = data['response'][0]['periods'][0]['aqi']
            sxcat = data['response'][0]['periods'][0]['category']
            sxcol = data['response'][0]['periods'][0]['color']
            sxmet = data['response'][0]['periods'][0]['method']
            sxdom = data['response'][0]['periods'][0]['dominant']
            sxo3 = data['response'][0]['periods'][0]['pollutants'][0]['valueUGM3']
            sxpm25 = data['response'][0]['periods'][0]['pollutants'][1]['valueUGM3']
            sxpm10 = data['response'][0]['periods'][0]['pollutants'][2]['valueUGM3']
            sxco = data['response'][0]['periods'][0]['pollutants'][3]['valueUGM3']
            sxno2 = data['response'][0]['periods'][0]['pollutants'][4]['valueUGM3']
            sxso2 = data['response'][0]['periods'][0]['pollutants'][5]['valueUGM3']

            read_file.close()

        except serial.SerialException as e:
            log.info("critical", e)

        record['o3'] = sxo3
        record['co'] = sxco
        record['no2'] = sxno2
        record['so2'] = sxso2
        record['pm25'] = sxpm25
        record['pm10'] = sxpm10
        record['aqi'] = sxaqi
        #record['aqitime'] = sxtime
        #record['aqicategory'] = sxcat
        #record['aqicolor'] = sxcol
        #record['aqimethod'] = sxmet
        #record['aqidominats'] = sxdom

        return record

