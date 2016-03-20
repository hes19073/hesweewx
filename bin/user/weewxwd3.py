##
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

import syslog
import threading
import urllib2
import json
import math
import time
import ephem
from math import sin
from datetime import datetime

import weewx
import weewx.engine
import weewx.manager
import weewx.wxformulas
import weewx.almanac
from weewx.units import convert, obs_group_dict
from weeutil.weeutil import to_bool, accumulateLeaves

WEEWXWD_VERSION = '1.2.0b1'

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
        0   : 'Mostly clear and cooler.',
        1   : 'Mostly clear with little temperature change.',
        2   : 'Mostly clear for 12 hours with little temperature change.',
        3   : 'Mostly clear for 12 to 24 hours and cooler.',
        4   : 'Mostly clear with little temperature change.',
        5   : 'Partly cloudy and cooler.',
        6   : 'Partly cloudy with little temperature change.',
        7   : 'Partly cloudy with little temperature change.',
        8   : 'Mostly clear and warmer.',
        9   : 'Partly cloudy with little temperature change.',
        10  : 'Partly cloudy with little temperature change.',
        11  : 'Mostly clear with little temperature change.',
        12  : 'Increasing clouds and warmer. Precipitation possible within 24 to 48 hours.',
        13  : 'Partly cloudy with little temperature change.',
        14  : 'Mostly clear with little temperature change.',
        15  : 'Increasing clouds with little temperature change. Precipitation possible within 24 hours.',
        16  : 'Mostly clear with little temperature change.',
        17  : 'Partly cloudy with little temperature change.',
        18  : 'Mostly clear with little temperature change.',
        19  : 'Increasing clouds with little temperature change. Precipitation possible within 12 hours.',
        20  : 'Mostly clear with little temperature change.',
        21  : 'Partly cloudy with little temperature change.',
        22  : 'Mostly clear with little temperature change.',
        23  : 'Increasing clouds and warmer. Precipitation possible within 24 hours.',
        24  : 'Mostly clear and warmer. Increasing winds.',
        25  : 'Partly cloudy with little temperature change.',
        26  : 'Mostly clear with little temperature change.',
        27  : 'Increasing clouds and warmer. Precipitation possible within 12 hours. Increasing winds.',
        28  : 'Mostly clear and warmer. Increasing winds.',
        29  : 'Increasing clouds and warmer.',
        30  : 'Partly cloudy with little temperature change.',
        31  : 'Mostly clear with little temperature change.',
        32  : 'Increasing clouds and warmer. Precipitation possible within 12 hours. Increasing winds.',
        33  : 'Mostly clear and warmer. Increasing winds.',
        34  : 'Increasing clouds and warmer.',
        35  : 'Partly cloudy with little temperature change.',
        36  : 'Mostly clear with little temperature change.',
        37  : 'Increasing clouds and warmer. Precipitation possible within 12 hours. Increasing winds.',
        38  : 'Partly cloudy with little temperature change.',
        39  : 'Mostly clear with little temperature change.',
        40  : 'Mostly clear and warmer. Precipitation possible within 48 hours.',
        41  : 'Mostly clear and warmer.',
        42  : 'Partly cloudy with little temperature change.',
        43  : 'Mostly clear with little temperature change.',
        44  : 'Increasing clouds with little temperature change. Precipitation possible within 24 to 48 hours.',
        45  : 'Increasing clouds with little temperature change.',
        46  : 'Partly cloudy with little temperature change.',
        47  : 'Mostly clear with little temperature change.',
        48  : 'Increasing clouds and warmer. Precipitation possible within 12 to 24 hours.',
        49  : 'Partly cloudy with little temperature change.',
        50  : 'Mostly clear with little temperature change.',
        51  : 'Increasing clouds and warmer. Precipitation possible within 12 to 24 hours. Windy.',
        52  : 'Partly cloudy with little temperature change.',
        53  : 'Mostly clear with little temperature change.',
        54  : 'Increasing clouds and warmer. Precipitation possible within 12 to 24 hours. Windy.',
        55  : 'Partly cloudy with little temperature change.',
        56  : 'Mostly clear with little temperature change.',
        57  : 'Increasing clouds and warmer. Precipitation possible within 6 to 12 hours.',
        58  : 'Partly cloudy with little temperature change.',
        59  : 'Mostly clear with little temperature change.',
        60  : 'Increasing clouds and warmer. Precipitation possible within 6 to 12 hours. Windy.',
        61  : 'Partly cloudy with little temperature change.',
        62  : 'Mostly clear with little temperature change.',
        63  : 'Increasing clouds and warmer. Precipitation possible within 12 to 24 hours. Windy.',
        64  : 'Partly cloudy with little temperature change.',
        65  : 'Mostly clear with little temperature change.',
        66  : 'Increasing clouds and warmer. Precipitation possible within 12 hours.',
        67  : 'Partly cloudy with little temperature change.',
        68  : 'Mostly clear with little temperature change.',
        69  : 'Increasing clouds and warmer. Precipitation likley.',
        70  : 'Clearing and cooler. Precipitation ending within 6 hours.',
        71  : 'Partly cloudy with little temperature change.',
        72  : 'Clearing and cooler. Precipitation ending within 6 hours.',
        73  : 'Mostly clear with little temperature change.',
        74  : 'Clearing and cooler. Precipitation ending within 6 hours.',
        75  : 'Partly cloudy and cooler.',
        76  : 'Partly cloudy with little temperature change.',
        77  : 'Mostly clear and cooler.',
        78  : 'Clearing and cooler. Precipitation ending within 6 hours.',
        79  : 'Mostly clear with little temperature change.',
        80  : 'Clearing and cooler. Precipitation ending within 6 hours.',
        81  : 'Mostly clear and cooler.',
        82  : 'Partly cloudy with little temperature change.',
        83  : 'Mostly clear with little temperature change.',
        84  : 'Increasing clouds with little temperature change. Precipitation possible within 24 hours.',
        85  : 'Mostly cloudy and cooler. Precipitation continuing.',
        86  : 'Partly cloudy with little temperature change.',
        87  : 'Mostly clear with little temperature change.',
        88  : 'Mostly cloudy and cooler. Precipitation likely.',
        89  : 'Mostly cloudy with little temperature change. Precipitation continuing.',
        90  : 'Mostly cloudy with little temperature change. Precipitation likely.',
        91  : 'Partly cloudy with little temperature change.',
        92  : 'Mostly clear with little temperature change.',
        93  : 'Increasing clouds and cooler. Precipitation possible and windy within 6 hours.',
        94  : 'Increasing clouds with little temperature change. Precipitation possible and windy within 6 hours.',
        95  : 'Mostly cloudy and cooler. Precipitation continuing. Increasing winds.',
        96  : 'Partly cloudy with little temperature change.',
        97  : 'Mostly clear with little temperature change.',
        98  : 'Mostly cloudy and cooler. Precipitation likely. Increasing winds.',
        99  : 'Mostly cloudy with little temperature change. Precipitation continuing. Increasing winds.',
        100 : 'Mostly cloudy with little temperature change. Precipitation likely. Increasing winds.',
        101 : 'Partly cloudy with little temperature change.',
        102 : 'Mostly clear with little temperature change.',
        103 : 'Increasing clouds and cooler. Precipitation possible within 12 to 24 hours possible wind shift to the W, NW, or N.',
        104 : 'Increasing clouds with little temperature change. Precipitation possible within 12 to 24 hours possible wind shift to the W, NW, or N.',
        105 : 'Partly cloudy with little temperature change.',
        106 : 'Mostly clear with little temperature change.',
        107 : 'Increasing clouds and cooler. Precipitation possible within 6 hours possible wind shift to the W, NW, or N.',
        108 : 'Increasing clouds with little temperature change. Precipitation possible within 6 hours possible wind shift to the W, NW, or N.',
        109 : 'Mostly cloudy and cooler. Precipitation ending within 12 hours possible wind shift to the W, NW, or N.',
        110 : 'Mostly cloudy and cooler. Possible wind shift to the W, NW, or N.',
        111 : 'Mostly cloudy with little temperature change. Precipitation ending within 12 hours possible wind shift to the W, NW, or N.',
        112 : 'Mostly cloudy with little temperature change. Possible wind shift to the W, NW, or N.',
        113 : 'Mostly cloudy and cooler. Precipitation ending within 12 hours possible wind shift to the W, NW, or N.',
        114 : 'Partly cloudy with little temperature change.',
        115 : 'Mostly clear with little temperature change.',
        116 : 'Mostly cloudy and cooler. Precipitation possible within 24 hours possible wind shift to the W, NW, or N.',
        117 : 'Mostly cloudy with little temperature change. Precipitation ending within 12 hours possible wind shift to the W, NW, or N.',
        118 : 'Mostly cloudy with little temperature change. Precipitation possible within 24 hours possible wind shift to the W, NW, or N.',
        119 : 'Clearing, cooler and windy. Precipitation ending within 6 hours.',
        120 : 'Clearing, cooler and windy.',
        121 : 'Mostly cloudy and cooler. Precipitation ending within 6 hours. Windy with possible wind shift to the W, NW, or N.',
        122 : 'Mostly cloudy and cooler. Windy with possible wind shift o the W, NW, or N.',
        123 : 'Clearing, cooler and windy.',
        124 : 'Partly cloudy with little temperature change.',
        125 : 'Mostly clear with little temperature change.',
        126 : 'Mostly cloudy with little temperature change. Precipitation possible within 12 hours. Windy.',
        127 : 'Partly cloudy with little temperature change.',
        128 : 'Mostly clear with little temperature change.',
        129 : 'Increasing clouds and cooler. Precipitation possible within 12 hours, possibly heavy at times. Windy.',
        130 : 'Mostly cloudy and cooler. Precipitation ending within 6 hours. Windy.',
        131 : 'Partly cloudy with little temperature change.',
        132 : 'Mostly clear with little temperature change.',
        133 : 'Mostly cloudy and cooler. Precipitation possible within 12 hours. Windy.',
        134 : 'Mostly cloudy and cooler. Precipitation ending in 12 to 24 hours.',
        135 : 'Mostly cloudy and cooler.',
        136 : 'Mostly cloudy and cooler. Precipitation continuing, possible heavy at times. Windy.',
        137 : 'Partly cloudy with little temperature change.',
        138 : 'Mostly clear with little temperature change.',
        139 : 'Mostly cloudy and cooler. Precipitation possible within 6 to 12 hours. Windy.',
        140 : 'Mostly cloudy with little temperature change. Precipitation continuing, possibly heavy at times. Windy.',
        141 : 'Partly cloudy with little temperature change.',
        142 : 'Mostly clear with little temperature change.',
        143 : 'Mostly cloudy with little temperature change. Precipitation possible within 6 to 12 hours. Windy.',
        144 : 'Partly cloudy with little temperature change.',
        145 : 'Mostly clear with little temperature change.',
        146 : 'Increasing clouds with little temperature change. Precipitation possible within 12 hours, possibly heavy at times. Windy.',
        147 : 'Mostly cloudy and cooler. Windy.',
        148 : 'Mostly cloudy and cooler. Precipitation continuing, possibly heavy at times. Windy.',
        149 : 'Partly cloudy with little temperature change.',
        150 : 'Mostly clear with little temperature change.',
        151 : 'Mostly cloudy and cooler. Precipitation likely, possibly heavy at times. Windy.',
        152 : 'Mostly cloudy with little temperature change. Precipitation continuing, possibly heavy at times. Windy.',
        153 : 'Mostly cloudy with little temperature change. Precipitation likely, possibly heavy at times. Windy.',
        154 : 'Partly cloudy with little temperature change.',
        155 : 'Mostly clear with little temperature change.',
        156 : 'Increasing clouds and cooler. Precipitation possible within 6 hours. Windy.',
        157 : 'Increasing clouds with little temperature change. Precipitation possible within 6 hours. Windy',
        158 : 'Increasing clouds and cooler. Precipitation continuing. Windy with possible wind shift to the W, NW, or N.',
        159 : 'Partly cloudy with little temperature change.',
        160 : 'Mostly clear with little temperature change.',
        161 : 'Mostly cloudy and cooler. Precipitation likely. Windy with possible wind shift to the W, NW, or N.',
        162 : 'Mostly cloudy with little temperature change. Precipitation continuing. Windy with possible wind shift to the W, NW, or N.',
        163 : 'Mostly cloudy with little temperature change. Precipitation likely. Windy with possible wind shift to the W, NW, or N.',
        164 : 'Increasing clouds and cooler. Precipitation possible within 6 hours. Windy with possible wind shift to the W, NW, or N.',
        165 : 'Partly cloudy with little temperature change.',
        166 : 'Mostly clear with little temperature change.',
        167 : 'Increasing clouds and cooler. Precipitation possible within 6 hours possible wind shift to the W, NW, or N.',
        168 : 'Increasing clouds with little temperature change. Precipitation possible within 6 hours. Windy with possible wind shift to the W, NW, or N.',
        169 : 'Increasing clouds with little temperature change. Precipitation possible within 6 hours possible wind shift to the W, NW, or N.',
        170 : 'Partly cloudy with little temperature change.',
        171 : 'Mostly clear with little temperature change.',
        172 : 'Increasing clouds and cooler. Precipitation possible within 6 hours. Windy with possible wind shift to the W, NW, or N.',
        173 : 'Increasing clouds with little temperature change. Precipitation possible within 6 hours. Windy with possible wind shift to the W, NW, or N.',
        174 : 'Partly cloudy with little temperature change.',
        175 : 'Mostly clear with little temperature change.',
        176 : 'Increasing clouds and cooler. Precipitation possible within 12 to 24 hours. Windy with possible wind shift to the W, NW, or N.',
        177 : 'Increasing clouds with little temperature change. Precipitation possible within 12 to 24 hours. Windy with possible wind shift to the W, NW, or N.',
        178 : 'Mostly cloudy and cooler. Precipitation possibly heavy at times and ending within 12 hours. Windy with possible wind shift to the W, NW, or N.',
        179 : 'Partly cloudy with little temperature change.',
        180 : 'Mostly clear with little temperature change.',
        181 : 'Mostly cloudy and cooler. Precipitation possible within 6 to 12 hours, possibly heavy at times. Windy with possible wind shift to the W, NW, or N.',
        182 : 'Mostly cloudy with little temperature change. Precipitation ending within 12 hours. Windy with possible wind shift to the W, NW, or N.',
        183 : 'Mostly cloudy with little temperature change. Precipitation possible within 6 to 12 hours, possibly heavy at times. Windy with possible wind shift to the W, NW, or N.',
        184 : 'Mostly cloudy and cooler. Precipitation continuing.',
        185 : 'Partly cloudy with little temperature change.',
        186 : 'Mostly clear with little temperature change.',
        187 : 'Mostly cloudy and cooler. Precipitation likely. Windy with possible wind shift to the W, NW, or N.',
        188 : 'Mostly cloudy with little temperature change. Precipitation continuing.',
        189 : 'Mostly cloudy with little temperature change. Precipitation likely.',
        190 : 'Partly cloudy with little temperature change.',
        191 : 'Mostly clear with little temperature change.',
        192 : 'Mostly cloudy and cooler. Precipitation possible within 12 hours, possibly heavy at times. Windy.',
        193 : 'FORECAST REQUIRES 3 HOURS OF RECENT DATA',
        194 : 'Mostly clear and cooler.',
        195 : 'Mostly clear and cooler.',
        196 : 'Mostly clear and cooler.'
        }

def logmsg(level, src, msg):
    syslog.syslog(level, '%s %s' % (src, msg))

def logdbg(src, msg):
    logmsg(syslog.LOG_DEBUG, src, msg)

def logdbg2(src, msg):
    if weewx.debug >= 2:
        logmsg(syslog.LOG_DEBUG, msg)

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
        event.packet.update(data_x)

    def new_archive_record(self, event):
        data_x = {}
        if 'outTemp' in event.record:
            data_x['outTempDay'], data_x['outTempNight'] = calc_daynighttemps(event.record['outTemp'], event.record['dateTime'])
        else:
            data_x['outTempDay'], data_x['outTempNight'] = (None, None)
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
        obs_group_dict["outTempDay"] = "group_temperature"
        obs_group_dict["outTempNight"] = "group_temperature"

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

    def next(self):
        # get our next record
        _rec = self.input_generator.next()
        _rec_mwx = weewx.units.to_METRICWX(_rec)

        # get our historical humidex, if not available then calculate it
        if 'outTemp' in _rec_mwx and 'outHumidity' in _rec_mwx:
            _rec_mwx['humidex'] = weewx.wxformulas.humidexC(_rec_mwx['outTemp'], _rec_mwx['outHumidity'])
        else:
            _rec_mwx['humidex'] = None

        if 'outTemp' in _rec_mwx and 'outHumidity' in _rec_mwx and 'windSpeed' in _rec_mwx:
            _rec_mwx['appTemp'] = weewx.wxformulas.apptempC(_rec_mwx['outTemp'], _rec_mwx['outHumidity'], _rec_mwx['windSpeed'])
        else:
            _rec_mwx['appTemp'] = None

        # 'calculate' outTempNight
        if 'outTemp' in _rec_mwx:
            _rec_mwx['outTempDay'], _rec_mwx['outTempNight'] = calc_daynighttemps(_rec_mwx['outTemp'], _rec_mwx['dateTime'])
        else:
            _rec_mwx['outTempDay'], _rec_mwx['outTempNight'] = (None, None)

        # Sunshine hours
        # Step 1 - Calculate Sun Elevation Angle as gS in radians
        if 'radiation' in _rec_mwx:
            loc = ephem.Observer()
            loc.lon = '11.341407'
            loc.lat = '53.605963'
            loc.pressure = 0
            #datum = _rec_mwx['dateTime']
            loc.date = datetime.utcfromtimestamp(_rec_mwx['dateTime'])
            s = ephem.Sun()
            s.compute(loc)
            gS = s.alt

        # Step 2 - Calculate predicted solar radiation level as pR and record

            pR = 1373 * sin(gS) * 0.4

        # Step - 3 Calculate if any sunshine hours and record

            radiation = _rec_mwx['radiation']
            if radiation is not None and gS > 0.104719755 and radiation > pR:
                _rec_mwx['sunshinehours'] = _rec_mwx['interval'] / 60.0
                _rec_mwx['sunshineS'] = 300.0
            else:
                _rec_mwx['sunshinehours'] = 0.0
                _rec_mwx['sunshineS'] = 0.0


            #Wet bulb calculations == Kuehlgrenztemperatur, Feuchtekugeltemperatur

        Tc = _rec_mwx['outTemp']
        RH = _rec_mwx['outHumidity']
        PP = _rec_mwx['pressure']

        if Tc is not None and RH is not None and PP is not None:

            Tdc = ((Tc - (14.55 + 0.114 * Tc) * (1 - (0.01 * RH)) - ((2.5 + 0.007 * Tc) * (1 - (0.01 * RH))) ** 3 - (15.9 + 0.117 * Tc) * (1 - (0.01 * RH)) ** 14))
            E = (6.11 * 10 ** (7.5 * Tdc / (237.7 + Tdc)))
            WBc = (((0.00066 * PP) * Tc) + ((4098 * E) / ((Tdc + 237.7) ** 2) * Tdc)) / ((0.00066 * PP) + (4098 * E) / ((Tdc + 237.7) ** 2))
            _rec_mwx['wetBulb'] = WBc

            #Chandler Burning Index calculations

            cdIn = (((110 - 1.373 * RH) - 0.54 * (10.20 - Tc)) * (124 * 10**(-0.0142 * RH)))/60
            _rec_mwx['cbIndex'] = cdIn
            #_rec_mwx['cbIndex'] = round(cdIn, 1)

        else:
            _rec_mwx['wetBulb'] = None
            _rec_mwx['cbIndex'] = None

        # Air-density

        dp = _rec_mwx['dewpoint']
        PP = _rec_mwx['pressure']
        Tc = _rec_mwx['outTemp']
        #Tk = Tc + 273.15

        if Tc is not None and dp is not None and PP is not None:

             p = (0.99999683 + dp *(-0.90826951E-2 + dp * (0.78736169E-4 + dp * (-0.61117958E-6 + dp * (0.43884187E-8 + dp * (-0.29883885E-10 + dp * (0.21874425E-12 + dp * (-0.17892321E-14 + dp * (0.11112018E-16 + dp * (-0.30994571E-19))))))))))
             Pv = 100 * 6.1078/(p**8)
             Pd = (PP * 100) - Pv
             Ta = Tc + 273.15
             airDe = (Pd/(287.05 * Ta)) + (Pv/(461.495 * Ta))
             #_rec_mwx['airDensity'] = airDe
             _rec_mwx['airDensity'] = round(airDe, 3)

        else:

             _rec_mwx['airDensity'] = None

        #Winddruck
        # Wd = cp * paD/2 ** vKmh
        # cp = Druckbeiwert (dimensionslos)
        # paD = airDensity = Dichte der Luft
        # vkmh = windGust = Windgeschwindigkeit

        vkmh = _rec_mwx['windGust']
        airDe = _rec_mwx['airDensity']

        if vkmh is not None and airDe is not None:

            vkmh2 = vkmh * vkmh
            _rec_mwx['windDruck'] = airDe / 2 * vkmh2

        else:
            _rec_mwx['windDruck'] = None


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
                    except:
                        loginf("WdSuppArchive:", "Weather Underground API query failure")
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
                w = urllib2.urlopen(WU_URL)
                _WUresponse = w.read()
                w.close()
                return _WUresponse
            except:
                loginf("WdSuppArchive:", "Failed to get Weather Underground API response on attempt %d" % (count + 1,))
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
            # Conditions data
            elif _wuq['name'] == 'conditions' and _wuq['response'] is not None:
                # WU does not seem to provide day/night icon name in their 'conditions' response so we
                # need to do. Just need to add 'nt_' to front of name before looking up in out Saratoga
                # icons dictionary
                if self.night:
                    _data['currentIcon'] = icon_dict['nt_' + _wuq['response']['icon']]
                else:
                    _data['currentIcon'] = icon_dict[_wuq['response']['icon']]
                _data['currentText'] = _wuq['response']['weather']
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
            except Exception, e:
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
            except Exception, e:
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
        except Exception, e:
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
            loginf("WdSuppArchive:", 'new_loop_packet: Loop packet data error. Cannot decode packet.')

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
        except Exception, e:
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
    except KeyError, e:
        logdbg2("weewxwd3:check_enable:", "%s: Missing option %s" % (service, e))
        return None

    return wdsupp_dict
