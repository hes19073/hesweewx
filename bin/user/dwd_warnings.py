#!/usr/bin/python3
# Erzeugen von Warnmeldungen
# Copyright (C) 2021 Johanna Roedenbeck
# licensed under the terms of the General Public License (GPL) v3

import json
import time
import configobj

config = configobj.ConfigObj("/etc/weewx/weewx.conf")

if 'DeutscherWetterdienst' in config and 'warning' in config['DeutscherWetterdienst']:
    # Bundeslaender und Landkreise, fuer die Warndaten
    # bereitgestellt werden sollen, aus weewx.conf lesen
    if 'states' in config['DeutscherWetterdienst']['warning']:
        states = config['DeutscherWetterdienst']['warning']['states']
        if not isinstance(states,list):
            states=[states]
    else:
        states=[]
    counties=config['DeutscherWetterdienst']['warning']['counties']
    ICON_PTH=config['DeutscherWetterdienst']['warning']['icons']
    target_path=config['DeutscherWetterdienst']['path']
else:
    # test only
    # vom Benutzer anzupassen
    states=['Sachsen','Thüringen']
    counties={
        'Kreis Mittelsachsen - Tiefland':'DL',
        'Stadt Döbeln':'DL',
        'Stadt Leipzig':'L',
        'Stadt Jena':'J',
        'Stadt Dresden':'DD'}
    ICON_PTH="../dwd/warn_icons_50x50"
    target_path='/etc/weewx/skins/Belchertown-de/dwd'

# Der DWD verwendet ganz offensichtlich nicht die nach ISO genormten
# Abkuerzungen fuer Bundeslaender.
dwd_copy={
  'SN':'https://www.dwd.de/DE/wetter/warnungen_aktuell/warnlagebericht/sachsen/warnlage_sac_node.html',
  'TH':'https://www.dwd.de/DE/wetter/warnungen_aktuell/warnlagebericht/thueringen/warnlage_thu_node.html',
  'SA':'https://www.dwd.de/DE/wetter/warnungen_aktuell/warnlagebericht/sachen_anhalt/warnlage_saa_node.html',
  'BB':'https://www.dwd.de/DE/wetter/warnungen_aktuell/warnlagebericht/berlin_brandenburg/warnlage_bb_node.html',
  'MV':'https://www.dwd.de/DE/wetter/warnungen_aktuell/warnlagebericht/mecklenburg_vorpommern/warnlage_mv_node.html',
  'NS':'https://www.dwd.de/DE/wetter/warnungen_aktuell/warnlagebericht/niedersachsen_bremen/warnlage_nds_node.html'}

# Ende des vom Benutzer anzupassenden Bereichs

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
  
def dwd_warn_icon_file(type,level):
    if type==8 or type==9:
        return "warn_icons_%s.png" % dwd_warning_type[type]
    if level<2 or level>5: return None
    return "warn_icons_%s_%s.png" % (dwd_warning_type[type],level-1)

def dwd_level_text(level):
    try:
        return dwd_level[level]
    except IndexError:
        if level==10: return 'Hitzewarnung'
    return None

# read JSONP file and remove function call from it
__x=None
with open('%s/warnings.json' % target_path,encoding='utf-8') as file:
    __x=file.read().split('(',1)
    if __x[0]=="warnWetter.loadWarnings":
        __x=json.loads(__x[1][:-2])
        #for __i in __x:
        #    print(__i)

if __x is not None:

    # initialize dict for all regions to create warnings for
    wwarn={counties[i]:[] for i in counties}
    #print("wwarn %s" % wwarn)

    if True:
        try:
            ts=__x['time']
        except IndexError:
            ts=None
        try:
            wrn=__x['warnings']
        except IndexError:
            wrn=None
        try:
            vrb=__x['vorabInformation']
        except IndexError:
            vrb=None
        try:
            cpy=__x['copyright']
        except IndexError:
            cpy=None
        
        region={}
        for __i in wrn:
            for __j in wrn[__i]:
                if __j['state'] in states:
                    if __j['regionName'] not in region:
                        region[__j['regionName']]=__j
                if __j['regionName'] in counties:
                    if counties[__j['regionName']] not in wwarn:
                        wwarn[counties[__j['regionName']]]=[]
                    wwarn[counties[__j['regionName']]].append(__j)
                    
        #for __i in region:
        #    print("%s" % (__i,))

        #for __i in wwarn:
        #    print(__i)        

    for __ww in wwarn:
        s=""
        r=None
        for __i in wwarn[__ww]:
            if r is None or r!=__i['regionName']:
                r=__i['regionName']
                s+='<p style="margin-top:5px"><strong>%s</strong></p>\n' % r

            s+='<table style="vertical-align:middle"><tr style="vertical-align:middle">\n'
            __icon_fn=dwd_warn_icon_file(__i['type'],__i['level'])
            if __icon_fn is not None:
                s+='<td style="width:60px"><img src="%s/%s" /></td>\n' % (ICON_PTH,__icon_fn)
            __size=110 if int(__i['level'])>2 else 100
            s+='<td><p style="font-size:%i%%;margin-bottom:0">%s</p>\n' % (__size,__i['headline'])
            s='%s<p style="font-size:80%%">gültig vom %s bis %s</p></td>\n' % (s,time.strftime("%d.%m. %H:%M",time.localtime(__i['start']/1000)),time.strftime("%d.%m. %H:%M",time.localtime(__i['end']/1000)))
            s+='</tr></table>\n'

            if 'description' in __i and __i['description']:
                s+="<p>%s</p>\n" % __i['description']
            if 'instruction' in __i and __i['instruction']:
                s+="<p>%s</p>\n" % __i['instruction']
            
            s+='<p style="font-size:40%%">%s &ndash; %s &emsp;&ndash;&emsp; %s &ndash; %s</p>' % (__i['type'],__i['event'],__i['level'],dwd_level_text(__i['level']))
        
        if s:
            s+='<p style="font-size:80%%">Quelle: <a href="%s" target="_blank">DWD</a></p>\n' % dwd_copy[wwarn[__ww][0]['stateShort']]
        else:
            s='<p>zur Zeit keine Warnungen</p>'

        #print("--> %s" % __ww)
        #print(s)
        
        with open("%s/warn-%s.inc" % (target_path,__ww),"w") as file:
            file.write(s)
        
