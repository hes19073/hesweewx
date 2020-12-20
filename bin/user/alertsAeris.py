# -*- coding: utf-8 -*-
# $Id: alertsAeris.py 1651 2020-09-24 12:10:37Z hes $
# original by Pat O'Brien, August 19, 2018
# Copyright 2020 Hartmut Schweidler
#
# Wetter Warnung by Aeris

"""
in skin.conf
[Extras]
    # getAeris
    alerts_aeris = 1
    alerts_aeris_api_id =
    alerts_aeris_api_secret =
    alerts_aeris_stale = 3450
    alerts_aeris_limit = 1
    # alerts_aeris_lang = de         # en default, fr, es

    nachsehen und aktuelle Daten laden und auswerten
    Bereistellung der Warnmeldung als Text
"""

from __future__ import absolute_import

import datetime
import logging
import time
import calendar
import json
import os

import weewx
import weecfg
import weeutil.weeutil
import weeutil.logger
import weewx.units

from weewx.cheetahgenerator import SearchList
from weewx.tags import TimespanBinder
from weeutil.weeutil import TimeSpan

log = logging.getLogger(__name__)

# Print version in syslog
VERSION = "3.0.1"

log.info("alertsAeris WARNUNG version %s", VERSION)

class getAeris(SearchList):
    def __init__(self, generator):
        SearchList.__init__(self, generator)

    def get_extension_list(self, timespan, db_lookup):
        """ Download and parse the alerts data Aeris Weather   """
        # Setup label dict for text and titles
        try:
            d = self.generator.skin_dict['Labels']['Generic']
        except KeyError:
            d = {}
        label_dict = weeutil.weeutil.KeyDict(d)

        # Setup database manager
        binding = self.generator.config_dict['StdReport'].get('data_binding', 'wx_binding')
        manager = self.generator.db_binder.get_manager(binding)

        # Find the right HTML ROOT
        if 'HTML_ROOT' in self.generator.skin_dict:
            html_root = os.path.join(self.generator.config_dict['WEEWX_ROOT'],
                                      self.generator.skin_dict['HTML_ROOT'])
        else:
            html_root = os.path.join(self.generator.config_dict['WEEWX_ROOT'],
                                      self.generator.config_dict['StdReport']['HTML_ROOT'])

        # Return right away if we're not going to use the alerts.
        alerts_updated = time.time()
        if self.generator.skin_dict['Extras']['alerts_aeris'] == "0":
            # Return an empty SLE
            search_list_extension = {
                                 'alerts_html' : "",
                                 'alerts_html_long' : "",
                                 'alerts_update' : "alerts_updated",
                                }

            return [search_list_extension]

        """
        Alerts Data = Warnungen
        """
        alerts_file = "/home/weewx/archive/alertsAeris.json"
        alerts_aeris_id = self.generator.skin_dict['Extras']['alerts_aeris_api_id']
        alerts_aeris_secret = self.generator.skin_dict['Extras']['alerts_aeris_api_secret']
        alerts_stale_timer = self.generator.skin_dict['Extras']['alerts_aeris_stale']
        latitude = self.generator.config_dict['Station']['latitude']
        longitude = self.generator.config_dict['Station']['longitude']

        alerts_is_stale = False

        # Aries code
        def aeris_coded_alerts(data):
            # alerts by aeris weather

            alerts_dict = {
                    "TOE": label_dict["forecast_alert_code_TOE"],
                    "ADR": label_dict["forecast_alert_code_ADR"],
                    "AQA": label_dict["forecast_alert_code_AQA"],
                    "AQ.S": label_dict["forecast_alert_code_AQ_S"],
                    "AS.Y": label_dict["forecast_alert_code_AS_Y"],
                    "AR.W": label_dict["forecast_alert_code_AR_W"],
                    "AF.Y": label_dict["forecast_alert_code_AF_Y"],
                    "MH.Y": label_dict["forecast_alert_code_MH_Y"],
                    "AF.W": label_dict["forecast_alert_code_AF_W"],
                    "AVW": label_dict["forecast_alert_code_AVW"],
                    "AVA": label_dict["forecast_alert_code_AVA"],
                    "BH.S": label_dict["forecast_alert_code_BH_S"],
                    "BZ.W": label_dict["forecast_alert_code_BZ_W"],
                    "DU.Y": label_dict["forecast_alert_code_DU_Y"],
                    "BS.Y": label_dict["forecast_alert_code_BS_Y"],
                    "BW.Y": label_dict["forecast_alert_code_BW_Y"],
                    "CAE": label_dict["forecast_alert_code_CAE"],
                    "CDW": label_dict["forecast_alert_code_CDW"],
                    "CEM": label_dict["forecast_alert_code_CEM"],
                    "CF.Y": label_dict["forecast_alert_code_CF_Y"],
                    "CF.S": label_dict["forecast_alert_code_CF_S"],
                    "CF.W": label_dict["forecast_alert_code_CF_W"],
                    "CF.A": label_dict["forecast_alert_code_CF_A"],
                    "FG.Y": label_dict["forecast_alert_code_FG_Y"],
                    "MF.Y": label_dict["forecast_alert_code_MF_Y"],
                    "SM.Y": label_dict["forecast_alert_code_SM_Y"],
                    "MS.Y": label_dict["forecast_alert_code_MS_Y"],
                    "DS.W": label_dict["forecast_alert_code_DS_W"],
                    "EQW": label_dict["forecast_alert_code_EQW"],
                    "EVI": label_dict["forecast_alert_code_EVI"],
                    "EH.W": label_dict["forecast_alert_code_EH_W"],
                    "EH.A": label_dict["forecast_alert_code_EH_A"],
                    "EC.W": label_dict["forecast_alert_code_EC_W"],
                    "EC.A": label_dict["forecast_alert_code_EC_A"],
                    "RFD": label_dict["forecast_alert_code_RFD"],
                    "EW.W": label_dict["forecast_alert_code_EW_W"],
                    "FRW": label_dict["forecast_alert_code_FRW"],
                    "FW.A": label_dict["forecast_alert_code_FW_A"],
                    "FF.S": label_dict["forecast_alert_code_FF_S"],
                    "FF.W": label_dict["forecast_alert_code_FF_W"],
                    "FF.A": label_dict["forecast_alert_code_FF_A"],
                    "FE.W": label_dict["forecast_alert_code_FE_W"],
                    "FL.Y": label_dict["forecast_alert_code_FL_Y"],
                    "FL.S": label_dict["forecast_alert_code_FL_S"],
                    "FL.W": label_dict["forecast_alert_code_FL_W"],
                    "FA.W": label_dict["forecast_alert_code_FA_W"],
                    "FL.A": label_dict["forecast_alert_code_FL_A"],
                    "FA.A": label_dict["forecast_alert_code_FA_A"],
                    "FZ.W": label_dict["forecast_alert_code_FZ_W"],
                    "FZ.A": label_dict["forecast_alert_code_FZ_A"],
                    "ZL.Y": label_dict["forecast_alert_code_ZL_Y"],
                    "ZF.Y": label_dict["forecast_alert_code_ZF_Y"],
                    "ZR.W": label_dict["forecast_alert_code_ZR_W"],
                    "UP.Y": label_dict["forecast_alert_code_UP_Y"],
                    "FR.Y": label_dict["forecast_alert_code_FR_Y"],
                    "GL.W": label_dict["forecast_alert_code_GL_W"],
                    "GL.A": label_dict["forecast_alert_code_GL_A"],
                    "HZ.W": label_dict["forecast_alert_code_HZ_W"],
                    "HZ.A": label_dict["forecast_alert_code_HZ_A"],
                    "HMW": label_dict["forecast_alert_code_HMW"],
                    "SE.W": label_dict["forecast_alert_code_SE_W"],
                    "SE.A": label_dict["forecast_alert_code_SE_A"],
                    "HWO": label_dict["forecast_alert_code_HWO"],
                    "HT.Y": label_dict["forecast_alert_code_HT_Y"],
                    "HT.W": label_dict["forecast_alert_code_HT_W"],
                    "UP.W": label_dict["forecast_alert_code_UP_W"],
                    "UP.A": label_dict["forecast_alert_code_UP_A"],
                    "SU.Y": label_dict["forecast_alert_code_SU_Y"],
                    "SU.W": label_dict["forecast_alert_code_SU_W"],
                    "HW.W": label_dict["forecast_alert_code_HW_W"],
                    "HW.A": label_dict["forecast_alert_code_HW_A"],
                    "HF.W": label_dict["forecast_alert_code_HF_W"],
                    "HF.A": label_dict["forecast_alert_code_HF_A"],
                    "HU.S": label_dict["forecast_alert_code_HU_S"],
                    "HU.W": label_dict["forecast_alert_code_HU_W"],
                    "HU.A": label_dict["forecast_alert_code_HU_A"],
                    "FA.Y": label_dict["forecast_alert_code_FA_Y"],
                    "IS.W": label_dict["forecast_alert_code_IS_W"],
                    "LE.W": label_dict["forecast_alert_code_LE_W"],
                    "LW.Y": label_dict["forecast_alert_code_LW_Y"],
                    "LS.Y": label_dict["forecast_alert_code_LS_Y"],
                    "LS.S": label_dict["forecast_alert_code_LS_S"],
                    "LS.W": label_dict["forecast_alert_code_LS_W"],
                    "LS.A": label_dict["forecast_alert_code_LS_A"],
                    "LEW": label_dict["forecast_alert_code_LEW"],
                    "LAE": label_dict["forecast_alert_code_LAE"],
                    "LO.Y": label_dict["forecast_alert_code_LO_Y"],
                    "MA.S": label_dict["forecast_alert_code_MA_S"],
                    "NUW": label_dict["forecast_alert_code_NUW"],
                    "RHW": label_dict["forecast_alert_code_RHW"],
                    "RA.W": label_dict["forecast_alert_code_RA_W"],
                    "FW.W": label_dict["forecast_alert_code_FW_W"],
                    "RFW": label_dict["forecast_alert_code_RFW"],
                    "RP.S": label_dict["forecast_alert_code_RP_S"],
                    "SV.W": label_dict["forecast_alert_code_SV_W"],
                    "SV.A": label_dict["forecast_alert_code_SV_A"],
                    "SV.S": label_dict["forecast_alert_code_SV_S"],
                    "TO.S": label_dict["forecast_alert_code_TO_S"],
                    "SPW": label_dict["forecast_alert_code_SPW"],
                    "NOW": label_dict["forecast_alert_code_NOW"],
                    "SC.Y": label_dict["forecast_alert_code_SC_Y"],
                    "SW.Y": label_dict["forecast_alert_code_SW_Y"],
                    "RB.Y": label_dict["forecast_alert_code_RB_Y"],
                    "SI.Y": label_dict["forecast_alert_code_SI_Y"],
                    "SO.W": label_dict["forecast_alert_code_SO_W"],
                    "SQ.W": label_dict["forecast_alert_code_SQ_W"],
                    "SQ.A": label_dict["forecast_alert_code_SQ_A"],
                    "SB.Y": label_dict["forecast_alert_code_SB_Y"],
                    "SN.W": label_dict["forecast_alert_code_SN_W"],
                    "MA.W": label_dict["forecast_alert_code_MA_W"],
                    "SPS": label_dict["forecast_alert_code_SPS"],
                    "SG.W": label_dict["forecast_alert_code_SG_W"],
                    "SS.W": label_dict["forecast_alert_code_SS_W"],
                    "SS.A": label_dict["forecast_alert_code_SS_A"],
                    "SR.W": label_dict["forecast_alert_code_SR_W"],
                    "SR.A": label_dict["forecast_alert_code_SR_A"],
                    "TO.W": label_dict["forecast_alert_code_TO_W"],
                    "TO.A": label_dict["forecast_alert_code_TO_A"],
                    "TC.S": label_dict["forecast_alert_code_TC_S"],
                    "TR.S": label_dict["forecast_alert_code_TR_S"],
                    "TR.W": label_dict["forecast_alert_code_TR_W"],
                    "TR.A": label_dict["forecast_alert_code_TR_A"],
                    "TS.Y": label_dict["forecast_alert_code_TS_Y"],
                    "TS.W": label_dict["forecast_alert_code_TS_W"],
                    "TS.A": label_dict["forecast_alert_code_TS_A"],
                    "TY.S": label_dict["forecast_alert_code_TY_S"],
                    "TY.W": label_dict["forecast_alert_code_TY_W"],
                    "TY.A": label_dict["forecast_alert_code_TY_A"],
                    "VOW": label_dict["forecast_alert_code_VOW"],
                    "WX.Y": label_dict["forecast_alert_code_WX_Y"],
                    "WX.W": label_dict["forecast_alert_code_WX_W"],
                    "WI.Y": label_dict["forecast_alert_code_WI_Y"],
                    "WC.Y": label_dict["forecast_alert_code_WC_Y"],
                    "WC.W": label_dict["forecast_alert_code_WC_W"],
                    "WC.A": label_dict["forecast_alert_code_WC_A"],
                    "WI.W": label_dict["forecast_alert_code_WI_W"],
                    "WS.W": label_dict["forecast_alert_code_WS_W"],
                    "WS.A": label_dict["forecast_alert_code_WS_A"],
                    "LE.A": label_dict["forecast_alert_code_LE_A"],
                    "BZ.A": label_dict["forecast_alert_code_BZ_A"],
                    "WW.Y": label_dict["forecast_alert_code_WW_Y"],
                    "LE.Y": label_dict["forecast_alert_code_LE_Y"],
                    "ZR.Y": label_dict["forecast_alert_code_ZR_Y"],
                    "AW.WI.MN": label_dict["forecast_alert_code_AW_WI_MN"],
                    "AW.WI.MD": label_dict["forecast_alert_code_AW_WI_MD"],
                    "AW.WI.SV": label_dict["forecast_alert_code_AW_WI_SV"],
                    "AW.WI.EX": label_dict["forecast_alert_code_AW_WI_EX"],
                    "AW.SI.MN": label_dict["forecast_alert_code_AW_SI_MN"],
                    "AW.SI.MD": label_dict["forecast_alert_code_AW_SI_MD"],
                    "AW.SI.SV": label_dict["forecast_alert_code_AW_SI_SV"],
                    "AW.SI.EX": label_dict["forecast_alert_code_AW_SI_EX"],
                    "AW.TS.MN": label_dict["forecast_alert_code_AW_TS_MN"],
                    "AW.TS.MD": label_dict["forecast_alert_code_AW_TS_MD"],
                    "AW.TS.SV": label_dict["forecast_alert_code_AW_TS_SV"],
                    "AW.TS.EX": label_dict["forecast_alert_code_AW_TS_EX"],
                    "AW.LI.MN": label_dict["forecast_alert_code_AW_LI_MN"],
                    "AW.LI.MD": label_dict["forecast_alert_code_AW_LI_MD"],
                    "AW.LI.SV": label_dict["forecast_alert_code_AW_LI_SV"],
                    "AW.LI.EX": label_dict["forecast_alert_code_AW_LI_EX"],
                    "AW.FG.MN": label_dict["forecast_alert_code_AW_FG_MN"],
                    "AW.FG.MD": label_dict["forecast_alert_code_AW_FG_MD"],
                    "AW.FG.SV": label_dict["forecast_alert_code_AW_FG_SV"],
                    "AW.FG.EX": label_dict["forecast_alert_code_AW_FG_EX"],
                    "AW.HT.MN": label_dict["forecast_alert_code_AW_HT_MN"],
                    "AW.HT.MD": label_dict["forecast_alert_code_AW_HT_MD"],
                    "AW.HT.SV": label_dict["forecast_alert_code_AW_HT_SV"],
                    "AW.HT.EX": label_dict["forecast_alert_code_AW_HT_EX"],
                    "AW.LT.MN": label_dict["forecast_alert_code_AW_LT_MN"],
                    "AW.LT.MD": label_dict["forecast_alert_code_AW_LT_MD"],
                    "AW.LT.SV": label_dict["forecast_alert_code_AW_LT_SV"],
                    "AW.LT.EX": label_dict["forecast_alert_code_AW_LT_EX"],
                    "AW.CE.MN": label_dict["forecast_alert_code_AW_CE_MN"],
                    "AW.CE.MD": label_dict["forecast_alert_code_AW_CE_MD"],
                    "AW.CE.SV": label_dict["forecast_alert_code_AW_CE_SV"],
                    "AW.CE.EX": label_dict["forecast_alert_code_AW_CE_EX"],
                    "AW.FR.MN": label_dict["forecast_alert_code_AW_FR_MN"],
                    "AW.FR.MD": label_dict["forecast_alert_code_AW_FR_MD"],
                    "AW.FR.SV": label_dict["forecast_alert_code_AW_FR_SV"],
                    "AW.FR.EX": label_dict["forecast_alert_code_AW_FR_EX"],
                    "AW.AV.MN": label_dict["forecast_alert_code_AW_AV_MN"],
                    "AW.AV.MD": label_dict["forecast_alert_code_AW_AV_MD"],
                    "AW.AV.SV": label_dict["forecast_alert_code_AW_AV_SV"],
                    "AW.AV.EX": label_dict["forecast_alert_code_AW_AV_EX"],
                    "AW.RA.MN": label_dict["forecast_alert_code_AW_RA_MN"],
                    "AW.RA.MD": label_dict["forecast_alert_code_AW_RA_MD"],
                    "AW.RA.SV": label_dict["forecast_alert_code_AW_RA_SV"],
                    "AW.RA.EX": label_dict["forecast_alert_code_AW_RA_EX"],
                    "AW.FL.MN": label_dict["forecast_alert_code_AW_FL_MN"],
                    "AW.FL.MD": label_dict["forecast_alert_code_AW_FL_MD"],
                    "AW.FL.SV": label_dict["forecast_alert_code_AW_FL_SV"],
                    "AW.FL.EX": label_dict["forecast_alert_code_AW_FL_EX"],
                    "AW.RF.MN": label_dict["forecast_alert_code_AW_RF_MN"],
                    "AW.RF.MD": label_dict["forecast_alert_code_AW_RF_MD"],
                    "AW.RF.SV": label_dict["forecast_alert_code_AW_RF_SV"],
                    "AW.RF.EX": label_dict["forecast_alert_code_AW_RF_EX"],
                    "AW.UK.MN": label_dict["forecast_alert_code_AW_UK_MN"],
                    "AW.UK.MD": label_dict["forecast_alert_code_AW_UK_MD"],
                    "AW.UK.SV": label_dict["forecast_alert_code_AW_UK_SV"],
                    "AW.UK.EX": label_dict["forecast_alert_code_AW_UK_EX"],
            }

            return alerts_dict[data]

        if self.generator.skin_dict['Extras']['alerts_aeris_limit']:
            alerts_aeris_limit = self.generator.skin_dict['Extras']['alerts_aeris_limit']
            alerts_aeris_url = "https://api.aerisapi.com/alerts/%s,%s?&format=json&limit=%s&client_id=%s&client_secret=%s" % ( latitude, longitude, alerts_aeris_limit, alerts_aeris_id, alerts_aeris_secret )
        else:
            # Default to 1 alerts to show if the option is missing. Can go up to 10
            alerts_aeris_url = "https://api.aerisapi.com/alerts/%s,%s?&format=json&limit=1&client_id=%s&client_secret=%s" % ( latitude, longitude, alerts_aeris_id, alerts_aeris_secret )
            # alerts_aeris_url = "https://api.aerisapi.com/alerts/%s,%s?&format=json&limit=1&lang=%s&client_id=%s&client_secret=%s" % ( latitude, longitude, aeris_lang, alerts_aeris_id, alerts_aeris_secret )

        # Determine if the file exists and get it's modified time
        if os.path.isfile(alerts_file):
            if (int(time.time()) - int(os.path.getmtime(alerts_file))) > int(alerts_stale_timer):
                alerts_is_stale = True
        else:
            # File doesn't exist, download a new copy
            alerts_is_stale = True

        # File is stale, download a new copy
        if alerts_is_stale:
            try:
                try:
                    # Python 3
                    from urllib.request import Request, urlopen
                except ImportError:
                    # Python 2
                    from urllib2 import Request, urlopen
                user_agent = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_4; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.472.63 Safari/534.3'
                headers = { 'User-Agent' : user_agent }
                # alerts conditions
                req = Request( alerts_aeris_url, None, headers )
                response = urlopen( req )
                alerts_page = response.read()
                response.close()

                # Combine timestamp and alerts into 1 file
                try:
                    alerts_file_result = json.dumps( {"timestamp": int(time.time()), "aeris": [json.loads(alerts_page)]} )
                except:
                    alerts_file_result = json.dumps( {"timestamp": int(time.time()), "aeris": [json.loads(alerts_page.decode('utf-8'))]} )

            except Exception as error:
                raise Warning( "Error downloading aeris data. Check the URL in your configuration and try again. You are trying to use URL: %s, and the error is: %s" % ( alerts_aeris_url, error ) )

            # Save aeris data to file. w+ creates the file if it doesn't exist, and truncates the file and re-writes it everytime
            try:
                with open(alerts_file, 'wb+') as file:
                    # Python 2/3
                    try:
                        file.write(alerts_file_result.encode('utf-8'))
                    except:
                        file.write(alerts_file_result)
                    log.info( "New Alerts file downloaded to %s" % alerts_file )
                    #file.close()
            except IOError as e:
                raise Warning( "Error writing aeris info to %s. Reason: %s" % ( alerts_file, e) )

        # Process the alerts file
        with open(alerts_file, "r") as read_file:
            data = json.load(read_file)

        read_file.close()

        html_alerts = ""
        html_alerts_long = ""
        alerts_updated = time.strftime("%d.%m.%Y %H:%M", time.localtime(data['timestamp']))
        if len(data["aeris"][0]["response"]) > 0:
            alerts_aeris_title = aeris_coded_alerts( data['aeris'][0]['response'][0]['details']['type'] )
            alerts_aeris_color = data['aeris'][0]['response'][0]['details']['color']
            alerts_aeris_body = data['aeris'][0]['response'][0]['details']['body'].replace('\n', '<br>')
            alerts_aeris_bodyFull = data['aeris'][0]['response'][0]['details']['bodyFull'].replace('\n', '<br>')
            # alerts_aeris_link = data['aeris'][0]['response'][0]['details']['name']
            # alerts_aeris_link = data['aeris'][0]['response'][0]['details']['type']
            alerts_aeris_begins = time.strftime("%d.%m.%Y %H:%M", time.localtime(data['aeris'][0]['response'][0]['timestamps']['begins']))
            alerts_aeris_expire = time.strftime("%d.%m.%Y %H:%M", time.localtime(data['aeris'][0]['response'][0]['timestamps']['expires']))
            alerts_aeris_issued = time.strftime("%d.%m.%Y %H:%M", time.localtime(data['aeris'][0]['response'][0]['timestamps']['issued']))
            alerts_updated = time.strftime("%d.%m.%Y %H:%M", time.localtime(data['timestamp']))
            # gen text
            output = '<div style="background-color:#' + alerts_aeris_color + ';">'
            output += '<h3>' + alerts_aeris_title + '</h3>'
            output += 'gültig ab: <i> ' + alerts_aeris_begins + '</i>'
            output += '  bis: <i> ' + alerts_aeris_expire + '</i>'
            output += '<p>' + alerts_aeris_body + '</p>'
            output += '</div> <!-- end .alerts_aeris -->'
            # Add to the output
            html_alerts += output
            # add to long output
            html_alerts_long = html_alerts + '<p>' + alerts_aeris_bodyFull + '</p>'

        else:
            html_alerts = ""
            html_alerts_long = ""

        # Build the search list with the new values
        search_list_extension = {
                                 'alerts_html' : html_alerts,
                                 'alerts_html_long' : html_alerts_long,
                                 'alerts_update' : alerts_updated,
                                }

        # Finally, return our extension as a list:
        return [search_list_extension]
# end
