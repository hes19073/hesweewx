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
## Version: 0.1                                    Date: 26 September 2019
##
## Revision History
##  02 October 2019          v0.2        # Preise Gas Wasser Strom
##  26 September 2019        v0.1        -Initial implementation
##

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

HAUSWD_VERSION = '0.2'


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
            data_x['gas_m3'], data_x['gas_kWh'], data_x['gas_preis'] = calc_gas(event.packet['gasTotal'])

        else:
            data_x['gas_m3'] = None
            data_x['gas_kWh'] = None
            data_x['gas_preis'] = None

        if 'eleTotal' in event.packet:
            data_x['ele_kWh'], data_x['ele_preis'] = calc_ele(event.packet['eleTotal'])

        else:
            data_x['ele_kWh'] = None
            data_x['ele_preis'] = None

        if 'eleATotal' in event.packet:
            data_x['eleA_kWh'], data_x['eleA_preis'] = calc_eleA(event.packet['eleATotal'])

        else:
            data_x['eleA_kWh'] = None
            data_x['eleA_preis'] = None

        if 'wasTotal' in event.packet and 'wasATotal':
            data_x['was_m3'], data_x['was_preis'], data_x['wasA_m3'], data_x['wasA_preis']  = calc_was(event.packet['wasTotal'], event.packet['wasATotal'])

        else:
            data_x['was_m3'] = None
            data_x['was_preis'] = None
            data_x['wasA_m3'] = None
            data_x['wasA_preis'] = None

        event.packet.update(data_x)

    def new_archive_record(self, event):

        data_x = {}
        if 'gasTotal' in event.record:
            data_x['gas_m3'], data_x['gas_kWh'], data_x['gas_preis'] = calc_gas(event.record['gasTotal'])

        else:
            data_x['gas_m3'] = 0.0
            data_x['gas_kWh'] = 0.0
            data_x['gas_preis'] = 0.0

        if 'eleTotal' in event.record:
            data_x['ele_kWh'], data_x['ele_preis'] = calc_ele(event.record['eleTotal'])

        else:
            data_x['ele_kWh'] = 0.0
            data_x['ele_preis'] = 0.0

        if 'eleATotal' in event.record:
            data_x['eleA_kWh'], data_x['eleA_preis'] = calc_eleA(event.record['eleATotal'])

        else:
            data_x['eleA_kWh'] = 0.0
            data_x['eleA_preis'] = 0.0

        if 'wasTotal' in event.record and 'wasATotal':
            data_x['was_m3'], data_x['was_preis'], data_x['wasA_m3'], data_x['wasA_preis'] = calc_was(event.record['wasTotal'], event.record['wasATotal'])

        else:
            data_x['was_m3'] = 0.0
            data_x['was_preis'] = 0.0
            data_x['wasA_m3'] = 0.0
            data_x['wasA_preis'] = 0.0

        # Wertung der Zaehler
        """ read old data from file 'anfangZahl' for calculate_delta """
        try:
            with open('/home/weewx/archive/anfangZahl') as f:
                line = f.readline()
                values = line.split(',')

            gas_val = float(values[0])
            was_val = float(values[1])
            waa_val = float(values[2])
            ele_val = float(values[3])
            ela_val = float(values[4])

            f.close()

        except Exception as e:
            log.error("Daten: cannot read Date: %s", e)

        if 'gasZahl' in event.record:
            gas_new = self.calculate_delta(event.record['gasZahl'], gas_val)
            data_x['gasZ_m3'] = gas_new
            data_x['gasZ_kWh'] = gas_new * self.BrennWert * self.ZustandsZahl
            data_x['gasZ_preis'] = gas_new * self.BrennWert * self.ZustandsZahl * self.GasPreis
            last_gasZ = event.record['gasZahl']

        else:
            data_x['gasZ_m3'] = 0.0
            data_x['gasZ_kWh'] = 0.0
            data_x['gasZ_preis'] = 0.0

        if 'eleZahl' in event.record:
            ele_new = self.calculate_delta(event.record['eleZahl'], ele_val)
            data_x['eleZ_kWh'] = ele_new
            data_x['eleZ_preis'] = ele_new * self.StromPreis
            last_eleZ = event.record['eleZahl']

        else:
            data_x['eleZ_kWh'] = 0.0
            data_x['eleZ_preis'] = 0.0

        if 'eleAZahl' in event.record:
            elea_new = self.calculate_delta(event.record['eleAZahl'], ela_val)
            data_x['eleAZ_kWh'] = elea_new
            data_x['eleAZ_preis'] = elea_new * self.StromPreis
            last_elaZ = event.record['eleAZahl']

        else:
            data_x['eleAZ_kWh'] = 0.0
            data_x['eleAZ_preis'] = 0.0


        if 'wasZahl' in event.record and 'wasAZahl' in event.record:
            was_new = self.calculate_delta(event.record['wasZahl'], was_val)
            waa_new = self.calculate_delta(event.record['wasAZahl'], waa_val)
            data_x['wasZ_m3'] = was_new
            data_x['wasAZ_m3'] = waa_new
            data_x['wasG_preis'] = (was_new * self.WasserPreis) + ((was_new - waa_new) * self.AbwasserPreis)
            data_x['wasZ_preis'] = was_new * self.WasserPreis
            data_x['wasAZ_preis'] = waa_new * self.WasserPreis
            last_wasZ = event.record['wasZahl']
            last_waaZ = event.record['wasAZahl']

        else:
            data_x['wasZ_m3'] = 0.0
            data_x['wasAZ_m3'] = 0.0
            data_x['wasG_preis'] = 0.0
            data_x['wasZ_preis'] = 0.0
            data_x['wasAZ_preis'] = 0.0


        stand = str(last_gasZ) + ',' + str(last_wasZ) + ',' + str(last_waaZ) + ',' + str(last_eleZ) + ',' + str(last_elaZ)

        data_w = open('/home/weewx/archive/anfangZahl', 'w')
        data_w.write(stand)
        data_w.close()


        event.record.update(data_x)

    @staticmethod
    def calculate_delta(newtotal, oldtotal):
        """Calculate differential given two cumulative measurements."""
        if newtotal is not None and oldtotal is not None:
            if newtotal >= oldtotal:
                delta = newtotal - oldtotal
            else:
                log.info("Hand: counter reset detected: new=%s old=%s", newtotal, oldtotal)
                delta = 0.0
        else:
            delta = 0.0

        return delta


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
        obs_group_dict["gas_preis"] = "group_preis"
        obs_group_dict["was_preis"] = "group_preis"
        obs_group_dict["ele_preis"] = "group_preis"
        obs_group_dict["gasZ_preis"] = "group_preis"
        obs_group_dict["wasZ_preis"] = "group_preis"
        obs_group_dict["eleZ_preis"] = "group_preis"
        obs_group_dict["wasAZ_preis"] = "group_preis"
        obs_group_dict["eleAZ_preis"] = "group_preis"

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
#                                 Utilities
#===============================================================================

def calc_gas(gas_x):
    # berechnung m3 kWh und preis
    brennwert = 9.8      # wemaGas Zahl kWh pro m3
    zustandszahl = 0.95  # wemaGas Zahl laut Rechnung
    GasPreis = 0.0619    # 6.19 Cent/kWh

    if gas_x is not None:
        gasX_m3 = gas_x / 1000.0
        gasX_kWh = gasX_m3 * brennwert * zustandszahl
        gasX_preis = gasX_kWh * GasPreis

        return (gasX_m3, gasX_kWh, gasX_preis)

    else:
        return (None, None, None)

def calc_ele(ele_x):
    # berechnung kWh und preis
    # Impulsfaktor messung s0 100
    StromPreis = 0.272    # wemag 27.20 cent/kWh

    if ele_x is not None:
        elekWh = (ele_x / 100.0)
        elepreis = elekWh * StromPreis

        return (elekWh, elepreis)

    else:
        return (None, None)

def calc_eleA(ele_x):
    # berechnung kWh und preis
    StromPreis = 0.272    # wemag 27.20 cent/kWh

    if ele_x is not None:
        elekWh = (ele_x / 1000.0)
        elepreis = elekWh * StromPreis

        return (elekWh, elepreis)

    else:
        return (None, None)

def calc_was(was_x, wasA_x):
    # berechnung m3 und preis
    WasserPreis = 1.47         # ZV SN 1.47 Euro/m3
    AbwasserPreis = 2.65       # ZV SN 2.65 Euro/m3
    GrundWasser = 45.0         # Grund 45 E/a
    GrundAbwasser = 90.0       # GrundA 90.0 E/a

    if was_x is not None and wasA_x is not None:
        wasm3 = was_x / 1000.0
        wasAm3 = wasA_x / 1000.0

        waspreis = wasm3 * WasserPreis
        wasApreis = wasAm3 * WasserPreis

        return (wasm3, waspreis, wasAm3, wasApreis)

    else:
        return (None, None, None, None)

