# $Id: windfinder.py 1300 2015-04-14 13:19:10Z mwall $
# Copyright 2014 Matthew Wall

"""
This is a weewx extension that uploads data to WindFinder.

http://www.windfinder.com/

Based on windfinder API as of 10jun2014:

http://www.windfinder.com/wind-cgi/httpload.pl?sender_id=<stationID>&password=<PWD>&date=19.5.2011&time=17:13&airtemp=20&windspeed=12&gust=14&winddir=180&pressure=1012&rain=5

Station must be registered first by visiting:

http://www.windfinder.com/weather-station/add.htm

The preferred upload frequency (post_interval) is one record every 15 minutes.

Minimal Configuration:

[StdRESTful]
    [[WindFinder]]
        station_id = WINDFINDER_STATION_ID
        password = WINDFINDER_PASSWORD
"""

import Queue
import sys
import syslog
import time
import urllib
import urllib2

import weewx
import weewx.restx
import weewx.units
from weeutil.weeutil import to_bool, accumulateLeaves

VERSION = "0.8"

if weewx.__version__ < "3":
    raise weewx.UnsupportedFeature("weewx 3 is required, found %s" %
                                   weewx.__version__)

def logmsg(level, msg):
    syslog.syslog(level, 'restx: WindFinder: %s' % msg)

def logdbg(msg):
    logmsg(syslog.LOG_DEBUG, msg)

def loginf(msg):
    logmsg(syslog.LOG_INFO, msg)

def logerr(msg):
    logmsg(syslog.LOG_ERR, msg)

def _mps_to_knot(v):
    from_t = (v, 'meter_per_second', 'group_speed')
    return weewx.units.convert(from_t, 'knot')[0]

class WindFinder(weewx.restx.StdRESTbase):
    def __init__(self, engine, config_dict):
        """This service recognizes standard restful options plus the following:

        station_id: WindFinder station identifier

        password: WindFinder password
        """
        super(WindFinder, self).__init__(engine, config_dict)
        loginf("service version is %s" % VERSION)
        try:
            site_dict = config_dict['StdRESTful']['WindFinder']
            site_dict = accumulateLeaves(site_dict, max_level=1)
            site_dict['station_id']
            site_dict['password']
        except KeyError, e:
            logerr("Data will not be posted: Missing option %s" % e)
            return
        site_dict['manager_dict'] = weewx.manager.get_manager_dict(
            config_dict['DataBindings'], config_dict['Databases'], 'wx_binding')

        self.archive_queue = Queue.Queue()
        self.archive_thread = WindFinderThread(self.archive_queue, **site_dict)
        self.archive_thread.start()
        self.bind(weewx.NEW_ARCHIVE_RECORD, self.new_archive_record)
        loginf("Data will be uploaded for %s" % site_dict['station_id'])

    def new_archive_record(self, event):
        self.archive_queue.put(event.record)

class WindFinderThread(weewx.restx.RESTThread):

    _SERVER_URL = 'http://www.windfinder.com/wind-cgi/httpload.pl'
    _DATA_MAP = {'airtemp':       ('outTemp',     '%.1f'), # C
                 'winddir':       ('windDir',     '%.0f'), # degree
                 'windspeed':     ('windSpeed',   '%.1f'), # knots
                 'gust':          ('windGust',    '%.1f'), # knots
                 'pressure':      ('barometer',   '%.3f'), # hPa
                 'rain':          ('rainRate',    '%.2f'), # mm/hr
                 }

    def __init__(self, queue, station_id, password, manager_dict,
                 server_url=_SERVER_URL, skip_upload=False,
                 post_interval=300, max_backlog=sys.maxint, stale=None,
                 log_success=True, log_failure=True,
                 timeout=60, max_tries=3, retry_wait=5):
        super(WindFinderThread, self).__init__(queue,
                                               protocol_name='WindFinder',
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
        req = urllib2.Request(url)
        req.add_header("User-Agent", "weewx/%s" % weewx.__version__)
        self.post_with_retries(req)

    def check_response(self, response):
        # this is a very crude way to parse the response, but windfinder does
        # not make things easy for us.  the status is contained within the
        # body tags in an html response.  no codes, no http status.  sigh.
        lines = []
        reading = False
        for line in response:
            if line.find('<body') >= 0:
                reading = True
            elif line.find('</body>') >= 0:
                reading = False
            elif reading:
                lines.append(line)
        msg = ''.join(lines)
        if not msg.startswith('OK'):
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
        values['sender_id'] = self.station_id
        values['password'] = self.password
        time_tt = time.localtime(record['dateTime'])
        values['date'] = time.strftime("%d.%m.%Y", time_tt)
        values['time'] = time.strftime("%H:%M", time_tt)
        for key in self._DATA_MAP:
            rkey = self._DATA_MAP[key][0]
            if record.has_key(rkey) and record[rkey] is not None:
                values[key] = self._DATA_MAP[key][1] % record[rkey]
        url = self.server_url + '?' + urllib.urlencode(values)
        logdbg('url: %s' % url)
        return url
