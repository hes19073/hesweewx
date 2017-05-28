# -*- coding: utf-8 -*-
# $Id: dwd.py 1651 2017-03-26 18:10:37Z hes $
""" 
for now, tomorrow, day after tomorro
    ('hasel',      'VARCHAR(4)'),
    ('erle',       'VARCHAR(4)'),
    ('esche',      'VARCHAR(4)'),
    ('birke',      'VARCHAR(4)'),
    ('graeser',    'VARCHAR(4)'),
    ('roggen',     'VARCHAR(4)'),
    ('beifuss',    'VARCHAR(4)'),
    ('ambrosia',   'VARCHAR(4)'),
    ]


import json
import xmltodict
 
def convert(xml_file, xml_attribs=True):
    with open(xml_file, "rb") as f:    # notice the "rb" mode
        d = xmltodict.parse(f, xml_attribs=xml_attribs)
        return json.dumps(d, indent=4)

"""

# FIXME: waning by dwd-specific
# FIXME: health by dwd-specific

from __future__ import with_statement
import os
import platform
import re
import syslog
import time
import datetime
import dateutil.parser
import dateutil.tz
import dateutil.relativedelta
import xml.etree.cElementTree
import xml.etree.ElementTree as etree

import weewx
import weedb
import weewx.manager

import weeutil.weeutil
from weewx.engine import StdService
from weewx.cheetahgenerator import SearchList


DRIVER_VERSION = "0.16"

def logmsg(level, msg):
    syslog.syslog(level, 'DWD-Pollen: %s' % msg)

def logdbg(msg):
    logmsg(syslog.LOG_DEBUG, msg)

def loginf(msg):
    logmsg(syslog.LOG_INFO, msg)

def logerr(msg):
    logmsg(syslog.LOG_ERR, msg)

class DWDPollen(SearchList):
    
    def __init__(self, generator):
        SearchList.__init__(self, generator)

    def get_extension_list(self, timespan, db_lookup):

        filename = '/home/dwd/filelist/pollen0.xml'
            
        self.tz = dateutil.tz.gettz('Europe/Berlin')
        #fxp = xml.etree.cElementTree.fromstring(filexml)

        fxp = etree.parse(filename, etree.XMLParser(encoding='ISO-8859-1'))
        root = fxp.getroot()

        #loginf("DWD-XML-root: %s" % root)

        date = root.attrib['last_update'].split()[0].split('-')
        day0 = datetime.datetime(int(date[0]), int(date[1]), int(date[2]), 12, 0, 0, 0, tzinfo=self.tz)
        for reg in root.findall('region'):

            #loginf("DWD-XML nach ID : %s " % reg.attrib['ID'])
            #for preg in reg.findall('partregion'):
            if reg.attrib['ID'] == '20':

                hasel_h = reg.find("Hasel/today").text
                hasel_m = reg.find("Hasel/tomorrow").text 
                erle_h = reg.find("Erle/today").text
                erle_m = reg.find("Erle/tomorrow").text
                esche_h = reg.find("Esche/today").text
                esche_m = reg.find("Esche/tomorrow").text
                birke_h = reg.find("Birke/today").text
                birke_m = reg.find("Birke/tomorrow").text
                graeser_h = reg.find("Graeser/today").text
                graeser_m = reg.find("Graeser/tomorrow").text
                roggen_h = reg.find("Roggen/today").text
                roggen_m = reg.find("Roggen/tomorrow").text
                beifuss_h = reg.find("Beifuss/today").text
                beifuss_m = reg.find("Beifuss/tomorrow").text
                ambrosia_h = reg.find("Ambrosia/today").text
                ambrosia_m = reg.find("Ambrosia/tomorrow").text

                break

            #if reg.attrib['name'] == 'Mecklenburg-Vorpommern':
            #    break

        search_list_extension = {'Poll_akt'   : day0,
                                 'hasel_0'    : hasel_h,
                                 'hasel_1'    : hasel_m,
                                 'erle_0'     : erle_h, 
                                 'erle_1'     : erle_m, 
                                 'esche_0'    : esche_h, 
                                 'esche_1'    : esche_m, 
                                 'birke_0'    : birke_h, 
                                 'birke_1'    : birke_m, 
                                 'graeser_0'  : graeser_h, 
                                 'graeser_1'  : graeser_m, 
                                 'roggen_0'   : roggen_h, 
                                 'roggen_1'   : roggen_m,    
                                 'beifuss_0'  : beifuss_h, 
                                 'beifuss_1'  : beifuss_m,    
                                 'ambrosia_0' : ambrosia_h, 
                                 'ambrosia_1' : ambrosia_m}


        return [search_list_extension]
