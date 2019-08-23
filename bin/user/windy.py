# Copyright 2019 Matthew Wall

"""
This is a weewx extension that uploads data to a windy.com

http://windy.com

The protocol is desribed at the windy community forum:

https://community.windy.com/topic/8168/report-you-weather-station-data-to-windy

Minimal configuration

[StdRESTful]
    [[Windy]]
        api_key = API_KEY
        station = STATION_IDENTIFIER
"""

from __future__ import absolute_import

import logging


# deal with differences between python 2 and python 3
try:
    from Queue import Queue
except ImportError:
    from queue import Queue

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

from distutils.version import StrictVersion
import json
import sys
import time
import requests

import weewx
import weewx.restx
import weewx.units
from weeutil.weeutil import to_bool

log = logging.getLogger(__name__)


VERSION = "0.31"

REQUIRED_WEEWX = "3.8.0"
if StrictVersion(weewx.__version__) < StrictVersion(REQUIRED_WEEWX):
    raise weewx.UnsupportedFeature("weewx %s or greater is required, found %s"
                                   % (REQUIRED_WEEWX, weewx.__version__))


class Windy(weewx.restx.StdRESTbase):
    _DEFAULT_URL = 'https://stations.windy.com/pws/update'

    def __init__(self, engine, cfg_dict):
        super(Windy, self).__init__(engine, cfg_dict)
        log.info("version is %s", VERSION)
        site_dict = weewx.restx.get_site_dict(cfg_dict, 'Windy',
                                              'api_key', 'station')
        if site_dict is None:
            return
        site_dict.setdefault('server_url', Windy._DEFAULT_URL)

        # FIXME: we should not have to do this here!
        binding = site_dict.pop('binding', 'wx_binding')
        mgr_dict = weewx.manager.get_manager_dict_from_config(
            cfg_dict, binding)

        self.archive_queue = Queue()
        self.archive_thread = WindyThread(self.archive_queue,
                                          manager_dict=mgr_dict,
                                          **site_dict)

        self.archive_thread.start()
        self.bind(weewx.NEW_ARCHIVE_RECORD, self.new_archive_record)
        log.info("Data will be uploaded to %s", site_dict['server_url'])

    def new_archive_record(self, event):
        self.archive_queue.put(event.record)


class WindyThread(weewx.restx.RESTThread):

    def __init__(self, queue, api_key, station, server_url=Windy._DEFAULT_URL,
                 skip_upload=False, manager_dict=None,
                 post_interval=None, max_backlog=sys.maxsize, stale=None,
                 log_success=True, log_failure=True,
                 timeout=60, max_tries=3, retry_wait=5):
        super(WindyThread, self).__init__(queue,
                                          protocol_name='Windy',
                                          manager_dict=manager_dict,
                                          post_interval=post_interval,
                                          max_backlog=max_backlog,
                                          stale=stale,
                                          log_success=log_success,
                                          log_failure=log_failure,
                                          max_tries=max_tries,
                                          timeout=timeout,
                                          retry_wait=retry_wait)
        self.api_key = api_key
        self.station = int(station)
        self.server_url = server_url
        self.skip_upload = to_bool(skip_upload)

    def format_url(self, _):
        """Return an URL for doing a POST to windy"""
        url = '%s/%s' % (self.server_url, self.api_key)
        if weewx.debug >= 2:
            log.debug("url: %s", url)

        #url = url + '?'
        #data = self.get_post_body(self)
        #return requests.post(url, json=data)
        return url

    def get_post_body(self, record):
        """Specialized version for doing a POST to windy"""
        record_m = weewx.units.to_METRICWX(record)
        data = {
            'station': self.station,  # integer identifier, usually "0"
            'dateutc':time.strftime("%Y-%m-%d %H:%M:%S",
                                    time.gmtime(record_m['dateTime']))
            }
        if 'outTemp' in record_m:
            data['temp'] = record_m['outTemp']  # degree_C
        if 'windSpeed' in record_m:
            data['wind'] = record_m['windSpeed']  # m/s
        if 'windDir' in record_m:
            data['winddir'] = record_m['windDir']  # degree
        if 'windGust' in record_m:
            data['gust'] = record_m['windGust']  # m/s
        if 'outHumidity' in record_m:
            data['rh'] = record_m['outHumidity']  # percent
        if 'dewpoint' in record_m:
            data['dewpoint'] = record_m['dewpoint']  # degree_C
        if 'barometer' in record_m:
            data['pressure'] = 100.0 * record_m['barometer']  # Pascals
        if 'hourRain' in record_m:
            data['precip'] = record_m['hourRain']  # mm in past hour
        if 'UV' in record_m:
            data['uv'] = record_m['UV']

        body = {
            'observations': [data]
        }
        if weewx.debug >= 2:
            log.debug("JSON: %s", body)

        return json.dumps(body), 'application/json'

# Use this hook to test the uploader:
#   PYTHONPATH=bin python bin/user/windy.py

if __name__ == "__main__":
    class FakeMgr(object):
        table_name = 'fake'

        def getSql(self, query, value):
            return None


    weewx.debug = 2
    queue = Queue()
    t = WindyThread(queue, api_key='123', station=0)
    r = {'dateTime': int(time.time() + 0.5),
         'usUnits': weewx.US,
         'outTemp': 32.5,
         'inTemp': 75.8,
         'outHumidity': 24,
         'windSpeed': 10,
         'windDir': 32}
    print(t.format_url(r))
#    print(t.get_post_body(r))
    t.process_record(r, FakeMgr())

