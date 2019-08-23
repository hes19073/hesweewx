# $Id: wetter.py 1492 2016-06-24 15:42:44Z mwall $
# Copyright 2013 Matthew Wall
"""
Upload data to wetter.com
  http://wetter.com

[StdRESTful]
    [[Wetter]]
        enable = true | false
        username = STATION ID
        password = STATION PASSWORD
"""

import re
import sys
import time

# Python 2/3 compatiblity
try:
    import Queue as queue                   # python 2
    from urllib import urlencode            # python 2
    from urllib2 import Request as request  # python 2
except ImportError:
    import queue                            # python 3
    from urllib.parse import urlencode      # python 3
    from urllib.request import Request      # python 3

import weewx
import weewx.restx
import weewx.units
from weeutil.weeutil import to_bool, accumulateLeaves
from weeutil.log import logdbg, loginf, logerr, logcrt

VERSION = "0.6"
API_VERSION = "0.5"

if weewx.__version__ < "3":
    raise weewx.UnsupportedFeature("weewx 3 is required, found %s" %
                                   weewx.__version__)


class Wetter(weewx.restx.StdRESTful):
        """This service recognizes standard restful options plus the following:

        username: username

        password: password
        """
    _SERVER_URL = 'http://interface.wetterarchiv.de/weather'

    def __init__(self, engine, cfg_dict):
        super(Wetter, self).__init__(engine, cfg_dict)
        loginf("version is %s" % VERSION)
        loginf("wetter API version is %s" % API_VERSION)
        site_dict = weewx.restx.get_site_dict(cfg_dict, 'Wetter',
                                              'username', 'password')
        if site_dict is None:
            return
        site_dict.setdefault('server_url', Wetter._SERVER_URL)

        # FIXME: we should not have to do this here!
        binding = site_dict.pop('binding', 'wx_binding')
        mgr_dict = weewx.manager.get_manager_dict_from_config(
            cfg_dict, binding)

        self.archive_queue = Queue()
        self.archive_thread = WetterThread(self.archive_queue,
                                          manager_dict=mgr_dict,
                                          **site_dict)

        self.archive_thread.start()
        self.bind(weewx.NEW_ARCHIVE_RECORD, self.new_archive_record)
        loginf("Data will be uploaded to %s" % site_dict['server_url'])
        loginf("Data will be uploaded for station id %s" % site_dict['username'])

    def new_archive_record(self, event):
        self.archive_queue.put(event.record)

class WetterThread(weewx.restx.RESTThread):

    _SERVER_URL = 'http://interface.wetterarchiv.de/weather'
    _DATA_MAP = {'hu':  ('outHumidity', '%.0f', 1.0), # percent
                 'te':  ('outTemp',     '%.1f', 1.0), # C
                 'dp':  ('dewpoint',    '%.1f', 1.0), # C
                 'pr':  ('barometer',   '%.1f', 1.0), # hPa
                 'wd':  ('windDir',     '%.0f', 1.0), # degrees
                 'ws':  ('windSpeed',   '%.1f', 1.0), # m/s
                 'wg':  ('windGust',    '%.1f', 1.0), # m/s
                 'pa':  ('hourRain',    '%.2f', 1.0), # mm
                 'rr':  ('rainRate',    '%.2f', 1.0), # mm/hr
                 'uv':  ('UV',          '%.0f', 1.0), # uv index
                 'sr':  ('radiation',   '%.2f', 1.0), # W/m^2
                 }
                 #'hui': ('inHumidity',  '%.0f', 1.0), # percent
                 #'tei': ('inTemp',      '%.1f', 1.0), # C
                 #'huo': ('extraHumid1', '%.0f', 1.0), # percent
                 #'teo': ('extraTemp1',  '%.1f', 1.0), # C
                 #'tes': ('soilTemp1',   '%.1f', 1.0)  # C
                 #}

    def __init__(self, queue, username, password, manager_dict=None,
                 server_url=Wetter._SERVER_URL, skip_upload=False,
                 post_interval=None, max_backlog=sys.maxsize, stale=None,
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
        #url = urlencode(data)
        url = urlencode(data).encode('utf-8')
        if weewx.debug >= 2:
            logdbg('url: %s' % re.sub(r"passwort=[^\&]*", "passwort=XXX", url))
        if self.skip_upload:
            loginf("skipping upload")
            return
        req = Request(self.server_url, url)
        req.add_header("User-Agent", "weewx/%s" % weewx.__version__)
        self.post_with_retries(req)

    def check_response(self, response):
        txt = response.read().lower()
        if txt.find(b'"errorcode":"100"') != -1 or \
           txt.find(b'"errorcode":"101"') != -1 or \
           txt.find(b'"errorcode":"102"') != -1:
            raise weewx.restx.BadLogin(txt)
        elif txt.find(b'"status":"error"') != -1:
            raise weewx.restx.FailedPost("Server returned '%s'" % txt)

    def get_data(self, in_record):
        # put everything into the right units
        record = weewx.units.to_METRICWX(in_record)

        # put data into expected scaling, structure, and format
        values = {}
        values['id'] = self.username
        values['pwd'] = self.password
        values['sid'] = 'weewx'
        values['ver'] = weewx.__version__
        values['dtutc'] = time.strftime('%Y%m%d%H%M', time.gmtime(record['dateTime']))
        for key in self._DATA_MAP:
            rkey = self._DATA_MAP[key][0]
            if rkey in record and record[rkey] is not None:
                values[key] = self._DATA_MAP[key][1] % record[rkey]

        return values
