# coding=utf-8

"""weewx module that records cpm and nSvh from GMC 300.

Put this file in the bin/user directory.

Service Configuration """

import logging
import weewx
import weedb
import weewx.manager
import weeutil.weeutil

from weewx.wxengine import StdService

log = logging.getLogger(__name__)

class HausEG(StdService):
    def __init__(self, engine, config_dict):
        super(HausEG, self).__init__(engine, config_dict)
        d = config_dict.get('HausEG', {})
        self.filename = d.get('filename', '/var/tmp/hauseg.txt')
        log.info("DataHausEG: using %s", self.filename)
        self.bind(weewx.NEW_ARCHIVE_RECORD, self.read_file)

    def read_file(self, event):
        try:
            with open(self.filename) as f:
                #value = f.read()
                line = f.readline()
                values = line.split(',')

            #log.debug("HausEG: found value of %s", values)

            event.record['ele'] = float(values[1])
            event.record['eleA'] = float(values[2])
            event.record['extraTemp1'] = float(values[3])
            event.record['extraTemp2'] = float(values[9])
            event.record['extraTemp3'] = float(values[10])
            event.record['extraTemp4'] = float(values[11])
            event.record['extraTemp5'] = float(values[12])
            event.record['extraTemp6'] = float(values[13])
            event.record['extraTemp7'] = float(values[14])
            event.record['extraTemp8'] = float(values[15])
            event.record['extraTemp9'] = float(values[16])
            event.record['extraTemp10'] = float(values[4])
            event.record['extraTemp11'] = float(values[5])
            event.record['extraTemp12'] = float(values[6])
            event.record['extraTemp13'] = float(values[7])
            event.record['extraTemp14'] = float(values[8])
            event.record['gas'] = float(values[17])
            event.record['was'] = float(values[19])
            event.record['wasA'] = float(values[20])

        except Exception as e:
            log.error("HausEG: cannot read value: %s", e)

