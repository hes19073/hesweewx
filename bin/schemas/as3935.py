#
#
#    See the file LICENSE.txt for your full rights.
#
#     air.py 2766 2015-05-09 02:45:36Z hes $
#
"""The as3935 schema, which is also used by weewx."""

schema = [
    ('dateTime', 'INTEGER NOT NULL PRIMARY KEY'),
    ('usUnits', 'INTEGER NOT NULL'),
    ('interval', 'INTEGER NOT NULL'),
    ('distance', 'REAL'),
    ('strikes', 'REAL'),
    ('energy', 'REAL'),
    ('lightning_strikes', 'REAL'),
    ('avg_distance', 'REAL'),
    ]

# Schema to be used for the daily summaries. The default is to include all the observation types in the table as
# 'scalar' types, plus one for 'wind' as a vector type.
#day_summaries = [(e[0], 'SCALAR') for e in table if e[0] not in ('dateTime', 'usUnits', 'interval')]
#
#schema = {
#    'table': table,
#    'day_summaries' : day_summaries
#}

