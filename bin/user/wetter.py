# $Id: wetter.py 1156 2014-12-03 19:44:45Z mwall $
# Copyright 2013 Matthew Wall
"""
Upload data to wetter.com
  http://wetter.com

[StdRESTful]
    [[Wetter]]
        username = USERNAME
        password = PASSWORD
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

VERSION = "0.2"

if weewx.__version__ < "3":
    raise weewx.UnsupportedFeature("weewx 3 is required, found %s" %
                                   weewx.__version__)

def logmsg(level, msg):
    syslog.syslog(level, 'restx: Wetter: %s' % msg)

def logdbg(msg):
    logmsg(syslog.LOG_DEBUG, msg)

def loginf(msg):
    logmsg(syslog.LOG_INFO, msg)

def logerr(msg):
    logmsg(syslog.LOG_ERR, msg)

class Wetter(weewx.restx.StdRESTbase):
    def __init__(self, engine, config_dict):
        """This service recognizes standard restful options plus the following:

        username: username

        password: password
        """
        super(Wetter, self).__init__(engine, config_dict)        
        loginf("service version is %s" % VERSION)
        try:
            site_dict = config_dict['StdRESTful']['Wetter']
            site_dict = accumulateLeaves(site_dict, max_level=1)
            site_dict['username']
            site_dict['password']
        except KeyError, e:
            logerr("Data will not be posted: Missing option %s" % e)
            return
        site_dict['manager_dict'] = weewx.manager.get_manager_dict(
            config_dict['DataBindings'], config_dict['Databases'], 'wx_binding')

        self.archive_queue = Queue.Queue()
        self.archive_thread = WetterThread(self.archive_queue, **site_dict)
        self.archive_thread.start()
        self.bind(weewx.NEW_ARCHIVE_RECORD, self.new_archive_record)
        loginf("Data will be uploaded for user id %s" % site_dict['username'])

    def new_archive_record(self, event):
        self.archive_queue.put(event.record)

class WetterThread(weewx.restx.RESTThread):

    _SERVER_URL = 'http://www.wetterarchiv.de/interface/http/input.php'
    _DATA_MAP = {'windrichtung': ('windDir',     '%.0f', 1.0), # degrees
                 'windstaerke':  ('windSpeed',   '%.1f', 0.2777777777), # m/s
                 'temperatur':   ('outTemp',     '%.1f', 1.0), # C
                 'feuchtigkeit': ('outHumidity', '%.0f', 1.0), # percent
                 'luftdruck':    ('barometer',   '%.3f', 1.0), # mbar?
                 'niederschlagsmenge': ('hourRain',    '%.2f', 10.0), # mm
                 }

    def __init__(self, queue, username, password, manager_dict,
                 server_url=_SERVER_URL, skip_upload=False,
                 post_interval=None, max_backlog=sys.maxint, stale=None,
                 log_success=True, log_failure=True,
                 timeout=60, max_tries=3, retry_wait=5):
        super(WetterThread, self).__init__(queue,
                                           protocol_name='Wetter',
                                           manager_dict=manager_dict,
                                           post_interval=post_interval,
                                           max_backlog=max_backlog,
                                           stale=stale,
                                           log_success=log_success,
                                           log_failure=log_failure,
                                           max_tries=max_tries,
                                           timeout=timeout,
                                           retry_wait=retry_wait)
        self.username = username
        self.password = password
        self.server_url = server_url
        self.skip_upload = to_bool(skip_upload)

    def process_record(self, record, dbm):
        r = self.get_record(record, dbm)
        data = self.get_data(r)
        if self.skip_upload:
            loginf("skipping upload")
            return
        req = urllib2.Request(self.server_url, urllib.urlencode(data))
        req.get_method = lambda: 'POST'
        req.add_header("User-Agent", "weewx/%s" % weewx.__version__)
        self.post_with_retries(req)

    def check_response(self, response):
        txt = response.read()
        if txt.find('Zugangsdaten%3A+Benutzerdaten+falsch') >= 0:
            raise weewx.restx.BadLogin(txt)
        elif not txt.startswith('status=SUCCESS'):
            raise weewx.restx.FailedPost("Server returned '%s'" % txt)

    def get_data(self, in_record):
        # put everything into the right units
        record = weewx.units.to_METRIC(in_record)

        # put data into expected scaling, structure, and format
        values = {}
        values['benutzername'] = self.username
        values['passwort'] = self.password
        values['niederschlagsmenge_zeit'] = 60
        values['datum'] = time.strftime('%Y%m%d%H%M',
                                        time.localtime(record['dateTime']))
        for key in self._DATA_MAP:
            rkey = self._DATA_MAP[key][0]
            if record.has_key(rkey) and record[rkey] is not None:
                v = record[rkey] * self._DATA_MAP[key][2]
                values[key] = self._DATA_MAP[key][1] % v

        logdbg('data: %s' % values)
        return values
