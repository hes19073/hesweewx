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
    ('distance', 'REAL'),
    ('strikes', 'REAL'),
    ('energy', 'REAL'),
    ('lightning_strikes', 'REAL'),
    ('avg_distance', 'REAL'),
    ]

