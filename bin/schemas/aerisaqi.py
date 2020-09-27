#
#    Copyright (c) 2009-2020 Tom Keffer <tkeffer@gmail.com>
#
#    See the file LICENSE.txt for your rights.
#
"""The extended wview schema."""

# =============================================================================
# This is a list containing the default schema of the archive database.  It is
# only used for initialization --- afterwards, the schema is obtained
# dynamically from the database.  Although a type may be listed here, it may
# not necessarily be supported by your weather station hardware.
# =============================================================================
# NB: This schema is specified using the WeeWX V4 "new-style" schema.
# =============================================================================
schema = [
    ('dateTime', 'INTEGER NOT NULL PRIMARY KEY'),
    ('usUnits', 'INTEGER NOT NULL'),
    ('interval', 'INTEGER NOT NULL'),
    ('aqi', 'INTEGER'),
    ('o3','REAL'),
    ('co','REAL'),
    ('no2', 'REAL'),
    ('so2', 'REAL'),
    ('pm25', 'REAL'),
    ('pm10', 'REAL'),
    ]


#day_summaries = [(e[0], 'scalar') for e in table
#                 if e[0] not in ('dateTime', 'usUnits', 'interval')]

#schema = {
#    'table': table,
#    'day_summaries' : day_summaries
#}

