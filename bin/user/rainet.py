# rain - ET for diff test

import weewx.units
import weewx.xtypes

class RainET(weewx.xtypes.XType):

    @staticmethod
    def get_scalar(obs_type, record, db_manager=None):

        if obs_type != 'rain-ET':
            raise weewx.UnknownType

        rain = record.get('rain')
        ET = record.get('ET')

        if rain is not None and ET is not None:
            record['rain-ET'] = rain - ET

    @staticmethod
    def get_aggregate(obs_type, timespan, aggregate_type, db_manager, **option_dict):

        if obs_type != 'rain-ET':
            raise weewx.UnknownType
        if aggregate_type != 'sum':
            raise weewx.UnknownAggregation

        sql = "SELECT SUM(rain - ET) FROM %s WHERE dateTime>? AND dateTime<=?;" % db_manager.table_name

        row = db_manager.getSql(sql, timespan)

        if row is not None:
            value = row[0]
        else:
            value = None

        # There is probably a more elegant way of doing this:
        if db_manager.std_unit_system == weewx.US:
            unit = 'inch'
        elif db_manager.std_unit_system == weewx.METRIC:
            unit = 'cm'
        else:
            unit = 'mm'

        vt = weewx.units.ValueTuple(value, unit, 'group_rain')
        return vt

# Insert my new class into the xtypes system:
weewx.xtypes.xtypes.append(RainET())

