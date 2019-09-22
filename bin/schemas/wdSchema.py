##
##This program is free software; you can redistribute it and/or modify it under
##the terms of the GNU General Public License as published by the Free Software
##Foundation; either version 2 of the License, or (at your option) any later
##version.
##
##This program is distributed in the hope that it will be useful, but WITHOUT
##ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
##FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
##details.
##
## Version: 1.3.0                                    Date: 1 May 2019
##
## Revision History
##  01 May 2019         v1.3.0      - DS for WU
##  01 August 2015      v1.2.0      -removed Weewx-WD schema data from
##                                   weewxwd3.py
##
"""The Weewx-WD schemas"""
# =============================================================================
# These lists contain the default schema of the Weewx-WD archive table and the
# supp table. They are only used for initialization, or in conjunction with the
# weewxwd_config --create-database and --reconfigure options. Otherwise, once
# the tables are created the schema is obtained dynamically from the database.
# Although a type may be listed here, it may not necessarily be supported by
# your weather station hardware.
#
# You may trim this list of any unused types if you wish, but it will not
# result in saving as much space as you may think --- most of the space is
# taken up by the primary key indexes (type "dateTime").
# =============================================================================
#

WDSCHEMA_VERSION = '1.2.0b1'

# Define schema for archive table
weewxwd_schema = [
    ('dateTime',     'INTEGER NOT NULL UNIQUE PRIMARY KEY'),
    ('usUnits',      'INTEGER NOT NULL'),
    ('interval',     'INTEGER NOT NULL'),
    ('humidex',      'REAL'),
    ('appTemp',      'REAL'),
    ('summersimmerIndex',  'REAL'),
    ('outTempDay',   'REAL'),
    ('outTempNight', 'REAL'),
    ('heatdeg',      'REAL'),
    ('cooldeg',      'REAL'),
    ('homedeg',      'REAL'),
    ('SVP',          'REAL'),
    ('SVPin',        'REAL'),
    ('AVP',          'REAL'),
    ('AVPin',        'REAL'),
    ('wdd_deg',      'REAL'),
    ('GDD4',         'REAL'),
    ('GDD6',         'REAL'),
    ('GDD10',        'REAL'),
    ('thwIndex',     'REAL'),
    ('thswIndex',    'REAL'),
    ('rain_ET',      'REAL'),
    ('windSpeed10',  'REAL'),
    ('dayRain',      'REAL'),
    ('monthRain',    'REAL'),
    ('yearRain',     'REAL'),
    ('dayET',        'REAL'),
    ('monthET',      'REAL'),
    ('yearET',       'REAL'),
    ('stormRain',    'REAL'),
    ('stormStart',   'INTEGER'),
    ('forecastRule', 'REAL'),
    ]

# Define schema for supp table
wdsupp_schema = [
    ('dateTime',            'INTEGER NOT NULL UNIQUE PRIMARY KEY'),
    ('usUnits',             'INTEGER NOT NULL'),
    ('interval',            'INTEGER NOT NULL'),
    ('forecastIcon',        'INTEGER'),
    ('forecastText',        'VARCHAR(256)'),
    ('forecastTextMetric',  'VARCHAR(256)'),
    ('currentIcon',         'INTEGER'),
    ('currentText',         'VARCHAR(256)'),
    ('tempRecordHigh',      'REAL'),
    ('tempNormalHigh',      'REAL'),
    ('tempRecordHighYear',  'INTEGER'),
    ('tempRecordLow',       'REAL'),
    ('tempNormalLow',       'REAL'),
    ('tempRecordLowYear',   'INTEGER'),
    ('vantageForecastIcon', 'INTEGER'),
    ('vantageForecastRule', 'VARCHAR(256)'),
    ('stormRain',           'REAL'),
    ('stormStart',          'INTEGER'),
    ('visibility_km',       'REAL'),
    ('pop',                 'REAL'),
    ('vantageForecastNumber', 'REAL'),
    ('windSpeed10',           'REAL'),
    ('rain15',                'REAL'),
    ('hourRain',              'REAL'),
    ('rain24',                'REAL'),
    ('dayRain',               'REAL'),
    ('monthRain',             'REAL'),
    ('yearRain',              'REAL'),
    ('dayET',                 'REAL'),
    ('monthET',               'REAL'),
    ('yearET',                'REAL'),
    ]

