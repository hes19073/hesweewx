# -*- coding: utf-8 -*-
# $Id: dwdpollen.py 1651 2019-03-03 12:10:37Z hes $
# original by Pat O'Brien, August 19, 2018
# Copyright 2019 Hartmut Schweidler
# DDW Pollen Flug

import datetime
import time
import calendar
import json
import os
import syslog
import re

import weewx
import weecfg
import weeutil.weeutil

from weewx.cheetahgenerator import SearchList
from weewx.tags import TimespanBinder
from weeutil.weeutil import TimeSpan

def logmsg(level, msg):
    syslog.syslog(level, 'DWD Pollen Vorhersage Extension: %s' % msg)

def logdbg(msg):
    logmsg(syslog.LOG_DEBUG, msg)

def loginf(msg):
    logmsg(syslog.LOG_INFO, msg)

def logerr(msg):
    logmsg(syslog.LOG_ERR, msg)

# Print version in syslog
VERSION = "3.0.1"

loginf("version %s" % VERSION)


class DWD(SearchList):
    def __init__(self, generator):
        SearchList.__init__(self, generator)

    def get_extension_list(self, timespan, db_lookup):

        """ Download and parse the pollen data.
            von DWD
            This is required for the majority of the theme to work
        """

        # Return right away if we're not going to use the forecast.
        if self.generator.skin_dict['Extras']['pollen_enabled'] == "0":
            # Return an empty SLE
            search_list_extension = { }

            return [search_list_extension]


        pollen_file = "/home/weewx/archive/pollen.json"
        latitude = self.generator.config_dict['Station']['latitude']
        longitude = self.generator.config_dict['Station']['longitude']
        pollen_stale_timer = self.generator.skin_dict['Extras']['pollen_stale']
        pollen_url = "https://opendata.dwd.de/climate_environment/health/alerts/s31fg.json"

        pollen_is_stale = False

        # Determine if the file exists and get it's modified time
        if os.path.isfile(pollen_file):
            if (int(time.time()) - int(os.path.getmtime(pollen_file))) > int(pollen_stale_timer):
                pollen_is_stale = True
        else:
            # File doesn't exist, download a new copy
            pollen_is_stale = True

        """Generate a Pollen from DWD using data from 11:00 (39200 12=43200s).  If the
        current time is before 11:00, use the data from the previous day."""
        now = time.time()
        ts = weeutil.weeutil.startOfDay(now) + 43300
        if now < ts:
            ts -= 86400
            logdbg('DWD: Pollen was already calculated for %s' %
                   (weeutil.weeutil.timestamp_to_string(ts)))
            pollen_is_stale = False

        # File is stale, download a new copy
        if pollen_is_stale:
            import urllib.request, urllib.error, urllib.parse
            urllib.request.urlretrieve(pollen_url, pollen_file)

            loginf("New DWD Pollenflug data downloaded to %s" % pollen_file)

        with open(pollen_file, encoding="utf8") as read_file:
            data = json.loads(read_file.read())

        # read pollen data
        last_up = data['last_update']
        last_date = last_up
        next_up = data['next_update']
        next_date = next_up
        import re
        last_date = re.sub(r' Uhr$', '', last_date)
        format = '%Y-%m-%d %H:%M'
        las_up = time.mktime(datetime.datetime.strptime(last_date, format).timetuple())
        #syslog.syslog(syslog.LOG_INFO, "Pollen-Uhr: LAST Generated in %.2f seconds" % las_up)

        next_date = re.sub(r' Uhr$', '', next_date)
        format = '%Y-%m-%d %H:%M'
        new_up = time.mktime(datetime.datetime.strptime(next_date, format).timetuple())
        #syslog.syslog(syslog.LOG_INFO, "Pollen-Uhr: NEW  Generated in %.2f seconds" % new_up)


        for obj in data['content']:
            heo = int(obj['region_id'])
            if heo == 20:
                region_id = obj['region_id']
                region = obj['region_name']
                hasel_h = obj['Pollen']['Hasel']['today']
                hasel_m = obj['Pollen']['Hasel']['tomorrow']
                hasel_n = obj['Pollen']['Hasel']['dayafter_to']
                erle_h = obj['Pollen']['Erle']['today']
                erle_m = obj['Pollen']['Erle']['tomorrow']
                erle_n = obj['Pollen']['Erle']['dayafter_to']
                birke_h = obj['Pollen']['Birke']['today']
                birke_m = obj['Pollen']['Birke']['tomorrow']
                birke_n = obj['Pollen']['Birke']['dayafter_to']
                graeser_h = obj['Pollen']['Graeser']['today']
                graeser_m = obj['Pollen']['Graeser']['tomorrow']
                graeser_n = obj['Pollen']['Graeser']['dayafter_to']
                roggen_h = obj['Pollen']['Roggen']['today']
                roggen_m = obj['Pollen']['Roggen']['tomorrow']
                roggen_n = obj['Pollen']['Roggen']['dayafter_to']
                esche_h = obj['Pollen']['Esche']['today']
                esche_m = obj['Pollen']['Esche']['tomorrow']
                esche_n = obj['Pollen']['Esche']['dayafter_to']
                beifuss_h = obj['Pollen']['Beifuss']['today']
                beifuss_m = obj['Pollen']['Beifuss']['tomorrow']
                beifuss_n = obj['Pollen']['Beifuss']['dayafter_to']
                ambrosia_h = obj['Pollen']['Ambrosia']['today']
                ambrosia_m = obj['Pollen']['Ambrosia']['tomorrow']
                ambrosia_n = obj['Pollen']['Ambrosia']['dayafter_to']


        # Put into a dictionary to return
        search_list_extension  = {
                                  'las_up' : las_up,
                                  'new_up' : new_up,
                                  'region_id': region_id,
                                  'region': region,
                                  'hasel_h': hasel_h,
                                  'hasel_m': hasel_m,
                                  'hasel_n': hasel_n,
                                  'erle_h': erle_h,
                                  'erle_m': erle_m,
                                  'erle_n': erle_n,
                                  'birke_h': birke_h,
                                  'birke_m' : birke_m,
                                  'birke_n': birke_n,
                                  'graeser_h': graeser_h,
                                  'graeser_m': graeser_m,
                                  'graeser_n': graeser_n,
                                  'roggen_h': roggen_h,
                                  'roggen_m': roggen_m,
                                  'roggen_n': roggen_n,
                                  'esche_h': esche_h,
                                  'esche_m' : esche_m,
                                  'esche_n': esche_n,
                                  'beifuss_h': beifuss_h,
                                  'beifuss_m': beifuss_m,
                                  'beifuss_n': beifuss_n,
                                  'ambrosia_h': ambrosia_h,
                                  'ambrosia_m': ambrosia_m,
                                  'ambrosia_n': ambrosia_n,
                                 }

        # Return our json data
        return [search_list_extension]

