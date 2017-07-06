# Sonennstunden kalkulation
# 17.05.2015 Hes
"""weewx erweiterung sunshine """

import syslog
import ephem
from math import sin
from datetime import datetime

import weewx
from weewx.wxengine import StdService

class sunHoursClass(StdService):
   
    def __init__(self, engine, config_dict):

        super(sunHoursClass, self).__init__(engine, config_dict)
   
        self.bind(weewx.NEW_ARCHIVE_RECORD, self.newArchiveRecord)
           
    def newArchiveRecord(self, event):
        """Gets called on a new archive record event."""

        # Step 1 - Calculate Sun Elevation Angle as gS in radians

        loc = ephem.Observer()
        loc.lon = '11.341407'  # lon from station
        loc.lat = '53.605963'  # lat from station
        loc.pressure = 0
        loc.date = datetime.utcfromtimestamp(event.record.get('dateTime'))
        s = ephem.Sun()
        s.compute(loc)
        gS = s.alt

        # Step 2 - Calculate predicted solar radiation level as pR and record
       
        pR = 1373 * sin(gS) * 0.4
 
        # Step - 3 Calculate if any sunshine hours and record

        radiation = event.record.get('radiation')
        if radiation is not None and gS > 0.104719755 and radiation > pR:
            event.record['sunshinehours'] = event.record['interval'] / 60.0
            event.record['sunshineS'] = 300.0
        else:
            event.record['sunshinehours'] = 0.0
            event.record['sunshineS'] = 0.0

