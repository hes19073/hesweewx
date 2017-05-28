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
## Version: 1.2.0b1                                    Date: 1 August 2015
##
## Revision History
##  ?? August 2015      v1.2.0      -removed Weewx-WD schema data from
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
    ('outTempDay',   'REAL'),
    ('outTempNight', 'REAL'),
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
    ('maxSolarRad',         'REAL'),
    ('visibility_km',       'REAL'),
    ('pop',                 'REAL'),
    ('vantageForecastNumber', 'REAL'),
    ]

