# -*- coding: utf-8 -*-
# $Id: earth.py 1651 2018-09-01 12:10:37Z hes $
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
    syslog.syslog(level, 'Erdbeben Extension: %s' % msg)
    
def logdbg(msg):
    logmsg(syslog.LOG_DEBUG, msg)
    
def loginf(msg):
    logmsg(syslog.LOG_INFO, msg)
    
def logerr(msg):
    logmsg(syslog.LOG_ERR, msg)

# Print version in syslog for easier troubleshooting
VERSION = "1.0"
loginf("version %s" % VERSION)


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
        #Sample URL from Belchertown Weather: http://earthquake.usgs.gov/fdsnws/event/1/query?limit=1&lat=42.223&lon=-72.374&maxradiuskm=1000&format=geojson&nodata=204&minmag=2
        earthquake_url = "http://earthquake.usgs.gov/fdsnws/event/1/query?limit=1&lat=%s&lon=%s&maxradiuskm=%s&format=geojson&nodata=204&minmag=2" % ( latitude, longitude, earthquake_maxradiuskm )
        earthquake_is_stale = False

        # Determine if the file exists and get it's modified time
        if os.path.isfile( earthquake_file ):
            if ( int( time.time() ) - int( os.path.getmtime( earthquake_file ) ) ) > int( earthquake_stale_timer ):
                earthquake_is_stale = True
        else:
            # File doesn't exist, download a new copy
            earthquake_is_stale = True
            
        # File is stale, download a new copy
        if earthquake_is_stale:
            # Download new earthquake data
            try:
                import urllib2
                user_agent = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_4; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.472.63 Safari/534.3'
                headers = { 'User-Agent' : user_agent }
                req = urllib2.Request( earthquake_url, None, headers )
                response = urllib2.urlopen( req )
                page = response.read()
                response.close()
            except Exception as error:
                raise ValueError( "Error downloading earthquake data. Check the URL and try again. You are trying to use URL: %s, and the error is: %s" % ( earthquake_url, error ) )
                
            # Save earthquake data to file. w+ creates the file if it doesn't exist, and truncates the file and re-writes it everytime
            try:
                with open( earthquake_file, 'w+' ) as file:
                    file.write( page )
                    loginf( "New earthquake data downloaded to %s" % earthquake_file )
            except IOError, e:
                raise ValueError( "Error writing earthquake data to %s. Reason: %s" % ( earthquake_file, e) )
            
        # Process the earthquake file
        with open( earthquake_file, "r") as read_file:
            eqdata = json.load( read_file )

        eqtime = time.strftime( "%d.%B %Y, %H:%M  %Z", time.localtime( eqdata["features"][0]["properties"]["time"] / 1000 ) )
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
