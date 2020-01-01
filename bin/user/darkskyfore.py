# -*- coding: utf-8 -*-
# $Id: darkskyfore.py 1651 2019-05-04 12:10:37Z hes $
# original by Pat O'Brien, August 19, 2018
# Copyright 2017 Hartmut Schweidler
# Die Erde und ihre Beben
# Wetter by DarkSky


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

from weewx.cheetahgenerator import SearchList
from weewx.tags import TimespanBinder
from weeutil.weeutil import TimeSpan

log = logging.getLogger(__name__)

def deg2dir(value):
        # map a decimal degree to a compass direction
    try:
        v = float(value)
    except (ValueError, TypeError):
        return None
    if 0 <= v <= 22.5:
        return 'N'
    elif 22.5 < v <= 65.5:
        return 'NE'
    elif 65.5 < v <= 112.5:
        return 'E'
    elif 112.5 < v <= 157.5:
        return 'SE'
    elif 157.5 < v <= 202.5:
        return 'S'
    elif 202.5 < v <= 247.5:
        return 'SW'
    elif 247.5 < v <= 292.5:
        return 'W'
    elif 292.5 < v <= 337.5:
        return 'NW'
    elif 337.5 < v <= 360:
        return 'N'
    return None


# Print version in syslog
VERSION = "1.2.1"

log.info("DS version %s", VERSION)

class getForecast(SearchList):
    def __init__(self, generator):
        SearchList.__init__(self, generator)

    def get_extension_list(self, timespan, db_lookup):

        """ Download and parse the Forecast data.
            von DakrSky 
            This is required for the majority of the theme to work
        """

        # Return right away if we're not going to use the forecast.
        if self.generator.skin_dict['Extras']['forecast_enabled'] == "0":
            # Return an empty SLE
            search_list_extension = {
                                     'current_obs_icon': "",
                                     'current_obs_summary': "",
                                     'current_visibility': "",
                                    }

            return [search_list_extension]


        forecast_file = "/home/weewx/archive/darksky_forecast.json"
        forecast_json_url = "/home/weewx/archive/darksky_forecast.json"
        darksky_secret_key = self.generator.skin_dict['Extras']['darksky_secret_key']
        darksky_units = self.generator.skin_dict['Extras']['darksky_units'].lower()
        latitude = self.generator.config_dict['Station']['latitude']
        longitude = self.generator.config_dict['Station']['longitude']
        forecast_stale_timer = self.generator.skin_dict['Extras']['forecast_stale']
        forecast_url = "https://api.darksky.net/forecast/%s/%s,%s?units=%s&lang=de" % (darksky_secret_key, latitude, longitude, darksky_units)

        forecast_is_stale = False

        # Determine if the file exists and get it's modified time
        if os.path.isfile(forecast_file):
            if (int(time.time()) - int(os.path.getmtime(forecast_file))) > int(forecast_stale_timer):
                forecast_is_stale = True
        else:
            # File doesn't exist, download a new copy
            forecast_is_stale = True

        # File is stale, download a new copy
        if forecast_is_stale:
            import urllib.request, urllib.error, urllib.parse
            urllib.request.urlretrieve(forecast_url, forecast_file)

            log.info("New DarkSky Forecast data downloaded to %s", forecast_file)

        with open(forecast_file, encoding="utf8") as read_file:
            data = json.loads(read_file.read())


        html_output = ""
        forecast_updated = time.strftime( "%d.%m.%Y %H:%M", time.localtime( data["currently"]["time"] ) )
        current_obs_summary = data["currently"]["summary"]
        current_temp = data["currently"]["temperature"]
        current_apptemp = data["currently"]["apparentTemperature"]
        current_windSpeed = (data["currently"]["windSpeed"] * 3.6)
        current_windGust = (data["currently"]["windGust"] * 3.6)
        current_windDir = deg2dir(data["currently"]["windBearing"])
        current_visibility = data["currently"]["visibility"]
        cur_now_summary = data["hourly"]["summary"]
        cur_week_summary = data["daily"]["summary"]
        cur_day_summary = data["daily"]["data"][0]["summary"]



        if data["currently"]["icon"] == "partly-cloudy-night":
            current_obs_icon = '<img id="wxicon" src="xicons/partly-cloudy-night.png">'
        else:
            current_obs_icon = '<img id="wxicon" src="xicons/'+data["currently"]["icon"]+'.png">'

        # Even though we specify the DarkSky unit as darksky_units, if the user selects "auto" as their unit
        # then we don't know what DarkSky will return for visibility. So always use the DarkSky output to
        # tell us what unit they are using. This fixes the guessing game for what label to use for the DarkSky "auto" unit
        if ( data["flags"]["units"].lower() == "us" ) or ( data["flags"]["units"].lower() == "uk2" ):
            visibility_unit = "miles"
        elif ( data["flags"]["units"].lower() == "si" ) or ( data["flags"]["units"].lower() == "ca" ):
            visibility_unit = "km"
        else:
            visibility_unit = ""

        # Loop through each day and generate the forecast row HTML
        for daily_data in data["daily"]["data"]:
            # Setup some variables
            if daily_data["icon"] == "partly-cloudy-night":
                image_url = "xicons/clear-day.png"
            else:
                image_url = "xicons/" + daily_data["icon"] + ".png"


            condition_text = ""
            if daily_data["icon"] == "clear-day":
                condition_text = "Wolkenlos"
            elif daily_data["icon"] == "clear-night":
                condition_text = "Wolkenlos"
            elif daily_data["icon"] == "rain":
                condition_text = "Regen"
            elif daily_data["icon"] == "snow":
                condition_text = "Schnee"
            elif daily_data["icon"] == "sleet":
                condition_text = "Schneeregen"
            elif daily_data["icon"] == "wind":
                condition_text = "Windig"
            elif daily_data["icon"] == "fog":
                condition_text = "Nebel"
            elif daily_data["icon"] == "cloudy":
                condition_text = "bedeckt"
            elif daily_data["icon"] == "partly-cloudy-day":
                condition_text = "teilweise wolkig"
            elif daily_data["icon"] == "partly-cloudy-night":
                condition_text = "teilweise wolkig"
            elif daily_data["icon"] == "hail":
                condition_text = "Hagel"
            elif daily_data["icon"] == "thunderstorm":
                condition_text = "Gewitter"
            elif daily_data["icon"] == "tornado":
                condition_text = "Tornado"

            # Build html
            if time.strftime( "%a %m/%d", time.localtime( daily_data["time"] ) ) == time.strftime( "%a %m/%d", time.localtime( time.time() ) ):
                # If the time in the darksky output is today, do not add border-left and say "Today" in the header
                output = '<div class="col-sm-1-5 wuforecast">'
                weekday = "Heute"
            else:
                output = '<div class="col-sm-1-5 wuforecast border-left">'
                weekday = time.strftime( "%a: %d.%m.%Y", time.localtime( daily_data["time"] ) )
                #weekday = time.strftime( "%a %-m/%d", time.localtime( daily_data["time"] ) )  # Original by ob

            output += '<span id="weekday">' + weekday + '</span>'
            output += '<br>'
            output += '<div class="forecast-conditions">'
            output += '<img id="icon" src="'+image_url+'">'
            output += '<br>'
            output += '<span class="forecast-condition-text">'
            output += condition_text
            output += '</span>'
            output += '</div>'
            output += '<span class="forecast-high">'+str(int(daily_data["temperatureHigh"])) + '&deg;C</span> | <span class="forecast-low">'+str(int(daily_data["temperatureLow"])) + '&deg;C</span>'
            output += '<br>'
            output += '<div class="forecast-precip">'
            if "precipType" in daily_data:
                if daily_data["precipType"] == "snow":
                    output += '<div class="snow-precip">'
                    output += '<img src="xicons/snowflake-icon-15px.png"> <span>'+ str(int(daily_data["precipAccumulation"])) + '<span> cm'
                    output += '</div>'
                elif daily_data["precipType"] == "rain":
                    output += '<img src="xicons/raindrop.png"> <span >'+ str(int(daily_data["precipProbability"] * 100)) + ' %</span>'
            else:
                output += '<img src="xicons/raindrop.png"> <span > 0%</span>'
            output += '</div>'
            output += '<div class="forecast-wind">'
            #output += '<img src="xicons/wind.png" width="15px" height="15px"> <span >'+ str(int(daily_data["windGust"] * 3.6)) + ' km/h'
            output += '<img src="xicons/strong-wind.svg"> <span >'+ str(int(daily_data["windGust"] * 3.6)) + ' km/h'
            output += '</div>'
            output += "</div> <!-- end .wuforecast -->"
            output += '<br />'
            # Add to the output
            html_output += output


        # Put into a dictionary to return
        search_list_extension  = {
                                  'forecast_updated': forecast_updated,
                                  'forecast_json_url': forecast_json_url,
                                  'current_obs_icon': current_obs_icon,
                                  'current_obs_summary': current_obs_summary,
                                  'current_temp': current_temp,
                                  'current_apptemp': current_apptemp,
                                  'current_windSpeed': current_windSpeed,
                                  'current_windGust': current_windGust,
                                  'current_windDir': current_windDir,
                                  'current_visibility': current_visibility,
                                  'day_summary': cur_day_summary,
                                  'now_summary': cur_now_summary,
                                  'week_summary': cur_week_summary,
                                  'forecastHTML' : html_output
                                 }

        # Return our json data
        return [search_list_extension]

