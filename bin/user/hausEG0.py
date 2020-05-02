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
            with open('/home/weewx/archive/0ZahlStand') as f:
                line = f.readline()
                values = line.split(',')

            last_was = float(values[0])
            last_waa = float(values[1])
            last_ele = float(values[2])
            last_gas = float(values[3])
            last_ela = float(values[4])

            f.close()

        except Exception as e:
            log.error("Daten: cannot read Date: %s", e)

        try:
            with open(self.filename) as f:
                #value = f.read()
                line = f.readline()
                values = line.split(',')

            log.debug("HausEG: found value of %s" % values)

            event.record['ele'] = float(values[1])
            event.record['eleA'] = float(values[2])
            event.record['extraTemp1'] = float(values[3])
            event.record['extraTemp10'] = float(values[4])
            event.record['extraTemp11'] = float(values[5])
            event.record['extraTemp12'] = float(values[6])
            event.record['extraTemp13'] = float(values[7])
            event.record['extraTemp14'] = float(values[8])
            event.record['extraTemp2'] = float(values[9])
            event.record['extraTemp3'] = float(values[10])
            event.record['extraTemp4'] = float(values[11])
            event.record['extraTemp5'] = float(values[12])
            event.record['extraTemp6'] = float(values[13])
            event.record['extraTemp7'] = float(values[14])
            event.record['extraTemp8'] = float(values[15])
            event.record['extraTemp9'] = float(values[16])
            event.record['gas'] = float(values[17])
            event.record['was'] = float(values[19])
            event.record['wasA'] = float(values[20])

            was_val = float(values[19])
            event.record['wasTotal'] = calculate_delta(was_val, last_was)
            was_new = event.record['was']

            wasA_val = float(values[20])
            event.record['wasATotal'] = calculate_delta(wasA_val, last_waa)
            waa_new = event.record['wasA']

            ele_val = float(values[1])
            event.record['eleTotal'] = calculate_delta(ele_val, last_ele)
            ele_new = event.record['ele']

            gas_val = float(values[17])
            event.record['gasTotal'] = calculate_delta(gas_val, last_gas)
            gas_new = event.record['gas']

            eleA_val = float(values[2])
            event.record['eleATotal'] = calculate_delta(eleA_val, last_ela)
            ela_new = event.record['eleA']

            f.close()

            dat_A = open("/home/weewx/archive/0ZahlStand", "w")
            data_new = str(was_val) + "," + str(wasA_val) + "," + str(ele_val) + "," + str(gas_val) + "," + str(eleA_val)
            dat_A.write(data_new)
            dat_A.close()

        except Exception as e:
            log.error("HausEG: cannot read value: %s" % e)

def calculate_delta(newtotal, oldtotal):
    """Calculate differential given two cumulative measurements."""
    if newtotal is not None and oldtotal is not None:
        if newtotal >= oldtotal:
            delta = newtotal - oldtotal
        else:
            log.info("Hand: counter reset detected: new=%s old=%s", newtotal, oldtotal)
            delta = 0.0
    else:
        delta = 0.0

    return delta
