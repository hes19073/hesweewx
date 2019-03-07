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
          ('yyyymmdd',             'REAL'),
          ('yyyymmddhh',           'REAL'),
          ('windGust_m_s',         'REAL'),
          ('windGust',             'REAL'),
          ('windSpeed_m_s',        'REAL'),
          ('windSpeed',            'REAL'),
          ('rain',                 'REAL'),
          ('solarShineS',          'REAL'),
          ('snow',                 'REAL'),
          ('cloud',                'REAL'),
          ('Dampfdruck_hpa',       'REAL'),
          ('pressure',             'REAL'),
          ('outTemp',              'REAL'),
          ('outHumidity',          'REAL'),
          ('outTempMax',           'REAL'),
          ('outTempMin',           'REAL'),
          ('temp5cm',              'REAL'),
          ('barometer',            'REAL'),
          ('dewpoint',             'REAL'),
          ('windDir',              'REAL'),
          ('windchill',            'REAL'),
          ('heatindex',            'REAL')]
