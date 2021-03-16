#!/usr/bin/python3

# phenologyservice.py
# 2020 Nov 20 . ccr

# ==================================================boilerplate»=====
""" WeeWX Phenology Service and Growing-Degree-Day XTypes

This script is distributed as part of the Phenology Extension to
WeeWX.  WeeWX is maintained by Tom Keffer and Matthew Wall.  This
script is maintained by Chuck Rhode although it may contain portions
copied from Keffer and Wall or directly inspired by them.

Copyright 2018—2021 by Chuck Rhode.

See LICENSE.txt for your rights.

# =================================================«boilerplate======

This module provides support routines for the Phenology Cheetah
Generator and the Phenology Image Generator.

"""

import locale
import os
import logging
import datetime
import weewx
import weeutil
import weewx.units
import weewx.xtypes
import weewx.engine
import weecfg
import user.growing_degrees

ZERO = 0
SPACE = ' '
NULL = ''
NUL = '\x00'
NA = -1

NOW_TS = datetime.datetime.now().timestamp()

LOG = logging.getLogger(__name__)

class Phenologies(dict):

    """Serve phenology models.

    This class retrieves growing-degree-day specifics from the
    database of models, which is keyed by model name.

    """

    def load_from_config_dict(self, config_dict):

        """Retrieve phenology models, part I.

        """
        
        phenology_models_dict = {}
        try:
            weewx_root = config_dict['WEEWX_ROOT']
            std_report = config_dict['StdReport']
            skin_root = std_report.get('SKIN_ROOT', 'skins')
            phenology_report = std_report['PhenologyReport']
            is_enabled = weeutil.weeutil.to_bool(phenology_report['enable'])
            phenology_skin = phenology_report['skin']
            phenology_skin_path = os.path.join(weewx_root, skin_root, phenology_skin)
            os.chdir(phenology_skin_path)
            (dummy, phenology_skin_dict) = weecfg.read_config('skin.conf')
            extras = phenology_skin_dict['Extras']
            self.load_from_extras(extras)
        except KeyError as e:
            LOG.error("No XTypes.  Missing parameter: {}".format(e))
        except AttributeError as e:
            LOG.error("Bad 'enable': {}".format(e))
        except (IOError, OSError, SyntaxError) as e:
            LOG.error("No XTypes.  {}".format(e))
        return self

    def load_from_extras(self, extras):

        """Retrieve phenology models, part II.

        """
        
        try:
            phenology_models = extras['phenologies']
            (dummy, phenology_models_dict) = weecfg.read_config(phenology_models)
            name_models = extras['models']
        except KeyError as e:
            LOG.error("No XTypes.  Missing parameter: {}".format(e))
        except AssertionError:
            LOG.error("PhenologyReport is not enabled.")
        except (IOError, SyntaxError) as e:
            LOG.error("No XTypes.  {}".format(e))
        self.southern_hemisphere_start_month_offset = phenology_models_dict.get('southern_hemisphere_start_month_offset')
        models_dict = phenology_models_dict.get('Phenologies', {})
        self.harvest(models_dict, name_models)
        return self

    def harvest(self, models_dict, name_models):

        """Build a dictionary of models.

        This method extracts growing-degree-day specifics from the
        database of models.

        """
        
        for name_scientific in models_dict:
            name_common = models_dict[name_scientific].get('name_common')
            if name_common == name_scientific:
                name_common = None
            for title_model in models_dict[name_scientific]:
                if title_model in ['name_common']:
                    pass
                else:
                    name_model = title_model.split()[-1]
                    if name_model in name_models:
                        model = {
                            'name_scientific': name_scientific,
                            'name_common': name_common,
                            'name_model': name_model,
                            }
                        model.update(models_dict[name_scientific][title_model])
                        self[name_model] = model
        return self

    def get_development_stages_t(self, converter, model_key):
        result = {}
        model_val = self.get(model_key)
        if model_val:
            is_biofix_required = model_val.get('biofix_is_required', NULL).lower() in ['true', 't', '1', '.true.', '.t.'] 
            (val, units) = model_val.get('biofix', ('0', 'degree_C_day'))
            try:
                val_t = weewx.units.ValueTuple(float(val), units, 'group_degree_day')
            except ValueError:
                val_t = weewx.units.ValueTuple(None, units, 'group_degree_day')
            biofix_std_t = converter.convert(val_t)
            if is_biofix_required:
                result['Biofix'] = [biofix_std_t]
            for (event_key, event_val) in model_val.get('Stages', {}).items():
                try:
                    event_range = event_val[:]  # a copy
                    units = event_range.pop(-1)
                    event = []
                    for val in event_range:
                        val_t = weewx.units.ValueTuple(float(val), units, 'group_degree_day')
                        val_std_t = converter.convert(val_t)
                        event_t = val_std_t + biofix_std_t
                        event.append(event_t)
                    result[event_key] = event
                except KeyError:
                    pass
                except TypeError:
                    pass
                except ValueError:
                    pass
        return result


class GrowingDegreeDays(weewx.xtypes.XType):

    """Extend basic weather types.

    Provide growing degree days output from phenology models.

    """

    def __init__(self, phenologies):
        weewx.xtypes.XType.__init__(self)
        self.metadata = phenologies
        return

    def get_gdd_series(self, obs_type, timespan, db_manager):

        """Get Growing Degree Days series.

        This function returns a list of four ValueTuple vectors:
        start_time, stop_time, gdd, and gdd_cumulative.

        """
        
        try:
            model = self.metadata[obs_type]
        except KeyError:
            raise weewx.UnknownType(obs_type)
        converter = weewx.units.StdUnitConverters[db_manager.std_unit_system] 
        self.convert_metadata_to_standard_units(converter, model)
        vector_time_stamp = []
        vector_temp_min = []
        vector_temp_max = []
        for day_time_span in weeutil.weeutil.genDaySpans(*timespan):
            vector_time_stamp.append(day_time_span)
            temp_min = weewx.xtypes.DailySummaries.get_aggregate('outTemp', day_time_span, 'min', db_manager)
            temp_max = weewx.xtypes.DailySummaries.get_aggregate('outTemp', day_time_span, 'max', db_manager)
            vector_temp_min.append(temp_min)
            vector_temp_max.append(temp_max)
        day_count = len(vector_time_stamp)
        vector_time_stamp_start = []
        vector_time_stamp_stop = []
        vector_gdd = []
        vector_gdd_cumulative = []
        total = ZERO
        (threshold_temp, threshold_temp_units) = model['threshold_t'][:2]
        (cutoff_temp, cutoff_units) = model['cutoff_t'][:2]
        if cutoff_units in ['degree_F']:
            scale = 'f'
        else:
            scale = 'c'
        method = user.growing_degrees.__dict__[model['method']]
        for (ndx, day_time_span) in enumerate(vector_time_stamp):
            try:
                (temp_max, temp_max_units) = vector_temp_max[ndx][:2]
                (temp_min, temp_min_units) = vector_temp_min[ndx][:2]
                if ndx + 1 < day_count:
                    (temp_min_2, temp_min_2_units) = vector_temp_min[ndx + 1][:2]
                else:
                    (temp_min_2, temp_min_2_units) = (None, None)
                assert temp_max_units == temp_min_units == threshold_temp_units
                if None in [temp_max, temp_min]:
                    gdd = None
                else:
                    gdd = method(
                        day_max_temp=temp_max,
                        day_min_temp=temp_min,
                        threshold_temp=threshold_temp,
                        cutoff_temp=cutoff_temp,
                        day_2_min_temp=temp_min_2,
                        scale=scale,
                        )
                    if gdd is None:
                        pass
                    else:
                        (day_time_stamp_start, day_time_stamp_stop) = day_time_span
                        vector_time_stamp_start.append(day_time_stamp_start)
                        vector_time_stamp_stop.append(day_time_stamp_stop)
                        vector_gdd.append(gdd)
                        total += gdd
                        vector_gdd_cumulative.append(total)
            except KeyError as e:
                LOG.error("Missing model parameters.  {}".format(e))
                raise weewx.CannotCalculate
            except ValueError:
                LOG.error("Bad calculation.")
                raise weewx.CannotCalculate
            except AssertionError:
                LOG.error("Mixed units.")
                raise weewx.CannotCalculate
        (unit, unit_group) = weewx.units.getStandardUnitType(db_manager.std_unit_system, 'cooldeg', agg_type=None)
        result = []
        result.append(weewx.units.ValueTuple(vector_time_stamp_start, 'unix_epoch', 'group_time'))
        result.append(weewx.units.ValueTuple(vector_time_stamp_stop, 'unix_epoch', 'group_time'))
        result.append(weewx.units.ValueTuple(vector_gdd, unit, unit_group))
        result.append(weewx.units.ValueTuple(vector_gdd_cumulative, unit, unit_group))
        return result

    def get_series(self, obs_type, timespan, db_manager, aggregate_type=None, aggregate_interval=None):
        key_agg_tuple = obs_type.split('_') + [NULL]
        (key, agg) = key_agg_tuple[:2]
        (time_stamp_start_vt, time_stamp_stop_vt, gdd_vt, gdd_cumulative_vt) = self.get_gdd_series(key, timespan, db_manager)
        if aggregate_type is None:
            is_cumulative = agg.lower() in ['accum']
            if is_cumulative:
                result = [time_stamp_start_vt, time_stamp_stop_vt, gdd_cumulative_vt]
            else:
                result = [time_stamp_start_vt, time_stamp_stop_vt, gdd_vt]
        else:
            raise weewx.UnknownAggregation(aggregate_type)
        return result

    def convert_metadata_to_standard_units(self, converter, model):

        """Units conversion.

        Make sure we use threshold and cutoff temperatures in the same
        units as outTemp series.  This function side-affects the model
        dictionary and the metadata dictionary, which contains it.

        """
        
        if model.get('has_standard_units', False):
            pass
        else:
            for item_name in ['threshold', 'cutoff']:
                try:
                    tuple_name = item_name + '_t'
                    (item_value, item_units) = model[item_name]
                    tuple_item = (float(item_value), item_units, 'group_temperature')
                    model[tuple_name] = converter.convert(tuple_item)
                except KeyError:
                    model[tuple_name] = (None, None, None)
                except ValueError:
                    model[tuple_name] = (None, None, None)
            model['has_standard_units'] = True
        return self


class PhenologyService(weewx.engine.StdService):

    """Instantiate extended data types for phenologies.

    """

    def __init__(self, engine, config_dict):
        weewx.engine.StdService.__init__(self, engine, config_dict)
        phenologies = Phenologies().load_from_config_dict(config_dict)
        self.gdd = GrowingDegreeDays(phenologies)
        weewx.xtypes.xtypes.append(self.gdd)
        return

    def shutDown(self):
        weewx.xtypes.xtypes.remove(self.gdd)
        return self


MONTH_NDX = {
    locale.nl_langinfo(locale.ABMON_1).lower(): 1,
    locale.nl_langinfo(locale.ABMON_2).lower(): 2,
    locale.nl_langinfo(locale.ABMON_3).lower(): 3,
    locale.nl_langinfo(locale.ABMON_4).lower(): 4,
    locale.nl_langinfo(locale.ABMON_5).lower(): 5,
    locale.nl_langinfo(locale.ABMON_6).lower(): 6,
    locale.nl_langinfo(locale.ABMON_7).lower(): 7,
    locale.nl_langinfo(locale.ABMON_8).lower(): 8,
    locale.nl_langinfo(locale.ABMON_9).lower(): 9,
    locale.nl_langinfo(locale.ABMON_10).lower(): 10,
    locale.nl_langinfo(locale.ABMON_11).lower(): 11,
    locale.nl_langinfo(locale.ABMON_12).lower(): 12,
    'jan': 1,
    'feb': 2,
    'mar': 3,
    'apr': 4,
    'may': 5,
    'jun': 6,
    'jul': 7,
    'aug': 8,
    'sep': 9,
    'oct': 10,
    'nov': 11,
    'dec': 12,
    }
    

def is_empty(val):
    if val:
        if isinstance(val, str):
            if val.strip().lower() in [NULL, 'none']:
                result = True
            else:
                result = False
        else:
            result = False
    else:
        result = True
    return result


def get_day_span(southern_hemisphere_start_month_offset, start_date_tuple, latest_ts):

    """Return a start_ts, stop_ts tuple

    Note:  start_date is a tuple of ('xxx', 9).

    """

    try:
        (start_month_abbrev, start_day_ndx) = start_date_tuple[:2]
    except ValueError:
        (start_month_abbrev, start_day_ndx) = ('Jan', '1')
    try:
        start_month_ndx = MONTH_NDX[start_month_abbrev[:3].lower()]
    except KeyError:
        start_month_ndx = 1
    try:
        start_day_ndx = int(start_day_ndx)
    except ValueError:
        start_day_ndx = 1
    try:
        start_month_ndx = (start_month_ndx + int(southern_hemisphere_start_month_offset)) % 12
    except ValueError:
        pass
    except TypeError:
        pass
    latest_date_time = datetime.datetime.fromtimestamp(latest_ts)
    year = latest_date_time.year
    start_day = datetime.datetime(month=start_month_ndx, day=start_day_ndx, year=year)
    if start_day > latest_date_time:
        start_day = datetime.datetime(month=start_month_ndx, day=start_day_ndx, year=year - 1)
    result = (start_day.timestamp(), latest_date_time.timestamp())
    return result


def expand_themes(themes):

    def accumulate_styles(style_name, themes, max_level=99):
        leaf = themes.get(style_name)
        if leaf:
            result = {}
            if max_level:
                if 'themes' in leaf:
                    theme_list = leaf['themes']
                    if isinstance(theme_list, list):
                        pass
                    else:
                        theme_list = [(theme_list)]
                    for style in theme_list:
                        result.update(accumulate_styles(style_name=style, themes=themes, max_level=max_level - 1))
                for (key, val) in leaf.items():
                    if key in ['themes']:
                        pass
                    else:
                        result[key] = val
        else:
            if is_empty(style_name):
                pass
            else:
                LOG.error("Missing theme:  {}".format(style_name))
            result = {}
        return result

    result = {}
    for theme_name in themes.sections:
        result[theme_name] = accumulate_styles(style_name=theme_name, themes=themes)
    return result


def get_generation_ts(gen_ts, extras, db_manager):
    result = gen_ts
    if not result:
        try:
            date_tuple = extras['generation_date']
            (year, month, day, hrs, mins) = [int(i) for i in date_tuple]
            gen_date = datetime.datetime(year, month, day, hrs, mins)
            result = gen_date.timestamp()
        except KeyError:
            result = None
    if not result:
        result = db_manager.lastGoodStamp()
    if not result:
        result = NOW_TS
    return result


# Fin
