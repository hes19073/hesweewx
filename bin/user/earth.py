# -*- coding: utf-8 -*-
# original belchertown.py by Pat O'Brien, August 19, 2018
# $Id: earth.py 1651 2018-09-01 12:10:37Z hes $
# Copyright 2017 Hartmut Schweidler
# Die Erde und ihre Beben


from __future__ import absolute_import

import datetime
import logging
import time
import calendar
import json
import os

import weewx
import weecfg
import weeutil.logger
import weeutil.weeutil
import weeutil.config
import weewx.units

from weewx.cheetahgenerator import SearchList
from weewx.tags import TimespanBinder
from weeutil.weeutil import TimeSpan

log = logging.getLogger(__name__)

# Print version in syslog for easier troubleshooting
VERSION = "1.1"

log.info("version %s", VERSION)


class getEarthquake(SearchList):
    def __init__(self, generator):
        SearchList.__init__(self, generator)

    def get_extension_list(self, timespan, db_lookup):
        """
        Parse the Earthquake data.
        """

        # Return right away if we're not going to use the earthquake.
        if self.generator.skin_dict['Extras']['earthquake_enabled'] == "0":
            # Return an empty SLE
            search_list_extension = { }
            return [search_list_extension]

        earthquake_file = "/home/weewx/archive/earthquake.json"
        earthquake_stale_timer = self.generator.skin_dict['Extras']['earthquake_stale']
        latitude = self.generator.config_dict['Station']['latitude']
        longitude = self.generator.config_dict['Station']['longitude']
        earthquake_maxradiuskm = self.generator.skin_dict['Extras']['earthquake_maxradiuskm']
        #Sample URL from Belchertown Weather: 
        #       http://earthquake.usgs.gov/fdsnws/event/1/query?limit=1&lat=53.605963&lon=11.341407&maxradiuskm=10000&format=geojson&nodata=204&minmag=2
        earthquake_url = "http://earthquake.usgs.gov/fdsnws/event/1/query?limit=1&lat=%s&lon=%s&maxradiuskm=%s&format=geojson&nodata=204&minmag=2" % (latitude, longitude, earthquake_maxradiuskm)
        earthquake_is_stale = False

        # Determine if the file exists and get it's modified time
        if os.path.isfile(earthquake_file):
            if (int(time.time()) - int(os.path.getmtime(earthquake_file))) > int(earthquake_stale_timer):
                earthquake_is_stale = True
        else:
            # File doesn't exist, download a new copy
            earthquake_is_stale = True

        # File is stale, download a new copy
        if earthquake_is_stale:
            import urllib.request, urllib.error, urllib.parse
            urllib.request.urlretrieve(earthquake_url, earthquake_file)

            log.info("New earthquake data downloaded to %s", earthquake_file)


        with open(earthquake_file, encoding="utf8") as read_file:
            eqdata= json.loads(read_file.read())

        eqtime = time.strftime( "%d.%m.%Y %H:%M %Z", time.localtime( eqdata["features"][0]["properties"]["time"] / 1000 ) )
        #eqtime = eqdata["features"][0]["properties"]["time"] / 1000
        equrl = eqdata["features"][0]["properties"]["url"]
        eqplace = eqdata["features"][0]["properties"]["place"]
        eqmag = eqdata["features"][0]["properties"]["mag"]
        eqlat = str( round( eqdata["features"][0]["geometry"]["coordinates"][0], 4 ) )
        eqlon = str( round( eqdata["features"][0]["geometry"]["coordinates"][1], 4 ) )
        eqtief = str( round( eqdata["features"][0]["geometry"]["coordinates"][2], 2 ) )

        # Put into a dictionary to return
        search_list_extension  = { 'earthquake_time': eqtime,
                                   'earthquake_url': equrl,
                                   'earthquake_place': eqplace,
                                   'earthquake_magnitude': eqmag,
                                   'earthquake_lat': eqlat,
                                   'earthquake_lon': eqlon,
                                   'earthquake_tief': eqtief }
        # Return our json data
        return [search_list_extension]
