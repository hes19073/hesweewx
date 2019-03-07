#
#
#    See the file LICENSE.txt for your full rights.
#
#     air.py 2766 2015-05-09 02:45:36Z hes $
#
"""The air schema, which is also used by weewx."""

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
    ('adc_sensor' 'INTEGER'),
    ('temp','INTEGER'),
    ('pressure','INTEGER'),
    ('altitude','INTEGER'),
    ('pm_25','INTEGER'),
    ('pm_10','INTEGER'),
    ]

