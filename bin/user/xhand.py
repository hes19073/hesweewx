# -*- coding: utf-8 -*-
#
# Portions Copyright 2014 Matthew Wall
# Portions taken from the pond.py example on the "add sensor" page
# on the weewx wiki, edited by Tom Keffer
#
# weewx service that reads data from a file as key value pairs and
# adds it to every loop packet
#
# This driver will read data from a file.  Each line of the file 
# for example:
# /home/weewx/archive/0verbrauch
#
# 50.323,32.2,109.4,75.887,009.8
# was   ,wasA,ele  ,gas   ,eleA
#
# The names must match the weewx database schema,
# but the schema can be extended for new fields
#
# Add this service to weewx.conf, then restart weewx
#[Engine]
#[[Services]]
#    data_services = ..., user.xhand.HandService
#
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.
#
# See http://www.gnu.org/licenses/

import syslog
import weewx
import weedb
import weewx.manager
import weeutil.weeutil

from weewx.wxengine import StdService

class HandService(StdService):
    def __init__(self, engine, config_dict):
        super(HandService, self).__init__(engine, config_dict)
        d = config_dict.get('HandService', {})
        self.filename = d.get('filename', '/home/weewx/archive/0verbrauch')
        syslog.syslog(syslog.LOG_INFO, "HandService: using %s" % self.filename)
        self.bind(weewx.NEW_ARCHIVE_RECORD, self.lese_file)


    def lese_file(self, event):
        try:
            with open(self.filename) as f:
                line = f.readline()
                values = line.split(',')

            event.record['wasZahl'] = float(values[0])
            event.record['wasAZahl'] = float(values[1])
            event.record['eleZahl'] = float(values[2])
            event.record['gasZahl'] = float(values[3])
            event.record['eleAZahl'] = float(values[4])

        except Exception as e:
            syslog.syslog(syslog.LOG_INFO, "HAND read failed: %s" % e)


