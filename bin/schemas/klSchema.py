#
#    Copyright (c) 2009-2019 Tom Keffer <tkeffer@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#
"""The wview schema, which is also used by weewx."""

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
table = [('dateTime',             'INTEGER NOT NULL UNIQUE PRIMARY KEY'),
          ('usUnits',              'INTEGER NOT NULL'),
          ('interval',             'INTEGER NOT NULL'),
          ('temp0',                'REAL'),
          ('temp1',                'REAL'),
          ('temp2',                'REAL'),
          ('temp3',                'REAL'),
          ('temp4',                'REAL'),
          ('temp5',                'REAL'),
          ('temp6',                'REAL'),
          ('temp7',                'REAL'),
          ('temp8',                'REAL'),
          ('humidity0',            'REAL'),
          ('humidity1',            'REAL'),
          ('humidity2',            'REAL'),
          ('humidity3',            'REAL'),
          ('humidity4',            'REAL'),
          ('humidity5',            'REAL'),
          ('humidity6',            'REAL'),
          ('humidity7',            'REAL'),
          ('humidity8',            'REAL'),
          ('dewpoint0',            'REAL'),
          ('dewpoint1',            'REAL'),
          ('dewpoint2',            'REAL'),
          ('dewpoint3',            'REAL'),
          ('dewpoint4',            'REAL'),
          ('dewpoint5',            'REAL'),
          ('dewpoint6',            'REAL'),
          ('dewpoint7',            'REAL'),
          ('dewpoint8',            'REAL'),
          ('heatindex0',           'REAL'),
          ('heatindex1',           'REAL'),
          ('heatindex2',           'REAL'),
          ('heatindex3',           'REAL'),
          ('heatindex4',           'REAL'),
          ('heatindex5',           'REAL'),
          ('heatindex6',           'REAL'),
          ('heatindex7',           'REAL'),
          ('heatindex8',           'REAL'),
          ('rxCheckPercent',       'REAL'),
          ('batteryStatus0',       'REAL'),
          ('batteryStatus1',       'REAL'),
          ('batteryStatus2',       'REAL'),
          ('batteryStatus3',       'REAL'),
          ('batteryStatus4',       'REAL'),
          ('batteryStatus5',       'REAL'),
          ('batteryStatus6',       'REAL'),
          ('batteryStatus7',       'REAL'),
          ('batteryStatus8',       'REAL'),
          ('SVD0',                 'REAL'),
          ('SVD1',                 'REAL'),
          ('SVD2',                 'REAL'),
          ('SVD3',                 'REAL'),
          ('SVD4',                 'REAL'),
          ('SVD5',                 'REAL'),
          ('SVD6',                 'REAL'),
          ('SVD7',                 'REAL'),
          ('SVD8',                 'REAL'),
          ('AVD0',                 'REAL'),
          ('AVD1',                 'REAL'),
          ('AVD2',                 'REAL'),
          ('AVD3',                 'REAL'),
          ('AVD4',                 'REAL'),
          ('AVD5',                 'REAL'),
          ('AVD6',                 'REAL'),
          ('AVD7',                 'REAL'),
          ('AVD8',                 'REAL'),
          ('absolutF0',            'REAL'),
          ('absolutF1',            'REAL'),
          ('absolutF2',            'REAL'),
          ('absolutF3',            'REAL'),
          ('absolutF4',            'REAL'),
          ('absolutF5',            'REAL'),
          ('absolutF6',            'REAL'),
          ('absolutF7',            'REAL'),
          ('absolutF8',            'REAL'),
          ('heatdeg0',             'REAL'),
          ('heatdeg1',             'REAL'),
          ('heatdeg2',             'REAL'),
          ('heatdeg3',             'REAL'),
          ('heatdeg4',             'REAL'),
          ('heatdeg5',             'REAL'),
          ('heatdeg6',             'REAL'),
          ('heatdeg7',             'REAL'),
          ('heatdeg8',             'REAL'),
          ('cooldeg0',             'REAL'),
          ('cooldeg1',             'REAL'),
          ('cooldeg2',             'REAL'),
          ('cooldeg3',             'REAL'),
          ('cooldeg4',             'REAL'),
          ('cooldeg5',             'REAL'),
          ('cooldeg6',             'REAL'),
          ('cooldeg7',             'REAL'),
          ('cooldeg8',             'REAL'),
          ('homedeg0',             'REAL'),
          ('homedeg1',             'REAL'),
          ('homedeg2',             'REAL'),
          ('homedeg3',             'REAL'),
          ('homedeg4',             'REAL'),
          ('homedeg5',             'REAL'),
          ('homedeg6',             'REAL'),
          ('homedeg7',             'REAL'),
          ('homedeg8',             'REAL'),
]

# Schema to be used for the daily summaries. The default is to include all the observation types in the table as
# 'scalar' types, plus one for 'wind' as a vector type.
day_summaries = [(e[0], 'scalar') for e in table if e[0] not in ('dateTime', 'usUnits', 'interval')]\
                + [('wind', 'vector')]

schema = {
    'table': table,
    'day_summaries' : day_summaries
}
