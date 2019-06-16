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
## Version: 1.3.0                                    Date: 1 May 2019
##
## Revision History
##  1 May 2019            v1.3.0    -python 3 delete WU
##  10 August 2015        v1.2.0    -revised for Weewx v3.2.0
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
import math
import os
import time
import ephem

from math import sin
from datetime import datetime

try:
    # Python 3
    from io import StringIO
except ImportError:
    # Python 2
    from StringIO import StringIO

try:
    # Python 3
    from urllib.request import Request, urlopen
except ImportError:
    # Python 2
    from urllib2 import Request, urlopen

try:
    # Python 3
    from urllib.error import URLError
except ImportError:
    # Python 2
    from urllib2 import URLError

try:
    # Python 3
    from http.client import BadStatusLine, IncompleteRead
except ImportError:
    # Python 2
    from httplib import BadStatusLine, IncompleteRead

try:
    import cjson as json
    setattr(json, 'dumps', json.encode)
    setattr(json, 'loads', json.decode)
except (ImportError, AttributeError):
    try:
        import simplejson as json
    except ImportError:
        import json

import weewx
import weedb
import weewx.engine
import weewx.manager
import weewx.wxformulas
import weewx.almanac
import weeutil.weeutil

from weewx.units import convert, obs_group_dict
from weeutil.weeutil import to_bool, accumulateLeaves
from weewx.units import CtoF, CtoK, mps_to_mph, kph_to_mph

WEEWXWD_VERSION = '1.3.0'

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
        193 : 'PROGNOSE ERFORDERT 3 STUNDEN AKTUELLE DATEN',
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

        if 'rain' in event.packet and 'ET' in event.packet:
            data_x['rain_ET'] = event.packet['rain'] - event.packet['ET']
        else:
            data_x['rain_ET'] = None

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
            data_x['GDD10'] = weewx.wxformulas.cooling_degrees(event.packet['outTemp'], 5.0)
        else:
            data_x['GDD10'] = None



        event.packet.update(data_x)

    def new_archive_record(self, event):
        data_x = {}
        if 'outTemp' in event.record:
            data_x['outTempDay'], data_x['outTempNight'] = calc_daynighttemps(event.record['outTemp'], event.record['dateTime'])
        else:
            data_x['outTempDay'], data_x['outTempNight'] = (None, None)

        if 'rain' in event.record and 'ET' in event.record:
            data_x['rain_ET'] = event.record['rain'] - event.record['ET']
        else:
            data_x['rain_ET'] = None

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
            data_x['GDD10'] = weewx.wxformulas.cooling_degrees(event.record['outTemp'], 5.0)
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
        obs_group_dict["outTempDay"] = "group_temperature"
        obs_group_dict["outTempNight"] = "group_temperature"
        obs_group_dict["rain_ET"] = "group_rain"

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
                # help for supp

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


    def new_archive_record(self, event):
        """ Kick off in a new thread.
        """

        #t = wdSuppThread(self.wdSupp_main, event)
        #t.setName('wdSuppThread')
        #t.start()

        #def wdSupp_main(self, event):
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


        # parse the WU responses and put into a dictionary
        _wu_record = self.parse_WU_response(_data_record['usUnits'])

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
                #if self.vacuum > 0:
                #    if self.last_vacuum is None or ((now + 1 - self.vacuum) >= self.last_vacuum):
                #        self.vacuum_database(dbm)
                #        self.last_vacuum = now
        return

    def parse_WU_response(self, units):
        """ Parse a potentially multi-feature API response and construct a data
            dict with the required fields.
        """
        forecast_file = "/home/weewx/archive/darksky_forecast.json"
        # Create a holder dict for the data we will gather
        _data = {}
        # Do some pre-processing and error checking
        # forecast Dark Sky current read
        with open(forecast_file, encoding="utf8") as read_file:
            data = json.loads(read_file.read())

        _data['currentIcon'] = data["currently"]["time"]
        _data['currentText'] = data["currently"]["summary"]
        _data['tempRecordHigh'] = data["currently"]["temperature"]
        _data['tempNormalHigh'] = data["currently"]["apparentTemperature"]
        data_wspee = str(int(data["currently"]["windSpeed"] * 3.6))
        data_wgust = str(int(data["currently"]["windGust"] * 3.6))
        _data['forecastText'] = data_wspee + " km/h in Spitzen " + data_wgust + " km/h"
        _data['visibility_km'] = data["currently"]["visibility"]
        _data['tempRecordLow'] = data["currently"]["dewPoint"]

        return _data

    def process_loop(self):
        """ Process latest loop data and populate fields as appropriate.

            Adds following fields (if available) to data dictionary:
                - forecast icon (Vantage only)
                - forecast rule (Vantage only)(Note returns full text forecast)
                - stormRain (Vantage only)
                - stormStart (Vantage only)
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
