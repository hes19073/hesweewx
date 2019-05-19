#!/usr/bin/env python
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT 
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# Version: 1.2.1                                  Date: 15 May 2019
#
# Revision History
#  05 September 2015  v1.2.0    - Initial implementation, based upon portions of
#                                 weewxwd3.py
#
"""Manage the databases used by Weewx-WD"""
from __future__ import with_statement

import optparse
import os.path
import sys
import syslog
import time

from datetime import date, timedelta


# Find the install bin subdirectory:
this_file = os.path.join(os.getcwd(), __file__)
this_dir = os.path.abspath(os.path.dirname(this_file))
bin_dir = os.path.abspath(os.path.join(this_dir, os.pardir))

# Now that we've found the bin subdirectory, inject it into the path:
sys.path.insert(0, bin_dir)

# Now we can import some weewx modules
import weewx
VERSION = weewx.__version__
import user.extensions      #@UnusedImport
import weedb
import weewx.manager
import weewx.units
import weecfg
import weewx
import weewx.engine
import weewx.wxformulas
import weewx.almanac
from weewx.units import convert, obs_group_dict
from weeutil.weeutil import to_bool, accumulateLeaves
from weeutil.weeutil import timestamp_to_string

# Weewx-WD imports
import user.weewxwd3
#import user.wdSearchX3
#import user.wdAstroSearchX3
#import user.wdTaggedStats3
#import user.imageStackedWindRose3

from user.weewxwd3 import WdGenerateDerived

WEEWXWD_CONFIG_VERSION = '1.2.1'

description = """Manage the Weewx-WD database. This utility performs many of the functions
on the Weewx-WD database that the wee_database utility performs on the weewx
database. Most of these functions are handled automatically by Weewx-WD, but
they may be useful as a utility in special cases. In particular, the
'reconfigure' option can be useful if additional data types are added to or
dropped from the database schema or to change unit systems."""

usage = """weewxwd_config --help
       weewxwd_config --create-archive
            [CONFIG_FILE|--config=CONFIG_FILE]
            [--wd-binding=BINDING_NAME]
       weewxwd_config --drop-daily
            [CONFIG_FILE|--config=CONFIG_FILE]
            [--wd-binding=BINDING_NAME]
       weewxwd_config --backfill-daily
            [CONFIG_FILE|--config=CONFIG_FILE]
            [--wd-binding=BINDING_NAME]
       weewxwd_config --reconfigure
            [CONFIG_FILE|--config=CONFIG_FILE]
            [--wd-binding=BINDING_NAME]
       weewxwd_config --string-check
            [CONFIG_FILE|--config=CONFIG_FILE]
            [--wd-binding=BINDING_NAME] [--fix]
       weewxwd_config --copy-v2-data
            [CONFIG_FILE|--config=CONFIG_FILE]
            [--wx-binding=BINDING_NAME]
            [--wd-binding=BINDING_NAME]
       weewxwd_config --clear-v2-data
            [CONFIG_FILE|--config=CONFIG_FILE]
            [--wx-binding=BINDING_NAME]
            [--wd-binding=BINDING_NAME]
       weewxwd_config --version
       weewxwd_config --status
"""

epilog = """If you are using a MySQL database it is assumed that you have the
appropriate permissions for the requested operation."""

def main():

    # Set defaults for the system logger:
    syslog.openlog('weewxwd', syslog.LOG_PID|syslog.LOG_CONS)

    # Create a command line parser:
    parser = optparse.OptionParser(description=description, usage=usage, epilog=epilog)
    
    # Add the various options:
    parser.add_option("--create-archive", dest="create_archive", action='store_true',
                      help="Create the Weewx-WD archive database.")
    parser.add_option("--drop-daily", dest="drop_daily", action='store_true',
                      help="Drop the Weewx-WD daily summary tables.")
    parser.add_option('--backfill-daily', dest='backfill_daily', action='store_true',
                      help='Backfill Weewx-WD daily summary tables from Weewx-WD archive.')
    parser.add_option("--reconfigure", dest="reconfigure", action='store_true',
                      help="Create a new Weewx-WD archive database using configuration information found "
                      "in the configuration file. In particular, the new database will use the unit "
                      "system found in option [StdConvert][target_unit]. The new database will have "
                      "the same name as the old database, with a '_new' on the end.")
    parser.add_option("--string-check", dest="string_check", action="store_true",
                      help="Check a sqlite version of the Weewx-WD database to "
                      "see whether it contains embedded strings.")
    parser.add_option("--copy-v2-data", dest="copy_v2", action='store_true',
                      help="Copy historical Weewx-WD observation data from Weewx archive to Weewx-WD archive.")
    parser.add_option("--clear-v2-data", dest="clear_v2", action='store_true',
                      help="Clear historical Weewx-WD data from Weewx (not Weewx-WD) archive. NOTE: This option will irreversibly clear all data stored in the 'extraTemp1' and 'extraTemp2' fields in the Weewx (not Weewx-WD) archive.")
    parser.add_option('--version', dest='version', action='store_true',
                      help='Display Weewx-WD executable file versions.')
    parser.add_option('--status', dest='status', action='store_true',
                      help='Display Weewx-WD archive status.')
    parser.add_option('--config', dest='config_path', type=str, metavar="CONFIG_PATH",
                      help="Use configuration file CONFIG_PATH. Default is /etc/weewx/weewx.conf or /home/weewx/weewx.conf.")
    parser.add_option("--wx-binding", dest="wxbinding", metavar="WX_BINDING_NAME",
                      default='wx_binding',
                      help="The weewx data binding. Default is 'wx_binding'.")
    parser.add_option("--wd-binding", dest="wdbinding", metavar="WD_BINDING_NAME",
                      default='wd_binding',
                      help="The Weewx-WD data binding. Default is 'wd_binding'.")
    parser.add_option("--fix", dest="fix", action="store_true",
                      help="Fix any embedded strings in a sqlite database.")

    # Now we are ready to parse the command line:
    (options, args) = parser.parse_args()

    if options.version:
        print "Weewx-WD weewxwd_config version:             %s" % WEEWXWD_CONFIG_VERSION
        print "Weewx-WD weewxwd version:                    %s" % user.weewxwd3.WEEWXWD_VERSION
        print "Weewx-WD SLE version:                        %s" % user.wdSearchX3.WEEWXWD_SLE_VERSION
        print "Weewx-WD Astronomical SLE version:           %s" % user.wdAstroSearchX3.WEEWXWD_ASTRO_SLE_VERSION
        print "Weewx-WD Tagged Statistics version:          %s" % user.wdTaggedStats3.WEEWXWD_TAGGED_STATS_VERSION
        print "Weewx-WD Stacked Windrose Generator version: %s" % user.imageStackedWindRose3.WEEWXWD_STACKED_WINDROSE_VERSION
        exit(1)

    config_path, config_dict = weecfg.read_config(options.config_path, args)
    print "Using configuration file %s" % config_path
    
    db_binding_wd, db_binding_wx = get_bindings(config_dict)
    db_binding_wx = options.wxbinding
    db_binding_wd = options.wdbinding
    database_wx = config_dict['DataBindings'][db_binding_wx]['database']
    database_wd = config_dict['DataBindings'][db_binding_wd]['database']
    print "Using database binding '%s', which is bound to database '%s'" % (db_binding_wx, database_wx)
    print "Using database binding '%s', which is bound to database '%s'" % (db_binding_wd, database_wd)
    
    if options.status:
        print_status(config_dict, db_binding_wd, db_binding_wx)
        exit(1)

    if options.create_archive:
        createMainDatabase(config_dict, db_binding_wd)
    
    if options.reconfigure:
        reconfigMainDatabase(config_dict, db_binding_wd)

    if options.drop_daily:
        dropDaily(config_dict, db_binding_wd)
        
    if options.backfill_daily:
        backfillDaily(config_dict, db_binding_wd)

    if options.string_check:
        string_check(config_dict, db_binding_wd, options.fix)
    
    if options.copy_v2:
        copy_v2_data(config_dict, db_binding_wd, db_binding_wx)
        exit(1)

    if options.clear_v2:
        clear_v2_data(config_dict, db_binding_wx)
        exit(1)

def createMainDatabase(config_dict, db_binding):
    """Create a weewx archive database"""

    # Try a simple open. If it succeeds, that means the database
    # exists and is initialized. Otherwise, an exception will be thrown.
    try:
        with weewx.manager.open_manager_with_config(config_dict, db_binding) as dbmanager:
            print "Database '%s' already exists. Nothing done." % (dbmanager.database_name,)
    except weedb.OperationalError:
        # Database does not exist. Try again, but allow initialization:
        with weewx.manager.open_manager_with_config(config_dict, db_binding, initialize=True) as dbmanager:
            print "Created database '%s'" % (dbmanager.database_name,)

def dropDaily(config_dict, db_binding):
    """Drop the daily summaries from a weewx database"""
    
    manager_dict = weewx.manager.get_manager_dict(config_dict['DataBindings'], 
                                                  config_dict['Databases'], 
                                                  db_binding)
    database_name = manager_dict['database_dict']['database_name']

    ans = None
    while ans not in ['y', 'n']:
        print "Proceeding will delete all your daily summaries from database '%s'" % database_name
        ans = raw_input("Are you sure you want to proceed (y/n)? ")
        if ans == 'y' :
            
            print "Dropping daily summary tables from '%s' ... " % (database_name,)
            try:
                with weewx.manager.open_manager_with_config(config_dict, db_binding) as dbmanager:
                    try:
                        dbmanager.drop_daily()
                    except weedb.OperationalError, e:
                        print "Got error '%s'\nPerhaps there was no daily summary?" % e
                    else:
                        print "Dropped daily summary tables from database '%s'" % (database_name,)
            except weedb.OperationalError:
                # No daily summaries. Nothing to be done.
                print "No daily summaries found in database '%s'. Nothing done." % (database_name,)
    
def backfillDaily(config_dict, db_binding):
    """Backfill the daily summaries"""

    manager_dict = weewx.manager.get_manager_dict(config_dict['DataBindings'], 
                                                  config_dict['Databases'], 
                                                  db_binding)
    database_name = manager_dict['database_dict']['database_name']

    print "Backfilling daily summaries in database '%s'" % database_name

    t1 = time.time()
    # Open up the archive. This will create the tables necessary for the daily summaries if they
    # don't already exist:
    with weewx.manager.open_manager_with_config(config_dict, db_binding, initialize=True) as dbmanager:
        nrecs, ndays = dbmanager.backfill_day_summary()
    tdiff = time.time() - t1
    
    if nrecs:
        print "Backfilled '%s' with %d records over %d days in %.2f seconds" % (database_name, nrecs, ndays, tdiff)
    else:
        print "Daily summaries up to date in '%s'." % database_name
    
def reconfigMainDatabase(config_dict, db_binding):
    """Create a new database, then populate it with the contents of an old database"""

    manager_dict = weewx.manager.get_manager_dict_from_config(config_dict, 
                                                              db_binding)
    # Make a copy for the new database (we will be modifying it)
    new_database_dict = dict(manager_dict['database_dict'])
    
    # Now modify the database name
    new_database_dict['database_name'] = manager_dict['database_dict']['database_name']+'_new'

    # First check and see if the new database already exists. If it does, check
    # with the user whether it's ok to delete it.
    try:
        weedb.create(new_database_dict)
    except weedb.DatabaseExists:
        ans = None
        while ans not in ['y', 'n']:
            ans = raw_input("New database '%s' already exists. Delete it first (y/n)? " % (new_database_dict['database_name'],))
            if ans == 'y':
                weedb.drop(new_database_dict)
            elif ans == 'n':
                print "Nothing done."
                return

    # Get the unit system of the old archive:
    with weewx.manager.Manager.open(manager_dict['database_dict']) as old_dbmanager:
        old_unit_system = old_dbmanager.std_unit_system
    
    # Get the unit system of the new archive:
    try:
        target_unit_nickname = config_dict['StdConvert']['target_unit']
    except KeyError:
        target_unit_system = None
    else:
        target_unit_system = weewx.units.unit_constants[target_unit_nickname.upper()]
        
        
    ans = None
    while ans not in ['y', 'n']:
        print "Copying Weewx-WD archive database '%s' to '%s'" % (manager_dict['database_dict']['database_name'], new_database_dict['database_name'])
        if target_unit_system is None or old_unit_system==target_unit_system:
            print "The new archive will use the same unit system as the old ('%s')." % (weewx.units.unit_nicknames[old_unit_system],)
        else:
            print "Units will be converted from the '%s' system to the '%s' system." % (weewx.units.unit_nicknames[old_unit_system], 
                                                                                        weewx.units.unit_nicknames[target_unit_system])
        ans = raw_input("Are you sure you wish to proceed (y/n)? ")
        if ans == 'y':
            weewx.manager.reconfig(manager_dict['database_dict'],
                                   new_database_dict, 
                                   new_unit_system=target_unit_system,
                                   new_schema=manager_dict['schema'])
            print "Done."
        elif ans == 'n':
            print "Nothing done."

def print_status(config_dict, db_binding_wd, db_binding_wx):
    """ Display brief status information on whether or not reconstruction of any
        Weewx-WD archive data is required.

        The installation of the Weewx-WD extension does not in itself
        reconstruct any earlier Weewx-WD data that was previously kept in the
        Weewx archive. A simple check is conducted of the earliest and
        latest timestamps in the Weewx-WD archive that hold Weewx-WD data.
        These times are compared against the earliest and latest timestamps
        in the Weewx archive.

        Parameters:
            config_dict: a dictionary of the weewx.conf settings
            db_binding_wd: binding for Weewx-WD database
            db_binding_wx: binding for Weewx database

        Returns:
            Nothing.
    """

    manager_dict = weewx.manager.get_manager_dict(config_dict['DataBindings'],
                                                  config_dict['Databases'],
                                                  db_binding_wd)
    database_name = manager_dict['database_dict']['database_name']
    with weewx.manager.open_manager_with_config(config_dict, db_binding_wd) as dbmanager_wd:
        with weewx.manager.open_manager_with_config(config_dict, db_binding_wx) as dbmanager_wx:

            earliest_wd_ts = None
            latest_wd_ts = None
            table_name = dbmanager_wd.table_name

            # find earliest and latest Weewx-WD archive timestamps that hold valid data
            _row = dbmanager_wd.getSql("SELECT MIN(dateTime), MAX(dateTime) FROM %s WHERE humidex IS NOT NULL AND appTemp IS NOT NULL" % table_name)
            if _row:
                # we have an answer
                earliest_wd_ts = _row[0]
                latest_wd_ts = _row[1]

            # get our first and last good timestamps from Weewx archive
            earliest_wx_ts = dbmanager_wx.firstGoodStamp()
            latest_wx_ts = dbmanager_wx.lastGoodStamp()

            if earliest_wd_ts is None or latest_wd_ts is None:
                # no Weewx-WD data, reconstruct the lot if available
                if earliest_wx_ts is not None and latest_wx_ts is not None:
                    # data available so say so
                    print "Reconstruction of Weewx-WD database '%s' table '%s' data from %s to %s (approx %d days) is recommended." % (database_name, table_name, timestamp_to_string(earliest_wx_ts), timestamp_to_string(latest_wx_ts), int((latest_wx_ts - earliest_wx_ts)/86400) + 1)
                else:
                    # no data with which to reconstruct
                    print "Reconstruction of Weewx-WD database '%s' table '%s' is not required" % (database_name, table_name)
            elif earliest_wx_ts is not None and latest_wx_ts is not None:
                # some Weewx-WD data available and we also have some Weewx data
                # check if we need to reconstruct
                if earliest_wd_ts > earliest_wx_ts:
                    # we have 'before' data to reconstruct
                    print "Reconstruction of Weewx-WD database '%s' table '%s' data from %s to %s (approx %d days) is recommended." % (database_name, table_name, timestamp_to_string(earliest_wx_ts), timestamp_to_string(earliest_wd_ts), int((earliest_wd_ts - earliest_wx_ts)/86400) + 1)
                elif latest_wd_ts < latest_wx_ts:
                    # we have 'after' data to reconstruct
                    print "Reconstruction of Weewx-WD database '%s' table '%s' data from %s to %s (approx %d days) is recommended." % (database_name, table_name, timestamp_to_string(latest_wd_ts), timestamp_to_string(latest_wx_ts), int((latest_wx_ts - latest_wd_ts)/86400) + 1)
                else:
                    # no data with which to reconstruct so say so
                    print "Reconstruction of Weewx-WD database '%s' table '%s' is not required" % (database_name, table_name)
            else:
                # no data with which to reconstruct so say so
                print "Reconstruction of Weewx-WD database '%s' table '%s' is not required" % (database_name, table_name)

def string_check(config_dict, db_binding, fix=False):
    
    print "Checking Weewx-WD archive database for strings..."
    found_problem = False

    # Open up the main database archive
    with weewx.manager.open_manager_with_config(config_dict, db_binding) as dbmanager:
        
        obs_pytype_list = []
        obs_list = []
        
        # Get the schema and extract the Python type each observation type should be
        for column in dbmanager.connection.genSchemaOf('archive'):
            schema_type = column[2]
            if schema_type == 'INTEGER':
                schema_type = int
            elif schema_type == 'REAL':
                schema_type = float
            elif schema_type == 'STR':
                schema_type = str
            # Save the observation type for this column (eg, 'outTemp'):
            obs_list.append(column[1])
            # Save the Python type for this column (eg, 'int'):
            obs_pytype_list.append(schema_type)
        
        # Cycle through each row in the database
        for record in dbmanager.genBatchRows():
            # Now examine each column
            for icol in range(len(record)):
                # Check to see if this column is an instance of the correct Python type
                if record[icol] is not None and not isinstance(record[icol], obs_pytype_list[icol]):
                    # Oops. Found a bad one. Print it out
                    sys.stdout.write("Timestamp = %s; record['%s']= %r; ... " % (record[0], obs_list[icol], record[icol]))
                    found_problem = True
                    
                    if fix:
                        # Cooerce to the correct type. If it can't be done, then set it to None
                        try:
                            corrected_value = obs_pytype_list[icol](record[icol])
                        except ValueError:
                            corrected_value = None
                        # Update the database with the new value
                        dbmanager.updateValue(record[0], obs_list[icol], corrected_value)
                        # Inform the user
                        sys.stdout.write("changed to %r\n" % corrected_value)
                    else:
                        sys.stdout.write("ignored.\n")
        # Print out a message if nothing was found
        if not found_problem:
            print "Check complete. No embedded strings found."
                    
def copy_v2_data(config_dict, db_binding_wd, db_binding_wx):
    """ Copy legacy Weewx-WD derived obs from a Weewx archive.
    
        Does a simple check of the first and last valid timestamps in 
        Weewx-WD and Weewx archives to identify any Weewx-WD missing data 
        timespans. The check is simple and only identifies missing data 
        before the first and after the last valid Weewx-WD timestamps. 
        Missing data between these timestamps will not be identified and 
        copied. 

        Parameters:
            config_dict: a dictionary of the weewx.conf settings
            db_binding_wd: binding for Weewx-WD database
            db_binding_wx: binding for Weewx database
            
        Returns:
            Nothing.
    """
    
    t1 = time.time()
    
    with weewx.manager.open_manager_with_config(config_dict, db_binding_wd) as dbmanager_wd:
        with weewx.manager.open_manager_with_config(config_dict, db_binding_wx) as dbmanager_wx:
    
            # get the spans of any records we need to insert both:
            # - before the start of our Weewx-WD database, and
            # - after the end of our Weewx-WD database
            before_span, after_span = get_backfill_spans(dbmanager_wd, dbmanager_wx)
            before_start_ts, before_stop_ts, after_start_ts, after_stop_ts = before_span + after_span
            
            # do the backfill noting numbers of records, days and periods we have 
            # dealt with
            nrecs_b = None
            ndays_b = 0
            nrecs_a = None
            ndays_a = 0
            nperiods = 0
            if before_start_ts is not None and before_stop_ts is not None:
                nrecs_b, ndays_b = backfill_wd(dbmanager_wd, dbmanager_wx, before_start_ts - 1, before_stop_ts - 1)
                if nrecs_b is not None:
                    nperiods += 1 if nrecs_b > 0 else nperiods
            if after_start_ts is not None and after_stop_ts is not None:
                nrecs_a, ndays_a = backfill_wd(dbmanager_wd, dbmanager_wx, after_start_ts, after_stop_ts)
                if nrecs_a is not None:
                    nperiods += 1 if nrecs_a > 0 else nperiods
            
            tdiff = time.time() - t1
            # informational statement on what we did/did not do
            nrecs = sum(filter(None, (nrecs_b, nrecs_a)))
            if nperiods > 0:
                print "%d record(s) over %d period(s) covering approximately %d day(s) processed in %s." % (nrecs, nperiods, ndays_b + ndays_a, str(timedelta(seconds=int(tdiff))))
            else:
                print "No records processed."

def clear_v2_data(config_dict, db_binding_wx):
    """ Clear any legacy humidex and apparent temperature data from the 
        Weewx (not Weewx-WD) database.
    
        Under Weewx v2.x Weewx-WD stored humidex and apparent temperature 
        data in the Weewx archive in fields extraTemp1 and extratemp2 
        respectively. Under Weewx v3 Weewx-WD now stores this data in a 
        separate database and hence this legacy data can be removed from 
        the Weewx database.

        Parameters:
            config_dict: a dictionary of the weewx.conf settings
            db_binding_wx: binding for Weewx database
            
        Returns:
            Nothing.
    """
    
    manager_dict = weewx.manager.get_manager_dict(config_dict['DataBindings'], 
                                                  config_dict['Databases'], 
                                                  db_binding_wx)
    database_name = manager_dict['database_dict']['database_name']
    with weewx.manager.open_manager_with_config(config_dict, db_binding_wx) as dbmanager_wx:
    
        # get our first and last good timestamps
        start_ts = dbmanager_wx.firstGoodStamp()
        stop_ts = dbmanager_wx.lastGoodStamp()
        
        # do we actually have any extraTemp1 and extraTemp2 fields with data in them?
        #_row = dbmanager_wx.getSql("SELECT COUNT(windrun) FROM %s" % dbmanager_wx.table_name)
        _row = dbmanager_wx.getSql("SELECT COUNT(outTemp), COUNT(outHumidity) FROM %s" % dbmanager_wx.table_name)
        print "datebase of row %s" % (_row)
        if _row:
            # we have an answer
            if _row[0] > 0 or _row[1] >0:
                # we do have some fields to clear so clear them
                
                # set some counters
                nrecs = 0
                ndays = (date.fromtimestamp(stop_ts) -  date.fromtimestamp(start_ts)).days
                
                # confirm we still want to do this
                print "'extraTemp1' and 'extraTemp2' data in database '%s' from %s to %s (approx %d days) is about to be cleared. Any data in these fields will be irretrievably lost." % (database_name, timestamp_to_string(start_ts), timestamp_to_string(stop_ts), ndays)
                ans = None
                ans = raw_input("Are you sure you wish to proceed (y/n)? ")
                if ans == 'y':
                    # we do so go ahead and clear them
                    for _rec in dbmanager_wx.genBatchRecords(start_ts - 1, stop_ts):

                        #msr = weewx.wxformulas.solar_rad_Bras(53.605963, 11.341407, 53, _rec['dateTime'], 2)
                        #dbmanager_wx.updateValue(_rec['dateTime'], 'maxSolarRad', msr) 

                        #if _rec['outTemp'] <> 0 and _rec['outHumidity'] <> 0:
                        #    cb1 = weewx.wxformulas.cloudbase_Metric(_rec['outTemp'], _rec['outHumidity'], 53)
                        #else:
                        #    cb1 = 0
                        #dbmanager_wx.updateValue(_rec['dateTime'], 'cloudbase', cb1)

                        #if _rec['windSpeed'] > 0:
                        #    be2 = _rec['windSpeed'] * 5.0 / 60.0
                        #else:
                        #    be2 = 0.0
                        #dbmanager_wx.updateValue(_rec['dateTime'], 'windrun', be2)

                        #if _rec['outTemp'] <> 0 and _rec['outHumidity'] <> 0:
                        #    hu1 = weewx.wxformulas.absF_C(_rec['outTemp'], _rec['outHumidity'])
                        #else:
                        #    hu1 = 0
                        #dbmanager_wx.updateValue(_rec['dateTime'], 'absolutF', hu1)

                        #if _rec['outTemp'] <> 0 and _rec['outHumidity'] <> 0:
                        #    ssI = weewx.wxformulas.sumsimIndex_C(_rec['outTemp'], _rec['outHumidity'])
                        #else:
                        #    ssI = 0
                        #dbmanager_wx.updateValue(_rec['dateTime'], 'summersimmerIndex', ssI)

                        """ test aus altem
                        if _rec['outTemp'] <> 0 and _rec['outHumidity'] <> 0 and _rec['windSpeed'] <> 0:
                            ap1 = weewx.wxformulas.apptempC(_rec['outTemp'], _rec['outHumidity'], _rec['windSpeed'])
                        else:
                            ap1 = 0
                        dbmanager_wx.updateValue(_rec['dateTime'], 'appTemp', ap1)

                        if _rec['inTemp'] <> 0 and _rec['inHumidity'] <> 0:
                            dp1 = weewx.wxformulas.dewpointC(_rec['inTemp'], _rec['inHumidity'])
                        else:
                            dp1 = 0
                        dbmanager_wx.updateValue(_rec['dateTime'], 'inDewpoint', dp1)

                        if _rec['radiation'] <> 0:
                            sunS = weewx.wxformulas.sunhes(_rec['radiation'], _rec['dateTime'])
                        else:
                            sunS = 0.0
                        dbmanager_wx.updateValue(_rec['dateTime'], 'sunshineS', sunS)

                        if _rec['outTemp'] <> 0 and _rec['outHumidity'] <> 0 and _rec['pressure'] <> 0:
                            we1 = weewx.wxformulas.wetbulb_Metric(_rec['outTemp'], _rec['outHumidity'],
                                                                  _rec['pressure'])
                        else:
                            we1 = 0
                        dbmanager_wx.updateValue(_rec['dateTime'], 'wetBulb', we1)

                        if _rec['outTemp'] <> 0 and _rec['outHumidity'] <> 0:
                            cbI = weewx.wxformulas.cbindex_Metric(_rec['outTemp'], _rec['outHumidity'])
                        else:
                            cbI = 0.0
                        dbmanager_wx.updateValue(_rec['dateTime'], 'cbIndex', cbI)

                        if _rec['outTemp'] <> 0 and _rec['dewpoint'] <> 0 and _rec['pressure'] <> 0:
                            ai1 = weewx.wxformulas.density_Metric(_rec['dewpoint'], _rec['outTemp'],
                                                                  _rec['pressure'])
                        else:
                            ai1 = 0
                        dbmanager_wx.updateValue(_rec['dateTime'], 'airDensity', ai1)

                        if _rec['outTemp'] <> 0 and _rec['dewpoint'] <> 0 and _rec['pressure'] <> 0 and _rec['windSpeed'] <> 0:
                            wi1 = weewx.wxformulas.winddruck_Metric(_rec['dewpoint'], _rec['outTemp'],
                                                                    _rec['pressure'], _rec['windSpeed'])
                        else:
                            wi1 = 0
                        dbmanager_wx.updateValue(_rec['dateTime'], 'windDruck', wi1)


                        if _rec['outTemp'] <> 0:
                            hdg = weewx.wxformulas.heating_degrees(_rec['outTemp'], 18.333)
                        else:
                            hdg = None

                        dbmanager_wx.updateValue(_rec['dateTime'], 'heatdeg', hdg)

                        if _rec['outTemp'] <> 0:
                            cdg = weewx.wxformulas.cooling_degrees(_rec['outTemp'], 18.333)
                        else:
                            cdg = None

                        dbmanager_wx.updateValue(_rec['dateTime'], 'cooldeg', cdg)

                        if _rec['outTemp'] <> 0:
                            odg = weewx.wxformulas.cooling_degrees(_rec['outTemp'], 15.0)
                        else:
                            odg = None

                        dbmanager_wx.updateValue(_rec['dateTime'], 'homedeg', odg)

                        if _rec['outTemp'] <> None:
                            svp = weewx.uwxutils.TWxUtils.SaturationVaporPressure(_rec['outTemp'])
                        else:
                            svp = None

                        dbmanager_wx.updateValue(_rec['dateTime'], 'SVP', svp)

                        if _rec['inTemp'] <> None:
                            svpin = weewx.uwxutils.TWxUtils.SaturationVaporPressure(_rec['inTemp'])
                        else:
                            svpin = None

                        dbmanager_wx.updateValue(_rec['dateTime'], 'SVPin', svpin)

                        if _rec['outTemp'] <> None and _rec['outHumidity'] <> None:
                            avp = _rec['outHumidity'] * (weewx.uwxutils.TWxUtils.SaturationVaporPressure(_rec['outTemp'])) / 100.0
                        else:
                            avp = None

                        dbmanager_wx.updateValue(_rec['dateTime'], 'AVP', avp)
        
                        if _rec['inTemp'] <> None and _rec['inHumidity'] <> None:
                           avpin = _rec['inHumidity'] * (weewx.uwxutils.TWxUtils.SaturationVaporPressure(_rec['inTemp'])) / 100.0
                        else:
                           avpin = None

                        dbmanager_wx.updateValue(_rec['dateTime'], 'AVPin', avpin)"""

                        if _rec['outTemp'] is None or _rec['outHumidity'] is None or _rec['radiation'] is None or _rec['windSpeed'] is None:
                            et1 = 0.0
                        else:
                            et1 = weewx.wxformulas.evapotranspiration_Metric(_rec['outTemp'], _rec['outTemp'],
                                                                            _rec['outHumidity'], _rec['outHumidity'],
                                                                            _rec['radiation'], _rec['windSpeed'],
                                                                            10.6, 53.6059563, 11.341407, 53.6, _rec['dateTime'])

                        dbmanager_wx.updateValue(_rec['dateTime'], 'ET', et1)


                        """ Muster original
                        #dbmanager_wx.updateValue(_rec['dateTime'], 'extraTemp1', None)
                        #dbmanager_wx.updateValue(_rec['dateTime'], 'extraTemp2', None)
                        achtung loescht die eintraege in extraTemp1 und extratTemp2 aus der Datenbank wx """

                        nrecs += 1
                    dbmanager_wx.connection.commit()
                    # all done, say so and give some stats
                    print "Done. 'extraTemp1' and 'extraTemp2' cleared in %d records (approx %d days)." %(nrecs, ndays)
                elif ans == 'n':
                    # we backed out so say so
                    print "Action cancelled. Nothing done."
            else:
                # no rows need to be cleared
                print "No 'extraTemp1' or 'extraTemp2' data found in database '%s' that need to be cleared. No data changed." % (database_name)
        else:
            # no rows need to be cleared
            print "No 'extraTemp1' or 'extraTemp2' data found in database '%s' that need to be cleared. No data changed." % (database_name)
                
def get_bindings(config_dict):
    """ Get db_bindings for the Weewx-WD and Weewx databases.

        Parameters:
            config_dict: a dictionary of the weewx.conf settings

        Returns:
            db_binding_wd: binding for Weewx-WD database.
            db_binding_wx: binding for Weewx database.
    """

    # Extract our binding from the Weewx-WD section of the config file. If
    # it's missing, fill with a default
    if 'Weewx-WD' in config_dict:
        db_binding_wd = config_dict['Weewx-WD'].get('data_binding', 'wd_binding')
    else:
        db_binding_wd = 'wd_binding'

    # Extract the Weewx binding for use when we check the need for backfill
    # from the Weewx archive
    if 'StdArchive' in config_dict:
        db_binding_wx = config_dict['StdArchive'].get('data_binding', 'wx_binding')
    else:
        db_binding_wx = 'wx_binding'

    return (db_binding_wd, db_binding_wx)

def get_backfill_spans(dbmanager_wd, dbmanager_wx):
    """ Calculate timespans that require backfill of data from Weewx 
        archive to Weewx-WD archive.
        
        If Weewx-WD was installed some time after Weewx was first run
        there will likely be one or more periods of missing data in the
        Weewx-WD archive that is otherwise available from the Weewx 
        archive. This routine takes a simplistic approach to determining 
        these timespans as follows:
        - first good timestamp in Weewx archive to first good timestamp in 
          Weewx-WD archive
        - last good timestamp in Weewx-WD archive to last good timestamp in 
          Weewx archive
        - if there is no data in the Weewx-WD archive then first good 
          timestamp to last good timestamp in Weewx archive
        - if there is no data in the Weewx archive then a (None, None) 
          timespan is returned for each period
          
        Gaps in the Weewx-WD data are not included in any timespand results.
    
        Parameters:
            dbmanager_wd: Manager object for Weewx-WD database.
            dbmanager_wx: Manager object for Weewx database.
            
        Returns:
            A tuple consisting of two tuples each consisting of a start and 
            stop timestamp. The first tuple represents the timespan of data 
            that is older then the Weewx-WD data. The second tuple 
            represents the timespan of data that is newer than the Weewx-WD 
            data. (None, None) represents no timespan.
    """
    
    # get fist and last good timestamps for each database
    first_wd_ts = dbmanager_wd.firstGoodStamp()
    last_wd_ts = dbmanager_wd.lastGoodStamp()
    first_wx_ts = dbmanager_wx.firstGoodStamp()
    last_wx_ts = dbmanager_wx.lastGoodStamp()
    
    if first_wd_ts is None or last_wd_ts is None:
        # no data in wd
        if first_wx_ts is not None and last_wx_ts is not None:
            # we have data in wx
            return ((first_wx_ts, last_wx_ts), (None, None))
        else:
            # we have no data in wx
            return ((None, None), (None, None))
    else:
        # wd data
        if first_wx_ts is not None and last_wx_ts is not None:
            # we have data in wx
            if first_wx_ts < first_wd_ts:
                #we have 'before' data to add
                before = (first_wx_ts, first_wd_ts)
            else:
                before = (None, None)
            if last_wx_ts > last_wd_ts:
                #we have 'after' data to add
                after = (last_wd_ts, last_wx_ts)
            else:
                after = (None, None)
            return (before, after)
        else:
            # we have no data in wx
            return ((None, None), (None, None))
    
def backfill_wd(dbmanager_wd, dbmanager_wx, start_ts, stop_ts):
    """ Backfill Weewx-WD database with derived obs over a timespan.
        
        Steps through each Weewx record in the timespan extracting 
        humidex/appTemp from extraTemp1/extraTemp2 values if they contain 
        data otherwise humidex/appTemp are calculated and saved in the 
        Weewx-WD database against the original timestamp. Also sets 
        outTempDay and outTempNight such that:
        - outTempDay=outTemp if time is > 06:00 and time is <= 18:00
        - outTempNight=outTemp if time is <= 06:00 and time is > 18:00
        - outTempDay and outTempNight = None at all other times.
        
        Parameters:
            dbmanager_wd: manager object for Weewx-WD database
            dbmanager_wx: manager object for Weewx database
            start_ts:     inclusive timestamp for the start of the timespan
            stop_ts:      inclusive timestamp for the end of the timespan
            
        Returns:
            ndays: the number of days processed
    """
    
    # set up a reference time point
    t1 = time.time()
    
    # set some stats
    nrecs = None
    
    ndays = (date.fromtimestamp(stop_ts) -  date.fromtimestamp(start_ts)).days

    # how many recs do we need to update?
    _row = dbmanager_wx.getSql("SELECT COUNT(dateTime) FROM %s WHERE dateTime >= %s AND dateTime <= %s" % (dbmanager_wx.table_name, start_ts, stop_ts))
    if _row:
        # we have an answer
        nrecs = _row[0] if _row[0] > 0 else None

    # confirm we still want to do this
    print "%d records have been identified to backfill database '%s' from %s to %s (approx %d days). This may take some time (hours) to complete." % (nrecs, dbmanager_wd.database_name, timestamp_to_string(start_ts), timestamp_to_string(stop_ts), ndays)
    ans = None
    ans = raw_input("Are you sure you wish to proceed (y/n)? ")
    if ans == 'y':
        print "Processing %d records..." % (nrecs,)
        # create a generator object that will yield records over our timespan that have had humidex/appTemp added
        # need to be inclusive on the start hence the - 1
        record_generator = WdGenerateDerived(dbmanager_wx.genBatchRecords(start_ts - 1, stop_ts))            
        # now call the addRecord method with our generator object
        # should be much faster than passing addRecord individual records
        dbmanager_wd.addRecord(record_generator)
    else:
        print "Action cancelled. Nothing done."
        # we backed out so set nrecs to None
        nrecs = None
    
    return nrecs, ndays

if __name__=="__main__" :
    main()

