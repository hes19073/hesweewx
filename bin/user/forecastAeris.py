# -*- coding: utf-8 -*-
# $Id: forecastAreis.py 1651 2019-05-04 12:10:37Z hes $
# original by Pat O'Brien, August 19, 2018
# Copyright 2020 Hartmut Schweidler
#
# Wetter Prognose by AerisWeather
""" in skin.conf
    [Extras]
        # forecastAeris ny aerisWeather
        forecast_enabled = 0

        # getAeris
        forecast_provider = aeris
        forecast_api_id =
        forecast_api_secret
        forecast_stale = 3450
        # forecast_aeris_limit =
        forecast_lang = de
        forecast_units = si

"""

from __future__ import absolute_import

import datetime
import logging
import time
import calendar
import json
import os

import weewx
import weecfg
import weeutil.weeutil
import weeutil.logger
import weewx.units

from weewx.cheetahgenerator import SearchList
from weewx.tags import TimespanBinder
from weeutil.weeutil import TimeSpan

log = logging.getLogger(__name__)

# Print version in syslog
VERSION = "3.0.1"

log.info("Forcast AerisWeather version %s", VERSION)

class getAeris(SearchList):
    def __init__(self, generator):
        SearchList.__init__(self, generator)

    def get_extension_list(self, timespan, db_lookup):

        """ Download and parse the Forecast data.
            von AerisWeather
            This is required for the majority of the theme to work
        """
        # Setup label dict for text and titles
        try:
            d = self.generator.skin_dict['Labels']['Generic']
        except KeyError:
            d = {}
        label_dict = weeutil.weeutil.KeyDict(d)

        # Setup database manager
        binding = self.generator.config_dict['StdReport'].get('data_binding', 'wx_binding')
        manager = self.generator.db_binder.get_manager(binding)

        # Find the right HTML ROOT
        if 'HTML_ROOT' in self.generator.skin_dict:
            html_root = os.path.join(self.generator.config_dict['WEEWX_ROOT'],
                                      self.generator.skin_dict['HTML_ROOT'])
        else:
            html_root = os.path.join(self.generator.config_dict['WEEWX_ROOT'],
                                      self.generator.config_dict['StdReport']['HTML_ROOT'])


        # Return right away if we're not going to use the forecast.
        if self.generator.skin_dict['Extras']['forecast_enabled'] == "0":
            # Return an empty SLE
            search_list_extension = {
                                    'forecast_updated': '',
                                    'forecastHTML' : '',
                                    }

            return [search_list_extension]
        """
        Forecast Data
        """
        forecast_provider = self.generator.skin_dict['Extras']['forecast_provider']
        forecast_file = "/home/weewx/archive/forecastAeris.json"
        forecast_api_id = self.generator.skin_dict['Extras']['forecast_api_id']
        forecast_api_secret = self.generator.skin_dict['Extras']['forecast_api_secret']
        forecast_units = self.generator.skin_dict['Extras']['forecast_units'].lower()
        latitude = self.generator.config_dict['Station']['latitude']
        longitude = self.generator.config_dict['Station']['longitude']
        forecast_stale_timer = self.generator.skin_dict['Extras']['forecast_stale']
        forecast_is_stale = False

        def aeris_coded_weather(data):
            # https://www.aerisweather.com/support/docs/api/reference/weather-codes/
            output = ""
            coverage_code = data.split(":")[0]
            intensity_code = data.split(":")[1]
            weather_code = data.split(":")[2]

            cloud_dict = {
                "CL": label_dict["forecast_cloud_code_CL"],
                "FW": label_dict["forecast_cloud_code_FW"],
                "SC": label_dict["forecast_cloud_code_SC"],
                "BK": label_dict["forecast_cloud_code_BK"],
                "OV": label_dict["forecast_cloud_code_OV"],
            }

            coverage_dict = {
                "AR": label_dict["forecast_coverage_code_AR"],
                "BR": label_dict["forecast_coverage_code_BR"],
                "C": label_dict["forecast_coverage_code_C"],
                "D": label_dict["forecast_coverage_code_D"],
                "FQ": label_dict["forecast_coverage_code_FQ"],
                "IN": label_dict["forecast_coverage_code_IN"],
                "IS": label_dict["forecast_coverage_code_IS"],
                "L": label_dict["forecast_coverage_code_L"],
                "NM": label_dict["forecast_coverage_code_NM"],
                "O": label_dict["forecast_coverage_code_O"],
                "PA": label_dict["forecast_coverage_code_PA"],
                "PD": label_dict["forecast_coverage_code_PD"],
                "S": label_dict["forecast_coverage_code_S"],
                "SC": label_dict["forecast_coverage_code_SC"],
                "VC": label_dict["forecast_coverage_code_VC"],
                "WD": label_dict["forecast_coverage_code_WD"],
            }

            intensity_dict = {
                "VL": label_dict["forecast_intensity_code_VL"],
                "L": label_dict["forecast_intensity_code_L"],
                "H": label_dict["forecast_intensity_code_H"],
                "VH": label_dict["forecast_intensity_code_VH"],
            }

            weather_dict = {
                "A": label_dict["forecast_weather_code_A"],
                "BD": label_dict["forecast_weather_code_BD"],
                "BN": label_dict["forecast_weather_code_BN"],
                "BR": label_dict["forecast_weather_code_BR"],
                "BS": label_dict["forecast_weather_code_BS"],
                "BY": label_dict["forecast_weather_code_BY"],
                "F": label_dict["forecast_weather_code_F"],
                "FR": label_dict["forecast_weather_code_FR"],
                "H": label_dict["forecast_weather_code_H"],
                "IC": label_dict["forecast_weather_code_IC"],
                "IF": label_dict["forecast_weather_code_IF"],
                "IP": label_dict["forecast_weather_code_IP"],
                "K": label_dict["forecast_weather_code_K"],
                "L": label_dict["forecast_weather_code_L"],
                "R": label_dict["forecast_weather_code_R"],
                "RW": label_dict["forecast_weather_code_RW"],
                "RS": label_dict["forecast_weather_code_RS"],
                "SI": label_dict["forecast_weather_code_SI"],
                "WM": label_dict["forecast_weather_code_WM"],
                "S": label_dict["forecast_weather_code_S"],
                "SW": label_dict["forecast_weather_code_SW"],
                "T": label_dict["forecast_weather_code_T"],
                "UP": label_dict["forecast_weather_code_UP"],
                "VA": label_dict["forecast_weather_code_VA"],
                "WP": label_dict["forecast_weather_code_WP"],
                "ZF": label_dict["forecast_weather_code_ZF"],
                "ZL": label_dict["forecast_weather_code_ZL"],
                "ZR": label_dict["forecast_weather_code_ZR"],
                "ZY": label_dict["forecast_weather_code_ZY"],
            }

            # Check if the weather_code is in the cloud_dict and use that if it's there. If not then it's a combined weather code.
            if weather_code in cloud_dict:
                return cloud_dict[weather_code];
            else:
                # Add the coverage if it's present, and full observation forecast is requested
                if coverage_code:
                    output += coverage_dict[coverage_code] + " : "
                # Add the intensity if it's present
                if intensity_code:
                    output += intensity_dict[intensity_code] + " : "
                # Weather output
                output += weather_dict[weather_code];
            return output

        def aeris_icon(data):
            # https://www.aerisweather.com/support/docs/api/reference/icon-list/
            icon_name = data.split(".")[0]; # Remove .png

            icon_dict = {
                "blizzard": "snow",
                "blizzardn": "snow",
                "blowingsnow": "snow",
                "blowingsnown": "snow",
                "clear": "clear-day",
                "clearn": "clear-night",
                "cloudy": "cloudy",
                "cloudyn": "cloudy",
                "cloudyw": "cloudy",
                "cloudywn": "cloudy",
                "cold": "clear-day",
                "coldn": "clear-night",
                "drizzle": "rain",
                "drizzlen": "rain",
                "dust": "fog",
                "dustn": "fog",
                "fair": "clear-day",
                "fairn": "clear-night",
                "drizzlef": "rain",
                "fdrizzlen": "rain",
                "flurries": "sleet",
                "flurriesn": "sleet",
                "flurriesw": "sleet",
                "flurrieswn": "sleet",
                "fog": "fog",
                "fogn": "fog",
                "freezingrain": "rain",
                "freezingrainn": "rain",
                "hazy": "fog",
                "hazyn": "fog",
                "hot": "clear-day",
                "N/A ": "unknown",
                "mcloudy": "partly-cloudy-day",
                "mcloudyn": "partly-cloudy-night",
                "mcloudyr": "rain",
                "mcloudyrn": "rain",
                "mcloudyrw": "rain",
                "mcloudyrwn": "rain",
                "mcloudys": "snow",
                "mcloudysn": "snow",
                "mcloudysf": "snow",
                "mcloudysfn": "snow",
                "mcloudysfw": "snow",
                "mcloudysfwn": "snow",
                "mcloudysw": "partly-cloudy-day",
                "mcloudyswn": "partly-cloudy-night",
                "mcloudyt": "thunderstorm",
                "mcloudytn": "thunderstorm",
                "mcloudytw": "thunderstorm",
                "mcloudytwn": "thunderstorm",
                "mcloudyw": "partly-cloudy-day",
                "mcloudywn": "partly-cloudy-night",
                "na": "unknown",
                "pcloudy": "partly-cloudy-day",
                "pcloudyn": "partly-cloudy-night",
                "pcloudyr": "rain",
                "pcloudyrn": "rain",
                "pcloudyrw": "rain",
                "pcloudyrwn": "rain",
                "pcloudys": "snow",
                "pcloudysn": "snow",
                "pcloudysf": "snow",
                "pcloudysfn": "snow",
                "pcloudysfw": "snow",
                "pcloudysfwn": "snow",
                "pcloudysw": "partly-cloudy-day",
                "pcloudyswn": "partly-cloudy-night",
                "pcloudyt": "thunderstorm",
                "pcloudytn": "thunderstorm",
                "pcloudytw": "thunderstorm",
                "pcloudytwn": "thunderstorm",
                "pcloudyw": "partly-cloudy-day",
                "pcloudywn": "partly-cloudy-night",
                "rain": "rain",
                "rainn": "rain",
                "rainandsnow": "rain",
                "rainandsnown": "rain",
                "raintosnow": "rain",
                "raintosnown": "rain",
                "rainw": "rain",
                "rainw": "rain",
                "showers": "rain",
                "showersn": "rain",
                "showersw": "rain",
                "showersw": "rain",
                "sleet": "sleet",
                "sleetn": "sleet",
                "sleetsnow": "sleet",
                "sleetsnown": "sleet",
                "smoke": "fog",
                "smoken": "fog",
                "snow": "snow",
                "snown": "snow",
                "snoww": "snow",
                "snowwn": "snow",
                "snowshowers": "snow",
                "snowshowersn": "snow",
                "snowshowersw": "snow",
                "snowshowerswn": "snow",
                "snowtorain": "snow",
                "snowtorainn": "snow",
                "sunny": "clear-day",
                "sunnyn": "clear-night",
                "sunnyw": "partly-cloudy-day",
                "sunnywn": "partly-cloudy-night",
                "tstorm": "thunderstorm",
                "tstormn": "thunderstorm",
                "tstorms": "thunderstorm",
                "tstormsn": "thunderstorm",
                "tstormsw": "thunderstorm",
                "tstormswn": "thunderstorm",
                "wind": "wind",
                "wind": "wind",
                "wintrymix": "sleet",
                "wintrymixn": "sleet",
            }
            return icon_dict[icon_name]

        # Quelle
        forecast_url = "https://api.aerisapi.com/forecasts/%s,%s?&format=json&filter=day&limit=7&client_id=%s&client_secret=%s" % (latitude, longitude, forecast_api_id, forecast_api_secret)

        # Determine if the file exists and get it's modified time
        if os.path.isfile(forecast_file):
            if (int(time.time()) - int(os.path.getmtime(forecast_file))) > int(forecast_stale_timer):
                forecast_is_stale = True
        else:
            # File doesn't exist, download a new copy
            forecast_is_stale = True

        # File is stale, download a new copy
        if forecast_is_stale:
            try:
                try:
                    # Python 3
                    from urllib.request import Request, urlopen
                except ImportError:
                    # Python 2
                    from urllib2 import Request, urlopen
                user_agent = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_4; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.472.63 Safari/534.3'
                headers = { 'User-Agent' : user_agent }

                # Forecast
                req = Request( forecast_url, None, headers )
                response = urlopen( req )
                forecast_page = response.read()
                response.close()

                try:
                    forecast_file_result = json.dumps( {"timestamp": int(time.time()), "forecast": [json.loads(forecast_page)]} )
                except:
                    forecast_file_result = json.dumps( {"timestamp": int(time.time()), "forecast": [json.loads(forecast_page.decode('utf-8'))]} )

            except Exception as error:
                raise Warning( "Error downloading forecast data. Check the URL in your configuration and try again. You are trying to use URL: %s, and the error is: %s" % ( forecast_url, error ) )

            # Save forecast data to file. w+ creates the file if it doesn't exist, and truncates the file and re-writes it everytime
            try:
                with open( forecast_file, 'wb+' ) as file:
                    # Python 2/3
                    try:
                        file.write( forecast_file_result.encode('utf-8') )
                    except:
                        file.write( forecast_file_result )

                    log.info( "New forecast file downloaded to %s" % forecast_file )

            except IOError as e:
                raise Warning( "Error writing forecast info to %s. Reason: %s" % ( forecast_file, e) )

        # Process the forecast file
        with open( forecast_file, "r" ) as read_file:
            data = json.load( read_file )


        html_output = ""
        #forecast_updated = time.strftime("%d.%m.%Y %H:%M", time.localtime(data["forecast"][0]["response"][0]["periods"][0]["timestamp"]))
        forecast_updated = time.strftime("%d.%m.%Y %H:%M", time.localtime(data["timestamp"]))
        for daily_data in data["forecast"][0]["response"][0]["periods"]:

            image_url = "xicons/AerisIcons/" + daily_data['icon']
            condition_text = aeris_coded_weather(daily_data["weatherPrimaryCoded"])
            #condition_text = daily_data["weatherPrimary"]
            # Build html
            if time.strftime( "%a %m/%d", time.localtime( daily_data["timestamp"] ) ) == time.strftime( "%a %m/%d", time.localtime( time.time() ) ):
                # If the time in the darksky output is today, do not add border-left and say "Today" in the header
                output = '<div class="col-sm-1-5 wuforecast">'
                weekday = "Heute"
            else:
                output = '<div class="col-sm-1-5 wuforecast border-left">'
                weekday = time.strftime( "%a: %d.%m.%Y", time.localtime( daily_data["timestamp"] ) )

            output += '<span id="weekday">' + weekday + '</span>'
            output += '<br>'
            output += '<div class="forecast-conditions">'
            output += '<img id="icon" src="'+image_url+'">'
            output += '<br>'
            output += '<span class="forecast-condition-text">'
            output += condition_text
            output += '</span>'
            output += '</div>'
            output += '<span class="hes1_valhi">'+str(int(daily_data["maxTempC"])) + '&deg;C</span> | <span class="hes1_vallo">'+str(int(daily_data["minTempC"]))+ '&deg;C</span>'
            output += '<br><br>'
            output += '<div class="forecast-precip">'
            if int(daily_data["pop"]) > 0:
                output += 'Niederschlag: <span> ' + str(int(daily_data["pop"])) + ' </span>%'
                if int(daily_data["snowCM"]) > 0:
                    output += '<div class="snow-precip">'
                    output += '<img src="xicons/snowflake-icon-15px.png"> <span>'+ str(int(daily_data["snowCM"])) + '</span> cm'
                    output += '</div>'

                elif int(daily_data["precipMM"]) > 0:
                    output += '<div class="rain-precip">'
                    output += '<img src="xicons/raindrop.png"><span >'+ str(int(daily_data["precipMM"])) + ' </span> mm'
                    output += '</div>'

            else:
                output += 'Niederschlag: <span > 0%</span>'

            output += '</div>'
            output += '<div class="forecast-wind">'
            output += '<img src="xicons/strong-wind.svg"><span> aus: <b>' + daily_data["windDir"] + '</b></span><br>'
            output += '<span> '+ str(int(daily_data["windSpeedKPH"])) + ' bis ' + str(int(daily_data["windGustKPH"])) + ' km/h </span><br>'
            output += '<img src="xicons/strong-wind.svg"><span>in 80 m:  <b>' + daily_data["windDir80m"] + '</b></span><br>'
            output += '<span> '+ str(int(daily_data["windSpeed80mKPH"])) + ' bis ' + str(int(daily_data["windGust80mKPH"])) + ' km/h </span>'
            output += '</div> <!-- end wind --> '
            output += '</div> <!-- end aeris forecast -->'
            output += '<br>'
            # Add to the output
            html_output += output

        # Put into a dictionary to return
        search_list_extension  = {
                                  'forecast_updated': forecast_updated,
                                  'forecastHTML' : html_output,
                                 }
        # Finally, return our extension as a list:
        return [search_list_extension]


