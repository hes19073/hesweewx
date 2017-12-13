#!/usr/bin/env python
# coding=utf-8
"""weewx module that records air sensor

Installation

Put this file in the bin/user directory.

"""

from __future__ import with_statement

import os
import platform
import re
import syslog
import time
import math
import grovepi
import grovepi6
import smbus
import RPi.GPIO as GPIO
import weewx
import weeutil.weeutil
from weewx.engine import StdService
from grove_i2c_barometic_sensor_BMP180 import BMP085
from grove_i2c_digital_light_sensor import Tsl2561

VERSION = "0.4"

if weewx.__version__ < "3":
    raise weewx.UnsupportedFeature("weewx 3 is required, found %s" %
                                   weewx.__version__)
schema = [
    ('dateTime', 'INTEGER NOT NULL PRIMARY KEY'),
    ('usUnits', 'INTEGER NOT NULL'),
    ('interval', 'INTEGER NOT NULL'),
    ('air_sensor','INTEGER'),
    ('gas_sensor','INTEGER'),
    ('hcho_sensor','INTEGER'),
    ('water_sensor','INTEGER'),
    ('light_sensor','INTEGER'),
    ('uv_sensor','INTEGER'),
    ('gasC_sensor','INTEGER'),
    ('gasO_sensor','INTEGER'),
    ('gasN_sensor','INTEGER'),
    ('gasx_sensor','INTEGER'),
    ('lightD_sensor','INTEGER'),
    ('dust_sensor','INTEGER'),
    ('lightIn_sensor','INTEGER'),
    ('adc_sensor','INTEGER'),
    ('temp','REAL'),
    ('pressure','REAL'),
    ('altitude','REAL'),
    ('barometer', 'REAL'),
    ('sound','REAL'),
    ('inTemp','REAL'),
    ('inHumidity','REAL'),
    ]

def logmsg(level, msg):
    syslog.syslog(level, 'air: %s' % msg)

def logdbg(msg):
    logmsg(syslog.LOG_DEBUG, msg)

def loginf(msg):
    logmsg(syslog.LOG_INFO, msg)

def logerr(msg):
    logmsg(syslog.LOG_ERR, msg)


class AirMonitor(StdService):
    """Collect Sensor Air information."""

    def __init__(self, engine, config_dict):
        super(AirMonitor, self).__init__(engine, config_dict)
        loginf("service version is %s" % VERSION)

        d = config_dict.get('AirMonitor', {})
        self.hardware = d.get('hardware', [None])
        if not isinstance(self.hardware, list):
            self.hardware = [self.hardware]

        # get the database parameters we need to function
        binding = d.get('data_binding', 'air_binding')
        self.dbm = self.engine.db_binder.get_manager(data_binding=binding,
                                                     initialize=True)

        # be sure schema in database matches the schema we have
        dbcol = self.dbm.connection.columnsOf(self.dbm.table_name)
        dbm_dict = weewx.manager.get_manager_dict(
            config_dict['DataBindings'], config_dict['Databases'], binding)
        memcol = [x[0] for x in dbm_dict['schema']]
        if dbcol != memcol:
            raise Exception('air schema mismatch: %s != %s' % (dbcol, memcol))

        # see what we are running on
        self.system = platform.system()

        # provide info about the system on which we are running
        loginf('Air sysinfo: %s' % ' '.join(os.uname()))
        loginf('AirMonitor')

        self.last_ts = None
        self.bind(weewx.NEW_ARCHIVE_RECORD, self.new_archive_record)

    def shutDown(self):
        try:
            self.dbm.close()
        except:
            pass

    def new_archive_record(self, event):
        """save data to database then prune old records as needed"""
        now = int(time.time() + 0.5)
        delta = now - event.record['dateTime']
        if delta > event.record['interval'] * 60:
            logdbg("Skipping record: time difference %s too big" % delta)
            return

        if self.last_ts is not None:
            self.save_data(self.get_data(now, self.last_ts))

        self.last_ts = now

    def save_data(self, record):
        """save data to database"""
        self.dbm.addRecord(record)

    def prune_data(self, ts):
        """delete records with dateTime older than ts"""
        sql = "delete from %s where dateTime < %d" % (self.dbm.table_name, ts)
        self.dbm.getSql(sql)
        try:
            # sqlite databases need some help to stay small
            self.dbm.getSql('vacuum')
        except Exception, e:
            pass

    def get_data(self, now_ts, last_ts):
        record = {}
        record['dateTime'] = now_ts                       # required
        record['usUnits'] = weewx.METRIC                  # required
        record['interval'] = int((now_ts - last_ts) / 60) # required
        if self.system == 'Linux':
            record.update(self._get_linux_info())
        else:
            logerr('unsupported system %s' % self.system)

        return record

    # this should work on any linux running kernel 2.2 or later
    def _get_linux_info(self):

        rev = GPIO.RPI_REVISION
        if rev == 2 or rev == 3:
            bus = smbus.SMBus(1)
        else:
            bus = smbus.SMBus(0)

        record = {}

        air_sen = 0
        gas_sen = 1
        hcho_sen = 2
        light_sen = 0
        water_sen = 3
        sound_sensor = 2
        senC = 1
        grovepi.pinMode(air_sen, "INPUT")
        grovepi.pinMode(gas_sen, "INPUT")
        grovepi.pinMode(hcho_sen, "INPUT")
        grovepi.pinMode(water_sen, "INPUT")
        #grovepi6.pinMode(light_sen, "INPUT")
        #grovepi6.pinMode(senC, "INPUT")
        #grovepi6.pinMode(sound_sensor, "INPUT")
        #grovepi.pinMode(i2c-2, "INPUT")

        bmp = BMP085(0x77, 1)

        tempaaaa = bmp.readTemperature()
        pressure = bmp.readPressure()
        altitude = bmp.readAltitude(101560)
        sensor = 4
        blue = 1

        #record = {}

        try:

            #record = {}

            loginf("START BYTE GOOD")
            temp = bmp.readTemperature()
            pressure = bmp.readPressure()
            altitude = bmp.readAltitude(101560)

            [temp1,humidity] = grovepi.dht(sensor,blue)  

            watsen = grovepi.digitalRead(water_sen)

            if watsen == 1:
                 watwert = 100
            else:
                 watwert = 0

            record['air_sensor'] = grovepi.analogRead(air_sen)
            record['gas_sensor'] = grovepi.analogRead(gas_sen)
            record['hcho_sensor'] = grovepi.analogRead(hcho_sen)
            #record['light_sensor'] = senorli
            record['water_sensor'] = watwert
            record['inTemp'] = temp1
            record['inHumidity'] = humidity
            #record['sound'] = grovepi6.analogRead(sound_sensor)
            #record['gasC_sensor'] = grovepi6.analogRead(senC)
            record['pressure'] = pressure / 100.0
            record['temp'] = tempaaaa
            record['altitude'] = altitude
            #record['hcho_sensor'] = hcho_se
            #record['gasN_sensor'] = grovepi.analogRead(gas_sen)
            #record['gasO_sensor'] = grovepi.read_i2c_byte(0x29)
            #record['lightD_sensor'] = liDig

            loginf("END BYTE GOOD")

            #uvi = grovepi5.analogRead(0)
            #record['uv_sensor'] = uvi * 307 / 2000

        except IOError:
             print "Error"

        return record

