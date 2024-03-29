#
#    Copyright (c) 2009-2021 Tom Keffer <tkeffer@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#
"""The wview schema, which is also used by weewx."""

# =============================================================================
# This is original schema for both weewx and wview, expressed using Python.
# It is only used for initialization --- afterwards, the schema is obtained
# dynamically from the database.
#
# Although a type may be listed here, it may not necessarily be supported by
# your weather station hardware.
#
# You may trim this list of any unused types if you wish, but it may not
# result in saving as much space as you might think --- most of the space is
# taken up by the primary key indexes (type "dateTime").
# =============================================================================
# NB: This schema is specified using the WeeWX V4 "new-style" schema.
# =============================================================================
table = [('dateTime',             'INTEGER NOT NULL UNIQUE PRIMARY KEY'),
         ('usUnits',              'INTEGER NOT NULL'),
         ('interval',             'INTEGER NOT NULL'),
         ('barometer',            'REAL'),
         ('pressure',             'REAL'),
         ('altimeter',            'REAL'),
         ('inTemp',               'REAL'),
         ('outTemp',              'REAL'),
         ('inHumidity',           'REAL'),
         ('outHumidity',          'REAL'),
         ('windSpeed',            'REAL'),
         ('windDir',              'REAL'),
         ('windGust',             'REAL'),
         ('windGustDir',          'REAL'),
         ('rainRate',             'REAL'),
         ('rain',                 'REAL'),
         ('stormRain',            'REAL'),
         ('dewpoint',             'REAL'),
         ('windchill',            'REAL'),
         ('heatindex',            'REAL'),
         ('ET',                   'REAL'),
         ('radiation',            'REAL'),
         ('UV',                   'REAL'),
         ('extraTemp1',           'REAL'),
         ('extraTemp2',           'REAL'),
         ('extraTemp3',           'REAL'),
         ('soilTempO1',           'REAL'),
         ('soilTempO2',           'REAL'),
         ('soilTempO3',           'REAL'),
         ('soilTempO4',           'REAL'),
         ('soilTempO5',           'REAL'),
         ('leafTemp1',            'REAL'),
         ('leafTemp2',            'REAL'),
         ('extraHumid1',          'REAL'),
         ('extraHumid2',          'REAL'),
         ('soilMoist1',           'REAL'),
         ('soilMoist2',           'REAL'),
         ('soilMoist3',           'REAL'),
         ('soilMoist4',           'REAL'),
         ('leafWet1',             'REAL'),
         ('leafWet2',             'REAL'),
         ('rxCheckPercent',       'REAL'),
         ('txBatteryStatus',      'REAL'),
         ('consBatteryVoltage',   'REAL'),
         ('hail',                 'REAL'),
         ('hailRate',             'REAL'),
         ('heatingTemp',          'REAL'),
         ('heatingVoltage',       'REAL'),
         ('supplyVoltage',        'REAL'),
         ('referenceVoltage',     'REAL'),
         ('windBatteryStatus',    'REAL'),
         ('rainBatteryStatus',    'REAL'),
         ('outTempBatteryStatus', 'REAL'),
         ('lighting',             'REAL'),
         ('extraTemp4',           'REAL'),
         ('extraTemp5',           'REAL'),
         ('extraTemp6',           'REAL'),
         ('extraTemp7',           'REAL'),
         ('extraTemp8',           'REAL'),
         ('extraTemp9',           'REAL'),
         ('maxSolarRad',          'REAL'),
         ('cloudbase',            'REAL'),
         ('humidex',              'REAL'),
         ('appTemp',              'REAL'),
         ('windrun',              'REAL'),
         ('stormStart',           'REAL'),
         ('inDewpoint',           'REAL'),
         ('inTempBatteryStatus',  'REAL'),
         ('absolutF',             'REAL'),
         ('sunshineS',            'REAL'),
         ('snow',                 'REAL'),
         ('snowRate',             'REAL'),
         ('snowTotal',            'REAL'),
         ('wetBulb',              'REAL'),
         ('cbIndex',              'REAL'),
         ('airDensity',           'REAL'),
         ('windDruck',            'REAL'),
         ('soilTemp1',            'REAL'),
         ('soilTemp2',            'REAL'),
         ('soilTemp3',            'REAL'),
         ('soilTemp4',            'REAL'),
         ('soilTemp5',            'REAL'),
         ('dampfDruck',           'REAL'),
         ('summersimmerIndex',    'REAL'),
         ('SVP',                  'REAL'),
         ('SVPin',                'REAL'),
         ('AVP',                  'REAL'),
         ('AVPin',                'REAL'),
         ('densityA',             'REAL'),
         ('thwIndex',             'REAL'),
         ('thswIndex',            'REAL'),
         ('windSpeed10',          'REAL'),
         ('windSpeed2',           'REAL'),
         ('windGust10',           'REAL'),
         ('windGustDir10',        'REAL'),
         ('THSW',                 'REAL'),
         ('dayRain',              'REAL'),
         ('rain15',               'REAL'),
         ('rain24',               'REAL'),
         ('hourRain',             'REAL'),
         ('dayET',                'REAL'),
         ('forecastRule',         'REAL'),
         ('extraTempO0',          'REAL'),
         ('extraTempO1',          'REAL'),
         ('extraTempO2',          'REAL'),
         ('extraTempO3',          'REAL'),
         ('extraTempO4',          'REAL'),
         ('extraTempO5',          'REAL'),
         ('extraTempO6',          'REAL'),
         ('extraTempO7',          'REAL'),
         ('trendIcon',            'REAL'),
         ('bar_calibration',      'REAL'),
         ('bar_reduction',        'REAL'),
         ('bar_offset',           'REAL'),
         ('pressure_raw',         'REAL'),
         ('monthRain',            'REAL'),
         ('yearRain',             'REAL'),
         ('monthET',              'REAL'),
         ('yearET',               'REAL'),
         ('beaufort',             'REAL'),
         ('radiationEnergy',      'REAL'),
         ]

day_summaries = [(e[0], 'scalar') for e in table
                 if e[0] not in ('dateTime', 'usUnits', 'interval')] + [('wind', 'VECTOR')]

schema = {
    'table': table,
    'day_summaries': day_summaries
}

