# -*- coding: utf-8 -*-
# $Id: iss.py 1651 2018-09-19 12:10:37Z hes $
# Copyright 2017 Hartmut Schweidler
# Die Erde und ihre Beben

import datetime
import time
import calendar
import json
import os
import syslog

import weewx
import weecfg

from weewx.cheetahgenerator import SearchList
from weewx.tags import TimespanBinder
from weeutil.weeutil import TimeSpan

def logmsg(level, msg):
    syslog.syslog(level, 'ISS watch Extension: %s' % msg)

def logdbg(msg):
    logmsg(syslog.LOG_DEBUG, msg)

def loginf(msg):
    logmsg(syslog.LOG_INFO, msg)

def logerr(msg):
    logmsg(syslog.LOG_ERR, msg)

# Print version in syslog for easier troubleshooting
VERSION = "0.3"

loginf("ISS - version %s" % VERSION)

class getdata(SearchList):
    def __init__(self, generator):
        SearchList.__init__(self, generator)

    def get_extension_list(self, timespan, db_lookup):

        """ ISS watch data from
            http://api.open-notify.org/iss-pass.json?lat=53.69&lon=11.33
            get Data
        """

        # Return right away if we're not going to use the earthquake.
        if self.generator.skin_dict['Extras']['iss_enabled'] == "0":
            # Return an empty SLE
            search_list_extension = { }
            return [search_list_extension]

        iss_file = "/home/weewx/archive/iss_data.json"
        latitude = self.generator.config_dict['Station']['latitude']
        longitude = self.generator.config_dict['Station']['longitude']
        iss_stale_timer = self.generator.skin_dict['Extras']['iss_stale']
        iss_url = "http://api.open-notify.org/iss-pass.json?lat=%s&lon=%s" % (latitude, longitude)

        iss_is_stale = False

        # Determine if the file exists and get it's modified time
        if os.path.isfile(iss_file):
            if (int(time.time()) - int(os.path.getmtime(iss_file))) > int(iss_stale_timer):
                iss_is_stale = True
        else:
            # File doesn't exist, download a new copy
            iss_is_stale = True

        # File is stale, download a new copy
        if iss_is_stale:
            import urllib.request, urllib.error, urllib.parse
            urllib.request.urlretrieve(iss_url, iss_file)

            loginf( "New ISS data downloaded to %s" % iss_file )

        with open(iss_file, encoding="utf8") as read_file:
            issdata = json.loads(read_file.read())

        # latitude = issdata['request']['latitude']
        # longitude = issdata['request']['longitude']
        #risetime_y = datetime.datetime.fromtimestamp(issdata['response'][0]['risetime'])
        iss_time_y = time.strftime("%d.%m.%Y, %H:%M", time.localtime(issdata['response'][0]['risetime']))
        duration_y = issdata['response'][0]['duration']
        iss_time_n = time.strftime("%d.%m.%Y, %H:%M", time.localtime(issdata['response'][1]['risetime']))
        duration_n = issdata['response'][1]['duration']
        # print "The next ISS pass for %s %s is %s for %s seconds" %
        #            (latitude, longitude, risetime_y, duration_y)
        # sample output:

        # The next ISS pass for 41.4984174 -81.6937287 is 2017-12-28 05:08:31 for 489 seconds
        # Build the search list with the new values
        search_list_extension = {
                                 'iss_time': iss_time_y,
                                 'duration': duration_y,
                                 'iss_time_n': iss_time_n,
                                 'duration_n': duration_n,
                                }

        # Finally, return our extension as a list:
        return [search_list_extension]



