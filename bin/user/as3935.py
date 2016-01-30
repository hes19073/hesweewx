# $Id: as3935.py 1329 2015-06-18 15:20:40Z mwall $
# Copyright 2015 Matthew Wall

"""
A service for weewx that reads the AS3935 lightning sensor range.  This service
will add two fields to each archive record:

  lightning_strikes - number of lightning strikes in the pass archive interval
  avg_distance - average distance of the lightning strikes

To track these and use them in reports and plots, extend the schema as
described in the weewx customization guide.

The service can also save data to a separate 'lightning' database.  To enable
this feature, specify a data_binding in the AS3935 section of weewx.conf.

Configuration:

Rev. 1 Raspberry Pis should leave bus set at 0, while rev. 2 Pis should
set bus equal to 1. The address should be changed to match the address of
the sensor.  Common implementations are in README.md.

[AS3935]
    address = 3
    bus = 1
    noise_floor = 0
    calibration = 6
    indoors = True
    pin = 17
    data_binding = lightning_binding

[DataBindings]
    [[lightning_binding]]
        database = lightning_sqlite

[Databases]
    [[lightning_sqlite]]
        root = %(WEEWX_ROOT)s
        database_name = archive/lightning.sdb
        driver = weedb.sqlite

[Engine]
    [[Services]]
        data_services = ..., user.as3935.AS3935

Credit:

Based on Phil Fenstermacher's RaspberryPi-AS3935 library and demo.py script.
  https://github.com/pcfens/RaspberryPi-AS3935
"""

from RPi_AS3935 import RPi_AS3935
import RPi.GPIO as GPIO
import time
import syslog
import weewx
import weewx.manager
from datetime import datetime
from weewx.wxengine import StdService
from weeutil.weeutil import to_bool

VERSION = "0.2"

schema = [('dateTime', 'INTEGER NOT NULL PRIMARY KEY'),
          ('usUnits', 'INTEGER NOT NULL'),
          ('distance', 'REAL')]

def get_default_binding_dict():
    return {'database': 'lightning_sqlite',
            'manager': 'weewx.manager.Manager',
            'table_name': 'archive',
            'schema': 'user.as3935.schema'}

def logmsg(level, msg):
    syslog.syslog(level, 'as3935: %s' % msg)

def logdbg(msg):
    logmsg(syslog.LOG_DEBUG, msg)

def loginf(msg):
    logmsg(syslog.LOG_INFO, msg)

def logerr(msg):
    logmsg(syslog.LOG_ERR, msg)

class AS3935(StdService):
    def __init__(self, engine, config_dict):
        super(AS3935, self).__init__(engine, config_dict)
        loginf("service version is %s" % VERSION)
        svc_dict = config_dict.get('AS3935', {})
        addr = int(svc_dict.get('address', 0x03))
        bus = int(svc_dict.get('bus', 1))
        indoors = to_bool(svc_dict.get('indoors', True))
        noise_floor = int(svc_dict.get('noise_floor', 0))
        calib = int(svc_dict.get('calibration', 0x6))
        pin = int(svc_dict.get('pin', 17))
        self.binding = svc_dict.get('data_binding', None)

        self.data = []

        # if a binding was specified, then use it to save strikes to database
        if self.binding is not None:
            # configure the lightning database
            dbm_dict = weewx.manager.get_manager_dict(
                config_dict['DataBindings'], config_dict['Databases'],
                self.binding, default_binding_dict=get_default_binding_dict())
            with weewx.manager.open_manager(dbm_dict, initialize=True) as dbm:
                # ensure schema on disk matches schema in memory
                dbcol = dbm.connection.columnsOf(dbm.table_name)
                memcol = [x[0] for x in dbm_dict['schema']]
                if dbcol != memcol:
                    raise Exception('as3935: schema mismatch: %s != %s' %
                                    (dbcol, memcol))

        # configure the gpio and sensor
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.IN)
        self.sensor = RPi_AS3935(address=addr, bus=bus)
        self.sensor.set_indoors(indoors)
        self.sensor.set_noise_floor(noise_floor)
        self.sensor.calibrate(tun_cap=calib)

        # add a gpio callback for the lightning strikes
        GPIO.add_event_detect(pin, GPIO.RISING, callback=self.handle_interrupt)
        # on each new archive record, read then clear data since last record
        self.bind(weewx.NEW_ARCHIVE_RECORD, self.read_data)
   
    def read_data(self, event):
        avg = None
        count = len(self.data)
        if count:
            avg = 0
            for x in self.data:
                avg += x[1]
            avg /= count
        self.data = []
        event.record['lightning_strikes'] = count
        event.record['avg_distance'] = avg

    def save_data(self, strike_ts, distance):
        if self.binding is None:
            return
        rec = {'dateTime': strike_ts,
               'usUnits': weewx.METRIC,
               'distance': distance}
        dbm_dict = weewx.manager.get_manager_dict(
            self.config_dict['DataBindings'], self.config_dict['Databases'],
            self.binding, default_binding_dict=get_default_binding_dict())
        with weewx.manager.open_manager(dbm_dict) as dbm:
            dbm.addRecord(rec)

    def handle_interrupt(self, channel):
        try:   
            time.sleep(0.003)
            reason = self.sensor.get_interrupt()
            if reason == 0x01:
                loginf("noise level too high - adjusting")  
                self.sensor.raise_noise_floor()
            elif reason == 0x04:
                loginf("detected disturber - masking")
                self.sensor.set_mask_disturber(True)
            elif reason == 0x08:
                strike_ts = int(time.time())
                distance = float(self.sensor.get_distance())
                loginf("strike at %s km" % distance)
                self.data.append((strike_ts, distance))
                self.save_data(strike_ts, distance)
        except Exception, e:
            logerr("callback failed: %s" % e)
