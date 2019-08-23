# Based on WindFinder plugin, portions copyright 2014 Matthew Wall

"""This is a WeeWX extension that uploads data to WindGuru.

http://www.windguru.cz/

Station must be registered first by visiting:

https://stations.windguru.cz/register.php

The preferred upload frequency (post_interval) is one record every 5 minutes.

Minimal Configuration:

[StdRESTful]
    [[WindGuru]]
        station_id = WINDGURU_STATION_ID
        password = WINDGURU_PASSWORD

WindGuru does not have a published public API, please contact them if you want
to add support, they were very responsive.

Data is uploaded using a GET request:
http://www.windguru.cz/upload/api.php?stationtype=weewx&uid=station_id&interval=60&precip_interval=60&wind_avg=windSpeed&wind_max=windGust&wind_direction=windDir&temperature=outTemp&rh=outHumidity&mslp=barometer&precip=rain

Parameters explained:
interval: seconds, archive interval over which wind information is averaged
precip_interval: seconds, archive interval over which precipitation is accumulated in a sum
wind_avg: knots, average wind speed during interval
wind_max: knots, max wind speed during interval
wind_min: knots, min wind speed during interval
wind_direction: degrees, average wind direction during interval
temperature: celsius
rh: percent
mslp: hPa, mean sea level pressure
precip: mm
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
import weewx.restx
import weewx.units
from weeutil.config import search_up, accumulateLeaves
from weeutil.weeutil import to_bool

log = logging.getLogger(__name__)

VERSION = "0.2"

if weewx.__version__ < "3":
    raise weewx.UnsupportedFeature("weewx 3 is required, found %s" %
                                   weewx.__version__)


def _mps_to_knot(v):
    from_t = (v, 'meter_per_second', 'group_speed')
    return weewx.units.convert(from_t, 'knot')[0]


class WindGuru(weewx.restx.StdRESTbase):
    def __init__(self, engine, config_dict):
        """This service recognizes standard restful options plus the following:

        station_id: WindGuru station identifier

        password: WindGuru password
        """
        super(WindGuru, self).__init__(engine, config_dict)
        log.info("service version is %s", VERSION)
        try:
            site_dict = config_dict['StdRESTful']['WindGuru']
            site_dict = accumulateLeaves(site_dict, max_level=1)
            site_dict['station_id']
            site_dict['password']
        except KeyError as e:
            log.error("Data will not be posted: Missing option %s", e)
            return
        site_dict['manager_dict'] = weewx.manager.get_manager_dict(
                config_dict['DataBindings'], config_dict['Databases'], 'wx_binding')

        self.archive_queue = queue.Queue()
        self.archive_thread = WindGuruThread(self.archive_queue, **site_dict)
        self.archive_thread.start()
        self.bind(weewx.NEW_ARCHIVE_RECORD, self.new_archive_record)
        log.info("Data will be uploaded for %s", site_dict['station_id'])

    def new_archive_record(self, event):
        self.archive_queue.put(event.record)


class WindGuruThread(weewx.restx.RESTThread):
    _SERVER_URL = 'http://www.windguru.cz/upload/api.php'
    _DATA_MAP = {'temperature':     ('outTemp', '%.1f', 1.0),      # C
                 'wind_direction':  ('windDir', '%.0f', 1.0),      # degree
                 'wind_avg':        ('windSpeed', '%.1f', 1.0),    # knots
                 'wind_max':        ('windGust', '%.1f', 1.0),     # knots
                 'mslp':            ('barometer', '%.3f', 1.0),    # hPa
                 'rh':              ('outHumidity', '%.1f', 1.0),  # %
                 'rain':            ('rain', '%.2f', 1.0),         # mm
                 'interval':        ('interval', '%d', 1.0),       # seconds
                 'precip_interval': ('interval', '%d', 1.0)        # seconds
                 }


    try:
        max_integer = sys.maxint    # python 2
    except AttributeError:
        max_integer = sys.maxsize    # python 3

    def __init__(self, queue, station_id, password, manager_dict,
                 server_url=_SERVER_URL, skip_upload=False,
                 post_interval=60, max_backlog=max_integer, stale=None,
                 log_success=True, log_failure=True,
                 timeout=60, max_tries=3, retry_wait=5):
        super(WindGuruThread, self).__init__(queue,
                                             protocol_name='WindGuru',
                                             manager_dict=manager_dict,
                                             post_interval=post_interval,
                                             max_backlog=max_backlog,
                                             stale=stale,
                                             log_success=log_success,
                                             log_failure=log_failure,
                                             max_tries=max_tries,
                                             timeout=timeout,
                                             retry_wait=retry_wait)
        self.station_id = station_id
        self.password = password
        self.server_url = server_url
        self.skip_upload = to_bool(skip_upload)

    def process_record(self, record, dbm):
        r = self.get_record(record, dbm)
        if 'windSpeed' not in r or r['windSpeed'] is None:
            raise weewx.restx.FailedPost("No windSpeed in record")
        url = self.get_url(r)
        if self.skip_upload:
            raise weewx.restx.FailedPost("Upload disabled for this service")
        req = Request(url)
        req.add_header("User-Agent", "weewx/%s" % weewx.__version__)
        self.post_with_retries(req)

    def check_response(self, response):
        lines = []
        for line in response:
            lines.append(line)
        msg = b''.join(lines)
        if not msg.startswith(b'OK'):
            raise weewx.restx.FailedPost("Server response: %s" % msg)

    def get_url(self, in_record):
        # put everything into the right units and scaling
        record = weewx.units.to_METRICWX(in_record)
        if 'windSpeed' in record and record['windSpeed'] is not None:
            record['windSpeed'] = _mps_to_knot(record['windSpeed'])
        if 'windGust' in record and record['windGust'] is not None:
            record['windGust'] = _mps_to_knot(record['windGust'])

        # put data into expected structure and format
        values = {}
        values['stationtype'] = 'weewx'
        values['uid'] = self.station_id
        # TODO: Password md5, though WindGuru doesn't care at the moment
        # values['password'] = self.password
        time_tt = time.localtime(record['dateTime'])
        values['date'] = time.strftime("%d.%m.%Y", time_tt)
        values['time'] = time.strftime("%H:%M", time_tt)
        for key in self._DATA_MAP:
            rkey = self._DATA_MAP[key][0]
            if rkey in record and record[rkey] is not None:
                values[key] = self._DATA_MAP[key][1] % record[rkey]

        url = self.server_url + '?' + urlencode(values)
        if weewx.debug >= 2:
            log.debug('url: %s', re.sub(r"password=[^\&]*", "password=XXX", url))
        return url
