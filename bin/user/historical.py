#
#    Copyright (c) 2020 Tom Keffer <tkeffer@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#
"""A WeeWX extension that calculates historical highs, lows for a date, and the times they occurred."""

import datetime

import weedb
import weewx.units
import weewx.xtypes
from weewx.engine import StdService
from weeutil.weeutil import isStartOfDay

VERSION = "0.30"

# We have to add this to the collection of special aggregation types that change the unit. For example, asking for the
# time of a minimum temperature returns something in group_time, not group_temperature.
weewx.units.agg_group['historical_mintime'] = 'group_time'
weewx.units.agg_group['historical_maxtime'] = 'group_time'


class Historical(weewx.xtypes.XType):
    """XTypes extension to calculate historical statistics for days-of-the-year"""

    sql_stmts = {
        'sqlite': {
            'historical_min': "SELECT MIN(`min`) FROM {table}_day_{obs_type} "
                              "WHERE STRFTIME('%m-%d', dateTime,'unixepoch','localtime') = '{month:02d}-{day:02d}';",
            'historical_mintime': "SELECT `mintime` FROM {table}_day_{obs_type} "
                                  "WHERE STRFTIME('%m-%d', dateTime,'unixepoch','localtime') = '{month:02d}-{day:02d}' "
                                  "ORDER BY `min` ASC LIMIT 1;",
            'historical_min_avg': "SELECT AVG(`min`) FROM {table}_day_{obs_type} "
                                  "WHERE STRFTIME('%m-%d', dateTime,'unixepoch','localtime') = '{month:02d}-{day:02d}';",
            'historical_max': "SELECT MAX(`max`) FROM {table}_day_{obs_type} "
                              "WHERE STRFTIME('%m-%d', dateTime,'unixepoch','localtime') = '{month:02d}-{day:02d}';",
            'historical_maxtime': "SELECT `maxtime` FROM {table}_day_{obs_type} "
                                  "WHERE STRFTIME('%m-%d', dateTime,'unixepoch','localtime') = '{month:02d}-{day:02d}' "
                                  "ORDER BY `max` DESC LIMIT 1;",
            'historical_max_avg': "SELECT AVG(`max`) FROM {table}_day_{obs_type} "
                                  "WHERE STRFTIME('%m-%d', dateTime,'unixepoch','localtime') = '{month:02d}-{day:02d}';",
            'historical_avg': "SELECT SUM(`wsum`), SUM(`sumtime`) FROM {table}_day_{obs_type} "
                              "WHERE STRFTIME('%m-%d', dateTime,'unixepoch','localtime') = '{month:02d}-{day:02d}';",
        },
        'mysql': {
            'historical_min': "SELECT MIN(`min`) FROM {table}_day_{obs_type} "
                              "WHERE FROM_UNIXTIME(dateTime, '%%m-%%d') = '{month:02d}-{day:02d}';",
            'historical_mintime': "SELECT `mintime` FROM {table}_day_{obs_type} "
                                  "WHERE FROM_UNIXTIME(dateTime, '%%m-%%d') = '{month:02d}-{day:02d}' "
                                  "ORDER BY `min` ASC, dateTime ASC LIMIT 1;",
            'historical_min_avg': "SELECT AVG(`min`) FROM {table}_day_{obs_type} "
                                  "WHERE FROM_UNIXTIME(dateTime, '%%m-%%d') = '{month:02d}-{day:02d}';",
            'historical_max': "SELECT MAX(`max`) FROM {table}_day_{obs_type} "
                              "WHERE FROM_UNIXTIME(dateTime, '%%m-%%d') = '{month:02d}-{day:02d}';",
            'historical_maxtime': "SELECT `maxtime` FROM {table}_day_{obs_type} "
                                  "WHERE FROM_UNIXTIME(dateTime, '%%m-%%d') = '{month:02d}-{day:02d}' "
                                  "ORDER BY `max` DESC, dateTime ASC LIMIT 1;",
            'historical_max_avg': "SELECT AVG(`max`) FROM {table}_day_{obs_type} "
                                  "WHERE FROM_UNIXTIME(dateTime, '%%m-%%d') = '{month:02d}-{day:02d}';",
            'historical_avg': "SELECT SUM(`wsum`), SUM(`sumtime`) FROM {table}_day_{obs_type} "
                              "WHERE FROM_UNIXTIME(dateTime, '%%m-%%d') = '{month:02d}-{day:02d}';",
        },
    }

    def get_aggregate(self, obs_type, timespan, aggregate_type, db_manager, **option_dict):
        """Calculate historical statistical aggregation for a date in the year"""

        dbtype = db_manager.connection.dbtype

        # Do we know how to calculate this kind of aggregation?
        if aggregate_type not in Historical.sql_stmts[dbtype]:
            raise weewx.UnknownAggregation(aggregate_type)

        # The time span must lie on midnight-to-midnight boundaries
        if db_manager.first_timestamp is None or db_manager.last_timestamp is None:
            raise weewx.UnknownAggregation(aggregate_type)
        if not (isStartOfDay(timespan.start) or timespan.start == db_manager.first_timestamp) \
                or not (isStartOfDay(timespan.stop) or timespan.stop == db_manager.last_timestamp):
            raise weewx.UnknownAggregation("%s of %s" % (aggregate_type, timespan))

        start_day = datetime.date.fromtimestamp(timespan.start)
        stop_day = datetime.date.fromtimestamp(timespan.stop)

        # The timespan must cover just one day
        delta = stop_day - start_day
        if delta.days != 1:
            raise weewx.UnknownAggregation("%s of %s" % (aggregate_type, timespan))

        interp_dict = {
            'table': db_manager.table_name,
            'obs_type': obs_type,
            'month': start_day.month,
            'day': start_day.day
        }

        # Get the correct sql statement, and format it with the interpolation dictionary.
        sql_stmt = Historical.sql_stmts[dbtype][aggregate_type].format(**interp_dict)

        try:
            row = db_manager.getSql(sql_stmt)
        except weedb.NoColumnError:
            raise weewx.UnknownType(aggregate_type)

        # Given the result set, calculate the desired value
        if not row or None in row:
            value = None
        elif aggregate_type == 'historical_avg':
            value = row[0] / row[1] if row[1] else None
        else:
            value = row[0]

        # Look up the unit type and group of this combination of observation type and aggregation:
        u, g = weewx.units.getStandardUnitType(db_manager.std_unit_system, obs_type,
                                               aggregate_type)

        # Form the ValueTuple and return it:
        return weewx.units.ValueTuple(value, u, g)


class HistService(StdService):
    """WeeWX dummy service for initializing the Historical XTypes extension"""


# Instantiate an instance of Historical, and add it to the list of xtypes
weewx.xtypes.xtypes.append(Historical())

if __name__ == '__main__':
    import time
    import weewx.manager
    from weeutil.weeutil import TimeSpan

    db_manager = weewx.manager.DaySummaryManager.open({'SQLITE_ROOT': '/home/weewx/archive',
                                                       'database_name': 'big_weewx.sdb',
                                                       'driver': 'weedb.sqlite'})

    # db_manager = weewx.manager.DaySummaryManager.open({'database_name': 'big_weewx',
    #                                                    'driver': 'weedb.mysql',
    #                                                    'host': 'localhost',
    #                                                    'user': 'weewx',
    #                                                    'password': 'weewx'})

    start_ts = time.mktime((2019, 12, 31, 0, 0, 0, 0, 0, -1))
    stop_ts = time.mktime((2020, 1, 1, 0, 0, 0, 0, 0, -1))

    dh = Historical()
    r = dh.get_aggregate('outTemp', TimeSpan(start_ts, stop_ts), 'historical_min', db_manager)
    print(r)

    r = dh.get_aggregate('outTemp', TimeSpan(start_ts, stop_ts), 'historical_min_avg', db_manager)
    print(r)

    r = dh.get_aggregate('outTemp', TimeSpan(start_ts, stop_ts), 'historical_mintime', db_manager)
    print(r)

    r = dh.get_aggregate('outTemp', TimeSpan(start_ts, stop_ts), 'historical_max', db_manager)
    print(r)

    r = dh.get_aggregate('outTemp', TimeSpan(start_ts, stop_ts), 'historical_maxtime', db_manager)
    print(r)

    r = dh.get_aggregate('outTemp', TimeSpan(start_ts, stop_ts), 'historical_max_avg', db_manager)
    print(r)

    r = dh.get_aggregate('outTemp', TimeSpan(start_ts, stop_ts), 'historical_avg', db_manager)
    print(r)

