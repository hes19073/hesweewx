# -*- coding: utf-8 -*-
# $Id: forecastAirQ.py 1651 2020-09-03 12:10:37Z hes $
# original by Pat O'Brien, August 19, 2018
# Copyright 2017 Hartmut Schweidler
# Die Erde Verschutzung
# forecast AirQualityIndex by AerisWeather


from __future__ import absolute_import

import datetime
import logging
import time
import json
import os

import weewx
import weecfg
import weeutil.logger

from weewx.cheetahgenerator import SearchList
from weewx.tags import TimespanBinder
from weeutil.weeutil import TimeSpan

log = logging.getLogger(__name__)


# Print version in syslog
VERSION = "3.0.1"

log.info("forecastAirQ version %s", VERSION)

class getAqi(SearchList):
    def __init__(self, generator):
        SearchList.__init__(self, generator)

    def get_extension_list(self, timespan, db_lookup):

        """ Download and parse the AQI data.
            von AerisWeather
            This is required for the majority of the theme to work
        """

        # Return right away if we're not going to use the aqiIndex.
        if self.generator.skin_dict['Extras']['aqi_enabled'] == "0":
            # Return an empty SLE
            search_list_extension = {
                                     'aqiIndex_updated': "",
                                     'aqiIndex_pm25': "",
                                     'aqiIndex_pm10': "",
                                    }

            return [search_list_extension]


        aqiIndex_file = "/home/weewx/archive/aeris_aqi.json"
        #aqiIndex_json_url = "/home/weewx/archive/aerisIndex.json"
        aeris_id_key = self.generator.skin_dict['Extras']['aeris_id_key']
        aeris_secret_key = self.generator.skin_dict['Extras']['aeris_secret_key']
        latitude = self.generator.config_dict['Station']['latitude']
        longitude = self.generator.config_dict['Station']['longitude']
        aqiIndex_stale_timer = self.generator.skin_dict['Extras']['aqiIndex_stale']
        aqiIndex_url = "https://api.aerisapi.com/airquality/%s,%s?client_id=%s&client_secret=%s" % (latitude, longitude, aeris_id_key, aeris_secret_key)

        aqiIndex_is_stale = False

        # Determine if the file exists and get it's modified time
        if os.path.isfile(aqiIndex_file):
            if (int(time.time()) - int(os.path.getmtime(aqiIndex_file))) > int(aqiIndex_stale_timer):
                aqiIndex_is_stale = True
        else:
            # File doesn't exist, download a new copy
            aqiIndex_is_stale = True

        # File is stale, download a new copy
        if aqiIndex_is_stale:
            import urllib.request, urllib.error, urllib.parse
            urllib.request.urlretrieve(aqiIndex_url, aqiIndex_file)

            log.info("New AerisWeather aqiIndex data downloaded to %s", aqiIndex_file)

        with open(aqiIndex_file, encoding="utf8") as read_file:
            data = json.loads(read_file.read())

        sxtime = data['response'][0]['periods'][0]['timestamp']
        sxo3 = data['response'][0]['periods'][0]['pollutants'][0]['valueUGM3']
        sxpm25 = data['response'][0]['periods'][0]['pollutants'][1]['valueUGM3']
        sxpm10 = data['response'][0]['periods'][0]['pollutants'][2]['valueUGM3']
        sxco = data['response'][0]['periods'][0]['pollutants'][3]['valueUGM3']
        sxno2 = data['response'][0]['periods'][0]['pollutants'][4]['valueUGM3']
        sxso2 = data['response'][0]['periods'][0]['pollutants'][5]['valueUGM3']


        # Put into a dictionary to return
        search_list_extension  = {
                                  'aqiIndex_updated': sxtime,
                                  'aqiIndex_o3': sxo3,
                                  'aqiIndex_pm10': sxpm10,
                                  'aqiIndex_pm25': sxpm25,
                                  'aqiIndex_co': sxco,
                                  'aqiIndex_no2': sxno2,
                                  'aqiIndex_so2': sxso2,
                                 }

        # Return our json data
        return [search_list_extension]



