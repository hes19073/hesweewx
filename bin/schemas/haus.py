#
#    Copyright (c) 2011 Tom Keffer <tkeffer@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#
#    $Revision: 1459 $
#    $Author: mwall $
#    $Date: 2013-10-08 17:44:50 -0700 (Tue, 08 Oct 2013) $
#
"""Database schemas used by weewx"""

#===============================================================================
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
schema = [('dateTime',             'INTEGER NOT NULL UNIQUE PRIMARY KEY'),
                        ('usUnits',              'INTEGER NOT NULL'),
                        ('interval',             'INTEGER NOT NULL'),
                        ('extraTemp1',           'REAL'),
                        ('extraTemp2',           'REAL'),
                        ('extraTemp3',           'REAL'),
                        ('extraTemp4',           'REAL'),
                        ('extraTemp5',           'REAL'),
                        ('extraTemp6',           'REAL'),
                        ('extraTemp7',           'REAL'),
                        ('extraTemp8',           'REAL'),
                        ('extraTemp9',           'REAL'),
                        ('extraTemp10',           'REAL'),
                        ('extraTemp11',           'REAL'),
                        ('extraTemp12',           'REAL'),
                        ('extraTemp13',           'REAL'),
                        ('extraTemp14',           'REAL'),
                        ('extraTemp15',           'REAL'),
                        ('extraTemp16',           'REAL'),
                        ('extraTemp17',           'REAL'),
                        ('extraTemp18',           'REAL'),
                        ('extraTemp19',           'REAL'),
                        ('extraTemp20',           'REAL'),
                        ('extraTemp21',           'REAL'),
                        ('extraTemp22',           'REAL'),
                        ('extraTemp23',           'REAL'),
                        ('extraTemp24',           'REAL'),
                        ('extraHumid1',          'REAL'),
                        ('extraHumid2',          'REAL'),
                        ('rxCheckPercent',       'REAL'),
                        ('txBatteryStatus',      'REAL'),
                        ('consBatteryVoltage',   'REAL'),
                        ('heatingVoltage',       'REAL'),
                        ('supplyVoltage',        'REAL'),
                        ('referenceVoltage',     'REAL'),
                        ('windBatteryStatus',    'REAL'),
                        ('rainBatteryStatus',    'REAL'),
                        ('outTempBatteryStatus', 'REAL'),
                        ('inTempBatteryStatus',  'REAL'),
                        ('gas',                  'REAL'),
                        ('gasTotal',             'REAL'),
                        ('gasZahl',              'REAL'),
                        ('gasDelta',             'REAL'),
                        ('ele',                  'REAL'),
                        ('eleTotal',             'REAL'),
                        ('eleZahl',              'REAL'),
                        ('eleDelta',             'REAL'),
                        ('eleA',                 'REAL'),
                        ('eleATotal',            'REAL'),
                        ('eleAZahl',             'REAL'),
                        ('eleADelta',            'REAL'),
                        ('was',                  'REAL'),
                        ('wasTotal',             'REAL'),
                        ('wasZahl',              'REAL'),
                        ('wasDelta',             'REAL'),
                        ('wasA',                 'REAL'),
                        ('wasATotal',            'REAL'),
                        ('wasAZahl',             'REAL'),
                        ('wasADelta',            'REAL'),
                        ('elePV',                'REAL'),
                        ('elePVTotal',           'REAL'),
                        ('elePVZahl',            'REAL'),
                        ('elePVDelta',           'REAL'),
]


