# $Id: cmon.py 1142 2014-11-25 01:00:42Z mwall $
# Copyright 2013 Matthew Wall
"""weewx module that records cpu, memory, disk, and network usage.

Installation

Put this file in the bin/user directory.


Configuration

Add the following to weewx.conf:

[ComputerMonitor]
    data_binding = cmon_binding
    max_age = 2592000 # 30 days; None to store indefinitely

[DataBindings]
    [[cmon_binding]]
        database = cmon_sqlite
        manager = weewx.manager.DaySummaryManager
        table_name = archive
        schema = user.cmon.schema

[Databases]
    [[cmon_sqlite]]
        root = %(WEEWX_ROOT)s
        database_name = archive/cmon.sdb
        driver = weedb.sqlite

[Engine]
    [[Services]]
        archive_services = ..., user.cmon.ComputerMonitor


Schema

The default schema is defined in this file.  If you prefer to maintain a schema
different than the default, specify the desired schema in the configuration.
For example, this would be a schema that stores only memory and network data,
and uses eth1 instead of the default eth0:

[DataBindings]
    [[cmon_binding]]
        database = cmon_sqlite
        [[[schema]]]
            dateTime = INTEGER NOT NULL PRIMARY KEY
            usUnits = INTEGER NOT NULL
            interval = INTEGER NOT NULL
            mem_total = INTEGER
            mem_free = INTEGER
            mem_used = INTEGER
            swap_total = INTEGER
            swap_free = INTEGER
            swap_used = INTEGER
            net_eth1_rbytes = INTEGER
            net_eth1_rpackets = INTEGER
            net_eth1_rerrs = INTEGER
            net_eth1_rdrop = INTEGER
            net_eth1_tbytes = INTEGER
            net_eth1_tpackets = INTEGER
            net_eth1_terrs = INTEGER
            net_eth1_tdrop = INTEGER

Another approach to maintaining a custom schema is to define the schema in the
file user/extensions.py as cmonSchema:

cmonSchema = [
    ('dateTime', 'INTEGER NOT NULL PRIMARY KEY'),
    ('usUnits', 'INTEGER NOT NULL'),
    ('interval', 'INTEGER NOT NULL'),
    ('mem_total','INTEGER'),
    ('mem_free','INTEGER'),
    ('mem_used','INTEGER'),
    ('net_eth1_rbytes','INTEGER'),
    ('net_eth1_rpackets','INTEGER'),
    ('net_eth1_rerrs','INTEGER'),
    ('net_eth1_rdrop','INTEGER'),
    ('net_eth1_tbytes','INTEGER'),
    ('net_eth1_tpackets','INTEGER'),
    ('net_eth1_terrs','INTEGER'),
    ('net_eth1_tdrop','INTEGER'),
    ]

then load it using this configuration:

[DataBindings]
    [[cmon_binding]]
        schema = user.extensions.cmonSchema
"""

# FIXME: make these methods platform-independent instead of linux-specific
# FIXME: deal with MB/GB in memory sizes
# FIXME: save the counts or save the differences?  for now the differences

from __future__ import with_statement
import os
import platform
import re
import syslog
import time
from subprocess import Popen, PIPE

import weewx
import weeutil.weeutil
from weewx.engine import StdService

VERSION = "0.7"

if weewx.__version__ < "3":
    raise weewx.UnsupportedFeature("weewx 3 is required, found %s" %
                                   weewx.__version__)

schema = [
    ('dateTime', 'INTEGER NOT NULL PRIMARY KEY'),
    ('usUnits', 'INTEGER NOT NULL'),
    ('interval', 'INTEGER NOT NULL'),
    ('mem_total','INTEGER'),
    ('mem_free','INTEGER'),
    ('mem_used','INTEGER'),
    ('swap_total','INTEGER'),
    ('swap_free','INTEGER'),
    ('swap_used','INTEGER'),
    ('cpu_user','INTEGER'),
    ('cpu_nice','INTEGER'),
    ('cpu_system','INTEGER'),
    ('cpu_idle','INTEGER'),
    ('cpu_iowait','INTEGER'),
    ('cpu_irq','INTEGER'),
    ('cpu_softirq','INTEGER'),
    ('load1','REAL'),
    ('load5','REAL'),
    ('load15','REAL'),
    ('proc_active','INTEGER'),
    ('proc_total','INTEGER'),

# measure cpu temperature (not all platforms support this)
    ('cpu_temp','REAL'),  # degree C
    ('cpu_temp1','REAL'), # degree C
    ('cpu_temp2','REAL'), # degree C
    ('cpu_temp3','REAL'), # degree C
    ('cpu_temp4','REAL'), # degree C

# measure gpu temperature (not all platforms support this)
#    ('gpu_temp','REAL'), # degree C

# the default interface on most linux systems is eth0
    ('net_eth0_rbytes','INTEGER'),
    ('net_eth0_rpackets','INTEGER'),
    ('net_eth0_rerrs','INTEGER'),
    ('net_eth0_rdrop','INTEGER'),
    ('net_eth0_tbytes','INTEGER'),
    ('net_eth0_tpackets','INTEGER'),
    ('net_eth0_terrs','INTEGER'),
    ('net_eth0_tdrop','INTEGER'),

# some systems have a wireless interface as wlan0
    ('net_wlan0_rbytes','INTEGER'),
    ('net_wlan0_rpackets','INTEGER'),
    ('net_wlan0_rerrs','INTEGER'),
    ('net_wlan0_rdrop','INTEGER'),
    ('net_wlan0_tbytes','INTEGER'),
    ('net_wlan0_tpackets','INTEGER'),
    ('net_wlan0_terrs','INTEGER'),
    ('net_wlan0_tdrop','INTEGER'),

# if the computer is an openvpn server, track the tunnel traffic
#    ('net_tun0_rbytes','INTEGER'),
#    ('net_tun0_rpackets','INTEGER'),
#    ('net_tun0_rerrs','INTEGER'),
#    ('net_tun0_rdrop','INTEGER'),
#    ('net_tun0_tbytes','INTEGER'),
#    ('net_tun0_tpackets','INTEGER'),
#    ('net_tun0_terrs','INTEGER'),
#    ('net_tun0_tdrop','INTEGER'),

# disk volumes will vary, but root is always present
    ('disk_root_total','INTEGER'),
    ('disk_root_free','INTEGER'),
    ('disk_root_used','INTEGER'),
# separate partition for home is not uncommon
    ('disk_home_total','INTEGER'),
    ('disk_home_free','INTEGER'),
    ('disk_home_used','INTEGER'),
#    ('disk_var_weewx_total','INTEGER'),
#    ('disk_var_weewx_free','INTEGER'),
#    ('disk_var_weewx_used','INTEGER'),

# measure the ups parameters if we can
    ('ups_temp','REAL'),    # degree C
    ('ups_load','REAL'),    # percent
    ('ups_charge','REAL'),  # percent
    ('ups_voltage','REAL'), # volt
    ('ups_time','REAL'),    # seconds
    ]

# this exension will scan for all mounted file system.  these are the
# filesystems we ignore.
IGNORED_MOUNTS = [
    '/lib/init/rw',
    '/proc',
    '/sys',
    '/dev',
    '/afs',
    '/mit',
    '/run',
    ]

CPU_KEYS = ['user','nice','system','idle','iowait','irq','softirq']

# bytes received
# packets received
# packets dropped
# fifo buffer errors
# packet framing errors
# compressed packets
# multicast frames
NET_KEYS = [
    'rbytes','rpackets','rerrs','rdrop','rfifo','rframe','rcomp','rmulti',
    'tbytes','tpackets','terrs','tdrop','tfifo','tframe','tcomp','tmulti'
    ]

def logmsg(level, msg):
    syslog.syslog(level, 'cmon: %s' % msg)

def logdbg(msg):
    logmsg(syslog.LOG_DEBUG, msg)

def loginf(msg):
    logmsg(syslog.LOG_INFO, msg)

def logerr(msg):
    logmsg(syslog.LOG_ERR, msg)

def _readproc_line(filename):
    """read single line proc file, return the string"""
    info = ''
    with open(filename) as fp:
        info = fp.read()
    return info

def _readproc_lines(filename):
    """read proc file that has 'name value' format for each line"""
    info = {}
    with open(filename) as fp:
        for line in fp:
            line = line.replace('  ',' ')
            (label,data) = line.split(' ',1)
            info[label] = data
    return info

def _readproc_dict(filename):
    """read proc file that has 'name:value' format for each line"""
    info = {}
    with open(filename) as fp:
        for line in fp:
            if line.find(':') >= 0:
                (n,v) = line.split(':',1)
                info[n.strip()] = v.strip()
    return info


class ComputerMonitor(StdService):
    """Collect CPU, Memory, Disk, and other computer information."""

    def __init__(self, engine, config_dict):
        super(ComputerMonitor, self).__init__(engine, config_dict)
        loginf("service version is %s" % VERSION)

        d = config_dict.get('ComputerMonitor', {})
        self.ignored_mounts = d.get('ignored_mounts', IGNORED_MOUNTS)
        self.hardware = d.get('hardware', [None])
        if not isinstance(self.hardware, list):
            self.hardware = [self.hardware]
        self.max_age = weeutil.weeutil.to_int(d.get('max_age', 2592000))

        # get the database parameters we need to function
        binding = d.get('data_binding', 'cmon_binding')
        self.dbm = self.engine.db_binder.get_manager(data_binding=binding,
                                                     initialize=True)

        # be sure schema in database matches the schema we have
        dbcol = self.dbm.connection.columnsOf(self.dbm.table_name)
        dbm_dict = weewx.manager.get_manager_dict(
            config_dict['DataBindings'], config_dict['Databases'], binding)
        memcol = [x[0] for x in dbm_dict['schema']]
        if dbcol != memcol:
            raise Exception('cmon schema mismatch: %s != %s' % (dbcol, memcol))

        # see what we are running on
        self.system = platform.system()

        # provide info about the system on which we are running
        loginf('sysinfo: %s' % ' '.join(os.uname()))
        if self.system == 'Linux':
            cpuinfo = _readproc_dict('/proc/cpuinfo')
            for key in cpuinfo:
                loginf('cpuinfo: %s: %s' % (key, cpuinfo[key]))

        self.last_ts = None
        self.last_cpu = {}
        self.last_net = {}
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
        if self.max_age is not None:
            self.prune_data(now - self.max_age)

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
        if self.system == 'Darwin':
            record.update(self._get_macosx_info())
        elif self.system == 'BSD':
            record.update(self._get_bsd_info())
        elif self.system == 'Linux':
            record.update(self._get_linux_info())
        else:
            logerr('unsupported system %s' % self.system)
        if 'rpi' in self.hardware:
            record.update(self._get_rpi_info())
        if 'apcups' in self.hardware:
            record.update(self._get_apcups_info())
        return record

    def _get_bsd_info(self):
        # FIXME: implement bsd methods
        return {}

    def _get_macosx_info(self):
        # FIXME: implement macosx methods
        return {}

    # this should work on any linux running kernel 2.2 or later
    def _get_linux_info(self):
        record = {}

        # read memory status
        meminfo = _readproc_dict('/proc/meminfo')
        record['mem_total'] = int(meminfo['MemTotal'].split()[0]) # kB
        record['mem_free'] = int(meminfo['MemFree'].split()[0]) # kB
        record['mem_used'] = record['mem_total'] - record['mem_free']
        record['swap_total'] = int(meminfo['SwapTotal'].split()[0]) # kB
        record['swap_free'] = int(meminfo['SwapFree'].split()[0]) # kB
        record['swap_used'] = record['swap_total'] - record['swap_free']

        # get cpu usage
        cpuinfo = _readproc_lines('/proc/stat')
        values = cpuinfo['cpu'].split()[0:7]
        for i,key in enumerate(CPU_KEYS):
            if self.last_cpu.has_key(key):
                record['cpu_'+key] = int(values[i]) - self.last_cpu[key]
            self.last_cpu[key] = int(values[i])

        # get network usage
        netinfo = _readproc_dict('/proc/net/dev')
        for iface in netinfo:
            values = netinfo[iface].split()
            for i,key in enumerate(NET_KEYS):
                if not self.last_net.has_key(iface):
                    self.last_net[iface] = {}
                if self.last_net[iface].has_key(key):
                    record['net_'+iface+'_'+key] = int(values[i]) - self.last_net[iface][key]
                    if record['net_'+iface+'_'+key] < 0:
                        maxcnt = 0x100000000 # 32-bit counter
                        if record['net_'+iface+'_'+key] + maxcnt < 0:
                            maxcnt = 0x10000000000000000 # 64-bit counter
                        record['net_'+iface+'_'+key] += maxcnt
                self.last_net[iface][key] = int(values[i])

#        uptimestr = _readproc_line('/proc/uptime')
#        (uptime,idletime) = uptimestr.split()

        # get load and process information
        loadstr = _readproc_line('/proc/loadavg')
        (load1,load5,load15,nproc) = loadstr.split()[0:4]
        record['load1'] = float(load1)
        record['load5'] = float(load5)
        record['load15'] = float(load15)

        (num_proc,tot_proc) = nproc.split('/')
        record['proc_active'] = int(num_proc)
        record['proc_total'] = int(tot_proc)

        # read cpu temperature
        tdir = '/sys/class/hwmon/hwmon0/device'
        # rpi keeps cpu temperature in a different location
        tfile = '/sys/class/thermal/thermal_zone0/temp'
        if os.path.exists(tdir):
            for f in os.listdir(tdir):
                if f.endswith('_input'):
                    s = _readproc_line(os.path.join(tdir,f))
                    if len(s):
                        n = f.replace('_input','')
                        tC = int(s) / 1000 # degree C
                        tF = 32.0 + tC * 9.0 / 5.0
                        record['cpu_' + n] = tC
        elif os.path.exists(tfile):
            s = _readproc_line(tfile)
            tC = int(s) / 1000 # degree C
            record['cpu_temp'] = tC

        # get stats on mounted filesystems
        disks = []
        mntlines = _readproc_lines('/proc/mounts')
        for mnt in mntlines:
            mntpt = mntlines[mnt].split()[0]
            ignore = False
            if mnt.find(':') >= 0:
                ignore = True
            for m in self.ignored_mounts:
                if mntpt.startswith(m):
                    ignore = True
                    break
            if not ignore:
                disks.append(mntpt)
        for disk in disks:
            label = disk.replace('/','_')
            if label == '_':
                label = '_root'
            st = os.statvfs(disk)
            free = int((st.f_bavail * st.f_frsize) / 1024) # kB
            total = int((st.f_blocks * st.f_frsize) / 1024) # kB
            used = int(((st.f_blocks - st.f_bfree) * st.f_frsize) / 1024) # kB
            record['disk'+label+'_free'] = free
            record['disk'+label+'_total'] = total
            record['disk'+label+'_used'] = used

        return record

    DIGITS = re.compile('[\d.]+')

    def _get_apcups_info(self):
        record = {}
        try:
            cmd = '/sbin/apcaccess'
            p = Popen(cmd, shell=True, stdout=PIPE)
            o = p.communicate()[0]
            for line in o.split('\n'):
                if line.startswith('ITEMP'):
                    m = self.DIGITS.search(line)
                    if m:
                        record['ups_temp'] = float(m.group())
                elif line.startswith('LOADPCT'):
                    m = self.DIGITS.search(line)
                    if m:
                        record['ups_load'] = float(m.group())
                elif line.startswith('BCHARGE'):
                    m = self.DIGITS.search(line)
                    if m:
                        record['ups_charge'] = float(m.group())
                elif line.startswith('OUTPUTV') or line.startswith('BATTV'):
                    m = self.DIGITS.search(line)
                    if m:
                        record['ups_voltage'] = float(m.group())
                elif line.startswith('TIMELEFT'):
                    m = self.DIGITS.search(line)
                    if m:
                        record['ups_time'] = float(m.group())
        except (ValueError, IOError, KeyError), e:
            logerr('apcups_info failed: %s' % e)
        return record

    def _get_rpi_info(self):
        record = {}
        # get cpu temp on raspberry pi
        try:
            cmd = '/opt/vc/bin/vcgencmd measure_temp'
            p = Popen(cmd, shell=True, stdout=PIPE)
            o = p.communicate()[0]
            record['gpu_temp'] = float(o.replace("'C\n", '').partition('=')[2])
        except (ValueError, IOError, KeyError), e:
            logerr('rpi_info failed: %s' % e)
        return record


# what follows is a basic unit test of this module.  to run the test:
#
# cd /home/weewx
# PYTHONPATH=bin python bin/user/cmon.py
#
if __name__=="__main__":
    from weewx.engine import StdEngine
    config = {
        'Station': {
            'station_type': 'Simulator',
            'altitude': [0, 'foot'],
            'latitude': 0,
            'longitude': 0},
        'Simulator': {
            'driver': 'weewx.drivers.simulator',
            'mode': 'simulator'},
        'ComputerMonitor': {
            'binding': 'cmon_binding'},
        'DataBindings': {
            'cmon_binding': {
                'database': 'cmon_sqlite',
                'manager': 'weewx.manager.DaySummaryManager',
                'table_name': 'archive',
                'schema': 'user.cmon.schema'}},
        'Databases': {
            'cmon_sqlite': {
                'root': '%(WEEWX_ROOT)s',
                'database_name': '/tmp/cmon.sdb',
                'driver': 'weedb.sqlite'}},
        'Engine': {
            'Services': {
                'archive_services': 'user.cmon.ComputerMonitor'}}}
    engine = StdEngine(config)
    svc = ComputerMonitor(engine, config)
    record = svc.get_data()
    print record

    time.sleep(5)
    record = svc.get_data()
    print record

    time.sleep(5)
    record = svc.get_data()
    print record

    os.remove('/tmp/cmon.sdb')
