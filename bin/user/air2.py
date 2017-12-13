#!/usr/bin/python
# coding=utf-8

from __future__ import print_function
import serial, struct, sys
import os
import platform
import re
import syslog
import time
import weewx
import weeutil.weeutil
from weewx.engine import StdService

VERSION = "0.1"

if weewx.__version__ < "3":
    raise weewx.UnsupportedFeature("weewx 3 is required, found %s" %
                                   weewx.__version__)
schema = [
    ('dateTime', 'INTEGER NOT NULL PRIMARY KEY'),
    ('usUnits', 'INTEGER NOT NULL'),
    ('interval', 'INTEGER NOT NULL'),
    ('pm_25','INTEGER'),
    ('pm_10','INTEGER'),
    ]

def logmsg(level, msg):
    syslog.syslog(level, 'air2: %s' % msg)

def logdbg(msg):
    logmsg(syslog.LOG_DEBUG, msg)

def loginf(msg):
    logmsg(syslog.LOG_INFO, msg)

def logerr(msg):
    logmsg(syslog.LOG_ERR, msg)

def bytes2int(bytes):
    return struct.unpack("B", bytes)[0]

class Air2Monitor(StdService):
    """Collect Sensor Air information."""

    def __init__(self, engine, config_dict):
        super(Air2Monitor, self).__init__(engine, config_dict)
        loginf("service version is %s" % VERSION)

        d = config_dict.get('Air2Monitor', {})
        #self.hardware = d.get('hardware', [None])
        #if not isinstance(self.hardware, list):
        #    self.hardware = [self.hardware]
        #self.max_age = weeutil.weeutil.to_int(d.get('max_age', 2592000))

        # get the database parameters we need to function
        binding = d.get('data_binding', 'air2_binding')
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
        #self.system = platform.system()

        # provide info about the system on which we are running
        #loginf('sysinfo: %s' % ' '.join(os.uname()))

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
        #if self.max_age is not None:
        #    self.prune_data(now - self.max_age)

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

        record.update(self._get_linux_info())

        return record

    # this should work on any linux running kernel 2.2 or later
    def _get_linux_info(self):

        try:

            record = {}
 
            ser = serial.Serial()
            ser.port = "/dev/serial/by-id/usb-1a86_USB2.0-Serial-if00-port0"
            ser.baudrate = 9600
            pm25 = 0
            pm10 = 0
            ser.open()
            ser.flushInput()

            read_full = False
            data = []
            loginf("Serial device initialized")
            while not read_full:
                if ser.read() == b'\xaa':
                    loginf("First")
                    if ser.read() == b'\xc0':
                        loginf("SECOND HEADER GOOD")
                        for i in range(8):
                            byte = ser.read()
                            data.append(bytes2int(byte))

                        if data[-1] == 171:
                            # END BYTE IS GOOD. DO CRC AND CALCULATE
                            loginf("END BYTE GOOD")
                            if data[6] == sum(data[0:6])%256:
                                loginf("CRC GOOD")
                            pm25 = (data[0]+data[1]*256)/10
                            pm10 = (data[4]+data[3]*256)/10
                            read_full = True


            ser.close()
            record['pm_25'] = pm25
            record['pm_10'] = pm10

            return record

        except serial.SerialException as e:
            loginf.critical(e)

