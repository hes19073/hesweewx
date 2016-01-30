#!/usr/bin/env python
#
# Copyright 2014 Matthew Wall
# See the file LICENSE.txt for your rights.

"""Driver for ADS WS1 weather stations.

Thanks to Steve (sesykes71) for the testing that made this driver possible.

Thanks to Jay Nugent (WB8TKL) and KRK6 for weather-2.kr6k-V2.1
  http://server1.nuge.com/~weather/
"""

from __future__ import with_statement
import serial
import syslog
import time

import weewx.drivers

DRIVER_NAME = 'WS1'
DRIVER_VERSION = '0.20'


def loader(config_dict, _):
    return WS1Driver(**config_dict[DRIVER_NAME])

def confeditor_loader():
    return WS1ConfEditor()


INHG_PER_MBAR = 0.0295333727
METER_PER_FOOT = 0.3048
MILE_PER_KM = 0.621371

DEFAULT_PORT = '/dev/ttyS0'
DEBUG_READ = 0


def logmsg(level, msg):
    syslog.syslog(level, 'ws1: %s' % msg)

def logdbg(msg):
    logmsg(syslog.LOG_DEBUG, msg)

def loginf(msg):
    logmsg(syslog.LOG_INFO, msg)

def logerr(msg):
    logmsg(syslog.LOG_ERR, msg)

class WS1Driver(weewx.drivers.AbstractDevice):
    """weewx driver that communicates with an ADS-WS1 station
    
    port - serial port
    [Required. Default is /dev/ttyS0]

    max_tries - how often to retry serial communication before giving up
    [Optional. Default is 5]

    retry_wait - how long to wait, in seconds, before retrying after a failure
    [Optional. Default is 10]
    """
    def __init__(self, **stn_dict):
        self.port = stn_dict.get('port', DEFAULT_PORT)
        self.max_tries = int(stn_dict.get('max_tries', 5))
        self.retry_wait = int(stn_dict.get('retry_wait', 10))
        self.last_rain = None
        loginf('driver version is %s' % DRIVER_VERSION)
        loginf('using serial port %s' % self.port)
        global DEBUG_READ
        DEBUG_READ = int(stn_dict.get('debug_read', DEBUG_READ))
        self.station = Station(self.port)
        self.station.open()

    def closePort(self):
        if self.station is not None:
            self.station.close()
            self.station = None

    @property
    def hardware_name(self):
        return "WS1"

    def genLoopPackets(self):
        while True:
            packet = {'dateTime': int(time.time() + 0.5),
                      'usUnits': weewx.US}
            readings = self.station.get_readings_with_retry(self.max_tries,
                                                            self.retry_wait)
            data = Station.parse_readings(readings)
            packet.update(data)
            self._augment_packet(packet)
            yield packet

    def _augment_packet(self, packet):
        # calculate the rain delta from rain total
        if self.last_rain is not None:
            packet['rain'] = packet['long_term_rain'] - self.last_rain
        else:
            packet['rain'] = None
        self.last_rain = packet['long_term_rain']


class Station(object):
    def __init__(self, port):
        self.port = port
        self.baudrate = 2400
        self.timeout = 3
        self.serial_port = None

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, _, value, traceback):
        self.close()

    def open(self):
        logdbg("open serial port %s" % self.port)
        self.serial_port = serial.Serial(self.port, self.baudrate,
                                         timeout=self.timeout)

    def close(self):
        if self.serial_port is not None:
            logdbg("close serial port %s" % self.port)
            self.serial_port.close()
            self.serial_port = None

    # FIXME: use either CR or LF as line terminator.  apparently some ws1
    # hardware occasionally ends a line with only CR instead of the standard
    # CR-LF, resulting in a line that is too long.
    def get_readings(self):
        buf = self.serial_port.readline()
        if DEBUG_READ:
            logdbg("bytes: '%s'" % ' '.join(["%0.2X" % ord(c) for c in buf]))
        buf = buf.strip()
        return buf

    def get_readings_with_retry(self, max_tries=5, retry_wait=10):
        for ntries in range(0, max_tries):
            try:
                buf = self.get_readings()
                Station.validate_string(buf)
                return buf
            except (serial.serialutil.SerialException, weewx.WeeWxIOError), e:
                loginf("Failed attempt %d of %d to get readings: %s" %
                       (ntries + 1, max_tries, e))
                time.sleep(retry_wait)
        else:
            msg = "Max retries (%d) exceeded for readings" % max_tries
            logerr(msg)
            raise weewx.RetriesExceeded(msg)

    @staticmethod
    def validate_string(buf):
        if len(buf) != 50:
            raise weewx.WeeWxIOError("Unexpected buffer length %d" % len(buf))
        if buf[0:2] != '!!':
            raise weewx.WeeWxIOError("Unexpected header bytes '%s'" % buf[0:2])
        return buf

    @staticmethod
    def parse_readings(raw):
        """WS1 station emits data in PeetBros format:

        http://www.peetbros.com/shop/custom.aspx?recid=29

        Each line has 50 characters - 2 header bytes and 48 data bytes:

        !!000000BE02EB000027700000023A023A0025005800000000
          SSSSXXDDTTTTLLLLPPPPttttHHHHhhhhddddmmmmRRRRWWWW

          SSSS - wind speed (0.1 kph)
          XX   - wind direction calibration
          DD   - wind direction (0-255)
          TTTT - outdoor temperature (0.1 F)
          LLLL - long term rain (0.01 in)
          PPPP - pressure (0.1 mbar)
          tttt - indoor temperature (0.1 F)
          HHHH - outdoor humidity (0.1 %)
          hhhh - indoor humidity (0.1 %)
          dddd - date (day of year)
          mmmm - time (minute of day)
          RRRR - daily rain (0.01 in)
          WWWW - one minute wind average (0.1 kph)
        """
        # FIXME: peetbros could be 40 bytes or 44 bytes, what about ws1?
        # FIXME: peetbros uses two's complement for temp, what about ws1?
        # FIXME: for ws1 is the pressure reading 'pressure' or 'barometer'?
        buf = raw[2:]
        data = dict()
        data['windSpeed'] = Station._decode(buf[0:4], 0.1 * MILE_PER_KM) # mph
        data['windDir'] = Station._decode(buf[6:8], 1.411764)  # compass deg
        data['outTemp'] = Station._decode(buf[8:12], 0.1)  # degree_F
        data['long_term_rain'] = Station._decode(buf[12:16], 0.01)  # inch
        data['pressure'] = Station._decode(buf[16:20], 0.1 * INHG_PER_MBAR)  # inHg
        data['inTemp'] = Station._decode(buf[20:24], 0.1)  # degree_F
        data['outHumidity'] = Station._decode(buf[24:28], 0.1)  # percent
        data['inHumidity'] = Station._decode(buf[28:32], 0.1)  # percent
        data['day_of_year'] = Station._decode(buf[32:36])
        data['minute_of_day'] = Station._decode(buf[36:40])
        data['daily_rain'] = Station._decode(buf[40:44], 0.01)  # inch
        data['wind_average'] = Station._decode(buf[44:48], 0.1 * MILE_PER_KM)  # mph
        return data

    @staticmethod
    def _decode(s, multiplier=None, neg=False):
        v = None
        try:
            v = int(s, 16)
            if neg:
                bits = 4 * len(s)
                if v & (1 << (bits - 1)) != 0:
                    v -= (1 << bits)
            if multiplier is not None:
                v *= multiplier
        except ValueError, e:
            if s != '----':
                logdbg("decode failed for '%s': %s" % (s, e))
        return v


class WS1ConfEditor(weewx.drivers.AbstractConfEditor):
    @property
    def default_stanza(self):
        return """
[WS1]
    # This section is for the ADS WS1 series of weather stations.

    # Serial port such as /dev/ttyS0, /dev/ttyUSB0, or /dev/cuaU0
    port = /dev/ttyUSB0

    # The driver to use:
    driver = weewx.drivers.ws1
"""

    def prompt_for_settings(self):
        print "Specify the serial port on which the station is connected, for"
        print "example /dev/ttyUSB0 or /dev/ttyS0."
        port = self._prompt('port', '/dev/ttyUSB0')
        return {'port': port}


# define a main entry point for basic testing of the station without weewx
# engine and service overhead.  invoke this as follows from the weewx root dir:
#
# PYTHONPATH=bin python bin/weewx/drivers/ws1.py

if __name__ == '__main__':
    import optparse

    usage = """%prog [options] [--help]"""

    syslog.openlog('ws1', syslog.LOG_PID | syslog.LOG_CONS)
    syslog.setlogmask(syslog.LOG_UPTO(syslog.LOG_DEBUG))
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('--version', dest='version', action='store_true',
                      help='display driver version')
    parser.add_option('--port', dest='port', metavar='PORT',
                      help='serial port to which the station is connected',
                      default=DEFAULT_PORT)
    (options, args) = parser.parse_args()

    if options.version:
        print "ADS WS1 driver version %s" % DRIVER_VERSION
        exit(0)

    with Station(options.port) as s:
        while True:
            print time.time(), s.get_readings()
