#
#    Copyright (c) 2011 Tom Keffer <tkeffer@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#
#    $Id: extensions.py 2749 2014-11-29 18:15:24Z tkeffer $
#

"""User extensions module

This module is imported from the main executable, so anything put here will be
executed before anything else happens. This makes it a good place to put user
extensions.
"""

import locale
# This will use the locale specified by the environment variable 'LANG'
# Other options are possible. See:
# http://docs.python.org/2/library/locale.html#locale.setlocale
locale.setlocale(locale.LC_ALL, '')
#locale.setlocale(locale.LC_ALL, 'de_DE')


# setup units to support custom Klimalogg sensor map
from weewx.units import obs_group_dict

obs_group_dict['next_date'] = 'group_time'
obs_group_dict['up_date'] = 'group_time'
obs_group_dict['earthquake_time'] = 'group_time'
obs_group_dict['current_temp'] = 'group_temperature'
obs_group_dict['current_apptemp'] = 'group_temperature'
obs_group_dict['current_wind'] = 'group_speed'
obs_group_dict['densityA'] = 'group_altitude'
obs_group_dict['altiAir'] = 'group_altitude'
obs_group_dict['tempAir'] = 'group_temperature'
obs_group_dict['tem_A'] = 'group_temperature'
obs_group_dict['temp0'] = 'group_temperature'
obs_group_dict['temp1'] = 'group_temperature'
obs_group_dict['temp2'] = 'group_temperature'
obs_group_dict['temp3'] = 'group_temperature'
obs_group_dict['temp4'] = 'group_temperature'
obs_group_dict['temp5'] = 'group_temperature'
obs_group_dict['temp6'] = 'group_temperature'
obs_group_dict['temp7'] = 'group_temperature'
obs_group_dict['temp8'] = 'group_temperature'
obs_group_dict['humidity0'] = 'group_percent'
obs_group_dict['humidity1'] = 'group_percent'
obs_group_dict['humidity2'] = 'group_percent'
obs_group_dict['humidity3'] = 'group_percent'
obs_group_dict['humidity4'] = 'group_percent'
obs_group_dict['humidity5'] = 'group_percent'
obs_group_dict['humidity6'] = 'group_percent'
obs_group_dict['humidity7'] = 'group_percent'
obs_group_dict['humidity8'] = 'group_percent'
obs_group_dict['dewpoint0'] = 'group_temperature'
obs_group_dict['dewpoint1'] = 'group_temperature'
obs_group_dict['dewpoint2'] = 'group_temperature'
obs_group_dict['dewpoint3'] = 'group_temperature'
obs_group_dict['dewpoint4'] = 'group_temperature'
obs_group_dict['dewpoint5'] = 'group_temperature'
obs_group_dict['dewpoint6'] = 'group_temperature'
obs_group_dict['dewpoint7'] = 'group_temperature'
obs_group_dict['dewpoint8'] = 'group_temperature'
obs_group_dict['heatindex0'] = 'group_temperature'
obs_group_dict['heatindex1'] = 'group_temperature'
obs_group_dict['heatindex2'] = 'group_temperature'
obs_group_dict['heatindex3'] = 'group_temperature'
obs_group_dict['heatindex4'] = 'group_temperature'
obs_group_dict['heatindex5'] = 'group_temperature'
obs_group_dict['heatindex6'] = 'group_temperature'
obs_group_dict['heatindex7'] = 'group_temperature'
obs_group_dict['heatindex8'] = 'group_temperature'
obs_group_dict['rxCheckPercent'] = 'group_percent'
obs_group_dict['batteryStatus0'] = 'group_count'
obs_group_dict['batteryStatus1'] = 'group_count'
obs_group_dict['batteryStatus2'] = 'group_count'
obs_group_dict['batteryStatus3'] = 'group_count'
obs_group_dict['batteryStatus4'] = 'group_count'
obs_group_dict['batteryStatus5'] = 'group_count'
obs_group_dict['batteryStatus6'] = 'group_count'
obs_group_dict['batteryStatus7'] = 'group_count'
obs_group_dict['batteryStatus8'] = 'group_count'
obs_group_dict['absolutF0'] = 'group_gram'
obs_group_dict['absolutF1'] = 'group_gram'
obs_group_dict['absolutF2'] = 'group_gram'
obs_group_dict['absolutF3'] = 'group_gram'
obs_group_dict['absolutF4'] = 'group_gram'
obs_group_dict['absolutF5'] = 'group_gram'
obs_group_dict['absolutF6'] = 'group_gram'
obs_group_dict['absolutF7'] = 'group_gram'
obs_group_dict['absolutF8'] = 'group_gram'
obs_group_dict['SVD'] = 'group_pressure'
obs_group_dict['SVDin'] = 'group_pressure'
obs_group_dict['SVD0'] = 'group_pressure'
obs_group_dict['SVD1'] = 'group_pressure'
obs_group_dict['SVD2'] = 'group_pressure'
obs_group_dict['SVD3'] = 'group_pressure'
obs_group_dict['SVD4'] = 'group_pressure'
obs_group_dict['SVD5'] = 'group_pressure'
obs_group_dict['SVD6'] = 'group_pressure'
obs_group_dict['SVD7'] = 'group_pressure'
obs_group_dict['SVD8'] = 'group_pressure'
obs_group_dict['slp_A'] = 'group_pressure'
obs_group_dict['AVD'] = 'group_gram'
obs_group_dict['AVDin'] = 'group_gram'
obs_group_dict['AVD0'] = 'group_gram'
obs_group_dict['AVD1'] = 'group_gram'
obs_group_dict['AVD2'] = 'group_gram'
obs_group_dict['AVD3'] = 'group_gram'
obs_group_dict['AVD4'] = 'group_gram'
obs_group_dict['AVD5'] = 'group_gram'
obs_group_dict['AVD6'] = 'group_gram'
obs_group_dict['AVD7'] = 'group_gram'
obs_group_dict['AVD8'] = 'group_gram'
obs_group_dict['eleTotal'] = 'group_count'
obs_group_dict['eleZahl'] = 'group_count'
obs_group_dict['eleATotal'] = 'group_count'
obs_group_dict['eleAZahl'] = 'group_count'
obs_group_dict['gasTotal'] = 'group_count'
obs_group_dict['gasZahl'] = 'group_count'
obs_group_dict['wasTotal'] = 'group_count'
obs_group_dict['wasZahl'] = 'group_count'
obs_group_dict['wasATotal'] = 'group_count'
obs_group_dict['wasAZahl'] = 'group_count'
obs_group_dict['wasA'] = 'group_anzahl'
obs_group_dict['eleA'] = 'group_anzahl'
obs_group_dict['was'] = 'group_anzahl'
obs_group_dict['ele'] = 'group_anzahl'
obs_group_dict['gas'] = 'group_anzahl'

