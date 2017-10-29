#
#    Copyright (c) 2014 Just van den Broecke <just@justobjects.nl>
#
#    See GNU GPL LICENSE at top-level dir of this project.
#
"""Weather API fetcher for the weewx weather system"""

from __future__ import with_statement
import json
import time
from urllib2 import Request, urlopen, URLError, HTTPError
import urllib
import syslog

import weeutil.weeutil
import weewx.drivers
import weewx.wxformulas

from weewx.units import Converter

def loader(config_dict, engine):

    station = WeatherAPIStation(**config_dict['WeatherAPI'])

    return station

class WeatherAPIStation(weewx.drivers.AbstractDevice):
    """Station simulator by querying weather APIs"""

    def __init__(self, **stn_dict):
        """Initialize the WeatherAPIStation

        NAMED ARGUMENTS:

        loop_interval: The time (in seconds) between emitting LOOP packets. [Optional. Default is 2.5]

        openweathermap_url: the OpenWeatherMapAPI URL like 'http://api.openweathermap.org/data/2.5/weather?q=Otterlo,nl&units=imperial'
        """
        self.loop_interval = float(stn_dict.get('loop_interval', 5))

        # e.g.'http://api.openweathermap.org/data/2.5/weather?q=Otterlo,nl&units=imperial'
        self.openweathermap_url = ''.join(stn_dict.get('openweathermap_url'))
        syslog.syslog(syslog.LOG_INFO, "WeatherAPIStation: openweathermap_url=%s" % self.openweathermap_url)

        self.the_time = time.time()

    def genLoopPackets(self):

        while True:

            # http://api.openweathermap.org/data/2.5/find?q=Otterlo&units=imperial

            try:
                json_data = self.read_from_url(self.openweathermap_url)
                self.the_time = time.time()
                if json_data is not None:
                    data_dict = self.parse_data(json_data)
                    if data_dict is not None:
                        packet = self.createpacket(data_dict)
                        if packet is not None:
                            print("Created packet: %s" % str(packet))
                            yield packet
            finally:
                # We should never loose the loop due to some error
                # Determine how long to sleep
                # We are in real time mode. Try to keep synched up with the
                # wall clock
                # sleep_time = self.the_time + self.loop_interval - time.time()
                # if sleep_time > 0:

                time.sleep(self.loop_interval)

    def read_from_url(self, url, parameters=None):
        """
        Read the data from the URL.
        :param url: the url to fetch
        :param parameters: optional dict of query parameters
        :return:
        """
        # log.info('Fetch data from URL: %s ...' % url)

        req = Request(url)
        rsp_data = None
        try:
            # Urlencode optional parameters
            query_string = None
            if parameters:
                query_string = urllib.urlencode(parameters)

            syslog.syslog(syslog.LOG_INFO, "WeatherAPIStation: fetching packet from=%s ..." % url)
            response = urlopen(req, query_string)

            # everything is fine
            rsp_data = response.read()
        except Exception, e:
            syslog.syslog(syslog.LOG_WARNING, 'HTTPError fetching from URL %s: e=%s' % (url, str(e)))

        return rsp_data

    def parse_data(self, json_string):
        # One-time read/parse only
        file_data = None
        try:
            file_data = json.loads(json_string)
        except Exception, e:
            syslog.syslog(syslog.LOG_WARNING, 'Cannot parse JSON from %s, err= %s' % (json_string, str(e)))

        return file_data

    def createpacket(self, rsp_dict):
    # {"coord": {
    #     "lon": 5.77,
    #     "lat": 52.1
    # },
    #     "sys": {
    #         "type": 1,
    #         "id": 5207,
    #         "message": 0.6065,
    #         "country": "Netherlands",
    #         "sunrise": 1413266452,
    #         "sunset": 1413305086
    #     },
    #     "weather": [
    #         {
    #             "id": 503,
    #             "main": "Rain",
    #             "description": "very heavy rain",
    #             "icon": "10n"
    #         },
    #         {
    #             "id": 701,
    #             "main": "Mist",
    #             "description": "mist",
    #             "icon": "50n"
    #         }
    #     ],
    #     "base": "cmc stations",
    #     "main": {
    #         "temp": 286.87,
    #         "pressure": 1005,
    #         "humidity": 93,
    #         "temp_min": 286.15,
    #         "temp_max": 287.75
    #     },
    #     "wind": {
    #         "speed": 5.7,
    #         "deg": 200
    #     },
    #     "rain": { ## Achtung kein durchgehendes Argument 
    #     "1h": 47.27
    # }, "clouds": {
    #     "all": 90
    # }, "dt": 1413313501, "id": 2749203, "name": "Ede", "cod": 200}

        packet = {'dateTime': int(self.the_time+0.5), 'usUnits' : weewx.METRIC }
        try:
            main = rsp_dict['main']
            packet['outTemp'] = main['temp']
            # packet['barometer'] = main['temp']
            # p_m = (1016.5, 'mbar', 'group_pressure')
            # c = Converter()
            # print c.convert(p_m)
            # (30.020673360897813, 'inHg', 'group_pressure')

            #c = Converter()
            #p_m = (main['pressure'], 'mbar', 'group_pressure')
            #pressure, units, group = c.convert(p_m)

            packet['barometer'] = main['pressure']
            #packet['pressure'] = pressure
            packet['outHumidity'] = main['humidity']
            wind = rsp_dict['wind']
            # p_m = (wind['speed'], 'meter_per_second', 'group_speed')
            # speed, units, group = c.convert(p_m)

            packet['windSpeed'] = wind['speed']
            # packet['windGust'] = wind['speed']
            packet['windDir'] = wind['deg']
            # packet['windGust'] = Wind['deg']

            # packet['rainRate'] = rsp_dict['rain']['1h'] Element nicht permanent FIXME 

            packet['windchill'] = weewx.wxformulas.windchillF(packet['outTemp'], packet['windSpeed'])
            packet['dewpoint']  = weewx.wxformulas.dewpointF(packet['outTemp'], packet['outHumidity'])
            packet['heatindex'] = weewx.wxformulas.heatindexF(packet['outTemp'], packet['outHumidity'])
        except Exception, e:
            syslog.syslog(syslog.LOG_WARNING, "WeatherAPIStation: error creating packet=" + str(rsp_dict) + ' e=' + str(e))
            packet = None

        return packet

    def getTime(self):
        return self.the_time

    @property
    def hardware_name(self):
        return "WeatherAPI"


if __name__ == "__main__":

    station = WeatherAPIStation(openweathermap_url=['http://api.openweathermap.org/data/2.5/weather?q=Otterlo','nl&units=imperial'], loop_interval=2.0)
    for packet in station.genLoopPackets():
        print weeutil.weeutil.timestamp_to_string(packet['dateTime']), packet



