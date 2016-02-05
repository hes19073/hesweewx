import syslog
import threading
import urllib2
import json
import time

import weewx
import weewx.units
import weeutil.weeutil
import weeutil.Sun 
from weewx.wxengine import StdService
from weewx.units import ValueHelper, getStandardUnitType
from weewx.cheetahgenerator import SearchList

def logmsg(level, msg):
    syslog.syslog(level, 'wdWU: %s' % msg)

def logdbg(msg):
    logmsg(syslog.LOG_DEBUG, msg)

def loginf(msg):
    logmsg(syslog.LOG_INFO, msg)

def logerr(msg):
    logmsg(syslog.LOG_ERR, msg)
    
def toint(label, value, default_value):
    """convert to integer but also permit a value of None"""
    if isinstance(value, str) and value.lower() == 'none':
        value = None
    if value is not None:
        try:
            value = int(value)
        except Exception, e:
            logerr("bad value '%s' for %s" % (value, label))
            value = default_value
    return value
    
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

# Define default database schema
defaultWdWUSchema = [('dateTime',            'INTEGER NOT NULL UNIQUE PRIMARY KEY'),  # epoch
                     ('usUnits',             'INTEGER'),  # 0x01 or 0x10
                     ('forecastIcon',        'INTEGER'),
                     ('forecastText',        'VARCHAR(256)'),
                     ('forecastTextMetric',  'VARCHAR(256)'),  # 
                     ('currentIcon',         'INTEGER'),  #
                     ('currentText',         'VARCHAR(256)'),  # 
                     ('tempRecordHigh',      'REAL'),  # 
                     ('tempNormalHigh',      'REAL'),  # 
                     ('tempRecordHighYear',  'INTEGER'),  # 
                     ('tempRecordLow',       'REAL'),  # 
                     ('tempNormalLow',       'REAL'),  # 
                     ('tempNormalLowYear',   'INTEGER'),  # 
                     ('vantageForecastIcon', 'INTEGER'),  # 
                     ('vantageForecastRule', 'VARCHAR(256)'),  # 
                    ]

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
                   
class wdWUThread(threading.Thread):
    """Thread to rund wdWU service"""
    
    def __init__(self, target, *args):
        self._target = target
        self._args = args
        threading.Thread.__init__(self)

    def run(self):
        self._target(*self._args)
    
class wdWU(StdService):
    """Service to collect various WU forecast and conditions data
       via WU API.
       
       Currently supports following WU API calls:
       - conditions (for current conditions and icon)
       - forecast (for current forecast and icon)
       - almanac (for temperature max/min normal/record/year of)
       
       Also collects returns Davis Vantage forecast data.
       Collected data is stored in wdConditions database on the archive
       period (whilst Davis Vantage console data is received every loop
       period the only loop data stored is the values at the time of the 
       archive record.
    """

    def __init__(self, engine, config_dict):
        super(wdWU, self).__init__(engine, config_dict)
        #
        # Setup for WU API calls/Vantage Console data
        #
        
        # Create a list of the API calls we need
        self.WUqueryTypes=['conditions', 'forecast', 'almanac']
        # Set interval between API calls for each API call type we need.
        self.interval = {}
        self.interval['conditions'] = int(self.config_dict['WeewxWd']['WU']['current_interval'])
        self.interval['forecast'] = int(self.config_dict['WeewxWd']['WU']['forecast_interval'])
        self.interval['almanac'] = int(self.config_dict['WeewxWd']['WU']['almanac_interval'])
        # Set ts we last made the call
        self.last = {}
        self.last['conditions'] = None
        self.last['forecast'] = None
        self.last['almanac'] = None
        # Create holder for WU responses
        self.response = {}
        # Create holder for Davis Console loop data
        self.loop_packet = {}
        # Set max no of tries we will make in any one attempt to contact WU via API
        self.maxTries = 3
        # Get our lat/long, needed for sunrise/sunset calcs to set transition to 
        # day/night icons
        self.latitude = float(config_dict['Station']['latitude'])
        self.longitude = float(config_dict['Station']['longitude'])
        # Get our API key from weewx.conf, first look in [WeewxWD] and if no luck
        # try [Forecast] if it exists. Wrap in a try..except loop to catch exceptions (ie one or
        # both don't exist.
        try:
            if self.config_dict['WeewxWd']['WU']['apiKey'] != "":
                self.apiKey = self.config_dict['WeewxWd']['WU']['apiKey']
            elif self.config_dict['Forecast']['WU']['api_key'] != "":
                self.apiKey = self.config_dict['Forecast']['WU']['api_key']
            else:
                loginf("Cannot find valid Weather Underground API key")
        except:
            loginf("Cannot find Weather Underground API key")
        # Get our 'location' for use in WU API calls. Refer weewx.conf for details.
        self.location = self.config_dict['WeewxWd']['WU']['location']
        # Set fixed part of WU API call url
        self.defaultUrl = 'http://api.wunderground.com/api'
        
        #
        # Setup database aspects
        #
        
        # Get our config_dict
        d = config_dict.get('WeewxWd', {})
        # Set the parameters for various databases
        self.conditions_database = d['wdConditions_database']
        self.conditions_table = d.get('conditions_table', 'archive')
        schema_str = d.get('conditions_schema', None)
        self.conditions_schema = weeutil.weeutil._get_object(schema_str) \
            if schema_str is not None else defaultWdWUSchema
        # Get our database now and check the schema
        archive = self.setup_database(self.conditions_database,
                                      self.config_dict['Databases'][self.conditions_database],
                                      self.conditions_table, self.conditions_schema)
        dbcol = archive.connection.columnsOf(self.conditions_table)
        memcol = [x[0] for x in self.conditions_schema]
        if dbcol != memcol:
            raise Exception('wdWU: schema mismatch: %s != %s' %
                            (dbcol, memcol))
        archive.close
        # Set some of our parameters we require to manage the db
        # How long to keep loop records
        self.max_age = d.get('max_age', 600)
        self.max_age = toint('max_age', self.max_age, None)
        # Option to vacuum the sqlite database
        self.vacuum = d.get('vacuum', True)
        self.vacuum = weeutil.weeutil.tobool(self.vacuum)
        # How often to retry database failures
        self.db_max_tries = d.get('database_max_tries', 3)
        self.db_max_tries = int(self.db_max_tries)
        # How long to wait between retries, in seconds
        self.db_retry_wait = d.get('database_retry_wait', 10)
        self.db_retry_wait = int(self.db_retry_wait)

        # Bind ourself to NEW_ARCHIVE_RECORD to ensure we have a chance to:
        # - update WU data(if necessary)
        # - save our data
        # on each new record
        self.bind(weewx.NEW_ARCHIVE_RECORD, self.WU)
        # bind ourself to each new loop packet so we can capture Davis
        # Vantage forecast data
        self.bind(weewx.NEW_LOOP_PACKET, self.process_loop)
        loginf(('forecast interval=%s conditions interval=%s almanac interval=%s '
               'max_age=%s vacuum=%s api_key=%s location=%s') %
               (self.interval['forecast'], self.interval['conditions'], self.interval['almanac'],
               self.max_age, self.vacuum, 'xxxxxxxxxxxx'+self.apiKey[-4:], self.location))
               
    def WU(self, event):
        """Kick off in a new thread"""
        t = wdWUThread(self.WU_main, event)
        t.setName('wdWUThread')
        t.start()

    def WU_main(self, event):
        """Loop through the WU API requests we need to do and
           call the routine to parse and save the results.
        """

        # Get time now as a ts
        now = time.time()
        # Work out sunrise and sunset ts so we can determine if it is night or day. Needed so
        # we can set day or night icons when translating WU icons to Saratoga icons
        (y,m,d) = time.localtime(now)[0:3]
        (sunrise_utc, sunset_utc) = weeutil.Sun.sunRiseSet(y, m, d, self.longitude, self.latitude)
        sunrise_tt = weeutil.weeutil.utc_to_local_tt(y, m, d, sunrise_utc)
        sunset_tt  = weeutil.weeutil.utc_to_local_tt(y, m, d, sunset_utc)
        sunrise_ts = time.mktime(sunrise_tt)
        sunset_ts = time.mktime(sunset_tt) 
        # If we are not between sunrise and sunset it must be night
        self.night = not (sunrise_ts < now < sunset_ts)
        # Loop through our list of API calls to be made
        for _WUquery in self.WUqueryTypes:
            logdbg("Last Weather Underground %s query at %s" % (_WUquery, self.last[_WUquery]))
            # If we haven't done this API call previously or if its been too long since
            # the last then do it (again)
            if (self.last[_WUquery] is None) or ((now + 1 - self.interval[_WUquery]) >= self.last[_WUquery]):
                # Call a routine to make the API call and save the response. Wrap in a try..except just in case
                try:
                    self.response[_WUquery] = self.get_WU_response(_WUquery)
                    logdbg("Downloaded updated Weather Underground %s information" % (_WUquery))
                    # If we got something back then reset our timer
                    if self.response[_WUquery] is not None:
                        self.last[_WUquery] = now
                except:
                    loginf("Weather Underground %s API query failure" % (_WUquery))
        # Call routine to parse the resonses then save the required info
        _data_packet = self.parse_WU_response(event)
        self.save_WU_response(_data_packet)
        return
        
    def get_WU_response(self, _WUquery):
        """Construct the WU API call and get WU response"""

        # Construct our API call URL
        url = '%s/%s/%s/pws:1/q/%s.json' % (self.defaultUrl, self.apiKey, _WUquery, self.location)
        # We will attempt the call self.maxTries times
        for count in range(self.maxTries):
            # Attempt the call
            try:
                w = urllib2.urlopen(url)
                _WUresponse = w.read()
                w.close()
                return _WUresponse
            except:
                loginf('Failed to get current conditions on attempt %d' % (count+1))
        else:
            loginf('Failed to get current conditions')
        return None

    def parse_WU_response(self, event):
        """Parse the WU response and write relevant fields to file"""
        
        # Creat a holder for the data (lines) we will write to file
        _data_packet = {}
        _data_packet['dateTime'] = event.record['dateTime']
        _data_packet['usUnits'] = event.record['usUnits']
        # Step through each of the API calls
        for _WUquery in self.WUqueryTypes:
            # Deserialise our JSON response
            _parsed_response = json.loads(self.response[_WUquery])
            # Check for recognised format
            if not 'response' in _parsed_response:
                loginf('Unknown format in current conditions')
                return _data_packet
            _response = _parsed_response['response']
            # Check for WU provided error otherwise start pulling in the fields/data we want
            if 'error' in _response:
                loginf('Error in WU current conditions response')
                return _data_packet
            # Forecast data
            elif _WUquery == 'forecast':
                # Look up Saratoga icon number given WU icon name
                _data_packet['forecastIcon'] = icon_dict[_parsed_response['forecast']['txt_forecast']['forecastday'][0]['icon']]
                _data_packet['forecastText'] = _parsed_response['forecast']['txt_forecast']['forecastday'][0]['fcttext']
                _data_packet['forecastTextMetric'] = _parsed_response['forecast']['txt_forecast']['forecastday'][0]['fcttext_metric']
            # Conditions data
            elif _WUquery == 'conditions':
                # WU does not seem to provide day/night icon name in their 'conditions' response so we
                # need to do. Just need to add 'nt_' to front of name before looking up in out Saratoga 
                # icons dictionary
                if self.night:
                    _data_packet['currentIcon'] = icon_dict['nt_' + _parsed_response['current_observation']['icon']]
                else:
                    _data_packet['currentIcon'] = icon_dict[_parsed_response['current_observation']['icon']]
                _data_packet['currentText'] = _parsed_response['current_observation']['weather']
            # Almanac data
            elif _WUquery == 'almanac':
                if _data_packet['usUnits'] is weewx.US:
                    _data_packet['tempRecordHigh'] = _parsed_response['almanac']['temp_high']['record']['F']
                    _data_packet['tempNormalHigh'] = _parsed_response['almanac']['temp_high']['normal']['F']
                    _data_packet['tempRecordLow'] = _parsed_response['almanac']['temp_low']['record']['F']
                    _data_packet['tempNormalLow'] = _parsed_response['almanac']['temp_low']['normal']['F']
                else:
                    _data_packet['tempRecordHigh'] = _parsed_response['almanac']['temp_high']['record']['C']
                    _data_packet['tempNormalHigh'] = _parsed_response['almanac']['temp_high']['normal']['C']
                    _data_packet['tempRecordLow'] = _parsed_response['almanac']['temp_low']['record']['C']
                    _data_packet['tempNormalLow'] = _parsed_response['almanac']['temp_low']['normal']['C']
                _data_packet['tempRecordHighYear'] = _parsed_response['almanac']['temp_high']['recordyear']
                _data_packet['tempNormalLowYear'] = _parsed_response['almanac']['temp_low']['recordyear']
        _data_packet['vantageForecastIcon'] = self.loop_packet['forecastIcon']
        _data_packet['vantageForecastRule'] = self.loop_packet['forecastRule']
        return _data_packet
    
    def save_WU_response(self, _data_packet):
        """Save the WU response to db"""
        
        archive = wdWU.setup_database(self.conditions_database,
                                      self.config_dict['Databases'][self.conditions_database],
                                      self.conditions_table, self.conditions_schema)
        # save our data to the database
        wdWU.save_data(archive, _data_packet, self.db_max_tries, self.db_retry_wait)
        # set ts of last packet processed
        self.last_ts = _data_packet['dateTime']
        # prune older packets and vacuum if required
        if self.max_age is not None:
            self.prune_loops(archive, self.conditions_table, self.last_ts - self.max_age,
                                     self.db_max_tries, self.db_retry_wait)
            # vacuum the database
            if self.vacuum:
                self.vacuum_database(archive)
        archive.close
        return

    def process_loop(self, event):
        # reset OUR loop packet
        try:
            # pick out the loop data we want
            self.loop_packet['forecastIcon'] = event.packet['forecastIcon']
            self.loop_packet['forecastRule'] = event.packet['forecastRule']
        except:
            loginf('process_loop: Loop packet data error. Cannot decode packet.')

    @staticmethod
    def save_data(archive, _data_packet, max_tries=3, retry_wait=10):
        for count in range(max_tries):
            try:
                archive.addRecord(_data_packet)
                break
            except Exception, e:
                logerr('Save failed (attempt %d of %d): %s' % ((count+1), max_tries, e))
                logdbg('Waiting %d seconds before retry' % (retry_wait))
                time.sleep(retry_wait)
        else:
            raise Exception('Save failed after %d attempts' % max_tries)

    @staticmethod
    def prune_loops(archive, table, ts, max_tries=3, retry_wait=10):
        """remove loop packets older than ts from the database"""

        sql = "delete from %s where dateTime < %d" % (table, ts)
        for count in range(max_tries):
            try:
                archive.getSql(sql)
                logdbg('Deleted loop packets prior to %d' % (ts))
                break
            except Exception, e:
                logerr('Prune failed (attempt %d of %d): %s' % ((count+1), max_tries, e))
                logdbg('Waiting %d seconds before retry' % (retry_wait))
                time.sleep(retry_wait)
        else:
            raise Exception('Prune failed after %d attemps' % max_tries)
        return

    @staticmethod
    def vacuum_database(archive):
        # vacuum will only work on sqlite databases.  It will compact the
        # database file.  if we do not do this, the file grows even though
        # we prune records from the database.  It should be ok to run this
        # on a mysql database - it will silently fail.
        try:
            logdbg('Vacuuming database %s' % (archive.database))
            archive.getSql('vacuum')
        except Exception, e:
            logdbg('Vacuuming database % failed: %s' % (archive.database, e))

    @staticmethod
    def setup_database(dbname, dbcfg, table, schema):
        archive = weewx.archive.Archive.open_with_create(dbcfg, schema, table)
        logdbg("Using table '%s' in database '%s'" % (table, dbname))
        return archive

    def shutDown(self):
        pass

