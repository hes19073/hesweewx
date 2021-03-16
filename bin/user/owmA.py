# $Id: owm.py 1156 2014-12-03 19:44:45Z mwall $
# Copyright 2013 Matthew Wall
""" Upload data to OpenWeatherMap
  http://openweathermap.org

Thanks to Antonio Burriel for the dewpoint, longitude, and radiation fixes.

[StdRESTful]
    [[OpenWeatherMap]]
        username = OWM_USERNAME
        password = OWM_PASSWORD
        station_name = STATION_NAME
"""

import re
import sys
import syslog
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
import weewx.restx
import weewx.units
from weeutil.weeutil import to_bool, accumulateLeaves

VERSION = "0.4"

if weewx.__version__ < "3":
    raise weewx.UnsupportedFeature("weewx 3 is required, found %s" %
                                   weewx.__version__)

def logmsg(level, msg):
    syslog.syslog(level, 'restx: OWM: %s' % msg)

def logdbg(msg):
    logmsg(syslog.LOG_DEBUG, msg)

def loginf(msg):
    logmsg(syslog.LOG_INFO, msg)

def logerr(msg):
    logmsg(syslog.LOG_ERR, msg)

class OpenWeatherMap(weewx.restx.StdRESTbase):
    def __init__(self, engine, config_dict):
        """This service recognizes standard restful options plus the following:

        username: OpenWeatherMap username

        password: OpenWeatherMap password

        station_name: station name

        latitude: Station latitude in decimal degrees
        Default is station latitude

        longitude: Station longitude in decimal degrees
        Default is station longitude

        altitude: Station altitude in meters
        Default is station altitude
        """
        super(OpenWeatherMap, self).__init__(engine, config_dict)        
        loginf('service version is %s' % VERSION)
        try:
            site_dict = config_dict['StdRESTful']['OpenWeatherMap']
            site_dict = accumulateLeaves(site_dict, max_level=1)
            site_dict['username']
            site_dict['password']
            site_dict['station_name']
        except KeyError as e:
            logerr("Data will not be posted: Missing option %s" % e)
            return

        site_dict.setdefault('latitude', engine.stn_info.latitude_f)
        site_dict.setdefault('longitude', engine.stn_info.longitude_f)
        site_dict.setdefault('altitude', engine.stn_info.altitude_vt[0])
        site_dict['manager_dict'] = weewx.manager.get_manager_dict(
            config_dict['DataBindings'], config_dict['Databases'], 'wx_binding')

        self.archive_queue = queue.Queue()
        self.archive_thread = OpenWeatherMapThread(self.archive_queue, **site_dict)
        self.archive_thread.start()

        self.bind(weewx.NEW_ARCHIVE_RECORD, self.new_archive_record)
        loginf("Data will be uploaded for %s" % site_dict['station_name'])

    def new_archive_record(self, event):
        self.archive_queue.put(event.record)

class OpenWeatherMapThread(weewx.restx.RESTThread):
    """The OpenWeatherMap api does not include timestamp, so we can only
    upload the latest observation.
    """

    _SERVER_URL = 'http://openweathermap.org/data/post'
    _DATA_MAP = {
        'wind_dir':   ('windDir',     '%.0f', 1.0, 0.0),    # degrees
        'wind_speed': ('windSpeed',   '%.1f', 0.2777777777, 0.0), # m/s
        'wind_gust':  ('windGust',    '%.1f', 0.2777777777, 0.0), # m/s
        'temp':       ('outTemp',     '%.1f', 1.0, 0.0),    # C
        'humidity':   ('outHumidity', '%.0f', 1.0, 0.0),    # percent
        'pressure':   ('barometer',   '%.3f', 1.0, 0.0),    # mbar?
        'rain_1h':    ('hourRain',    '%.2f', 10.0, 0.0),   # mm
        'rain_24h':   ('rain24',      '%.2f', 10.0, 0.0),   # mm
        'rain_today': ('dayRain',     '%.2f', 10.0, 0.0),   # mm
        'snow':       ('snow',        '%.2f', 10.0, 0.0),   # mm
        'lum':        ('radiation',   '%.2f', 1.0, 0.0),    # W/m^2
        'dewpoint':   ('dewpoint',    '%.1f', 1.0, 273.15), # K
        'uv':         ('UV',          '%.2f', 1.0, 0.0),    # index
        }

    try:
        max_integer = sys.maxint    # python 2
    except AttributeError:
        max_integer = sys.maxsize # python 3

    def __init__(self, queue,
                 username, password, latitude, longitude, altitude,
                 station_name, manager_dict,
                 server_url=_SERVER_URL, skip_upload=False,
                 post_interval=None, max_backlog=0, stale=None,
                 log_success=True, log_failure=True,
                 timeout=60, max_tries=3, retry_wait=5):

        super(OpenWeatherMapThread, self).__init__(queue,
                                                   protocol_name='OWM',
                                                   manager_dict=manager_dict,
                                                   post_interval=post_interval,
                                                   max_backlog=max_backlog,
                                                   stale=stale,
                                                   log_success=log_success,
                                                   log_failure=log_failure,
                                                   timeout=timeout,
                                                   max_tries=max_tries,
                                                   retry_wait=retry_wait)

        self.username = username
        self.password = password
        self.latitude = float(latitude)
        self.longitude = float(longitude)
        self.altitude = float(altitude)
        self.station_name = station_name
        self.server_url = server_url
        self.skip_upload = to_bool(skip_upload)

    def process_record(self, record, dbm):
        r = self.get_record(record, dbm)
        data = self.get_data(r)
        if self.skip_upload:
            loginf("skipping upload")
            return

        req = Request(self.server_url, data)
        req.get_method = lambda: 'POST'
        req.add_header("User-Agent", "weewx/%s" % weewx.__version__)
        b64s = base64.encodestring('%s:%s' % (self.username, self.password)).replace('\n', '')
        req.add_header("Authorization", "Basic %s" % b64s)
        self.post_with_retries(req)

    def get_data(self, in_record):
        # put everything into the right units
        record = weewx.units.to_METRIC(in_record)

        # put data into expected scaling, structure, and format
        values = {}
        values['name'] = self.station_name
        values['lat']  = str(self.latitude)
        values['long'] = str(self.longitude)
        values['alt']  = str(self.altitude) # meter
        for key in self._DATA_MAP:
            rkey = self._DATA_MAP[key][0]
            if rkey in record and record[rkey] is not None:
                v = record[rkey] * self._DATA_MAP[key][2] + self._DATA_MAP[key][3]
                values[key] = self._DATA_MAP[key][1] % v

        logdbg('data: %s' % values)

        values = urlencode(values)

        return values

