# coding=utf-8

"""weewx module that records ppm.

Put this file in the bin/user directory.

Service Configuration

Add the following to weewx.conf:

[AerisAqiMonitor]
    data_binding = aerisaqi_binding
    key = ''
    skey = ''
    interval = 3540

[DataBindings]
    [[aerisaqi_binding]]
        database = aerisaqi_sqlite
        manager = weewx.manager.DaySummaryManager
        table_name = archive
        schema = user.forecastAqi.schema

[Databases]
    [[aerisaqi_sqlite]]
        database_name = weewxAerisAqi.sdb
        database_type = SQLite

[Engine]
    [[Services]]
        archive_services = ..., user.forecastAqi.AerisAqiMonitor

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
import weeutil.logger
from weeutil.weeutil import to_int
from weewx.engine import StdService

log = logging.getLogger(__name__)

VERSION = "3.0.2"

if weewx.__version__ < "3":
    raise weewx.UnsupportedFeature("weewx 3 is required, found %s" %
                                   weewx.__version__)

schema = [
    ('dateTime', 'INTEGER NOT NULL PRIMARY KEY'),
    ('usUnits', 'INTEGER NOT NULL'),
    ('interval', 'INTEGER NOT NULL'),
    ('aqi', 'INTEGER'),
    ('o3','REAL'),
    ('co','REAL'),
    ('no2', 'REAL'),
    ('so2', 'REAL'),
    ('pm25', 'REAL'),
    ('pm10', 'REAL'),
    ('aqitime', 'INTEGER'),
    ('aqidominats', 'INTEGER'),
    ]

class AerisAqiMonitor(StdService):
    """Collect Sensor Air information."""

    def __init__(self, engine, config_dict):
        super(AerisAqiMonitor, self).__init__(engine, config_dict)
        log.info("AerisAQIMonitor-Service version is %s", VERSION)


        d = config_dict.get('AerisAqiMonitor', {})
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

        # get Aeris AQI
        self.aeris_id_key = d.get('key', None)
        self.aeris_secret_key = d.get('skey', None)
        #latitude = 53.605963           # d.get('latitude', None)
        #longitude = 11.341407          # d.get('longitude', None)
        #aqiIndex_stale_timer =  3540   #self.skin_dict['Extras']['aqiIndex_stale']
        #aqiIndex_url = "https://api.aerisapi.com/airquality/%s,%s?client_id=%s&client_secret=%s" % (latitude, longitude, aeris_id_key, aeris_secret_key)

        self.last_ts = None
        self.bind(weewx.NEW_ARCHIVE_RECORD, self.new_archive_record)


    def shutDown(self):
        try:
            self.dbm.close()
        except:
            pass

    def new_archive_record(self, event):
        # get Aeris AQI
        aqiIndex_file = "/home/weewx/archive/aqiAeris.json"
        #aeris_id_key = d.get('key', None)
        #aeris_secret_key = d.get('skey', None)
        latitude = 53.605963           # d.get('latitude', None)
        longitude = 11.341407          # d.get('longitude', None)
        aqiIndex_stale_timer =  3540   #self.skin_dict['Extras']['aqiIndex_stale']
        aqiIndex_url = "https://api.aerisapi.com/airquality/%s,%s?client_id=%s&client_secret=%s" % (latitude, longitude, self.aeris_id_key, self.aeris_secret_key)

        # provide info about the system on which we are running
        aqiIndex_is_stale = False

        # Determine if the file exists and get it's modified time
        if os.path.isfile(aqiIndex_file):
            if (int(time.time()) - int(os.path.getmtime(aqiIndex_file))) > int(aqiIndex_stale_timer):
                aqiIndex_is_stale = True
        else:
            # File doesn't exist, download a new copy
            aqiIndex_is_stale = True

        # File is stale, download a new copy
        if aqiIndex_is_stale:
            import urllib.request, urllib.error, urllib.parse
            urllib.request.urlretrieve(aqiIndex_url, aqiIndex_file)

            log.info("New AerisWeather ForecastAQI data downloaded to %s", aqiIndex_file)

        """save data to database """
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
        x_time = ''
        x_aqi = ''
        x_dom = ''
        x_o3 = ''
        x_pm25 = ''
        x_pm10 = ''
        x_co = ''
        x_no2 = ''
        x_so2 = ''

        record = {}
        record['dateTime'] = now_ts
        record['usUnits'] = weewx.METRIC
        record['interval'] = int((now_ts - last_ts) / 60)

        aqiIndex_file = "/home/weewx/archive/aqiAeris.json"

        try:
            with open(aqiIndex_file, encoding="utf8") as read_file:
                data = json.loads(read_file.read())

            x_time = data['response'][0]['periods'][0]['timestamp']
            x_aqi = data['response'][0]['periods'][0]['aqi']
            x_dom = data['response'][0]['periods'][0]['dominant']
            x_o3 = data['response'][0]['periods'][0]['pollutants'][0]['valueUGM3']
            x_pm25 = data['response'][0]['periods'][0]['pollutants'][1]['valueUGM3']
            x_pm10 = data['response'][0]['periods'][0]['pollutants'][2]['valueUGM3']
            x_co = data['response'][0]['periods'][0]['pollutants'][3]['valueUGM3']
            x_no2 = data['response'][0]['periods'][0]['pollutants'][4]['valueUGM3']
            x_so2 = data['response'][0]['periods'][0]['pollutants'][5]['valueUGM3']
            #x_cat = data['response'][0]['periods'][0]['category']
            #x_col = data['response'][0]['periods'][0]['color']
            #x_met = data['response'][0]['periods'][0]['method']

            read_file.close()

        except Exception as e:
            log.debug("read failed for AqiIndex: %s",  e)

        record['o3'] = x_o3
        record['co'] = x_co
        record['no2'] = x_no2
        record['so2'] = x_so2
        record['pm25'] = x_pm25
        record['pm10'] = x_pm10
        record['aqi'] = x_aqi
        if x_dom == "o3":
            x_do = 1
        elif x_dom == "pm2.5":
            x_do = 2
        elif x_dom == "pm10":
            x_do = 3
        elif x_dom == "co":
            x_do = 4
        elif x_dom == "no2":
            x_do = 5
        elif x_dom == "so2":
            x_do = 6
        else:
            x_do = 0

        record['aqitime'] = x_time
        #record['aqicategory'] = x_cat
        #record['aqicolor'] = x_col
        #record['aqimethod'] = x_met
        record['aqidominats'] = x_do

        return record



