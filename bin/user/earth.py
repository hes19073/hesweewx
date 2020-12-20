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
import locale

import weewx
import weecfg
import weeutil.logger
import weeutil.weeutil
import weeutil.config
import weewx.units

from math import atan2, degrees, radians, cos, sin, asin, sqrt

from weewx.cheetahgenerator import SearchList
from weewx.tags import TimespanBinder
from weeutil.weeutil import TimeSpan

log = logging.getLogger(__name__)

# Print version in syslog for easier troubleshooting
VERSION = "3.1.1"

log.info("version %s", VERSION)


class getEarthquake(SearchList):
    def __init__(self, generator):
        SearchList.__init__(self, generator)

    def get_gps_distance(self, pointA, pointB, distance_unit):
        # https://www.geeksforgeeks.org/program-distance-two-points-earth/ and https://stackoverflow.com/a/43960736
        # The math module contains a function named radians which converts from degrees to radians.
        if (type(pointA) != tuple) or (type(pointB) != tuple):
            raise TypeError("Only tuples are supported as arguments")
        lat1 = pointA[0]
        lon1 = pointA[1]
        lat2 = pointB[0]
        lon2 = pointB[1]
        # convert decimal degrees to radians
        lat1r, lon1r, lat2r, lon2r = map(radians, [lat1, lon1, lat2, lon2])
        # Haversine formula
        dlat = lat2r - lat1r
        dlon = lon2r - lon1r
        a = sin(dlat / 2)**2 + cos(lat1r) * cos(lat2r) * sin(dlon / 2)**2
        c = 2 * asin(sqrt(a))
        # Radius of earth in kilometers is 6371. Use 3956 for miles
        if distance_unit == "km":
            r = 6371
        else:
            # Assume mile
            r = 3956
        bearing = self.get_gps_bearing(pointA, pointB)
        # Returns distance as object 0 and bearing as object 1
        return [(c * r), self.get_cardinal_direction(bearing), bearing]

    def get_gps_bearing(self, pointA, pointB):
        """
        https://gist.github.com/jeromer/2005586
        Calculates the bearing between two points.
        :Parameters:
          - pointA: The tuple representing the latitude/longitude for the
            first point. Latitude and longitude must be in decimal degrees
          - pointB: The tuple representing the latitude/longitude for the
            second point. Latitude and longitude must be in decimal degrees
        :Returns:
          The bearing in degrees
        :Returns Type:
          float
        """
        if (type(pointA) != tuple) or (type(pointB) != tuple):
            raise TypeError("Only tuples are supported as arguments")
        lat1 = radians(pointA[0])
        lat2 = radians(pointB[0])
        diffLong = radians(pointB[1] - pointA[1])
        x = sin(diffLong) * cos(lat2)
        y = cos(lat1) * sin(lat2) - (sin(lat1)
                * cos(lat2) * cos(diffLong))
        initial_bearing = atan2(x, y)
        # Now we have the initial bearing but math.atan2 return values
        # from -180 to + 180 degrees which is not what we want for a compass bearing
        # The solution is to normalize the initial bearing as shown below
        initial_bearing = degrees(initial_bearing)
        compass_bearing = (initial_bearing + 360) % 360
        return compass_bearing

    def get_cardinal_direction(self, degree, return_only_labels=False):
        default_ordinate_names = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW', 'N/A']
        try:
            ordinate_names = weeutil.weeutil.option_as_list(self.generator.skin_dict['Units']['Ordinates']['directions'])
            try:
                ordinate_names = [unicode(x, "utf-8") for x in ordinate_names] # Python 2, convert to unicode
            except:
                pass
        except KeyError:
            ordinate_names = default_ordinate_names

        if return_only_labels:
            return ordinate_names

        if 0 <= degree <= 11.25:
            return ordinate_names[0]
        elif 11.26 <= degree <= 33.75:
            return ordinate_names[1]
        elif 33.76 <= degree <= 56.25:
            return ordinate_names[2]
        elif 56.26 <= degree <= 78.75:
            return ordinate_names[3]
        elif 78.76 <= degree <= 101.25:
            return ordinate_names[4]
        elif 101.26 <= degree <= 123.75:
            return ordinate_names[5]
        elif 123.76 <= degree <= 146.25:
            return ordinate_names[6]
        elif 146.26 <= degree <= 168.75:
            return ordinate_names[7]
        elif 168.76 <= degree <= 191.25:
            return ordinate_names[8]
        elif 191.26 <= degree <= 213.75:
            return ordinate_names[9]
        elif 213.76 <= degree <= 236.25:
            return ordinate_names[10]
        elif 236.26 <= degree <= 258.75:
            return ordinate_names[11]
        elif 258.76 <= degree <= 281.25:
            return ordinate_names[12]
        elif 281.26 <= degree <= 303.75:
            return ordinate_names[13]
        elif 303.76 <= degree <= 326.25:
            return ordinate_names[14]
        elif 326.26 <= degree <= 348.75:
            return ordinate_names[15]
        elif 348.76 <= degree <= 360:
            return ordinate_names[0]

    def get_extension_list(self, timespan, db_lookup):
        """
        Parse the Earthquake data.
        """

        # Return right away if we're not going to use the earthquake.
        if self.generator.skin_dict['Extras']['earthquake_enabled'] == "0":
            # Return an empty SLE
            search_list_extension = { }
            return [search_list_extension]

        # Setup the converter
        # Get the target unit nickname (something like 'US' or 'METRIC'):
        ## target_unit_nickname = self.generator.config_dict['StdConvert']['target_unit']
        # Get the target unit: weewx.US, weewx.METRIC, weewx.METRICWX
        ## target_unit = weewx.units.unit_constants[target_unit_nickname.upper()]
        # Bind to the appropriate standard converter units
        ## converter = weewx.units.StdUnitConverters[target_unit]

        earthquake_file = "/home/weewx/archive/earthquake.json"
        earthquake_stale_timer = self.generator.skin_dict['Extras']['earthquake_stale']
        latitude = self.generator.config_dict['Station']['latitude']
        longitude = self.generator.config_dict['Station']['longitude']
        distance_unit = self.generator.converter.group_unit_dict["group_distance"]
        # distance_unit = 'km'
        eq_distance_label = self.generator.skin_dict['Units']['Labels'].get(distance_unit, "")
        eq_distance_round = self.generator.skin_dict['Units']['StringFormats'].get(distance_unit, "%.1f")
        earthquake_maxradiuskm = self.generator.skin_dict['Extras']['earthquake_maxradiuskm']
        # Sample URL from Belchertown Weather:
        # http://earthquake.usgs.gov/fdsnws/event/1/query?limit=1&lat=53.605963&lon=11.341407&maxradiuskm=10000&format=geojson&nodata=204&minmag=2
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
        eqdistance_bearing = self.get_gps_distance((float(latitude), float(longitude)),
                                                   (float(eqlat), float(eqlon)),
                                                    distance_unit)
        # eqdistance = eq_distance_round % eqdistance_bearing[0]
        eqdistance = locale.format("%g", float(eq_distance_round % eqdistance_bearing[0]))
        eqbearing = eqdistance_bearing[1]
        eqbearing_raw = eqdistance_bearing[2]

        # Put into a dictionary to return
        search_list_extension  = { 'earthquake_time': eqtime,
                                   'earthquake_url': equrl,
                                   'earthquake_place': eqplace,
                                   'earthquake_magnitude': eqmag,
                                   'earthquake_lat': eqlat,
                                   'earthquake_lon': eqlon,
                                   'earthquake_tief': eqtief,
                                   'earthquake_dist': eqdistance,
                                   'earthquake_lage': eqbearing,
                                   'earthquake_lag': eqbearing_raw,
                                 }
        # Return our json data
        return [search_list_extension]
