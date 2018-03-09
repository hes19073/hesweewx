# -*- coding: utf-8 -*-
# $Id: xvaporpressure.py  2017-12-28 11:45:37 hes $
# Copyright 2017 Hartmut Schweidler
# original by tom keffer
# Dampfdichte innen und aussen kalkulation
# saettigungsdampfdichte innen und aussen
"""weewx erweiterung vaporpressure """

import syslog
import weewx.engine
import weewx.units
import weewx.uwxutils

import weewx
from weewx.wxengine import StdService

class VaporPressure(StdService):

    def __init__(self, engine, config_dict):

        super(VaporPressure, self).__init__(engine, config_dict)

        self.bind(weewx.NEW_ARCHIVE_RECORD, self.addVP)

    def addVP(self, event):
        """Gets called on a new archive record event."""
        """Add vapor pressure to a record"""
        # Convert the record to Metric units:
        #recordM = weewx.units.to_METRICWX(event.record) only by US units
        recordM = event.record
        if recordM['outTemp'] is not None and recordM['outHumidity'] is not None:

            event.record['SVP'] = weewx.uwxutils.TWxUtils.SaturationVaporPressure(recordM['outTemp'])
            event.record['AVP'] = record['outHumidity'] * event.record['SVP'] / 100.0

        if recordM['inTemp'] is not None and recordM['inHumidity'] is not None:
            event.record['SVPin'] = weewx.uwxutils.TWxUtils.SaturationVaporPressure(recordM['inTemp'])
            event.record['AVPin'] = recordM['inHumidity'] * event.record['SVPin'] / 100.0

