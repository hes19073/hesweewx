//
//

#if $Extras.has_key("aeris_enabled") and $Extras.aeris_enabled == '1'
function ajaxforecast() {
    jQuery.getJSON("/home/weewx/archive/aeris_forecast.json", update_forecast_data);
};

function aeris_coded_weather( data, full_observation = false ) {
    // https://www.aerisweather.com/support/docs/api/reference/weather-codes/
    var output = "";
    var coverage_code = data.split(":")[0]
    var intensity_code = data.split(":")[1]
    var weather_code = data.split(":")[2]

    var cloud_dict = {
        "CL": "$obs.label.forecast_cloud_code_CL",
        "FW": "$obs.label.forecast_cloud_code_FW",
        "SC": "$obs.label.forecast_cloud_code_SC",
        "BK": "$obs.label.forecast_cloud_code_BK",
        "OV": "$obs.label.forecast_cloud_code_OV"
    }

    var coverage_dict = {
        "AR": "$obs.label.forecast_coverage_code_AR",
        "BR": "$obs.label.forecast_coverage_code_BR",
        "C": "$obs.label.forecast_coverage_code_C",
        "D": "$obs.label.forecast_coverage_code_D",
        "FQ": "$obs.label.forecast_coverage_code_FQ",
        "IN": "$obs.label.forecast_coverage_code_IN",
        "IS": "$obs.label.forecast_coverage_code_IS",
        "L": "$obs.label.forecast_coverage_code_L",
        "NM": "$obs.label.forecast_coverage_code_NM",
        "O": "$obs.label.forecast_coverage_code_O",
        "PA": "$obs.label.forecast_coverage_code_PA",
        "PD": "$obs.label.forecast_coverage_code_PD",
        "S": "$obs.label.forecast_coverage_code_S",
        "SC": "$obs.label.forecast_coverage_code_SC",
        "VC": "$obs.label.forecast_coverage_code_VC",
        "WD": "$obs.label.forecast_coverage_code_WD"
    }

    var intensity_dict = {
        "VL": "$obs.label.forecast_intensity_code_VL",
        "L": "$obs.label.forecast_intensity_code_L",
        "H": "$obs.label.forecast_intensity_code_H",
        "VH": "$obs.label.forecast_intensity_code_VH"
    }

    var weather_dict = {
        "A": "$obs.label.forecast_weather_code_A",
        "BD": "$obs.label.forecast_weather_code_BD",
        "BN": "$obs.label.forecast_weather_code_BN",
        "BR": "$obs.label.forecast_weather_code_BR",
        "BS": "$obs.label.forecast_weather_code_BS",
        "BY": "$obs.label.forecast_weather_code_BY",
        "F": "$obs.label.forecast_weather_code_F",
        "FR": "$obs.label.forecast_weather_code_FR",
        "H": "$obs.label.forecast_weather_code_H",
        "IC": "$obs.label.forecast_weather_code_IC",
        "IF": "$obs.label.forecast_weather_code_IF",
        "IP": "$obs.label.forecast_weather_code_IP",
        "K": "$obs.label.forecast_weather_code_K",
        "L": "$obs.label.forecast_weather_code_L",
        "R": "$obs.label.forecast_weather_code_R",
        "RW": "$obs.label.forecast_weather_code_RW",
        "RS": "$obs.label.forecast_weather_code_RS",
        "SI": "$obs.label.forecast_weather_code_SI",
        "WM": "$obs.label.forecast_weather_code_WM",
        "S": "$obs.label.forecast_weather_code_S",
        "SW": "$obs.label.forecast_weather_code_SW",
        "T": "$obs.label.forecast_weather_code_T",
        "UP": "$obs.label.forecast_weather_code_UP",
        "VA": "$obs.label.forecast_weather_code_VA",
        "WP": "$obs.label.forecast_weather_code_WP",
        "ZF": "$obs.label.forecast_weather_code_ZF",
        "ZL": "$obs.label.forecast_weather_code_ZL",
        "ZR": "$obs.label.forecast_weather_code_ZR",
        "ZY": "$obs.label.forecast_weather_code_ZY"
    }

    // Check if the weather_code is in the cloud_dict and use that if it's there. If not then it's a combined weather code.
    if ( cloud_dict.hasOwnProperty( weather_code ) ) {
        return cloud_dict[weather_code];
    } else {
        // Add the coverage if it's present, and full observation forecast is requested
        if ( ( coverage_code ) && ( full_observation ) ) {
            output += coverage_dict[coverage_code] + " ";
        }
        // Add the intensity if it's present
        if ( intensity_code ) {
            output += intensity_dict[intensity_code] + " ";
        }
        // Weather output
        output += weather_dict[weather_code];
    }

    return output;
}

function aeris_coded_alerts( data, full_observation = false ) {
    // https://www.aerisweather.com/support/docs/aeris-maps/reference/alert-types/

    var alert_dict = {
        "TOE": "$obs.label.forecast_alert_code_TOE",
        "ADR": "$obs.label.forecast_alert_code_ADR",
        "AQA": "$obs.label.forecast_alert_code_AQA",
        "AQ.S": "$obs.label.forecast_alert_code_AQ_S",
        "AS.Y": "$obs.label.forecast_alert_code_AS_Y",
        "AR.W": "$obs.label.forecast_alert_code_AR_W",
        "AF.Y": "$obs.label.forecast_alert_code_AF_Y",
        "MH.Y": "$obs.label.forecast_alert_code_MH_Y",
        "AF.W": "$obs.label.forecast_alert_code_AF_W",
        "AVW": "$obs.label.forecast_alert_code_AVW",
        "AVA": "$obs.label.forecast_alert_code_AVA",
        "BH.S": "$obs.label.forecast_alert_code_BH_S",
        "BZ.W": "$obs.label.forecast_alert_code_BZ_W",
        "DU.Y": "$obs.label.forecast_alert_code_DU_Y",
        "BS.Y": "$obs.label.forecast_alert_code_BS_Y",
        "BW.Y": "$obs.label.forecast_alert_code_BW_Y",
        "CAE": "$obs.label.forecast_alert_code_CAE",
        "CDW": "$obs.label.forecast_alert_code_CDW",
        "CEM": "$obs.label.forecast_alert_code_CEM",
        "CF.Y": "$obs.label.forecast_alert_code_CF_Y",
        "CF.S": "$obs.label.forecast_alert_code_CF_S",
        "CF.W": "$obs.label.forecast_alert_code_CF_W",
        "CF.A": "$obs.label.forecast_alert_code_CF_A",
        "FG.Y": "$obs.label.forecast_alert_code_FG_Y",
        "MF.Y": "$obs.label.forecast_alert_code_MF_Y",
        "SM.Y": "$obs.label.forecast_alert_code_SM_Y",
        "MS.Y": "$obs.label.forecast_alert_code_MS_Y",
        "DS.W": "$obs.label.forecast_alert_code_DS_W",
        "EQW": "$obs.label.forecast_alert_code_EQW",
        "EVI": "$obs.label.forecast_alert_code_EVI",
        "EH.W": "$obs.label.forecast_alert_code_EH_W",
        "EH.A": "$obs.label.forecast_alert_code_EH_A",
        "EC.W": "$obs.label.forecast_alert_code_EC_W",
        "EC.A": "$obs.label.forecast_alert_code_EC_A",
        "RFD": "$obs.label.forecast_alert_code_RFD",
        "EW.W": "$obs.label.forecast_alert_code_EW_W",
        "FRW": "$obs.label.forecast_alert_code_FRW",
        "FW.A": "$obs.label.forecast_alert_code_FW_A",
        "FF.S": "$obs.label.forecast_alert_code_FF_S",
        "FF.W": "$obs.label.forecast_alert_code_FF_W",
        "FF.A": "$obs.label.forecast_alert_code_FF_A",
        "FE.W": "$obs.label.forecast_alert_code_FE_W",
        "FL.Y": "$obs.label.forecast_alert_code_FL_Y",
        "FL.S": "$obs.label.forecast_alert_code_FL_S",
        "FL.W": "$obs.label.forecast_alert_code_FL_W",
        "FA.W": "$obs.label.forecast_alert_code_FA_W",
        "FL.A": "$obs.label.forecast_alert_code_FL_A",
        "FA.A": "$obs.label.forecast_alert_code_FA_A",
        "FZ.W": "$obs.label.forecast_alert_code_FZ_W",
        "FZ.A": "$obs.label.forecast_alert_code_FZ_A",
        "ZL.Y": "$obs.label.forecast_alert_code_ZL_Y",
        "ZF.Y": "$obs.label.forecast_alert_code_ZF_Y",
        "ZR.W": "$obs.label.forecast_alert_code_ZR_W",
        "UP.Y": "$obs.label.forecast_alert_code_UP_Y",
        "FR.Y": "$obs.label.forecast_alert_code_FR_Y",
        "GL.W": "$obs.label.forecast_alert_code_GL_W",
        "GL.A": "$obs.label.forecast_alert_code_GL_A",
        "HZ.W": "$obs.label.forecast_alert_code_HZ_W",
        "HZ.A": "$obs.label.forecast_alert_code_HZ_A",
        "HMW": "$obs.label.forecast_alert_code_HMW",
        "SE.W": "$obs.label.forecast_alert_code_SE_W",
        "SE.A": "$obs.label.forecast_alert_code_SE_A",
        "HWO": "$obs.label.forecast_alert_code_HWO",
        "HT.Y": "$obs.label.forecast_alert_code_HT_Y",
        "HT.W": "$obs.label.forecast_alert_code_HT_W",
        "UP.W": "$obs.label.forecast_alert_code_UP_W",
        "UP.A": "$obs.label.forecast_alert_code_UP_A",
        "SU.Y": "$obs.label.forecast_alert_code_SU_Y",
        "SU.W": "$obs.label.forecast_alert_code_SU_W",
        "HW.W": "$obs.label.forecast_alert_code_HW_W",
        "HW.A": "$obs.label.forecast_alert_code_HW_A",
        "HF.W": "$obs.label.forecast_alert_code_HF_W",
        "HF.A": "$obs.label.forecast_alert_code_HF_A",
        "HU.S": "$obs.label.forecast_alert_code_HU_S",
        "HU.W": "$obs.label.forecast_alert_code_HU_W",
        "HU.A": "$obs.label.forecast_alert_code_HU_A",
        "FA.Y": "$obs.label.forecast_alert_code_FA_Y",
        "IS.W": "$obs.label.forecast_alert_code_IS_W",
        "LE.W": "$obs.label.forecast_alert_code_LE_W",
        "LW.Y": "$obs.label.forecast_alert_code_LW_Y",
        "LS.Y": "$obs.label.forecast_alert_code_LS_Y",
        "LS.S": "$obs.label.forecast_alert_code_LS_S",
        "LS.W": "$obs.label.forecast_alert_code_LS_W",
        "LS.A": "$obs.label.forecast_alert_code_LS_A",
        "LEW": "$obs.label.forecast_alert_code_LEW",
        "LAE": "$obs.label.forecast_alert_code_LAE",
        "LO.Y": "$obs.label.forecast_alert_code_LO_Y",
        "MA.S": "$obs.label.forecast_alert_code_MA_S",
        "NUW": "$obs.label.forecast_alert_code_NUW",
        "RHW": "$obs.label.forecast_alert_code_RHW",
        "RA.W": "$obs.label.forecast_alert_code_RA_W",
        "FW.W": "$obs.label.forecast_alert_code_FW_W",
        "RFW": "$obs.label.forecast_alert_code_RFW",
        "RP.S": "$obs.label.forecast_alert_code_RP_S",
        "SV.W": "$obs.label.forecast_alert_code_SV_W",
        "SV.A": "$obs.label.forecast_alert_code_SV_A",
        "SV.S": "$obs.label.forecast_alert_code_SV_S",
        "TO.S": "$obs.label.forecast_alert_code_TO_S",
        "SPW": "$obs.label.forecast_alert_code_SPW",
        "NOW": "$obs.label.forecast_alert_code_NOW",
        "SC.Y": "$obs.label.forecast_alert_code_SC_Y",
        "SW.Y": "$obs.label.forecast_alert_code_SW_Y",
        "RB.Y": "$obs.label.forecast_alert_code_RB_Y",
        "SI.Y": "$obs.label.forecast_alert_code_SI_Y",
        "SO.W": "$obs.label.forecast_alert_code_SO_W",
        "SQ.W": "$obs.label.forecast_alert_code_SQ_W",
        "SQ.A": "$obs.label.forecast_alert_code_SQ_A",
        "SB.Y": "$obs.label.forecast_alert_code_SB_Y",
        "SN.W": "$obs.label.forecast_alert_code_SN_W",
        "MA.W": "$obs.label.forecast_alert_code_MA_W",
        "SPS": "$obs.label.forecast_alert_code_SPS",
        "SG.W": "$obs.label.forecast_alert_code_SG_W",
        "SS.W": "$obs.label.forecast_alert_code_SS_W",
        "SS.A": "$obs.label.forecast_alert_code_SS_A",
        "SR.W": "$obs.label.forecast_alert_code_SR_W",
        "SR.A": "$obs.label.forecast_alert_code_SR_A",
        "TO.W": "$obs.label.forecast_alert_code_TO_W",
        "TO.A": "$obs.label.forecast_alert_code_TO_A",
        "TC.S": "$obs.label.forecast_alert_code_TC_S",
        "TR.S": "$obs.label.forecast_alert_code_TR_S",
        "TR.W": "$obs.label.forecast_alert_code_TR_W",
        "TR.A": "$obs.label.forecast_alert_code_TR_A",
        "TS.Y": "$obs.label.forecast_alert_code_TS_Y",
        "TS.W": "$obs.label.forecast_alert_code_TS_W",
        "TS.A": "$obs.label.forecast_alert_code_TS_A",
        "TY.S": "$obs.label.forecast_alert_code_TY_S",
        "TY.W": "$obs.label.forecast_alert_code_TY_W",
        "TY.A": "$obs.label.forecast_alert_code_TY_A",
        "VOW": "$obs.label.forecast_alert_code_VOW",
        "WX.Y": "$obs.label.forecast_alert_code_WX_Y",
        "WX.W": "$obs.label.forecast_alert_code_WX_W",
        "WI.Y": "$obs.label.forecast_alert_code_WI_Y",
        "WC.Y": "$obs.label.forecast_alert_code_WC_Y",
        "WC.W": "$obs.label.forecast_alert_code_WC_W",
        "WC.A": "$obs.label.forecast_alert_code_WC_A",
        "WI.W": "$obs.label.forecast_alert_code_WI_W",
        "WS.W": "$obs.label.forecast_alert_code_WS_W",
        "WS.A": "$obs.label.forecast_alert_code_WS_A",
        "LE.A": "$obs.label.forecast_alert_code_LE_A",
        "BZ.A": "$obs.label.forecast_alert_code_BZ_A",
        "WW.Y": "$obs.label.forecast_alert_code_WW_Y",
        "LE.Y": "$obs.label.forecast_alert_code_LE_Y",
        "ZR.Y": "$obs.label.forecast_alert_code_ZR_Y",
        "AW.WI.MN": "$obs.label.forecast_alert_code_AW_WI_MN",
        "AW.WI.MD": "$obs.label.forecast_alert_code_AW_WI_MD",
        "AW.WI.SV": "$obs.label.forecast_alert_code_AW_WI_SV",
        "AW.WI.EX": "$obs.label.forecast_alert_code_AW_WI_EX",
        "AW.SI.MN": "$obs.label.forecast_alert_code_AW_SI_MN",
        "AW.SI.MD": "$obs.label.forecast_alert_code_AW_SI_MD",
        "AW.SI.SV": "$obs.label.forecast_alert_code_AW_SI_SV",
        "AW.SI.EX": "$obs.label.forecast_alert_code_AW_SI_EX",
        "AW.TS.MN": "$obs.label.forecast_alert_code_AW_TS_MN",
        "AW.TS.MD": "$obs.label.forecast_alert_code_AW_TS_MD",
        "AW.TS.SV": "$obs.label.forecast_alert_code_AW_TS_SV",
        "AW.TS.EX": "$obs.label.forecast_alert_code_AW_TS_EX",
        "AW.LI.MN": "$obs.label.forecast_alert_code_AW_LI_MN",
        "AW.LI.MD": "$obs.label.forecast_alert_code_AW_LI_MD",
        "AW.LI.SV": "$obs.label.forecast_alert_code_AW_LI_SV",
        "AW.LI.EX": "$obs.label.forecast_alert_code_AW_LI_EX",
        "AW.FG.MN": "$obs.label.forecast_alert_code_AW_FG_MN",
        "AW.FG.MD": "$obs.label.forecast_alert_code_AW_FG_MD",
        "AW.FG.SV": "$obs.label.forecast_alert_code_AW_FG_SV",
        "AW.FG.EX": "$obs.label.forecast_alert_code_AW_FG_EX",
        "AW.HT.MN": "$obs.label.forecast_alert_code_AW_HT_MN",
        "AW.HT.MD": "$obs.label.forecast_alert_code_AW_HT_MD",
        "AW.HT.SV": "$obs.label.forecast_alert_code_AW_HT_SV",
        "AW.HT.EX": "$obs.label.forecast_alert_code_AW_HT_EX",
        "AW.LT.MN": "$obs.label.forecast_alert_code_AW_LT_MN",
        "AW.LT.MD": "$obs.label.forecast_alert_code_AW_LT_MD",
        "AW.LT.SV": "$obs.label.forecast_alert_code_AW_LT_SV",
        "AW.LT.EX": "$obs.label.forecast_alert_code_AW_LT_EX",
        "AW.CE.MN": "$obs.label.forecast_alert_code_AW_CE_MN",
        "AW.CE.MD": "$obs.label.forecast_alert_code_AW_CE_MD",
        "AW.CE.SV": "$obs.label.forecast_alert_code_AW_CE_SV",
        "AW.CE.EX": "$obs.label.forecast_alert_code_AW_CE_EX",
        "AW.FR.MN": "$obs.label.forecast_alert_code_AW_FR_MN",
        "AW.FR.MD": "$obs.label.forecast_alert_code_AW_FR_MD",
        "AW.FR.SV": "$obs.label.forecast_alert_code_AW_FR_SV",
        "AW.FR.EX": "$obs.label.forecast_alert_code_AW_FR_EX",
        "AW.AV.MN": "$obs.label.forecast_alert_code_AW_AV_MN",
        "AW.AV.MD": "$obs.label.forecast_alert_code_AW_AV_MD",
        "AW.AV.SV": "$obs.label.forecast_alert_code_AW_AV_SV",
        "AW.AV.EX": "$obs.label.forecast_alert_code_AW_AV_EX",
        "AW.RA.MN": "$obs.label.forecast_alert_code_AW_RA_MN",
        "AW.RA.MD": "$obs.label.forecast_alert_code_AW_RA_MD",
        "AW.RA.SV": "$obs.label.forecast_alert_code_AW_RA_SV",
        "AW.RA.EX": "$obs.label.forecast_alert_code_AW_RA_EX",
        "AW.FL.MN": "$obs.label.forecast_alert_code_AW_FL_MN",
        "AW.FL.MD": "$obs.label.forecast_alert_code_AW_FL_MD",
        "AW.FL.SV": "$obs.label.forecast_alert_code_AW_FL_SV",
        "AW.FL.EX": "$obs.label.forecast_alert_code_AW_FL_EX",
        "AW.RF.MN": "$obs.label.forecast_alert_code_AW_RF_MN",
        "AW.RF.MD": "$obs.label.forecast_alert_code_AW_RF_MD",
        "AW.RF.SV": "$obs.label.forecast_alert_code_AW_RF_SV",
        "AW.RF.EX": "$obs.label.forecast_alert_code_AW_RF_EX",
        "AW.UK.MN": "$obs.label.forecast_alert_code_AW_UK_MN",
        "AW.UK.MD": "$obs.label.forecast_alert_code_AW_UK_MD",
        "AW.UK.SV": "$obs.label.forecast_alert_code_AW_UK_SV",
        "AW.UK.EX": "$obs.label.forecast_alert_code_AW_UK_EX"
    }

    return alert_dict[data];
}

function aeris_icon( data ) {
    // https://www.aerisweather.com/support/docs/api/reference/icon-list/
    icon_name = data.split(".")[0]; // Remove .png

    var icon_dict = {
        "blizzard": "snow",
        "blizzardn": "snow",
        "blowingsnow": "snow",
        "blowingsnown": "snow",
        "clear": "clear-day",
        "clearn": "clear-night",
        "cloudy": "cloudy",
        "cloudyn": "cloudy",
        "cloudyw": "cloudy",
        "cloudywn": "cloudy",
        "cold": "clear-day",
        "coldn": "clear-night",
        "drizzle": "rain",
        "drizzlen": "rain",
        "dust": "fog",
        "dustn": "fog",
        "fair": "mostly-clear-day",
        "fairn": "mostly-clear-night",
        "drizzlef": "rain",
        "fdrizzlen": "rain",
        "flurries": "sleet",
        "flurriesn": "sleet",
        "flurriesw": "sleet",
        "flurrieswn": "sleet",
        "fog": "fog",
        "fogn": "fog",
        "freezingrain": "rain",
        "freezingrainn": "rain",
        "hazy": "fog",
        "hazyn": "fog",
        "hot": "clear-day",
        "N/A ": "unknown",
        "mcloudy": "mostly-cloudy-day",
        "mcloudyn": "mostly-cloudy-night",
        "mcloudyr": "rain",
        "mcloudyrn": "rain",
        "mcloudyrw": "rain",
        "mcloudyrwn": "rain",
        "mcloudys": "snow",
        "mcloudysn": "snow",
        "mcloudysf": "snow",
        "mcloudysfn": "snow",
        "mcloudysfw": "snow",
        "mcloudysfwn": "snow",
        "mcloudysw": "mostly-cloudy-day",
        "mcloudyswn": "mostly-cloudy-night",
        "mcloudyt": "thunderstorm",
        "mcloudytn": "thunderstorm",
        "mcloudytw": "thunderstorm",
        "mcloudytwn": "thunderstorm",
        "mcloudyw": "mostly-cloudy-day",
        "mcloudywn": "mostly-cloudy-night",
        "na": "unknown",
        "na": "unknown",
        "pcloudy": "partly-cloudy-day",
        "pcloudyn": "partly-cloudy-night",
        "pcloudyr": "rain",
        "pcloudyrn": "rain",
        "pcloudyrw": "rain",
        "pcloudyrwn": "rain",
        "pcloudys": "snow",
        "pcloudysn": "snow",
        "pcloudysf": "snow",
        "pcloudysfn": "snow",
        "pcloudysfw": "snow",
        "pcloudysfwn": "snow",
        "pcloudysw": "partly-cloudy-day",
        "pcloudyswn": "partly-cloudy-night",
        "pcloudyt": "thunderstorm",
        "pcloudytn": "thunderstorm",
        "pcloudytw": "thunderstorm",
        "pcloudytwn": "thunderstorm",
        "pcloudyw": "partly-cloudy-day",
        "pcloudywn": "partly-cloudy-night",
        "rain": "rain",
        "rainn": "rain",
        "rainandsnow": "rain",
        "rainandsnown": "rain",
        "raintosnow": "rain",
        "raintosnown": "rain",
        "rainw": "rain",
        "rainw": "rain",
        "showers": "rain",
        "showersn": "rain",
        "showersw": "rain",
        "showersw": "rain",
        "sleet": "sleet",
        "sleetn": "sleet",
        "sleetsnow": "sleet",
        "sleetsnown": "sleet",
        "smoke": "fog",
        "smoken": "fog",
        "snow": "snow",
        "snown": "snow",
        "snoww": "snow",
        "snowwn": "snow",
        "snowshowers": "snow",
        "snowshowersn": "snow",
        "snowshowersw": "snow",
        "snowshowerswn": "snow",
        "snowtorain": "snow",
        "snowtorainn": "snow",
        "sunny": "clear-day",
        "sunnyn": "clear-night",
        "sunnyw": "mostly-clear-day",
        "sunnywn": "mostly-clear-night",
        "tstorm": "thunderstorm",
        "tstormn": "thunderstorm",
        "tstorms": "thunderstorm",
        "tstormsn": "thunderstorm",
        "tstormsw": "thunderstorm",
        "tstormswn": "thunderstorm",
        "wind": "wind",
        "wind": "wind",
        "wintrymix": "sleet",
        "wintrymixn": "sleet"
    }

    return icon_dict[icon_name];
}

function show_forcast_alert( data, aeris_provider ) {
    belchertown_debug("Forecast: Updating alert data for " + aeris_provider);
    var i, forecast_alert_modal, forecast_alerts;
    forecast_alert_modal = "";
    forecast_alerts = [];

    // Empty anything that's been appended to the modal from the previous run
    jQuery(".wx-stn-alert-text").empty();

    if ( aeris_provider == "aeris" ) {
        if ( data['alerts'][0]['response'][0] ) {
            for ( i = 0; i < data['alerts'][0]['response'].length; i++ ) {
                //forecast_alert_title = data['alerts'][0]['response'][i]['details']['name'];
                forecast_alert_title = aeris_coded_alerts( data['alerts'][0]['response'][i]['details']['type'] );
                forecast_alert_body = data['alerts'][0]['response'][i]['details']['body'].replace(/\n/g, '<br>');
                //forecast_alert_link = data['alerts'][0]['response'][i]['details']['name'];
                forecast_alert_link = data['alerts'][0]['response'][i]['details']['type'];
                forecast_alert_expires = moment.unix( data['alerts'][0]['response'][i]['timestamps']['expires'] ).utcOffset($moment_js_utc_offset).format( '$obs.label.time_forecast_alert_expires' );
                forecast_alerts.push( { "title": forecast_alert_title, "body": forecast_alert_body, "link": forecast_alert_link, "expires": forecast_alert_expires });
            }
        }
    }

    if ( forecast_alerts.length > 0 ) {
        belchertown_debug("Forecast: There are " + forecast_alerts.length + " alert(s).");
        for ( i = 0; i < forecast_alerts.length; i++ ) {

            alert_link = "<i class='fa fa-exclamation-triangle'></i> <a href='#forecast-alert-"+i+"' data-toggle='modal' data-target='#forecast-alert-"+i+"'>" +forecast_alerts[i]["title"] + " $obs.label.alert_in_effect " + forecast_alerts[i]["expires"] + "</a><br>";
            jQuery(".wx-stn-alert-text").append( alert_link );

            forecast_alert_modal += "<!-- Forecast Alert Modal "+i+" -->";
            forecast_alert_modal += "<div class='modal fade' id='forecast-alert-"+i+"' tabindex='-1' role='dialog' aria-labelledby='forecast-alert'>";
              forecast_alert_modal += "<div class='modal-dialog' role='document'>";
                forecast_alert_modal += "<div class='modal-content'>";
                  forecast_alert_modal += "<div class='modal-header'>";
                    forecast_alert_modal += "<button type='button' class='close' data-dismiss='modal' aria-label='Close'><span aria-hidden='true'>&times;</span></button>";
                    forecast_alert_modal += "<h4 class='modal-title' id='forecast-alert'>" + forecast_alerts[i]["title"] + "</h4>";
                  forecast_alert_modal += "</div>";
                  forecast_alert_modal += "<div class='modal-body'>";
                    forecast_alert_modal += forecast_alerts[i]["body"];
                  forecast_alert_modal += "</div>";
                  forecast_alert_modal += "<div class='modal-footer'>";
                    forecast_alert_modal += "<button type='button' class='btn btn-primary' data-dismiss='modal'>Close</button>";
                  forecast_alert_modal += "</div>";
                forecast_alert_modal += "</div>";
              forecast_alert_modal += "</div>";
            forecast_alert_modal += "</div>";

            jQuery(".wx-stn-alert-text").append( forecast_alert_modal );
        }
        jQuery(".wx-stn-alert").show();
    } else {
        belchertown_debug("Forecast: There are no forecast alerts");
        jQuery(".wx-stn-alert").hide();
    }
}

function update_forecast_data( data ) {
    aeris_provider = "$Extras.aeris_provider";
    belchertown_debug("Forecast: Provider is " + aeris_provider);
    belchertown_debug("Forecast: Updating data");

    forecast_row = [];

    if ( aeris_provider == "N/A" ) {
        jQuery(".forecastrow").hide();
        belchertown_debug("Forecast: No provider, hiding forecastrow");
        return;
    }

    if ( aeris_provider == "aeris" ) {
        var forecast_subtitle = moment.unix( data["timestamp"] ).utcOffset($moment_js_utc_offset).format( '$obs.label.time_forecast_last_updated' );

        try {
            belchertown_debug("Forecast: icon from Aeris data is " + data["current"][0]["response"]["ob"]["icon"] );
            var wxicon = get_relative_url() + "/images/" + aeris_icon( data["current"][0]["response"]["ob"]["icon"] ) + ".png";
            belchertown_debug("Forecast: Belchertown icon is " + wxicon);
            // Current observation text
            jQuery(".current-obs-text").html( aeris_coded_weather( data["current"][0]["response"]["ob"]["weatherPrimaryCoded"], true ) );

            // Visibility text in station observation table
            if ( ( "$Extras.forecast_units" == "si" ) || ( "$Extras.forecast_units" == "ca" ) ) {
                // si and ca = kilometer
                visibility = data["current"][0]["response"]["ob"]["visibilityKM"];
            } else {
                // us and uk2 and default = miles
                visibility = data["current"][0]["response"]["ob"]["visibilityMI"];
            }

            try {
                visibility_output = parseFloat(parseFloat( visibility )).toLocaleString("$system_locale_js", {minimumFractionDigits: unit_rounding_array["visibility"], maximumFractionDigits: unit_rounding_array["visibility"]}) + " " + unit_label_array["visibility"];

                jQuery(".station-observations .visibility").html( visibility_output );
            } catch(err) {
                // Visibility not in the station observation table or any of the unit arrays, so silently exit
            }
        } catch(err) {
            // Probably a non-metar current observation, which does not have visibility, icon, conditions, etc. So silently exit.
        }

        for (i = 0; i < data["forecast"][0]["response"][0]["periods"].length; i++) {
            var image_url = get_relative_url() + "/images/" + aeris_icon( data["forecast"][0]["response"][0]["periods"][i]["icon"] ) + ".png";
            var condition_text = aeris_coded_weather( data["forecast"][0]["response"][0]["periods"][i]["weatherPrimaryCoded"], false );
            var weekday = moment.unix( data["forecast"][0]["response"][0]["periods"][i]["timestamp"] + 7200 ).utcOffset($moment_js_utc_offset).format( "$obs.label.time_forecast_date" );

            // Determine temperature units
            if ( ( "$Extras.forecast_units" == "ca" ) || ( "$Extras.forecast_units" == "uk2" ) || ( "$Extras.forecast_units" == "si" ) ) {
                minTemp = data["forecast"][0]["response"][0]["periods"][i]["minTempC"];
                maxTemp = data["forecast"][0]["response"][0]["periods"][i]["maxTempC"];
            } else {
                // Default
                minTemp = data["forecast"][0]["response"][0]["periods"][i]["minTempF"];
                maxTemp = data["forecast"][0]["response"][0]["periods"][i]["maxTempF"];
            }

            // Determine wind units
            if ( "$Extras.forecast_units" == "ca" ) {
                // ca = kph
                windSpeed = data["forecast"][0]["response"][0]["periods"][i]["windSpeedKPH"];
                windGust = data["forecast"][0]["response"][0]["periods"][i]["windGustKPH"];
            } else if ( "$Extras.forecast_units" == "si" ) {
                // si = meters per second. MPS is KPH / 3.6
                windSpeed = data["forecast"][0]["response"][0]["periods"][i]["windSpeedKPH"] / 3.6;
                windGust = data["forecast"][0]["response"][0]["periods"][i]["windGustKPH"] / 3.6;
            } else {
                // us and uk2 and default = mph
                windSpeed = data["forecast"][0]["response"][0]["periods"][i]["windSpeedMPH"];
                windGust = data["forecast"][0]["response"][0]["periods"][i]["windGustMPH"];
            }

            if ( ( data["forecast"][0]["response"][0]["periods"][i]["snowCM"] > 0 ) || ( data["forecast"][0]["response"][0]["periods"][i]["snowIN"] > 0 ) ) {
                // Determine snow unit
                if ( ( "$Extras.forecast_units" == "si" ) || ( "$Extras.forecast_units" == "ca" ) || ( "$Extras.forecast_units" == "uk2" ) ) {
                    snow_depth = data["forecast"][0]["response"][0]["periods"][i]["snowCM"];
                    snow_unit = "cm";
                } else {
                    snow_depth = data["forecast"][0]["response"][0]["periods"][i]["snowIN"];
                    snow_unit = "in";
                }
            } else if ( data["forecast"][0]["response"][0]["periods"][i]["pop"] > 0 ) {
                // Rain percent of precip
                precip = data["forecast"][0]["response"][0]["periods"][i]["pop"];
            } else {
                precip = 0;
                snow_depth = 0;
                snow_unit = "";
            }

            var forecast_link_setup = "$Extras.forecast_daily_forecast_link".replace("YYYY", moment.unix( data["forecast"][0]["response"][0]["periods"][i]["timestamp"] + 7200 ).utcOffset($moment_js_utc_offset).format( "YYYY" )).replace("MM", moment.unix( data["forecast"][0]["response"][0]["periods"][i]["timestamp"] + 7200 ).utcOffset($moment_js_utc_offset).format( "MM" )).replace("DD", moment.unix( data["forecast"][0]["response"][0]["periods"][i]["timestamp"] + 7200 ).utcOffset($moment_js_utc_offset).format( "DD" ));
            var forecast_link = '<a href="'+forecast_link_setup+'" target="_blank">$obs.label.daily_forecast</a>';

            forecast_row.push( {
                    "weekday": weekday,
                    "image_url": image_url,
                    "condition_text": condition_text,
                    "minTemp": minTemp,
                    "maxTemp": maxTemp,
                    "windSpeed": windSpeed,
                    "windGust": windGust,
                    "snow_depth": snow_depth,
                    "snow_unit": snow_unit,
                    "precip": precip,
                    "forecast_link": forecast_link

            } );
        }
    }

    // WX icon in temperature box
    jQuery("#wxicon").attr( "src", wxicon );
    belchertown_debug("Forecast: Changing icon to " + wxicon);

    // Build daily forecast row
    var output_html = "";
    for (i = 0; i < forecast_row.length; i++) {
        if ( i == 0 ) {
            output_html += '<div class="col-sm-1-5 forecast-day forecast-today">';
        } else {
            output_html += '<div class="col-sm-1-5 forecast-day border-left">';
        }
        // Add 7200 (2 hours) to the epoch to get an hour well into the day to avoid any DST issues. This way it'll either be 1am or 2am. Without it, we get 12am or 11pm (the previous day).
        output_html += '<span id="weekday">'+forecast_row[i]["weekday"]+'</span>';
        output_html += '<br>';
        output_html += '<div class="forecast-conditions">';
        output_html += '<img id="icon" src="'+forecast_row[i]["image_url"]+'">';
        output_html += '<span class="forecast-condition-text">'+forecast_row[i]["condition_text"]+'</span>';
        output_html += '</div>';
        output_html += '<span class="forecast-high">'+ parseFloat( forecast_row[i]["maxTemp"] ).toFixed(0) +'&deg;</span> | <span class="forecast-low">'+ parseFloat( forecast_row[i]["minTemp"] ).toFixed(0) +'&deg;</span>';
        output_html += '<br>';
        output_html += '<div class="forecast-precip">';
        if ( forecast_row[i]["snow_depth"] > 0 ) {
            output_html += '<div class="snow-precip">';
            output_html += '<img src="'+get_relative_url()+'/images/snowflake-icon-15px.png"> <span>'+ parseFloat( forecast_row[i]["snow_depth"] ).toFixed(0) +'<span> ' + forecast_row[i]["snow_unit"];
            output_html += '</div>';
        } else if ( forecast_row[i]["precip"] > 0 ) {
            output_html += '<i class="wi wi-raindrop wi-rotate-45 rain-precip"></i> <span>'+ parseFloat( forecast_row[i]["precip"] ).toFixed(0) +'%</span>';
        } else {
            output_html += '<i class="wi wi-raindrop wi-rotate-45 rain-no-precip"></i> <span>0%</span>';
        }
        output_html += '</div>';
        output_html += '<div class="forecast-wind">';
        output_html += '<i class="wi wi-strong-wind"></i> <span>'+ parseFloat( forecast_row[i]["windSpeed"] ).toFixed(0) +'</span> | <span> '+ parseFloat( forecast_row[i]["windGust"] ).toFixed(0) +'$unit.label.windSpeed';
        output_html += '</div>';
        #if $Extras.has_key("forecast_show_daily_forecast_link") and $Extras.forecast_show_daily_forecast_link == '1'
        output_html += forecast_row[i]["forecast_link"];
        #end if
        output_html += '</div>';
    }

    // Show the forecast row
    jQuery(".forecast-subtitle").html( "$obs.label.forecast_last_updated " + forecast_subtitle );
    jQuery(".forecasts").html( output_html );

    #if $Extras.has_key("aeris_alert_enabled") and $Extras.aeris_alert_enabled == '1'
    // Show weather alert
    show_forcast_alert( data, aeris_provider );
    #end if

}
#end if



//## in index.html
//<script type="text/javascript">
//        #if $Extras.has_key("forecast_enabled") and $Extras.forecast_enabled == '1'
//        // Load forecast
//        ajaxforecast(); // Initial call to load forecast data like 8 day outlook, weather icon and observation text
//        #end if
//</script>


