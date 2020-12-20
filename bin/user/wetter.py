# Copyright 2013-2020 Matthew Wall
"""
Upload data to wetter.com
  http://wetter.com

[StdRESTful]
    [[Wetter]]
        enable = true | false
        username = STATION ID
        password = STATION PASSWORD
"""

try:
    # Python 3
    import queue
except ImportError:
    import Queue as queue
import re
import sys
import time
try:
    # Python 3
    from urllib.parse import urlencode
except ImportError:
    # Python 2
    from urllib import urlencode

import weewx
import weewx.restx
import weewx.units

VERSION = "0.6"
API_VERSION = "5.0.2 - 2015/06/01"

if weewx.__version__ < "3":
    raise weewx.UnsupportedFeature("weewx 3 is required, found %s" %
                                   weewx.__version__)

try:
    # Test for new-style weewx logging by trying to import weeutil.logger
    import weeutil.logger
    import logging
    log = logging.getLogger(__name__)

    def logdbg(msg):
        log.debug(msg)

    def loginf(msg):
        log.info(msg)

    def logerr(msg):
        log.error(msg)

except ImportError:
    # Old-style weewx logging
    import syslog

    def logmsg(level, msg):
        syslog.syslog(level, 'Wetter: %s' % msg)

    def logdbg(msg):
        logmsg(syslog.LOG_DEBUG, msg)

    def loginf(msg):
        logmsg(syslog.LOG_INFO, msg)

    def logerr(msg):
        logmsg(syslog.LOG_ERR, msg)


class Wetter(weewx.restx.StdRESTful):
    def __init__(self, engine, config_dict):
        """This service recognizes standard restful options plus the following:

        username: username

        password: password
        """
        super(Wetter, self).__init__(engine, config_dict)        
        loginf("service version is %s" % VERSION)
        loginf("wetter API version is %s" % API_VERSION)
        site_dict = weewx.restx.get_site_dict(config_dict, 'Wetter', 'username', 'password')
        if site_dict is None:
            return

        site_dict['manager_dict'] = weewx.manager.get_manager_dict_from_config(
            config_dict, 'wx_binding')

        self.archive_queue = queue.Queue()
        self.archive_thread = WetterThread(self.archive_queue, **site_dict)
        self.archive_thread.start()
        self.bind(weewx.NEW_ARCHIVE_RECORD, self.new_archive_record)
        loginf("Data will be uploaded for station id %s" % site_dict['username'])

    def new_archive_record(self, event):
        self.archive_queue.put(event.record)

class WetterThread(weewx.restx.RESTThread):

    _SERVER_URL = 'http://interface.wetterarchiv.de/weather'
    _DATA_MAP = {'hu':  ('outHumidity', '%.0f'), # percent
                 'te':  ('outTemp',     '%.1f'), # C
                 'dp':  ('dewpoint',    '%.1f'), # C
                 'pr':  ('barometer',   '%.1f'), # hPa
                 'wd':  ('windDir',     '%.0f'), # degrees
                 'ws':  ('windSpeed',   '%.1f'), # m/s
                 'wg':  ('windGust',    '%.1f'), # m/s
                 'pa':  ('hourRain',    '%.2f'), # mm
                 'rr':  ('rainRate',    '%.2f'), # mm/hr
                 'uv':  ('UV',          '%.0f'), # uv index
                 'sr':  ('radiation',   '%.2f'), # W/m^2
                 'hui': ('inHumidity',  '%.0f'), # percent
                 'tei': ('inTemp',      '%.1f'), # C
                 'huo': ('extraHumid1', '%.0f'), # percent
                 'teo': ('extraTemp1',  '%.1f'), # C
                 'tes': ('soilTemp1',   '%.1f')  # C
                 }

    def __init__(self, queue, username, password, manager_dict,
                 server_url=_SERVER_URL, skip_upload=False,
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
                                           retry_wait=retry_wait,
                                           skip_upload=skip_upload)
        self.username = username
        self.password = password
        self.server_url = server_url

    def check_response(self, response):
        """Override, and check for wetter errors."""
        txt = response.read().decode().lower()
        if txt.find('"errorcode":"100"') != -1 or \
           txt.find('"errorcode":"101"') != -1 or \
           txt.find('"errorcode":"102"') != -1:
            raise weewx.restx.BadLogin(txt)
        elif txt.find('"status":"error"') != -1:
            raise weewx.restx.FailedPost("Server returned '%s'" % txt)

    def format_url(self, in_record):
        """Override, and format an URL for wetter"""
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

        url = "%s?%s" % (self.server_url, urlencode(values))
        if weewx.debug >= 2:
            logdbg('url: %s' % re.sub(r"passwort=[^\&]*", "passwort=XXX", url))
        return url


# Do direct testing of this extension like this:
#   PYTHONPATH=WEEWX_BINDIR python WEEWX_BINDIR/user/wetter.py
if __name__ == "__main__":
    import optparse

    weewx.debug = 2

    try:
        # WeeWX V4 logging
        weeutil.logger.setup('wetter', {})
    except NameError:
        # WeeWX V3 logging
        syslog.openlog('wetter', syslog.LOG_PID | syslog.LOG_CONS)
        syslog.setlogmask(syslog.LOG_UPTO(syslog.LOG_DEBUG))

    usage = """%prog --user USERNAME --pw PASSWORD [--version] [--help]"""

    parser = optparse.OptionParser(usage=usage)
    parser.add_option('--version', dest='version', action='store_true',
                      help='display driver version')
    parser.add_option('--user', metavar='USERNAME',
                      help='The username')
    parser.add_option('--pw', metavar='PASSWORD', help='Password for USERNAME')
    (options, args) = parser.parse_args()

    if options.version:
        print("wetter uploader version %s" % VERSION)
        exit(0)

    if options.user is None or options.pw is None:
        exit("You must supply both option --user and option --pw.")

    print("Using username '%s' and password '%s'" % (options.user, options.pw))
    q = queue.Queue()
    t = WetterThread(q, options.user, options.pw, manager_dict=None)
    t.start()
    q.put({'dateTime': int(time.time() + 0.5),
           'usUnits': weewx.US,
           'outTemp': 32.5,
           'inTemp': 75.8,
           'outHumidity': 24})
    q.put(None)
    t.join(20)

