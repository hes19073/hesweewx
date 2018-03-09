# $Id: crt.py 1477 2016-04-10 13:19:56Z mwall $
# Copyright 2013-2016 Matthew Wall
# thanks to gary roderick for significant contributions to this code

"""Emit loop data to file in Cumulus realtime format.

   http://wiki.sandaysoft.com/a/Realtime.txt
   http://wiki.sandaysoft.com/a/Webtags

Put this file in bin/user/crt.py, then add this to your weewx.conf:

[CumulusRealTime]
    filename = /path/to/realtime.txt

[Engine]
    [[Services]]
        archive_services = ..., user.crt.CumulusRealTime

If no unit_system is specified, the units will be those of the database.
Units and other parameters may be specified:

[CumulusRealTime]
    filename = /path/to/realtime.txt
    date_separator = /
    none = NULL
    unit_system = (US | METRIC | METRICWX)
    wind_units = (meter_per_second | mile_per_hour | km_per_hour | knot)
    temperature_units = (degree_C | degree_F)
    pressure_units = (hPa | mbar | inHg)
    rain_units = (mm | inch)
    cloudbase_units = (foot | meter)

Note that most of the code in this file is to calculate/lookup data that
are not directly provided by weewx in a LOOP packet.

The cumulus 'specification' for realtime.txt is ambiguous in places:

  - pressure trend interval is not specified, we use 3 hours for pressure
  - temperature trend interval is not specified, we use 3 hours for temperature
  
The following assumptions are based on the Cumulus realtime and webtag docs:
  - wind avg speed/wind avg dir interval is not specified. The equivalent 
    Cumulus Webtags for wind avg speed and avg wind direction default to 
    10 minute averages so we use 10 minutes as well.
  - wind direction bearings in degrees are set from > 0 to 360 with 0
    indicating calm.  refer to the #avgbearing Webtag. this is different to
    the standard used in weewx.
  - possible Cumulus windrun units are km, miles, km and nm corresponding to 
    wind speeds in m/s, mph, km/h, kts.  weewx does not know what a nautical
    mile (nm) is.
  
The following assumptions are based on examination of realtime.txt instances
from a number of live Cumulus sites:
  - time zone is not specified, local time is used throughout
  - how to handle None/NULL is not specified.  Examination of realtime.txt 
    from a number of live Cumulus sites indicates when there is no wind 
    (average or gust) wind speeds are set to zero. For other fields that
    may be None/Null we return the 'none' parameter setting (default = NULL) 
    from the weewx.conf [CumulusRealTime] section.
  - ordinal wind directions are set to --- when there is no wind.
"""

# FIXME: consider in-memory caching so that database queries are not
#        necessary after the first invocation

import math
import time
import syslog
from distutils.version import StrictVersion

import weewx
import weewx.almanac
import weewx.manager
import weewx.wxformulas
import weeutil.weeutil
import weedb
from weewx.engine import StdService

VERSION = "0.18"

REQUIRED_WEEWX = "3.5.0"
if StrictVersion(weewx.__version__) < StrictVersion(REQUIRED_WEEWX):
    raise weewx.UnsupportedFeature("weewx %s or greater is required, found %s"
                                   % (REQUIRED_WEEWX, weewx.__version__))

def logmsg(level, msg):
    syslog.syslog(level, 'crt: %s' % msg)

def logdbg(msg):
    logmsg(syslog.LOG_DEBUG, msg)

def loginf(msg):
    logmsg(syslog.LOG_INFO, msg)

def logerr(msg):
    logmsg(syslog.LOG_ERR, msg)

COMPASS_POINTS = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                  'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW', 'N']

# map weewx unit names to cumulus unit names
UNITS_PRES = {'inHg': 'in', 'mbar': 'mb', 'hPa': 'hPa'}
UNITS_TEMP = {'degree_C': 'C', 'degree_F': 'F'}
UNITS_RAIN = {'inch': 'in', 'mm': 'mm'}
UNITS_WIND = {'mile_per_hour': 'mph',
              'meter_per_second': 'm/s',
              'km_per_hour': 'km/h',
              'knot': 'kts'}
UNITS_CLOUDBASE = {'foot': 'ft', 'meter': 'm'}
# categorize the weewx-to-cumulus unit mappings
UNITS = {'pressure': UNITS_PRES,
         'temperature': UNITS_TEMP,
         'rain': UNITS_RAIN,
         'wind': UNITS_WIND,
         'cloudbase': UNITS_CLOUDBASE}
SPEED_TO_RUN = {'mile_per_hour': 'mile',
                'meter_per_second': 'km',
                'km_per_hour': 'km',
                'knot': 'mile'}

def _convert(from_v, from_units, to_units, group):
    """Given a value, units and unit group convert to different units."""
    vt = (from_v, from_units, group)
    return weewx.units.convert(vt, to_units)[0]

def _convert_us(from_v, from_us, to_units, obs, group):
    """Given obs type, value, unit system and unit group convert to units."""
    from_units = weewx.units.getStandardUnitType(from_us, obs)[0]
    return _convert(from_v, from_units, to_units, group)

def clamp_degrees(x):
    """Convert a bearing to a Cumulus bearing.
    
    weewx uses 0.0 inclusive to 360.0 (exclusive) bearings whilst Cumulus 
    uses 0.0 (exclusive) to 360.0 (inclusive) bearings. When the wind is 
    calm Cumulus emits a wind direction of 0 degrees.
    """
    if x is not None:
        return x if x != 0.0 else 360.0
    return None

def degree_to_compass(x):
    if x is None:
        return '---'
    idx = int((x + 11.25) / 22.5)
    return COMPASS_POINTS[idx]

def get_db_units(dbm):
    val = dbm.getSql("SELECT usUnits FROM %s LIMIT 1" % dbm.table_name)
    return val[0] if val is not None else None

def calc_avg_windspeed(dbm, ts, interval=600):
    sts = ts - interval
    val = dbm.getSql("SELECT AVG(windSpeed) FROM %s "
                     "WHERE dateTime>? AND dateTime<=?" % dbm.table_name,
                     (sts, ts))
    return val[0] if val is not None else None

def calc_avg_winddir(dbm, ts, interval=600):
    sts = ts - interval
    val = dbm.getSql("SELECT AVG(windDir) FROM %s "
                     "WHERE dateTime>? AND dateTime<=?" % dbm.table_name,
                     (sts, ts))
    return clamp_degrees(val[0]) if val is not None else None

def calc_max_gust_10min(dbm, ts):
    sts = ts - 600
    val = dbm.getSql("SELECT MAX(windGust) FROM %s "
                     "WHERE dateTime>? AND dateTime<=?" % dbm.table_name,
                     (sts, ts))
    return val[0] if val is not None else None

def calc_avg_winddir_10min(dbm, ts):
    sts = ts - 600
    val = dbm.getSql("SELECT AVG(windDir) FROM %s "
                     "WHERE dateTime>? AND dateTime<=?" % dbm.table_name,
                     (sts, ts))
    return clamp_degrees(val[0]) if val is not None else None

def calc_windrun(dbm, ts, db_us):
    """Calculate windrun since midnight.  returns a value in the distance units
    of the database (thus the temporal normalization).
    """
    run = 0
    sod_ts = weeutil.weeutil.startOfDay(ts)
    for row in dbm.genSql("SELECT `interval`,windSpeed FROM %s "
                          "WHERE dateTime>? AND dateTime<=?" % dbm.table_name,
                          (sod_ts, ts)):
        if row[1] is not None:
            inc = row[1] * row[0]
            if db_us == weewx.METRICWX:
                inc *= 60.0
            else:
                inc /= 60.0
            run += inc
    return run

def get_trend(label, dbm, ts, n=3):
    """Calculate the trend over past n hours, default to 3 hour window."""
    lastts = ts - n * 3600
    old_val = dbm.getSql("SELECT %s FROM %s "
                         "WHERE dateTime>? AND dateTime<=?" %
                         (label, dbm.table_name), (lastts, ts))
    if old_val is None or old_val[0] is None:
        return None
    return old_val[0]

def calc_trend(newval, oldval):
    if newval is None or oldval is None:
        return None
    return newval - oldval

def calc_rain_hour(dbm, ts):
    sts = ts - 3600
    val = dbm.getSql("SELECT SUM(rain) FROM %s "
                     "WHERE dateTime>? AND dateTime<=?" % dbm.table_name,
                     (sts, ts))
    return val[0] if val is not None else None

def calc_rain_month(dbm, ts):
    span = weeutil.weeutil.archiveMonthSpan(ts)
    val = dbm.getSql("SELECT SUM(rain) FROM %s "
                     "WHERE dateTime>? AND dateTime<=?" % dbm.table_name,
                     (span.start, ts))
    return val[0] if val is not None else None

def calc_rain_year(dbm, ts):
    span = weeutil.weeutil.archiveYearSpan(ts)
    val = dbm.getSql("SELECT SUM(rain) FROM %s "
                     "WHERE dateTime>? AND dateTime<=?" % dbm.table_name,
                     (span.start, ts))
    return val[0] if val is not None else None

def calc_rain_yesterday(dbm, ts):
    ts = weeutil.weeutil.startOfDay(ts)
    sts = ts - 3600 * 24
    val = dbm.getSql("SELECT SUM(rain) FROM %s "
                     "WHERE dateTime>? AND dateTime<=?" % dbm.table_name,
                     (sts, ts))
    return val[0] if val is not None else None

def calc_rain_day(dbm, ts):
    sts = weeutil.weeutil.startOfDay(ts)
    val = dbm.getSql("SELECT SUM(rain) FROM %s "
                     "WHERE dateTime>? AND dateTime<=?" % dbm.table_name, 
                     (sts, ts))
    return val[0] if val is not None else None

def calc_ET_today(dbm, ts):
    sts = weeutil.weeutil.startOfDay(ts)
    val = dbm.getSql("SELECT SUM(ET) FROM %s "
                     "WHERE dateTime>? AND dateTime<=?" % dbm.table_name,
                     (sts, ts))
    return val[0] if val is not None else None

def calc_minmax(label, dbm, ts, minmax='MAX'):
    sts = weeutil.weeutil.startOfDay(ts)
    val = dbm.getSql("SELECT %s(%s) FROM %s "
                     "WHERE dateTime>? AND dateTime<=?" %
                     (minmax, label, dbm.table_name), (sts, ts))
    if val is None:
        return None, None
    t = dbm.getSql("SELECT dateTime FROM %s "
                   "WHERE dateTime>? AND dateTime<=? AND %s=?" %
                   (dbm.table_name, label), (sts, ts, val[0]))
    if t is None:
        return None, None
    tstr = time.strftime("%H:%M", time.localtime(t[0]))
    return val[0], tstr

def calc_is_daylight(alm):
    sunrise = alm.sunrise.raw
    sunset = alm.sunset.raw
    if sunrise < alm.time_ts < sunset:
        return 1
    return 0

def calc_daylight_hours(alm):
    sunrise = alm.sunrise.raw
    sunset = alm.sunset.raw
    if alm.time_ts <= sunrise:
        return 0
    elif alm.time_ts < sunset:
        return (alm.time_ts - sunrise) / 3600.0
    return (sunset - sunrise) / 3600.0

def calc_is_sunny(rad, max_rad, threshold):
    if not rad or not max_rad:
        return 0
    if rad <= threshold * max_rad:
        return 0
    return 1

# indication of sensor contact depens on the weather station.  if the station
# has more than one indicator, then indicate failure if contact is lost with
# any one of them.
#
# Vantage
#   packet['rxCheckPercent'] == 0
#
# FineOffset
#   packet['status'] & 0x40
#
# TE923
#   packet['sensorX_state'] == STATE_MISSING_LINK
#   packet['wind_state'] == STATE_MISSING_LINK
#   packet['rain_state'] == STATE_MISSING_LINK
#   packet['uv_state'] == STATE_MISSING_LINK
#
# WMR100
# WMR200
# WMR9x8
#
# WS28xx
#   packet['rxCheckPercent'] == 0
#
# WS23xx
#   packet['cn'] == 'lost'
#
def lost_sensor_contact(packet):
    if 'rxCheckPercent' in packet and packet['rxCheckPercent'] == 0:
        return 1
    if 'cn' in packet and packet['cn'] == 'lost':
        return 1
    if (('windspeed_state' in packet and packet['windspeed_state'] == 'no_link') or
        ('rain_state' in packet and packet['rain_state'] == 'no_link') or
        ('uv_state' in packet and packet['uv_state'] == 'no_link') or
        ('h_1_state' in packet and packet['h_1_state'] == 'no_link') or
        ('h_2_state' in packet and packet['h_2_state'] == 'no_link') or
        ('h_3_state' in packet and packet['h_3_state'] == 'no_link') or
        ('h_4_state' in packet and packet['h_4_state'] == 'no_link') or
        ('h_5_state' in packet and packet['h_5_state'] == 'no_link')):
        return 1
    return 0

class ZambrettiForecast():
    DEFAULT_FORECAST_BINDING = 'forecast_binding'
    DEFAULT_BINDING_DICT = {
        'database': 'forecast_sqlite',
        'manager': 'weewx.manager.Manager',
        'table_name': 'archive',
        'schema': 'user.forecast.schema'}

    def __init__(self, config_dict):
        self.forecasting_installed = False
        self.db_max_tries = 3
        self.db_retry_wait = 3
        try:
            self.dbm_dict = weewx.manager.get_manager_dict(
                config_dict['DataBindings'],
                config_dict['Databases'],
                ZambrettiForecast.DEFAULT_FORECAST_BINDING,
                default_binding_dict=ZambrettiForecast.DEFAULT_BINDING_DICT)
            weewx.manager.open_manager(self.dbm_dict)
            self.forecasting_installed = True
        except (weedb.DatabaseError, weewx.UnsupportedFeature,
                weewx.UnknownBinding, KeyError):
            pass

    def is_installed(self):
        return self.forecasting_installed

    def get_zambretti_code(self):
        if not self.forecasting_installed:
            return 0

        # FIXME: add api to forecast instead of doing all the work here
        with weewx.manager.open_manager(self.dbm_dict) as dbm:
            sql = "select dateTime,zcode from %s where method = 'Zambretti' order by dateTime desc limit 1" % dbm.table_name
#            sql = "select zcode from %s where method = 'Zambretti' and dateTime = (select max(dateTime) from %s where method = 'Zambretti')" % (dbm.table_name, dbm.table_name)
            for count in range(self.db_max_tries):
                try:
                    record = dbm.getSql(sql)
                    if record is not None:
                        return ZambrettiForecast.alpha_to_number(record[1])
                except Exception, e:
                    logerr('get zambretti failed (attempt %d of %d): %s' %
                           ((count + 1), self.db_max_tries, e))
                    logdbg('waiting %d seconds before retry' %
                           self.db_retry_wait)
                    time.sleep(self.db_retry_wait)
        return 0

    # given a zambretti letter code A-Z, convert to digit 1-26
    @staticmethod
    def alpha_to_number(x):
        return ord(x) - 64


class CumulusRealTime(StdService):

    def __init__(self, engine, config_dict):
        super(CumulusRealTime, self).__init__(engine, config_dict)
        loginf("service version is %s" % VERSION)
        self.altitude_m = weewx.units.convert(
            engine.stn_info.altitude_vt, "meter")[0]
        self.latitude = engine.stn_info.latitude_f
        self.longitude = engine.stn_info.longitude_f

        d = config_dict.get('CumulusRealTime', {})
        self.filename = d.get('filename', '/var/tmp/realtime.txt')
        loginf("output goes to %s" % self.filename)
        self.datesep = d.get('date_separator', '/')
        self.sunny_threshold = float(d.get('sunny_threshold', 0.75))
        self.nonesub = d.get('none', 'NULL')
        loginf("'None' values will be displayed as %s" % self.nonesub)

        # source unit system is the database unit system
        self.db_us = None
        # initialise packet unit system
        self.pkt_us = None

        # get the unit system for display
        us = None
        us_label = d.get('unit_system', None)
        if us_label is not None:
            if us_label in weewx.units.unit_constants:
                loginf("units will be displayed as %s" % us_label)
                us = weewx.units.unit_constants[us_label]
            else:
                logerr("unknown unit_system %s" % us_label)
        self.unit_system = us

        # get any overrides to the display units
        self.units = dict()
        for x in UNITS:
            ukey = '%s_units' % x
            if ukey in d:
                if d[ukey] in UNITS[x]:
                    loginf("%s units will be displayed as %s" % (x, d[ukey]))
                    self.units[x] = d[ukey]
                else:
                    logerr("unknown unit '%s' for %s" % (d[ukey], ukey))

        # configure forecasting
        self.forecast = ZambrettiForecast(config_dict)
        loginf("zambretti forecast: %s" % self.forecast.is_installed())

        # configure the binding
        binding = d.get('binding', 'loop').lower()
        loginf("binding is %s" % binding)
        if binding == 'loop':
            self.bind(weewx.NEW_LOOP_PACKET, self.handle_new_loop)
        else:
            self.bind(weewx.NEW_ARCHIVE_RECORD, self.handle_new_archive)

    def handle_new_loop(self, event):
        self.handle_data(event.packet)

    def handle_new_archive(self, event):
        self.handle_data(event.record)

    def handle_data(self, event_data):
        try:
            dbm = self.engine.db_binder.get_manager('wx_binding')
            data = self.calculate(event_data, dbm)
            self.write_data(data)
        except Exception, e:
            logdbg("crt: Exception while handling data: %s" % e)
            weeutil.weeutil.log_traceback('crt: **** ')
            raise

    def write_data(self, data):
        with open(self.filename, 'w') as f:
            f.write(self.create_realtime_string(data))
            f.write("\n")

    # convert from database unit system to specified units
    def _cvt(self, from_v, to_units, obs, group):
        if self.db_us is None:
            return None
        return _convert_us(from_v, self.db_us, to_units, obs, group)

    # convert from database unit system to specified unit system
    def _cvt_us(self, from_v, to_us, obs, group):
        to_units = weewx.units.getStandardUnitType(to_us, obs)[0]
        return self._cvt(from_v, to_units, obs, group)

    # convert observation in group pressure
    def _cvt_p(self, obs, packet, unit):
        return _convert_us(packet.get(obs), self.pkt_us, unit, 
                           obs, 'group_pressure')

    # convert observation in group temperature
    def _cvt_t(self, obs, packet, unit):
        return _convert_us(packet.get(obs), self.pkt_us, unit, 
                           obs, 'group_temperature')

    # convert observation in group rainrate
    def _cvt_rr(self, obs, packet, unit):
        return _convert_us(packet.get(obs), self.pkt_us, unit, 
                           obs, 'group_rainrate')

    # convert observation in group speed
    def _cvt_w(self, obs, packet, unit):
        return _convert_us(packet.get(obs), self.pkt_us, unit, 
                           obs, 'group_speed')

    # convert observation group altitude
    def _cvt_a(self, obs, packet, unit):
        return _convert_us(packet.get(obs), self.pkt_us, unit, 
                           obs, 'group_altitude')

    # calculate the data elements that that weewx does not provide directly.
    def calculate(self, packet, dbm):
        ts = packet.get('dateTime')

        # the 'from' unit system is whatever the database is using.  get it
        # from the database once then cache it for use in conversions.  if
        # there is not yet a database, return an empty dict and we'll get it
        # the next time around.
        if self.db_us is None:
            try:
                self.db_us = get_db_units(dbm)
            except weedb.DatabaseError, e:
                logerr("cannot determine database units: %s" % e)
                return dict()

        # the 'to' unit system defaults to the unit system of the packet
        # (typically the same unit system as the database, but it might not
        # be), but if a different unit system is specified, use that...
        self.pkt_us = packet.get('usUnits')
        if self.unit_system is not None and self.unit_system != self.pkt_us:
            packet = weewx.units.to_std_system(packet, self.unit_system)
            self.pkt_us = self.unit_system

        # ... then get any other specialized units.
        p_u = self.units.get(
            'pressure',
            weewx.units.getStandardUnitType(self.pkt_us, 'barometer')[0])
        t_u = self.units.get(
            'temperature',
            weewx.units.getStandardUnitType(self.pkt_us, 'outTemp')[0])
        r_u = self.units.get(
            'rain',
            weewx.units.getStandardUnitType(self.pkt_us, 'rain')[0])
        w_u = self.units.get(
            'wind',
            weewx.units.getStandardUnitType(self.pkt_us, 'windSpeed')[0])
        cb_u = self.units.get(
            'cloudbase',
            weewx.units.getStandardUnitType(self.pkt_us, 'altitude')[0])

        # cumulus does not use cm for rain, but weewx might
        if r_u == 'cm':
            r_u = 'mm'
        # infer rain rate units from rain units
        rr_u = '%s_per_hour' % r_u
        # infer windrun units from wind units
        wr_u = SPEED_TO_RUN.get(w_u, 'mile')

        # now create the dictionary of data
        data = dict(packet)
        data['units_wind'] = UNITS_WIND.get(w_u, w_u)
        data['units_temperature'] = UNITS_TEMP.get(t_u, t_u)
        data['units_pressure'] = UNITS_PRES.get(p_u, p_u)
        data['units_rain'] = UNITS_RAIN.get(r_u, r_u)
        data['units_cloudbase'] = UNITS_CLOUDBASE.get(cb_u, cb_u)

        data['barometer'] = self._cvt_p('barometer', packet, p_u)
        data['inTemp'] = self._cvt_t('inTemp', packet, t_u)
        data['outTemp'] = self._cvt_t('outTemp', packet, t_u)
        data['dewpoint'] = self._cvt_t('dewpoint', packet, t_u)
        data['heatindex'] = self._cvt_t('heatindex', packet, t_u)
        data['humidex'] = self._cvt_t('humidex', packet, t_u)
        data['windchill'] = self._cvt_t('windchill', packet, t_u)
        data['appTemp'] = self._cvt_t('appTemp', packet, t_u)
        data['windSpeed'] = self._cvt_w('windSpeed', packet, w_u)
        data['rainRate'] = self._cvt_rr('rainRate', packet, rr_u)
        data['cumulus_windDir'] = clamp_degrees(packet.get('windDir'))
        data['windDir_compass'] = degree_to_compass(packet.get('windDir'))
        data['windSpeed_avg'] = self._cvt(
            calc_avg_windspeed(dbm, ts), w_u, 'windSpeed', 'group_speed')
        v = _convert_us(packet.get('windSpeed'), self.pkt_us, 'knot',
                        'windSpeed', 'group_speed')
        data['windSpeed_beaufort'] = weewx.wxformulas.beaufort(v)
        wr = calc_windrun(dbm, ts, self.db_us)
        data['windrun'] = self._cvt(wr, wr_u, 'windrun', 'group_distance')
        # weewx does not know of nautical miles so if wind speed units are knot
        # then we have a windrun in miles and we need to manually convert it to
        # nautical miles
        if w_u == 'knot' and data['windrun'] is not None:
            data['windrun'] /= 1.15077945
        data['cloudbase'] = self._cvt_a('cloudbase', packet, cb_u)
        p1 = packet.get('barometer')
        p2 = get_trend('barometer', dbm, ts)
        p2 = self._cvt_us(p2, self.pkt_us, 'barometer', 'group_pressure')
        data['pressure_trend'] = calc_trend(p1, p2)
        t1 = packet.get('outTemp')
        t2 = get_trend('outTemp', dbm, ts)
        t2 = self._cvt_us(t2, self.pkt_us, 'outTemp', 'group_temperature')
        data['temperature_trend'] = calc_trend(t1, t2)

        data['rain_month'] = self._cvt(
            calc_rain_month(dbm, ts), r_u, 'rain', 'group_rain')
        data['rain_year'] = self._cvt(
            calc_rain_year(dbm, ts), r_u, 'rain', 'group_rain')
        data['rain_yesterday'] = self._cvt(
            calc_rain_yesterday(dbm, ts), r_u, 'rain', 'group_rain')
        data['dayRain'] = self._cvt(
            calc_rain_day(dbm, ts), r_u, 'rain', 'group_rain')

        v, t = calc_minmax('outTemp', dbm, ts, 'MAX')
        data['outTemp_max'] = self._cvt(
            v, t_u, 'outTemp', 'group_temperature')
        data['outTemp_max_time'] = t
        v, t = calc_minmax('outTemp', dbm, ts, 'MIN')
        data['outTemp_min'] = self._cvt(
            v, t_u, 'outTemp', 'group_temperature')
        data['outTemp_min_time'] = t
        v, t = calc_minmax('barometer', dbm, ts, 'MAX')
        data['pressure_max'] = self._cvt(
            v, p_u, 'barometer', 'group_pressure')
        data['pressure_max_time'] = t
        v, t = calc_minmax('barometer', dbm, ts, 'MIN')
        data['pressure_min'] = self._cvt(
            v, p_u, 'barometer', 'group_pressure')
        data['pressure_min_time'] = t
        v, t = calc_minmax('windSpeed', dbm, ts, 'MAX')
        data['windSpeed_max'] = self._cvt(
            v, w_u, 'windSpeed', 'group_speed')
        data['windSpeed_max_time'] = t
        v, t = calc_minmax('windGust', dbm, ts, 'MAX')
        data['windGust_max'] = self._cvt(
            v, w_u, 'windGust', 'group_speed')
        data['windGust_max_time'] = t

        data['10min_high_gust'] = self._cvt(
            calc_max_gust_10min(dbm, ts), w_u, 'windSpeed', 'group_speed')
        v = calc_avg_winddir_10min(dbm, ts)
        data['10min_avg_wind_bearing'] = v
        data['avg_wind_dir'] = degree_to_compass(v)

        data['rain_hour'] = self._cvt(
            calc_rain_hour(dbm, ts), r_u, 'rain', 'group_rain')

        data['ET_today'] = calc_ET_today(dbm, ts)
        data['lost_sensors_contact'] = lost_sensor_contact(packet)

        t_C = _convert_us(packet.get('outTemp'), self.pkt_us, 'degree_C',
                          'outTemp', 'group_temperature')
        p_mbar = _convert_us(packet.get('barometer'), self.pkt_us, 'mbar',
                             'barometer', 'group_pressure')
        alm = weewx.almanac.Almanac(ts, self.latitude, self.longitude,
                                    self.altitude_m, t_C, p_mbar)
        data['is_daylight'] = calc_is_daylight(alm)
        data['sunshine_hours'] = calc_daylight_hours(alm)
        data['is_sunny'] = calc_is_sunny(data.get('radiation'),
                                         data.get('max_rad'),
                                         self.sunny_threshold)
        data['zambretti_code'] = self.forecast.get_zambretti_code()
        return data

    def format(self, data, label, places=None):
        value = data.get(label)
        if value is None:
            value = self.nonesub
        elif places is not None:
            try:
                v = float(value)
                fmt = "%%.%df" % places
                value = fmt % v
            except ValueError:
                pass
        return str(value)

    # the * indicates a field that is not part of a typical LOOP packet
    # the ## indicates calculation is not yet implemented
    def create_realtime_string(self, data):
        fields = []
        p_dp = 2 if data['units_pressure'] == 'in' else 1
        r_dp = 2 if data['units_rain'] == 'in' else 1
        datefmt = "%%d%s%%m%s%%y" % (self.datesep, self.datesep)
        tstr = time.strftime(datefmt, time.localtime(data['dateTime']))
        fields.append(tstr)                                           # 1
        tstr = time.strftime("%H:%M:%S", time.localtime(data['dateTime']))
        fields.append(tstr)                                           # 2
        fields.append(self.format(data, 'outTemp', 1))                # 3
        fields.append(self.format(data, 'outHumidity', 0))            # 4
        fields.append(self.format(data, 'dewpoint', 1))               # 5
        fields.append(self.format(data, 'windSpeed_avg', 1))          # 6  *
        fields.append(self.format(data, 'windSpeed', 1))              # 7
        fields.append(self.format(data, 'cumulus_windDir', 0))        # 8
        fields.append(self.format(data, 'rainRate', r_dp))            # 9
        fields.append(self.format(data, 'dayRain', r_dp))             # 10
        fields.append(self.format(data, 'barometer', p_dp))           # 11
        fields.append(self.format(data, 'windDir_compass'))           # 12 *
        fields.append(self.format(data, 'windSpeed_beaufort'))        # 13 *
        fields.append(self.format(data, 'units_wind'))                # 14 *
        fields.append(self.format(data, 'units_temperature'))         # 15 *
        fields.append(self.format(data, 'units_pressure'))            # 16 *
        fields.append(self.format(data, 'units_rain'))                # 17 *
        fields.append(self.format(data, 'windrun', 1))                # 18 *
        fields.append(self.format(data, 'pressure_trend', p_dp))      # 19 *
        fields.append(self.format(data, 'rain_month', r_dp))          # 20 *
        fields.append(self.format(data, 'rain_year', r_dp))           # 21 *
        fields.append(self.format(data, 'rain_yesterday', r_dp))      # 22 *
        fields.append(self.format(data, 'inTemp', 1))                 # 23
        fields.append(self.format(data, 'inHumidity', 0))             # 24
        fields.append(self.format(data, 'windchill', 1))              # 25
        fields.append(self.format(data, 'temperature_trend', 1))      # 26 *
        fields.append(self.format(data, 'outTemp_max', 1))            # 27 *
        fields.append(self.format(data, 'outTemp_max_time'))          # 28 *
        fields.append(self.format(data, 'outTemp_min', 1))            # 29 *
        fields.append(self.format(data, 'outTemp_min_time'))          # 30 *
        fields.append(self.format(data, 'windSpeed_max', 1))          # 31 *
        fields.append(self.format(data, 'windSpeed_max_time'))        # 32 *
        fields.append(self.format(data, 'windGust_max', 1))           # 33 *
        fields.append(self.format(data, 'windGust_max_time'))         # 34 *
        fields.append(self.format(data, 'pressure_max', p_dp))        # 35 *
        fields.append(self.format(data, 'pressure_max_time'))         # 36 *
        fields.append(self.format(data, 'pressure_min', p_dp))        # 37 *
        fields.append(self.format(data, 'pressure_min_time'))         # 38 *
        fields.append('%s' % weewx.__version__)                       # 39
        fields.append('0')                                            # 40
        fields.append(self.format(data, '10min_high_gust', 1))        # 41 *
        fields.append(self.format(data, 'heatindex', 1))              # 42 *
        fields.append(self.format(data, 'humidex', 1))                # 43 *
        fields.append(self.format(data, 'UV', 0))                     # 44
        fields.append(self.format(data, 'ET_today', r_dp))            # 45 *
        fields.append(self.format(data, 'radiation', 0))              # 46
        fields.append(self.format(data, '10min_avg_wind_bearing', 0)) # 47 *
        fields.append(self.format(data, 'rain_hour', r_dp))           # 48 *
        fields.append(self.format(data, 'zambretti_code'))            # 49 *
        fields.append(self.format(data, 'is_daylight'))               # 50 *
        fields.append(self.format(data, 'lost_sensors_contact'))      # 51 *
        fields.append(self.format(data, 'avg_wind_dir'))              # 52 *
        fields.append(self.format(data, 'cloudbase', 0))              # 53 *
        fields.append(self.format(data, 'units_cloudbase'))           # 54 *
        fields.append(self.format(data, 'appTemp', 1))                # 55 *
        fields.append(self.format(data, 'sunshine_hours', 1))         # 56 *
        fields.append(self.format(data, 'maxSolarRad', 1))            # 57
        fields.append(self.format(data, 'is_sunny'))                  # 58 *
        return ' '.join(fields)
