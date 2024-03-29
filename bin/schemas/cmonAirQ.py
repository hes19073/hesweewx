# cmon und airQ
table = [
    ('dateTime', 'INTEGER NOT NULL PRIMARY KEY'),
    ('usUnits', 'INTEGER NOT NULL'),
    ('interval', 'INTEGER NOT NULL'),
    ('mem_total', 'INTEGER'),
    ('mem_free', 'INTEGER'),
    ('mem_used', 'INTEGER'),
    ('swap_total', 'INTEGER'),
    ('swap_free', 'INTEGER'),
    ('swap_used', 'INTEGER'),
    ('cpu_user', 'INTEGER'),
    ('cpu_nice', 'INTEGER'),
    ('cpu_system', 'INTEGER'),
    ('cpu_idle', 'INTEGER'),
    ('cpu_iowait', 'INTEGER'),
    ('cpu_irq', 'INTEGER'),
    ('cpu_softirq', 'INTEGER'),
    ('load1', 'REAL'),
    ('load5', 'REAL'),
    ('load15', 'REAL'),
    ('proc_active', 'INTEGER'),
    ('proc_total', 'INTEGER'),
    ('cpu_temp', 'REAL'),  # degree C
    ('cpu_temp1', 'REAL'), # degree C
    ('cpu_temp2', 'REAL'), # degree C
    ('cpu_temp3', 'REAL'), # degree C
    ('cpu_temp4', 'REAL'), # degree C
    ('cpu_volt', 'REAL'),
    ('cpu_ampere', 'REAL'),
    ('cpu_kern1', 'REAL'),
    ('cpu_kern2', 'REAL'),
    ('usb_volt', 'REAL'),
    ('usb_ampere', 'REAL'),
    ('core_temp','REAL'), # degree C
    ('core_volt', 'REAL'),
    ('core_ampere', 'REAL'),
    ('core_sdram_c', 'REAL'),
    ('core_sdram_i', 'REAL'),
    ('core_sdram_p', 'REAL'),
    ('arm_mem', 'REAL'),
    ('gpu_mem', 'REAL'),
    ('net_eth0_rbytes', 'INTEGER'),
    ('net_eth0_rpackets', 'INTEGER'),
    ('net_eth0_rerrs', 'INTEGER'),
    ('net_eth0_rdrop', 'INTEGER'),
    ('net_eth0_tbytes', 'INTEGER'),
    ('net_eth0_tpackets', 'INTEGER'),
    ('net_eth0_terrs', 'INTEGER'),
    ('net_eth0_tdrop', 'INTEGER'),
    ('net_enp3s0_rbytes', 'INTEGER'),
    ('net_enp3s0_rpackets', 'INTEGER'),
    ('net_enp3s0_rerrs', 'INTEGER'),
    ('net_enp3s0_rdrop', 'INTEGER'),
    ('net_enp3s0_tbytes', 'INTEGER'),
    ('net_enp3s0_tpackets', 'INTEGER'),
    ('net_enp3s0_terrs', 'INTEGER'),
    ('net_enp3s0_tdrop', 'INTEGER'),
    ('disk_root_total', 'INTEGER'),
    ('disk_root_free', 'INTEGER'),
    ('disk_root_used', 'INTEGER'),
    ('disk_home_total', 'INTEGER'),
    ('disk_home_free', 'INTEGER'),
    ('disk_home_used', 'INTEGER'),
    ('ups_temp', 'REAL'),
    ('ups_load', 'REAL'),
    ('ups_charge', 'REAL'),
    ('ups_voltage', 'REAL'),
    ('ups_time', 'REAL'),
    ('powerR', 'REAL'),
    ('powerG', 'REAL'),
    ('energyR', 'REAL'),
    ('energyG', 'REAL'),
    #('airqDeviceID',    'REAL'),
    #('airqStatus',      'REAL'),
    ('airqMeasuretime', 'REAL'),
    ('airqUptime',      'REAL'),
    ('airqTemp',        'REAL'),
    ('airqHumidity',    'REAL'),
    ('airqHumAbs',      'REAL'),
    ('airqDewpoint',    'REAL'),
    ('airqPressure',    'REAL'),
    ('airqAltimeter',   'REAL'),
    ('airqBarometer',   'REAL'),
    ('airqco',          'REAL'),
    ('airqco2',         'REAL'),
    ('airqh2s',         'REAL'),
    ('airqno2',         'REAL'),
    ('pm1_0',           'REAL'),
    ('pm2_5',           'REAL'),
    ('pm10_0',          'REAL'),
    ('airqo3',          'REAL'),
    ('airqso2',         'REAL'),
    ('airqTVOC',        'REAL'),
    ('airqo2',          'REAL'),
    ('airqnoise',       'REAL'),
    ('airqPerfIdx',     'REAL'),
    ('airqHealthIdx',   'REAL'),
    ('cnt0_3',          'REAL'),
    ('cnt0_5',          'REAL'),
    ('cnt1_0',          'REAL'),
    ('cnt2_5',          'REAL'),
    ('cnt5_0',          'REAL'),
    ('cnt10_0',         'REAL'),
    ('airqTypPS',       'REAL'),
    ('airqBattery',     'REAL'),
    ('airqDoorEvent',   'REAL'),
    ('airqHumAbsdelta', 'REAL'),
    ('airqCO2delta',    'REAL'),
    ('airqco_m',        'REAL'),
    ('airqno2_m',       'REAL'),
    ('airqo3_m',        'REAL'),
    ('airqso2_m',       'REAL'),
    ('airqco2_m',       'REAL'),
    ]

day_summaries = [(e[0], 'scalar') for e in table
                 if e[0] not in ('dateTime', 'usUnits', 'interval')] + [('wind', 'VECTOR')]

schema = {
    'table': table,
    'day_summaries': day_summaries
}

