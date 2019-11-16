#
#
#    See the file LICENSE.txt for your full rights.
#
#     air.py 2766 2015-05-09 02:45:36Z hes $
#
"""The air schema, which is also used by weewx."""

schema = [
    ('dateTime',      'INTEGER NOT NULL PRIMARY KEY'),
    ('usUnits',       'INTEGER NOT NULL'),
    ('interval',      'INTEGER NOT NULL'),
    ('air_sensor',    'REAL'),
    ('gas_sensor',    'REAL'),
    ('hcho_sensor',   'REAL'),
    ('water_sensor',  'REAL'),
    ('light_sensor',  'REAL'),
    ('uv_sensor',     'REAL'),
    ('gasC_sensor',   'REAL'),
    ('gasO_sensor',   'REAL'),
    ('gasN_sensor',   'REAL'),
    ('gasx_sensor',   'REAL'),
    ('lightD_sensor', 'REAL'),
    ('dust_sensor',   'REAL'),
    ('lightIn_sensor', 'REAL'),
    ('adc_sensor',     'REAL'),
    ('temp',           'REAL'),
    ('pressure',       'REAL'),
    ('altitude',       'REAL'),
    ('pm_25',          'REAL'),
    ('pm_10',          'REAL'),
    ]

# Schema to be used for the daily summaries. The default is to include all the observation types in the table as
# 'scalar' types, plus one for 'wind' as a vector type.
day_summaries = [(e[0], 'scalar') for e in table if e[0] not in ('dateTime', 'usUnits', 'interval')]\
                + [('wind', 'vector')]

schema = {
    'table': table,
    'day_summaries' : day_summaries
}
