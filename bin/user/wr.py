##
##This program is free software; you can redistribute it and/or modify
##it under the terms of the GNU General Public License as published by
##the Free Software Foundation; either version 2 of the License, or
##(at your option) any later version.
##
##This program is distributed in the hope that it will be useful,
##but WITHOUT ANY WARRANTY; without even the implied warranty of
##MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##GNU General Public License for more details.
##
## Version: 1.0.0                                    Date: 10 January 2015
##
## Revision History
##  10 January 2015  v1.0.0     -Rewritten for Weewx v3.0.0  
##  1 May 2014       v0.9.3     -Fixed issue that arose with Weewx 2.6.3 now 
##                               allowing use of UTF-8 characters in plots
##                              -Fixed logic error in code that calculates size
##                               of windrose 'petals'
##                              -Removed unnecessary import statements
##                              -Tweaked windrose size calculations to better
##                               cater for labels on plot
##  30 July 2013     v0.9.1     -Revised version number to align with Weewx-WD
##                               version numbering
##  20 July 2013     v0.1       -Initial implementation
##

import time
import datetime
import syslog
import os.path
import math

import weeutil.weeutil
import weewx.reportengine
import weewx.units

import Image
import ImageDraw
import ImageFont

WEEWXWD_STACKED_WINDROSE_VERSION = '1.0.0'

#===============================================================================
#                    Class ImageStackedWindRoseGenerator
#===============================================================================

class ImageStackedWindRoseGenerator(weewx.reportengine.ReportGenerator):
    """Class for managing the stacked windrose image generator."""

    def run(self):
        self.setup()
        
        # Generate any images
        self.genImages(self.gen_ts)
        
    def setup(self):
        # Get our binding to use
        self.data_binding = self.config_dict['StdArchive'].get('data_binding', 'wx_binding')
        
        self.image_dict = self.skin_dict['ImageStackedWindRoseGenerator']
        self.title_dict = self.skin_dict['Labels']['Generic']
        self.converter  = weewx.units.Converter.fromSkinDict(self.skin_dict)
        self.formatter  = weewx.units.Formatter.fromSkinDict(self.skin_dict)
        self.unit_helper= weewx.units.UnitInfoHelper(self.formatter, self.converter)

        # Set image attributes
        self.image_width = int(self.image_dict['image_width'])
        self.image_height = int(self.image_dict['image_height'])
        self.image_background_box_color = int(self.image_dict['image_background_box_color'],0)
        self.image_background_circle_color = int(self.image_dict['image_background_circle_color'],0)
        self.image_background_range_ring_color = int(self.image_dict['image_background_range_ring_color'],0)
        self.image_background_image = self.image_dict['image_background_image']

        # Set windrose attributes
        self.windrose_plot_border = int(self.image_dict['windrose_plot_border'])
        self.windrose_legend_bar_width = int(self.image_dict['windrose_legend_bar_width'])
        self.windrose_font_path = self.image_dict['windrose_font_path']
        self.windrose_plot_font_size  = int(self.image_dict['windrose_plot_font_size'])
        self.windrose_plot_font_color = int(self.image_dict['windrose_plot_font_color'],0)
        self.windrose_legend_font_size  = int(self.image_dict['windrose_legend_font_size'])
        self.windrose_legend_font_color = int(self.image_dict['windrose_legend_font_color'],0)
        self.windrose_label_font_size  = int(self.image_dict['windrose_label_font_size'])
        self.windrose_label_font_color = int(self.image_dict['windrose_label_font_color'],0)
        # Look for petal colours, if not defined then set some defaults
        try:
            self.petal_colors = self.image_dict['windrose_plot_petal_colors']
        except KeyError:
            self.petal_colors = ['lightblue','blue','midnightblue','forestgreen','limegreen','green','greenyellow']
        # Loop through petal colours looking for 0xBGR values amongst colour
        # names, set any 0xBGR to their numeric value and leave colour names
        # alone
        i = 0
        while i<len(self.petal_colors):
            try:
                # Can it be converted to a number?
                self.petal_colors[i] = int(self.petal_colors[i],0)
            except ValueError:  # Cannot convert to a number, assume it is
                                # a colour word so leave it
                pass
            i += 1
        # Get petal width, if not defined then set default to 16 (degrees)
        try:
            self.windrose_plot_petal_width = int(self.image_dict['windrose_plot_petal_width'])
        except KeyError:
            self.windrose_plot_petal_width = 16
        # Boundaries for speed range bands, these mark the colour boundaries
        # on the stacked bar in the legend. 7 elements only (ie 0, 10% of max,
        # 20% of max...100% of max)
        self.speedFactor = [0.0,0.1,0.2,0.3,0.5,0.7,1.0]
        
    def genImages(self, gen_ts):
        """Generate the images.
        
        The time period chosen is from gen_ts going back skin.conf 'time_length' seconds.
    
        gen_ts: The time stamp of the end of the plot period. If not set defaults to the time of the last record
        in the archive database.
        """

        # Time period taken to generate plots, set plot count to 0
        t1 = time.time()
        ngen = 0
        # Loop over each time span class (day, week, month, etc.):
        for timespan in self.image_dict.sections :
            # Now, loop over all plot names in this time span class:
            for plotname in self.image_dict[timespan].sections :
                # Accumulate all options from parent nodes:
                plot_options = weeutil.weeutil.accumulateLeaves(self.image_dict[timespan][plotname])
                # Get the database archive
                default_archive = self.db_binder.get_manager(self.data_binding)
#                archivedb = self._getArchive(plot_options['archive_database'])
                # Get end time for plot. In order try gen_ts, last known good
                # archive time stamp and then current time
                self.plotgen_ts = gen_ts
                if not self.plotgen_ts:
                    self.plotgen_ts = default_archive.lastGoodStamp()
                    if not self.plotgen_ts:
                        self.plotgen_ts = time.time()
                # Get the path of the image file we will save
                image_root = os.path.join(self.config_dict['WEEWX_ROOT'], plot_options['HTML_ROOT'])
                # Get image file format. Can use any format PIL can write
                # Default to png
                if plot_options.has_key('format'):
                    format = plot_options['format']
                else:
                    format = "png"
                # Get full file name and path for plot
                img_file = os.path.join(image_root, '%s.%s' % (plotname,format))
                # Check whether this plot needs to be done at all:
                ai = plot_options.as_int('time_length') if plot_options.has_key('time_length') else None
                if skipThisPlot(self.plotgen_ts, ai, img_file, plotname) :
                    continue
                # Create the subdirectory that the image is to be put in.
                # Wrap in a try block in case it already exists.
                try:
                    os.makedirs(os.path.dirname(img_file))
                except:
                    pass
                # Loop over each line to be added to the plot.
                for line_name in self.image_dict[timespan][plotname].sections:

                    # Accumulate options from parent nodes. 
                    line_options = weeutil.weeutil.accumulateLeaves(self.image_dict[timespan][plotname][line_name])
                    
                    # See if a plot title has been explicitly requested.
                    # 'label' used for consistency in skin.conf with 
                    # ImageGenerator sections
                    label = line_options.get('label')
                    if label:
                        self.label = unicode(label, 'utf8')
                    else:
                        # No explicit label so set label to nothing
