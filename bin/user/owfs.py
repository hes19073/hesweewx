#!/usr/bin/python
# owfs.py 1396 2016-01-21 05:08:45Z mwall $
#
# Copyright 2013 Matthew Wall
# Thanks to Mark Cressey (onewireweewx) and Howard Walter (TAI code).
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.
#
# See http://www.gnu.org/licenses/

"""Classes and functions for interfacing with one-wire sensors via owfs.

This file contains both a weewx driver and a weewx service.  Either will
read raw data from owfs, then the weewx calibration can be used to adjust
raw values as needed.  Mapping from one-wire device and attribute to weewx
database field is done in the OWFS section of weewx.conf.

This module requires the python bindings for owfs.  The owfs software itself
can be installed if you like, but it is not necessary; the owftpd, owhttpd,
and owserver services are not used and do not need to be running.  In fact,
it is safer to leave those services disabled to ensure that they do not
conflict with weewx when it attempts to read one-wire devices.

On debian systems, install the python bindings with something like this:

sudo apt-get install python-ow

Put this file, owfs.py, in the weewx 'user' directory, then modify weewx.conf
with something like this:

[OWFS]
    interface = u
    driver = user.owfs
    [[sensor_map]]
        inTemp = /uncached/28.8A071E050000/temperature

To use as a driver:

[Station]
    station_type = OWFS

To use as a service:

[Engine]
    [[Service]]
        data_services = user.owfs.OWFSService

The service can be bound to LOOP or ARCHIVE.  The default binding is archive;
when a new archive record is created, this service is invoked to collect data
from the one-wire bus.  The other option is loop binding; when loop data are
collected, this service is invoked to collect data from the one-wire bus.

Beware that a slow one-wire bus can adversely affect the performance and
behavior of weewx, especially when using loop binding.

Use the binding parameter to indicate LOOP or ARCHIVE binding.  For example,

[OWFS]
    binding = loop

Only numeric sensor values are supported.

By default, data from each sensor are treated as gauge.  Data types include:

  gauge - record the value as it is read from the sensor
  delta - difference between current and last reading
  average - time average by calculating the delta divided by time period
  counter - difference between current and last, always increasing

By default, the units of the sensors is assumed to be metric.  If the sensors
have been configured to output in US units, use the unit_system option.  For
example,

[OWFS]
    unit_system = US

The interface indicates where the one-wire devices are attached.  The default
value is u, which is shorthand for 'usb'.  This is the option to use for a
DS9490R USB adaptor.  Other options include a serial port such as /dev/ttyS0,
or remote_system:3003 to get data from a remote host running owserver.  For
example,

[OWFS]
    interface = /dev/ttyS0

The sensor map is simply a list of database field followed by full path to the
desired sensor reading.  Only sensor values that can be converted to float
are supported at this time.

Some devices support caching.  To use raw, uncached values, preface the path
with /uncached.

To find out what devices are actually attached:

 sudo PYTHONPATH=/home/weewx/bin python /home/weewx/bin/user/owfs.py --sensors

To display the names of data fields for each sensor, as well as actual data:

 sudo PYTHONPATH=/home/weewx/bin python /home/weewx/bin/user/owfs.py --readings

To display the value from a single sensor:

 sudo PYTHONPATH=bin python bin/user/owfs.py --reading /path/to/sensor

Details about the python bindings are at the owfs project on sourceforge:

  http://owfs.sourceforge.net/owpython.html

Example Configurations

AAG TAI8515 V3 weather station

[OWFS]
    [[sensor_map]]
        outTemp = /uncached/XX.YYYYYYYYYYYY/temperature
        windDir = /uncached/XX.YYYYYYYYYYYY              # volt.ALL
        windSpeed = /uncached/XX.YYYYYYYYYYYY            # counters.A
    [[sensor_type]]
        windDir = aag_windvane
        windSpeed = aag_windspeed

Hobby-Boards ADS wind instrument, lightning sensor, solar radiation
sensor, and rainwise rain instrument

[OWFS]
    [[sensor_map]]
        inTemp = /XX.YYYYYYYYYYYY/temperature
        UV = /XX.YYYYYYYYYYYY/UVI/UVI
        luminosity = /XX.YYYYYYYYYYYY/S3-R1-A/luminosity
        lightning = /XX.YYYYYYYYYYYY/counters.A
        rain = /XX.YYYYYYYYYYYY                          # counters.B
        windDir = /XX.YYYYYYYYYYYY                       # VAD
        windSpeed = /XX.YYYYYYYYYYYY                     # counters.A
    [[sensor_type]]
        lightning = counter
        rain = rainwise_bucket
        windDir = ads_windvane
        windSpeed = ads_windspeed

[StdCalibrate]
    [[Corrections]]
        radiation = luminosity * 1.730463

Hobby-Boards with Inspeed wind instrument

[OWFS]
    [[sensor_map]]
        windDir = /XX.YYYYYYYYYYYY                       # VAD / VDD
        windSpeed = /XX.YYYYYYYYYYYY                     # counters.A
    [[sensor_type]]
        windDir = inspeed_windvane
        windSpeed = inspeed_windspeed
"""

# FIXME: automatically detect each sensor type
# FIXME: automatically detect per-sensor units

import syslog
import time
import ow

import weewx
from weewx.drivers import AbstractDevice
from weewx.engine import StdService

DRIVER_NAME = 'OWFS'
DRIVER_VERSION = "0.18"

def logmsg(level, msg):
    syslog.syslog(level, 'owfs: %s' % msg)

def logdbg(msg):
    logmsg(syslog.LOG_DEBUG, msg)

def loginf(msg):
    logmsg(syslog.LOG_INFO, msg)

def logerr(msg):
    logmsg(syslog.LOG_ERR, msg)

def get_float(path):
    sv = ow.owfs_get(path)
    sv = sv.replace(',','.')
    v = float(sv)
    return v

def gauge(key, path, last_data, ts):
    return get_float(path)

def delta(key, path, last_data, ts):
    v = get_float(path)
    if key in last_data:
        x = v - last_data.get(key)
    else:
        x = None
    last_data[key] = v
    return x

def counter(key, path, last_data, ts):
    v = get_float(path)
    if key in last_data and v >= last_data.get(key):
        x = v - last_data.get(key)
#        if x < 0:
#            maxcnt = 0x10000 # 16-bit counter
#            if x + maxcnt < 0:
#                maxcnt = 0x100000000 # 32-bit counter
#                if x + maxcnt < 0:
#                    maxcnt = 0x10000000000000000 # 64-bit counter
#            x += maxcnt
    else:
        x = None
    last_data[key] = v
    return x

def average(key, path, last_data, ts):
    v = get_float(path)
    if key in last_data:
        (oldv, oldt) = last_data.get(key)
        if ts > oldt:
            x = (v - oldv)/(ts - oldt)
        else:
            x = None
    else:
        x = None
    last_data[key] = (v, ts)
    return x

def rainwise_bucket(key, path, last_data, ts):
    cnt = counter(key, "%s%s" % (path, "/counters.B"), last_data, ts)
    if cnt is not None:
        cnt *= 0.0254 # rainwise bucket is 0.01 inches per tip, convert to cm
    return cnt

def ads_windspeed(key, path, last_data, ts):
    ws = average(key, "%s%s" % (path, "/counters.A"), last_data, ts)
    if ws is not None:
        ws *= 2.01168 # convert to kph
    return ws

def ads_winddir(key, path, last_data, ts):
    """Calculate wind direction for Hobby-Boards ADS wind instrument.
    Get wind direction from the VAD register fo the DS2438.
    Formula from the Hobby-Boards ADS anemometer user manual."""
    v = get_float('%s%s' % (path, '/VAD'))
    wdir = None
    if 2.66 <= v <= 2.72:
        wdir = 0     # N
    elif 6.49 <= v <= 6.55:
        wdir = 22.5  # NNE
    elif 5.96 <= v <= 6.55:
        wdir = 45    # NE
    elif 9.35 <= v <= 9.41:
        wdir = 67.5  # ENE
    elif 9.27 <= v <= 9.33:
        wdir = 90    # E
    elif 9.50 <= v <= 9.56:
        wdir = 112.5 # ESE
    elif 8.48 <= v <= 8.54:
        wdir = 135   # SE
    elif 8.98 <= v <= 9.04:
        wdir = 157.5 # SSE
    elif 7.57 <= v <= 7.63:
        wdir = 180   # S
    elif 7.95 <= v <= 8.01:
        wdir = 202.5 # SSW
    elif 4.28 <= v <= 4.34:
        wdir = 225   # SW
    elif 4.59 <= v <= 4.65:
        wdir = 247.5 # WSW
    elif 0.89 <= v <= 0.95:
        wdir = 270   # W
    elif 2.20 <= v <= 2.26:
        wdir = 292.5 # WNW
    elif 1.54 <= v <= 1.60:
        wdir = 315   # NW
    elif 3.54 <= v <= 3.60:
        wdir = 337.5 # NNW
    return wdir

def inspeed_windspeed(key, path, last_data, ts):
    ws = average(key, "%s%s" % (path, "/counters.A"), last_data, ts)
    if ws is not None:
        ws *= 4.02336 # convert to kph
    return ws

def inspeed_winddir(key, path, last_data, ts):
    """Calculate wind direction for Hobby-Boards Inspeed wind instrument.
    Get wind direction from the VDD and VAD register of DS2438.
    Formula from the Hobby-Boards Inspeed anemometer user manual."""
    vdd = get_float('%s%s' % (path, '/VDD'))
    vad = get_float('%s%s' % (path, '/VAD'))
    return (400*(vad-0.05*vdd))/vdd if vdd else None

def aag_windspeed(key, path, last_data, ts):
    ws = average(key, "%s%s" % (path, "/counters.A"), last_data, ts)
    if ws is not None:
        ws *= 3.948 / 2 # speed in mph is 2.453 * cnt / 2; convert to kph
    return ws

def aag_winddir(key, path, last_data, ts):
    """Calculate wind direction for AAG TAI8515 V3 wind instrument.
    Contributed by Howard Walter, based on oww C implementation."""
    w = ow.owfs_get("%s%s" % (path, "/volt.ALL"))
    wd = w.split(',')
    wd = [float(x) for x in wd]
    mx = max(x for x in wd)
    wd = [x/mx for x in wd]
    if wd[0] < 0.26:
        if wd[1] < 0.505:
            wdir = 11
        else:
            if wd[3] < 0.755:
                wdir = 13
            else:
                wdir = 12
    else:
        if wd[1] < 0.26:
            if wd[2] < 0.505:
                wdir = 9
            else:
                wdir = 10
        else:
            if wd[2] < 0.26:
                if wd[3] < 0.505:
                    wdir = 7
                else:
                    wdir = 8
            else:
                if wd[3] < 0.26:
                    if wd[0] < 0.755:
                        wdir = 5
                    else:
                        wdir = 6
                else:
                    if wd[3] < 0.84:
                        if wd[2] < 0.84:
                            wdir = 15
                        else:
                            wdir = 14
                    else:
                        if wd[0] < 0.845:
                            if wd[1] < 0.845:
                                wdir = 3
                            else:
                                wdir = 4
                        else:
                            if wd[1] > 0.84:
                                wdir = 0
                            else:
                                if wd[2] > 0.845:
                                    wdir = 2
                                else:
                                    wdir = 1
    return 22.5 * wdir

def humhes(key, path, last_data, ts):
    tem = get_float('%s%s' % (path, '/temperature'))
    vdd = get_float('%s%s' % (path, '/VDD'))
    vdo = get_float('%s%s' % (path, '/VAD'))
    vda = (5.0 / vdd) * vdo
    SrH = (vda - 0.847847) / (29.404604 / 1000)
    dhu = (SrH + 2) / (1.0305 + (0.000044 * tem) - (0.0000011 * tem * tem))
    #dhu = (((vda / vdd) - 0.16) / 0.0062) / (1.0546 - (0.00216 * tem))
    #dhu = (SrH + 2) / (1.0305 + (0.000044 * tem) #- (0.0000011 * tem * 100))

    if dhu > 100.0:
       d = 99
    else:
       d = dhu     
    return  d
    
def lighes(key, path, last_data, ts):
    li1 = get_float('%s%s' % (path, '/vis'))
    vdd = get_float('%s%s' % (path, '/VDD'))
    vao = get_float('%s%s' % (path, '/VAD'))
    vad = (5 / vdd) * vao
    #d = (vdd - vad) * 700  # Helligkeit nach eservice
    d = li1 * 4200.0        # watt nach eservice
    if d < 0:
        d = 0

    return d

def owvolt(key, path, last_data, ts):
    vdd = get_float('%s%s' % (path, '/VDD'))
    d = vdd
    return d

def heshum(key, path, last_data, ts):
     v = get_float(path)

     if v > 100:
            v = 99
     else:
            v = v

     return v


SENSOR_TYPES = {
    'gauge': gauge,
    'delta': delta,
    'average': average,
    'counter': counter,
    'ads_windvane': ads_winddir,
    'ads_windspeed': ads_windspeed,
    'inspeed_windvane': inspeed_winddir,
    'inspeed_windspeed': inspeed_windspeed,
    'aag_windvane': aag_winddir,
    'aag_windspeed': aag_windspeed,
    'rainwise_bucket': rainwise_bucket,
    'humhes': humhes,
    'heshum': heshum,
    'lighes': lighes,
    'owvolt': owvolt,
    }

def loader(config_dict, engine):
    return OWFSDriver(**config_dict['OWFS'])

class OWFSDriver(weewx.drivers.AbstractDevice):
    """Driver for one-wire sensors via owfs."""
    
    def __init__(self, **stn_dict) :
        """Initialize the driver.

        interface: Where to find the one-wire sensors.  Options include
        u, /dev/ttyS0
        [Required. Default is u (usb)]

        sensor_map: Associate sensor values with database fields.
        [Required]

        sensor_type: Indicate how data should be processed before saving.
        [Optional. Default is gauge]

        polling_interval: How often to poll for data, in seconds.
        [Optional. Default is 10]

        unit_system: The unit system the data are assumed to be in.  Can
        be one of 'METRIC' or 'US'.  This assumes that all sensors are
        reporting data in the same unit system.
        [Optional. Default is METRIC]
        """
        self.sensor_map = stn_dict['sensor_map']
        self.sensor_type = stn_dict.get('sensor_type', {})
        self.interface = stn_dict.get('interface', 'u')
        self.polling_interval = int(stn_dict.get('polling_interval', 10))
        self.unit_system = stn_dict.get('unit_system', 'METRIC').lower()
        self.last_data = {}
        self.units = weewx.US if self.unit_system == 'us' else weewx.METRIC

        loginf('driver version is %s' % DRIVER_VERSION)
        loginf('interface is %s' % self.interface)
        loginf('sensor map is %s' % self.sensor_map)
        loginf('sensor type map is %s' % self.sensor_type)
        loginf('polling interval is %s' % str(self.polling_interval))
        loginf('sensor unit system is %s' % self.unit_system)
        ow.init(self.interface)

        # open all 1-wire channels on a Hobby Boards 4-channel hub.  see:
        #   http://owfs.org/index.php?page=4-channel-hub
#        ow.owfs_put("%s/hub/branch.BYTE" % hubpath, 15)

    @property
    def hardware_name(self):
        return 'OWFS'

    def genLoopPackets(self):
        while True:
            last_data = dict(self.last_data)
            p = {'usUnits': self.units,
                 'dateTime': int(time.time() + 0.5)}
            for s in self.sensor_map:
                p[s] = None
                st = 'gauge'
                if s in self.sensor_type:
                    st = self.sensor_type[s]
                if st in SENSOR_TYPES:
                    try:
                        func = SENSOR_TYPES[st]
                        p[s] = func(s, self.sensor_map[s],
                                    last_data, p['dateTime'])
                    except ow.exError, e:
                        logerr("Failed to get sensor data: %s" % e)
                else:
                    logerr("unknown sensor type '%s' for %s" % (st, s))
            self.last_data.update(last_data)
            self.calculate_derived(p)
            yield p
            time.sleep(self.polling_interval)

    def calculate_derived(self, data):
        if 'windSpeed' in data:
            if data['windSpeed'] is None or data['windSpeed'] == 0:
                data['windDir'] = None

class OWFSService(weewx.engine.StdService):
    """Collect data from one-wire devices via owfs."""

    def __init__(self, engine, config_dict):
        """
        interface: Where to find the one-wire sensors.  Options include
        u, /dev/ttyS0
        [Required. Default is u (usb)]

        sensor_map: Associate sensor values with database fields.
        [Required]

        sensor_type: Indicates how data should be processed before saving.
        [Optional. Default is gauge]
        """
        super(OWFSService, self).__init__(engine, config_dict)

        d = config_dict.get('OWFS', {})
        self.sensor_map = d['sensor_map']
        self.sensor_type = d.get('sensor_type', {})
        self.interface = d.get('interface', 'u')
        self.unit_system = d.get('unit_system', 'METRIC').lower()
        self.binding = d.get('binding', 'archive')
        self.last_data = {}
        self.units = weewx.US if self.unit_system == 'us' else weewx.METRIC

        loginf('service version is %s' % DRIVER_VERSION)
        loginf('binding is %s' % self.binding)
        loginf('interface is %s' % self.interface)
        loginf('sensor map is %s' % self.sensor_map)
        loginf('sensor type map is %s' % self.sensor_type)
        loginf('sensor unit system is %s' % self.unit_system)

        ow.init(self.interface)
        if self.binding == 'loop':
            self.bind(weewx.NEW_LOOP_PACKET, self.handle_new_loop)
        else:
            self.bind(weewx.NEW_ARCHIVE_RECORD, self.handle_new_archive)

    def handle_new_loop(self, event):
        data = self.getData(event.packet)
        event.packet.update(data)

    def handle_new_archive(self, event):
        delta = time.time() - event.record['dateTime']
        if delta > event.record['interval'] * 60:
            logdbg("Skipping record: time difference %s too big" % delta)
            return
        data = self.getData(event.record)
        event.record.update(data)

    # this implementation assumes that data from one-wire sensors are metric.
    # if the packets to which we append are something other than metric, then
    # we do a conversion after we have all the data.
    def getData(self, packet):
        last_data = dict(self.last_data)
        p = {'usUnits': self.units}
        for s in self.sensor_map:
            p[s] = None
            st = 'gauge'
            if s in self.sensor_type:
                st = self.sensor_type[s]
            if st in SENSOR_TYPES:
                func = SENSOR_TYPES[st]
                try:
                    p[s] = func(s, self.sensor_map[s],
                                last_data, packet['dateTime'])
                except ow.exError, e:
                    logerr("Failed to get onewire data: %s" % e)
            else:
                logerr("unknown sensor type '%s' for %s" % (st, s))
        self.last_data.update(last_data)

        if packet['usUnits'] != self.units:
            p['usUnits'] = self.units
            converter = weewx.units.StdUnitConverters[packet['usUnits']]
            p = converter.convertDict(p)
            if 'usUnits' in p:
                del p['usUnits']
        return p

# define a main entry point for basic testing without weewx engine and service
# overhead.  invoke this as follows from the weewx root dir:
#
# PYTHONPATH=bin python bin/user/owfs.py
if __name__ == '__main__':
    usage = """%prog [options] [--debug] [--help]"""

    def main():
        import optparse
        syslog.openlog('wee_owfs', syslog.LOG_PID | syslog.LOG_CONS)
        parser = optparse.OptionParser(usage=usage)
        parser.add_option('--version', dest='version', action='store_true',
                          help='display driver version')
        parser.add_option('--debug', dest='debug', action='store_true',
                          help='display diagnostic information while running')
        parser.add_option("--iface", dest="iface", type=str, metavar="IFACE",
                          help="specify the interface, e.g., u or /dev/ttyS0")
        parser.add_option('--sensors', dest='sensors', action='store_true',
                          help='display list attached sensors')
        parser.add_option('--readings', dest='readings', action='store_true',
                          help='display sensor readings')
        parser.add_option('--reading',dest='reading',type=str,metavar="SENSOR",
                          help='display output of specified sensor')
        (options, args) = parser.parse_args()

        if options.version:
            print "owfs version %s" % DRIVER_VERSION
            exit(1)

        # default to usb for the interface
        iface = options.iface if options.iface is not None else 'u'

        if options.debug is not None:
            syslog.setlogmask(syslog.LOG_UPTO(syslog.LOG_DEBUG))
        else:
            syslog.setlogmask(syslog.LOG_UPTO(syslog.LOG_INFO))

        if options.sensors:
            ow.init(iface)
            traverse(ow.Sensor('/'), identify_sensor)
        elif options.readings:
            ow.init(iface)
            traverse(ow.Sensor('/'), display_sensor_info)
        elif options.reading:
            ow.init(iface)
            print '%s: %s' % (options.reading, ow.owfs_get(options.reading))

    def identify_sensor(s):
        print '%s: %s %s' % (s.id, s._path, s._type)

    def display_sensor_info(s):
        print s.id
        display_dict(s.__dict__)

    def display_dict(d, level=0):
        for k in d:
            if isinstance(d[k], dict):
                display_dict(d[k], level=level+1)
            elif k == 'alias':
                pass
            elif k.startswith('_'):
                print '%s%s: %s' % ('  '*level, k, d[k])
            else:
                v = 'UNKNOWN'
                try:
                    v = ow.owfs_get(d[k])
                except ow.exError, e:
                    v = 'FAIL: %s' % e
                print '%s%s: %s' % ('  '*level, d[k], v)

    def traverse(device, func):
        for s in device.sensors():
            if s._type in ['DS2409']:
                traverse(s, func)
            else:
                func(s)

if __name__ == '__main__':
    main()
