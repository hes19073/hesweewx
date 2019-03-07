# -*- coding: utf-8 -*-
##This program is free software; you can redistribute it and/or modify it under
##the terms of the GNU General Public License as published by the Free Software
##Foundation; either version 2 of the License, or (at your option) any later
##version.
##
##This program is distributed in the hope that it will be useful, but WITHOUT
##ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
##FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
##details.
##
## Version: 1.2.0b1                                    Date: 1 August 2015
##
## Revision History
##  ?? August 2015        v1.2.0    -revised for Weewx v3.2.0
##                                  -moved __main__ code to weewxwd_config utility
##                                  -now uses appTemp and humidex as provided by
##                                   StdWXCalculate
##                                  -simplified WdWXCalculate.new_loop_packet,
##                                   WdWXCalculate.new_archive_record and
##                                   WdArchive.new_archive_record methods
##  10 January 2015     v1.0.0      -rewritten for Weewx v3.0
##                                  -uses separate database for Weewx-WD specific
##                                   data, no longer recycles existing Weewx
##                                   database fields
##                                  -added __main__ to allow command line execution
##                                   of a number of db management actions
##                                  -removed --debug option from main()
##                                  -added --create_archive option to main()
##                                   to create the weewxwd database
##                                  -split --backfill_daily into separate
##                                   --drop_daily and --backfill_daily options
##                                  -added 'user.' to all Weewx-WD imports
##  18 September 2014   v0.9.4      -Added GNU license text
##      (never released)
##  18 May 2014         v0.9.2      -Removed code that set windDir/windGustDir to 0
##                                   if windDir/windGustDir were None respectively
##  30 July 2013        v0.9.1      -Revised version number to align with Weewx-WD
##                                   version numbering
##  20 July 2013        v0.1        -Initial implementation
##

from __future__ import absolute_import
from __future__ import print_function

import syslog
import threading
import urllib.request, urllib.error, urllib.parse
import json
import math
import os
import time
import ephem

from math import sin
from datetime import datetime
#from urllib import urlopen

import weewx
import weewx.engine
import weewx.manager
import weewx.wxformulas
import weewx.almanac
import user.zformulas

from weewx.units import convert, obs_group_dict
from weeutil.weeutil import to_bool, accumulateLeaves
from weewx.units import CtoF, CtoK, mps_to_mph, kph_to_mph

WEEWXWD_VERSION = '1.2.1'

# Define a dictionary with our API call query details
WU_queries = [
    {
        'name': 'conditions',
        'interval': None,
        'last': None,
        'interval': None,
        'def_interval': 1800,
        'response': None,
        'json_title': 'current_observation'
    },
    {
        'name': 'forecast',
        'interval': None,
        'last': None,
        'interval': 1800,
        'def_interval': 1800,
        'response': None,
        'json_title': 'forecast'
    },
    {
        'name': 'almanac',
        'interval': None,
        'last': None,
        'interval': 3600,
        'def_interval': 3600,
        'response': None,
        'json_title': 'almanac'
    }
]

# Define a dictionary to look up WU icon names and
# return corresponding Saratoga icon code
icon_dict = {
    'clear'             : 0,
    'cloudy'            : 18,
    'flurries'          : 25,
    'fog'               : 11,
    'hazy'              : 7,
    'mostlycloudy'      : 18,
    'mostlysunny'       : 9,
    'partlycloudy'      : 19,
    'partlysunny'       : 9,
    'sleet'             : 23,
    'rain'              : 20,
    'snow'              : 25,
    'sunny'             : 28,
    'tstorms'           : 29,
    'nt_clear'          : 1,
    'nt_cloudy'         : 13,
    'nt_flurries'       : 16,
    'nt_fog'            : 11,
    'nt_hazy'           : 13,
    'nt_mostlycloudy'   : 13,
    'nt_mostlysunny'    : 1,
    'nt_partlycloudy'   : 4,
    'nt_partlysunny'    : 1,
    'nt_sleet'          : 12,
    'nt_rain'           : 14,
    'nt_snow'           : 16,
    'nt_tstorms'        : 17,
    'chancerain'        : 20,
    'chancesleet'       : 23,
    'chancesnow'        : 25,
    'chancetstorms'     : 29
    }


# Define a dictionary to look up Davis forecast rule
# and return forecast text
davis_fr_dict= {
        0   : 'Meist heiter und kälter.',
        1   : 'Meist heiter mit geringer Temperaturänderung.',
        2   : 'Meist heiter für 12 Stunden mit geringer Temperaturänderung.',
        3   : 'Meist heiter für 12 bis 24 Stunden und kälter.',
        4   : 'Meist heiter mit geringer Temperaturänderung.',
        5   : 'Teils wolkig und kälter.',
        6   : 'Teils wolkig mit geringer Temperaturänderung.',
        7   : 'Teils wolkig mit geringer Temperaturänderung.',
        8   : 'Meist heiter und wärmer.',
        9   : 'Teils wolkig mit geringer Temperaturänderung.',
        10  : 'Teils wolkig mit geringer Temperaturänderung.',
        11  : 'Meist heiter mit geringer Temperaturänderung.',
        12  : 'Zunehmend bewölkt und wärmer. Niederschlag möglich innerhalb 24 bis 48 Stunden.',
        13  : 'Teils wolkig mit geringer Temperaturänderung.',
        14  : 'Meist heiter mit geringer Temperaturänderung.',
        15  : 'Zunehmend bewölkt mit geringer Temperaturänderung. Niederschlag möglich innerhalb 24 Stunden.',
        16  : 'Meist heiter mit geringer Temperaturänderung.',
        17  : 'Teils wolkig mit geringer Temperaturänderung.',
        18  : 'Meist heiter mit geringer Temperaturänderung.',
        19  : 'Zunehmend bewölkt mit geringer Temperaturänderung. Niederschlag möglich innerhalb 12 Stunden.',
        20  : 'Meist heiter mit geringer Temperaturänderung.',
        21  : 'Teils wolkig mit geringer Temperaturänderung.',
        22  : 'Meist heiter mit geringer Temperaturänderung.',
        23  : 'Zunehmend bewölkt und wärmer. Niederschlag möglich innerhalb 24 Stunden.',
        24  : 'Meist heiter und wärmer. Zunehmender Wind.',
        25  : 'Teils wolkig mit geringer Temperaturänderung.',
        26  : 'Meist heiter mit geringer Temperaturänderung.',
        27  : 'Zunehmend bewölkt und wärmer. Niederschlag möglich innerhalb 12 Stunden. Zunehmender Wind.',
        28  : 'Meist heiter und wärmer. Zunehmender Wind.',
        29  : 'Zunehmend bewölkt und wärmer.',
        30  : 'Teils wolkig mit geringer Temperaturänderung.',
        31  : 'Meist heiter mit geringer Temperaturänderung.',
        32  : 'Zunehmend bewölkt und wärmer. Niederschlag möglich innerhalb 12 Stunden. Zunehmender Wind.',
        33  : 'Meist heiter und wärmer. Zunehmender Wind.',
        34  : 'Zunehmend bewölkt und wärmer.',
        35  : 'Teils wolkig mit geringer Temperaturänderung.',
        36  : 'Meist heiter mit geringer Temperaturänderung.',
        37  : 'Zunehmend bewölkt und wärmer. Niederschlag möglich innerhalb 12 Stunden. Zunehmender Wind.',
        38  : 'Teils wolkig mit geringer Temperaturänderung.',
        39  : 'Meist heiter mit geringer Temperaturänderung.',
        40  : 'Meist heiter und wärmer. Niederschlag möglich innerhalb 48 Stunden.',
        41  : 'Meist heiter und wärmer.',
        42  : 'Teils wolkig mit geringer Temperaturänderung.',
        43  : 'Meist heiter mit geringer Temperaturänderung.',
        44  : 'Zunehmend bewölkt mit geringer Temperaturänderung. Niederschlag möglich innerhalb 24 bis 48 Stunden.',
        45  : 'Zunehmend bewölkt mit geringer Temperaturänderung.',
        46  : 'Teils wolkig mit geringer Temperaturänderung.',
        47  : 'Meist heiter mit geringer Temperaturänderung.',
        48  : 'Zunehmend bewölkt und wärmer. Niederschlag möglich innerhalb 12 bis 24 Stunden.',
        49  : 'Teils wolkig mit geringer Temperaturänderung.',
        50  : 'Meist heiter mit geringer Temperaturänderung.',
        51  : 'Zunehmend bewölkt und wärmer. Niederschlag möglich innerhalb 12 bis 24 Stunden. Windig.',
        52  : 'Teils wolkig mit geringer Temperaturänderung.',
        53  : 'Meist heiter mit geringer Temperaturänderung.',
        54  : 'Zunehmend bewölkt und wärmer. Niederschlag möglich innerhalb 12 bis 24 Stunden. Windig.',
        55  : 'Teils wolkig mit geringer Temperaturänderung.',
        56  : 'Meist heiter mit geringer Temperaturänderung.',
        57  : 'Zunehmend bewölkt und wärmer. Niederschlag möglich innerhalb 6 bis 12 Stunden.',
        58  : 'Teils wolkig mit geringer Temperaturänderung.',
        59  : 'Meist heiter mit geringer Temperaturänderung.',
        60  : 'Zunehmend bewölkt und wärmer. Niederschlag möglich innerhalb 6 bis 12 Stunden. Windig.',
        61  : 'Teils wolkig mit geringer Temperaturänderung.',
        62  : 'Meist heiter mit geringer Temperaturänderung.',
        63  : 'Zunehmend bewölkt und wärmer. Niederschlag möglich innerhalb 12 bis 24 Stunden. Windig.',
        64  : 'Teils wolkig mit geringer Temperaturänderung.',
        65  : 'Meist heiter mit geringer Temperaturänderung.',
        66  : 'Zunehmend bewölkt und wärmer. Niederschlag möglich innerhalb 12 Stunden.',
        67  : 'Teils wolkig mit geringer Temperaturänderung.',
        68  : 'Meist heiter mit geringer Temperaturänderung.',
        69  : 'Zunehmend bewölkt und wärmer. Niederschlag wahrscheinlich.',
        70  : 'Aufklarend und kälter. Niederschlag endet innerhalb 6 Stunden.',
        71  : 'Teils wolkig mit geringer Temperaturänderung.',
        72  : 'Aufklarend und kälter. Niederschlag endet innerhalb 6 Stunden.',
        73  : 'Meist heiter mit geringer Temperaturänderung.',
        74  : 'Aufklarend und kälter. Niederschlag endet innerhalb 6 Stunden.',
        75  : 'Teils wolkig und kälter.',
        76  : 'Teils wolkig mit geringer Temperaturänderung.',
        77  : 'Meist heiter und kälter.',
        78  : 'Aufklarend und kälter. Niederschlag endet innerhalb 6 Stunden.',
        79  : 'Meist heiter mit geringer Temperaturänderung.',
        80  : 'Aufklarend und kälter. Niederschlag endet innerhalb 6 Stunden.',
        81  : 'Meist heiter und kälter.',
        82  : 'Teils wolkig mit geringer Temperaturänderung.',
        83  : 'Meist heiter mit geringer Temperaturänderung.',
        84  : 'Zunehmend bewölkt mit geringer Temperaturänderung. Niederschlag möglich innerhalb 24 Stunden.',
        85  : 'Meist wolkig und kälter. Niederschlag dauert an.',
        86  : 'Teils wolkig mit geringer Temperaturänderung.',
        87  : 'Meist heiter mit geringer Temperaturänderung.',
        88  : 'Meist wolkig und kälter. Niederschlag wahrscheinlich.',
        89  : 'Meist wolkig mit geringer Temperaturänderung. Niederschlag dauert an.',
        90  : 'Meist wolkig mit geringer Temperaturänderung. Niederschlag wahrscheinlich.',
        91  : 'Teils wolkig mit geringer Temperaturänderung.',
        92  : 'Meist heiter mit geringer Temperaturänderung.',
        93  : 'Zunehmend bewölkt und kälter. Niederschlag möglich und windig innerhalb 6 Stunden.',
        94  : 'Zunehmend bewölkt mit geringer Temperaturänderung. Niederschlag möglich und windig innerhalb 6 Stunden.',
        95  : 'Meist wolkig und kälter. Niederschlag dauert an. Zunehmender Wind.',
        96  : 'Teils wolkig mit geringer Temperaturänderung.',
        97  : 'Meist heiter mit geringer Temperaturänderung.',
        98  : 'Meist wolkig und kälter. Niederschlag wahrscheinlich. Zunehmender Wind.',
        99  : 'Meist wolkig mit geringer Temperaturänderung. Niederschlag dauert an. Zunehmender Wind.',
        100 : 'Meist wolkig mit geringer Temperaturänderung. Niederschlag wahrscheinlich. Zunehmender Wind.',
        101 : 'Teils wolkig mit geringer Temperaturänderung.',
        102 : 'Meist heiter mit geringer Temperaturänderung.',
        103 : 'Zunehmend bewölkt und kälter. Niederschlag möglich innerhalb 12 bis 24 Stunden und möglicher Windrichtungswechsel auf W, NW, oder N.',
        104 : 'Zunehmend bewölkt mit geringer Temperaturänderung. Niederschlag möglich innerhalb 12 bis 24 Stunden und möglicher Windrichtungswechsel auf W, NW, oder N.',
        105 : 'Teils wolkig mit geringer Temperaturänderung.',
        106 : 'Meist heiter mit geringer Temperaturänderung.',
        107 : 'Zunehmend bewölkt und kälter. Niederschlag möglich innerhalb 6 Stunden und möglicher Windrichtungswechsel auf W, NW, oder N.',
        108 : 'Zunehmend bewölkt mit geringer Temperaturänderung. Niederschlag möglich innerhalb 6 Stunden und möglicher Windrichtungswechsel auf W, NW, oder N.',
        109 : 'Meist wolkig und kälter. Niederschlag endet innerhalb 12 Stunden und möglicher Windrichtungswechsel auf W, NW, oder N.',
        110 : 'Meist wolkig und kälter. Windrichtungswechsel möglich auf W, NW, oder N.',
        111 : 'Meist wolkig mit geringer Temperaturänderung. Niederschlag endet innerhalb 12 Stunden und möglicher Windrichtungswechsel auf W, NW, oder N.',
        112 : 'Meist wolkig mit geringer Temperaturänderung. Windrichtungswechsel möglich auf W, NW, oder N.',
        113 : 'Meist wolkig und kälter. Niederschlag endet innerhalb 12 Stunden und möglicher Windrichtungswechsel auf W, NW, oder N.',
        114 : 'Teils wolkig mit geringer Temperaturänderung.',
        115 : 'Meist heiter mit geringer Temperaturänderung.',
        116 : 'Meist wolkig und kälter. Niederschlag möglich innerhalb 24 Stunden und möglicher Windrichtungswechsel auf W, NW, oder N.',
        117 : 'Meist wolkig mit geringer Temperaturänderung. Niederschlag endet innerhalb 12 Stunden und möglicher Windrichtungswechsel auf W, NW, oder N.',
        118 : 'Meist wolkig mit geringer Temperaturänderung. Niederschlag möglich innerhalb 24 Stunden und möglicher Windrichtungswechsel auf W, NW, oder N.',
        119 : 'Aufklarend, kälter und windig. Niederschlag endet innerhalb 6 Stunden.',
        120 : 'Aufklarend, kälter und windig.',
        121 : 'Meist wolkig und kälter. Niederschlag endet innerhalb 6 Stunden. Windig mit möglichem Windrichtungswechsel auf W, NW, oder N.',
        122 : 'Meist wolkig und kälter. Windig mit möglichem Windrichtungswechsel auf W, NW, oder N.',
        123 : 'Aufklarend, kälter und windig.',
        124 : 'Teils wolkig mit geringer Temperaturänderung.',
        125 : 'Meist heiter mit geringer Temperaturänderung.',
        126 : 'Meist wolkig mit geringer Temperaturänderung. Niederschlag möglich innerhalb 12 Stunden. Windig.',
        127 : 'Teils wolkig mit geringer Temperaturänderung.',
        128 : 'Meist heiter mit geringer Temperaturänderung.',
        129 : 'Zunehmend bewölkt und kälter. Niederschlag möglich innerhalb 12 Stunden, zeitweise heftig. Windig.',
        130 : 'Meist wolkig und kälter. Niederschlag endet innerhalb 6 Stunden. Windig.',
        131 : 'Teils wolkig mit geringer Temperaturänderung.',
        132 : 'Meist heiter mit geringer Temperaturänderung.',
        133 : 'Meist wolkig und kälter. Niederschlag möglich innerhalb 12 Stunden. Windig.',
        134 : 'Meist wolkig und kälter. Niederschlag endet in 12 bis 24 Stunden.',
        135 : 'Meist wolkig und kälter.',
        136 : 'Meist wolkig und kälter. Niederschlag dauert an, zeitweise heftig. Windig.',
        137 : 'Teils wolkig mit geringer Temperaturänderung.',
        138 : 'Meist heiter mit geringer Temperaturänderung.',
        139 : 'Meist wolkig und kälter. Niederschlag möglich innerhalb 6 bis 12 Stunden. Windig.',
        140 : 'Meist wolkig mit geringer Temperaturänderung. Niederschlag dauert an, zeitweise heftig. Windig.',
        141 : 'Teils wolkig mit geringer Temperaturänderung.',
        142 : 'Meist heiter mit geringer Temperaturänderung.',
        143 : 'Meist wolkig mit geringer Temperaturänderung. Niederschlag möglich innerhalb 6 bis 12 Stunden. Windig.',
        144 : 'Teils wolkig mit geringer Temperaturänderung.',
        145 : 'Meist heiter mit geringer Temperaturänderung.',
        146 : 'Zunehmend bewölkt mit geringer Temperaturänderung. Niederschlag möglich innerhalb 12 Stunden, zeitweise heftig. Windig.',
        147 : 'Meist wolkig und kälter. Windig.',
        148 : 'Meist wolkig und kälter. Niederschlag dauert an, zeitweise heftig. Windig.',
        149 : 'Teils wolkig mit geringer Temperaturänderung.',
        150 : 'Meist heiter mit geringer Temperaturänderung.',
        151 : 'Meist wolkig und kälter. Niederschlag wahrscheinlich, zeitweise heftig. Windig.',
        152 : 'Meist wolkig mit geringer Temperaturänderung. Niederschlag dauert an, zeitweise heftig. Windig.',
        153 : 'Meist wolkig mit geringer Temperaturänderung. Niederschlag wahrscheinlich, zeitweise heftig. Windig.',
        154 : 'Teils wolkig mit geringer Temperaturänderung.',
        155 : 'Meist heiter mit geringer Temperaturänderung.',
        156 : 'Zunehmend bewölkt und kälter. Niederschlag möglich innerhalb 6 Stunden. Windig.',
        157 : 'Zunehmend bewölkt mit geringer Temperaturänderung. Niederschlag möglich innerhalb 6 Stunden. Windig.',
        158 : 'Zunehmend bewölkt und kälter. Niederschlag dauert an. Windig mit möglichem Windrichtungswechsel auf W, NW, oder N.',
        159 : 'Teils wolkig mit geringer Temperaturänderung.',
        160 : 'Meist heiter mit geringer Temperaturänderung.',
        161 : 'Meist wolkig und kälter. Niederschlag wahrscheinlich. Windig mit möglichem Windrichtungswechsel auf W, NW, oder N.',
        162 : 'Meist wolkig mit geringer Temperaturänderung. Niederschlag dauert an. Windig mit möglichem Windrichtungswechsel auf W, NW, oder N.',
        163 : 'Meist wolkig mit geringer Temperaturänderung. Niederschlag wahrscheinlich. Windig mit möglichem Windrichtungswechsel auf W, NW, oder N.',
        164 : 'Zunehmend bewölkt und kälter. Niederschlag möglich innerhalb 6 Stunden. Windig mit möglichem Windrichtungswechsel auf W, NW, oder N.',
        165 : 'Teils wolkig mit geringer Temperaturänderung.',
        166 : 'Meist heiter mit geringer Temperaturänderung.',
        167 : 'Zunehmend bewölkt und kälter. Niederschlag möglich innerhalb 6 Stunden und möglicher Windrichtungswechsel auf W, NW, oder N.',
        168 : 'Zunehmend bewölkt mit geringer Temperaturänderung. Niederschlag möglich innerhalb 6 Stunden. Windig mit möglichem Windrichtungswechsel auf W, NW, oder N.',
        169 : 'Zunehmend bewölkt mit geringer Temperaturänderung. Niederschlag möglich innerhalb 6 Stunden und möglicher Windrichtungswechsel auf W, NW, oder N.',
        170 : 'Teils wolkig mit geringer Temperaturänderung.',
        171 : 'Meist heiter mit geringer Temperaturänderung.',
        172 : 'Zunehmend bewölkt und kälter. Niederschlag möglich innerhalb 6 Stunden. Windig mit möglichem Windrichtungswechsel auf W, NW, oder N.',
        173 : 'Zunehmend bewölkt mit geringer Temperaturänderung. Niederschlag möglich innerhalb 6 Stunden. Windig mit möglichem Windrichtungswechsel auf W, NW, oder N.',
        174 : 'Teils wolkig mit geringer Temperaturänderung.',
        175 : 'Meist heiter mit geringer Temperaturänderung.',
        176 : 'Zunehmend bewölkt und kälter. Niederschlag möglich innerhalb 12 bis 24 Stunden. Windig mit möglichem Windrichtungswechsel auf W, NW, oder N.',
        177 : 'Zunehmend bewölkt mit geringer Temperaturänderung. Niederschlag möglich innerhalb 12 bis 24 Stunden. Windig mit möglichem Windrichtungswechsel auf W, NW, oder N.',
        178 : 'Meist wolkig und kälter. Niederschlag zeitweise heftig und endet innerhalb 12 Stunden. Windig mit möglichem Windrichtungswechsel auf W, NW, oder N.',
        179 : 'Teils wolkig mit geringer Temperaturänderung.',
        180 : 'Meist heiter mit geringer Temperaturänderung.',
        181 : 'Meist wolkig und kälter. Niederschlag möglich innerhalb 6 bis 12 Stunden, zeitweise heftig. Windig mit möglichem Windrichtungswechsel auf W, NW, oder N.',
        182 : 'Meist wolkig mit geringer Temperaturänderung. Niederschlag endet innerhalb 12 Stunden. Windig mit möglichem Windrichtungswechsel auf W, NW, oder N.',
        183 : 'Meist wolkig mit geringer Temperaturänderung. Niederschlag möglich innerhalb 6 bis 12 Stunden, zeitweise heftig. Windig mit möglichem Windrichtungswechsel auf W, NW, oder N.',
        184 : 'Meist wolkig und kälter. Niederschlag dauert an.',
        185 : 'Teils wolkig mit geringer Temperaturänderung.',
        186 : 'Meist heiter mit geringer Temperaturänderung.',
        187 : 'Meist wolkig und kälter. Niederschlag wahrscheinlich. Windig mit möglichem Windrichtungswechsel auf W, NW, oder N.',
        188 : 'Meist wolkig mit geringer Temperaturänderung. Niederschlag dauert an.',
        189 : 'Meist wolkig mit geringer Temperaturänderung. Niederschlag wahrscheinlich.',
        190 : 'Teils wolkig mit geringer Temperaturänderung.',
        191 : 'Meist heiter mit geringer Temperaturänderung.',
        192 : 'Meist wolkig und kälter. Niederschlag möglich innerhalb 12 Stunden, zeitweise heftig. Windig.',
        193 : 'FORECAST REQUIRES 3 HOURS OF RECENT DATA',
        194 : 'Meist heiter und kälter.',
        195 : 'Meist heiter und kälter.',
        196 : 'Meist heiter und kälter.',
        }

def logmsg(level, src, msg):
    syslog.syslog(level, '%s %s' % (src, msg))

def logdbg(src, msg):
    logmsg(syslog.LOG_DEBUG, src, msg)

def logdbg2(src, msg):
    if weewx.debug >= 2:
        logmsg(syslog.LOG_DEBUG, src, msg)

def loginf(src, msg):
    logmsg(syslog.LOG_INFO, src, msg)

def logerr(src, msg):
    logmsg(syslog.LOG_ERR, src, msg)

#===============================================================================
#                            Class WdWXCalculate
#===============================================================================

class WdWXCalculate(weewx.engine.StdService):

    def __init__(self, engine, config_dict):
        super(WdWXCalculate, self).__init__(engine, config_dict)

        # bind ourself to both loop and archive events
        self.bind(weewx.NEW_LOOP_PACKET, self.new_loop_packet)
        self.bind(weewx.NEW_ARCHIVE_RECORD, self.new_archive_record)

    def new_loop_packet(self, event):
        data_x = {}
        if 'outTemp' in event.packet:
            data_x['outTempDay'], data_x['outTempNight'] = calc_daynighttemps(event.packet['outTemp'], event.packet['dateTime'])
        else:
            data_x['outTempDay'], data_x['outTempNight'] = (None, None)

        if 'outTemp' in event.packet and 'outHumidity' in event.packet:
            data_x['summersimmerIndex'] = weewx.wxformulas.sumsimIndex_C(event.packet['outTemp'], event.packet['outHumidity'])
        else:
            data_x['summersimmerIndex'] = None

        if 'outTemp' in event.packet:
            data_x['heatdeg'] = weewx.wxformulas.heating_degrees(event.packet['outTemp'], 18.333)
        else:
            data_x['heatdeg'] = None

        if 'outTemp' in event.packet:
            data_x['cooldeg'] = weewx.wxformulas.cooling_degrees(event.packet['outTemp'], 18.333)
        else:
            data_x['cooldeg'] = None

        if 'outTemp' in event.packet:
            data_x['homedeg'] = weewx.wxformulas.heating_degrees(event.packet['outTemp'], 15.0)
        else:
            data_x['homedeg'] = None

        if 'outTemp' in event.packet:
            data_x['wdd_deg'] = weewx.wxformulas.heating_degrees(event.packet['outTemp'], 10.0)
        else:
            data_x['wdd_deg'] = None

        if 'outTemp' in event.packet:
            data_x['SVP'] = weewx.uwxutils.TWxUtils.SaturationVaporPressure(event.packet['outTemp'])
        else:
            data_x['SVP'] = None

        if 'inTemp' in event.packet:
            data_x['SVPin'] = weewx.uwxutils.TWxUtils.SaturationVaporPressure(event.packet['inTemp'])
        else:
            data_x['SVPin'] = None

        if 'outTemp' in event.packet and 'outHumidity' in event.packet:
            data_x['AVP'] = event.packet['outHumidity'] * (weewx.uwxutils.TWxUtils.SaturationVaporPressure(event.packet['outTemp'])) / 100.0
        else:
            data_x['AVP'] = None

        if 'inTemp' in event.packet and 'inHumidity' in event.packet:
            data_x['AVPin'] = event.packet['inHumidity'] * (weewx.uwxutils.TWxUtils.SaturationVaporPressure(event.packet['inTemp'])) / 100.0
        else:
            data_x['AVPin'] = None

        if 'outTemp' in event.packet:
            data_x['GDD4'] = weewx.wxformulas.cooling_degrees(event.packet['outTemp'], 4.0)
        else:
            data_x['GDD4'] = None

        if 'outTemp' in event.packet:
            data_x['GDD6'] = weewx.wxformulas.cooling_degrees(event.packet['outTemp'], 6.0)
        else:
            data_x['GDD6'] = None

        if 'outTemp' in event.packet:
            data_x['GDD10'] = weewx.wxformulas.cooling_degrees(event.packet['outTemp'], 10.0)
        else:
            data_x['GDD10'] = None

        if 'outTemp' in event.packet and 'pressure' in event.packet:
            data_x['densityA'] = weewx.wxformulas.da_Metric(event.packet['outTemp'], event.packet['pressure'])
        else:
            data_x['densityA'] = None




        event.packet.update(data_x)

    def new_archive_record(self, event):
        data_x = {}
        if 'outTemp' in event.record:
            data_x['outTempDay'], data_x['outTempNight'] = calc_daynighttemps(event.record['outTemp'], event.record['dateTime'])
        else:
            data_x['outTempDay'], data_x['outTempNight'] = (None, None)

        if 'outTemp' in event.record and 'outHumidity' in event.record:
            data_x['summersimmerIndex'] = weewx.wxformulas.sumsimIndex_C(event.record['outTemp'], event.record['outHumidity'])
        else:
            data_x['summersimmerIndex'] = None

        if 'outTemp' in event.record and 'pressure' in event.record:
            data_x['densityA'] = weewx.wxformulas.da_Metric(event.record['outTemp'], event.record['pressure'])
        else:
            data_x['densityA'] = None

        if 'outTemp' in event.record:
            data_x['heatdeg'] = weewx.wxformulas.heating_degrees(event.record['outTemp'], 18.333)
        else:
            data_x['heatdeg'] = None

        if 'outTemp' in event.record:
            data_x['cooldeg'] = weewx.wxformulas.cooling_degrees(event.record['outTemp'], 18.333)
        else:
            data_x['cooldeg'] = None

        if 'outTemp' in event.record:
            data_x['homedeg'] = weewx.wxformulas.heating_degrees(event.record['outTemp'], 15.0)
        else:
            data_x['homedeg'] = None

        if 'outTemp' in event.record:
            data_x['wdd_deg'] = weewx.wxformulas.heating_degrees(event.record['outTemp'], 10.0)
        else:
            data_x['wdd_deg'] = None

        if 'outTemp' in event.record:
            data_x['SVP'] = weewx.uwxutils.TWxUtils.SaturationVaporPressure(event.record['outTemp'])
        else:
            data_x['SVP'] = None

        if 'inTemp' in event.record:
            data_x['SVPin'] = weewx.uwxutils.TWxUtils.SaturationVaporPressure(event.record['inTemp'])
        else:
            data_x['SVPin'] = None

        if 'outTemp' in event.record and 'outHumidity' in event.record:
            data_x['AVP'] = event.record['outHumidity'] * (weewx.uwxutils.TWxUtils.SaturationVaporPressure(event.record['outTemp'])) / 100.0
        else:
            data_x['AVP'] = None

        if 'inTemp' in event.record and 'inHumidity' in event.record:
            data_x['AVPin'] = event.record['inHumidity'] * (weewx.uwxutils.TWxUtils.SaturationVaporPressure(event.record['inTemp'])) / 100.0
        else:
            data_x['AVPin'] = None

        if 'outTemp' in event.record:
            data_x['GDD4'] = weewx.wxformulas.cooling_degrees(event.record['outTemp'], 4.0)
        else:
            data_x['GDD4'] = None

        if 'outTemp' in event.record:
            data_x['GDD6'] = weewx.wxformulas.cooling_degrees(event.record['outTemp'], 6.0)
        else:
            data_x['GDD6'] = None

        if 'outTemp' in event.record:
            data_x['GDD10'] = weewx.wxformulas.cooling_degrees(event.record['outTemp'], 10.0)
        else:
            data_x['GDD10'] = None


        event.record.update(data_x)

#===============================================================================
#                              Class WdArchive
#===============================================================================

class WdArchive(weewx.engine.StdService):
    """ Service to store Weewx-WD specific archive data. """

    def __init__(self, engine, config_dict):
        super(WdArchive, self).__init__(engine, config_dict)

        # Extract our binding from the Weewx-WD section of the config file. If
        # it's missing, fill with a default
        if 'WeewxWD' in config_dict:
            self.data_binding = config_dict['WeewxWD'].get('data_binding', 'wd_binding')
        else:
            self.data_binding = 'wd_binding'

        # Extract the Weewx binding for use when we check the need for backfill
        # from the Weewx archive
        if 'StdArchive' in config_dict:
            self.data_binding_wx = config_dict['StdArchive'].get('data_binding', 'wx_binding')
        else:
            self.data_binding_wx = 'wx_binding'

        loginf("WdArchive:", "WdArchive will use data binding %s" % self.data_binding)

        # setup our database if needed
        self.setup_database(config_dict)

        # set the unit groups for our obs
        obs_group_dict["humidex"] = "group_temperature"
        obs_group_dict["appTemp"] = "group_temperature"
        obs_group_dict["summersimmerIndex"] = "group_temperature"
        obs_group_dict["outTempDay"] = "group_temperature"
        obs_group_dict["outTempNight"] = "group_temperature"
        obs_group_dict['densityA'] = "group_altitude"

        # bind ourselves to NEW_ARCHIVE_RECORD event
        self.bind(weewx.NEW_ARCHIVE_RECORD, self.new_archive_record)


    def new_archive_record(self, event):
        """Called when a new archive record has arrived.

           Use our manager's addRecord method to save the relevant Weewx-WD
           fields to Weewx-WD archive.
        """

        # get our manager
        dbmanager = self.engine.db_binder.get_manager(self.data_binding)
        # now put the record in the archive
        dbmanager.addRecord(event.record)

    def setup_database(self, config_dict):
        """Setup the main database archive"""

        # This will create the database if it doesn't exist, then return an
        # opened instance of the database manager.
        dbmanager = self.engine.db_binder.get_manager(self.data_binding, initialize=True)
        loginf("WdArchive:", "Using binding '%s' to database '%s'" % (self.data_binding, dbmanager.database_name))

        # Check if we have any historical data to suck in from Weewx main archive
        # get a dbmanager for the Weewx archive
        dbmanager_wx = self.engine.db_binder.get_manager(self.data_binding_wx, initialize=False)


        # Back fill the daily summaries.
        loginf("WdArchive:", "Starting backfill of daily summaries")
        t1 = time.time()
        nrecs, ndays = dbmanager.backfill_day_summary()
        tdiff = time.time() - t1
        if nrecs:
            loginf("WdArchive:", "Processed %d records to backfill %d day summaries in %.2f seconds" % (nrecs, ndays, tdiff))
        else:
            loginf("WdArchive:", "Daily summaries up to date.")

#===============================================================================
#                              Class WeeArchive
#===============================================================================

class WeeArchive(weewx.engine.StdService):
    """ Service to store Weewx-WEE specific archive data. """

    def __init__(self, engine, config_dict):
        super(WeeArchive, self).__init__(engine, config_dict)

        # Extract our binding from the Weewx-WEE section of the config file. If
        # it's missing, fill with a default
        if 'WeewxArchive' in config_dict:
            self.data_binding = config_dict['WeewxArchive'].get('data_binding', 'wee_binding')
        else:
            self.data_binding = 'wee_binding'

        loginf("Weewx-Archive:", "Weewx-Archive will use data binding %s" % self.data_binding)

        # setup our database if needed
        self.setup_database(config_dict)

        # bind ourselves to NEW_ARCHIVE_RECORD event
        self.bind(weewx.NEW_ARCHIVE_RECORD, self.new_archive_record)


    def new_archive_record(self, event):
        """Called when a new archive record has arrived. """

        # get our manager
        dbmanager = self.engine.db_binder.get_manager(self.data_binding)
        # now put the record in the archive
        dbmanager.addRecord(event.record)

    def setup_database(self, config_dict):
        """Setup the main database archive"""

        # This will create the database if it doesn't exist, then return an
        # opened instance of the database manager.
        dbmanager = self.engine.db_binder.get_manager(self.data_binding, initialize=True)
        loginf("Weewx-Archive:", "Using binding '%s' to database '%s'" % (self.data_binding, dbmanager.database_name))


#===============================================================================
#                           Class WdGenerateDerived
#===============================================================================

class WdGenerateDerived(object):
    """ Generator wrapper. Adds Weewx-WD derived obs to the output of the
        wrapped generator.
    """

    def __init__(self, input_generator):
        """ Initialize an instance of WdGenerateDerived

            input_generator: An iterator which will return dictionary records.
        """
        self.input_generator = input_generator

    def __iter__(self):
        return self

    """ Initialize copy weewx.
    def next(self):
        # get our next record
        _rec = self.input_generator.next()
        _re_wee = weewx.units.to_METRICWX(_rec)

        _re_wee['dateTime'] = _re_wee['dateTime']
        _re_wee['usUnits'] = _re_wee['usUnits']
        _re_wee['interval'] = _re_wee['interval']
        _re_wee['barometer'] = _re_wee['barometer']
        _re_wee['pressure'] = _re_wee['pressure']
        _re_wee['altimeter'] = _re_wee['altimeter']
        _re_wee['inTemp'] = _re_wee['inTemp']
        _re_wee['outTemp'] = _re_wee['outTemp']
        _re_wee['inHumidity'] = _re_wee['inHumidity']
        _re_wee['outHumidity'] = _re_wee['outHumidity']
        _re_wee['windSpeed'] = _re_wee['windSpeed']
        _re_wee['windDir'] = _re_wee['windDir']
        _re_wee['windGust'] = _re_wee['windGust']
        _re_wee['windGustDir'] = _re_wee['windGustDir']
        _re_wee['rainRate'] = _re_wee['rainRate']
        _re_wee['rain'] = _re_wee['rain']
        _re_wee['stormRain'] = _re_wee['stormRain']
        _re_wee['dewpoint'] = _re_wee['dewpoint']
        _re_wee['windchill'] = _re_wee['windchill']
        _re_wee['heatindex'] = _re_wee['heatindex']
        _re_wee['ET'] = _re_wee['ET']
        _re_wee['radiation'] = _re_wee['radiation']
        _re_wee['UV'] = _re_wee['UV']
        _re_wee['extraTemp1'] = _re_wee['extraTemp1']
        _re_wee['extraTemp2'] = _re_wee['extraTemp2']
        _re_wee['extraTemp3'] = _re_wee['extraTemp3']
        _re_wee['soilTempO1'] = _re_wee['soilTempO1']
        _re_wee['soilTempO2'] = _re_wee['soilTempO2']
        _re_wee['soilTempO3'] = _re_wee['soilTempO3']
        _re_wee['soilTempO4'] = _re_wee['soilTempO4']
        _re_wee['soilTempO5'] = _re_wee['soilTempO5']
        _re_wee['leafTemp1'] = _re_wee['leafTemp1']
        _re_wee['leafTemp2'] = _re_wee['leafTemp2']
        _re_wee['extraHumid1'] = _re_wee['extraHumid1']
        _re_wee['extraHumid2'] = _re_wee['extraHumid2']
        _re_wee['soilMoist1'] = _re_wee['soilMoist1']
        _re_wee['soilMoist2'] = _re_wee['soilMoist2']
        _re_wee['soilMoist3'] = _re_wee['soilMoist3']
        _re_wee['soilMoist4'] = _re_wee['soilMoist4']
        _re_wee['leafWet1'] = _re_wee['leafWet1']
        _re_wee['leafWet2'] = _re_wee['leafWet2']
        _re_wee['rxCheckPercent'] = _re_wee['rxCheckPercent']
        _re_wee['txBatteryStatus'] = _re_wee['txBatteryStatus']
        _re_wee['consBatteryVoltage'] = _re_wee['consBatteryVoltage']
        _re_wee['hail'] = _re_wee['hail']
        _re_wee['hailRate'] = _re_wee['hailRate']
        _re_wee['heatingTemp'] = _re_wee['heatingTemp']
        _re_wee['heatingVoltage'] = _re_wee['heatingVoltage']
        _re_wee['supplyVoltage'] = _re_wee['supplyVoltage']
        _re_wee['referenceVoltage'] = _re_wee['referenceVoltage']
        _re_wee['windBatteryStatus'] = _re_wee['windBatteryStatus']
        _re_wee['rainBatteryStatus'] = _re_wee['rainBatteryStatus']
        _re_wee['outTempBatteryStatus'] = _re_wee['outTempBatteryStatus']
        _re_wee['lighting'] = _re_wee['lighting']
        _re_wee['extraTemp4'] = _re_wee['extraTemp4']
        _re_wee['extraTemp5'] = _re_wee['extraTemp5']
        _re_wee['extraTemp6'] = _re_wee['extraTemp6']
        _re_wee['extraTemp7'] = _re_wee['extraTemp7']
        _re_wee['extraTemp8'] = _re_wee['extraTemp8']
        _re_wee['extraTemp9'] = _re_wee['extraTemp9']
        _re_wee['maxSolarRad'] = _re_wee['maxSolarRad']
        _re_wee['cloudbase'] = _re_wee['cloudbase']
        _re_wee['humidex'] = _re_wee['humidex']
        _re_wee['appTemp'] = _re_wee['appTemp']
        _re_wee['windrun'] = _re_wee['windrun']
        _re_wee['beaufort'] = _re_wee['beaufort']
        _re_wee['inDewpoint'] = _re_wee['inDewpoint']
        _re_wee['inTempBatteryStatus'] = _re_wee['inTempBatteryStatus']
        _re_wee['absolutF'] = _re_wee['absolutF']
        _re_wee['sunshineS'] = _re_wee['sunshineS']
        _re_wee['snow'] = _re_wee['snow']
        _re_wee['snowRate'] = _re_wee['snowRate']
        _re_wee['snowTotal'] = _re_wee['snowTotal']
        _re_wee['wetBulb'] = _re_wee['wetBulb']
        _re_wee['cbIndex'] = _re_wee['cbIndex']
        _re_wee['airDensity'] = _re_wee['airDensity']
        _re_wee['windDruck'] = _re_wee['windDruck']
        _re_wee['soilTemp1'] = _re_wee['soilTemp1']
        _re_wee['soilTemp2'] = _re_wee['soilTemp2']
        _re_wee['soilTemp3'] = _re_wee['soilTemp3']
        _re_wee['soilTemp4'] = _re_wee['soilTemp4']
        _re_wee['soilTemp5'] = _re_wee['soilTemp5']
        _re_wee['dampfDruck'] = _re_wee['dampfDruck']
        _re_wee['summersimmerIndex'] = _re_wee['summersimmerIndex']
        _re_wee['SVP'] = _re_wee['SVP']
        _re_wee['SVPin'] = _re_wee['SVPin']
        _re_wee['AVP'] = _re_wee['AVP']
        _re_wee['AVPin'] = _re_wee['AVPin']
        _re_wee['densityA'] = _re_wee['densityA']

        data_x = weewx.units.to_std_system(_re_wee, _rec['usUnits'])
        # return our modified record
        return data_x
        """ 

    def __next__(self):
        # get our next record
        _rec = next(self.input_generator)
        _rec_mwx = weewx.units.to_METRICWX(_rec)

        # get our historical humidex, if not available then calculate it
        #if _rec_mwx['extraTemp1'] is not None:
        #    _rec_mwx['humidex'] = _rec_mwx['extraTemp1']
        #else:
        if 'outTemp' in _rec_mwx and 'outHumidity' in _rec_mwx:
            _rec_mwx['humidex'] = weewx.wxformulas.humidexC(_rec_mwx['outTemp'],
                                                                _rec_mwx['outHumidity'])
        else:
            _rec_mwx['humidex'] = None

        # get our historical appTemp, if not available then calculate it
        #if _rec_mwx['extraTemp2'] is not None:
        #    _rec_mwx['appTemp'] = _rec_mwx['extraTemp2']
        #else:
        if 'outTemp' in _rec_mwx and 'outHumidity' in _rec_mwx and 'windSpeed' in _rec_mwx:
            _rec_mwx['appTemp'] = weewx.wxformulas.apptempC(_rec_mwx['outTemp'],
                                                                _rec_mwx['outHumidity'],
                                                                _rec_mwx['windSpeed'])
        else:
            _rec_mwx['appTemp'] = None

        # 'calculate' summersimmerIndex
        if 'outTemp' in _rec_mwx and 'outHumidity' in _rec_mwx:
            _rec_mwx['summersimmerIndex'] = weewx.wxformulas.sumsimIndex_C(_rec_mwx['outTemp'], _rec_mwx['outHumidity'])
        else:
            _rec_mwx['summersimmerIndex'] = None


        # 'calculate' outTempNight
        if 'outTemp' in _rec_mwx:
            _rec_mwx['outTempDay'], _rec_mwx['outTempNight'] = calc_daynighttemps(_rec_mwx['outTemp'], _rec_mwx['dateTime'])
        else:
            _rec_mwx['outTempDay'], _rec_mwx['outTempNight'] = (None, None)


        if 'outTemp' in _rec_mwx:
            _rec_mwx['heatdeg'] = weewx.wxformulas.heating_degrees(_rec_mwx['outTemp'], 18.333)
        else:
            _rec_mwx['heatdeg'] = None

        if 'outTemp' in _rec_mwx:
            _rec_mwx['cooldeg'] = weewx.wxformulas.cooling_degrees(_rec_mwx['outTemp'], 18.333)
        else:
            _rec_mwx['cooldeg'] = None

        if 'outTemp' in _rec_mwx:
            _rec_mwx['homedeg'] = weewx.wxformulas.cooling_degrees(_rec_mwx['outTemp'], 15.0)
        else:
            _rec_mwx['homedeg'] = None

        if 'outTemp' in _rec_mwx:
            _rec_mwx['SVP'] = weewx.uwxutils.TWxUtils.SaturationVaporPressure(_rec_mwx['outTemp'])
        else:
            _rec_mwx['SVP'] = None

        if 'inTemp' in _rec_mwx:
            _rec_mwx['SVPin'] = weewx.uwxutils.TWxUtils.SaturationVaporPressure(_rec_mwx['inTemp'])
        else:
            _rec_mwx['SVPin'] = None

        if 'outTemp' in _rec_mwx and 'outHumidity' in _rec_mwx:
            _rec_mwx['AVP'] = _rec_mwx['outHumidity'] * (weewx.uwxutils.TWxUtils.SaturationVaporPressure(_rec_mwx['outTemp'])) / 100.0
        else:
            _rec_mwx['AVP'] = None

        if 'inTemp' in _rec_mwx and 'inHumidity' in _rec_mwx:
            _rec_mwx['AVPin'] = _rec_mwx['inHumidity'] * (weewx.uwxutils.TWxUtils.SaturationVaporPressure(_rec_mwx['inTemp'])) / 100.0
        else:
            _rec_mwx['AVPin'] = None

        if 'outTemp' in _rec_mwx:
            _rec_mwx['wdd_deg'] = weewx.wxformulas.heating_degrees(_rec_mwx['outTemp'], 10.0)
        else:
            _rec_mwx['wdd_deg'] = None

        if 'outTemp' in _rec_mwx:
            _rec_mwx['densityA'] = weewx.wxformulas.da_Metric(_rec_mwx['outTemp'], _rec_mwx['pressure'])
        else:
            _rec_mwx['densityA'] = None


        # 'calculate' Green DayDegrees 4 6 10
        if 'outTemp' in _rec_mwx:
            _rec_mwx['GDD4'] = weewx.wxformulas.cooling_degrees(_rec_mwx['outTemp'], 4.0)
        else:
            _rec_mwx['GDD4'] = None

        if 'outTemp' in _rec_mwx:
            _rec_mwx['GDD6'] = weewx.wxformulas.cooling_degrees(_rec_mwx['outTemp'], 6.0)
        else:
            _rec_mwx['GDD6'] = None


        if 'outTemp' in _rec_mwx:
            _rec_mwx['GDD10'] = weewx.wxformulas.cooling_degrees(_rec_mwx['outTemp'], 10.0)
        else:
            _rec_mwx['GDD10'] = None



        data_x = weewx.units.to_std_system(_rec_mwx, _rec['usUnits'])
        # return our modified record
        return data_x

#===============================================================================
#                             Class wdSuppThread
#===============================================================================

class wdSuppThread(threading.Thread):
    """ Thread in which to run WdSuppArchive service.

        As we need to obtain WU data via WU API query we need to run this in
        another thread so as to not hold up Weewx if we have a slow connection
        or WU is unresponsive for any reason.
    """

    def __init__(self, target, *args):
        self._target = target
        self._args = args
        threading.Thread.__init__(self)

    def run(self):
        self._target(*self._args)

#===============================================================================
#                            Class WdSuppArchive
#===============================================================================

class WdSuppArchive(weewx.engine.StdService):
    """ Service to obtain and archive WU API sourced data and Davis console
        forecast/storm data as well as archive theoretical max solar
        radiation data. Data is only kept for a limited time before being
        dropped.
    """

    def __init__(self, engine, config_dict):
        super(WdSuppArchive, self).__init__(engine, config_dict)

        # Initialisation is 2 part; 1 part for wdsupp db/loop data, 2nd part
        # for WU API calls. We are only going to invoke ourself if we have the
        # necessary config data available in weewx.conf for 1 or both parts.
        # If any essential config data is missing/not set then give a short log
        # message and defer.

        if 'Weewx-WD' in config_dict:
            # we have a [Weewx-WD} stanza
            if 'Supplementary' in config_dict['Weewx-WD']:
                # we have a [[Supplementary]] stanza so we can initialise wdsupp db
                # get our binding, if it's missing use a default
                self.binding = config_dict['Weewx-WD']['Supplementary'].get('data_binding', 'wdsupp_binding')
                loginf("WdSuppArchive:", "WdSuppArchive will use data binding '%s'" % self.binding)
                # how long to keep records in our db (default 8 days)
                self.max_age = config_dict['Weewx-WD']['Supplementary'].get('max_age', 691200)
                self.max_age = toint('max_age', self.max_age, 691200)
                # how often to vacuum the sqlite database (default 24 hours)
                self.vacuum = config_dict['Weewx-WD']['Supplementary'].get('vacuum', 86400)
                self.vacuum = toint('vacuum', self.vacuum, 86400)
                # how many times do we retry database failures (default 3)
                self.db_max_tries = config_dict['Weewx-WD']['Supplementary'].get('database_max_tries', 3)
                self.db_max_tries = int(self.db_max_tries)
                # how long to wait between retries (default 2 sec)
                self.db_retry_wait = config_dict['Weewx-WD']['Supplementary'].get('database_retry_wait', 2)
                self.db_retry_wait = int(self.db_retry_wait)

                # initialise a few things
                # setup our database if needed
                self.setup_database(config_dict)
                # ts at which we last vacuumed
                self.last_vacuum = None
                # create holder for Davis Console loop data
                self.loop_packet = {}

                # set the unit groups for our obs
                obs_group_dict["tempRecordHigh"] = "group_temperature"
                obs_group_dict["tempNormalHigh"] = "group_temperature"
                obs_group_dict["tempRecordLow"] = "group_temperature"
                obs_group_dict["tempNormalLow"] = "group_temperature"
                obs_group_dict["tempRecordHighYear"] = "group_count"
                obs_group_dict["tempRecordLowYear"] = "group_count"
                obs_group_dict["stormRain"] = "group_rain"
                obs_group_dict["stormStart"] = "group_time"
                obs_group_dict["maxSolarRad"] = "group_radiation"
                obs_group_dict["forecastIcon"] = "group_count"
                obs_group_dict["currentIcon"] = "group_count"
                obs_group_dict["vantageForecastIcon"] = "group_count"
                obs_group_dict["visibility_km"] = "group_distance"
                obs_group_dict["pop"] = "group_count"
                obs_group_dict["vantageForecastNumber"] = "group_count"

                # event bindings
                # bind to NEW_LOOP_PACKET so we can capture Davis Vantage forecast
                # data
                self.bind(weewx.NEW_LOOP_PACKET, self.new_loop_packet)

                # bind to NEW_ARCHIVE_RECORD to ensure we have a chance to:
                # - update WU data(if necessary)
                # - save our data
                # on each new record
                self.bind(weewx.NEW_ARCHIVE_RECORD, self.new_archive_record)

            # do we have necessary config info for WU ie a [[[WU]]] stanza,
            # apiKey and location
            _wu_dict = check_enable(config_dict['Weewx-WD']['Supplementary'], 'WU', 'apiKey')
            if _wu_dict is None:
                # we are missing some/all essential WU API settings so set a
                # flag and return
                self.do_WU = False
                loginf("WdSuppArchive:", "WU API calls will not be made")
                loginf("              ", "**** Incomplete or missing config settings")
                return

            # if we got this far we have the essential WU API settings so carry
            # on with the rest of the initialisation
            # set a flag indicating we are doing WU API queries
            self.do_WU = True
            # get station info required for almanac/Sun related calcs
            self.latitude = float(config_dict['Station']['latitude'])
            self.longitude = float(config_dict['Station']['longitude'])
            self.altitude = convert(engine.stn_info.altitude_vt, 'meter')[0]
            # create a list of the WU API calls we need
            self.WU_queries = WU_queries
            # set interval between API calls for each API call type we need
            for q in self.WU_queries:
                q['interval'] = int(config_dict['Weewx-WD']['Supplementary']['WU'].get(q['name'] + '_interval', q['def_interval']))
            # Set max no of tries we will make in any one attempt to contact WU via API
            self.max_WU_tries = config_dict['Weewx-WD']['Supplementary']['WU'].get('max_WU_tries', 3)
            self.max_WU_tries = toint('max_WU_tries', self.max_WU_tries, 3)
            # set API call lockout period in sec (default 60 sec). refer weewx.conf
            self.api_lockout_period = config_dict['Weewx-WD']['Supplementary']['WU'].get('api_lockout_period', 60)
            self.api_lockout_period = toint('api_lockout_period', self.api_lockout_period, 60)
            # create holder for last WU API call ts
            self.last_WU_query = None
            # Get our API key from weewx.conf, we know we have something in
            # [Weewx-WD] but it could be None. If this is the case try
            # [Forecast] if it exists. [Weewx-WD] should not throw an exception
            # but [Forecast] may so wrap in a try..except loop to catch any
            # exceptions (eg [Forecast][WU]apiKey does not exist).
            try:
                if config_dict['Weewx-WD']['Supplementary']['WU'].get('apiKey', None) != None:
                    self.api_key = config_dict['Weewx-WD']['Supplementary']['WU'].get('apiKey')
                elif config_dict['Forecast']['WU'].get('api_key', None) != None:
                    self.api_key = config_dict['Forecast']['WU'].get('api_key')
                else:
                    loginf("WdSuppArchive:", "Cannot find valid Weather Underground API key")
                    loginf("              ", "**** Incomplete or missing config settings")
            except:
                loginf("WdSuppArchive:", "Cannot find Weather Underground API key")
                loginf("              ", "**** Incomplete or missing config settings")
            # get our 'location' for use in WU API calls. Default to station
            # lat/long.
            self.location = config_dict['Weewx-WD']['Supplementary']['WU'].get('location', '%s,%s' % (self.latitude, self.longitude))
            if self.location == 'replace_me':
                self.location = '%s,%s' % (self.latitude, self.longitude)
            # set fixed part of WU API call url
            self.default_url = 'http://api.wunderground.com/api'
            # we have everything we need to put a short message in the log with
            # a partially masked API key
            loginf("WdSuppArchive:", 'max_age=%s vacuum=%s, WU API calls will be made' % (self.max_age, self.vacuum))
            _msg = ''
            for _wuq in self.WU_queries:
                _msg += _wuq['name'] + ' interval=' + '%s ' % (_wuq['interval'],)
            loginf("WdSuppArchive:", _msg)
            loginf("WdSuppArchive:", 'api_key=%s location=%s' % ('xxxxxxxxxxxx' + self.api_key[-4:], self.location))

    def new_archive_record(self, event):
        """ Kick off in a new thread.
        """

        t = wdSuppThread(self.wdSupp_main, event)
        t.setName('wdSuppThread')
        t.start()

    def wdSupp_main(self, event):
        """ Take care of getting our data, archiving it and completing any
            database housekeeping.

            If we are making WU API calls then step through each of our WU API
            calls, obtain and parse our results. Grab any forecast/storm loop
            data and theoretical max solar radiation> Archive our data, delete
            any stale records and 'vacuum' the database if required.
        """

        # get time now as a ts
        now = time.time()
        # create a holder dict for our data record
        _data_record = {}
        # prepopulate it with a few things we know now
        _data_record['dateTime'] = event.record['dateTime']
        _data_record['usUnits'] = event.record['usUnits']
        _data_record['interval'] = event.record['interval']

        # get our WU data if we are setup for WU
        if self.do_WU:
            # get ts of record about to be processed
            rec_ts = event.record['dateTime']
            # almanac gives more accurate results with current temp and pressure
            # initialise some defaults
            temperature_C = 15.0
            pressure_mbar = 1010.0
            # get current outTemp and barometer if they exist
            if 'outTemp' in event.record:
                temperature_C = weewx.units.convert(weewx.units.as_value_tuple(event.record, 'outTemp'),
                                                    "degree_C")[0]
            if 'barometer' in event.record:
                pressure_mbar = weewx.units.convert(weewx.units.as_value_tuple(event.record, 'barometer'),
                                                    "mbar")[0]
            # get our almanac object
            self.almanac = weewx.almanac.Almanac(rec_ts, self.latitude,
                                                 self.longitude,
                                                 self.altitude,
                                                 temperature_C,
                                                 pressure_mbar)
            # work out sunrise and sunset ts so we can determine if it is night or day. Needed so
            # we can set day or night icons when translating WU icons to Saratoga icons
            sunrise_ts = self.almanac.sun.rise.raw
            sunset_ts = self.almanac.sun.set.raw
            # if we are not between sunrise and sunset it must be night
            self.night = not (sunrise_ts < rec_ts < sunset_ts)
            # get the fully constructed URL for those API feature calls that
            # are to be made
            _WU_URL, _features = self.construct_WU_URL(now)
            _response = None
            if _WU_URL is not None:
                if self.last_WU_query is None or ((now + 1 - self.api_lockout_period) >= self.last_WU_query):
                    # if we haven't made this API call previously or if its been too long since
                    # the last call then make the call, wrap in a try..except just in case
                    try:
                        _response = self.get_WU_response(_WU_URL,
                                                         self.max_WU_tries)
                        logdbg2("WdSuppArchive:", "Downloaded updated Weather Underground information for %s" % (_features,))
                        loginf("WdSuppArchive:", "Downloaded updated Weather Underground information for %s" % (_features,))
                    except Exception as e:
                        loginf("WdSuppArchive:", "Weather Underground API query failure: %s" % (e, ))
                    self.last_WU_query = max(q['last'] for q in self.WU_queries)
                else:
                    # API call limiter kicked in so say so
                    loginf("WdSuppArchive:", "API call limit reached. Tried to make an API call within %d sec of the previous call. API call skipped." % (self.api_lockout_period, ))
            # parse the WU responses and put into a dictionary
            _wu_record = self.parse_WU_response(_response, _data_record['usUnits'])
            # update our data record with any WU data
            _data_record.update(_wu_record)

        # process data from latest loop packet
        _data_loop = self.process_loop()
        # update our data record with any loop data
        _data_record.update(_data_loop)

        # get a dictionary for our database manager
        dbm_dict = weewx.manager.get_manager_dict_from_config(self.config_dict,
                                                              self.binding)
        with weewx.manager.open_manager(dbm_dict) as dbm:
            # save our data
            self.save_record(dbm, _data_record, self.db_max_tries, self.db_retry_wait)
            # set ts of last packet processed
            self.last_ts = _data_record['dateTime']
            # prune older packets and vacuum if required
            if self.max_age > 0:
                self.prune(dbm, self.last_ts - self.max_age,
                           self.db_max_tries,
                           self.db_retry_wait)
                # vacuum the database
                if self.vacuum > 0:
                    if self.last_vacuum is None or ((now + 1 - self.vacuum) >= self.last_vacuum):
                        self.vacuum_database(dbm)
                        self.last_vacuum = now
        return

    def construct_WU_URL(self, now):
        """ Construct a multi-feature WU API URL

            WU API allows multiple feature requests to be combined into a single
            http request (thus cutting down on API calls. Look at each of our WU
            queries then construct and return a WU API URL string that will
            request all features that are due. If no features are due then
            return None.
        """

        _feature_string = ''
        for _wuq in self.WU_queries:
            # if we haven't made this feature request previously or if its been
            # too long since the last call then make the call
            if (_wuq['last'] is None) or ((now + 1 - _wuq['interval']) >= _wuq['last']):
                # we need to request this feature so add the feature code to our
                # feature string
                if len(_feature_string) > 0:
                    _feature_string += '/' + _wuq['name']
                else:
                    _feature_string += _wuq['name']
                _wuq['last'] = now
        if len(_feature_string) > 0:
            # we have a feature we need so construct the URL
            url = '%s/%s/%s/lang:DL/pws:1/q/%s.json' % (self.default_url, self.api_key,
                                                _feature_string, self.location)
            return (url, _feature_string)
        return (None, None)

    def get_WU_response(self, WU_URL, max_WU_tries):
        """ Make a WU API call and return the raw response.
        """

        # we will attempt the call max_WU_tries times
        for count in range(max_WU_tries):
            # attempt the call
            try:
                #w = urllib.request.urlopen(WU_URL)
                w = urlopen(WU_URL)
                _WUresponse = w.read()
                w.close()
                return _WUresponse
            except Exception as e:
                loginf("WdSuppArchive:", "Failed to get Weather Underground API response on attempt %d: %s" % (count + 1, e))
        else:
            loginf("WdSuppArchive:", "Failed to get Weather Underground API response")
        return None

    def parse_WU_response(self, response, units):
        """ Parse a potentially multi-feature API response and construct a data
            dict with the required fields.
        """

        # Create a holder dict for the data we will gather
        _data = {}
        # Do some pre-processing and error checking
        if response is not None:
            # We have a response
            # Deserialise our JSON response
            _json_response = json.loads(response)
            # Check for recognised format
            if not 'response' in _json_response:
                loginf("WdSuppArchive:", "Unknown format in Weather Underground API response")
                return _data
            # Get the WU 'response' field so we can check for errors
            _response = _json_response['response']
            # Check for WU provided error otherwise start pulling in the fields/data we want
            if 'error' in _response:
                loginf("WdSuppArchive:", "Error in Weather Underground API response")
                return _data
            # Pull out our individual 'feature' responses, this way in the
            # future we can populate our results even if we did not get a
            # 'feature' response that time round
            for _wuq in self.WU_queries:
                if _wuq['json_title'] in _json_response:
                    _wuq['response'] = _json_response[_wuq['json_title']]
        # Step through each of possible queries and parse as required
        for _wuq in self.WU_queries:
            # Forecast data
            if _wuq['name'] == 'forecast' and _wuq['response'] is not None:
                # Look up Saratoga icon number given WU icon name
                _data['forecastIcon'] = icon_dict[_wuq['response']['txt_forecast']['forecastday'][0]['icon']]
                _data['forecastText'] = _wuq['response']['txt_forecast']['forecastday'][0]['fcttext']
                _data['forecastTextMetric'] = _wuq['response']['txt_forecast']['forecastday'][0]['fcttext_metric']
                _data['pop'] = _wuq['response']['txt_forecast']['forecastday'][0]['pop']
            # Conditions data
            elif _wuq['name'] == 'conditions' and _wuq['response'] is not None:
                # WU does not seem to provide day/night icon name in their 'conditions' response so we
                # need to do. Just need to add 'nt_' to front of name before looking up in out Saratoga
                # icons dictionary
                #if self.night:
                #    _data['currentIcon'] = icon_dict['nt_' + _wuq['response']['icon']]
                #else:
                _data['currentIcon'] = icon_dict[_wuq['response']['icon']]
                _data['currentText'] = _wuq['response']['weather']
                _data['visibility_km'] = _wuq['response']['visibility_km']
            # Almanac data
            elif _wuq['name'] == 'almanac' and _wuq['response'] is not None:
                if units is weewx.US:
                    _data['tempRecordHigh'] = _wuq['response']['temp_high']['record']['F']
                    _data['tempNormalHigh'] = _wuq['response']['temp_high']['normal']['F']
                    _data['tempRecordLow'] = _wuq['response']['temp_low']['record']['F']
                    _data['tempNormalLow'] = _wuq['response']['temp_low']['normal']['F']
                else:
                    _data['tempRecordHigh'] = _wuq['response']['temp_high']['record']['C']
                    _data['tempNormalHigh'] = _wuq['response']['temp_high']['normal']['C']
                    _data['tempRecordLow'] = _wuq['response']['temp_low']['record']['C']
                    _data['tempNormalLow'] = _wuq['response']['temp_low']['normal']['C']
                _data['tempRecordHighYear'] = _wuq['response']['temp_high']['recordyear']
                _data['tempRecordLowYear'] = _wuq['response']['temp_low']['recordyear']
        return _data

    def process_loop(self):
        """ Process latest loop data and populate fields as appropriate.

            Adds following fields (if available) to data dictionary:
                - forecast icon (Vantage only)
                - forecast rule (Vantage only)(Note returns full text forecast)
                - stormRain (Vantage only)
                - stormStart (Vantage only)
                - current theoretical max solar radiation
        """

        # holder dictionary for our gathered data
        _data = {}
        # Vantage forecast icon
        if 'forecastIcon' in self.loop_packet:
            _data['vantageForecastIcon'] = self.loop_packet['forecastIcon']
        # Vantage forecast rule
        if 'forecastRule' in self.loop_packet:
            try:
                _data['vantageForecastRule'] = davis_fr_dict[self.loop_packet['forecastRule']]
                _data['vantageForecastNumber'] = self.loop_packet['forecastRule']
            except:
                _data['vantageForecastRule'] = ""
                logdbg2("WdSuppArchive:", 'Could not decode Vantage forecast code')
        # Vantage stormRain
        if 'stormRain' in self.loop_packet:
            _data['stormRain'] = self.loop_packet['stormRain']
        # Vantage stormStart
        if 'stormStart' in self.loop_packet:
            _data['stormStart'] = self.loop_packet['stormStart']
        # theoretical solar radiation value
        _data['maxSolarRad'] = self.loop_packet['maxSolarRad']
        return _data

    @staticmethod
    def save_record(dbm, _data_record, max_tries = 3, retry_wait = 2):
        """ Save a data record to our database.
        """

        for count in range(max_tries):
            try:
                # save our data to the database
                dbm.addRecord(_data_record)
                break
            except Exception as e:
                logerr("WdSuppArchive:", 'save failed (attempt %d of %d): %s' %
                       ((count + 1), max_tries, e))
                logerr("WdSuppArchive:", 'waiting %d seconds before retry' % (retry_wait, ))
                time.sleep(retry_wait)
        else:
            raise Exception('save failed after %d attempts' % max_tries)

    @staticmethod
    def prune(dbm, ts, max_tries = 3, retry_wait = 2):
        """ Remove records older than ts from the database.
        """

        sql = "delete from %s where dateTime < %d" % (dbm.table_name, ts)
        for count in range(max_tries):
            try:
                dbm.getSql(sql)
                break
            except Exception as e:
                logerr("WdSuppArchive:", 'prune failed (attempt %d of %d): %s' % ((count+1), max_tries, e))
                logerr("WdSuppArchive:", 'waiting %d seconds before retry' % (retry_wait, ))
                time.sleep(retry_wait)
        else:
            raise Exception('prune failed after %d attemps' % max_tries)
        return

    @staticmethod
    def vacuum_database(dbm):
        """ Vacuum our database to save space.
        """

        # SQLite databases need a little help to prevent them from continually
        # growing in size even though we prune records from the database.
        # Vacuum will only work on SQLite databases.  It will compact the
        # database file. It should be OK to run this on a MySQL database - it
        # will silently fail.

        # remove timing code once we get a handle on how long this takes
        # Get time now as a ts
        t1 = time.time()
        try:
            dbm.getSql('vacuum')
        except Exception as e:
            logerr("WdSuppArchive:", 'Vacuuming database % failed: %s' % (dbm.database_name, e))

        t2 = time.time()
        logdbg("WdSuppArchive:", "vacuum_database executed in %0.9f seconds" % (t2-t1))

    def setup_database(self, config_dict):
        """ Setup the database table we will be using.
        """

        # This will create the database and/or table if either doesn't exist,
        # then return an opened instance of the database manager.
        dbmanager = self.engine.db_binder.get_database(self.binding,
                                                       initialize = True)
        loginf("WdSuppArchive:", "Using binding '%s' to database '%s'" %
                                        (self.binding, dbmanager.database_name))

    def new_loop_packet(self, event):
        """ Save Davis Console forecast data that arrives in loop packets so
            we can save it to archive later.

            The Davis Console forecast data is published in each loop packet.
            There is little benefit in saving this data to database each loop
            period as the data is slow changing so we will stash the data and
            save to database each archive period along with our WU sourced data.
        """

        # update our stashed loop packet data
        # wrap in a try..except just in case
        try:
            if 'forecastIcon' in event.packet:
                self.loop_packet['forecastIcon'] = event.packet['forecastIcon']
            else:
                self.loop_packet['forecastIcon'] = None
            if 'forecastRule' in event.packet:
                self.loop_packet['forecastRule'] = event.packet['forecastRule']
            else:
                self.loop_packet['forecastRule'] = None
            if 'stormRain' in event.packet:
                self.loop_packet['stormRain'] = event.packet['stormRain']
            else:
                self.loop_packet['stormRain'] = None
            if 'stormStart' in event.packet:
                self.loop_packet['stormStart'] = event.packet['stormStart']
            else:
                self.loop_packet['stormStart'] = None
            if 'maxSolarRad' in event.packet:
                self.loop_packet['maxSolarRad'] = event.packet['maxSolarRad']
            else:
                self.loop_packet['maxSolarRad'] = None
        except:
            loginf("WdSuppArchive:", "new_loop_packet: Loop packet data error. Cannot decode packet: %s" % (e, ))

    def shutDown(self):
        pass

#===============================================================================
#                                 Utilities
#===============================================================================

def toint(label, value_tbc, default_value):
    """ Convert value_tbc to an integer whilst handling None.

        If value_tbc cannot be converted to an integer default_value is
        returned.

        Input:
            label:         String with the name of the parameter being set
            value_tbc:     The value to be converted to an integer
            default_value: The value to be returned if value cannot be
                           converted to an integer
    """

    if isinstance(value_tbc, str) and value_tbc.lower() == 'none':
        value_tbc = None
    if value_tbc is not None:
        try:
            value_tbc = int(value_tbc)
        except Exception as e:
            logerr("weewxwd3:toint:", "bad value '%s' for %s" % (value_tbc, label))
            value_tbc = default_value
    return value_tbc

def calc_daynighttemps(temp, dt):
    """ 'Calculate' value for outTempDay and outTempNight.

        outTempDay and outTempNight are used to determine warmest night
        and coldest day stats. This is done by using two derived
        observations; outTempDay and outTempNight. These observations
        are defined as follows:

        outTempDay:   equals outTemp if time of day is > 06:00 and <= 18:00
                      otherwise it is None
        outTempNight: equals outTemp if time of day is > 18:00 or <= 06:00
                      otherwise it is None

        By adding these derived obs to the schema and loop packet the daily
        summaries for these obs are populated and aggregate stats can be
        accessed as per normal (eg $month.outTempDay.minmax to give the
        coldest max daytime temp in the month). Note that any aggregates that
        rely on the number of records (eg avg) will be meaningless due to
        the way outTempxxxx is calculated.
    """

    if temp is not None:
        # check if record covers daytime (6AM to 6PM) and if so add 'temp' to 'outTempDay'
        # remember record timestamped 6AM belongs in the night time
        if datetime.fromtimestamp(dt - 1).hour < 6 or datetime.fromtimestamp(dt - 1).hour > 17:
            # ie the data packet is from before 6am or after 6pm
            return (None, temp)
        else:
            # ie the data packet is from after 6am and before or including 6pm
            return (temp, None)
    else:
        return (None, None)

def check_enable(cfg_dict, service, *args):

    try:
        wdsupp_dict = accumulateLeaves(cfg_dict[service], max_level = 1)
    except KeyError:
        logdbg2("weewxwd3:check_enable:", "%s: No config info. Skipped." % service)
        return None

    # Check to see whether all the needed options exist, and none of them have
    # been set to 'replace_me':
    try:
        for option in args:
            if wdsupp_dict[option] == 'replace_me':
                raise KeyError(option)
    except KeyError as e:
        logdbg2("weewxwd3:check_enable:", "%s: Missing option %s" % (service, e))
        return None

    return wdsupp_dict
