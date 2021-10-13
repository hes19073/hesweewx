#!/usr/bin/python3
#
# WeeWX service to read data from the airQ device
#
# Copyright (C) 2021 Johanna Roedenbeck
# airQ API Copyright (C) Corant GmbH
#
# version for database by Hartmut Schweidler
# August 2021

"""

Hardware: https://www.air-q.com

Science option is required.

Most of the the observation types provided by the airQ device are
predefined within WeeWX. If no special configuration besides host
address and password is provided the measured values are stored to
those observation types.

More than one device can be used. That is done by configurating a
specific prefix for the observation types of each device.

Configuration in weewx.conf:

[airQ]

    # query_interval = 5.0 # optional, default 5.0 seconds
    host = replace_me_by_host_address_or_IP
    password = replace_me
    data_binding = airq_binding


"""

VERSION = 0.8

# imports for airQ
import base64
from Cryptodome.Cipher import AES
import http.client
import json

# deal with differences between python 2 and python 3
try:
    # Python 3
    import queue
except ImportError:
    # Python 2
    # noinspection PyUnresolvedReferences
    import Queue as queue

# imports for WeeW
import six
# import threading
import time
if __name__ != '__main__':
    # for use as service within WeeWX
    import weewx
    from weewx.engine import StdService
    import weewx.units
    import weewx.accum
    import weeutil.weeutil
    from weewx.wxformulas import altimeter_pressure_Metric,sealevel_pressure_Metric
else:
    # for standalone testing
    import sys
    import collections
    sys.path.append('../../test')
    from testpasswd import airqIP,airqpass
    class StdService(object):
        def __init__(self, engine, config_dict):
            pass
        def bind(self,p1,p2):
            pass
    class weewx(object):
        NEW_LOOP_PACKET = 1
        class units(object):
            def convertStd(p1, p2):
                return p1
            def convert(p1, p2):
                return (p1[0],p2,p1[2])
            obs_group_dict = collections.ChainMap()
            conversionDict = collections.ChainMap()
            default_unit_format_dict = collections.ChainMap()
            default_unit_label_dict = collections.ChainMap()
        class accum(object):
            accum_dict = collections.ChainMap()
    class weeutil(object):
        class weeutil(object):
            def to_int(x):
                return int(x)
    class Event(object):
        packet = { 'usUnits':16 }
    class Engine(object):
        class stn_info(object):
            altitude_vt = (0,'meter','group_altitude')


try:
    # Test for new-style weewx logging by trying to import weeutil.logger
    import weeutil.logger
    import logging
    log = logging.getLogger("user.airQ")

    def logdbg(msg):
        log.debug(msg)

    def loginf(msg):
        log.info(msg)

    def logerr(msg):
        log.error(msg)

except ImportError:
    # Old-style weewx logging
    import syslog

    def logmsg(level, msg):
        syslog.syslog(level, 'user.airQ: %s' % msg)

    def logdbg(msg):
        logmsg(syslog.LOG_DEBUG, msg)

    def loginf(msg):
        logmsg(syslog.LOG_INFO, msg)

    def logerr(msg):
        logmsg(syslog.LOG_ERR, msg)


ACCUM_LAST_DICT = { 'accumulator':'firstlast','extractor':'last' }

##############################################################################
#   get data out of the airQ device                                          #
##############################################################################

def airQreply(htmlreply, passwd):
    """ convert the reply to json """
    # the reply is a json string
    _rtn = json.loads(htmlreply)
    # 'content' is base64 encoded and encrypted data
    if 'content' in _rtn:
        # convert base64 to plain text
        _crtxt = base64.b64decode(_rtn['content'])
        # convert passwd to bytes
        _aeskey = passwd.encode('utf-8')
        # adjust to 32 bytes of length
        _aeskey = _aeskey.ljust(32,b'0')
        # decode AES256
        _cipher = AES.new(key=_aeskey, mode=AES.MODE_CBC, IV=_crtxt[:16])
        _txt = _cipher.decrypt(_crtxt[16:]).decode('utf-8')
        _rtn['content'] =  json.loads(_txt[:-ord(_txt[-1])])
    # reply converted to python dict with 'content' decoded
    return _rtn

def airQget(host, page, passwd):
    """ get page from airQ """
    try:
        connection = http.client.HTTPConnection(host)
        connection.request('GET', page)
        _response = connection.getresponse()
        if _response.status==200:
            # successful --> get response
            reply = airQreply(_response.read(), passwd)
        else:
            # HTML error
            reply = {'content':{}}
        reply['replystatus'] = _response.status
        reply['replyreason'] = _response.reason
        reply['replyexception'] = ""
    except http.client.HTTPException as e:
        reply = {
            'replystatus': 503,
            'replyreason': "HTTPException %s" % e,
            'replyexception': "HTTPException",
            'content': {}}
    except OSError as e:
        # device not found
        # connection reset
        if e.__class__.__name__ in ['ConnectionError','ConnectionResetError','ConnectionAbortedError','ConnectionRefusedError']:
            __status = 503
        else:
            __status = 404
        reply = {
            'replystatus': __status,
            'replyreason': "OSError %s - %s" % (e.__class__.__name__,e),
            'replyexception': e.__class__.__name__,
            'content': {}}
    finally:
        connection.close()

    # airq_dat = open("/home/weewx/archive/airq_data.json", "w")
    # wert = json.dumps(reply)
    # airq_dat.write(wert)
    # airq_dat.close()
    # loginf("DATA: %s" % reply)
    return reply

##############################################################################
#   data_services: augment LOOP packet with airQ readings                    #
##############################################################################

class AirqService(StdService):

    # observation types
    AIRQ_DATA = {
        'DeviceID':    ('airqDeviceID',    None,None,lambda x: x),
        'Status':      ('airqStatus',      None,None,lambda x: x),
        'timestamp':   None,
        'measuretime': ('airqMeasuretime', None, None, lambda x: int(x)),
        'uptime':      ('airqUptime',      None, None, lambda x: int(x)),
        'temperature': ('airqTemp',        'degree_C',                  'group_temperature',   lambda x: float(x[0])),
        'humidity':    ('airqHumidity',    'percent',                   'group_percent',       lambda x: x[0]),
        'humidity_abs':('airqHumAbs',      'gram_per_meter_cubed',      'group_gram',          lambda x: float(x[0])),
        'dewpt':       ('airqDewpoint',    'degree_C',                  'group_temperature',   lambda x: float(x[0])),
        'pressure':    ('airqPressure',    'mbar',                      'group_pressure',      lambda x: float(x[0])),
        'altimeter':   ('airqAltimeter',   'mbar',                      'group_pressure',      lambda x: float(x[0])),
        'barometer':   ('airqBarometer',   'mbar',                      'group_pressure',      lambda x: float(x[0])),
        'co':          ('airqco_m',        'milligram_per_meter_cubed', 'group_concentration', lambda x: x[0]),
        'co_vol':      ('co',              'ppm',                       'group_fraction',      lambda x: x),
        'co2':         ('co2',             'ppm',                       'group_fraction',      lambda x: x[0]),
        'h2s':         ('h2s',             "microgram_per_meter_cubed", "group_concentration", lambda x: x[0]),
        'no2':         ('no2_m',           "microgram_per_meter_cubed", "group_concentration", lambda x: x[0]),
        'no2_vol':     ('no2',             'ppb',                       'group_fraction',      lambda x: x[0]),
        'pm1':         ('pm1_0',           "microgram_per_meter_cubed", "group_concentration", lambda x: x[0]),
        'pm2_5':       ('pm2_5',           "microgram_per_meter_cubed", "group_concentration", lambda x: x[0]),
        'pm10':        ('pm10_0',          "microgram_per_meter_cubed", "group_concentration", lambda x: x[0]),
        'o3':          ('airqo3_m',        "microgram_per_meter_cubed", "group_concentration", lambda x: x[0]),
        'o3_vol':      ('o3',              "ppb",                       "group_fraction",      lambda x: x),
        'so2':         ('so2_m',           "microgram_per_meter_cubed", "group_concentration", lambda x: x[0]),
        'so2_vol':     ('so2',             'ppb',                       'group_fraction',      lambda x: x[0]),
        'tvoc':        ('TVOC',            'ppb',                       'group_fraction',      lambda x: x[0]),
        'oxygen':      ('o2',              'percent',                   'group_percent',       lambda x: x[0]),
        'sound':       ('noise',           'dB',                        'group_db',            lambda x: x[0]),
        'performance': ('airqPerfIdx',     'percent',                   'group_percent',       lambda x: float(x)/10),
        'health':      ('airqHealthIdx',   'percent',                   'group_percent',       lambda x: x/10),
        'cnt0_3':      ('cnt0_3',          'count',                     'group_count',         lambda x: int(x[0])),
        'cnt0_5':      ('cnt0_5',          'count',                     'group_count',         lambda x: int(x[0])),
        'cnt1':        ('cnt1_0',          'count',                     'group_count',         lambda x: int(x[0])),
        'cnt2_5':      ('cnt2_5',          'count',                     'group_count',         lambda x: int(x[0])),
        'cnt5':        ('cnt5_0',          'count',                     'group_count',         lambda x: int(x[0])),
        'cnt10':       ('cnt10_0',         'count',                     'group_count',         lambda x: int(x[0])),
        'TypPS':       ('TypPS',           None, None, lambda x:x),
        'bat':         ('airqBattery',     None, None, lambda x:x),
        'door_event':  ('airqDoorEvent',   None, None, lambda x:int(x))
        }

    # which readings are to accumulate calculating average
    AVG_GROUPS = [
        'group_temperature',
        'group_concentration',
        'group_fraction']

    # which readings are non-numeric
    ACCUM_LAST = [
        'DeviceID',
        'Status',
        'bat']

    # conversion volume to mass according to Dr. Daniel Lehmann of Corant
    CONV_V_M = {
        'co':  1.15,
        'no2': 1.88,
        'o3':  1.96,
        'so2': 2.62}

    def __init__(self, engine, config_dict):
        super(AirqService,self).__init__(engine, config_dict)
        loginf("air-Q %s service" % VERSION)
        # logging configuration
        self.log_success = config_dict.get('log_success',True)
        self.log_failure = config_dict.get('log_failure',True)

        d = config_dict.get('airQ', {})

        # get the database parameters we need to function
        binding = d.get('data_binding', 'airqDB_binding')
        self.dbm = self.engine.db_binder.get_manager(data_binding=binding,
                                                     initialize=True)

        # be sure schema in database matches the schema we have
        dbcol = self.dbm.connection.columnsOf(self.dbm.table_name)
        dbm_dict = weewx.manager.get_manager_dict(
            config_dict['DataBindings'], config_dict['Databases'], binding)
        memcol = [x[0] for x in dbm_dict['schema']]
        if dbcol != memcol:
            raise Exception('airq schema mismatch: %s != %s' % (dbcol, memcol))

        self.name = 'AirQ'
        self.address = d.get('host')                       # '192.168.38.18'
        self.passwd = d.get('password')                    # 'airsetup'
        self.query_interval = d.get('query_interval', 5.0) # '5'

        loginf("reading air-Q '%s', host '%s': starting" % (self.name,self.address))

        self.last_ts = None
        self.bind(weewx.NEW_ARCHIVE_RECORD, self.new_archive_record)

    def shutDown(self):
        try:
            self.dbm.close()
        except:
            pass


    def new_archive_record(self, event):
        """save data to database """
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


    def get_data(self, now_ts, last_ts):

        reply = airQget(self.address, '/data', self.passwd)

        record = {}
        record['dateTime'] = now_ts                       # required
        record['usUnits'] = weewx.METRIC                  # required
        record['interval'] = int((now_ts - last_ts) / 60) # required

        if reply['replyreason']=='OK':
            airqdata = reply

        else:
            return record

        record['airqUptime']  = airqdata['content']['uptime']
        record['airqMeasuretime']  = int(airqdata['content']['measuretime'] / 1000)
        record['airqTemp']  = airqdata['content']['temperature'][0]
        record['airqTemp_e']  = airqdata['content']['temperature'][1]
        record['airqHumidity']  = airqdata['content']['humidity'][0]
        record['airqHumidity_e']  = airqdata['content']['humidity'][1]
        record['airqHumAbs']  = airqdata['content']['humidity_abs'][0]
        record['airqHumAbs_e']  = airqdata['content']['humidity_abs'][1]
        record['airqDewpoint']  = airqdata['content']['dewpt'][0]
        record['airqDewpoint_e']  = airqdata['content']['dewpt'][1]
        record['airqPressure']  = airqdata['content']['pressure'][0]
        record['airqPressure_e']  = airqdata['content']['pressure'][1]
        record['airqco']  = float(airqdata['content']['co'][0] * 1000)
        record['airqco_e']  = airqdata['content']['co'][1]
        record['airqco2']  = airqdata['content']['co2'][0]
        record['airqco2_e']  = airqdata['content']['co2'][1]
        record['airqno2']  = airqdata['content']['no2'][0]
        record['airqno2_e']  = airqdata['content']['no2'][1]
        record['airqpm1_0']  = airqdata['content']['pm1'][0]
        record['airqpm1_0_e']  = airqdata['content']['pm1'][1]
        record['airqpm2_5']  = airqdata['content']['pm2_5'][0]
        record['airqpm2_5_e']  = airqdata['content']['pm2_5'][1]
        record['airqpm10_0']  = airqdata['content']['pm10'][0]
        record['airqpm10_0_e']  = airqdata['content']['pm10'][1]
        record['airqo3']  = airqdata['content']['o3'][0]
        record['airqo3_e']  = airqdata['content']['o3'][1]
        record['airqso2']  = airqdata['content']['so2'][0]
        record['airqso2_e']  = airqdata['content']['so2'][1]
        record['airqTVOC']  = float(airqdata['content']['tvoc'][0] / 1000)
        record['airqTVOC_e']  = airqdata['content']['tvoc'][1]
        record['airqo2']  = airqdata['content']['oxygen'][0]
        record['airqo2_e']  = airqdata['content']['oxygen'][1]
        record['airqnoise']  = airqdata['content']['sound'][0]
        record['airqnoise_e']  = airqdata['content']['sound'][1]
        record['airqcnt0_3']  = airqdata['content']['cnt0_3'][0]
        record['airqcnt0_5']  = airqdata['content']['cnt0_5'][0]
        record['airqcnt1_0']  = airqdata['content']['cnt1'][0]
        record['airqcnt2_5']  = airqdata['content']['cnt2_5'][0]
        record['airqcnt5_0']  = airqdata['content']['cnt5'][0]
        record['airqcnt10_0']  = airqdata['content']['cnt10'][0]
        record['airqcnt0_3_e']  = airqdata['content']['cnt0_3'][1]
        record['airqcnt0_5_e']  = airqdata['content']['cnt0_5'][1]
        record['airqcnt1_0_e']  = airqdata['content']['cnt1'][1]
        record['airqcnt2_5_e']  = airqdata['content']['cnt2_5'][1]
        record['airqcnt5_0_e']  = airqdata['content']['cnt5'][1]
        record['airqcnt10_0_e']  = airqdata['content']['cnt10'][1]
        record['airqBattery']  = airqdata['content']['bat'][0]
        record['airqBattery_e']  = airqdata['content']['bat'][1]
        record['airqDoorEvent']  = airqdata['content']['door_event']
        record['airqHumAbsDelta']  = airqdata['content']['dHdt']
        record['airqCO2delta']  = airqdata['content']['dCO2dt']
        record['airqTypPS']  = airqdata['content']['TypPS']
        record['airqPerfIdx']  = float(airqdata['content']['performance'] / 10)
        record['airqHealthIdx']  = float(airqdata['content']['health'] / 10)
        record['airqtime']  = int(airqdata['content']['timestamp'] / 1000)
        press_data = airqdata['content']['pressure'][0]
        temp_data = airqdata['content']['temperature'][0]
        record['airqAltimeter'] = altimeter_pressure_Metric(press_data, 53.6)
        record['airqBarometer'] = sealevel_pressure_Metric(press_data, 53.6, temp_data)

        return record


# To test the service, run it directly as follows:
if __name__ == '__main__':
    if False:
        connection = http.client.HTTPConnection(airqIP)
        reply = airQget(connection, '/data', airqpass)
        connection.close()
        print("Status {} - {}".format(reply['replystatus'],reply['replyreason']))
        #print(reply['content'])
        for ii in reply['content']:
            print("%15s: %s" % (ii,reply['content'][ii]))
    else:
        CONF = {
            'airQ': {
                '1': {
                    'host':airqIP,
                    'password':airqpass
                    }
                }
            }
        srv = AirqService(Engine(),CONF)
        print("weewx.accum.accum_dict = ")
        print(weewx.accum.accum_dict)
        print("weewx.units.conversionDict =")
        print(weewx.units.conversionDict)
        print("-----------")
        for jj in range(1):
            time.sleep(11)
            evt = Event()
            srv.new_loop_packet(evt)
            for ii in evt.packet:
                print("%15s: %s" % (ii,evt.packet[ii]))
            print("------------")
        srv.shutdown()
