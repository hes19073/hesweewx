#!/usr/bin/python
# Copyright 2013-2020 Matthew Wall
# Thanks to Mark Cressey (onewireweewx) and Howard Walter (TAI code).
# The Dallas windvane added by Glenn McKechnie.
#
# Copyright 2020-2021 Glenn McKechnie
# also pyownet /  pyownet_readings  in __name__ section
# https://github.com/glennmckechnie/weewx-owfs
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

ow-python documents can be found at http://owfs.sourceforge.net/owpython.html
OWFS main site https://owfs.org

or find the code locally. eg:-
/usr/lib/python2.7/dist-packages/ow/__init__.py

This file contains both a weewx driver and a weewx service.  Either will
read raw data from owfs, then the weewx calibration can be used to adjust
raw values as needed.  Mapping from one-wire device and attribute to weewx
database field is done in the OWFS section of weewx.conf.

This module requires either the python bindings for owfs, or the pyownet
module which requires owserver.

====

For python-ow (owbinding):

The owfs software itself can be installed if you like, but it is not necessary;
the owftpd, owhttpd, and owserver services are not used and do not need to be
running.  In fact, it is safer to leave those services disabled to ensure that
they do not conflict with weewx when it attempts to read one-wire devices.

On debian systems, install the python bindings with something like this:


python2.7 for weewx versions <= 3.9.2
sudo apt-get install python-ow

python3.x for weewx versions > 4
( if it is available, it's now missing from a few distros.)
sudo apt install python3-ow

then in weewx.conf you will use the following...
[OWFS]
    interface = u
    driver = user.owfs
    [[sensor_map]]
        inTemp = /uncached/28.8A071E050000/temperature

====

For pyownet (ownetbinding)

The owfs software is required when using this module. The owserver is essential
and owshell may be helpful.

python2.7 for weewx versions <= 3.9.2
sudo apt-get install owserver
sudo apt-get install pyownet

python3.x for weewx versions > 4
sudo apt-get install owserver
pip3 install pyownet (if it is not available via apt-get.
(use apt-get install pip3-python to install pip3 )

then in weewx.conf you will use the following...
[OWFS]
    driver = user.owfs
    [[sensor_map]]
        inTemp = /uncached/28.8A071E050000/temperature

To configure the owserver, move aside the contents of /etc/owfs.conf and create
a new file with the contents as follows, and uncommenting one of the first 3
device entries...

#! server: server = localhost:4304
#server: usb = all # for a DS9490
#server: device = /dev/ttyS1 # for a serial port
#server: device /dev/i2c-1 # for a pi using i2c-1
server: port = 4304

owserver must be configured and succesfully running before weewx can use it.

=======

Owserver and systemd.

Running owserver under systemd. This applies to the majority of recent
(2019) linux distributions but if you have no problems then there is no
need to use this section.

A problem that has been occuring with owserver on Debian Buster installs
is a refusal to start and run. There's no rhyme or reason to it, and it
magically fixes itself. ?

The following post describes a possible fix for that problem.

https://sourceforge.net/p/owfs/mailman/message/36765345/
part of...
https://sourceforge.net/p/owfs/mailman/owfs-developers/?viewmonth=201909

In summary, and quoting an extract from the above post ...

"/etc/systemd/system/owserver.service.d/override.conf is an override
file, that you create with"
sudo systemctl edit owserver.service

then add the following content...

# /etc/systemd/system/owserver.service.d/override.conf
[Service]
User=Debian-ow
Group=Debian-ow
ExecStart=
ExecStart=/usr/bin/owserver -c /etc/owfs.conf --foreground

[Install]
Also=


This disables the use of sockets for owserver, and brings the daemon to
the foreground.
Running owserver under systemd. (This applies to the majority of recent
linux distributions.)

======
Then proceed to the installation of this file or package

Place this file, owfs.py, in the weewx 'user' directory or use wee_extension
to install the package.
The following manual changes will need to be noted depending on your setup.

To use as a driver:

[Station]
    station_type = OWFS

[OWFS]
    driver = user.owfs

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

The interface indicates where the one-wire devices are attached.

Python2.x :

The default value is u, which is shorthand for 'usb'.  This is the option to
use for a DS9490R USB adaptor.  Other options include a serial port such as
/dev/ttyS0, or remote_system:3003 to get data from a remote host running
owserver.  For example,

[OWFS]
    interface = /dev/ttyS0 # for a serial port

[OWFS]
    interface = /dev/i2c-1 # for a pi using the i2c interface

Python3.x :

With python3 the pyownet module will be used and this requires the installation
and configuration of owserver. This is covered in detail above.
The interface can be omitted as the default value of
interface = localhost:4304
is hard coded and this will be suitable for most installations.


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

DALLAS Weathervane

[OWFS]

    [[sensor_map]]
        outTemp = /XX.YYYYYYYYYYYY/temperature
        inTemp = /XX.YYYYYYYYYYYY/temperature
        windDir = XX.YYYYYYYYYYYY
        windSpeed = /XX.YYYYYYYYYYYY
        rain = /XX.YYYYYYYYYYYY/counters.A

    [[sensor_type]]
        windDir = dallas_windvane
        windSpeed = aag_windspeed
        rain = rainwise_bucket

    [[sensor_direction]]
        XX.YYYYYYYYYYYY = 360
        XX.YYYYYYYYYYYY = 45
        XX.YYYYYYYYYYYY = 90
        XX.YYYYYYYYYYYY = 135
        XX.YYYYYYYYYYYY = 180
        XX.YYYYYYYYYYYY = 225
        XX.YYYYYYYYYYYY = 270
        XX.YYYYYYYYYYYY = 315

Also, if using the Dallas instrument, read the comments in the
dallas_winddir section below.

----
https://github.com/weewx/weewx/wiki/WeeWX-v4-and-logging

DEBUG messages

[Logging]
    [[loggers]]
        [[[user.owfs-dallas]]]
            level = DEBUG
            handlers = syslog,
            propagate = 0

"""

# FIXME: consider calling this extension weewx-ow instead of weewx-owfs
# FIXME: automatically detect each sensor type
# FIXME: automatically detect per-sensor units

import time

try:
    # weewx4 logging
    import weeutil.logger
    import logging
    log = logging.getLogger(__name__)
    def logdbg(msg):
        log.debug(msg)
    def loginf(msg):
        log.info(msg)
    def logerr(msg):
        log.error(msg)
except ImportError:
    # old-style weewx logging
    import syslog
    def logmsg(level, msg):
        syslog.syslog(level, 'owfs-gmck: %s' % msg)
    def logdbg(msg):
        logmsg(syslog.LOG_DEBUG, msg)
    def loginf(msg):
        logmsg(syslog.LOG_INFO, msg)
    def logerr(msg):
        logmsg(syslog.LOG_ERR, msg)


import weewx
from weewx.drivers import AbstractDevice
from weewx.engine import StdService

DRIVER_NAME = 'OWFS-gmck'
DRIVER_VERSION = "0.23.8"


class OWError(Exception):
    pass

class OWFSBinding(object):
    def __init__(self):
        import ow as owbinding
    def init(self, iface=None):
        import ow as owbinding
        if iface is None:
            iface = 'u'
        loginf('ow interface set as %s' % iface)
        owbinding.init(str(iface))
    def finish(self):
        import ow as owbinding
        try:
            owbinding.finish()
        except owbinding.exError as e:
            raise OWError(e)
    def get(self, path):
        import ow as owbinding
        try:
            return owbinding.owfs_get(path)
        except owbinding.exError as e:
            raise OWError(e)
    def put(self, path, value):
        import ow as owbinding
        try:
            owbinding.owfs_put(path, value)
        except owbinding.exError as e:
            raise OWError(e)
    def Sensor(self, path):
        import ow as owbinding
        return owbinding.Sensor(path)


class OWNetBinding(object):
    def __init__(self):
        import pyownet
        self.proxy = None
    def init(self, iface=None):
        host = 'localhost'
        port = 4304
        if iface is not None:
            if ':' in iface:
                host, port = iface.split(':')
                port = int(port)
            else:
                host = str(iface)
        loginf('pyownet interface set as %s:%s' % (host, port))
        import pyownet
        try:
            self.proxy = pyownet.protocol.proxy(host=host, port=port)
        except pyownet.Error as e:
            logerr(" ** is the owserver installed and running?")
            logerr(" ** ")
            raise OWError(e)
    def finish(self):
        self.proxy = None
    def get(self, path):
        import pyownet
        try:
            return self.proxy.read(path)
        except pyownet.Error as e:
            raise OWError(e)
    def put(self, path, value):
        import pyownet
        try:
            # from pyownet.protocol.str2bytez
            value = value.encode('ascii') + b'\x00'
            self.proxy.write(path, value)
        except pyownet.Error as e:
            raise OWError(e)

    def Sensor(self, path):
        import pyownet
        try:
            # print(path)
            return self.proxy.dir(path)
        except pyownet.Error as e:
            raise OWError(e)

try:
    ow = OWFSBinding()
    DRIVER_VERSION = DRIVER_VERSION+" (ow)"
except ImportError:
    try:
        ow = OWNetBinding()
        DRIVER_VERSION = DRIVER_VERSION+" (pyownet)"
    except ImportError:
        raise Exception("No one-wire library found")


def get_float(path):
    sv = ow.get(path)
    try:
        sv = sv.replace(',','.')
    except:
        # required for pyownet and weewx4
        sv = sv.replace(b',',b'.')
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

def rain_withpath(key, path, last_data, ts):
    # different to rainwise_bucket in that the full path needs to be given
    # in the weewx.conf file [OWFS][[sensor_map]] section
    cnt = counter(key, path, last_data, ts)
    try:
        cnt *= 0.0254  # for 0.01 inches per tip, convert to cm
    except:
        cnt = None
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
    w = ow.get("%s%s" % (path, "/volt.ALL"))
    try:
        wd = w.split(',')
    except TypeError:
        wd = w.split(b',')
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

def dallas_winddir(key, path, last_data, ts, **kwargs):
    """
    https://groups.google.com/d/topic/weewx-user/tj0n9uYUL20/discussion
    The Original Dallas wind vane has DS2401 sensors...
    https://web.archive.org/web/20061018205111/http://archives.sensorsmag.com/articles/0698/wir0698/
    The addresses of the DS2401's need to be found and
    recorded in weewx.conf as the example below shows.

    Also a sensor_type of windDir = dallas_windvane and
    and sensor_map entry of windDir = /XX.XXXXXXXXXXXX
    A sensor_direction section also needs to be added where
    each sensor is mapped to its direction in degrees.
    With that done the dallas_windvane code can begin to detect
    the actual DS2401 addresses.

    The OWFS section will be formatted something like this.
    The actual address values will be changed to suit yours.

    [OWFS]
        interface = localhost:4304  # or as suits your installation.
        driver = user.owfs

        [[sensor_type]]
            windDir = dallas_windvane
            windSpeed = aag_windspeed
            rain = rainwise_bucket

        [[sensor_map]]
            outTemp = /uncached/XX.YYYYYYYYYYYY/temperature
            inTemp = /uncached/XX.YYYYYYYYYYYY/temperature
            windDir = /12.5EAB0D000000
            windSpeed = /uncached/XX.YYYYYYYYYYYY
            rain = /uncached/XX.YYYYYYYYYYYY/counters.A

        [[sensor_direction]]
            01.B5374A040000 = 360
            01.B2374A040000 = 45
            01.BA374A040000 = 90
            01.B7374A040000 = 135
            01.C6374A040000 = 180
            01.C3374A040000 = 225
            01.BD374A040000 = 270
            01.AE374A040000 = 315


    The values in the above example configuration would involve running
    the following in a terminal. (adjust paths if required)

    cd /home/weewx
    PYTHONPATH=bin python  bin/user/owfs.py --iface=localhost:4304 --sensors
    id B2374A040000: path /01.B2374A040000 s._type DS2401

    Take a note of the path returned for any DS2401 sensor and match it
    to a physical direction. Ignore the instances that might return 2
    sensors, they are the intermediate points and are calculated by the
    software function.
    Rotate the Dallas weather vane manually to the next compass point
    (1 of 8 : N, NW, W etc ) Again, the intermediate points (ENE, WSW etc)
    are calculated within the driver section.
    Rinse repeat for the 8 *cardinal points.

    Make a note of where North points on your unit. It's arbitary but once
    you're up the ladder, you'll want to know it!
    """
    # """
    # # manual test for DS2406 presence and switch values
    # path = '/12.5EAB0D000001'
    # Ra = '/12.92400E000000/PIO.A'
    # Rb = '/12.92400E000000/PIO.B'
    # Wa = path+'/PIO.A'
    # Wb = path+'/PIO.B'
    # try:
    #    logdbg("%s : A- %s B- %s" % (Ra, int(ow.get(Ra)), int(ow.get(Rb))))
    # except:
    #    logdbg("DS2406 %s is being troublesome" % Ra)
    # try:
    #    logdbg("%s : A- %s B- %s" % (path, int(ow.get(Wa)), int(ow.get(Wb))))
    # except:
    #    logdbg("DS2406 %s is being troublesome" % Wa)

    f_sns = []
    # test if the controlling DS2406 is available
    # and if it exists turn it on.
    try:
        ow.get("%s%s" % (path, "/PIO.B"))
        try:
            ow.put(("%s%s" % (path, "/PIO.B")), '1')
            try:
                s_tate = int(ow.get("%s%s" % (path, "/PIO.B")))
                logdbg("DS2406 switched on ? : %s" % (s_tate))
            except Exception as e:
                logdbg("Failed to turn on DS2406: %s get %s" % (path, e))
        except (OWError, ValueError) as e:
            logdbg("pyownet error ? : %s" % e)
    except OWError as e:
        logdbg("Missing DS2406 %s err %s" % (path, e))
        # The controlling sensor is missing, but the DS2401's
        # may still be visible so we'll roll on through.
    except Exception:
        logdbg("Unknown exception")
        raise
    try:
        # scan for any DS2401's whether DS2406 was present
        # or not as sometimes they are available.
        for x in kwargs:
            # --#logdbg("x is %s of type %s" % (x, type(x)))
            try:
                ow.get("%s%s%s" % ("/uncached", x, "/address"))
                f_sns.append(x)
                logdbg("Found DS2401 %s" % x)
                # logdbg("Found DS2401 %s" % type(x))
            except OWError as e:
                # logdbg("DS2401 %s not found %s" % (x, e))
                pass
    except:
        raise

    # Create at least 2 entries, regardless of what we found
    f_sns.append(None)
    f_sns.append(None)

    # Turn off the DS2406 switch to declutter the bus?
    # Apparently it's recommended, it doesn't seem to matter though.
    ow.put(("%s%s" % (path, "/PIO.B")), '0')
    try:
        s_tate = int(ow.get("%s%s" % (path, "/PIO.B")))
        logdbg("DS2406 switched off? : %s" % (s_tate))
    except Exception as e:
        pass
        # logdbg("Still missing the DS2406 %s : %s" % (path, e))

    if f_sns[0] is not None:
        pth1 = str(f_sns[0])
        pth2 = str(f_sns[1])
        logdbg(" *** NEW list %s" % f_sns)
        ## logdbg(" NEW pth1 =  %s, pth2 = %s" % (f_sns[0], f_sns[1]))
        # The f_sns[0] primary key direction, or None
        p_deg = kwargs[pth1]
        # we may have a secondary key, check and record
        # logdbg("p_deg is %s" % p_deg)
        if f_sns[1] is not None:
            s_deg = kwargs[pth2]
            if s_deg == '45' and p_deg == '360':
                p_deg = 0
            wdir = (float(p_deg) + float(s_deg))/2
        else:
            s_deg = None
            wdir = float(p_deg)

        logdbg(" *** NEW --> %s <-- wdir degrees ... derived from %s and %s" % (wdir, p_deg, s_deg))
    else:
        logdbg("No DS2401 sensors were detected")
        wdir = None

    return wdir


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
    'dallas_windvane': dallas_winddir,
    'rain_fullpath': rain_withpath,
    }

def loader(config_dict, engine):
    return OWFSDriver(**config_dict['OWFS'])

class OWFSDriver(AbstractDevice):
    """Driver for one-wire sensors via owfs."""

    def __init__(self, **stn_dict):
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
        self.sensor_dir = stn_dict.get('sensor_direction', {})
        self.interface = stn_dict.get('interface', None)
        self.polling_interval = int(stn_dict.get('polling_interval', 10))
        self.unit_system = stn_dict.get('unit_system', 'METRIC').lower()
        self.last_data = {}
        self.units = weewx.US if self.unit_system == 'us' else weewx.METRIC

        loginf('driver version is %s' % DRIVER_VERSION)
        loginf('interface starts as %s' % self.interface)
        loginf('sensor map is %s' % self.sensor_map)
        loginf('sensor type map is %s' % self.sensor_type)
        loginf('dallas direction map is %s' % self.sensor_dir)
        loginf('polling interval is %s' % str(self.polling_interval))
        loginf('sensor unit system is %s' % self.unit_system)

        ow.init(self.interface)

        # open all 1-wire channels on a Hobby Boards 4-channel hub.  see:
        #   http://owfs.org/index.php?page=4-channel-hub
        # ow.put("%s/hub/branch.BYTE" % hubpath, 15)

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
                # https://www.element14.com/community/groups/ \
                # internet-of-things/blog/2015/01/07/old-meets-new- \
                # the-1-wire-weather-station-on-the-spark-core-part-5
                # Notice that the bus master can only read wind direction
                # information when the DS2407 addressable switch is closed.
                # This is for isolation reasons, otherwise, communication would
                # be disrupted each time a reed switch closed and the DS2401
                # associated with it signaled its presence on the line.
                # Communication with the wind direction sensor therefore begins
                # when the bus master turns on the DS2407 output, connecting
                # one side of all the DS2401s to the 1-Wire bus ground line.
                if st in SENSOR_TYPES:
                    func = SENSOR_TYPES[st]
                    # loginf("map of type %s " % type(self.sensor_map[s]))
                    if st == "dallas_windvane":
                        try:
                            p[s] = func(s, str(self.sensor_map[s]),
                                        last_data, p['dateTime'],
                                        **self.sensor_dir)
                        except (OWError, ValueError) as e:
                            logerr("Failed to get Dallas sensor data for %s (%s): %s" %
                                   (s, st, e))
                        continue
                    else:
                        try:
                            p[s] = func(s, str(self.sensor_map[s]),
                                        last_data, p['dateTime'])
                        except (OWError, ValueError) as e:
                            logerr("Failed to get sensor data for %s (%s): %s" %
                                   (s, st, e))
                else:
                    logerr("unknown sensor type '%s' for %s" % (st, s))
            self.last_data.update(last_data)
            yield p
            time.sleep(self.polling_interval)

    def closePort(self):
        ow.finish()


class OWFSService(StdService):
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
        self.sensor_dir = d.get('sensor_direction', {})
        self.interface = d.get('interface', None)
        self.unit_system = d.get('unit_system', 'METRIC').lower()
        self.binding = d.get('binding', 'archive')
        self.last_data = {}
        self.units = weewx.US if self.unit_system == 'us' else weewx.METRIC

        loginf('service version is %s' % DRIVER_VERSION)
        loginf('binding is %s' % self.binding)
        loginf('interface starts as %s' % self.interface)
        loginf('sensor map is %s' % self.sensor_map)
        loginf('sensor type map is %s' % self.sensor_type)
        loginf('dallas direction map is %s' % self.sensor_dir)
        loginf('sensor unit system is %s' % self.unit_system)

        ow.init(self.interface)

        if self.binding == 'loop':
            self.bind(weewx.NEW_LOOP_PACKET, self.handle_new_loop)
        else:
            self.bind(weewx.NEW_ARCHIVE_RECORD, self.handle_new_archive)

    def shutDown(self):
        ow.finish()

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
                if st == "dallas_windvane":
                    try:
                        p[s] = func(s, str(self.sensor_map[s]),
                                    last_data, packet['dateTime'],
                                    **self.sensor_dir)
                    except (OWError, ValueError) as e:
                        logerr("Failed to get Dallas sensor data for %s (%s): %s" %
                               (s, st, e))
                    continue
                else:
                    try:
                        p[s] = func(s, str(self.sensor_map[s]),
                                    last_data, packet['dateTime'])
                    except (OWError, ValueError) as e:
                        logerr("Failed to get onewire data for %s (%s): %s" %
                               (s, st, e))
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
        parser.add_option('--pyownet_readings', dest='pyownet_readings',
                          action='store_true',
                          help='display sensor readings via pyownet')
        parser.add_option('--reading', dest='reading', type=str,
                          metavar="SENSOR",
                          help='display output of specified sensor')
        parser.add_option('--dallas', dest='dallas',
                          type=str, metavar="12.X...X",
                          help='display DS2401 sensor/s that are visible. A \
                          DS2406 address must be supplied.')
        (options, args) = parser.parse_args()

        if options.version:
            print("owfs version %s" % DRIVER_VERSION)
            exit(1)

        try:
            # python-ow
            ow = OWFSBinding()
            print("Using module ow")

            def identify_sensor(s):
                print('id %s: path %s s._type %s' % (s.id, s._path, s._type))

            def display_sensor_info(s):
                print(s.id)
                print("display_sensor_info is %s" % s)
                display_dict(s.__dict__)

            def display_dict(d, level=0):
                v = None
                for k in d:
                    if isinstance(d[k], dict):
                        display_dict(d[k], level=level+1)
                    elif k == 'alias':
                        pass
                    elif k.startswith('_'):
                        print('%s%s: %s' % ('  '*level, k, d[k]))
                    else:
                        v = 'UNKNOWN'
                        try:
                            v = ow.get(d[k])
                        except OWError as e:
                            v = 'FAIL: %s' % e
                        try:
                            print('%s%s: %s' % ('  '*level, d[k], v))
                        except UnicodeEncodeError as e:
                            print(e)

            def traverse(device, func):
                for s in device.sensors():
                    if s._type in ['DS2409']:
                        traverse(s, func)
                    else:
                        func(s)

            try:
                iface = options.iface if options.iface is not None else 'u'
            except Exception as e:
                print("something bad happened %s" % e)

            if options.sensors:
                ow.init(iface)
                traverse(ow.Sensor('/'), identify_sensor)
            elif options.dallas:
                ow.init(iface)
                # if using a dallas station, or there are DS2406 chips, these
                # may need to be turned on by supplying the address of the
                # controlling DS2406
                try:
                    ow.put(("/%s%s" % (options.dallas, "/PIO.B")), '1')  # on
                    print(ow.get("/%s%s" % (options.dallas, "/PIO.B")))
                except Exception as e:
                    print("ow.put returned an error: %s" % e)
                traverse(ow.Sensor('/'), identify_sensor)
            elif options.readings:
                ow.init(iface)
                traverse(ow.Sensor('/'), display_sensor_info)
            elif options.pyownet_readings:
                print('Not available via python-ow module')
            elif options.reading:
                ow.init(iface)
                print('%s: %s' % (options.reading, ow.get(options.reading)))
            print("\nUsing module ow")

        except ImportError:
            try:
                # pyownet
                ow = OWNetBinding()
                print("Using module pyownet")

                import pyownet
                iface = "localhost:4304"

                def read_paths(more):
                    chnl = '1'
                    for pth in ow.Sensor('/'):
                        sensor_type = pth+'type'
                        b_type = bytes.decode(ow.get(sensor_type))
                        hub_main = pth+'main'
                        hub_aux = pth+'aux'
                        try:
                            sensor_type = bytes.decode(ow.get(sensor_type))
                        except AttributeError as e:
                            print('exception %s' % e)
                        if sensor_type == 'DS2409':
                            print('channel %s --main' % chnl)
                            nest_path = ow.Sensor(hub_main)
                            id_sensor(nest_path, more)
                            print('           --aux')
                            nest_path = ow.Sensor(hub_aux)
                            id_sensor(nest_path, more)
                            chnl = int(chnl)+1
                        elif sensor_type == 'DS1420':
                            print("sensor type: %s located at: %s\n" % (
                                   sensor_type, pth))
                        elif sensor_type:
                            more = False
                            nest_path = ow.Sensor('/')
                            print('sensor type: %s located at: %s' % (
                                   b_type, pth))
                            read_sensors(pth, b_type)
                            chnl = int(chnl)+1

                def id_sensor(nest_path, more):
                    for tt in nest_path:
                        type_path = tt+'type'
                        try:
                            ow.get(type_path)
                        except AttributeError as e:
                            print('id sensor exception as %s' % e)
                        sensor_type = bytes.decode(ow.get(type_path))
                        print('sensor type: %s located at: %s' % (sensor_type,
                                                                  tt))
                        if more:
                            read_sensors(tt, sensor_type)

                def read_sensors(nest_path, sensor_type):
                    if sensor_type == 'DS18S20':
                        temp = nest_path+'temperature'
                        print(" temperature\t%s\n" % bytes.decode(ow.get(temp)))
                    elif sensor_type == 'DS2423':
                        countA = nest_path+'counters.A'
                        countB = nest_path+'counters.B'
                        countALL = nest_path+'counters.ALL'
                        print(" counters.A\t%s\n counters.B\t%s\n counters.ALL\t%s\n" %
                              (bytes.decode(ow.get(countA)),
                               bytes.decode(ow.get(countB)),
                               bytes.decode(ow.get(countALL))))
                    elif sensor_type == 'DS2438':
                        vad = nest_path+'VAD'
                        vdd = nest_path+'VDD'
                        temp = nest_path+'temperature'
                        hum = nest_path+'humidity'
                        pres = nest_path+'B1-R1-A/pressure'
                        illum = nest_path+'S3-R1-A/illuminance'
                        print(" VAD \t\t%s\n VDD \t\t%s\n temperature\t%s" %
                              (bytes.decode(ow.get(vad)),
                               bytes.decode(ow.get(vdd)),
                               bytes.decode(ow.get(temp))))
                        print(" humidity\t%s\n pressure\t%s\n illuminance\t%s\n" %
                              (bytes.decode(ow.get(hum)),
                               bytes.decode(ow.get(pres)),
                               bytes.decode(ow.get(illum))))
                    elif sensor_type == 'DS2450':
                        vall = nest_path+'volt.ALL'
                        vall2 = nest_path+'volt2.ALL'
                        latestvall = nest_path+'latestvolt.ALL'
                        latestvall2 = nest_path+'latestvolt2.ALL'
                        PIOall = nest_path+'PIO.ALL'
                        print(" volt.ALL\t\t%s\n volt2.ALL\t\t%s" %
                              (bytes.decode(ow.get(vall)),
                               bytes.decode(ow.get(vall2))))
                        print(" latestvolt.ALL \t%s\n latestvolt2.ALL\t%s" %
                              (bytes.decode(ow.get(latestvall)),
                               bytes.decode(ow.get(latestvall2))))
                        print(" PIO.ALL\t\t%s\n" % bytes.decode(ow.get(PIOall)))
                    else:
                        print(" Nothing coded for this sensor\n %s\n" % ow.Sensor(nest_path))

                def print_details(ground):
                    v = 'UNKNOWN'
                    g_round = list(ow.Sensor(ground))
                    for val in g_round:
                        s_type = ow.get(val+'type').decode('utf-8')
                        print('\n ** Sensor is a %s at %s\n' % (s_type, val))
                        for lev_val in ow.Sensor(val):
                            try:
                                v = ow.get(lev_val)
                            except OWError as e:
                                if "directory" in str(e):
                                    v = ' **** Ignoring Directory'
                                else:
                                    v = e
                            except Exception as e:
                                print("except as %s" % e)
                            try:
                                v = v.decode('utf-8')
                            except:
                                v = v
                            try:
                                print('%s%s:\t%s' % ('  ', lev_val, v))
                            except UnicodeDecodeError as e:
                                print('%s%s:***Not Displaying Memory Content' %
                                      ('  ', lev_val))
                                continue

                def display_pyownet(b_asement):
                    v = None
                    s_type = ow.get(b_asement+'type').decode('utf-8')
                    print('\n ** Sensor is a %s at %s\n' % (s_type, b_asement))

                    for floor in ow.Sensor(b_asement):
                        if 'aux' in floor:
                            print("\n ** HUB aux **")
                            print_details(floor)
                        elif 'main' in floor:
                            print("\n ** HUB main **")
                            print_details(floor)
                        else:
                            v = 'UNKNOWN'
                            try:
                                v = ow.get(floor)
                            except OWError as e:
                                if "directory" in str(e):
                                    v = ' *** Ignoring Directory'
                                else:
                                    v = e
                            except Exception as e:
                                print("except as %s" % e)
                            try:
                                v = v.decode('utf-8')
                            except:
                                v = v
                            try:
                                print('%s%s:\t\t\t%s' % ('  ', floor, v))
                            except UnicodeEncodeError as e:
                                print('%s%s: *** Not Displaying Memory Content' %
                                      ('  ', floor))
                                continue
                            except UnicodeDecodeError as e:
                                # python 2.7
                                print('%s%s: *** Not Displaying Memory Content' %
                                      ('  ', floor))
                                continue

                def travers(device, func):
                    for sensor in ow.Sensor('/'):
                        display_pyownet(sensor)

                if options.sensors:
                    ow.init(iface)
                    nest_path = ow.Sensor('/')
                    id_sensor(nest_path, more=False)
                elif options.dallas:
                    ow.init(iface)
                    # if using a dallas station, or there are DS2406 chips,
                    # these may need to be turned on by supplying the address
                    # of the controlling DS2406
                    try:
                        ow.put(("/%s%s" % (options.dallas, "/PIO.B")), '1')  #on
                        print(ow.get("/%s%s" % (options.dallas, "/PIO.B")))
                    except Exception:
                        raise
                    read_paths(more=False)
                elif options.readings:
                    ow.init(iface)
                    travers(ow.Sensor('/'), display_pyownet)
                elif options.pyownet_readings:
                    ow.init(iface)
                    read_paths(more=True)
                elif options.reading:
                    ow.init(iface)
                    print("reading for this sensor -> %s" %
                          bytes.decode(ow.get(options.reading)))
                print("\nUsing module pyownet")

            except ImportError:
                raise Exception("No one-wire library found")
if __name__ == '__main__':
    main()

