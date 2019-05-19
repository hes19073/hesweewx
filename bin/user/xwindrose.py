# extended stats based on the xsearch example
# xwindrose.py  2016-06-13 18:15:24Z hes $

"""This search list extension offers extra tags:

windrose fpr steelgauges.
"""
import datetime
import time

from weewx.cheetahgenerator import SearchList
from weewx.tags import TimespanBinder
from weeutil.weeutil import TimeSpan
from weewx.units import ValueHelper

class windroseData(SearchList):

    def __init__(self, generator):
        SearchList.__init__(self, generator)

    def get_extension_list(self, timespan, db_lookup):
        """Returns a search list extension with windrose data for
           customclientraw.txt (steelseries gauges).
           This extension queries the last x hours of windSpeed/windDir
           records and generates a 16 element list containing the windrose
           data. The windrose timeframe can be set in skin.conf and defaults
           to 6 hours.

        Parameters:
          timespan: An instance of weeutil.weeutil.TimeSpan. This will
                    hold the start and stop times of the domain of
                    valid times.

          db_lookup: This is a function that, given a data binding
                     as its only parameter, will return a database manager
                     object.

        Returns:
          windroseData: A 16 element list containing the windrose data.
        """

        self.period = 21600    # 6 hours

        t1 = time.time()

        # Create windroseList container and initialise to all 0s
        windroseList=[0.0 for x in range(16)]
        # Get last x hours windSpeed obs as a ValueTuple. No need to
        # convert them as the steelseries code autoscales so untis are
        # meaningless.
        (time_start_vt, time_stop_vt, wind_speed_vt) = db_lookup().getSqlVectors(TimeSpan(timespan.stop - self.period, timespan.stop),
                                                                                 'windSpeed')
        # Get last x hours windDir obs as a ValueTuple. Again no need to
        # convert them as the steelseries code autoscales so untis are
        # meaningless.
        (time_start_vt, time_stop_vt, wind_dir_vt) = db_lookup().getSqlVectors(TimeSpan(timespan.stop - self.period, timespan.stop),
                                                                               'windDir')
        x = 0
        # Step through each windDir and add corresponding windSpeed to windroseList
        while x < len(wind_dir_vt[0]):
            # Only want to add windSpeed if both windSpeed and windDir have a vlaue
            if wind_speed_vt[0][x] != None and wind_dir_vt[0][x] != None:
                # Add the windSpeed value to the corresponding element of our windrose list
                windroseList[int((wind_dir_vt[0][x]+11.25)/22.5)%16] += wind_speed_vt[0][x]
            x += 1
        # Step through our windrose list and round all elements to
        # 1 decimal place
        y = 0
        while y < len(windroseList):
            windroseList[y] = round(windroseList[y],1)
            y += 1
        # Need to return a string of the list elements comma separated, no spaces and
        # bounded by [ and ]
        windroseData = '[' + ','.join(str(z) for z in windroseList) + ']'
        # Create a small dictionary with the tag names (keys) we want to use

        search_list_extension = {'windrosedata' : windroseData}

        return [search_list_extension]



