#!/usr/bin/python3

# phenologygenerator.py
# 2020 Dec 22 . ccr

# ==================================================boilerplate»=====
""" Phenology Image Generator

This is a drop-in replacement for the WeeWX Image Generator.

This script is distributed as part of the Phenology Extension to
WeeWX.  WeeWX is maintained by Tom Keffer and Matthew Wall.  This
script is maintained by Chuck Rhode although it may contain portions
copied from Keffer and Wall or directly inspired by them.

Copyright 2018—2021 by Chuck Rhode.

See LICENSE.txt for your rights.

# =================================================«boilerplate======

"""

# ccr . 2021 Feb 16 . Change max_ts.

import os
import time
import datetime
import logging
import configobj
import weewx.reportengine
import weewx.xtypes
import weeutil.config
import weeutil.weeutil
import weeplot.utilities
import user.phenology_plotter
import user.phenologyservice
import user.extensions  # Get locale, if any.
#
# Locale is set outside of WeeWX, but being sensitive to it is
# important for date displays.  American usage is 12-hour rather than
# 24-hour.
#

ZERO = 0
SPACE = ' '
NULL = ''
NUL = '\x00'
NA = -1

NOW_TS = datetime.datetime.now().timestamp()
LOG = logging.getLogger(__name__)


class ImageGenerator(weewx.reportengine.ReportGenerator):

    """Class for managing the image generator.

    """

    def run(self):
        self.setup()
        self.genImages()
        return self

    def setup(self):
        try:
            d = self.skin_dict['Labels']['Generic']
        except KeyError:
            d = {}
        self.title_dict = weeutil.weeutil.KeyDict(d)
        try:
            self.extras = self.skin_dict['Extras']
            cascading_themes = self.extras['Themes']
            self.themes = user.phenologyservice.expand_themes(cascading_themes)
        except KeyError:
            self.themes = {}
        self.image_dict = self.skin_dict['ImageGenerator']
        self.formatter  = weewx.units.Formatter.fromSkinDict(self.skin_dict)
        self.converter  = weewx.units.Converter.fromSkinDict(self.skin_dict)
        # ensure that the skin_dir is in the image_dict
        self.image_dict['skin_dir'] = os.path.join(
            self.config_dict['WEEWX_ROOT'],
            self.skin_dict['SKIN_ROOT'],
            self.skin_dict['skin'])
        self.log_success = weeutil.weeutil.to_bool(weeutil.config.search_up(self.image_dict, 'log_success', True))
        # ensure that we are in a consistent right location
        os.chdir(self.image_dict['skin_dir'])
        return self

    def genImages(self):
        
        """Generate the images.

        The time scales will be chosen to include the given timestamp, with
        nice beginning and ending times.

        """

        def get_stamps():
            max_ts = self.plot_gen_ts
            min_ts = self.plot_gen_ts - weeutil.weeutil.to_int(self.plot_options.get('time_length', 86400))
            (min_x, max_x, inc_x) = weeplot.utilities.scaletime(min_ts, max_ts)
            time_inc_user = weeutil.weeutil.to_int(self.plot_options.get('x_interval'))
            if time_inc_user is not None:
                inc_x = time_inc_user
            return (min_x, max_x, inc_x)

        clock_start = datetime.datetime.now()
        count_images = ZERO
        cache = user.phenology_plotter.Cache()
        for timespan in self.image_dict.sections:
            for plotname in self.image_dict[timespan].sections:
#                print('plotname: {}'.format(plotname))
                self.plot_options = accumulate_leaves_and_apply_themes(self.image_dict[timespan][plotname], self.themes)
                binding = self.plot_options['data_binding']
                db_manager = self.db_binder.get_manager(binding)
                self.plot_gen_ts = user.phenologyservice.get_generation_ts(self.gen_ts, self.extras, db_manager)
                img_root = os.path.join(self.config_dict['WEEWX_ROOT'], self.plot_options['HTML_ROOT'])
                img_file = os.path.join(img_root, '{}.png'.format(plotname))
                aggregate_interval = weeutil.weeutil.to_int(self.plot_options.get('aggregate_interval'))
                if skipThisPlot(self.plot_gen_ts, aggregate_interval, img_file):
                    continue
                if self.can_skip_fresh(img_file):
                    continue
                try:
                    os.makedirs(os.path.dirname(img_file))
                except OSError:
                    pass
                self.chart = user.phenology_plotter.SeasonsTimePlot(self.plot_options, cache)
                if weeutil.weeutil.to_bool(self.plot_options.get('show_daynight', False)):
                    self.chart.manifest['day_night'] = user.phenology_plotter.DayNightShading()
                self.set_label_x()
                self.chart.manifest['axis_x'] = user.phenology_plotter.AxisX()
                (min_x, max_x, inc_x) = get_stamps()
                self.chart.manifest['axis_x'].set_scale(min_x, max_x, inc_x)
                self.chart.manifest['axis_y'] = user.phenology_plotter.AxisY()
                collection = []
                for (line_ndx, line_name) in enumerate(self.image_dict[timespan][plotname].sections):
                    collection.append((line_ndx, line_name))
                collection.reverse()
                lines = []
                for (line_ndx, line_name) in collection:
                    line_options = accumulate_leaves_and_apply_themes(self.image_dict[timespan][plotname][line_name], self.themes)
                    (handle_line, handle_legend, stages) = self.add_line(line_ndx, line_name, line_options, min_x, max_x)
                    if handle_line is None:
                        pass
                    else:
                        lines.append([handle_line, self.chart.manifest[handle_legend].text, stages])
                lines.reverse()
                self.rescale_y(lines)
                if weeutil.weeutil.to_bool(self.plot_options.get('show_daynight', False)):
                    self.set_day_night_shading()
                self.chart.manifest['title'] = user.phenology_plotter.SeasonsTitle(lines, self.chart.manifest)
                image = self.chart.render()
                try:
                    image.save(img_file)
                    count_images += 1
                except IOError as e:
                    LOG.error("Unable to save to file '{}': {}".format(img_file, e))
                
        clock_stop = datetime.datetime.now()
        clock_diff = clock_stop - clock_start
        if self.log_success:
            LOG.info("Generated {} images for report {} in {:.2f} seconds".format(
                count_images,
                self.skin_dict['REPORT_NAME'],
                clock_diff.seconds,
                ))
        return self

    def can_skip_fresh(self, img_file):
        stale = weeutil.weeutil.to_int(self.plot_options.get('stale_age'))
        if stale is None:
            result = False
        else:
            try:
                last_mod = os.path.getmtime(img_file)
                if t_now - last_mod < stale:
                    LOG.debug("Skip {}: last_mod={} age={} stale={}".format(img_file, last_mod, t_now - last_mod, stale))
                    result = True
            except os.error:
                result = False
        return result

    def rescale_y(self, lines):
        yscale = self.plot_options.get('yscale', ['None', 'None', 'None'])
        prescale = weeutil.weeutil.convertToFloat(yscale)
        (min_y, max_y, inc_y) = prescale
        for (handle_line, line_name, stages) in lines:
            stages_temps = []
            for (v_range, stage_label) in stages:
                 for (v, u, g) in v_range:
                     stages_temps.append(v)
            stage_min_y = weeutil.weeutil.min_with_none(stages_temps)
            stage_max_y = weeutil.weeutil.max_with_none(stages_temps)
            chart_item = self.chart.manifest[handle_line]
            (line_min_y, line_max_y) = chart_item.get_min_max_y()
            min_y = weeutil.weeutil.min_with_none([min_y, line_min_y, stage_min_y])
            max_y = weeutil.weeutil.max_with_none([max_y, line_max_y, stage_max_y])
        if min_y is None and max_y is None :
#
#            There is no valid data found. Choose arbitrary scaling so
#            that even an empty chart is possible.
#
            (min_y, max_y, inc_y) = (0.0, 1.0, 0.2)
        else:
            (min_y, max_y, inc_y) = weeplot.utilities.scale(
                min_y, max_y,
                prescale=prescale,
                nsteps=self.chart.style.nticks_y,
                )
        self.chart.manifest['axis_y'].set_scale(min_y, max_y, inc_y)
        return self

    def set_day_night_shading(self):

        def get_pattern(key):
            result = self.plot_options.get(key)
            if result:
                skin_dir = self.image_dict.get('skin_dir', NULL)
                result = os.path.join(skin_dir, result)
            return result
        
        parms = {}
        (parms['lat'], parms['lon']) = (self.stn_info.latitude_f, self.stn_info.longitude_f)
        parms['color_day'] = user.phenology_plotter.to_rgb(self.plot_options.get('daynight_day_color', '#ffffff'))
        parms['color_night'] = user.phenology_plotter.to_rgb(self.plot_options.get('daynight_night_color', '#f0f0f0'))
        parms['color_edge'] = user.phenology_plotter.to_rgb(self.plot_options.get('daynight_edge_color', '#efefef'))
        parms['pattern_day'] = get_pattern('daynight_day_pattern')
        parms['pattern_night'] = get_pattern('daynight_night_pattern')
        parms['scale_x'] = self.chart.manifest['axis_x'].get_scale()
        parms['scale_y'] = self.chart.manifest['axis_y'].get_scale()
        for key in [
                'color_day',
                'color_night',
                'color_edge',
                ]:
            val = parms[key]
            if user.phenology_plotter.is_empty(val):
                parms[key] = None
        self.chart.manifest['day_night'].set_parms(**parms)
        return self

    def add_line(self, line_ndx, line_name, line_options, min_ts, max_ts):

        def trim_time_line(start_vec, stop_vec, data_vec, min_ts, max_ts):
            start_vec_new = []
            stop_vec_new = []
            data_vec_new = []
            while start_vec:
                start_ts = start_vec.pop(ZERO)
                stop_ts = stop_vec.pop(ZERO)
                data_val = data_vec.pop(ZERO)
                if (min_ts <= start_ts <= max_ts) and (min_ts <= stop_ts <= max_ts):
                    start_vec_new.append(start_ts)
                    stop_vec_new.append(stop_ts)
                    data_vec_new.append(data_val)
            return [start_vec_new, stop_vec_new, data_vec_new]
        
        var_type = line_options.get('data_type', line_name)
        aggregate_type = line_options.get('aggregate_type')
        if user.phenology_plotter.is_empty(aggregate_type):
            aggregate_type = None
            aggregate_interval = None
            half_interval = None
        else:
            try:
                aggregate_interval = weeutil.weeutil.to_int(line_options.get('aggregate_interval'))
                half_interval = aggregate_interval / 2.0
            except KeyError:
                LOG.error("Aggregate interval required.")
                LOG.error("Line type {} skipped".format(var_type))
                return (None, None, None)
        binding = line_options['data_binding']
        db_manager = self.db_binder.get_manager(binding)
        (metadata, stages) = self.add_phenology_metadata(var_type, line_options, line_ndx)
        artificial_min_ts = self.get_start_date(min_ts, metadata)
        (start_vec_t, stop_vec_t ,data_vec_t) = weewx.xtypes.get_series(
            var_type,
            weeutil.weeutil.TimeSpan(artificial_min_ts, max_ts),  # 2021 Feb 16
            db_manager,
            aggregate_type=aggregate_type,
            aggregate_interval=aggregate_interval,
            )
        plot_type = line_options.get('plot_type', 'line')
        if aggregate_type and aggregate_type.lower() in ('avg', 'max', 'min') and plot_type != 'bar':
            x = [x - half_interval for x in start_vec_t[ZERO]]
            start_vec_t = weewx.units.ValueTuple(x, start_vec_t[1], start_vec_t[2])
            x = [x - half_interval for x in stop_vec_t[ZERO]]
            stop_vec_t = weewx.units.ValueTuple(x, stop_vec_t[1], stop_vec_t[2])
        # Because an artificial min_ts may have been used to build
        # cumulative stats, trimming the timeline is now required.
        (start_array, stop_array, data_array) = trim_time_line(start_vec_t[ZERO], stop_vec_t[ZERO], data_vec_t[ZERO], min_ts, max_ts)
        start_vec_t = weewx.units.ValueTuple(start_array, start_vec_t[1], start_vec_t[2])
        stop_vec_t = weewx.units.ValueTuple(stop_array, stop_vec_t[1], stop_vec_t[2])
        data_vec_t = weewx.units.ValueTuple(data_array, data_vec_t[1], data_vec_t[2])
        # Do any necessary unit conversions:
        new_start_vec_t = self.converter.convert(start_vec_t)
        new_stop_vec_t  = self.converter.convert(stop_vec_t)
        new_data_vec_t = self.converter.convert(data_vec_t)
        self.set_label_y(var_type, line_options, new_data_vec_t)
        interval_vec = None
        gap_fraction = None
        if plot_type in ['bar']:
            interval_vec = [x[1] - x[ZERO] for x in zip(new_start_vec_t.value, new_stop_vec_t.value)]
        elif plot_type in ['line']:
            gap_fraction = weeutil.weeutil.to_float(line_options.get('line_gap_fraction'))
            if gap_fraction is None:
                pass
            else:
                if not ZERO < gap_fraction < 1:
                    LOG.error("Gap fraction {:5.3f} outside range 0 to 1. Ignored.".format(gap_fraction))
                    gap_fraction = None
        handle_legend = 'legend_line_{}'.format(line_ndx)
        handle_line = 'chart_line_{}'.format(line_ndx)
        if plot_type in ['line']:
            self.chart.manifest[handle_line] = user.phenology_plotter.Line(
                seq=line_ndx,
                array_x=new_stop_vec_t[ZERO],
                array_y=new_data_vec_t[ZERO],
                gap_fraction=gap_fraction,
                color_bgr=self.get_color(line_options),
                can_fill_curve=weeutil.weeutil.to_bool(self.plot_options.get('fill_curve', False)),
                fill_color_bgr=self.get_fill_color(line_options),
                pattern=self.get_pattern(line_options),
                stroke_width=self.get_stroke_width(line_options),
                line_type=self.get_line_type(line_options),
                marker_type=self.get_marker_type(line_options),
                marker_size=self.get_marker_size(line_options),
                )
        elif plot_type in ['bar']:
            self.chart.manifest[handle_line] = user.phenology_plotter.BarsVertical(
                seq=line_ndx,
                array_x=new_stop_vec_t[ZERO],
                array_y=new_data_vec_t[ZERO],
                bar_widths=interval_vec,
                color_bgr=self.get_color(line_options),
                fill_color_bgr=self.get_fill_color(line_options),
                pattern=self.get_pattern(line_options),
                stroke_width=self.get_stroke_width(line_options),
                )
        elif plot_type in ['vector']:
            try:
                vector_rotate = -float(line_options['vector_rotate'])
            except ValueError:
                vector_rotate = None
            except KeyError:
                vector_rotate = None
            if 'wind rose' in self.chart.manifest:
                pass
            else:
                self.chart.manifest['wind rose'] = user.phenology_plotter.CompassRose(vector_rotate)
            self.chart.manifest[handle_line] = user.phenology_plotter.Wind(
                seq=line_ndx,
                array_x=new_stop_vec_t[ZERO],
                array_y=new_data_vec_t[ZERO],
                vector_rotate=vector_rotate,
                color_bgr=self.get_color(line_options),
                stroke_width=self.get_stroke_width(line_options),
                )
        else:
            LOG.error("Can't plot {} as {}".format(var_type, plot_type))
        chart_item = self.chart.manifest.get(handle_line)
        if chart_item is None:
            pass
        else:
            self.set_line_legend(handle_legend, chart_item, var_type, line_options)
        return (handle_line, handle_legend, stages)

    def get_start_date(self, min_ts, metadata):

        """See PhenologyImageGenerator.

        """
        
        result = min_ts
        return result

    def set_label_x(self):
        bottom_label_format = self.plot_options.get('bottom_label_format', '%m/%d/%y %H:%M')
        plot_generation_time = datetime.datetime.fromtimestamp(self.plot_gen_ts)
        bottom_label = plot_generation_time.strftime(bottom_label_format)
        self.chart.manifest['label_x'] = user.phenology_plotter.LabelX(bottom_label)
        return self

    def set_label_y(self, var_type, line_options, vect_t):

        """Add a units label.

        NB:  All will get overwritten except the last. Get the label
        from the configuration dictionary.

        """
        
        default_label_y = weewx.units.get_label_string(self.formatter, self.converter, var_type)
        if default_label_y in [NULL]:
            default_label_y = self.formatter.get_label_string(vect_t.unit)
        label_y = line_options.get('y_label', default_label_y)
        self.chart.manifest['label_y'] = user.phenology_plotter.LabelY(label_y.strip())
        return self

    def get_color(self, line_options):
        color = line_options.get('color')
        if color is None:
            result = None
        else:
            result = user.phenology_plotter.to_rgb(color)
        return result

    def get_fill_color(self, line_options):
        color = line_options.get('fill_color')
        if color is None:
            result = None
        else:
            result = user.phenology_plotter.to_rgb(color)
        return result

    def get_pattern(self, line_options):
        pattern = line_options.get('chart_fill_pattern')
        if pattern is None:
            result = None
        else:
            skin_dir = self.image_dict.get('skin_dir', NULL)
            result = os.path.join(skin_dir, pattern)
        return result

    def get_stroke_width(self, line_options):
        result = weeutil.weeutil.to_int(line_options.get('width'))
        return result

    def get_line_type(self, line_options):
        result = line_options.get('line_type', 'solid')
        if user.phenology_plotter.is_empty(result):
            result = None
        return result

    def get_marker_type(self, line_options):
        result = line_options.get('marker_type')
        return result

    def get_marker_size(self, line_options):
        result = weeutil.weeutil.to_int(line_options.get('marker_size', 8))
        return result

    def add_phenology_metadata(self, var_type, line_options, line_ndx):

        """See PhenologyImageGenerator.

        """
        
        model = None
        result = []
        return (model, result)

    def set_line_legend(self, handle_legend, line, var_type, line_options):
        label = line_options.get('label')
        if not label:
            # No explicit label. Look up a generic one. NB: title_dict is a KeyDict which
            # will substitute the key if the value is not in the dictionary.
            label = self.title_dict[var_type]
        self.chart.manifest[handle_legend] = user.phenology_plotter.Legend(text=label, line=line)
        return self


class PhenologyImageGenerator(ImageGenerator):

    def run(self):
        self.development_models = user.phenologyservice.Phenologies().load_from_config_dict(self.config_dict)
        ImageGenerator.run(self)
        return self

    def add_phenology_metadata(self, var_type, line_options, line_ndx):

        """Create the manifest items to draw event horizons.

        NB:  This method side-affects line_options.

        """

        try:
            key_agg_tuple = var_type.split('_')
            (key, agg) = key_agg_tuple
            model = self.development_models[key]
            stages_t = self.development_models.get_development_stages_t(self.converter, key)
        except ValueError:
            model = None
        except KeyError:
            model = None
        if model:
            label_words = []
            name_scientific = model.get('name_scientific')
            name_common = model.get('name_common')
            label_words.append(name_scientific)
            if name_common is None:
                pass
            elif name_common == name_scientific:
                pass
            else:
                label_words.append('({})'.format(name_common))
            if 'label' in line_options:
                pass
            else:
                line_options['label'] = SPACE.join(label_words)
            result = []
            for (key, val) in stages_t.items():
                val_range = []
                for (v, u, g) in val:
                    y = weeutil.weeutil.to_float(v)
                    val_range.append((y, u, g))
                result.append((val_range, key))
            result.sort()
            result.reverse()
            for (stage_ndx, (y_range, stage_label)) in enumerate(result):
                stage_handle = 'chart_horizon_{}_{}'.format(line_ndx, stage_ndx)
                self.chart.manifest[stage_handle] = user.phenology_plotter.Horizon(y_range, stage_label)
        else:
            result = []
        return (model, result)

    def get_start_date(self, min_ts, metadata):
        if metadata:
            (result, latest_date_time_ts) = user.phenologyservice.get_day_span(
                self.development_models.get('southern_hemisphere_start_month_offset'),
                start_date_tuple=metadata.get('start_date'),
                latest_ts=self.plot_gen_ts,
                )
        else:
            result = min_ts
        return result


def skipThisPlot(time_ts, aggregate_interval, img_file):
    
    """A plot can be skipped if it was generated recently and has not changed.
    This happens if the time since the plot was generated is less than the
    aggregation interval.

    """

    # Images without an aggregation interval have to be plotted every time.
    # Also, the image definitely has to be generated if it doesn't exist.
    if aggregate_interval is None or not os.path.exists(img_file):
        return False

    # If its a very old image, then it has to be regenerated
    if time_ts - os.stat(img_file).st_mtime >= aggregate_interval:
        return False

    # Finally, if we're on an aggregation boundary, regenerate.
    time_dt = datetime.datetime.fromtimestamp(time_ts)
    tdiff = time_dt - time_dt.replace(hour=ZERO, minute=ZERO, second=ZERO, microsecond=ZERO)
    return abs(tdiff.seconds % aggregate_interval) > 1


def disable_timing(section, key):

    """Disable report_timing.

    """
    
    if key == 'report_timing':
        section['report_timing'] = "* * * * *"

        
def accumulate_leaves_and_apply_themes(leaf, themes, max_level=99):
    if leaf.parent is leaf:
        result = configobj.ConfigObj()
    else:
        if max_level:
            # Otherwise, recursively accumulate scalars above me
            result = accumulate_leaves_and_apply_themes(leaf.parent, themes, max_level - 1)
        else:
            result = configobj.ConfigObj()
                
    # Now merge my scalars into the results:
    merge_dict = {}
    for scalar in leaf.scalars:
        if scalar in ['themes']:
            theme_list = leaf['themes']
            if isinstance(theme_list, list):
                pass
            else:
                theme_list = [(theme_list)]
            theme_list = theme_list[:]  # a copy
            theme_list.reverse()
            for style in theme_list:
                merge_dict.update(themes[style])
        else:
            merge_dict[scalar] = leaf[scalar]
    result.merge(merge_dict)
    return result


def main_line():

    """Testing only.

    This function is called only when this module is run stand-alone.

    """

    import weewx.engine
    import weewx.station
    import weecfg
    import weeutil.logger
    
    config_path = '/home/crhode/WeeWX/weewx/weewx.conf'
    (config_path, config_dict) = weecfg.read_config(config_path)
    config_dict.walk(disable_timing)
    weewx.debug = weeutil.weeutil.to_int(config_dict.get('debug', ZERO))
    weeutil.logger.setup('wee_reports', config_dict)
    stn_info = weewx.station.StationInfo(**config_dict['Station'])
    try:
        binding = config_dict['StdArchive']['data_binding']
    except KeyError:
        binding = 'wx_binding'
    db_manager = weewx.manager.DBBinder(config_dict).get_manager(binding)
    ts = db_manager.lastGoodStamp()
    record = db_manager.getRecord(ts)
    report_engine = weewx.reportengine.StdReportEngine(config_dict, stn_info, record=record, gen_ts=None)
    skin_dict = report_engine._build_skin_dict('PhenologyReport')
    phenology_service = user.phenologyservice.PhenologyService(report_engine, config_dict)
    image_generator = PhenologyImageGenerator(
        config_dict=config_dict,
        skin_dict=skin_dict,
        gen_ts=None,
        first_run=False,
        stn_info=stn_info,
        record=record,
        )
    image_generator.setup()
    image_generator.start()
    image_generator.finalize()
    phenology_service.shutDown()
    return


if __name__ == "__main__":
    main_line()

     
# Fin
