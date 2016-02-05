# import time

import weewx
# import weewx.units
# import weeutil.weeutil
# import weeutil.Sun 
# from weewx.wxengine import StdService
from weewx.units import ValueHelper, getStandardUnitType
from weewx.cheetahgenerator import SearchList

# Define a dictionary to look up Davis forecast rule
# and return forecast text
davis_fr_dict= {
        0   : 'Mostly clear and cooler.',
        1   : 'Mostly clear with little temperature change.',
        2   : 'Mostly clear for 12 hours with little temperature change.',
        3   : 'Mostly clear for 12 to 24 hours and cooler.',
        4   : 'Mostly clear with little temperature change.',
        5   : 'Partly cloudy and cooler.',
        6   : 'Partly cloudy with little temperature change.',
        7   : 'Partly cloudy with little temperature change.',
        8   : 'Mostly clear and warmer.',
        9   : 'Partly cloudy with little temperature change.',
        10  : 'Partly cloudy with little temperature change.',
        11  : 'Mostly clear with little temperature change.',
        12  : 'Increasing clouds and warmer. Precipitation possible within 24 to 48 hours.',
        13  : 'Partly cloudy with little temperature change.',
        14  : 'Mostly clear with little temperature change.',
        15  : 'Increasing clouds with little temperature change. Precipitation possible within 24 hours.',
        16  : 'Mostly clear with little temperature change.',
        17  : 'Partly cloudy with little temperature change.',
        18  : 'Mostly clear with little temperature change.',
        19  : 'Increasing clouds with little temperature change. Precipitation possible within 12 hours.',
        20  : 'Mostly clear with little temperature change.',
        21  : 'Partly cloudy with little temperature change.',
        22  : 'Mostly clear with little temperature change.',
        23  : 'Increasing clouds and warmer. Precipitation possible within 24 hours.',
        24  : 'Mostly clear and warmer. Increasing winds.',
        25  : 'Partly cloudy with little temperature change.',
        26  : 'Mostly clear with little temperature change.',
        27  : 'Increasing clouds and warmer. Precipitation possible within 12 hours. Increasing winds.',
        28  : 'Mostly clear and warmer. Increasing winds.',
        29  : 'Increasing clouds and warmer.',
        30  : 'Partly cloudy with little temperature change.',
        31  : 'Mostly clear with little temperature change.',
        32  : 'Increasing clouds and warmer. Precipitation possible within 12 hours. Increasing winds.',
        33  : 'Mostly clear and warmer. Increasing winds.',
        34  : 'Increasing clouds and warmer.',
        35  : 'Partly cloudy with little temperature change.',
        36  : 'Mostly clear with little temperature change.',
        37  : 'Increasing clouds and warmer. Precipitation possible within 12 hours. Increasing winds.',
        38  : 'Partly cloudy with little temperature change.',
        39  : 'Mostly clear with little temperature change.',
        40  : 'Mostly clear and warmer. Precipitation possible within 48 hours.',
        41  : 'Mostly clear and warmer.',
        42  : 'Partly cloudy with little temperature change.',
        43  : 'Mostly clear with little temperature change.',
        44  : 'Increasing clouds with little temperature change. Precipitation possible within 24 to 48 hours.',
        45  : 'Increasing clouds with little temperature change.',
        46  : 'Partly cloudy with little temperature change.',
        47  : 'Mostly clear with little temperature change.',
        48  : 'Increasing clouds and warmer. Precipitation possible within 12 to 24 hours.',
        49  : 'Partly cloudy with little temperature change.',
        50  : 'Mostly clear with little temperature change.',
        51  : 'Increasing clouds and warmer. Precipitation possible within 12 to 24 hours. Windy.',
        52  : 'Partly cloudy with little temperature change.',
        53  : 'Mostly clear with little temperature change.',
        54  : 'Increasing clouds and warmer. Precipitation possible within 12 to 24 hours. Windy.',
        55  : 'Partly cloudy with little temperature change.',
        56  : 'Mostly clear with little temperature change.',
        57  : 'Increasing clouds and warmer. Precipitation possible within 6 to 12 hours.',
        58  : 'Partly cloudy with little temperature change.',
        59  : 'Mostly clear with little temperature change.',
        60  : 'Increasing clouds and warmer. Precipitation possible within 6 to 12 hours. Windy.',
        61  : 'Partly cloudy with little temperature change.',
        62  : 'Mostly clear with little temperature change.',
        63  : 'Increasing clouds and warmer. Precipitation possible within 12 to 24 hours. Windy.',
        64  : 'Partly cloudy with little temperature change.',
        65  : 'Mostly clear with little temperature change.',
        66  : 'Increasing clouds and warmer. Precipitation possible within 12 hours.',
        67  : 'Partly cloudy with little temperature change.',
        68  : 'Mostly clear with little temperature change.',
        69  : 'Increasing clouds and warmer. Precipitation likley.',
        70  : 'Clearing and cooler. Precipitation ending within 6 hours.',
        71  : 'Partly cloudy with little temperature change.',
        72  : 'Clearing and cooler. Precipitation ending within 6 hours.',
        73  : 'Mostly clear with little temperature change.',
        74  : 'Clearing and cooler. Precipitation ending within 6 hours.',
        75  : 'Partly cloudy and cooler.',
        76  : 'Partly cloudy with little temperature change.',
        77  : 'Mostly clear and cooler.',
        78  : 'Clearing and cooler. Precipitation ending within 6 hours.',
        79  : 'Mostly clear with little temperature change.',
        80  : 'Clearing and cooler. Precipitation ending within 6 hours.',
        81  : 'Mostly clear and cooler.',
        82  : 'Partly cloudy with little temperature change.',
        83  : 'Mostly clear with little temperature change.',
        84  : 'Increasing clouds with little temperature change. Precipitation possible within 24 hours.',
        85  : 'Mostly cloudy and cooler. Precipitation continuing.',
        86  : 'Partly cloudy with little temperature change.',
        87  : 'Mostly clear with little temperature change.',
        88  : 'Mostly cloudy and cooler. Precipitation likely.',
        89  : 'Mostly cloudy with little temperature change. Precipitation continuing.',
        90  : 'Mostly cloudy with little temperature change. Precipitation likely.',
        91  : 'Partly cloudy with little temperature change.',
        92  : 'Mostly clear with little temperature change.',
        93  : 'Increasing clouds and cooler. Precipitation possible and windy within 6 hours.',
        94  : 'Increasing clouds with little temperature change. Precipitation possible and windy within 6 hours.',
        95  : 'Mostly cloudy and cooler. Precipitation continuing. Increasing winds.',
        96  : 'Partly cloudy with little temperature change.',
        97  : 'Mostly clear with little temperature change.',
        98  : 'Mostly cloudy and cooler. Precipitation likely. Increasing winds.',
        99  : 'Mostly cloudy with little temperature change. Precipitation continuing. Increasing winds.',
        100 : 'Mostly cloudy with little temperature change. Precipitation likely. Increasing winds.',
        101 : 'Partly cloudy with little temperature change.',
        102 : 'Mostly clear with little temperature change.',
        103 : 'Increasing clouds and cooler. Precipitation possible within 12 to 24 hours possible wind shift to the W, NW, or N.',
        104 : 'Increasing clouds with little temperature change. Precipitation possible within 12 to 24 hours possible wind shift to the W, NW, or N.',
        105 : 'Partly cloudy with little temperature change.',
        106 : 'Mostly clear with little temperature change.',
        107 : 'Increasing clouds and cooler. Precipitation possible within 6 hours possible wind shift to the W, NW, or N.',
        108 : 'Increasing clouds with little temperature change. Precipitation possible within 6 hours possible wind shift to the W, NW, or N.',
        109 : 'Mostly cloudy and cooler. Precipitation ending within 12 hours possible wind shift to the W, NW, or N.',
        110 : 'Mostly cloudy and cooler. Possible wind shift to the W, NW, or N.',
        111 : 'Mostly cloudy with little temperature change. Precipitation ending within 12 hours possible wind shift to the W, NW, or N.',
        112 : 'Mostly cloudy with little temperature change. Possible wind shift to the W, NW, or N.',
        113 : 'Mostly cloudy and cooler. Precipitation ending within 12 hours possible wind shift to the W, NW, or N.',
        114 : 'Partly cloudy with little temperature change.',
        115 : 'Mostly clear with little temperature change.',
        116 : 'Mostly cloudy and cooler. Precipitation possible within 24 hours possible wind shift to the W, NW, or N.',
        117 : 'Mostly cloudy with little temperature change. Precipitation ending within 12 hours possible wind shift to the W, NW, or N.',
        118 : 'Mostly cloudy with little temperature change. Precipitation possible within 24 hours possible wind shift to the W, NW, or N.',
        119 : 'Clearing, cooler and windy. Precipitation ending within 6 hours.',
        120 : 'Clearing, cooler and windy.',
        121 : 'Mostly cloudy and cooler. Precipitation ending within 6 hours. Windy with possible wind shift to the W, NW, or N.',
        122 : 'Mostly cloudy and cooler. Windy with possible wind shift o the W, NW, or N.',
        123 : 'Clearing, cooler and windy.',
        124 : 'Partly cloudy with little temperature change.',
        125 : 'Mostly clear with little temperature change.',
        126 : 'Mostly cloudy with little temperature change. Precipitation possible within 12 hours. Windy.',
        127 : 'Partly cloudy with little temperature change.',
        128 : 'Mostly clear with little temperature change.',
        129 : 'Increasing clouds and cooler. Precipitation possible within 12 hours, possibly heavy at times. Windy.',
        130 : 'Mostly cloudy and cooler. Precipitation ending within 6 hours. Windy.',
        131 : 'Partly cloudy with little temperature change.',
        132 : 'Mostly clear with little temperature change.',
        133 : 'Mostly cloudy and cooler. Precipitation possible within 12 hours. Windy.',
        134 : 'Mostly cloudy and cooler. Precipitation ending in 12 to 24 hours.',
        135 : 'Mostly cloudy and cooler.',
        136 : 'Mostly cloudy and cooler. Precipitation continuing, possible heavy at times. Windy.',
        137 : 'Partly cloudy with little temperature change.',
        138 : 'Mostly clear with little temperature change.',
        139 : 'Mostly cloudy and cooler. Precipitation possible within 6 to 12 hours. Windy.',
        140 : 'Mostly cloudy with little temperature change. Precipitation continuing, possibly heavy at times. Windy.',
        141 : 'Partly cloudy with little temperature change.',
        142 : 'Mostly clear with little temperature change.',
        143 : 'Mostly cloudy with little temperature change. Precipitation possible within 6 to 12 hours. Windy.',
        144 : 'Partly cloudy with little temperature change.',
        145 : 'Mostly clear with little temperature change.',
        146 : 'Increasing clouds with little temperature change. Precipitation possible within 12 hours, possibly heavy at times. Windy.',
        147 : 'Mostly cloudy and cooler. Windy.',
        148 : 'Mostly cloudy and cooler. Precipitation continuing, possibly heavy at times. Windy.',
        149 : 'Partly cloudy with little temperature change.',
        150 : 'Mostly clear with little temperature change.',
        151 : 'Mostly cloudy and cooler. Precipitation likely, possibly heavy at times. Windy.',
        152 : 'Mostly cloudy with little temperature change. Precipitation continuing, possibly heavy at times. Windy.',
        153 : 'Mostly cloudy with little temperature change. Precipitation likely, possibly heavy at times. Windy.',
        154 : 'Partly cloudy with little temperature change.',
        155 : 'Mostly clear with little temperature change.',
        156 : 'Increasing clouds and cooler. Precipitation possible within 6 hours. Windy.',
        157 : 'Increasing clouds with little temperature change. Precipitation possible within 6 hours. Windy',
        158 : 'Increasing clouds and cooler. Precipitation continuing. Windy with possible wind shift to the W, NW, or N.',
        159 : 'Partly cloudy with little temperature change.',
        160 : 'Mostly clear with little temperature change.',
        161 : 'Mostly cloudy and cooler. Precipitation likely. Windy with possible wind shift to the W, NW, or N.',
        162 : 'Mostly cloudy with little temperature change. Precipitation continuing. Windy with possible wind shift to the W, NW, or N.',
        163 : 'Mostly cloudy with little temperature change. Precipitation likely. Windy with possible wind shift to the W, NW, or N.',
        164 : 'Increasing clouds and cooler. Precipitation possible within 6 hours. Windy with possible wind shift to the W, NW, or N.',
        165 : 'Partly cloudy with little temperature change.',
        166 : 'Mostly clear with little temperature change.',
        167 : 'Increasing clouds and cooler. Precipitation possible within 6 hours possible wind shift to the W, NW, or N.',
        168 : 'Increasing clouds with little temperature change. Precipitation possible within 6 hours. Windy with possible wind shift to the W, NW, or N.',
        169 : 'Increasing clouds with little temperature change. Precipitation possible within 6 hours possible wind shift to the W, NW, or N.',
        170 : 'Partly cloudy with little temperature change.',
        171 : 'Mostly clear with little temperature change.',
        172 : 'Increasing clouds and cooler. Precipitation possible within 6 hours. Windy with possible wind shift to the W, NW, or N.',
        173 : 'Increasing clouds with little temperature change. Precipitation possible within 6 hours. Windy with possible wind shift to the W, NW, or N.',
        174 : 'Partly cloudy with little temperature change.',
        175 : 'Mostly clear with little temperature change.',
        176 : 'Increasing clouds and cooler. Precipitation possible within 12 to 24 hours. Windy with possible wind shift to the W, NW, or N.',
        177 : 'Increasing clouds with little temperature change. Precipitation possible within 12 to 24 hours. Windy with possible wind shift to the W, NW, or N.',
        178 : 'Mostly cloudy and cooler. Precipitation possibly heavy at times and ending within 12 hours. Windy with possible wind shift to the W, NW, or N.',
        179 : 'Partly cloudy with little temperature change.',
        180 : 'Mostly clear with little temperature change.',
        181 : 'Mostly cloudy and cooler. Precipitation possible within 6 to 12 hours, possibly heavy at times. Windy with possible wind shift to the W, NW, or N.',
        182 : 'Mostly cloudy with little temperature change. Precipitation ending within 12 hours. Windy with possible wind shift to the W, NW, or N.',
        183 : 'Mostly cloudy with little temperature change. Precipitation possible within 6 to 12 hours, possibly heavy at times. Windy with possible wind shift to the W, NW, or N.',
        184 : 'Mostly cloudy and cooler. Precipitation continuing.',
        185 : 'Partly cloudy with little temperature change.',
        186 : 'Mostly clear with little temperature change.',
        187 : 'Mostly cloudy and cooler. Precipitation likely. Windy with possible wind shift to the W, NW, or N.',
        188 : 'Mostly cloudy with little temperature change. Precipitation continuing.',
        189 : 'Mostly cloudy with little temperature change. Precipitation likely.',
        190 : 'Partly cloudy with little temperature change.',
        191 : 'Mostly clear with little temperature change.',
        192 : 'Mostly cloudy and cooler. Precipitation possible within 12 hours, possibly heavy at times. Windy.',
        193 : 'FORECAST REQUIRES 3 HOURS OF RECENT DATA',
        194 : 'Mostly clear and cooler.',
        195 : 'Mostly clear and cooler.',
        196 : 'Mostly clear and cooler.'
        }

class wdConditionsTags(SearchList):
    """Return conditions, forecast and almanac info ."""

    def __init__(self, generator):
        """
        generator - the FileGenerator that uses this extension
        """
        
        SearchList.__init__(self, generator)
        # Get the 'WeewxWd' section of weewx.conf
        wcd = generator.config_dict.get('WeewxWd', {})
        db = generator._getArchive(wcd['wdConditions_database'])
        self.database = db
        self.table = wcd.get('table','archive')

    def get_extension(self, valid_timespan, archivedb, statsdb):
        """Returns various forecast, conditions and almanac tags. Utilises WU API calls
           and Davis Vantage console data.

        Parameters:
          valid_timespan: An instance of weeutil.weeutil.TimeSpan. This will
                          hold the start and stop times of the domain of
                          valid times.
          archivedb: An instance of weewx.archive.Archive

          statsdb:   An instance of weewx.stats.StatsDb

        Returns:
          forecastIcon:        Integer specifying the weather forecast
                               icon based on WU forecast API call. Integer has been
                               translated from WU icon name to Carter Lake icon number.
          forecastText:        WU forecast text (US units).
          forecastTextMetric:  WU forecast text using metric units..
          currentIcon:         Integer specifying the current conditions
                               icon based on WU conditions API call. Integer has been
                               translated from WU icon name to Carter Lake icon number.
          currentText:         WU current condityions summary text.
          tempRecordHigh:      Record high temperature from WU API almanac data. Data 
                               returned is a ValueHelper so normal Weewx dot code
                               formatting/coverting is available.
          tempNormalHigh:      Normal high temperature from WU API almanac data. Data 
                               returned is a ValueHelper so normal Weewx dot code
                               formatting/coverting is available.
          tempRecordHighYear:  Year of record high temperature from WU API almanac data. (YYYY)
          tempRecordLow:       Record low temperature from WU API almanac data. Data 
                               returned is a ValueHelper so normal Weewx dot code
                               formatting/coverting is available.
          tempNormalLow:       Normal low temperature from WU API almanac data. Data 
                               returned is a ValueHelper so normal Weewx dot code
                               formatting/coverting is available.
          tempRecordLowYear:   Year of record high temperature from WU API almanac data.  (YYYY)
                               formatting/coverting is available.
          vantageForecastIcon: Integer specify weather forecast icon from Davis Vantage console.
                               No translation has been done, icon can be decoded as per Davis
                               documentation.
          vantageForecastRule: Forecast text from Davis Vantage console. Forecast rule number has
                               been translated to text as per Davis documentation (refer
                               davis_fr_dict dictionary above).
        """
        
        # As wdWU thread may still be running use last known good record from
        # database rather that record with dateTime 'valid_timespan.stop'
        _ts = self.database.lastGoodStamp()
        _current_rec = self.database.getRecord(_ts)
        # Get our temp units and group
        (_tempUnit, _tempGroup) = getStandardUnitType(_current_rec['usUnits'], 'outTemp')
        # Get our data
        forecastIcon = _current_rec['forecastIcon']
        forecastText = _current_rec['forecastText']
        forecastTextMetric = _current_rec['forecastTextMetric']
        currentIcon = _current_rec['currentIcon']
        currentText = _current_rec['currentText']
        tempRecordHigh = _current_rec['tempRecordHigh']
        tempNormalHigh = _current_rec['tempNormalHigh']
        tempRecordHighYear = _current_rec['tempRecordHighYear']
        tempRecordLow = _current_rec['tempRecordLow']
        tempNormalLow = _current_rec['tempNormalLow']
        tempRecordLowYear = _current_rec['tempNormalLowYear']
        vantageForecastIcon = _current_rec['vantageForecastIcon']
        vantageForecastRule = _current_rec['vantageForecastRule']
        # Convert our temps to ValueTuples
        tempRecordHigh_vt = (_current_rec['tempRecordHigh'], _tempUnit, _tempGroup)
        tempNormalHigh_vt = (_current_rec['tempNormalHigh'], _tempUnit, _tempGroup)
        tempRecordLow_vt = (_current_rec['tempRecordLow'], _tempUnit, _tempGroup)
        tempNormalLow_vt = (_current_rec['tempNormalLow'], _tempUnit, _tempGroup)
        # Get our temps as ValueHelpers
        tempRecordHigh_vh = ValueHelper(tempRecordHigh_vt, formatter=self.generator.formatter, converter=self.generator.converter)
        tempNormalHigh_vh = ValueHelper(tempNormalHigh_vt, formatter=self.generator.formatter, converter=self.generator.converter)
        tempRecordLow_vh = ValueHelper(tempRecordLow_vt, formatter=self.generator.formatter, converter=self.generator.converter)
        tempNormalLow_vh = ValueHelper(tempNormalLow_vt, formatter=self.generator.formatter, converter=self.generator.converter)
        # Put our results into a small dictionary
        search_list_extension = {'forecastIcon'         : forecastIcon,
                                 'forecastText'         : forecastText,
                                 'forecastTextMetric'   : forecastTextMetric,
                                 'currentIcon'          : currentIcon,
                                 'currentText'          : currentText,
                                 'tempRecordHigh'       : tempRecordHigh_vh,
                                 'tempNormalHigh'       : tempNormalHigh_vh,
                                 'tempRecordHighYear'   : tempRecordHighYear,
                                 'tempRecordLow'        : tempRecordLow_vh,
                                 'tempNormalLow'        : tempNormalLow_vh,
                                 'tempRecordLowYear'    : tempRecordLowYear,
                                 'vantageForecastIcon'  : vantageForecastIcon,
                                 'vantageForecastRule'  : davis_fr_dict[int(vantageForecastRule)]}

        return search_list_extension

