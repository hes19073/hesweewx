# $Id: owm.py 1767 2017-11-08 13:13:33Z mwall $
# Copyright 2013 Matthew Wall
"""
Upload data to OpenWeatherMap
  http://openweathermap.org

Thanks to Antonio Burriel for the dewpoint, longitude, and radiation fixes.

[StdRESTful]
    [[OpenWeatherMap]]
        appid = APPID
        station_id = STATION_ID
"""

# FIXME: set the station lat/lon/alt using [PUT]/stations/{:id}

import re
import sys
import time

try:
    import cjson as json
    setattr(json, 'dumps', json.encode)
    setattr(json, 'loads', json.decode)
except (ImportError, AttributeError):
    try:
        import simplejson as json
    except ImportError:
        import json

import weewx
import weewx.restx
import weewx.units
from weeutil.weeutil import to_bool, accumulateLeaves
from weeutil.log import logdbg, loginf, logerr, logcrt

VERSION = "0.8.1"

if weewx.__version__ < "3":
    raise weewx.UnsupportedFeature("weewx 3 is required, found %s" %
                                   weewx.__version__)

#def logmsg(level, msg):
#    syslog.syslog(level, 'restx: OWM: %s' % msg)

#def logdbg(msg):
#    logmsg(syslog.LOG_DEBUG, msg)

#def loginf(msg):
#    logmsg(syslog.LOG_INFO, msg)

#def logerr(msg):
#    logmsg(syslog.LOG_ERR, msg)


def _obfuscate(s):
    return ('X'*(len(s)-4) + s[-4:])


class OpenWeatherMap(weewx.restx.StdRESTful):
    def __init__(self, engine, config_dict):
        """This service recognizes standard restful options plus the following:

        appid: APPID from OpenWeatherMap

        station_id: station identifier

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
            site_dict['appid']
            site_dict['station_id']
        except KeyError, e:
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
        loginf("Data will be uploaded for %s" % site_dict['station_id'])

    def new_archive_record(self, event):
        self.archive_queue.put(event.record)

class OpenWeatherMapThread(weewx.restx.RESTThread):

    # observations we should provide but do not
    # rain_6h mm
    # show_1h mm
    # snow_6h mm
    # snow_24h mm
    # visibility_distance km
    # visibility_prefix (N,E,S,W)
    # clouds[]:distance m
    # clouds[]:condition (SKC,NSC,FEW,SCT,BKN,OVC)
    # clouds[]:cumulus (CB,TCU)
    # weather[]:precipitation
    # weather[]:descriptor
    # weather[]:intensity
    # weather[]:proximity
    # weather[]:obsruration
    # weather[]:other
    #
    # derived quantities we could provide but do not
    # humidex
    # dew_point
    # heat_index
    #
    # observations we could provide but the api does not accept
    # uv
    # luminosity
    # radiation

    _SERVER_URL = 'http://api.openweathermap.org/data/3.0/measurements'
    _DATA_MAP = {
        'dt':          ('dateTime',    1, 0),        # epoch
        'wind_deg':    ('windDir',     1.0, 0.0),    # degrees
        'wind_speed':  ('windSpeed',   0.2777777777, 0.0), # m/s
        'wind_gust':   ('windGust',    0.2777777777, 0.0), # m/s
        'temperature': ('outTemp',     1.0, 0.0),    # C
        'humidity':    ('outHumidity', 1.0, 0.0),    # percent
        'pressure':    ('barometer',   1.0, 0.0),    # mbar?
        'rain_1h':     ('hourRain',    10.0, 0.0),   # mm
        'rain_24h':    ('rain24',      10.0, 0.0),   # mm
        }

    try:
        max_integer = sys.maxint    # python 2
    except AttributeError:
        max_integer = sys.maxsize # python 3


    def __init__(self, queue,
                 appid, latitude, longitude, altitude,
                 station_id, manager_dict,
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
        self.appid = appid
        self.latitude = float(latitude)
        self.longitude = float(longitude)
        self.altitude = float(altitude)
        self.station_id = station_id
        self.server_url = server_url
        self.skip_upload = to_bool(skip_upload)

    def process_record(self, record, dbm):
        r = self.get_record(record, dbm)
        data = self.get_data(r)
        url = "%s?appid=%s" % (self.server_url, self.appid)
        if weewx.debug > 1:
            logdbg('url: %s?appid=%s' %
                   (self.server_url, _obfuscate(self.appid)))
            logdbg('data: %s' % data)
        if self.skip_upload:
            loginf("skipping upload")
            return
        req = Request(url, data)
        req.get_method = lambda: 'POST'
        req.add_header("Content-Type", "application/json")
        req.add_header("User-Agent", "weewx/%s" % weewx.__version__)
        self.post_with_retries(req)

    def get_data(self, in_record):
        # put everything into the right units
        record = weewx.units.to_METRIC(in_record)

        # put data into expected scaling, structure, and format
        values = dict()
        values['station_id'] = self.station_id
        for _key in self._DATA_MAP:
            rkey = self._DATA_MAP[_key][0]
            if rkey in record and record[rkey] is not None:
                values[_key] = record[rkey] * self._DATA_MAP[_key][1] + self._DATA_MAP[_key][2]

        data = json.dumps([values])

        return data
