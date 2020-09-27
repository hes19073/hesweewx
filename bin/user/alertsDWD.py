# -*- coding: utf-8 -*-
# $Id: dwd.py  2020-08-27 12:10:37Z hes $
# original by Pat O'Brien, August 19, 2018
# Copyright 2019 Hartmut Schweidler
# DWD Wetter Warnungen
""" in skin.conf by
    [Extras]
        dwd_enabled = 1 or 0
        dwd_stale = 3600 # alle Stunde
        dwd_id = 813076071   # Gemeinde Klein Rogahn 813075001 LK LWL alt
        dwd_url = https://www.dwd.de/DWD/warnungen/warnapp/json/warnings.json


        Gemeinde WARNCELLID 8 + AGS
        LK                  1 + AGS
        Sondergebiete       9 + AGS

nachsehen und aktuelle Daten laden und auswerten
Bereistellung der Warnmeldung als Text """

from __future__ import absolute_import

import datetime
import logging
import time
import json
import os
import re

import weewx
import weecfg
import weeutil.logger
import weeutil.weeutil

from weewx.cheetahgenerator import SearchList
from weeutil.weeutil import TimeSpan
from weewx.units import obs_group_dict

log = logging.getLogger(__name__)

# Print version in syslog
VERSION = "3.0.1"

log.info("DWD-Warnungen Version: %s", VERSION)


class getWarnung(SearchList):
    def __init__(self, generator):
        SearchList.__init__(self, generator)

    def get_extension_list(self, timespan, db_lookup):

        """ Download the warnung data by DWD warnings.json
            to file to warnung.json
            This is not a json file so that at the
            start 'warnWetter.loadWarnings('
            and the end ');' to be deleted
            leere Warnmeldung vom DWD
            warnWetter.loadWarnings({"time":1598865395000,"warnings":{}, \
            "vorabInformation":{},"copyright":"Copyright Deutscher Wetterdienst"});

        """

        # Return right away if we're not going to use the forecast.
        if self.generator.skin_dict['Extras']['dwd_enabled'] == "0":
            # Return an empty SLE
            warnung_updated = datetime.now()
            w_headline = ''
            search_list_extension = {
                                     'warn_update' : warnung_updated,
                                     'warn_kopf': w_headline,
                                    }

            return [search_list_extension]


        warnung_file = "/home/weewx/archive/warnung.txt"
        dwd_file = '/home/weewx/archive/warn.json'
        #latitude = self.generator.config_dict['Station']['latitude']
        #longitude = self.generator.config_dict['Station']['longitude']
        warnung_stale_timer = self.generator.skin_dict['Extras']['dwd_stale']
        warnung_id = self.generator.skin_dict['Extras']['dwd_id']
        warnung_url = "https://www.dwd.de/DWD/warnungen/warnapp/json/warnings.json"

        obs_group_dict["warn_start"] = "group_time"
        obs_group_dict["warn_end"] = "group_time"

        warnung_is_stale = False

        # Determine if the file exists and get it's modified time
        if os.path.isfile(warnung_file):
            if (int(time.time()) - int(os.path.getmtime(warnung_file))) > int(warnung_stale_timer):
                warnung_is_stale = True
        else:
            # File doesn't exist, download a new copy
            warnung_is_stale = True

        # File is stale, download a new copy
        if warnung_is_stale:
            import urllib.request, urllib.error, urllib.parse
            urllib.request.urlretrieve(warnung_url, warnung_file)

            log.info("New DWD WetterWarnungen downloaded to %s", warnung_file)

        # Meldungen aus Datei 'warnung_file' als 'json-Daten' aufbereiten
        # zuerst 24 Zeichen am Anfang entfernen 'warnWetter.loadWarnings('
        # dann am Ende die Zeichen ');' entfernen
        dataText = open(warnung_file)

        for line in dataText:
           line = line[24:]
           dataJson = line.replace(');', '')

        dataText.close()

        outfile = open(dwd_file, "w")
        outfile.write(dataJson)

        outfile.close()

        #log.info("DWD Wetter Warnungen einlesen")

        # Datei dataJson als Json-String-Daten verarbeiten
        with open(dwd_file, encoding="utf8") as read_file:
            data = json.loads(read_file.read())

        # Datum der Aktualisierung der warnung_file Datei
        warnung_updated = time.strftime("%d.%m.%Y %H:%M", time.localtime(int(data["time"] / 1000)))

        # wenn der json-String kleiner als 200 Zeichen lang ist
        # KEINE Wetterwarnungen vom DWD vorhanden
        if len(data) < 200:
            w_start = ''
            w_end = ''
            w_type = ''
            w_level = ''
            w_description = ''
            w_event = ''
            w_headline = ''
            w_instruction = ''
            # region = ''
            # w_state = ''
            # w_stateShort = ''
            # altitudeStart = ''
            # altitudeEnd = ''

        else:
            i = 0
            # WARNCELLID = 113076000 NEU für Kreis Ludwiglust-Parchim
            # WARNCELLID = 913076001 ALT für Kreis Ludwigslust-Parchim West
            # todo int(WARNCELLID) for if '913076001' in obj:
            # and in data['warnings']['913076001'][0]
            for obj in data['warnings']:
                i = +1
                if '913076001' in obj:
                    w_start = time.strftime("%d.%m.%Y %H:%M", time.localtime(int(data['warnings']['913076001'][0]['start']) / 1000))
                    w_end = time.strftime("%d.%m.%Y %H:%M", time.localtime(int(data['warnings']['913076001'][0]['end']) / 1000))
                    w_type = data['warnings']['913076001'][0]['type']
                    w_level = data['warnings']['913076001'][0]['level']
                    w_description = data['warnings']['913076001'][0]['description']
                    w_event = data['warnings']['913076001'][0]['event']
                    w_headline = data['warnings']['913076001'][0]['headline']
                    w_instruction = data['warnings']['913076001'][0]['instruction']
                    # region = data['warnings']['913076001'][0]['regionName']
                    # w_state = data['warnings']['913076001'][0]['state']
                    # w_stateShort = data['warnings']['913076001'][0]['stateShort']
                    # altitudeStart = data['warnings']['913076001'][0]['altitudeStart']
                    # altitudeEnd = data['warnings']['913076001'][0]['altitudeEnd']


                else:
                    # No DWD data
                    w_start = ''
                    w_end = ''
                    w_type = ''
                    w_level = ''
                    w_description = ''
                    w_event = ''
                    w_headline = ''
                    w_instruction = ''
                    # region = ''
                    # w_state = ''
                    # w_stateShort = ''
                    # altitudeStart = ''
                    # altitudeEnd = ''

        # Put into a dictionary to return
        search_list_extension  = {
                                  'warn_update' : warnung_updated,
                                  'warn_meldung' : w_description,
                                  'warn_start' : w_start,
                                  'warn_end': w_end,
                                  'warn_type': w_type,
                                  'warn_event': w_event,
                                  'warn_level': w_level,
                                  'warn_kopf': w_headline,
                                  'warn_inst': w_instruction,
                                  #'warn_region': region,
                                  #'warn_stateS': w_stateShort,
                                  #'warn_state': w_state,
                                  #'warn_h_sta' : altitudeStart,
                                  #'warn_h_end': altitudeEnd,
                                 }

        # Return our data
        return [search_list_extension]
