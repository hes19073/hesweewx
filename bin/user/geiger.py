# coding=utf-8

"""weewx module that records cpm and nSvh from GMC 300.

Put this file in the bin/user directory.

Service Configuration

Add the following to weewx.conf:

[GeigerMonitor]
    data_binding = geiger_binding

[DataBindings]
    [[geiger_binding]]
        database = geiger_sqlite
        manager = weewx.manager.DaySummaryManager
        table_name = archive
        schema = user.geiger.schema

[Databases]
    [[geiger_sqlite]]
        database_name = archive/weewxGeiger.sdb
        driver = weedb.sqlite

[Engine]
    [[Services]]
        archive_services = ..., user.geiger.GeigerMonitor

"""

from __future__ import absolute_import
from __future__ import print_function

import logging
import serial, struct, sys
import os
import platform
import re

import time
import weewx
import weeutil.weeutil
from weewx.engine import StdService

log = logging.getLogger(__name__)

VERSION = "0.2"

if weewx.__version__ < "3":
    raise weewx.UnsupportedFeature("weewx 3 is required, found %s" %
                                   weewx.__version__)
schema = [
    ('dateTime', 'INTEGER NOT NULL PRIMARY KEY'),
    ('usUnits', 'INTEGER NOT NULL'),
    ('interval', 'INTEGER NOT NULL'),
    ('rad_cpm','INTEGER'),
    ('rad_nsvh','INTEGER'),
    ]


def getCPM(ser):
    ser.write(b'<GETCPM>>')
    rec = ser.read(2)
    return ord(rec[0])<< 8 | ord(rec[1])

class GeigerMonitor(StdService):
    """Collect Sensor Air information."""

    def __init__(self, engine, config_dict):
        super(GeigerMonitor, self).__init__(engine, config_dict)
        log.info("Geiger-Service version is %s", VERSION)

        d = config_dict.get('Geiger', {})
        # get PORT and BAUD of Geiger
        self._port = d.get('port', '/dev/ttyUSB1')
        # self._port = d.get('port', '/dev/geiger')
        self._baud = weeutil.weeutil.to_int(d.get('baud', 9600))

        # get the database parameters we need to function
        binding = d.get('data_binding', 'geiger_binding')
        self.dbm = self.engine.db_binder.get_manager(data_binding=binding,
                                                     initialize=True)

        # be sure schema in database matches the schema we have
        dbcol = self.dbm.connection.columnsOf(self.dbm.table_name)
        dbm_dict = weewx.manager.get_manager_dict(
            config_dict['DataBindings'], config_dict['Databases'], binding)
        memcol = [x[0] for x in dbm_dict['schema']]
        if dbcol != memcol:
            raise Exception('Geiger schema mismatch: %s != %s' % (dbcol, memcol))

        # provide info about the system on which we are running
        log.info('Geiger-sysinfo PORT: %s ', self._port)
        log.info('Geiger-sysinfo baud: %s ', self._baud)

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
            log.debug("Skipping record: time difference %s too big", delta)
            return
        if self.last_ts is not None:
            self.save_data(self.get_data(now, self.last_ts))
        self.last_ts = now

    def save_data(self, record):
        """save data to database"""
        self.dbm.addRecord(record)

    def get_data(self, now_ts, last_ts):
        record = {}
        record['dateTime'] = now_ts
        record['usUnits'] = weewx.METRIC
        record['interval'] = int((now_ts - last_ts) / 60)


        try:
            ser = serial.Serial()
            ser.port = "/dev/ttyUSB1"
            # ser.port = "/dev/geiger"
            ser.baudrate = 9600
            rad_cpm = 0

            ser.open()
            ser.flushInput()

            read_full = False
            #loginf("Serial device initialized for Geiger")

            while not read_full:
                #cpm = getCPM(ser)
                ser.write(b'<GETCPM>>')
                rec = ser.read(2)
                #cpm = ord((rec[0])<< 8 | ord(rec[1])
                cpm = ((rec[0] & 0x3f) << 8 | rec[1])

                rad_cpm = cpm

                read_full = True


            ser.close()

        except serial.SerialException as e:
            log.info("critical", e)

        record['rad_cpm'] = rad_cpm
        record['rad_nsvh'] = rad_cpm * 6.5

        return record
