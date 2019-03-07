#!/usr/bin/env python
# -*- coding: utf-8 -*-
# rfxcom driver for weewx
#
# Copyright 2016 Matthew Wall, Luc Heijst
#
# See http://www.gnu.org/licenses/
"""rfxcom is a USB device that receives radio transmissions from sensors
weather.
"""

# FIXME: eliminate the service component - there is no need to bind to events

import serial
import syslog
import time
from _struct import unpack

import weewx.drivers
import weewx.engine


DRIVER_NAME = 'rfxcom'
DRIVER_VERSION = '0.1'

DEBUG_SERIAL = 0
DEBUG_RAIN = 0
DEBUG_PARSE = 0
DEBUG_RFS = 0

def loader(config_dict, engine):
    return rfxcomDriver(engine, config_dict)

def confeditor_loader():
    return rfxcomConfEditor()

def configurator_loader(config_dict):
    return rfxcomConfigurator()

def logmsg(level, msg):
    syslog.syslog(level, 'rfxcom: %s' % msg)

def logdbg(msg):
    logmsg(syslog.LOG_DEBUG, msg)

def loginf(msg):
    logmsg(syslog.LOG_INFO, msg)

def logerr(msg):
    logmsg(syslog.LOG_ERR, msg)


def dbg_serial(verbosity, msg):
    if DEBUG_SERIAL >= verbosity:
        logdbg(msg)

def dbg_parse(verbosity, msg):
    if DEBUG_PARSE >= verbosity:
        logdbg(msg)


class rfxcomDriver(weewx.drivers.AbstractDevice):

    def __init__(self, engine, config_dict):
        loginf('driver version is %s' % DRIVER_VERSION)
        self.whitelist = [
            82, # TemperatureHumidity
            85, # Rain
            86, # Wind
            87, # UV
        ]
        stn_dict = config_dict.get(DRIVER_NAME, {})
        global DEBUG_PARSE
        DEBUG_PARSE = int(stn_dict.get('debug_parse', DEBUG_PARSE))
        global DEBUG_SERIAL
        DEBUG_SERIAL = int(stn_dict.get('debug_serial', DEBUG_SERIAL))
        global DEBUG_RAIN
        DEBUG_RAIN = int(stn_dict.get('debug_rain', DEBUG_RAIN))
        self.sensor_map = stn_dict.get('sensor_map', {})
        loginf('sensor map is: %s' % self.sensor_map)
        self.last_rain_count = None
        self.station = rfxcom(**stn_dict)
        self.station.open()

    def closePort(self):
        if self.station is not None:
            self.station.close()
            self.station = None

    @property
    def hardware_name(self):
        return 'rfxcom'

    def genLoopPackets(self):
        while True:
            while True:
                size=self.station.get_readings(1)
                if len(size) == 1:
                    break
            size = int(size.encode('hex'), 16)
            if size == 0:
                continue
            readings = self.station.get_readings(size)
            stype = ord(readings[0])
            logdbg(stype)
            subtype = ord(readings[1])
            data = readings[3:]
            if stype == 82:
                result = self.station.processTempHumid(data)
            elif stype == 85:
                result = self.station.processRain(data)
            elif stype == 86:
                result = self.station.processWind(subtype, data)
            elif stype == 87:
                result = self.station.processUV(subtype, data)
            else:
                logdbg("Warning: Type %d is unsupported" % stype)
            if stype == 82 or stype == 85 or stype == 86 or stype == 87:
                logdbg(result)
                yield result
            
class rfxcom(object):
    DEFAULT_PORT = '/dev/ttyUSB0'
    DEFAULT_BAUDRATE = 38400
    DEFAULT_PARITY = serial.PARITY_NONE
    DEFAULT_STOPBITS = serial.STOPBITS_ONE
    DEFAULT_BYTESIZE = serial.EIGHTBITS
    
    def __init__(self, **cfg):
        self.port = cfg.get('port', self.DEFAULT_PORT)
        loginf('using serial port %s' % self.port)

        self.baudrate = cfg.get('baudrate', self.DEFAULT_BAUDRATE)
        loginf('using baudrate %s' % self.baudrate)
        
        self.parity = cfg.get('parity', self.DEFAULT_PARITY)
        loginf('using parity %s' % self.parity)
        
        self.stopbits = cfg.get('stopbits', self.DEFAULT_STOPBITS)
        loginf('using stopbits %s' % self.stopbits)
        
        self.bytesize = cfg.get('bytesize', self.DEFAULT_BYTESIZE)
        loginf('using bytesize %s' % self.bytesize)

        self.timeout = 1 # seconds
        self.serial_port = None

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, _, value, traceback):
        self.close()

    def open(self):
        dbg_serial(1, "open serial port %s" % self.port)
        self.serial_port = serial.Serial(self.port,
                                        self.baudrate, 
                                        parity=self.parity,
                                        stopbits=self.stopbits,
                                        bytesize=self.bytesize,
                                        timeout=self.timeout)

    def close(self):
        if self.serial_port is not None:
            dbg_serial(1, "close serial port %s" % self.port)
            self.serial_port.close()
            self.serial_port = None
            
    def get_readings(self,data):
        buf = self.serial_port.read(data)
        return buf            

    def get_readings_with_conversion(self):
        buf = self.serial_port.read(1)
        if len(buf) != 1:
            buf = int(buf.encode('hex'), 16)
        buf = self.serial_port.read(buf)
        return buf

    def processTempHumid(self, data):
        # ID_hi, ID_lo, Time, Temperature, Humidity, Flags, Battery & Signal
        (ID_hi, ID_lo, temp_hi, temp_lo, humidity, sigbat) = unpack(">BBBBBxB", data)

        packet = dict()
        packet['dateTime'] = int(time.time())
        packet['usUnits'] = weewx.METRIC
        name = "TempHumid"
        hardware_id =  str('%02d' % int((hex(ID_hi))[2:])) + str('%02d' % int((hex(ID_lo))[2:]))
        temp = ((temp_hi & 0x7F) << 8 | temp_lo) / 10.0
        if temp_hi & 0x80:
            temp = -temp
        packet['temperature'] = temp
        packet['humidity'] = humidity    
        packet['signal'] = (sigbat >> 4 & 0x0f)
        packet['battery'] = (sigbat & 0x0f)

        return self.add_identifiers(packet, hardware_id, name)
    
    def processRain(self, data):
        # ID_hi, ID_lo, Time, Temperature, Humidity, Flags, Battery & Signal
        (ID_hi, ID_lo, rate_hi, rate_lo, total_hi, total_mi, total_lo, sigbat) = unpack(">BBBBBBBB", data)
    
        packet = dict()
        packet['dateTime'] = int(time.time())
        packet['usUnits'] = weewx.METRIC
        packet_type ="Rain"
        sensor_id =  str('%02d' % int((hex(ID_hi))[2:])) + str('%02d' % int((hex(ID_lo))[2:]))
        packet['rate'] = (rate_hi << 8 | rate_lo) / 100.0
        packet['rain_total'] = (total_hi << 16 | total_mi << 8 | total_lo) / 10.0
        packet['signal'] = (sigbat >> 4 & 0x0f)
        packet['battery'] =(sigbat & 0x0f)

        return self.add_identifiers(packet, sensor_id, packet_type) 

    def processUV(self, subtype, data):
        # ID_hi, ID_lo, Time, UV, Extratemp, Battery & Signal
        (ID_hi, ID_lo, temp_hi, temp_lo, uv, sigbat) = unpack(">BBBBBB", data)

        packet = dict()
        packet['dateTime'] = int(time.time())
        packet['usUnits'] = weewx.METRIC
        packet_type = "UV"
        sensor_id =  str('%02d' % int((hex(ID_hi))[2:])) + str('%02d' % int((hex(ID_lo))[2:]))
        temp = ((temp_hi & 0x7F) << 8 | temp_lo) / 10.0
        if temp_hi & 0x80:
            temp = -temp
        packet['temperature'] = temp
        packet['uv'] = uv
        packet['signal'] = (sigbat >> 4 & 0x0f)
        packet['battery'] =(sigbat & 0x0f)
        if subtype == 3:
            packet['Extratemp'] = ", %.1fC" % temp
        else:
            packet['Extratemp'] = ""
        
        return self.add_identifiers(packet, sensor_id, packet_type)
    
    def processWind(self, subtype, data):
        # ID_hi, ID_lo, Time, Direction, Average Speed, Speed, Battery & Signal
        (ID_hi, ID_lo, wind_hi, wind_lo, avg_hi, avg_lo, speed_hi, speed_lo, temp_hi, temp_lo, chill_hi, chill_lo, sigbat) = unpack(">BBBBBBBBBBBBB", data)

        packet = dict()
        packet['dateTime'] = int(time.time())
        packet['usUnits'] = weewx.METRIC
        packet_type = "Wind"
        sensor_id =  str('%02d' % int((hex(ID_hi))[2:])) + str('%02d' % int((hex(ID_lo))[2:]))
        packet['wind'] = wind_hi << 8 | wind_lo
        packet['average'] = (avg_hi << 8 | avg_lo) / 10
        packet['speed'] = (speed_hi << 8 | speed_lo) / 10
        temp = ((temp_hi & 0x7F) << 8 | temp_lo) / 10.0
        if temp_hi & 0x80:
            temp = -temp
        packet['temperature'] = temp
        chill = ((chill_hi & 0x7F) << 8 | chill_lo) / 10.0
        if chill_hi & 0x80:
            chill = -chill
        packet['chill'] = chill
        packet['signal'] = (sigbat >> 4 & 0x0f)
        packet['battery'] =(sigbat & 0x0f)
        if subtype == 4:
            packet['Extratemp'] = " %.1fC" % temp
            packet['Extrachill'] = " %.1fCF" % chill
        else:
            packet['Extratemp'] = ""
            packet['Extrachill'] = ""
            
        return self.add_identifiers(packet, sensor_id, packet_type)

    @staticmethod
    def add_identifiers(pkt, sensor_id='', packet_type=''):
        # qualify each field name with details about the sensor.  not every
        # sensor has all three fields.
        # observation.<sensor_id>.<packet_type>
        packet = dict()
        if 'dateTime' in pkt:
            packet['dateTime'] = pkt.pop('dateTime', 0)
        if 'usUnits' in pkt:
            packet['usUnits'] = pkt.pop('usUnits', 0)
        for n in pkt:
            packet["%s.%s.%s" % (n, sensor_id, packet_type)] = pkt[n]
        return packet   


class rfxcomConfEditor(weewx.drivers.AbstractConfEditor):
    @property
    def default_stanza(self):
        return """
[rfxcom]
    # This section is for the rfxcom USB receiver.
    # The serial port to which the meteostick is attached, e.g., /dev/ttyS0
    port = /dev/ttyUSB0
    # The driver to use
    driver = user.rfxcom
"""

    def prompt_for_settings(self):
        settings = dict()
        print "Specify the serial port on which the rfxcom is connected,"
        print "for example /dev/ttyUSB0 or /dev/ttyS0"
        settings['port'] = self._prompt('port', rfxcom.DEFAULT_PORT)
        return settings


class rfxcomConfigurator(weewx.drivers.AbstractConfigurator):
    def add_options(self, parser):
        super(rfxcomConfigurator, self).add_options(parser)
        parser.add_option(
            "--info", dest="info", action="store_true",
            help="display rfxcom configuration")
        parser.add_option(
            "--show-options", dest="opts", action="store_true",
            help="display rfxcom command options")
        parser.add_option(
            "--set-verbose", dest="verbose", metavar="X", type=int,
            help="set verbose: 0=off, 1=on; default off")
        parser.add_option(
            "--set-debug", dest="debug", metavar="X", type=int,
            help="set debug: 0=off, 1=on; default off")
        # bug in meteostick: according to docs, 0=high, 1=low

    def do_options(self, options, parser, config_dict, prompt):
        driver = rfxcomDriver(None, config_dict)
        info = driver.station.reset()
        if options.info:
            print info
        cfg = {
            'd': options.debug,
            'v': options.verbose}
        for opt in cfg:
            if cfg[opt]:
                cmd = opt + cfg[opt]
                print "set station parameter %s" % cmd
                driver.station.send_command(cmd)
        if options.opts:
            driver.station.send_command('?')
            print driver.station.get()
        driver.closePort()


# define a main entry point for basic testing of the station without weewx
# engine and service overhead.  invoke this as follows from the weewx root dir:
#
# PYTHONPATH=bin python bin/user/rfxcom.py

if __name__ == '__main__':
    import optparse

    usage = """%prog [options] [--help]"""

    syslog.openlog('rfxcom', syslog.LOG_PID | syslog.LOG_CONS)
    syslog.setlogmask(syslog.LOG_UPTO(syslog.LOG_DEBUG))
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('--version', dest='version', action='store_true',
                      help='display driver version')
    parser.add_option('--port', dest='port', metavar='PORT',
                      help='serial port to which the station is connected',
                      default=rfxcom.DEFAULT_PORT)
    parser.add_option('--baudrate', dest='baudrate', metavar='BAUDRATE',
                      help='serial port baudrate',
                      default=rfxcom.DEFAULT_BAUDRATE)
    parser.add_option('--parity', dest='parity', metavar='PARITY',
                      help='serial port parity',
                      default=rfxcom.DEFAULT_PARITY)
    parser.add_option('--stopbits', dest='stopbits', metavar='STOPBITS',
                      help='serial port stopbits',
                      default=rfxcom.DEFAULT_STOPBITS)
    parser.add_option('--bytesize', dest='bytesize', metavar='BYTESIZE',
                      help='serial port bytesize',
                      default=rfxcom.DEFAULT_BYTESIZE)
    (opts, args) = parser.parse_args()

    if opts.version:
        print "rfxcom driver version %s" % DRIVER_VERSION
        exit(0)

    with rfxcom(port = opts.port,
                baudrate = opts.baudrate,
                parity = opts.parity,
                stopbits = opts.stopbits,
                bytesize = opts.bytesize) as s:
        while True:
            print time.time(), s.get_readings()


