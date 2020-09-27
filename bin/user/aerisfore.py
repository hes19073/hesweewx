# -*- coding: utf-8 -*-
# original belchertown.py by Pat O'Brien, August 19, 2018
# $Id: aerisfore.py  2020-06-20 09:10:37Z hes $
# Copyright 2020 Hartmut Schweidler
# Wetter by Aries

from __future__ import with_statement
from __future__ import print_function  # Python 2/3 compatibility
from __future__ import absolute_import

import datetime
import logging
import time
import calendar
import json
import os
import locale

import weewx
import weecfg
import weeutil.logger
import weeutil.weeutil
import weeutil.config
import weewx.units

from weewx.cheetahgenerator import SearchList
from weewx.tags import TimespanBinder
from weeutil.weeutil import TimeSpan

try:
    from weeutil.config import search_up
except:
    # Pass here because chances are we have an old version of weewx which will get caught below.
    pass
try:
    # weewx 4
    from weeutil.config import accumulateLeaves
except:
    # weewx 3
    from weeutil.weeutil import accumulateLeaves

# Check weewx version. Many things like search_up, weeutil.weeutil.KeyDict (label_dict) are from 3.9
if weewx.__version__ < "3.9":
    raise weewx.UnsupportedFeature("weewx 3.9 and newer is required, found %s" % weewx.__version__)

try:
    # Test for new-style weewx v4 logging by trying to import weeutil.logger
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
        syslog.syslog(level, 'Belchertown Extension: %s' % msg)

    def logdbg(msg):
        logmsg(syslog.LOG_DEBUG, msg)

    def loginf(msg):
        logmsg(syslog.LOG_INFO, msg)

    def logerr(msg):
        logmsg(syslog.LOG_ERR, msg)

# Print version in syslog for easier troubleshooting
VERSION = "1.2.1"

log.info("version %s", VERSION)


class getAeris(SearchList):
    def __init__(self, generator):
        SearchList.__init__(self, generator)

    def get_extension_list(self, timespan, db_lookup):
        """
        Parse the Aeris data.
        """

        # Look for the debug flag which can be used to show more logging
        weewx.debug = int(self.generator.config_dict.get('debug', 0))

        # Setup label dict for text and titles
        try:
            d = self.generator.skin_dict['LabelsAeris']['Generic']
        except KeyError:
            d = {}
        label_dict = weeutil.weeutil.KeyDict(d)

        # Setup database manager
        binding = self.generator.config_dict['StdReport'].get('data_binding', 'wx_binding')
        manager = self.generator.db_binder.get_manager(binding)

        #belchertown_debug = self.generator.skin_dict['Extras'].get('belchertown_debug', 0)

        # Find the right HTML ROOT
        if 'HTML_ROOT' in self.generator.skin_dict:
            html_root = os.path.join(self.generator.config_dict['WEEWX_ROOT'],
                                      self.generator.skin_dict['HTML_ROOT'])
        else:
            html_root = os.path.join(self.generator.config_dict['WEEWX_ROOT'],
                                      self.generator.config_dict['StdReport']['HTML_ROOT'])
        """
        Forecast Data
        """
        if self.generator.skin_dict['Extras']['aeris_enabled'] == "1" and self.generator.skin_dict['Extras']['aeris_api_id'] != "" or 'aeris_dev_file' in self.generator.skin_dict['Extras']:

            aeris_provider = self.generator.skin_dict['Extras']['aeris_provider']
            aeris_file = "/home/weewx/archive/aeris_forecast.json"
            aeris_api_id = self.generator.skin_dict['Extras']['aeris_api_id']
            aeris_api_secret = self.generator.skin_dict['Extras']['aeris_api_secret']
            aeris_units = self.generator.skin_dict['Extras']['aeris_units'].lower()
            latitude = self.generator.config_dict['Station']['latitude']
            longitude = self.generator.config_dict['Station']['longitude']
            aeris_stale_timer = self.generator.skin_dict['Extras']['aeris_stale']
            aeris_is_stale = False

            def aeris_coded_weather( data ):
                # https://www.aerisweather.com/support/docs/api/reference/weather-codes/
                output = ""
                coverage_code = data.split(":")[0]
                intensity_code = data.split(":")[1]
                weather_code = data.split(":")[2]

                cloud_dict = {
                    "CL": label_dict["aeris_cloud_code_CL"],
                    "FW": label_dict["aeris_cloud_code_FW"],
                    "SC": label_dict["aeris_cloud_code_SC"],
                    "BK": label_dict["aeris_cloud_code_BK"],
                    "OV": label_dict["aeris_cloud_code_OV"]
                }

                coverage_dict = {
                    "AR": label_dict["aeris_coverage_code_AR"],
                    "BR": label_dict["aeris_coverage_code_BR"],
                    "C": label_dict["aeris_coverage_code_C"],
                    "D": label_dict["aeris_coverage_code_D"],
                    "FQ": label_dict["aeris_coverage_code_FQ"],
                    "IN": label_dict["aeris_coverage_code_IN"],
                    "IS": label_dict["aeris_coverage_code_IS"],
                    "L": label_dict["aeris_coverage_code_L"],
                    "NM": label_dict["aeris_coverage_code_NM"],
                    "O": label_dict["aeris_coverage_code_O"],
                    "PA": label_dict["aeris_coverage_code_PA"],
                    "PD": label_dict["aeris_coverage_code_PD"],
                    "S": label_dict["aeris_coverage_code_S"],
                    "SC": label_dict["aeris_coverage_code_SC"],
                    "VC": label_dict["aeris_coverage_code_VC"],
                    "WD": label_dict["aeris_coverage_code_WD"]
                }

                intensity_dict = {
                    "VL": label_dict["aeris_intensity_code_VL"],
                    "L": label_dict["aeris_intensity_code_L"],
                    "H": label_dict["aeris_intensity_code_H"],
                    "VH": label_dict["aeris_intensity_code_VH"]
                }

                weather_dict = {
                    "A": label_dict["aeris_weather_code_A"],
                    "BD": label_dict["aeris_weather_code_BD"],
                    "BN": label_dict["aeris_weather_code_BN"],
                    "BR": label_dict["aeris_weather_code_BR"],
                    "BS": label_dict["aeris_weather_code_BS"],
                    "BY": label_dict["aeris_weather_code_BY"],
                    "F": label_dict["aeris_weather_code_F"],
                    "FR": label_dict["aeris_weather_code_FR"],
                    "H": label_dict["aeris_weather_code_H"],
                    "IC": label_dict["aeris_weather_code_IC"],
                    "IF": label_dict["aeris_weather_code_IF"],
                    "IP": label_dict["aeris_weather_code_IP"],
                    "K": label_dict["aeris_weather_code_K"],
                    "L": label_dict["aeris_weather_code_L"],
                    "R": label_dict["aeris_weather_code_R"],
                    "RW": label_dict["aeris_weather_code_RW"],
                    "RS": label_dict["aeris_weather_code_RS"],
                    "SI": label_dict["aeris_weather_code_SI"],
                    "WM": label_dict["aeris_weather_code_WM"],
                    "S": label_dict["aeris_weather_code_S"],
                    "SW": label_dict["aeris_weather_code_SW"],
                    "T": label_dict["aeris_weather_code_T"],
                    "UP": label_dict["aeris_weather_code_UP"],
                    "VA": label_dict["aeris_weather_code_VA"],
                    "WP": label_dict["aeris_weather_code_WP"],
                    "ZF": label_dict["aeris_weather_code_ZF"],
                    "ZL": label_dict["aeris_weather_code_ZL"],
                    "ZR": label_dict["aeris_weather_code_ZR"],
                    "ZY": label_dict["aeris_weather_code_ZY"]
                }

                # Check if the weather_code is in the cloud_dict and use that if it's there. If not then it's a combined weather code.
                if weather_code in cloud_dict:
                    return cloud_dict[weather_code];
                else:
                    # Add the coverage if it's present, and full observation forecast is requested
                    if coverage_code:
                        output += coverage_dict[coverage_code] + " "
                    # Add the intensity if it's present
                    if intensity_code:
                        output += intensity_dict[intensity_code] + " "
                    # Weather output
                    output += weather_dict[weather_code];
                return output

            def aeris_icon( data ):
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
                    "wintrymixn": "sleet"
                }
                return icon_dict[icon_name]


            if aeris_provider == "aeris":
                aeris_current_url = "https://api.aerisapi.com/observations/%s,%s?&format=json&filter=allstations&filter=metar&limit=1&client_id=%s&client_secret=%s" % ( latitude, longitude, aeris_api_id, aeris_api_secret )
                aeris_url = "https://api.aerisapi.com/forecasts/%s,%s?&format=json&filter=day&limit=7&client_id=%s&client_secret=%s" % ( latitude, longitude, aeris_api_id, aeris_api_secret )
                if self.generator.skin_dict['Extras']['aeris_alert_limit']:
                    aeris_alert_limit = self.generator.skin_dict['Extras']['aeris_alert_limit']
                    aeris_alerts_url = "https://api.aerisapi.com/alerts/%s,%s?&format=json&limit=%s&client_id=%s&client_secret=%s" % ( latitude, longitude, aeris_alert_limit, aeris_api_id, aeris_api_secret )
                else:
                    # Default to 1 alerts to show if the option is missing. Can go up to 10
                    aeris_alerts_url = "https://api.aerisapi.com/alerts/%s,%s?&format=json&limit=1&client_id=%s&client_secret=%s" % ( latitude, longitude, aeris_api_id, aeris_api_secret )
            elif aeris_provider == "darksky":
                aeris_lang = self.generator.skin_dict['Extras']['aeris_lang'].lower()
                aeris_url = "https://api.darksky.net/forecast/%s/%s,%s?units=%s&lang=%s" % ( aeris_api_secret, latitude, longitude, aeris_units, aeris_lang )

            # Determine if the file exists and get it's modified time
            if os.path.isfile( aeris_file ):
                if ( int( time.time() ) - int( os.path.getmtime( aeris_file ) ) ) > int( aeris_stale_timer ):
                    aeris_is_stale = True
            else:
                # File doesn't exist, download a new copy
                aeris_is_stale = True

            # File is stale, download a new copy
            if aeris_is_stale:
                try:
                    try:
                        # Python 3
                        from urllib.request import Request, urlopen
                    except ImportError:
                        # Python 2
                        from urllib2 import Request, urlopen
                    user_agent = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_4; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.472.63 Safari/534.3'
                    headers = { 'User-Agent' : user_agent }
                    if 'aeris_dev_file' in self.generator.skin_dict['Extras']:
                        # Hidden option to use a pre-downloaded forecast file rather than using API calls for no reason
                        dev_aeris_file = self.generator.skin_dict['Extras']['aeris_dev_file']
                        req = Request( dev_aeris_file, None, headers )
                        response = urlopen( req )
                        aeris_file_result = response.read()
                        response.close()
                    else:
                        if aeris_provider == "aeris":
                            # Current conditions
                            req = Request( aeris_current_url, None, headers )
                            response = urlopen( req )
                            current_page = response.read()
                            response.close()
                            # Forecast
                            req = Request( aeris_url, None, headers )
                            response = urlopen( req )
                            aeris_page = response.read()
                            response.close()
                            if self.generator.skin_dict['Extras']['aeris_alert_enabled'] == "1":
                                # Alerts
                                req = Request( aeris_alerts_url, None, headers )
                                response = urlopen( req )
                                alerts_page = response.read()
                                response.close()

                            # Combine all into 1 file
                            if self.generator.skin_dict['Extras']['aeris_alert_enabled'] == "1":
                                try:
                                    aeris_file_result = json.dumps( {"timestamp": int(time.time()), "current": [json.loads(current_page)], "forecast": [json.loads(aeris_page)], "alerts": [json.loads(alerts_page)]} )
                                except:
                                    aeris_file_result = json.dumps( {"timestamp": int(time.time()), "current": [json.loads(current_page.decode('utf-8'))], "forecast": [json.loads(aeris_page.decode('utf-8'))], "alerts": [json.loads(alerts_page.decode('utf-8'))]} )
                            else:
                                try:
                                    aeris_file_result = json.dumps( {"timestamp": int(time.time()), "current": [json.loads(current_page)], "forecast": [json.loads(aeris_page)]} )
                                except:
                                    aeris_file_result = json.dumps( {"timestamp": int(time.time()), "current": [json.loads(current_page.decode('utf-8'))], "forecast": [json.loads(aeris_page.decode('utf-8'))]} )
                        elif aeris_provider == "darksky":
                            req = Request( aeris_url, None, headers )
                            response = urlopen( req )
                            aeris_file_result = response.read()
                            response.close()


                except Exception as error:
                    raise Warning( "Error downloading forecast data. Check the URL in your configuration and try again. You are trying to use URL: %s, and the error is: %s" % ( aeris_url, error ) )

                # Save forecast data to file. w+ creates the file if it doesn't exist, and truncates the file and re-writes it everytime
                try:
                    with open( aeris_file, 'wb+' ) as file:
                        # Python 2/3
                        try:
                            file.write( aeris_file_result.encode('utf-8') )
                        except:
                            file.write( aeris_file_result )
                        loginf( "New forecast file downloaded to %s" % aeris_file )
                except IOError as e:
                    raise Warning( "Error writing forecast info to %s. Reason: %s" % ( aeris_file, e) )

            # Process the forecast file
            with open( aeris_file, "r" ) as read_file:
                data = json.load( read_file )

            if aeris_provider == "aeris":
                current_obs_summary = aeris_coded_weather( data["current"][0]["response"]["ob"]["weatherPrimaryCoded"] )

                current_obs_icon = aeris_icon( data["current"][0]["response"]["ob"]["icon"] ) + ".png"

                if aeris_units == "si" or aeris_units == "ca":
                    if data["current"][0]["response"]["ob"]["visibilityKM"] is not None:
                        visibility = locale.format("%g", data["current"][0]["response"]["ob"]["visibilityKM"] )
                        visibility_unit = "km"
                    else:
                        visibility = "N/A"
                        visibility_unit = ""
                else:
                    # us, uk2 and default to miles per hour
                    if  data["current"][0]["response"]["ob"]["visibilityMI"] is not None:
                        visibility = locale.format("%g", float( data["current"][0]["response"]["ob"]["visibilityMI"] ) )
                        visibility_unit = "miles"
                    else:
                        visibility = "N/A"
                        visibility_unit = ""
            elif aeris_provider == "darksky":
                current_obs_summary = label_dict[ data["currently"]["summary"].lower() ]
                visibility = locale.format("%g", float( data["currently"]["visibility"] ) )

                if data["currently"]["icon"] == "partly-cloudy-night":
                    current_obs_icon = 'partly-cloudy-night.png'
                else:
                    current_obs_icon = data["currently"]["icon"]+'.png'

                # Even though we specify the DarkSky unit as darksky_units, if the user selects "auto" as their unit
                # then we don't know what DarkSky will return for visibility. So always use the DarkSky output to 
                # tell us what unit they are using. This fixes the guessing game for what label to use for the DarkSky "auto" unit
                if ( data["flags"]["units"].lower() == "us" ) or ( data["flags"]["units"].lower() == "uk2" ):
                    visibility_unit = "miles"
                elif ( data["flags"]["units"].lower() == "si" ) or ( data["flags"]["units"].lower() == "ca" ):
                    visibility_unit = "km"
                else:
                    visibility_unit = ""
        else:
            current_obs_icon = ""
            current_obs_summary = ""
            visibility = "N/A"
            visibility_unit = ""


        # Put into a dictionary to return
        search_list_extension  = { 'current_obs_icon': current_obs_icon,
                                   'current_obs_summary': current_obs_summary,
                                   'visibility': visibility,
                                   'visibility_unit': visibility_unit}

        # Return our json data
        return [search_list_extension]
