# -*- coding: utf-8 -*-
##This program is free software; you can redistribute it and/or modify it under
##the terms of the GNU General Public License as published by the Free Software
##Foundation; either version 2 of the License, or (at your option) any later
##version.
##
##This program is distributed in the hope that it will be useful, but WITHOUT
##ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
##FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
##details.
##
## Version: 3.0.1                                    Date: 25 September 2020
##
## Revision History
##  25 September 2020     v.1.3.2   -delete WdSuppArchive obsolate
##                                  -vantage driver read all data by LOOP 1 and 2
##                                  -Define a dictionary to look up Davis forecast rule
##                                   and return forecast text old 'davis_fr_dict'
##                                   new vantagetext.py
##  25 September 2019     v.1.3.1   -logging by python
##  1 May 2019            v1.3.0    -python 3 delete WU
##  10 August 2015        v1.2.0    -revised for Weewx v3.2.0
##                                  -moved __main__ code to weewxwd_config utility
##                                  -now uses appTemp and humidex as provided by
##                                   StdWXCalculate
##                                  -simplified WdWXCalculate.new_loop_packet,
##                                   WdWXCalculate.new_archive_record and
##                                   WdArchive.new_archive_record methods
##  10 January 2015     v1.0.0      -rewritten for Weewx v3.0
##                                  -uses separate database for Weewx-WD specific
##                                   data, no longer recycles existing Weewx
##                                   database fields
##                                  -added __main__ to allow command line execution
##                                   of a number of db management actions
##                                  -removed --debug option from main()
##                                  -added --create_archive option to main()
##                                   to create the weewxwd database
##                                  -split --backfill_daily into separate
##                                   --drop_daily and --backfill_daily options
##                                  -added 'user.' to all Weewx-WD imports
##  18 September 2014   v0.9.4      -Added GNU license text
##      (never released)
##  18 May 2014         v0.9.2      -Removed code that set windDir/windGustDir to 0
##                                   if windDir/windGustDir were None respectively
##  30 July 2013        v0.9.1      -Revised version number to align with Weewx-WD
##                                   version numbering
##  20 July 2013        v0.1        -Initial implementation
##

from __future__ import absolute_import
from __future__ import print_function

import logging
import os
import time

from datetime import datetime

import weewx
import weedb
import weeutil.config
import weeutil.logger
import weewx.engine
import weewx.manager
import weewx.wxformulas
import weeutil.weeutil

log = logging.getLogger(__name__)

WEEWXWD_VERSION = '3.0.1'


#===============================================================================
#                            Class WdWXCalculate
#===============================================================================

class WdWXCalculate(weewx.engine.StdService):

    def __init__(self, engine, config_dict):
        super(WdWXCalculate, self).__init__(engine, config_dict)

        # bind ourself to both loop and archive events
        self.bind(weewx.NEW_LOOP_PACKET, self.new_loop_packet)
        self.bind(weewx.NEW_ARCHIVE_RECORD, self.new_archive_record)

    def new_loop_packet(self, event):
        data_x = {}
        if 'outTemp' in event.packet:
            data_x['outTempDay'], data_x['outTempNight'] = calc_daynighttemps(event.packet['outTemp'], event.packet['dateTime'])
            data_x['heatdeg'] = weewx.wxformulas.heating_degrees(event.packet['outTemp'], 18.333)
            data_x['cooldeg'] = weewx.wxformulas.cooling_degrees(event.packet['outTemp'], 18.333)
            data_x['homedeg'] = weewx.wxformulas.heating_degrees(event.packet['outTemp'], 15.0)
            data_x['wdd_deg'] = weewx.wxformulas.cooling_degrees(event.packet['outTemp'], 10.0)
            data_x['SVP'] = weewx.uwxutils.TWxUtils.SaturationVaporPressure(event.packet['outTemp'])
            data_x['GDD4'] = weewx.wxformulas.cooling_degrees(event.packet['outTemp'], 4.0)
            data_x['GDD6'] = weewx.wxformulas.cooling_degrees(event.packet['outTemp'], 6.0)
            data_x['GDD10'] = weewx.wxformulas.cooling_degrees(event.packet['outTemp'], 5.0)

        else:
            data_x['outTempDay'], data_x['outTempNight'] = (None, None)
            data_x['heatdeg'] = None
            data_x['cooldeg'] = None
            data_x['homedeg'] = None
            data_x['wdd_deg'] = None
            data_x['SVP'] = None
            data_x['GDD4'] = None
            data_x['GDD6'] = None
            data_x['GDD10'] = None

        if 'rain' in event.packet and 'ET' in event.packet:
            data_x['rain_ET'] = event.packet['rain'] - event.packet['ET']
        else:
            data_x['rain_ET'] = None

        if 'inTemp' in event.packet:
            data_x['SVPin'] = weewx.uwxutils.TWxUtils.SaturationVaporPressure(event.packet['inTemp'])
        else:
            data_x['SVPin'] = None

        if 'outTemp' in event.packet and 'outHumidity' in event.packet:
            data_x['AVP'] = event.packet['outHumidity'] * (weewx.uwxutils.TWxUtils.SaturationVaporPressure(event.packet['outTemp'])) / 100.0
        else:
            data_x['AVP'] = None

        if 'inTemp' in event.packet and 'inHumidity' in event.packet:
            data_x['AVPin'] = event.packet['inHumidity'] * (weewx.uwxutils.TWxUtils.SaturationVaporPressure(event.packet['inTemp'])) / 100.0
        else:
            data_x['AVPin'] = None


        event.packet.update(data_x)

    def new_archive_record(self, event):
        data_x = {}
        if 'outTemp' in event.record:
            data_x['outTempDay'], data_x['outTempNight'] = calc_daynighttemps(event.record['outTemp'], event.record['dateTime'])
            data_x['heatdeg'] = weewx.wxformulas.heating_degrees(event.record['outTemp'], 18.333)
            data_x['cooldeg'] = weewx.wxformulas.cooling_degrees(event.record['outTemp'], 18.333)
            data_x['homedeg'] = weewx.wxformulas.heating_degrees(event.record['outTemp'], 15.0)
            data_x['wdd_deg'] = weewx.wxformulas.cooling_degrees(event.record['outTemp'], 10.0)
            data_x['SVP'] = weewx.uwxutils.TWxUtils.SaturationVaporPressure(event.record['outTemp'])
            data_x['GDD4'] = weewx.wxformulas.cooling_degrees(event.record['outTemp'], 4.0)
            data_x['GDD6'] = weewx.wxformulas.cooling_degrees(event.record['outTemp'], 6.0)
            data_x['GDD10'] = weewx.wxformulas.cooling_degrees(event.record['outTemp'], 5.0)

        else:
            data_x['outTempDay'], data_x['outTempNight'] = (None, None)
            data_x['heatdeg'] = None
            data_x['cooldeg'] = None
            data_x['homedeg'] = None
            data_x['wdd_deg'] = None
            data_x['SVP'] = None
            data_x['GDD4'] = None
            data_x['GDD6'] = None
            data_x['GDD10'] = None

        if 'rain' in event.record and 'ET' in event.record:
            data_x['rain_ET'] = event.record['rain'] - event.record['ET']
        else:
            data_x['rain_ET'] = None

        if 'inTemp' in event.record:
            data_x['SVPin'] = weewx.uwxutils.TWxUtils.SaturationVaporPressure(event.record['inTemp'])
        else:
            data_x['SVPin'] = None

        if 'outTemp' in event.record and 'outHumidity' in event.record:
            data_x['AVP'] = event.record['outHumidity'] * (weewx.uwxutils.TWxUtils.SaturationVaporPressure(event.record['outTemp'])) / 100.0
        else:
            data_x['AVP'] = None

        if 'inTemp' in event.record and 'inHumidity' in event.record:
            data_x['AVPin'] = event.record['inHumidity'] * (weewx.uwxutils.TWxUtils.SaturationVaporPressure(event.record['inTemp'])) / 100.0
        else:
            data_x['AVPin'] = None


        event.record.update(data_x)

#===============================================================================
#                              Class WdArchive
#===============================================================================

class WdArchive(weewx.engine.StdService):
    """ Service to store Weewx-WD specific archive data. """

    def __init__(self, engine, config_dict):
        super(WdArchive, self).__init__(engine, config_dict)

        # Extract our binding from the Weewx-WD section of the config file. If
        # it's missing, fill with a default
        if 'WeewxWD' in config_dict:
            self.data_binding = config_dict['WeewxWD'].get('data_binding', 'wd_binding')
        else:
            self.data_binding = 'wd_binding'

        # Extract the Weewx binding for use when we check the need for backfill
        # from the Weewx archive
        if 'StdArchive' in config_dict:
            self.data_binding_wx = config_dict['StdArchive'].get('data_binding', 'wx_binding')
        else:
            self.data_binding_wx = 'wx_binding'

        log.info("WdArchive will use data binding %s", self.data_binding)

        # setup our database if needed
        self.setup_database(config_dict)

        # bind ourselves to NEW_ARCHIVE_RECORD event
        self.bind(weewx.NEW_ARCHIVE_RECORD, self.new_archive_record)


    def new_archive_record(self, event):
        """Called when a new archive record has arrived.

           Use our manager's addRecord method to save the relevant Weewx-WD
           fields to Weewx-WD archive.
        """

        # get our manager
        dbmanager = self.engine.db_binder.get_manager(self.data_binding)
        # now put the record in the archive
        dbmanager.addRecord(event.record)

    def setup_database(self, config_dict):
        """Setup the main database archive"""

        # This will create the database if it doesn't exist, then return an
        # opened instance of the database manager.
        dbmanager = self.engine.db_binder.get_manager(self.data_binding, initialize=True)
        log.info("WdArchive using binding '%s' to database '%s'", self.data_binding, dbmanager.database_name)

        # Check if we have any historical data to suck in from Weewx main archive
        # get a dbmanager for the Weewx archive
        dbmanager_wx = self.engine.db_binder.get_manager(self.data_binding_wx, initialize=False)


        # Back fill the daily summaries.
        log.info("WD_Starting backfill of daily summaries")
        t1 = time.time()
        nrecs, ndays = dbmanager.backfill_day_summary()
        tdiff = time.time() - t1
        if nrecs:
            log.info("WdArchive Processed %d records to backfill %d day summaries in %.2f seconds",  nrecs, ndays, tdiff)
        else:
            log.info("WdArchive Daily summaries up to date.")

#===============================================================================
#                              Class WeeArchive
#===============================================================================

class WeeArchive(weewx.engine.StdService):
    """ Service to store Weewx-WEE specific archive data. """

    def __init__(self, engine, config_dict):
        super(WeeArchive, self).__init__(engine, config_dict)

        # Extract our binding from the Weewx-WEE section of the config file. If
        # it's missing, fill with a default
        if 'WeewxArchive' in config_dict:
            self.data_binding = config_dict['WeewxArchive'].get('data_binding', 'wee_binding')
        else:
            self.data_binding = 'wee_binding'

        log.info("Weewx-Archive will use data binding %s", self.data_binding)

        # setup our database if needed
        self.setup_database(config_dict)

        # bind ourselves to NEW_ARCHIVE_RECORD event
        self.bind(weewx.NEW_ARCHIVE_RECORD, self.new_archive_record)


    def new_archive_record(self, event):
        """Called when a new archive record has arrived. """

        # get our manager
        dbmanager = self.engine.db_binder.get_manager(self.data_binding)
        # now put the record in the archive
        dbmanager.addRecord(event.record)

    def setup_database(self, config_dict):
        """Setup the main database archive"""

        # This will create the database if it doesn't exist, then return an
        # opened instance of the database manager.
        dbmanager = self.engine.db_binder.get_manager(self.data_binding, initialize=True)
        log.info("Weewx-Archive using binding '%s' to database '%s'", self.data_binding, dbmanager.database_name)

#===============================================================================
#                                 Utilities
#===============================================================================

def calc_daynighttemps(temp, dt):
    """ 'Calculate' value for outTempDay and outTempNight.

        outTempDay and outTempNight are used to determine warmest night
        and coldest day stats. This is done by using two derived
        observations; outTempDay and outTempNight. These observations
        are defined as follows:

        outTempDay:   equals outTemp if time of day is > 06:00 and <= 18:00
                      otherwise it is None
        outTempNight: equals outTemp if time of day is > 18:00 or <= 06:00
                      otherwise it is None

        By adding these derived obs to the schema and loop packet the daily
        summaries for these obs are populated and aggregate stats can be
        accessed as per normal (eg $month.outTempDay.minmax to give the
        coldest max daytime temp in the month). Note that any aggregates that
        rely on the number of records (eg avg) will be meaningless due to
        the way outTempxxxx is calculated.
    """

    if temp is not None:
        # check if record covers daytime (6AM to 6PM) and if so add 'temp' to 'outTempDay'
        # remember record timestamped 6AM belongs in the night time
        if datetime.fromtimestamp(dt - 1).hour < 6 or datetime.fromtimestamp(dt - 1).hour > 17:
            # ie the data packet is from before 6am or after 6pm
            return (None, temp)
        else:
            # ie the data packet is from after 6am and before or including 6pm
            return (temp, None)
    else:
        return (None, None)



