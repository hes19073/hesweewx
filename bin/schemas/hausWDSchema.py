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
hauswd_schema = [
    ('dateTime',     'INTEGER NOT NULL UNIQUE PRIMARY KEY'),
    ('usUnits',      'INTEGER NOT NULL'),
    ('interval',     'INTEGER NOT NULL'),
    ('gas_m3',       'REAL'),
    ('gas_kWh',      'REAL'),
    ('gas_preis',    'REAL'),
    ('ele_kWh',      'REAL'),
    ('ele_preis',    'REAL'),
    ('eleA_kWh',     'REAL'),
    ('eleA_preis',   'REAL'),
    ('was_m3',       'REAL'),
    ('was_preis',    'REAL'),
    ('wasA_m3',      'REAL'),
    ('wasA_preis',   'REAL'),
    ('gasZ_m3',      'REAL'),
    ('gasZ_kWh',     'REAL'),
    ('gasZ_preis',   'REAL'),
    ('eleZ_kWh',     'REAL'),
    ('eleZ_preis',   'REAL'),
    ('eleAZ_kWh',    'REAL'),
    ('eleAZ_preis',  'REAL'),
    ('wasG_preis',   'REAL'),
    ('wasZ_m3',      'REAL'),
    ('wasZ_preis',   'REAL'),
    ('wasAZ_m3',     'REAL'),
    ('wasAZ_preis',  'REAL'),
    ('gasZahl',      'REAL'),
    ('eleZahl',      'REAL'),
    ('eleAZahl',     'REAL'),
    ('wasZahl',      'REAL'),
    ('wasAZahl',     'REAL'),
    ]


