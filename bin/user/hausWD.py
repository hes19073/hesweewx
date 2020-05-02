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
## Version: 0.3                                    Date: 20 Februar 2020
##
## Revision History
##  20 Februar 2020          v0.3        - Zaehler und Delta Preise
##  02 October 2019          v0.2        - Preise Gas Wasser Strom
##  26 September 2019        v0.1        - Initial implementation
##

## *Total = Zaehlerdifferenz Verbrauch
## *Deltawerte = Zaehlimpule s0
## Werte *Total Differenz aus Handeintrag und alter Zaehlerstand
## Werte *Delta Differenz aus Impuls Neu und Impuls alt
#
# Service to calculate Preise for Wasser-, Strom- und Gasverbrauch
#
# in weewx.config
# Add this service to weewx.conf, then restart weewx
#[Engine]
#    [[Services]]
#        process_services = ..., user,hausWD,HausWdCalculate,
#        archive_service = ...., user,hausWD,HausWdArchive

#[HausWD]
#   # Werte in Euro
#    Brennwert = 9.8
#    Zustandszahl = 0.95
#    Gaspreis = 0.0619
#    Strompreis = 0.272
#    Grundpreisstrom = 123.32
#    Wasserpreis = 1.47
#    Abwasserpreis = 2.65
#    Grundpreiswasser = 12.98
#
#

from __future__ import absolute_import
from __future__ import print_function

import logging
import datetime
import time
import weewx
import weedb
import weeutil.config
import weeutil.logger
import weewx.engine
import weewx.manager

import weeutil.weeutil

from weewx.units import convert, obs_group_dict
from weeutil.config import search_up, accumulateLeaves
from weeutil.weeutil import to_float

log = logging.getLogger(__name__)

HAUSWD_VERSION = '0.3'


#===============================================================================
#                            Class HausWdCalculate
#===============================================================================

class HausWdCalculate(weewx.engine.StdService):

    def __init__(self, engine, config_dict):
        super(HausWdCalculate, self).__init__(engine, config_dict)

        d = config_dict.get('HausWD', {})
        self.BrennWert = weeutil.weeutil.to_float(d.get('Brennwert', 9.8))
        self.ZustandsZahl = weeutil.weeutil.to_float(d.get('Zustandszahl', 0.95))
        self.GasPreis = weeutil.weeutil.to_float(d.get('Gaspreis', 0.0619))
        self.StromPreis = weeutil.weeutil.to_float(d.get('Strompreis', 0.272))
        self.WasserPreis = weeutil.weeutil.to_float(d.get('Wasserpreis', 1.47))
        self.AbwasserPreis = weeutil.weeutil.to_float(d.get('Abwasserpreis', 2.65))

        # bind ourself to both loop and archive events
        self.bind(weewx.NEW_LOOP_PACKET, self.new_loop_packet)
        self.bind(weewx.NEW_ARCHIVE_RECORD, self.new_archive_record)

    def new_loop_packet(self, event):

        data_x = {}
        if 'gasTotal' in event.packet:
            data_x['gasZ_m3'] = event.packet['gasTotal']
            data_x['gasZ_kWh'] = event.packet['gasTotal'] * self.BrennWert * self.ZustandsZahl
            data_x['gasZ_preis'] = event.packet['gasTotal'] * self.BrennWert * self.ZustandsZahl * self.GasPreis

        else:
            data_x['gasZ_m3'] = 0.0
            data_x['gasZ_kWh'] = 0.0
            data_x['gasZ_preis'] = 0.0

        if 'eleTotal' in event.packet:
            data_x['eleZ_kWh'] = event.packet['eleTotal']
            data_x['eleZ_preis'] = event.packet['eleTotal'] * self.StromPreis

        else:
            data_x['eleZ_kWh'] = 0.0
            data_x['eleZ_preis'] = 0.0

        if 'eleATotal' in event.packet:
            data_x['eleAZ_kWh'] = event.packet['eleATotal']
            data_x['eleAZ_preis'] = event.packet['eleATotal'] * self.StromPreis

        else:
            data_x['eleAZ_m3'] = 0.0
            data_x['eleAZ_preis'] = 0.0

        if 'elePVTotal' in event.packet:
            data_x['elePVZ_kWh'] = event.packet['elePVTotal']
            data_x['elePVZ_preis'] = event.packet['elePVTotal'] * self.StromPreis

        else:
            data_x['elePVZ_kWh'] = 0.0
            data_x['elePVZ_preis'] = 0.0

        if 'wasTotal' in event.packet and 'wasATotal' in event.packet:
            was_new = event.packet['wasTotal']
            waa_new = event.packet['wasATotal']
            data_x['wasZ_m3'] = was_new
            data_x['wasZ_preis'] = was_new * self.WasserPreis
            data_x['wasAZ_m3'] = waa_new
            data_x['wasAZ_preis']  = waa_new * self.WasserPreis
            data_x['wasG_preis'] = (was_new * self.WasserPreis) + ((was_new - waa_new) * self.AbwasserPreis)

        else:
            data_x['wasZ_m3'] = 0.0
            data_x['wasAZ_m3'] = 0.0
            data_x['wasZ_preis'] = 0.0
            data_x['wasAZ_preis'] = 0.0

        # Wertung der Impuls Zaehler Werte
        """ read data impulse  for calculate preis  """
        if 'gasDelta' in event.packet:
            gas_new = event.packet['gasDelta'] * 0.01
            data_x['gas_m3'] = gas_new
            data_x['gas_kWh'] = gas_new * self.BrennWert * self.ZustandsZahl
            data_x['gas_preis'] = gas_new * self.BrennWert * self.ZustandsZahl * self.GasPreis

        else:
            data_x['gas_m3'] = 0.0
            data_x['gas_kWh'] = 0.0
            data_x['gas_preis'] = 0.0

        if 'eleDelta' in event.packet:
            ele_new = event.packet['eleDelta'] * 0.001
            data_x['ele_kWh'] = ele_new
            data_x['ele_preis'] = ele_new * self.StromPreis

        else:
            data_x['ele_kWh'] = 0.0
            data_x['ele_preis'] = 0.0

        if 'eleADelta' in event.packet:
            ela_new = event.packet['eleADelta'] * 0.001
            data_x['eleA_kWh'] = ela_new
            data_x['eleA_preis'] = ela_new * self.StromPreis

        else:
            data_x['eleA_kWh'] = 0.0
            data_x['eleA_preis'] = 0.0

        if 'elePVDelta' in event.packet:
            elp_new = event.packet['elePVDelta'] * 0.001
            data_x['elePV_kWh'] = elp_new
            data_x['elePV_preis'] = elp_new * self.StromPreis

        else:
            data_x['elePV_kWh'] = 0.0
            data_x['elePV_preis'] = 0.0

        if 'wasDelta' in event.packet and 'wasADelta' in event.packet:
            #was_new = event.packet['wasDelta'] * 0.001
            #waa_new = event.packet['wasADelta'] * 0.001
            was_new = event.packet['wasDelta']
            waa_new = event.packet['wasADelta']
            data_x['was_m3'] = was_new
            data_x['wasA_m3'] = waa_new
            data_x['was_preis'] = was_new * self.WasserPreis
            data_x['wasA_preis']  = waa_new * self.WasserPreis
            data_x['wasG_preis'] = (was_new * self.WasserPreis) + ((was_new - waa_new) * self.AbwasserPreis)

        else:
            data_x['was_m3'] = 0.0
            data_x['wasA_m3'] = 0.0
            data_x['was_preis'] = 0.0
            data_x['wasA_preis'] = 0.0
            data_x['wasG_preis'] = 0.0


        event.packet.update(data_x)


    def new_archive_record(self, event):

        data_x = {}
        if 'gasTotal' in event.record:
            data_x['gasZ_m3'] = event.record['gasTotal']
            data_x['gasZ_kWh'] = event.record['gasTotal'] * self.BrennWert * self.ZustandsZahl
            data_x['gasZ_preis'] = event.record['gasTotal'] * self.BrennWert * self.ZustandsZahl * self.GasPreis

        else:
            data_x['gasZ_m3'] = 0.0
            data_x['gasZ_kWh'] = 0.0
            data_x['gasZ_preis'] = 0.0

        if 'eleTotal' in event.record:
            data_x['eleZ_kWh'] = event.record['eleTotal']
            data_x['eleZ_preis'] = event.record['eleTotal'] * self.StromPreis

        else:
            data_x['eleZ_kWh'] = 0.0
            data_x['eleZ_preis'] = 0.0

        if 'eleATotal' in event.record:
            data_x['eleAZ_kWh'] = event.record['eleATotal']
            data_x['eleAZ_preis'] = event.record['eleATotal'] * self.StromPreis

        else:
            data_x['eleAZ_kWh'] = 0.0
            data_x['eleAZ_preis'] = 0.0

        if 'elePVTotal' in event.record:
            data_x['elePVZ_kWh'] = event.record['elePVTotal']
            data_x['elePVZ_preis'] = event.record['elePVTotal'] * self.StromPreis

        else:
            data_x['elePVZ_kWh'] = 0.0
            data_x['elePVZ_preis'] = 0.0

        if 'wasTotal' in event.record and 'wasATotal' in event.record:
            was_new = event.record['wasTotal']
            waa_new = event.record['wasATotal']
            data_x['wasZ_m3'] = was_new
            data_x['wasAZ_m3'] = waa_new
            data_x['wasZ_preis'] = was_new * self.WasserPreis
            data_x['wasAZ_preis']  = waa_new * self.WasserPreis
            data_x['wasG_preis'] = (was_new * self.WasserPreis) + ((was_new - waa_new) * self.AbwasserPreis)

        else:
            data_x['wasZ_m3'] = 0.0
            data_x['wasAZ_m3'] = 0.0
            data_x['wasZ_preis'] = 0.0
            data_x['wasAZ_preis'] = 0.0
            data_x['wasG_preis'] = 0.0

        # Wertung der Impuls Zaehler Werte
        """ read data impulse  for calculate preis  """
        if 'gasDelta' in event.record:
            gas_new = event.record['gasDelta'] * 0.01
            data_x['gas_m3'] = gas_new
            data_x['gas_kWh'] = gas_new * self.BrennWert * self.ZustandsZahl
            data_x['gas_preis'] = gas_new * self.BrennWert * self.ZustandsZahl * self.GasPreis

        else:
            data_x['gas_m3'] = 0.0
            data_x['gas_kWh'] = 0.0
            data_x['gas_preis'] = 0.0

        if 'eleDelta' in event.record:
            ele_new = event.record['eleDelta'] * 0.001
            data_x['ele_kWh'] = ele_new
            data_x['ele_preis'] = ele_new * self.StromPreis

        else:
            data_x['ele_kWh'] = 0.0
            data_x['ele_preis'] = 0.0

        if 'eleADelta' in event.record:
            ela_new = event.record['eleDelta'] * 0.001
            data_x['eleA_kWh'] = ela_new
            data_x['eleA_preis'] = ela_new * self.StromPreis

        else:
            data_x['eleA_kWh'] = 0.0
            data_x['eleA_preis'] = 0.0

        if 'elePVDelta' in event.record:
            elp_new = event.record['elePVDelta'] * 0.001
            data_x['elePV_kWh'] = elp_new
            data_x['elePV_preis'] = elp_new * self.StromPreis

        else:
            data_x['elePV_kWh'] = 0.0
            data_x['elePV_preis'] = 0.0

        if 'wasDelta' in event.record and 'wasADelta' in event.record:
            #was_new = event.record['wasDelta'] * 0.001
            #waa_new = event.record['wasADelta'] * 0.001
            was_new = event.record['wasDelta']
            waa_new = event.record['wasADelta']
            data_x['was_m3'] = was_new
            data_x['wasA_m3'] = waa_new
            data_x['was_preis'] = was_new * self.WasserPreis
            data_x['wasA_preis']  = waa_new * self.WasserPreis
            data_x['wasG_preis'] = (was_new * self.WasserPreis) + ((was_new - waa_new) * self.AbwasserPreis)

        else:
            data_x['was_m3'] = 0.0
            data_x['wasA_m3'] = 0.0
            data_x['was_preis'] = 0.0
            data_x['wasA_preis'] = 0.0
            data_x['wasG_preis'] = 0.0


        event.record.update(data_x)


#===============================================================================
#                              Class HausWdArchive
#===============================================================================

class HausWdArchive(weewx.engine.StdService):
    """ Service to store Weewx-WD specific archive data. """

    def __init__(self, engine, config_dict):
        super(HausWdArchive, self).__init__(engine, config_dict)

        # Extract our binding from the Haus-WD section of the config file. If
        # it's missing, fill with a default
        if 'HausWD' in config_dict:
            self.data_binding = config_dict['HausWD'].get('data_binding', 'hausWD_binding')
        else:
            self.data_binding = 'hausWD_binding'

        # Extract the Weewx binding for use when we check the need for backfill
        # from the Weewx archive
        if 'StdArchive' in config_dict:
            self.data_binding_wx = config_dict['StdArchive'].get('data_binding', 'wx_binding')
        else:
            self.data_binding_wx = 'wx_binding'

        log.info("HausWdArchive will use data binding %s", self.data_binding)

        # setup our database if needed
        self.setup_database(config_dict)

        # set the unit groups for our obs
        obs_group_dict["gasZ_m3"] = "group_volume"
        obs_group_dict["wasZ_m3"] = "group_volume"
        obs_group_dict["wasAZ_m3"] = "group_volume"
        obs_group_dict["eleZ_kWh"] = "group_strom"
        obs_group_dict["eleAZ_kWh"] = "group_strom"
        obs_group_dict["elePVZ_kWh"] = "group_strom"
        obs_group_dict["gas_preis"] = "group_preis"
        obs_group_dict["was_preis"] = "group_preis"
        obs_group_dict["ele_preis"] = "group_preis"
        obs_group_dict["elePVZ_preis"] = "group_preis"
        obs_group_dict["gasZ_preis"] = "group_preis"
        obs_group_dict["wasZ_preis"] = "group_preis"
        obs_group_dict["eleZ_preis"] = "group_preis"
        obs_group_dict["wasAZ_preis"] = "group_preis"
        obs_group_dict["eleAZ_preis"] = "group_preis"
        obs_group_dict["wasG_preis"] = "group_preis"

        # bind ourselves to NEW_ARCHIVE_RECORD event
        self.bind(weewx.NEW_ARCHIVE_RECORD, self.new_archive_record)


    def new_archive_record(self, event):
        """Called when a new archive record has arrived.

           Use our manager's addRecord method to save the relevant Haus-WD
           fields to Haus-WD archive.
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
        log.info("HausWdArchive using binding '%s' to database '%s'", self.data_binding, dbmanager.database_name)

        # Check if we have any historical data to suck in from Weewx main archive
        # get a dbmanager for the Weewx archive
        dbmanager_wx = self.engine.db_binder.get_manager(self.data_binding_wx, initialize=False)


        # Back fill the daily summaries.
        log.info("HausWD_Starting backfill of daily summaries")
        t1 = time.time()
        nrecs, ndays = dbmanager.backfill_day_summary()
        tdiff = time.time() - t1
        if nrecs:
            log.info("HausWdArchive Processed %d records to backfill %d day summaries in %.2f seconds",  nrecs, ndays, tdiff)
        else:
            log.info("HausWdArchive Daily summaries up to date.")


#===============================================================================

