# $Id: weather365.py 0957 14-04-2017 1.3.1$
# Copyright 2017 Frank Bandle 
# based on Scripts written by M.Wall
# Thanks Luc Heijst for testing and correction
"""
Upload data to weather365.net
  https://channel1.weather365.net/stations/

[StdRESTful]
    [[Weather365]]
        stationid = INSERT_STATIONID_HERE
        password  = INSERT_PASSWORD_HERE
"""

from __future__ import absolute_import

import logging
import re
import sys
import time

# Python 2/3 compatiblity
try:
    import Queue as queue                   # python 2
    from urllib import urlencode            # python 2
    from urllib2 import Request             # python 2
except ImportError:
    import queue                            # python 3
    from urllib.parse import urlencode      # python 3
    from urllib.request import Request      # python 3

import weewx
import weeutil.logger
import weewx.restx
import weewx.units
from weeutil.config import search_up, accumulateLeaves
from weeutil.weeutil import to_bool

log = logging.getLogger(__name__)


VERSION = "1.4.2"

if weewx.__version__ < "3":
    raise weewx.UnsupportedFeature("weewx 3 is required, found %s" %
                                   weewx.__version__)

class Weather365(weewx.restx.StdRESTbase):
    def __init__(self, engine, config_dict):
        """This service recognizes standard restful options plus the following:

        stationid = INSERT_STATIONID_HERE
        password  = INSERT_PASSWORD_HERE

        latitude: Station latitude in decimal degrees
        Default is station latitude

        longitude: Station longitude in decimal degrees
        Default is station longitude
        """
        super(Weather365, self).__init__(engine, config_dict)
        log.info("service version is %s", VERSION)
        try:
            site_dict = config_dict['StdRESTful']['Weather365']
            site_dict = accumulateLeaves(site_dict, max_level=1)
            site_dict['stationid']
            site_dict['password']
        except KeyError as e:
            log.error("Data will not be posted: Missing option %s", e)
            return
        site_dict.setdefault('latitude', engine.stn_info.latitude_f)
        site_dict.setdefault('longitude', engine.stn_info.longitude_f)
        site_dict.setdefault('altitude', engine.stn_info.altitude_vt[0])
        site_dict['manager_dict'] = weewx.manager.get_manager_dict(
            config_dict['DataBindings'], config_dict['Databases'], 'wx_binding')

        self.archive_queue = queue.Queue()
        self.archive_thread = Weather365Thread(self.archive_queue, **site_dict)
        self.archive_thread.start()
        self.bind(weewx.NEW_ARCHIVE_RECORD, self.new_archive_record)
        log.info("Data will be uploaded for station id %s", site_dict['stationid'])

    def new_archive_record(self, event):
        self.archive_queue.put(event.record)

class Weather365Thread(weewx.restx.RESTThread):

    _SERVER_URL = 'https://channel1.weather365.net/stations/index.php'
    _DATA_MAP = {'winddir':    ('windDir',      '%.0f', 1.0), # degrees
                 'windspeed':  ('windSpeed',    '%.1f', 0.2777777777), # m/s
                 'windgust':   ('windGust',     '%.1f', 0.2777777777), # m/s
                 't2m':        ('outTemp',      '%.1f', 1.0), # C
                 'relhum':     ('outHumidity',  '%.0f', 1.0), # percent
                 'press':      ('barometer',    '%.3f', 1.0), # hpa?
                 'rainh':      ('hourRain',     '%.2f', 10.0), # mm
                 'raind':      ('dayRain',      '%.2f', 10.0), # mm
                 'rainrate':   ('rainRate',     '%.2f', 1.0), # mm/hr 
                 'uvi':        ('UV',           '%.1f', 1.0), # index * 1
                 'radi':       ('radiation',    '%.1f', 1.0), # W/m^2 * 1
                 'et':         ('ET',           '%.5f', 10.0), # mm * 1
                 'wchill':     ('windchill',    '%.1f', 1.0), # C * 1
                 'heat':       ('heatindex',    '%.1f', 1.0), # C * 1
                 'dew2m':      ('dewpoint',     '%.1f', 1.0), # C * 1
                 'rxsignal':   ('rxCheckPercent', '%.0f', 1.0), # percent / dB
                 'cloudbase':  ('cloudbase',     '%.1f', 1.0), # m 
                 'windrun':    ('windrun',       '%.1f', 1.0), # m
                 'humidex':    ('humidex',       '%.1f', 1.0), # 
                 'appTemp':    ('appTemp',       '%.1f', 1.0), # C
                 'soiltemp':      ('soilTemp1',   '%.1f', 1.0), # C
                 'soiltemp2':     ('soilTemp2',   '%.1f', 1.0), # C
                 'soiltemp3':     ('soilTemp3',   '%.1f', 1.0), # C
                 'soiltemp4':     ('soilTemp4',   '%.1f', 1.0), # C
                 'soilmoisture':  ('soilMoist1',  '%.1f', 1.0), # %
                 'soilmoisture2': ('soilMoist2',  '%.1f', 1.0), # %
                 'soilmoisture3': ('soilMoist3',  '%.1f', 1.0), # %
                 'soilmoisture4': ('soilMoist4',  '%.1f', 1.0), # %
                 'leafwetness':   ('leafWet1',    '%.1f', 1.0), # %
                 'leafwetness2':  ('leafWet2',    '%.1f', 1.0), # %
                 'temp2':         ('extraTemp1',  '%.1f', 1.0), # C
                 'temp3':         ('extraTemp2',  '%.1f', 1.0), # C
                 'temp4':         ('extraTemp3',  '%.1f', 1.0), # C
                 'humidity2':     ('extraHumid1', '%.0f', 1.0), # %
                 'humidity3':     ('extraHumid2', '%.0f', 1.0), # %
                 'txbattery':     ('txBatteryStatus', '%.0f', 1.0), # %
                 }

    try:
        max_integer = sys.maxint    # python 2
    except AttributeError:
        max_integer = sys.maxsize    # python 3

    def __init__(self, queue,
                 stationid, password, latitude, longitude, altitude,
                 manager_dict,
                 server_url=_SERVER_URL, skip_upload=False,
                 post_interval=None, max_backlog=max_integer, stale=None,
                 log_success=True, log_failure=True,
                 timeout=60, max_tries=3, retry_wait=5):
        super(Weather365Thread, self).__init__(queue,
                                           protocol_name='Weather365',
                                           manager_dict=manager_dict,
                                           post_interval=post_interval,
                                           max_backlog=max_backlog,
                                           stale=stale,
                                           log_success=log_success,
                                           log_failure=log_failure,
                                           max_tries=max_tries,
                                           timeout=timeout,
                                           retry_wait=retry_wait)
        self.latitude = float(latitude)
        self.longitude = float(longitude)
        self.altitude = float(altitude)
        self.stationid = stationid
        self.server_url = server_url
        self.skip_upload = to_bool(skip_upload)

    def process_record(self, record, dbm):
        r = self.get_record(record, dbm)
        data = self.get_data(r)
        url_data = urlencode(data).encode('utf-8')
        if self.skip_upload:
            log.info("skipping upload")
            return
        req = Request(self.server_url, url_data)
        #log.info("Data uploaded to %s is: (%s)", self.server_url, url_data)
        req.get_method = lambda: 'POST'
        req.add_header("User-Agent", "weewx/%s" % weewx.__version__)
        self.post_with_retries(req)

    def check_response(self, response):
        txt = response.read()
        if txt.find(b'invalid-login-data') >= 0:
            raise weewx.restx.BadLogin(txt)
        elif not txt.startswith(b'INSERT'):
            raise weewx.restx.FailedPost("Server returned '%s'" % txt)

    def get_data(self, in_record):
        # put everything into the right units
        record = weewx.units.to_METRIC(in_record)

        # put data into expected scaling, structure, and format
        values = {}
        values['lat']  = str(self.latitude)
        values['long'] = str(self.longitude)
        values['alt']  = str(self.altitude) # meter
        values['stationid'] = self.stationid
        values['prec_time'] = 60
        values['datum'] = time.strftime('%Y%m%d%H%M',
                                        time.localtime(record['dateTime']))
        values['utcstamp'] = int(record['dateTime'])
        for key in self._DATA_MAP:
            rkey = self._DATA_MAP[key][0]
            if rkey in record and record[rkey] is not None:
                v = record[rkey] * self._DATA_MAP[key][2]
                values[key] = self._DATA_MAP[key][1] % v

        return values
