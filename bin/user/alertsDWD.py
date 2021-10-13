# -*- coding: utf-8 -*-
# alertsDWD.py  2021-03-17 12:10:37Z hes $
# original by Pat O'Brien, August 19, 2018
# and by Johanna Roedenbeck, 16.03.2021 weewx-DWD
# Copyright 2021 Hartmut Schweidler
# DWD Wetter Warnungen
# licensed under the terms of the General Public License (GPL) v3
""" in skin.conf by
    [Extras]
        dwd_enabled = 1 or 0
        dwd_stale = 3600 # alle Stunde
        dwd_id = 913076001   # Gemeinde Klein Rogahn 913075001 LK LWL alt
        dwd_url = https://www.dwd.de/DWD/warnungen/warnapp/json/warnings.json
        dwd_icons = 'xicons/dwd_icons'

        Gemeinde WARNCELLID 8 + AGS
        LK                  1 + AGS
        Sondergebiete       9 + AGS

nachsehen und aktuelle Daten laden und auswerten
Bereistellung der Warnmeldung als Text 
und als warn_MV.inc"""

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

log = logging.getLogger(__name__)

# Print version in syslog
VERSION = "3.0.2"

log.info("DWD-Warnungen alerts_DWD Version: %s", VERSION)


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
            warnung_updated = time.time()
            w_head = ''
            search_list_extension = {
                                     'warn_update': warnung_updated,
                                     'warn_kopf': w_head,
                                    }

            return [search_list_extension]

        warnung_file = "/home/weewx/archive/warnung.txt"
        dwd_file = '/home/weewx/archive/warn.json'
        warnung_stale_timer = self.generator.skin_dict['Extras']['dwd_stale']
        warn_cell_id = self.generator.skin_dict['Extras']['dwd_id']
        warn_icons = self.generator.skin_dict['Extras']['dwd_icons']
        target_path = self.generator.skin_dict['Extras']['dwd_path']
        warnung_url = "https://www.dwd.de/DWD/warnungen/warnapp/json/warnings.json"
        w_start = ''
        w_end = ''
        w_type = ''
        w_level = ''
        w_desc = ''
        w_event = ''
        w_head = ''
        w_inst = ''
        w_stat = 'MV'
        warnung_is_stale = False

        # Der DWD verwendet ganz offensichtlich nicht die nach ISO genormten
        # Abkuerzungen fuer Bundeslaender.
        dwd_copy={
          'SN':'https://www.dwd.de/DE/wetter/warnungen_aktuell/warnlagebericht/sachsen/warnlage_sac_node.html',
          'TH':'https://www.dwd.de/DE/wetter/warnungen_aktuell/warnlagebericht/thueringen/warnlage_thu_node.html',
          'SA':'https://www.dwd.de/DE/wetter/warnungen_aktuell/warnlagebericht/sachen_anhalt/warnlage_saa_node.html',
          'BB':'https://www.dwd.de/DE/wetter/warnungen_aktuell/warnlagebericht/berlin_brandenburg/warnlage_bb_node.html',
          'MV':'https://www.dwd.de/DE/wetter/warnungen_aktuell/warnlagebericht/mecklenburg_vorpommern/warnlage_mv_node.html',
          'NS':'https://www.dwd.de/DE/wetter/warnungen_aktuell/warnlagebericht/niedersachsen_bremen/warnlage_nds_node.html',
          'HB':'https://www.dwd.de/DE/wetter/warnungen_aktuell/warnlagebericht/niedersachsen_bremen/warnlage_nds_node.html',
          'HE':'https://www.dwd.de/DE/wetter/warnungen_aktuell/warnlagebericht/hessen/warnlage_hes_node.html',
          'NRW':'https://www.dwd.de/DE/wetter/warnungen_aktuell/warnlagebericht/nordrhein_westfalen/warnlage_nrw_node.html',
          'BY':'https://www.dwd.de/DE/wetter/warnungen_aktuell/warnlagebericht/nordrhein_westfalen/warnlage_nrw_node.html',
          'SH':'https://www.dwd.de/DE/wetter/warnungen_aktuell/warnlagebericht/schleswig_holstein_hamburg/warnlage_shh_node.html',
          'HH':'https://www.dwd.de/DE/wetter/warnungen_aktuell/warnlagebericht/schleswig_holstein_hamburg/warnlage_shh_node.html',
          'RP':'https://www.dwd.de/DE/wetter/warnungen_aktuell/warnlagebericht/rheinland-pfalz_saarland/warnlage_rps_node.html',
          'SL':'https://www.dwd.de/DE/wetter/warnungen_aktuell/warnlagebericht/rheinland-pfalz_saarland/warnlage_rps_node.html',
          'BW':'https://www.dwd.de/DE/wetter/warnungen_aktuell/warnlagebericht/baden-wuerttemberg/warnlage_baw_node.html'}

        # level als Text
        dwd_level=(
          'keine Warnung',     # 0 no warning
          'Vorinformation',    # 1 preliminary info
          'Wetterwarnung',     # 2 minor
          'markantes Wetter',  # 3 moderate
          'Unwetterwarnung',   # 4 severe
          'extremes Unwetter') # 5 extreme

        # Namensbestandteile der Warn-Icons
        dwd_warning_type=(
          'gewitter',          # 0 thunderstorm
          'wind',              # 1 wind/storm
          'regen',             # 2 rain
          'schnee',            # 3 snow
          'nebel',             # 4 fog
          'frost',             # 5 frost
          'eis',               # 6 ice
          'tau',               # 7 thawing
          'hitze',             # 8 heat
          'uv')                # 9 uv warning

        def dwd_warn_icon_file(type, level):
            if type == 8 or type == 9:
                return "warn_icons_%s.png" % dwd_warning_type[type]
            if level < 2 or level > 5: return None
            return "warn_icons_%s_%s.png" % (dwd_warning_type[type],level-1)

        def dwd_level_text(level):
            try:
                return dwd_level[level]
            except IndexError:
                if level == 10: return 'Hitzewarnung'
            return None

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

        # log.info("DWD Wetter Warnungen einlesen")
        # Datei dataJson als Json-String-Daten verarbeiten
        with open(dwd_file, encoding="utf8") as read_file:
            data = json.loads(read_file.read())

        if data is not None:
            if True:
                try:
                    ts = data['time']
                except IndexError:
                    ts = None
                try:
                    wrn = data['warnings']
                except IndexError:
                    wrn = None
                try:
                    vrb = data['vorabInformation']
                except IndexError:
                    vrb = None
                try:
                    cpy = data['copyright']
                except IndexError:
                    cpy = None

        # Datum der Aktualisierung der warnung_file Datei
        warnung_updated = time.strftime("%d.%m.%Y %H:%M", time.localtime(int(data["time"] / 1000)))
        s = ""
        for warni in data['warnings']:
            s = ""

            if int(warni) == 913076001:
                w_regi = data['warnings']['913076001'][0]['regionName']
                w_end = time.strftime("%d.%m.%Y %H:%M", time.localtime(int(data['warnings']['913076001'][0]['end']) / 1000))
                w_start = time.strftime("%d.%m.%Y %H:%M", time.localtime(int(data['warnings']['913076001'][0]['start']) / 1000))
                w_type = data['warnings']['913076001'][0]['type']
                w_land = data['warnings']['913076001'][0]['state']
                w_level = data['warnings']['913076001'][0]['level']
                w_desc = data['warnings']['913076001'][0]['description']
                w_event = data['warnings']['913076001'][0]['event']
                w_head = data['warnings']['913076001'][0]['headline']
                w_inst = data['warnings']['913076001'][0]['instruction']
                w_stat = data['warnings']['913076001'][0]['stateShort']

                s += '<p style="margin-top:5px"><strong>%s</strong></p>\n' % w_regi
                s += '<table style="vertical-align:middle"><tr style="vertical-align:middle">\n'
                __icon_fn = dwd_warn_icon_file(w_type, w_level)

                if __icon_fn is not None:
                    s += '<td style="width:60px"><img src="%s/%s" /></td>\n' % (warn_icons, __icon_fn)
                __size = 110 if int(w_level) > 2 else 100
                s += '<td><p style="font-size:%i%%; margin-bottom:0">%s</p>\n' % (__size, w_head)
                s += '<p style="font-size:80%%">gültig vom %s bis %s</p></td>\n' % (w_start, w_end)
                s += '</tr></table>\n'

                if w_desc:
                    s += "<p>%s</p>\n" % w_desc
                if w_inst:
                    s += "<p>%s</p>\n" % w_inst

                s += '<p style="font-size:40%%">%s &ndash; %s &emsp;&ndash;&emsp; %s &ndash; %s</p>' % (w_type, w_event, w_level, dwd_level_text(w_level))
                s += '<p style="font-size:80%%">Quelle: <a href="%s" target="_blank">DWD</a>&nbsp;%s</p>\n' % (dwd_copy[w_stat], cpy)
                break

            else:
                w_start = ''
                w_end = ''
                w_type = ''
                w_level = ''
                w_desc = ''
                w_event = ''
                w_head = ''
                w_inst = ''
                w_stat = 'MV'
                s = '<p>Zur Zeit keine Warnungen</p>'

        with open("%s/warn-%s.inc" % (target_path, w_stat),"w") as file:
            file.write(s)

        # Put into a dictionary to return
        search_list_extension  = {
                                  'warn_update': warnung_updated,
                                  'warn_meldung': w_desc,
                                  'warn_start': w_start,
                                  'warn_end': w_end,
                                  'warn_type': w_type,
                                  'warn_event': w_event,
                                  'warn_level': w_level,
                                  'warn_kopf': w_head,
                                  'warn_inst': w_inst,
                                  # 'warn_region': w_regi,
                                  # 'warn_stateShort': w_stat,
                                  # 'warn_state': w_land,
                                  # 'warn_h_sta' : altitudeStart,
                                  # 'warn_h_end': altitudeEnd,
                                 }

        # Return our data
        return [search_list_extension]
