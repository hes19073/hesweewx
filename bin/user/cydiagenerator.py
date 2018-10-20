#!/usr/bin/python
# -*- coding: utf-8 -*-

# cydiagenerator.py
# 2018 Feb 14 . ccr

"""Generate a *.png graph image and an *.html report for the
Cydia pomonella Flight-Model.

"""

from __future__ import with_statement
from __future__ import division
import os.path
import time
import datetime
import csv
import syslog
import configobj
import codecs
import Cheetah.Template
import weeplot.genplot
import weeutil.weeutil
from weeutil.weeutil import to_bool, to_int, to_float
import weewx.units
from weewx.units import ValueTuple
import weewx.reportengine
import dd_table

ZERO = 0
SPACE = ' '
NULL = ''
NUL = '\x00'
NA = -1


def get_float_t(txt, unit_group):
    if txt is None:
        result = None
    elif isinstance(txt, basestring):
        if txt.lower() in [NULL, 'none']:
            result = None
    else:
        result = ValueTuple(float(txt[ZERO]), txt[1], unit_group)
    return result

# The default search list includes standard information sources that should be
# useful in most templates.
default_search_list = [
    "weewx.cheetahgenerator.Almanac",
    "weewx.cheetahgenerator.Station",
    "weewx.cheetahgenerator.Current",
    "weewx.cheetahgenerator.Stats",
    "weewx.cheetahgenerator.UnitInfo",
    "weewx.cheetahgenerator.Extras"]

def logmsg(lvl, msg):
    syslog.syslog(lvl, 'cydiagenerator: %s' % msg)

def logdbg(msg):
    logmsg(syslog.LOG_DEBUG, msg)

def loginf(msg):
    logmsg(syslog.LOG_INFO, msg)

def logerr(msg):
    logmsg(syslog.LOG_ERR, msg)

def logcrt(msg):
    logmsg(syslog.LOG_CRIT, msg)

# =============================================================================
#                    Class CydiaGenerator
# =============================================================================

class CydiaGenerator(weewx.reportengine.ReportGenerator):

    """Class for managing the image generator.

    """
    
    def __init__(self, config_dict, skin_dict, gen_ts, first_run, stn_info, record=None):
        weewx.reportengine.ReportGenerator.__init__(self, config_dict, skin_dict, gen_ts, first_run, stn_info, record)
        self.cydia_report_generator = CydiaReportGenerator(config_dict, skin_dict, gen_ts, first_run, stn_info, record)
        return

    def run(self):
        self.setup()
        self.genImages(self.gen_ts)
        if hasattr(self, 'plot'):
            self.cydia_report_generator.recs = self.zip_vectors()
            self.cydia_report_generator.run()
        return self
        
    def setup(self):
        
        self.image_dict = self.skin_dict['ImageGenerator']
        self.cydia_dict = self.skin_dict['CydiaGenerator']
        self.title_dict = self.skin_dict.get('Labels', {}).get('Generic', {})
        self.formatter  = weewx.units.Formatter.fromSkinDict(self.skin_dict)
        self.converter  = weewx.units.Converter.fromSkinDict(self.skin_dict)
        self.to_degree_f = weewx.units.FixedConverter('degree_F')
        # determine how much logging is desired
        self.log_success = to_bool(self.image_dict.get('log_success', True))
        # ensure that we are in a consistent right location
        os.chdir(os.path.join(self.config_dict['WEEWX_ROOT'],
                              self.skin_dict['SKIN_ROOT'],
                              self.skin_dict['skin']))
        return self

    def genImages(self, gen_ts):

        """Generate the images.
        
        The time scales will be chosen to include the given timestamp, with
        nice beginning and ending times.
    
        gen_ts: The time around which plots are to be generated. This will
        also be used as the bottom label in the plots.
        
        """

        t1 = time.time()
        ngen = ZERO
        
        for species_name in self.cydia_dict.sections:
            # Get the path that the image is going to be saved to:
            plot_options = weeutil.weeutil.accumulateLeaves(self.image_dict['year_images'])
            species_options = weeutil.weeutil.accumulateLeaves(self.cydia_dict[species_name])
            plot_options.update(species_options)

            date_string = plot_options.get('end_date')
            if date_string:
                plotgen_ts = time.mktime(time.strptime(date_string, '%m/%d/%Y'))
            else:
                plotgen_ts = gen_ts
                if plotgen_ts:
                    pass
                else:
                    plotgen_ts = time.time()

            date_string = plot_options.get('start_date')
            if date_string:
                start_date_ts = time.mktime(time.strptime(date_string, '%m/%d/%Y'))
            else:
                now_tuple = time.localtime(plotgen_ts)
                new_year_tuple = [now_tuple.tm_year, 1, 1, ZERO, ZERO, ZERO, ZERO, ZERO, now_tuple.tm_isdst]
                start_date_ts = time.mktime(tuple(new_year_tuple))
            
            image_root = os.path.join(self.config_dict['WEEWX_ROOT'], plot_options['HTML_ROOT'])
            #skin_root = os.path.join(self.config_dict['WEEWX_ROOT'], plot_options['SKIN_ROOT'])
            img_file = os.path.join(image_root, '%s.png' % species_name)
            html_file = os.path.join(image_root, '%s.html' % species_name)
            ai = 21600   #test mit 600 86400 = 24h
            
            # Calculate a suitable min, max time for the requested time.
            (minstamp, maxstamp, timeinc) = weeplot.utilities.scaletime(start_date_ts, plotgen_ts)
             
            # Now its time to find and hit the database:
            text_root = os.path.join(self.config_dict['WEEWX_ROOT'], plot_options['HTML_ROOT'])
            tmpl = self.skin_dict.get('CheetahGenerator', {}).get('CydiaDDData', {}).get('template', 'Cydia/NOAA-YYYY.csv.tmpl')
            (csv, ext) = os.path.splitext(tmpl)
            csv_name = csv.replace('YYYY', str(time.localtime(plotgen_ts).tm_year))
            csv_file_name = os.path.join(text_root, '%s' % csv_name)
            spec_threshold_lo = plot_options.get('threshold_lo', [50, 'degree_F'])
            threshold_lo_t = get_float_t(spec_threshold_lo, 'group_temperature')
            spec_threshold_hi = plot_options.get('threshold_hi', [88, 'degree_F'])
            threshold_hi_t = get_float_t(spec_threshold_hi, 'group_temperature')
            recs = self.get_vectors((minstamp, maxstamp), csv_file_name, threshold_lo_t, threshold_hi_t)
                
            # Do any necessary unit conversions:
            self.vectors = {}
            for (key, val) in recs.iteritems():
                self.vectors[key] = self.converter.convert(val)

            if skipThisPlot(plotgen_ts, ai, img_file):
                pass
            else:
                # Create the subdirectory that the image is to be put in.
                # Wrap in a try block in case it already exists.
                try:
                    os.makedirs(os.path.dirname(img_file))
                except OSError:
                    pass
            
                self.plot = self.plot_image(
                    species_name,
                    plot_options,
                    plotgen_ts,
                    (minstamp, maxstamp, timeinc),
                    self.vectors,
                    )
                # OK, the plot is ready. Render it onto an image
                image = self.plot.render()

                try:
                    # Now save the image
                    image.save(img_file)
                    ngen += 1
                except IOError, e:
                    syslog.syslog(syslog.LOG_CRIT, "cydiagenerator: Unable to save to file '%s' %s:" % (img_file, e))
                t2 = time.time()
                if self.log_success:
                    syslog.syslog(syslog.LOG_INFO, "cydiagenerator: Generated %d images for %s in %.2f seconds" % \
                        (ngen, self.skin_dict['REPORT_NAME'], t2 - t1))
                        
                #unit = codecs.open(html_file, 'w', 'utf-8')
                #self.generate_report(
                #    species_name,
                #    unit,
                #    plot_options,
                #    plotgen_ts,
                #    (minstamp, maxstamp, timeinc),
                #    (threshold_lo_t, threshold_hi_t),
                #    self.recs,
                #    self.plot.horizons,
                #    )
                #unit.close()
                        
        return self

    def plot_image(
            self,
            species_name,
            plot_options,
            plotgen_ts,
            stamps,
            vectors,
            ):

        line_options = plot_options
        (minstamp, maxstamp, timeinc) = stamps
        
        # Create a new instance of a time plot and start adding to it
        result = TimeHorizonPlot(plot_options)
                
        # Override the x interval if the user has given an explicit interval:
        timeinc_user = to_int(plot_options.get('x_interval'))
        if timeinc_user is not None:
            timeinc = timeinc_user
        result.setXScaling((minstamp, maxstamp, timeinc))
        
        # Set the y-scaling, using any user-supplied hints: 
        result.setYScaling(weeutil.weeutil.convertToFloat(plot_options.get('yscale', ['None', 'None', 'None'])))
        
        # Get a suitable bottom label:
        bottom_label_format = plot_options.get('bottom_label_format', '%m/%d/%y %H:%M')
        bottom_label = time.strftime(bottom_label_format, time.localtime(plotgen_ts))
        result.setBottomLabel(bottom_label)

        # This generator acts on only one variable type:
        var_type = 'heatdeg'

        # Get the type of plot ("bar', 'line', or 'vector')
        plot_type = line_options.get('plot_type', 'line')

        # Add a unit label.
        unit_label = plot_options.get('y_label', weewx.units.get_label_string(self.formatter, self.converter, var_type))
        # Strip off any leading and trailing whitespace so it's easy to center
        result.setUnitLabel(unit_label.strip())

        # See if a line label has been explicitly requested:
        label = line_options.get('label')
        if not label:
            # No explicit label. Is there a generic one? 
            # If not, then the SQL type will be used instead
            label = self.title_dict.get(var_type, var_type)

        # Insert horizon lines.
        horizons = []
        biofix = get_float_t(line_options.get('biofix_actual'), 'group_degree_day')
        if biofix:
            biofix_label = 'Biofix'
        else:
            biofix = get_float_t(line_options.get('biofix_estimated', [175, 'degree_F_day']), 'group_degree_day')
            biofix_label = 'Biofix (Prognose/ Estimated)'
        horizons.append([biofix, biofix_label])
        offsets = self.cydia_dict[species_name].get('Offsets_from_Biofix')
        if offsets:
            for (horizon_label, offset) in offsets.iteritems():
                horizon_val = offset.get('offset')
                if horizon_val:
                    horizon = get_float_t(horizon_val, 'group_degree_day')
                    if horizon:
                        horizons.append([biofix + horizon, horizon_label])
        result.horizons = [(self.converter.convert(horizon), horizon_label) for (horizon, horizon_label) in horizons]
        result.horizon_min = None
        result.horizon_max = None
        for ((horizon, horizon_units, horizon_group), horizon_label) in result.horizons[:1]:
            result.horizon_min = horizon
            result.horizon_max = horizon
        for ((horizon, horizon_units, horizon_group), horizon_label) in result.horizons[1:]:
            result.horizon_min = min(result.horizon_min, horizon)
            result.horizon_max = max(result.horizon_max, horizon)

        # See if a color has been explicitly requested.
        color = line_options.get('color')
        if color is not None: color = weeplot.utilities.tobgr(color)
        fill_color = line_options.get('fill_color')
        if fill_color is not None: fill_color = weeplot.utilities.tobgr(fill_color)
        result.horizon_top_color     = weeplot.utilities.tobgr(
            weeplot.utilities.tobgr(line_options.get('horizon_top_color', '0xffffff'))
            )
        result.horizon_bottom_color  = weeplot.utilities.tobgr(
            weeplot.utilities.tobgr(line_options.get('horizon_bottom_color', '0xf0f0f0'))
            )
        result.horizon_edge_color    = weeplot.utilities.tobgr(
            weeplot.utilities.tobgr(line_options.get('horizon_edge_color', '0xefefef'))
            )
        result.horizon_gradient      = int(line_options.get('horizon_gradient', 20))
        result.horizon_label_font_path = line_options.get('horizon_label_font_path',
                                                          '/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf')
        result.horizon_label_font_size = int(line_options.get('horizon_label_font_size', 12))
        result.horizon_label_font_color = weeplot.utilities.tobgr(
            line_options.get('horizon_label_font_color', '0x000000')
            )
        result.horizon_label_offset = int(line_options.get('horizon_label_offset', 3))

        
        # Get the line width, if explicitly requested.
        width = to_int(line_options.get('width'))
                            
        # Some plot types require special treatments:
        interval_vec = None                        
        vector_rotate = None
        gap_fraction = None
        if plot_type == 'bar':
            interval_vec = [x[1] - x[ZERO]for x in zip(vectors['date'].value, vectors['date'].value)]
        elif plot_type == 'line':
            gap_fraction = to_float(line_options.get('line_gap_fraction'))
        if gap_fraction is not None:
            if not ZERO < gap_fraction < 1:
                syslog.syslog(syslog.LOG_ERR, "imagegenerator: Gap fraction %5.3f outside range 0 to 1. Ignored." % gap_fraction)
                gap_fraction = None

        # Get the type of line (only 'solid' or 'none' for now)
        line_type = line_options.get('line_type', 'solid')
        if line_type.strip().lower() in ['', 'none']:
            line_type = None

        marker_type = line_options.get('marker_type')
        marker_size = to_int(line_options.get('marker_size', 8))

        # Get the spacings between labels, i.e. every how many lines a label is drawn
        x_label_spacing = plot_options.get('x_label_spacing', 2)
        y_label_spacing = plot_options.get('y_label_spacing', 2)

        # Add the line to the emerging plot:
        result.addLine(weeplot.genplot.PlotLine(
            vectors['date'][ZERO],
            vectors['dd_cumulative'][ZERO],
            label         = label, 
            color         = color,
            fill_color    = fill_color,
            width         = width,
            plot_type     = plot_type,
            line_type     = line_type,
            marker_type   = marker_type,
            marker_size   = marker_size,
            bar_width     = interval_vec,
            vector_rotate = vector_rotate,
            gap_fraction  = gap_fraction,
            ))
        return result
    
    def get_vectors(self, stamps, csv_file_name, threshold_lo_t, threshold_hi_t):

        (minstamp, maxstamp) = stamps
        threshold_lo = self.to_degree_f.convert(threshold_lo_t)[ZERO]
        threshold_hi = self.to_degree_f.convert(threshold_hi_t)[ZERO]
        result = {
            'date': ValueTuple([], 'unix_epoch', 'group_time'),
            'daily_max': ValueTuple([], 'degree_F', 'group_temperature'),
            'daily_min': ValueTuple([], 'degree_F', 'group_temperature'), 
            'dd': ValueTuple([], 'degree_F_day', 'group_degree_day'), 
            'dd_cumulative': ValueTuple([], 'degree_F_day', 'group_degree_day'), 
            }
        try:
            with open(csv_file_name) as csv_file:
                csv_dict = csv.DictReader(csv_file)
                recs = []
                for (ndx, rec) in enumerate(csv_dict):
                    try:
                        date_string = '%(YR)s/%(MO)s/%(DAY)s' % rec
                        stamp = time.mktime(time.strptime(date_string, '%Y/%m/%d'))
                    except ValueError:
                        stamp = None
                    if stamp is None:
                        pass
                    else:
                        recs.append([stamp, rec])
                recs.sort()
                dd_cumulative = ZERO
                for (ndx, (stamp, rec)) in enumerate(recs):
                    if (minstamp <= stamp) and (stamp <= maxstamp):
                        result['date'][ZERO].append(stamp)
                        try:
                            daily_max = float(rec.get('TMPMAX_F'))
                            result['daily_max'][ZERO].append(daily_max)
                            daily_min = float(rec.get('TMPMIN_F'))
                            result['daily_min'][ZERO].append(daily_min)
                            dd = dd_table.dd_clipped(daily_max, daily_min, threshold_lo, threshold_hi)
                            result['dd'][ZERO].append(dd)
                            dd_cumulative += dd
                            result['dd_cumulative'][ZERO].append(dd_cumulative)
                        except ValueError:
                            pass
                        except TypeError:
                            pass
        except IOError, e:
            syslog.syslog(syslog.LOG_CRIT, "cydiagenerator: Unable to read file '%s' %s:" % (csv_file_name, e))

        return result

    def generate_report(
            self,
            species_name,
            unit,
            plot_options,
            plotgen_ts,
            stamps,
            thresholds,
            vectors,
            horizons,
            ):
        horizon_labels = [(cumulative_dd, horizon_label) for ((cumulative_dd, dd_units, dd_group), horizon_label) in horizons]
        horizon_labels.sort()
        (minstamp, maxstamp, timeinc) = stamps
        (threshold_lo_t, threshold_hi_t) = thresholds
        body_prolog = u'''<!doctype html>
 <html lang="de">
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <title>%(location)s %(title)s</title>
    <link rel="stylesheet" type="text/css" href="./../css/weewx.css"/>
    <link rel="stylesheet" type="text/css" href="./../css/cydia.css"/>
    <link rel="icon" type="image/png" href="favicon.ico" />
  </head>

  <body>
    <div id="container">
'''
        body_epilog = u'''    </div>
  </body>
</html>
'''
        masthead = u'''      <div id="masthead">
        <h1>%(location)s</h1>
        <h2>%(title)s</h2>
          <h2>%(time_stamp)s</h2>
      </div>
'''
        content_prolog = u'''      <div id="content">
        <div id="plots">
          <img src="%(species_name)s.png" alt="%(title)s" />
        </div>

        <p>... where Degree-Days = ((Daily Max Temp + Daily Min Temp) /
        2.0) - %(threshold_lo).1f %(units_threshold_lo)s.</p>

        <p>... except that an adjustment is made for Daily Max/Min
        outside the range %(threshold_lo).1f %(units_threshold_lo)s —
        %(threshold_hi).1f %(units_threshold_hi)s by clipping the area
        normalized to Degree-Days under a symmetric sine wave normalized
        to Daily Max/Min between those limits.</p>
        
        <table>
          <tr valign=top>
            <th align=left>Date</th>
            <th align=right>Min Temp<br>%(units_temp)s</th>
            <th align=right>Max Temp<br>%(units_temp)s</th>
            <th align=right>DegDay<br>%(units_dd)s</th>
            <th align=right>Cumulative<br>DegDay<br>%(units_dd)s</th>
            <th align=left>Event</th>
          </tr>
'''
        content_epilog = u'''      </div>
'''
        detail = u'''          <tr>
            <td align=left>%(date_string)s</td>
            <td align=right>%(daily_min)5.1f</td>
            <td align=right>%(daily_max)5.1f</td>
            <td align=right>%(dd)5.1f</td>
            <td align=right>%(dd_cumulative)5.1f</td>
            <td align=left>%(remark)s</td>
          </tr>
'''
        data_items = {}
        data_items['species_name'] = os.path.basename(species_name)
        data_items['title'] = plot_options.get('label', NULL)
        bottom_label_format = plot_options.get('bottom_label_format', '%m/%d/%y %H:%M')
        data_items['time_stamp'] = time.strftime(bottom_label_format, time.localtime(plotgen_ts))
        data_items['location'] = self.config_dict.get('Station', {}).get('location', NULL)
        units_labels = self.skin_dict.get('Units', {}).get('Labels', {}) 
        data_items['units_temp'] = units_labels.get(vectors['daily_max'][1], NULL).decode('utf-8')
        data_items['units_dd'] = units_labels.get(vectors['dd'][1], NULL).decode('utf-8')
        data_items['threshold_lo'] = round(threshold_lo_t[ZERO], 1)
        data_items['units_threshold_lo'] = units_labels.get(threshold_lo_t[1], NULL).decode('utf-8')
        data_items['threshold_hi'] = round(threshold_hi_t[ZERO], 1)
        data_items['units_threshold_hi'] = units_labels.get(threshold_hi_t[1], NULL).decode('utf-8')
        unit.write(body_prolog % data_items)
        unit.write(masthead % data_items)
        unit.write(content_prolog % data_items)
        for (ndx, value) in enumerate(vectors['date'][ZERO]):
            rec = {}
            rec['date_string'] = time.strftime('%d %b', time.localtime(value))
            rec['daily_max'] = round(vectors['daily_max'][ZERO][ndx], 1)
            rec['daily_min'] = round(vectors['daily_min'][ZERO][ndx], 1)
            rec['dd'] = round(vectors['dd'][ZERO][ndx], 1)
            dd_cumulative = round(vectors['dd_cumulative'][ZERO][ndx], 1)
            rec['dd_cumulative'] = dd_cumulative
            remarks = []
            while horizon_labels:
                (horizon_dd, horizon_event) = horizon_labels[ZERO]
                if dd_cumulative > horizon_dd:
                    remarks.append(horizon_event)
                    horizon_labels.pop(ZERO)
                else:
                    break
            rec['remark'] = '; '.join(remarks)
            unit.write(detail % rec)
        unit.write(content_epilog % data_items)
        unit.write(body_epilog % data_items)
        return self
    
    def zip_vectors(self):
        size = len(self.vectors['date'][ZERO])
        result = []
        while size:
            result.append({})
            size -= 1
        for key in [
                'date',
                'daily_max',
                'daily_min',
                'dd',
                'dd_cumulative',
                ]:
            (vals, units, unit_group) = self.vectors[key]
            for (ndx, val) in enumerate(vals):
                val_t = ValueTuple(val, units, unit_group)
                result[ndx][key] = weewx.units.ValueHelper(val_t, 'day', self.formatter, self.converter)
        horizon_labels = [(cumulative_dd, horizon_label) for ((cumulative_dd, dd_units, dd_group), horizon_label) in self.plot.horizons]
        horizon_labels.sort()
        for rec in result:
            remarks = []
            while horizon_labels:
                (horizon_dd, horizon_event) = horizon_labels[ZERO]
                #if rec['dd_cumulative'].raw > horizon_dd:
                cydiaA = rec['dd_cumulative'].raw
                if cydiaA > horizon_dd:
                    remarks.append(horizon_event)
                    horizon_labels.pop(ZERO)
                else:
                    break
            val_t = ValueTuple('; '.join(remarks), None, None)
            rec['remark'] = weewx.units.ValueHelper(val_t, 'day', self.formatter, self.converter)
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
    tdiff = time_dt -  time_dt.replace(hour=ZERO, minute=ZERO, second=ZERO, microsecond=ZERO)
    return abs(tdiff.seconds % aggregate_interval) > 1


class TimeHorizonPlot(weeplot.genplot.TimePlot):

    def _getScaledDraw(self, draw):
        """Returns an instance of ScaledDraw, with the appropriate scaling.
        
        draw: An instance of ImageDraw
        """
        sdraw = ScaledDrawText(
            draw,
            [
                (self.lmargin + self.padding, self.tmargin + self.padding),
                (self.image_width - self.rmargin - self.padding, self.image_height - self.bmargin - self.padding),
            ],
            [
                (self.xscale[0], self.yscale[0]),
                (self.xscale[1], self.yscale[1]),
            ],
            )
        return sdraw
        
    def render(self):
        """Traverses the universe of things that have to be plotted in this image, rendering
        them and returning the results as a new Image object.
        
        """

        # NB: In what follows the variable 'draw' is an instance of an ImageDraw object and is in pixel units.
        # The variable 'sdraw' is an instance of ScaledDraw and its units are in the "scaled" units of the plot
        # (e.g., the horizontal scaling might be for seconds, the vertical for degrees Fahrenheit.)
        image = weeplot.genplot.Image.new("RGB", (self.image_width, self.image_height), self.image_background_color)
        draw = self._getImageDraw(image)
        draw.rectangle(((self.lmargin,self.tmargin), 
                        (self.image_width - self.rmargin, self.image_height - self.bmargin)), 
                        fill=self.chart_background_color)

        self._renderBottom(draw)
        self._renderTopBand(draw)
        
        self._calcXScaling()
        self._calcYScaling()
        (lo, hi, step) = self.yscale
        self.yscale = (min(self.horizon_min, lo), max(self.horizon_max, hi), max(step, 100.0))
        self._calcXLabelFormat()
        self._calcYLabelFormat()
        
        sdraw = self._getScaledDraw(draw)
        if self.horizons:
            self._renderHorizons(sdraw)
        if self.show_daynight:
            self._renderDayNight(sdraw)
        self._renderXAxes(sdraw)
        self._renderYAxes(sdraw)
        for ((horizon, horizon_units, horizon_group), horizon_label) in self.horizons:
            self._renderHorizonLabel(sdraw, horizon, horizon_label)
        self._renderPlotLines(sdraw)
        if self.render_rose:
            self._renderRose(image, draw)

        if self.anti_alias != 1:
            image.thumbnail((self.image_width / self.anti_alias, self.image_height / self.anti_alias), Image.ANTIALIAS)

        return image
    
    def _renderHorizons(self, sdraw):
        """Draw horizontal bands for insect developmental stages and treatments.

        """
        
        self.horizons.sort()
        self.horizons.reverse()
        origin = self.yscale[ZERO]
        for ((horizon, horizon_units, horizon_group), horizon_label) in self.horizons:
            sdraw.rectangle([(self.xscale[ZERO],horizon), (self.xscale[1], self.yscale[ZERO])], fill=self.horizon_bottom_color)
            self._renderHorizonShading(sdraw, horizon, origin)
            sdraw.line((self.xscale[ZERO],self.xscale[1]), (horizon, horizon), fill=self.horizon_edge_color)
        return self

    def _renderHorizonShading(self, sdraw, top, bottom):
        """Draw horizontal shading.

        """
        
        shades = self.horizon_gradient
        overall_height = (self.yscale[1] - self.yscale[ZERO]) * 0.10
        stripe_height = overall_height / shades
        foreground_color = self.horizon_top_color
        background_color = self.horizon_bottom_color
        ndx = ZERO
        while ndx < shades:
            transparency = 1.0 - ndx / shades
            c = weeplot.genplot.blend_hls(self.horizon_top_color, self.horizon_bottom_color, transparency)
            rgbc = weeplot.genplot.int2rgbstr(c)
            y1 = top - ndx * stripe_height
            y2 = y1 - stripe_height
            y1 = min(y1, top)
            y2 = max(y2, bottom)
            sdraw.rectangle([(self.xscale[ZERO], y1), (self.xscale[1], y2)], fill=rgbc)
            ndx += 1
        return self

    def _renderHorizonLabel(self, sdraw, y_pos, txt):
        """Draw label.

        """

        horizon_label_font = weeplot.utilities.get_font_handle(self.horizon_label_font_path, self.horizon_label_font_size)
        (width, height) = sdraw.textsize(txt, font=horizon_label_font)
        label_offset = (self.horizon_label_offset / sdraw.xscale, self.horizon_label_offset / sdraw.yscale)
        sdraw.text(
            (self.xscale[ZERO] + label_offset[ZERO], y_pos - height - label_offset[1]),
            txt, 
            fill=self.horizon_label_font_color,
            font=horizon_label_font,
            )
        return self


class ScaledDrawText(weeplot.utilities.ScaledDraw):

    def text(self, position, *pos_args, **key_args):
        (x, y) = position
        pixels = (self.xtranslate(x), self.ytranslate(y))
        result = self.draw.text(pixels, *pos_args, **key_args)
        return result

    def textsize(self, *pos_args, **key_args):
        (width, height) = self.draw.textsize(*pos_args, **key_args)
        result = (width / self.xscale, height / self.yscale)
        return result

# =============================================================================
# CydiaReportGenerator
# =============================================================================

class CydiaReportGenerator(weewx.reportengine.ReportGenerator):
    
    """Class for generating files from cydia templates.
    
    Useful attributes (some inherited from ReportGenerator):

        config_dict:      The weewx configuration dictionary 
        skin_dict:        The dictionary for this skin
        gen_ts:           The generation time
        first_run:        Is this the first time the generator has been run?
        stn_info:         An instance of weewx.station.StationInfo
        record:           A copy of the "current" record. May be None.
        formatter:        An instance of weewx.units.Formatter
        converter:        An instance of weewx.units.Converter
        search_list_objs: A list holding search list extensions
                          
    """

#    generator_dict = {'SummaryByDay'  : weeutil.weeutil.genDaySpans,
#                      'SummaryByMonth': weeutil.weeutil.genMonthSpans,
#                      'SummaryByYear' : weeutil.weeutil.genYearSpans}
    
#    format_dict = {'SummaryByDay'  : "%Y-%m-%d",
#                   'SummaryByMonth': "%Y-%m",
#                   'SummaryByYear' : "%Y"}

    def run(self):
        
        """Main entry point for file generation using Cydia Templates.

        """

        t1 = time.time()

        self.setup()
        
        # Make a copy of the skin dictionary (we will be modifying it):
        gen_dict = configobj.ConfigObj(self.skin_dict.dict())
        
        # Look for options in [CydiaGenerator],
        cydia_dict = gen_dict["CydiaGenerator"]
        
        # determine how much logging is desired
        log_success = to_bool(cydia_dict.get('log_success', True))

        # configure the search list extensions
        self.initExtensions(cydia_dict)

        # Generate any templates in the given dictionary:
        ngen = ZERO
        for species_name in cydia_dict.sections:
            ngen += self.generate(cydia_dict, species_name)

        self.teardown()

        elapsed_time = time.time() - t1
        if log_success:
            loginf("Generated %d files for report %s in %.2f seconds" %
                   (ngen, self.skin_dict['REPORT_NAME'], elapsed_time))

    def setup(self):
        
        # This dictionary will hold the formatted dates of all generated files
        
#        self.outputted_dict = {}
#        for key in self.generator_dict.iter_keys():
#            self.outputted_dict[key] = []; 
        self.formatter = weewx.units.Formatter.fromSkinDict(self.skin_dict)
        self.converter = weewx.units.Converter.fromSkinDict(self.skin_dict)

    def initExtensions(self, gen_dict):
        
        """Load the search list

        """
        
        self.search_list_objs = []

        search_list = weeutil.weeutil.option_as_list(gen_dict.get('search_list'))
        if search_list is None:
            search_list = list(default_search_list)

        search_list_ext = weeutil.weeutil.option_as_list(gen_dict.get('search_list_extensions'))
        if search_list_ext is not None:
            search_list.extend(search_list_ext)

        # provide feedback about the requested search list objects
        logdbg("using search list %s" % search_list)

        # Now go through search_list (which is a list of strings holding the
        # names of the extensions):
        for c in search_list:
            x = c.strip()
            if x:
                # Get the class
                class_ = weeutil.weeutil._get_object(x)
                # Then instantiate the class, passing self as the sole argument
                self.search_list_objs.append(class_(self))
                
    def teardown(self):
        
        """Delete any extension objects we created to prevent back references
        from slowing garbage collection

        """
        
        while self.search_list_objs:
            self.search_list_objs.pop(NA)
            
    def generate(self, cydia_dict, species_name):
        
        """Generate one or more reports for the indicated species.

        species_dict: A ConfigObj dictionary, holding the templates to be
        generated.
        
        self.gen_ts: The report will be current to this time.
        
        """
        
        ngen = 0
        
        # Change directory to the skin subdirectory.  We use absolute paths
        # for cydia, so the directory change is not necessary for generating
        # files.  However, changing to the skin directory provides a known
        # location so that calls to os.getcwd() in any templates will return
        # a predictable result.
        
        os.chdir(os.path.join(self.config_dict['WEEWX_ROOT'],
                              self.skin_dict['SKIN_ROOT'],
                              self.skin_dict['skin']))

        report_dict = weeutil.weeutil.accumulateLeaves(cydia_dict[species_name])
        
        (template, dest_dir, encoding, default_binding) = self._prepGen(species_name, report_dict)
        (dest_file_name, tmpl_ext) = os.path.splitext(os.path.basename(template))
        dest_file = os.path.join(dest_dir, dest_file_name)

        # Get start and stop times
#        default_archive = self.db_binder.get_manager(default_binding)
        if self.recs:
            start_ts = self.recs[ZERO]['date'].raw
            stop_ts = self.recs[-1]['date'].raw
        else:
            loginf('Skipping template %s: cannot find start time' % section['template'])
            return ngen

#        if gen_ts:
#            record = default_archive.getRecord(gen_ts,
#                                               max_delta=to_int(report_dict.get('max_delta')))
#            if record:
#                stop_ts = record['dateTime']
#            else:
#                loginf('Skipping template %s: generate time %s not in database' % (section['template'], timestamp_to_string(gen_ts)) )
#                return ngen
#        else:
#            stop_ts = default_archive.lastGoodStamp()
        
#        # Get an appropriate generator function
#        summarize_by = report_dict['summarize_by']
#        if summarize_by in self.generator_dict:
#            _spangen = self.generator_dict[summarize_by]
#        else:
#            # Just a single timespan to generate. Use a lambda expression.
#            _spangen = lambda start_ts, stop_ts : [weeutil.weeutil.TimeSpan(start_ts, stop_ts)]

        # Use the generator function
        
#        for timespan in _spangen(start_ts, stop_ts):
#            start_tt = time.localtime(timespan.start)
#            stop_tt  = time.localtime(timespan.stop)

#            if summarize_by in self.Generator.format_dict:
#                # This is a "SummaryBy" type generation. If it hasn't been done already, save the
#                # date as a string, to be used inside the document
#                date_str = time.strftime(self.format_dict[summarize_by], start_tt)
#                if date_str not in self.outputted_dict[summarize_by]:
#                    self.outputted_dict[summarize_by].append(date_str)
#                # For these "SummaryBy" generations, the file name comes from the start of the timespan:
#                _filename = self._getFileName(template, start_tt)
#            else:
#                # This is a "ToDate" generation. File name comes 
#                # from the stop (i.e., present) time:
#                _filename = self._getFileName(template, stop_tt)

#            # Get the absolute path for the target of this template
#            _fullname = os.path.join(dest_dir, _filename)

#            # Skip summary files outside the timespan
#            if report_dict['summarize_by'] in self.generator_dict \
#                    and os.path.exists(_fullname) \
#                    and not timespan.includesArchiveTime(stop_ts):
#                continue

            # skip files that are fresh, but only if staleness is defined
        timespan = weeutil.weeutil.TimeSpan(start_ts, stop_ts)
        stale = to_int(report_dict.get('stale_age'))
        if stale is not None:
            t_now = time.time()
            try:
                last_mod = os.path.getmtime(dest_file)
                if t_now - last_mod < stale:
                    logdbg("Skip '%s': last_mod=%s age=%s stale=%s" %
                        (dest_file, last_mod, t_now - last_mod, stale))
                    return ngen
            except os.error:
                pass

        searchList = self._getSearchList(encoding, timespan, default_binding, species_name, report_dict)
        tmpname = dest_file + '.tmp'
            
        try:
            compiled_template = Cheetah.Template.Template(
                file=template,
                searchList=searchList,
                filter=encoding,
                filtersLib=weewx.cheetahgenerator)
            with open(tmpname, mode='w') as _file:
                print >> _file, compiled_template
            os.rename(tmpname, dest_file)
        except Exception, e:
            # We would like to get better feedback when there are cheetah
            # compiler failures, but there seem to be no hooks for this.
            # For example, if we could get make cheetah emit the source
            # on which the compiler is working, one could compare that with
            # the template to figure out exactly where the problem is.
            # In Cheetah.Compile.ModuleCompiler the source is manipulated
            # a bit then handed off to parserClass.  Unfortunately there
            # are no hooks to intercept the source and spit it out.  So
            # the best we can do is indicate the template that was being
            # processed when the failure ocurred.
            logerr("Generate failed with exception '%s'" % type(e))
            logerr("**** Ignoring template %s" % template)
            logerr("**** Reason: %s" % e)
            weeutil.weeutil.log_traceback("****  ")
        else:
            ngen += 1
        finally:
            try:
                os.unlink(tmpname)
            except OSError:
                pass
        return ngen

    def _getSearchList(self, encoding, timespan, default_binding, species_name, report_dict):
        """Get the complete search list to be used by Cydia."""

        spec_threshold_lo = report_dict.get('threshold_lo', [50, 'degree_F'])
        threshold_lo_t = get_float_t(spec_threshold_lo, 'group_temperature')
        spec_threshold_hi = report_dict.get('threshold_hi', [88, 'degree_F'])
        threshold_hi_t = get_float_t(spec_threshold_hi, 'group_temperature')
        
        # Get the basic search list
        searchList = [
            {'encoding': encoding},
            {'cydia':
                {
                'degree_days': self.recs,
                'datetime': self.recs[-1]['date'],
                'label': report_dict.get('label', species_name),
                'species_name': species_name,
                'threshold_lo': weewx.units.ValueHelper(threshold_lo_t, 'year', self.formatter, self.converter),
                'threshold_hi': weewx.units.ValueHelper(threshold_hi_t, 'year', self.formatter, self.converter),
                },
            }, 
#            self.outputted_dict,
            ]
        
#        # Bind to the default_binding:
        db_lookup = self.db_binder.bind_default(default_binding)
        
#        # Then add the V3.X style search list extensions
        for obj in self.search_list_objs:
            searchList += obj.get_extension_list(timespan, db_lookup)
        return searchList

#    def _getFileName(self, template, ref_tt):
#        """Calculate a destination filename given a template filename.
#        Replace 'YYYY' with the year, 'MM' with the month, 'DD' with the day.
#        Strip off any trailing .tmpl"""

#        _filename = os.path.basename(template).replace('.tmpl', '')

#        # If the filename contains YYYY, MM, or DD, then do the replacement
#        if 'YYYY' in _filename or 'MM' in _filename or 'DD' in _filename:
#            # Get strings representing year, month, and day
#            _yr_str  = "%4d"  % ref_tt[0]
#            _mo_str  = "%02d" % ref_tt[1]
#            _day_str = "%02d"  % ref_tt[2]
#            # Replace any instances of 'YYYY' with the year string
#            _filename = _filename.replace('YYYY', _yr_str)
#            # Do the same thing with the month...
#            _filename = _filename.replace('MM', _mo_str)
#            # ... and the day
#            _filename = _filename.replace('DD', _day_str)

#        return _filename

    def _prepGen(self, species_name, report_dict):
        
        """Get the template, destination directory, encoding, and default
        binding.

        """

        template_name = report_dict.get('template', "%s.html.tmpl" % species_name)
        # -------- Template ---------
        # Cheetah will crash if given a template file name in Unicode. So,
        # convert to ascii, ignoring all characters that cannot be converted:
        template = os.path.join(self.config_dict['WEEWX_ROOT'],
                                self.config_dict['StdReport']['SKIN_ROOT'],
                                report_dict['skin'],
                                template_name.encode('ascii', 'ignore'))

        # ------ Destination directory --------
        dest_dir = os.path.join(self.config_dict['WEEWX_ROOT'],
                                       report_dict['HTML_ROOT'],
                                       os.path.dirname(template_name))
        try:
            # Create the directory that is to receive the generated files.  If
            # it already exists an exception will be thrown, so be prepared to
            # catch it.
            os.makedirs(dest_dir)
        except OSError:
            pass

        # ------ Encoding ------
        encoding = report_dict.get('encoding', 'html_entities').strip().lower()
        if encoding == 'utf-8':
            encoding = 'utf8'

        # ------ Default binding ---------
        default_binding = report_dict['data_binding']

        return (template, dest_dir, encoding, default_binding)

