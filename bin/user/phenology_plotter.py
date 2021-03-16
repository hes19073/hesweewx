#!/usr/bin/python3

# phenology_plotter.py
# 2020 Dec 22 . ccr

# ==================================================boilerplate»=====
""" Low-Level and Not so Low-Level Charting Functions

This module is used by the Phenology Image Generator.

This script is distributed as part of the Phenology Extension to
WeeWX.  WeeWX is maintained by Tom Keffer and Matthew Wall.  This
script is maintained by Chuck Rhode although it may contain portions
copied from Keffer and Wall or directly inspired by them.

Copyright 2018—2021 by Chuck Rhode.

See LICENSE.txt for your rights.

# =================================================«boilerplate======

"""

import os
import time
# import logging
import collections
import locale
import PIL
import PIL.ImageDraw
import PIL.ImageOps
import PIL.ImageChops
import PIL.ImageFilter
import weeplot.utilities
import weeutil.weeutil

ZERO = 0
SPACE = ' '
NULL = ''
NUL = '\x00'
NA = -1

# LOG = logging.getLogger(__name__)


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


class Manifest(collections.OrderedDict):

    """This is an ordered list of items to be plotted.

    Obviously background items should be rendered before foreground
    features.

    The manifest is keyed by item handle.  Item handles must therefore
    be unique.  

    """

    pass


class Style(object):

    """This class has no methods.

    It holds any attributes that may be assigned.

    """

    pass


class Item(object):

    """This is the manifest-item base class.

    """

    def render_background(self, image, style):
        raise NotImplementedError

    def render_foreground(self, image, style):
        raise NotImplementedError

    def get_scale(self):
        raise NotImplementedError

    def set_scale(self, min_v, max_v, inc_v):
        raise NotImplementedError

    def get_min_max_y(self):
        raise NotImplementedError

    def get_min_max_x(self):
        raise NotImplementedError

    
class ImageBackground(Item):

    def render_background(self, image, style):

        """Color the background of the image outside the chart body.

        """
        
        rect_ul = (ZERO, ZERO)
        rect_lr = image.size
        rect = (rect_ul, rect_lr)
        image.draw_rect(
            rect,
            fill=style.image_background_color,
            )
        if style.image_background_pattern:
            pattern = style.cache.image_open_resize(style.image_background_pattern, image.size)
            image.compose(pattern)
        return self

    def render_foreground(self, image, style):
        rect_ul = (ZERO, ZERO)
        rect_lr = image.size
        rect = (rect_ul, rect_lr)
        if style.image_border_color:
            image.draw_rect(
                rect,
                outline=style.image_border_color,
                width=style.image_border,
                )
        return self


class ChartBackground(Item):

    def __init__(self, manifest):
        self.manifest = manifest
        return

    def get_chart_rect(self, img):
        (x_lo, x_hi) = self.manifest['axis_x'].get_scale()[:2]
        (y_lo, y_hi) = self.manifest['axis_y'].get_scale()[:2]
        rect_ll = (x_lo, y_lo)
        rect_ur = (x_hi, y_hi)
        rect = (rect_ll, rect_ur)
        rect_scaled = img.xlate_vect(rect)
        (rect_ll, rect_ur) = rect_scaled
        (x_lo, y_lo) = rect_ll
        (x_hi, y_hi) = rect_ur
        x_lo -= 1
        y_lo += 1
        x_hi += 1
        y_hi -= 1
        rect_ll = (x_lo, y_lo)
        rect_ur = (x_hi, y_hi)
        result = (rect_ll, rect_ur)
        return result

    def render_background(self, image, style):

        """Color the chart body.

        """

        rect = self.get_chart_rect(image)
        field = Img(image.size)
        field.draw_rect(rect, fill=style.chart_background_color)
        image.compose(field)
        if style.chart_background_pattern:
            pattern = style.cache.image_open_resize(style.chart_background_pattern, image.size)
            mask = Img(image.size, mode='L')
            mask.draw_rect(rect, fill='white')
            image.compose(pattern, mask)
        return self

    def render_foreground(self, image, style):
        rect = self.get_chart_rect(image)
        if style.chart_border_color:
            image.draw_rect(
                rect,
                outline=style.chart_border_color,
                width=style.chart_border,
                )
        return self


class AxisX(Item):

    def __init__(self, min_v=None, max_v=None, inc_v=None):
        self.set_scale(min_v, max_v, inc_v)
        return

    def set_scale(self, min_v, max_v, inc_v):
        self.min_v = min_v
        self.max_v = max_v
        self.inc_v = inc_v
        self.tics = weeutil.weeutil.stampgen(self.min_v, self.max_v, self.inc_v)
        return self

    def get_scale(self):
        result = (self.min_v, self.max_v, self.inc_v)
        return result

    def render_background(self, image, style):
        return self

    def render_foreground(self, image, style):

        def get_label_format():
            if style.axis_x_format is None:
                delta = self.max_v - self.min_v
                if delta > 30*24*3600:
                    result = "%x"
                elif delta > 24*3600:
                    result = "%x %X"
                else:
                    result = "%X"
            else:
                result = style.axis_x_format
            return result

        (width, height) = image.size
        label_font = weeplot.utilities.get_font_handle(style.axis_font_path, style.axis_font_size)
        label_format = get_label_format()
        count_label = ZERO
        for (count_label, x) in enumerate(self.tics):
            grid_x_v = (x, x)
            grid_y_v = image.scale_y[:2]
            image.scaled_draw_line(grid_x_v, grid_y_v, fill=style.chart_gridline_color, width=style.magnification)
            if count_label % style.axis_x_spacing == ZERO:
                time_tuple = time.localtime(x)
                label_x = time.strftime(label_format, time_tuple)
                label_size = image.draw_get_textsize(label_x, font=label_font)
                xpos = image.xlate_x(x)
                pos = (xpos - label_size[ZERO] / 2, height - style.margin_bottom + 2)
                image.draw_text(pos, label_x, fill=style.axis_font_color, font=label_font)
            count_label += 1
        return self


class AxisY(Item):

    def __init__(self, min_v=None, max_v=None, inc_v=None):
        self.set_scale(min_v, max_v, inc_v)
        return

    def set_scale(self, min_v, max_v, inc_v):
        self.min_v = min_v
        self.max_v = max_v
        self.inc_v = inc_v
        self.tics = []
        try:
            count_gridlines = int(((self.max_v - self.min_v) / self.inc_v) + 1 + 0.5)
        except TypeError:
            count_gridlines = ZERO
        ndx = ZERO
        while ndx < count_gridlines:
            y = self.min_v + ndx * self.inc_v
            self.tics.append(y)
            ndx += 1
        return self

    def get_scale(self):
        result = (self.min_v, self.max_v, self.inc_v)
        return result

    def render_background(self, image, style):
        return self

    def render_foreground(self, image, style):
        
        def get_label_format():
            if style.axis_y_format is None:
                result = weeplot.utilities.pickLabelFormat(self.inc_v)
            else:
                result = style.axis_y_format
            return result
        
        label_font = weeplot.utilities.get_font_handle(style.axis_font_path, style.axis_font_size)
        label_format = get_label_format()
        count_label = ZERO
        for (ndx, y) in enumerate(self.tics):
            grid_x_v = image.scale_x[:2]
            grid_y_v = (y, y)
            image.scaled_draw_line(grid_x_v, grid_y_v, fill=style.chart_gridline_color, width=style.magnification)
            if ndx % style.axis_y_spacing == ZERO:
                label_y = locale.format(label_format, y)
                label_size = image.draw_get_textsize(label_y, font=label_font)
                ypos = image.xlate_y(y)
                if style.axis_y_side == 'left' or style.axis_y_side == 'both':
                    pos = (style.margin_left - label_size[ZERO] - 2, ypos - label_size[1] / 2)
                if style.axis_y_side == 'right' or style.axis_y_side == 'both':
                    pos = (image.width - style.margin_right + 4, ypos - label_size[1] / 2)
                image.draw_text(pos, label_y, fill=style.axis_font_color, font=label_font)
        return self


class LabelX(Item):

    def __init__(self, label_text):
        self.label_text = label_text
        return

    def render_background(self, image, style):
        return self

    def render_foreground(self, image, style):
        label_font = weeplot.utilities.get_font_handle(style.label_x_font_path, style.label_x_font_size)
        label_size = image.draw_get_textsize(self.label_text, font=label_font)
        (width, height) = image.size
        pos = ((width - label_size[ZERO]) / 2, height - label_size[1] - style.label_x_offset)
        image.draw_text(pos, self.label_text, fill=style.label_x_font_color, font=label_font)
        return self


class LabelY(Item):

    def __init__(self, label_text):
        self.label_text = label_text
        return

    def render_background(self, image, style):
        return self

    def render_foreground(self, image, style):
        label_font = weeplot.utilities.get_font_handle(style.label_y_font_path, style.label_y_font_size)
        if self.label_text:
            if style.axis_y_side == 'left' or style.axis_y_side == 'both':
                image.draw_text(style.label_y_position, self.label_text, fill=style.label_y_font_color, font=label_font)
            if style.axis_y_side == 'right' or style.axis_y_side == 'both':
                label_position_right = (self.image_width - self.margin_right + 4, ZERO)  # Should this offset be magnified?
                iamge.draw_text(label_position_right, self.label_text, fill=self.label_y_font_color, font=label_font)
        return self


class Title(Item):

    def __init__(self, title_text):
        self.title_text = title_text
        return

    def render_background(self, image, style):
        return self

    def render_foreground(self, image, style):

        """Finish drawing the top band.

        In the Seasons skin, the top band is not a single title but a
        colored list of plotted variables.  

        Thus, a chart Title, as such, is not implemented.

        """

        return self


class SeasonsTitle(Item):

    """Generate the title part of the top band.

    The top label is the concatentated label_list. However, it has to
    be drawn in segments because each label may be in a different
    color.

    """

    def __init__(self, lines, manifest):
        self.lines = lines
        self.manifest = manifest
        return

    def render_background(self, image, style):
        return self

    def render_foreground(self, image, style):
        (width, height) = image.size
        label_font = weeplot.utilities.get_font_handle(style.top_label_font_path, style.top_label_font_size)
        line_names = []
        for (ndx, (line_handle, line_name, stages)) in enumerate(self.lines):
            line_names.append(line_name)
        label = SPACE.join(line_names)
        label_size = image.draw_get_textsize(label, font=label_font)
        off_x = (width - label_size[ZERO]) / 2
        off_y = ZERO
        count_colors = len(style.chart_line_colors)
        for (ndx, (line_handle, line_name, stages)) in enumerate(self.lines):
            line = self.manifest[line_handle]
            color_bgr = line.color_bgr
            pos = (off_x, off_y)
            image.draw_text(pos, line_name, fill=color_bgr, font=label_font)
            label_size = image.draw_get_textsize(line_name + SPACE, font=label_font)
            off_x += label_size[ZERO]
        return self


class DayNightShading(Item):

    def set_parms(self, **parms):
        for (key, val) in parms.items():
            setattr(self, key, val)
        (self.min_x, self.max_x) = self.scale_x[:2]
        (self.min_y, self.max_y) = self.scale_y[:2]
        return

    def render_background(self, image, style):

        """Render the day/night shading on the chart background.

        This is complicated because gradients can't be scaled
        apparently.  They have to be rendered onto the unscaled image.

        """

        def init_color_ndx(first):
            if first in ['day']:
                result = ZERO
            else:
                result = 1
            return result

        def swap_color_ndx(ndx):
            result = 1 - ndx
            return result

        def draw_rect(mask_day, prev_x, x, color_ndx):

            """Draw a rectangle.

            """
            
            rect_ll = (prev_x, self.min_y)
            rect_ur = (x, self.max_y)
            rect = (rect_ll, rect_ur)
            mask_day.scaled_draw_rect(rect, fill=day_night_colors[color_ndx])
            return

        def draw_gradient(mask_day, x, twilight_secs, color_ndx):

            """Feather the edges of the rectangle.

            """

            if color_ndx:
                rotation = 90
            else:
                rotation = -90
            width = twilight_secs
            height = self.max_y - self.min_y
            size = (width, height)
            scaled_size = mask_day.xlate_size(size)
            gradient_day = ImgGradient(size=scaled_size, degrees_counter_clockwise=rotation)
            pos_x = x - twilight_secs / 2.0
            pos_y = self.max_y
            pos = (pos_x, pos_y)
            scaled_pos = mask_day.xlate_point(pos)
            mask_day.punch(pattern=gradient_day, offset_into_image=scaled_pos)
            return

        def render_day_night():
            color_ndx = init_color_ndx(first)
            prev_x = self.min_x
            for x in transitions:
                draw_rect(mask_day, prev_x, x, color_ndx)
                color_ndx = swap_color_ndx(color_ndx)
                prev_x = x
            else:
                draw_rect(mask_day, prev_x, self.max_x, color_ndx)
            return

        def render_twilight():
            twilight_secs = 2400.0 + (6000.0 * abs(self.lat) / 90.0)
            color_ndx = init_color_ndx(first)
            for x in transitions:
                draw_gradient(mask_day, x, twilight_secs, color_ndx)
                color_ndx = swap_color_ndx(color_ndx)
            return

        def draw_edges():
            if self.color_edge:
                for x in transitions:
                    x_v = (x, x)
                    y_v = (self.min_y, self.max_y)
                    image.scaled_draw_line(array_x=x_v, array_y=y_v, fill=self.color_edge, width=style.magnification)
            return

        day_night_colors = ['white', 'black']
        mask_night = Img(size=image.size, mode='L')
        mask_night.clone_scale(image)
        draw_rect(mask_night, self.min_x, self.max_x, color_ndx = ZERO)
        mask_day = Img(size=image.size, mode='L')
        mask_day.clone_scale(image)
        (first, transitions) = weeutil.weeutil.getDayNightTransitions(
            self.min_x,
            self.max_x,
            self.lat,
            self.lon,
            )
        render_day_night()
        render_twilight()
        gray_mask_night = mask_night.get_as_grayscale()
        gray_mask_day = mask_day.get_as_grayscale()
        field = Img(image.size)
        field.punch(pattern=self.color_night, mask=gray_mask_night)
        field.punch(pattern=self.color_day, mask=gray_mask_day)
        image.compose(field)
        if None in [self.pattern_night, self.pattern_day]:
            pass
        else:
            pattern = style.cache.image_open_resize(self.pattern_night, image.size)
            image.compose(pattern, mask=gray_mask_night)
            pattern = style.cache.image_open_resize(self.pattern_day, image.size)
            image.compose(pattern, mask=gray_mask_day)
        draw_edges()
        return self

    def render_foreground(self, image, style):
        return self


class Line(Item):

    def __init__(
            self,
            seq,
            array_x,
            array_y,
            gap_fraction,
            color_bgr,
            can_fill_curve,
            fill_color_bgr,
            pattern,
            stroke_width,
            line_type,
            marker_type,
            marker_size,
            ):
        self.seq = seq
        self.array_x = array_x
        self.array_y = array_y
        self.gap_fraction = gap_fraction
        self.color_bgr = color_bgr
        self.can_fill_curve = can_fill_curve
        self.fill_color_bgr = fill_color_bgr
        self.pattern = pattern
        self.stroke_width = stroke_width
        self.line_type = line_type
        self.marker_type = marker_type
        self.marker_size = marker_size
        return

    def render_background(self, image, style):

        """Draw shading under a curve.

        NB:  This method side-affects self.color_bgr and self.fill_color_bgr.

        """

        def draw_color(img, color):
            x_y = [(v_x, v_y) for (v_x, v_y) in zip(self.array_x, self.array_y) if v_y]
            if x_y:
                (x_first, y_first) = x_y[ZERO]
                (x_last, y_last) = x_y[-1]
                x = []
                y = []
                x.append(x_first)
                y.append(y_min)
                for (v_x, v_y) in x_y:
                    x.append(v_x)
                    y.append(v_y)
                x.append(x_last)
                y.append(y_min)
                img.scaled_draw_polygon(
                    x, y,
                    fill=color,
                    )
            return

        count_colors = len(style.chart_line_colors)
        if self.color_bgr is None:
            self.color_bgr = style.chart_line_colors[self.seq % count_colors]
        count_fill_colors = len(style.chart_fill_colors)
        if self.fill_color_bgr is None:
            self.fill_color_bgr = style.chart_fill_colors[self.seq % count_fill_colors]
        (x_min, x_max) = image.scale_x[:2]
        (y_min, y_max) = image.scale_y[:2]
        if self.can_fill_curve:
            mask = Img(image.size, mode='L')
            mask.clone_scale(image)
            draw_color(mask, 'white')
            field = Img(image.size, mode='RGBA')
            field.fill(self.fill_color_bgr)
            image.compose(field, mask)
            if self.pattern:
                pattern = style.cache.image_open_resize(self.pattern, image.size)
                image.compose(pattern, mask)
        return self

    def render_foreground(self, image, style):

        """Draw a curve.

        """

        def draw_outline():
            mask = Img(size=image.size)
            mask.clone_scale(image)
            mask.scaled_draw_line(
                self.array_x,
                self.array_y,
                line_type=self.line_type,
                marker_type=self.marker_type,
                marker_size=marker_size,
                fill  = 'White',
                width = 1,
                maxdx = max_delta_x,
                )
            if stroke_width == 1:
                pass
            else:
                mask = mask.get_as_dilated(stroke_width)
            image.punch(self.color_bgr, mask)
            return

        try:
            marker_size = self.marker_size * style.magnification
        except ValueError:
            marker_size = None
        (x_min, x_max) = image.scale_x[:2]
        (y_min, y_max) = image.scale_y[:2]
        count_line_widths = len(style.chart_line_widths)
        if self.stroke_width is None:
            stroke_width = style.chart_line_widths[self.seq % count_line_widths]
        else:
            stroke_width = self.stroke_width
        if self.gap_fraction is None:
            max_delta_x = None
        else:
            max_delta_x = (x_max - x_min) * self.gap_fraction
        draw_outline()
        return self

    def get_min_max_y(self):
        line_min_y = weeutil.weeutil.min_with_none(self.array_y)
        line_max_y = weeutil.weeutil.max_with_none(self.array_y)
        result = (line_min_y, line_max_y)
        return result

    def get_min_max_x(self):
        line_min_x = weeutil.weeutil.min_with_none(self.array_x)
        line_max_x = weeutil.weeutil.max_with_none(self.array_x)
        result = (line_min_x, line_max_x)
        return result
    
    
class BarsVertical(Line):

    def __init__(
            self,
            seq,
            array_x,
            array_y,
            bar_widths,
            color_bgr,
            fill_color_bgr,
            pattern,
            stroke_width,
            ):
        self.seq = seq
        self.array_x = array_x
        self.array_y = array_y
        self.bar_widths = bar_widths
        self.color_bgr = color_bgr
        self.fill_color_bgr = fill_color_bgr
        self.pattern = pattern
        self.stroke_width = stroke_width
        return

    def render_background(self, image, style):
        
        """Draw bar plot shading.

        NB:  This method side-affects self.color_bgr and self.fill_color_bgr.

        """

        def draw_color(img, color):
            for (x, y, bar_width) in zip(self.array_x, self.array_y, self.bar_widths):
                if y is None:
                    pass
                else:
                    rect_ll = (x - bar_width, min_y)
                    rect_ur = (x, y)
                    rect = (rect_ll, rect_ur)
                    img.scaled_draw_rect(
                        rect,
                        fill=color,
                        )
            return                

        count_colors = len(style.chart_line_colors)
        if self.color_bgr is None:
            self.color_bgr = style.chart_line_colors[self.seq % count_colors]
        count_fill_colors = len(style.chart_fill_colors)
        if self.fill_color_bgr is None:
            self.fill_color_bgr = style.chart_fill_colors[self.seq % count_fill_colors]
        (min_y, max_y) = image.scale_y[:2]
        mask = Img(image.size, mode='L')
        mask.clone_scale(image)
        draw_color(mask, 'white')
        field = Img(image.size, mode='RGBA')
        field.fill(self.fill_color_bgr)
        image.compose(field, mask)
        if self.pattern:
            pattern = style.cache.image_open_resize(self.pattern, image.size)
            image.compose(pattern, mask)
        return self

    def render_foreground(self, image, style):
        
        """Draw bar plot.

        """

        def draw_outline():
            for (x, y, bar_width) in zip(self.array_x, self.array_y, self.bar_widths):
                if y is None:
                    pass
                else:
                    rect_ll = (x - bar_width, min_y)
                    rect_ur = (x, y)
                    rect = (rect_ll, rect_ur)
                    image.scaled_draw_rect(
                        rect,
                        outline=self.color_bgr,
                        width = stroke_width,
                        )
            return

        count_line_widths = len(style.chart_line_widths)
        if self.stroke_width is None:
            stroke_width = style.chart_line_widths[self.seq % count_line_widths]
        else:
            stroke_width = self.stroke_width
        (min_y, max_y) = image.scale_y[:2]
        draw_outline()
        return self

    def get_min_max_x(self):
        line_min_x = weeutil.weeutil.min_with_none(self.array_x) - self.bar_widths[ZERO]
        line_max_x = weeutil.weeutil.max_with_none(self.array_x)
        result = (line_min_x, line_max_x)
        return result
    

class Wind(Line):

    def __init__(
            self,
            seq,
            array_x,
            array_y,
            vector_rotate,
            color_bgr,
            stroke_width,
            ):
        self.seq = seq
        self.array_x = array_x
        self.array_y = array_y
        self.vector_rotate = vector_rotate
        self.color_bgr = color_bgr
        self.stroke_width = stroke_width
        return

    def render_background(self, image, style):
        return self

    def render_foreground(self, image, style):

        """Draw progressive vector chart.

        """
        
        count_colors = len(style.chart_line_colors)
        if self.color_bgr is None:
            self.color_bgr = style.chart_line_colors[self.seq % count_colors]
        count_line_widths = len(style.chart_line_widths)
        if self.stroke_width is None:
            stroke_width = style.chart_line_widths[self.seq % count_line_widths]
        else:
            stroke_width = self.stroke_width
        for (x, vec) in zip(self.array_x, self.array_y):
            image.scaled_draw_vect(
                x, vec,
                rotate=self.vector_rotate,
                fill=self.color_bgr,
                width=self.stroke_width,
                )
        return self

    def get_min_max_y(self):
        try:
            vectors = [v for v in self.array_y if not (v is None)]
            magnitudes = [abs(v_complex) for v_complex in vectors]
            line_max_y = max(magnitudes)
            line_min_y = -line_max_y
        except ValueError:
            line_max_y = None
            line_min_y = None
        result = (line_min_y, line_max_y)
        return result


class Horizon(Item):

    def __init__(self, y_t_range, stage_label):
        y_lo_hi = y_t_range[:]  # a copy.
        y_lo_hi.sort()
        (y_lo_t, y_hi_t) = ([None] + y_lo_hi)[-2:]
        self.y_hi = y_hi_t[ZERO]
        if y_lo_t:
            self.y_lo = y_lo_t[ZERO]
        else:
            self.y_lo = None
        self.stage_label = stage_label
        return

    def render_background(self, image, style):
        return self

    def render_foreground(self, image, style):

        """Draw a labeled horizon line and shading.

        """
        
        def get_gradient():
            (x_min, x_max) = image.scale_x[:2]
            width = image.xlate_x(x_max) - image.xlate_x(x_min)
            height = style.horizon_shading
            size = (width, height)
            gradient = ImgGradient(size, 180).get_as_grayscale()
            if self.y_lo:
                height = image.xlate_y(self.y_lo) - image.xlate_y(self.y_hi)
            size = (width, height)
            result = Img(size, mode='L')
            result.punch('White', mask=gradient)
            if self.y_lo:
                result = result.get_as_rotated(180)
                result.punch('White', mask=gradient)
                result = result.get_as_rotated(180)
            return result

        def draw_gradient():
            gradient = get_gradient()
            field = Img(gradient.size)
            field.fill(style.horizon_shading_color)
            (x_min, x_max) = image.scale_x[:2]
            pos = (x_min, self.y_hi)
            pos = image.xlate_point(pos)
            image.compose(field, mask=gradient, offset_into_image=pos)
            return

        def draw_edges():
            (x_min, x_max) = image.scale_x[:2]
            x_v = image.scale_x[:2]
            y_v = (self.y_hi, self.y_hi)
            image.scaled_draw_line(array_x=x_v, array_y=y_v, fill=style.horizon_edge_color, width=style.magnification)
            if self.y_lo:
                y_v = (self.y_lo, self.y_lo)
                image.scaled_draw_line(array_x=x_v, array_y=y_v, fill=style.horizon_edge_color, width=style.magnification)
            return

        def draw_text():
            (x_min, x_max) = image.scale_x[:2]
            label_font = weeplot.utilities.get_font_handle(style.horizon_font_path, style.horizon_font_size)
            label_size = image.draw_get_textsize(self.stage_label, font=label_font)
            pos_x = image.xlate_x(x_min) + style.horizon_label_padding
            pos_y = image.xlate_y(self.y_hi) - label_size[1] - style.horizon_label_padding
            pos = (pos_x, pos_y)
            image.draw_text(pos, self.stage_label, fill=style.horizon_font_color, font=label_font)
            return

        if self.y_hi:
            draw_gradient()
            draw_edges()
            draw_text()
        return self

    
class Legend(Item):

    def __init__(self, text, line):
        self.text = text
        self.line = line
        return

    def render_background(self, image, style):
        return self

    def render_foreground(self, image, style):

        """Draw a legend segment.

        Doing this demands space inside or outside the chart frame.
        How to allocate this space is uncertain so drawing this item
        is not implemented, yet.

        """
        
        return self


class CompassRose(Item):

    def __init__(self, vector_rotate):
        self.vector_rotate = vector_rotate
        return

    def render_background(self, image, style):
        try:
            rose_mask = ImgOpen(style.rose_mask_path)
        except FileNotFoundError:
            rose_mask = None
        if rose_mask is None:
            pass
        else:
            if self.vector_rotate:
                rose_mask = rose_mask.get_as_rotated(self.vector_rotate)
            size = (style.rose_width, style.rose_height)
            mask = rose_mask.get_as_resized(size)
            image.punch(style.rose_color, mask, offset_into_image=style.rose_pos)
        return self

    def render_foreground(self, image, style):
        return self


class Chart(object):

    def __init__(self, config_dict, cache):
        self.manifest = Manifest()
        self.style = Style()
        self.style.cache = cache
        self.style.magnification = int(config_dict.get('anti_alias',  1))
        self.image_width = int(config_dict.get('image_width',  300)) * self.style.magnification
        self.image_height = int(config_dict.get('image_height', 180)) * self.style.magnification
        self.style.image_border = int(config_dict.get('image_border', 2)) * self.style.magnification
        self.style.image_border_color = to_rgb(config_dict.get('image_border_color'))
        self.style.image_background_color = to_rgb(config_dict.get('image_background_color', '#f5f5f5'))
        self.style.image_background_pattern = config_dict.get('image_background_pattern')
        self.manifest['image_background'] = ImageBackground()
        self.style.chart_border = int(config_dict.get('chart_border', 2)) * self.style.magnification
        self.style.chart_border_color = to_rgb(config_dict.get('chart_border_color'))
        self.style.chart_background_color = to_rgb(config_dict.get('chart_background_color', '#d8d8d8'))
        self.style.chart_background_pattern = config_dict.get('chart_background_pattern')
        self.manifest['chart_background'] = ChartBackground(manifest=self.manifest)
        self.style.chart_gridline_color = to_rgb(config_dict.get('chart_gridline_color',   '#a0a0a0'))
        color_list = config_dict.get('chart_line_colors', ['#ff0000', '#00ff00', '#0000ff'])
        fill_color_list = config_dict.get('chart_fill_colors', color_list)
        width_list = config_dict.get('chart_line_width',  [1, 1, 1])
        self.style.chart_line_colors = [to_rgb(v) for v in color_list]
        self.style.chart_fill_colors = [to_rgb(v) for v in fill_color_list]
        self.style.chart_line_widths = [int(v) for v in width_list]
        self.style.top_label_font_path = config_dict.get('top_label_font_path')
        self.style.top_label_font_size = int(config_dict.get('top_label_font_size', 10)) * self.style.magnification
        self.style.label_y_font_path = config_dict.get('unit_label_font_path')
        self.style.label_y_font_color = to_rgb(config_dict.get('unit_label_font_color', '#000000'))
        self.style.label_y_font_size = int(config_dict.get('unit_label_font_size', 10)) * self.style.magnification
        self.style.label_y_position = (10 * self.style.magnification, ZERO)
        self.style.label_x_font_path = config_dict.get('bottom_label_font_path')
        self.style.label_x_font_color= to_rgb(config_dict.get('bottom_label_font_color', '#000000'))
        self.style.label_x_font_size = int(config_dict.get('bottom_label_font_size', 10)) * self.style.magnification
        self.style.label_x_offset = int(config_dict.get('bottom_label_offset', 3))
        self.style.axis_font_path = config_dict.get('axis_label_font_path')
        self.style.axis_font_color = to_rgb(config_dict.get('axis_label_font_color', '#000000'))
        self.style.axis_font_size = int(config_dict.get('axis_label_font_size', 10)) * self.style.magnification
        self.style.axis_x_format = config_dict.get('x_label_format')
        self.style.axis_y_format = config_dict.get('y_label_format')
        self.style.nticks_y = int(config_dict.get('y_nticks', 10))
        self.style.axis_x_spacing = int(config_dict.get('x_label_spacing', 2))
        self.style.axis_y_spacing = int(config_dict.get('y_label_spacing', 2))
        self.style.axis_y_side = config_dict.get('y_label_side', 'left')
        if self.style.axis_y_side == 'left' or self.style.axis_y_side == 'both':
            self.style.margin_left = int(4.0 * self.style.axis_font_size)
        else:
            self.style.margin_left = 20 * self.style.magnification
        if self.style.axis_y_side == 'right' or self.style.axis_y_side == 'both':
            self.style.margin_right = int(4.0 * self.style.axis_font_size)
        else:
            self.style.margin_right = 20 * self.style.magnification
        self.style.margin_bottom = int(1.5 * (self.style.label_x_font_size + self.style.axis_font_size) + 0.5)
        self.style.margin_top = int(1.5 * self.style.top_label_font_size + 0.5)
        self.style.top_band_height = int(1.2 * self.style.top_label_font_size + 0.5)
        self.style.padding =  3 * self.style.magnification
        self.style.rose_mask_path = config_dict.get('rose_mask')
        self.style.rose_width = int(config_dict.get('rose_width', 60)) * self.style.magnification
        self.style.rose_height = int(config_dict.get('rose_height', 60)) * self.style.magnification
        pos_ul_x = self.style.margin_left + self.style.padding + 5
        pos_ul_y = self.image_height - self.style.margin_bottom - self.style.padding - self.style.rose_height
        self.style.rose_pos = (pos_ul_x, pos_ul_y)
        self.style.rose_color = to_rgb(config_dict.get('rose_color', '#ff220077'))
        self.style.horizon_font_path = config_dict.get('horizon_label_font_path')
        self.style.horizon_font_color = to_rgb(config_dict.get('horizon_label_font_color', '#ff0000'))
        self.style.horizon_font_size = int(config_dict.get('horizon_label_font_size', 12)) * self.style.magnification
        self.style.horizon_label_padding = int(config_dict.get('horizon_label_padding', 1)) * self.style.magnification
        self.style.horizon_shading = int(config_dict.get('horizon_shading', 15)) * self.style.magnification
        self.style.horizon_shading_color = to_rgb(config_dict.get('horizon_shading_color', '#ffbbbb'))
        self.style.horizon_edge_color = to_rgb(config_dict.get('horizon_edge_color', '#ff0000'))
        for key in [
                'image_border_color',
                'image_background_color',
                'image_background_pattern',
                'chart_border_color',
                'chart_background_color',
                'chart_background_pattern',
                'chart_gridline_color',
                'top_label_font_path',
                'label_x_font_path',
                'label_y_font_path',
                'axis_font_path',
                'axis_x_format',
                'axis_y_format',
                'rose_mask_path',
                'rose_color',
                'horizon_font_path',
                'horizon_font_color',
                'horizon_shading_color',
                'horizon_edge_color',
                ]:
            path = getattr(self.style, key)
            if is_empty(path):
                setattr(self.style, key, None)
        skin_dir = config_dict.get('skin_dir', NULL)
        for key in [
                'image_background_pattern',
                'chart_background_pattern',
                'top_label_font_path',
                'label_x_font_path',
                'label_y_font_path',
                'axis_font_path',
                'rose_mask_path',
                'horizon_font_path',
            ]:
            path = getattr(self.style, key)
            if path:
                setattr(self.style, key, self.normalize_path(skin_dir, path))
        return
    
    def normalize_path(self, skin_dir, path):
        if path is None:
            result = None
        else:
            result = os.path.join(skin_dir, path)
        return result

    def render(self):

        """Traverse the manifest.
        
        Return a new image object.

        """

        size = (self.image_width, self.image_height)
        result = Img(size)
        scale_x = self.manifest['axis_x'].get_scale()
        scale_y = self.manifest['axis_y'].get_scale()
        margin_ul = (self.style.margin_left, self.style.margin_top)
        margin_lr = (self.style.margin_right, self.style.margin_bottom)
        margins = (margin_ul, margin_lr)
        padding = self.style.padding
        result.set_scale(scale_x, scale_y, margins, padding)
        for item in self.manifest.values():
            item.render_background(result, self.style)
        for item in self.manifest.values():
            item.render_foreground(result, self.style)
        return result


class SeasonsTimePlot(Chart):

    pass


class Img(object):

    """Encapsulate PIL.Image, PIL.ImageDraw, and
    weeplot.utilities.ScaledDraw objects as a single über object.

    This object exposes ALL THE IMAGE-MANIPULATION METHODS YOU NEED!

    That's right ... without having to worry so much about which
    accursed object class they reside in.  It would be nicer, of
    course, if subclassing PIL.Image were easier, but it doesn't
    appear to be.

    """
    
    def __init__(self, size, mode='RGBA'):

        """Create a new black transparent image.

        """
        
        self.size = size
        self.image = PIL.Image.new(mode, size)
        self.draw = None
        self.scale_x = None
        self.scale_y = None
        self.sdraw = None
        return

    def get_image_attribute(self, obj):

        """Return the image attribute of an Img object.

        We aim to pass around Img objects as though they were
        PIL.Image objects.  If we need the PIL.Image, we can get it.

        """
        
        if hasattr(obj, 'image'):
            result = obj.image
        else:
            result = obj
        return result

    def set_draw(self):

        """Get a drawing object on the image.

        This is late-evaluated in case we don't need it.  If we've
        done it already, we don't do it again.

        """
        
        if self.draw is None:
            self.draw = PIL.ImageDraw.ImageDraw(self.image)
        return self

    def set_scale(self, scale_x, scale_y, margins=((ZERO, ZERO), (ZERO, ZERO)), padding=ZERO):
        ((margin_left, margin_top), (margin_right, margin_bottom)) = margins
        (image_width, image_height) = self.size
        image_point_ul = (margin_left + padding, margin_top + padding)
        image_point_lr = (image_width - margin_right - padding,
                        image_height - margin_bottom - padding)
        image_vect = (image_point_ul, image_point_lr)
        self.scale_x = scale_x
        self.scale_y = scale_y
        scale_point_ll = (self.scale_x[ZERO], self.scale_y[ZERO])
        scale_point_ur = (self.scale_x[1], self.scale_y[1])
        scale_vect = (scale_point_ll, scale_point_ur)
        self.set_draw()
        self.sdraw = ScaledDrawingWithPolygon(self.draw, image_vect, scale_vect)
        return self

    def clone_scale(self, other_img):
        self.set_draw()
        self.sdraw = ScaledDrawingCloned(self.draw, other_img.sdraw)
        return self

    def xlate_x(self, x):
        result = self.sdraw.xtranslate(x)
        return result

    def xlate_y(self, y):
        result = self.sdraw.ytranslate(y)
        return result

    def xlate_point(self, point):
        (x, y) = point
        result = (self.xlate_x(x), self.xlate_y(y))
        return result
    
    def xlate_vect(self, vect):
        (point_1, point_2) = vect
        result = (self.xlate_point(point_1), self.xlate_point(point_2))
        return result

    def xlate_size(self, size):
        box = self.xlate_vect([(ZERO, ZERO), size])
        ((box_ll_x, box_ll_y), (box_ur_x, box_ur_y)) = box
        result = (int(box_ur_x - box_ll_x) + 1, int(box_ll_y - box_ur_y) + 1)
        return result

    def get_as_rotated(self, degrees_counter_clockwise, **options):
        result = ImgCast(self.image.rotate(degrees_counter_clockwise, **options))
        return result

    def get_as_resized(self, size, **options):
        result = ImgCast(self.image.resize(size, **options))
        return result

    def get_as_inverted(self):
        result = ImgCast(PIL.ImageOps.invert(self.image))
        return result

    def get_as_grayscale(self):
        result = ImgCast(PIL.ImageOps.grayscale(self.image))
        return result

    def get_as_dilated(self, filter_size=3):
        if filter_size in [1]:
            filter_size = 1
        elif filter_size in [2, 3, 4]:
            filter_size = 3
        else:
            filter_size = 5
        filter_dilate = PIL.ImageFilter.MaxFilter(filter_size)
        result = ImgCast(self.image.filter(filter_dilate))
        return result

    def get_alpha(self):

        """Get alpha transparency layer.

        """
        
        result = self.image.getchannel('A')
        return result

    def put_alpha(self, mask):

        """Set alpha transparency layer to mask.

        """
        
        self.image.putalpha(self.get_image_attribute(alpha=mask))
        return self

    def compose(
            self,
            overlay,
            mask=None,
            offset_into_image=(ZERO, ZERO),
            offset_into_overlay=(ZERO, ZERO),
            ):
        overlay_image = self.get_image_attribute(overlay)
        copy_image = overlay_image.copy()
        if mask:
            mask_image = self.get_image_attribute(mask)
            copy_alpha = copy_image.getchannel('A')
            new_alpha = PIL.ImageChops.multiply(copy_alpha, mask_image)
            copy_image.putalpha(new_alpha)
        self.image.alpha_composite(
            copy_image,
            dest=offset_into_image,
            source=offset_into_overlay,
            )
        return self

    def fill(self, color):
        (x, y) = self.size
        box = (ZERO, ZERO, x, y)
        self.punch(pattern=color, offset_into_image=box)
        return self

    def punch(self, pattern, mask=None, offset_into_image=(ZERO, ZERO)):
        self.image.paste(
            self.get_image_attribute(pattern),
            mask=self.get_image_attribute(mask),
            box=offset_into_image,
            )
        return self

    def draw_rect(self, rect, fill=None, outline=None, width=1):
        self.set_draw()
        self.draw.rectangle(rect, fill=fill, outline=outline, width=width)
        return self

    def draw_text(self, pos, txt, **options):
        self.set_draw()
        self.draw.text(pos, txt, **options)
        return self

    def draw_get_textsize(self, txt, font=None, **options):
        self.set_draw()
        result = self.draw.textsize(txt, font=font, **options)
        return result

    def scaled_draw_rect(self, rect, **options):
        self.sdraw.rectangle(box=rect, **options)
        return self

    def scaled_draw_line(self, array_x, array_y, **options):
        self.sdraw.line(array_x, array_y, **options)
        return self

    def scaled_draw_polygon(self, array_x, array_y, **options):
        self.sdraw.polygon(array_x, array_y, **options)
        return self

    def scaled_draw_vect(self, array_x, array_v, rotate, **options):
        self.sdraw.vector(array_x, array_v, vector_rotate=rotate, **options)
        return self

    def save(self, path, **options):
        self.image.save(path, **options)
        return self


class ImgGradient(Img):

    """Create a gray gradient.

    """

    def __init__(self, size, degrees_counter_clockwise=ZERO):
        image = PIL.Image.linear_gradient('L').rotate(degrees_counter_clockwise)
        self.size = size
        self.image = image.resize(size)
        self.draw = None
        self.scale_x = None
        self.scale_y = None
        self.sdraw = None
        return

    
class ImgCast(Img):

    """Cast an image as an Img object.

    """

    def __init__(self, image):
        self.image = self.get_image_attribute(image)
        self.size = (self.image.width, self.image.height)
        self.draw = None
        self.scale_x = None
        self.scale_y = None
        self.sdraw = None
        return

    
class ImgOpen(Img):

    """Open an image file.

    """

    def __init__(self, image_path):
        self.image = PIL.Image.open(image_path)
        self.size = (self.image.width, self.image.height)
        self.draw = None
        self.scale_x = None
        self.scale_y = None
        self.sdraw = None
        return


class Cache(collections.OrderedDict):

    def image_open_resize(self, image_path, size):
        cache_key = '{} {}'.format(image_path, size)
        if cache_key in self:
#            LOG.error('cache hit')
            result = self[cache_key]
        else:
            pattern = ImgOpen(image_path)
            result = pattern.get_as_resized(size)
            self[cache_key] = result
#            LOG.error('cache miss, len(cache):  {}, cache_key:  {}'.format(len(self), cache_key))
            if len(self) > 3:
                self.popitem(last=False)
        return result


class ScaledDrawingWithPolygon(weeplot.utilities.ScaledDraw):

    def polygon(self, x, y, fill=None, outline=None, **options):
        scaled_x = [self.xtranslate(v) for v in x]
        scaled_y = [self.ytranslate(v) for v in y]
        scaled_x_y = list(zip(scaled_x, scaled_y))
        self.draw.polygon(scaled_x_y, fill=fill, outline=outline, **options)
        return self


class ScaledDrawingCloned(ScaledDrawingWithPolygon):

    def __init__(self, draw, sdraw):
        self.xscale = sdraw.xscale
        self.yscale = sdraw.yscale
        self.xoffset = sdraw.xoffset
        self.yoffset = sdraw.yoffset
        self.draw = draw
        return
    
    
def to_rgb(color_spec, alpha=0xff):
    try:
        assert not (color_spec is None)
        rgb = PIL.ImageColor.getrgb(color_spec)
        rgb = list(rgb) + [alpha]
        rgb = rgb[:4]
        result = tuple(rgb)
    except ValueError:
        result = color_spec
    except AssertionError:
        result = color_spec
    return result
    
    
def main_line():
    return


if __name__ == "__main__":
    main_line()


# Fin
