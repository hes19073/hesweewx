#
#    Copyright (c) 2009-2015 Tom Keffer <tkeffer@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#
"""The wxAlt schema, which is also used by weewx."""

# =============================================================================
# This is a list containing the default schema of the archive database.  It is
# identical to what is used by wview. It is only used for initialization ---
# afterwards, the schema is obtained dynamically from the database.  Although a
# type may be listed here, it may not necessarily be supported by your weather
# station hardware.
#
# You may trim this list of any unused types if you wish, but it will not
# result in saving as much space as you may think --- most of the space is
# taken up by the primary key indexes (type "dateTime").
# =============================================================================
schema = [('yyyymmdd',             'INTEGER NOT NULL UNIQUE PRIMARY KEY'),
          ('usUnits',              'INTEGER NOT NULL'),
          ('interval',             'INTEGER NOT NULL'),
          ('jahr',                 'REAL'),
          ('monat',                'REAL'),
          ('tag',                  'REAL'),
          ('windGust_ms',          'REAL'),
          ('windGust_KmH',         'REAL'),
          ('windSpeed_ms',         'REAL'),
          ('windSpeedKmH',         'REAL'),
          ('rain_cm',              'REAL'),
          ('sonne',                'REAL'),
          ('snow_cm',              'REAL'),
          ('cloud',                'REAL'),
          ('Dampfdruck_hpa',       'REAL'),
          ('pressure_hpa',         'REAL'),
          ('outTempAvg',           'REAL'),
          ('outHumidity',          'REAL'),
          ('outTempMax',           'REAL'),
          ('outTempMin',           'REAL'),
          ('temp5cm',              'REAL')]
