# coding=utf-8
# vantag forecast text
# ist der String zur Anzeige

from __future__ import absolute_import

import datetime
import logging

from weewx.cheetahgenerator import SearchList
from weewx.tags import TimespanBinder
from weeutil.weeutil import TimeSpan

log = logging.getLogger(__name__)

# Define a dictionary to look up Davis forecast rule
# and return forecast text
davis_fr_dict= {
    '0' : 'Meist heiter und kälter.',
    '1' : 'Meist heiter mit geringer Temperaturänderung.',
    '2' : 'Meist heiter für 12 Stunden mit geringer Temperaturänderung.',
    '3' : 'Meist heiter für 12 bis 24 Stunden und kälter.',
    '4' : 'Meist heiter mit geringer Temperaturänderung.',
    '5' : 'Teils wolkig und kälter.',
    '6' : 'Teils wolkig mit geringer Temperaturänderung.',
    '7' : 'Teils wolkig mit geringer Temperaturänderung.',
    '8' : 'Meist heiter und wärmer.',
    '9' : 'Teils wolkig mit geringer Temperaturänderung.',
    '10' : 'Teils wolkig mit geringer Temperaturänderung.',
    '11' : 'Meist heiter mit geringer Temperaturänderung.',
    '12' : 'Zunehmend bewölkt und wärmer. Niederschlag möglich innerhalb 24 bis 48 Stunden.',
    '13' : 'Teils wolkig mit geringer Temperaturänderung.',
    '14' : 'Meist heiter mit geringer Temperaturänderung.',
    '15' : 'Zunehmend bewölkt mit geringer Temperaturänderung. Niederschlag möglich innerhalb 24 Stunden.',
    '16' : 'Meist heiter mit geringer Temperaturänderung.',
    '17' : 'Teils wolkig mit geringer Temperaturänderung.',
    '18' : 'Meist heiter mit geringer Temperaturänderung.',
    '19' : 'Zunehmend bewölkt mit geringer Temperaturänderung. Niederschlag möglich innerhalb 12 Stunden.',
    '20' : 'Meist heiter mit geringer Temperaturänderung.',
    '21' : 'Teils wolkig mit geringer Temperaturänderung.',
    '22' : 'Meist heiter mit geringer Temperaturänderung.',
    '23' : 'Zunehmend bewölkt und wärmer. Niederschlag möglich innerhalb 24 Stunden.',
    '24' : 'Meist heiter und wärmer. Zunehmender Wind.',
    '25' : 'Teils wolkig mit geringer Temperaturänderung.',
    '26' : 'Meist heiter mit geringer Temperaturänderung.',
    '27' : 'Zunehmend bewölkt und wärmer. Niederschlag möglich innerhalb 12 Stunden. Zunehmender Wind.',
    '28' : 'Meist heiter und wärmer. Zunehmender Wind.',
    '29' : 'Zunehmend bewölkt und wärmer.',
    '30' : 'Teils wolkig mit geringer Temperaturänderung.',
    '31' : 'Meist heiter mit geringer Temperaturänderung.',
    '32' : 'Zunehmend bewölkt und wärmer. Niederschlag möglich innerhalb 12 Stunden. Zunehmender Wind.',
    '33' : 'Meist heiter und wärmer. Zunehmender Wind.',
    '34' : 'Zunehmend bewölkt und wärmer.',
    '35' : 'Teils wolkig mit geringer Temperaturänderung.',
    '36' : 'Meist heiter mit geringer Temperaturänderung.',
    '37' : 'Zunehmend bewölkt und wärmer. Niederschlag möglich innerhalb 12 Stunden. Zunehmender Wind.',
    '38' : 'Teils wolkig mit geringer Temperaturänderung.',
    '39' : 'Meist heiter mit geringer Temperaturänderung.',
    '40' : 'Meist heiter und wärmer. Niederschlag möglich innerhalb 48 Stunden.',
    '41' : 'Meist heiter und wärmer.',
    '42' : 'Teils wolkig mit geringer Temperaturänderung.',
    '43' : 'Meist heiter mit geringer Temperaturänderung.',
    '44' : 'Zunehmend bewölkt mit geringer Temperaturänderung. Niederschlag möglich innerhalb 24 bis 48 Stunden.',
    '45' : 'Zunehmend bewölkt mit geringer Temperaturänderung.',
    '46' : 'Teils wolkig mit geringer Temperaturänderung.',
    '47' : 'Meist heiter mit geringer Temperaturänderung.',
    '48' : 'Zunehmend bewölkt und wärmer. Niederschlag möglich innerhalb 12 bis 24 Stunden.',
    '49' : 'Teils wolkig mit geringer Temperaturänderung.',
    '50' : 'Meist heiter mit geringer Temperaturänderung.',
    '51' : 'Zunehmend bewölkt und wärmer. Niederschlag möglich innerhalb 12 bis 24 Stunden. Windig.',
    '52' : 'Teils wolkig mit geringer Temperaturänderung.',
    '53' : 'Meist heiter mit geringer Temperaturänderung.',
    '54' : 'Zunehmend bewölkt und wärmer. Niederschlag möglich innerhalb 12 bis 24 Stunden. Windig.',
    '55' : 'Teils wolkig mit geringer Temperaturänderung.',
    '56' : 'Meist heiter mit geringer Temperaturänderung.',
    '57' : 'Zunehmend bewölkt und wärmer. Niederschlag möglich innerhalb 6 bis 12 Stunden.',
    '58' : 'Teils wolkig mit geringer Temperaturänderung.',
    '59' : 'Meist heiter mit geringer Temperaturänderung.',
    '60' : 'Zunehmend bewölkt und wärmer. Niederschlag möglich innerhalb 6 bis 12 Stunden. Windig.',
    '61' : 'Teils wolkig mit geringer Temperaturänderung.',
    '62' : 'Meist heiter mit geringer Temperaturänderung.',
    '63' : 'Zunehmend bewölkt und wärmer. Niederschlag möglich innerhalb 12 bis 24 Stunden. Windig.',
    '64' : 'Teils wolkig mit geringer Temperaturänderung.',
    '65' : 'Meist heiter mit geringer Temperaturänderung.',
    '66' : 'Zunehmend bewölkt und wärmer. Niederschlag möglich innerhalb 12 Stunden.',
    '67' : 'Teils wolkig mit geringer Temperaturänderung.',
    '68' : 'Meist heiter mit geringer Temperaturänderung.',
    '69' : 'Zunehmend bewölkt und wärmer. Niederschlag wahrscheinlich.',
    '70' : 'Aufklarend und kälter. Niederschlag endet innerhalb 6 Stunden.',
    '71' : 'Teils wolkig mit geringer Temperaturänderung.',
    '72' : 'Aufklarend und kälter. Niederschlag endet innerhalb 6 Stunden.',
    '73' : 'Meist heiter mit geringer Temperaturänderung.',
    '74' : 'Aufklarend und kälter. Niederschlag endet innerhalb 6 Stunden.',
    '75' : 'Teils wolkig und kälter.',
    '76' : 'Teils wolkig mit geringer Temperaturänderung.',
    '77' : 'Meist heiter und kälter.',
    '78' : 'Aufklarend und kälter. Niederschlag endet innerhalb 6 Stunden.',
    '79' : 'Meist heiter mit geringer Temperaturänderung.',
    '80' : 'Aufklarend und kälter. Niederschlag endet innerhalb 6 Stunden.',
    '81' : 'Meist heiter und kälter.',
    '82' : 'Teils wolkig mit geringer Temperaturänderung.',
    '83' : 'Meist heiter mit geringer Temperaturänderung.',
    '84' : 'Zunehmend bewölkt mit geringer Temperaturänderung. Niederschlag möglich innerhalb 24 Stunden.',
    '85' : 'Meist wolkig und kälter. Niederschlag dauert an.',
    '86' : 'Teils wolkig mit geringer Temperaturänderung.',
    '87' : 'Meist heiter mit geringer Temperaturänderung.',
    '88' : 'Meist wolkig und kälter. Niederschlag wahrscheinlich.',
    '89' : 'Meist wolkig mit geringer Temperaturänderung. Niederschlag dauert an.',
    '90' : 'Meist wolkig mit geringer Temperaturänderung. Niederschlag wahrscheinlich.',
    '91' : 'Teils wolkig mit geringer Temperaturänderung.',
    '92' : 'Meist heiter mit geringer Temperaturänderung.',
    '93' : 'Zunehmend bewölkt und kälter. Niederschlag möglich und windig innerhalb 6 Stunden.',
    '94' : 'Zunehmend bewölkt mit geringer Temperaturänderung. Niederschlag möglich und windig innerhalb 6 Stunden.',
    '95' : 'Meist wolkig und kälter. Niederschlag dauert an. Zunehmender Wind.',
    '96' : 'Teils wolkig mit geringer Temperaturänderung.',
    '97' : 'Meist heiter mit geringer Temperaturänderung.',
    '98' : 'Meist wolkig und kälter. Niederschlag wahrscheinlich. Zunehmender Wind.',
    '99' : 'Meist wolkig mit geringer Temperaturänderung. Niederschlag dauert an. Zunehmender Wind.',
    '100' : 'Meist wolkig mit geringer Temperaturänderung. Niederschlag wahrscheinlich. Zunehmender Wind.',
    '101' : 'Teils wolkig mit geringer Temperaturänderung.',
    '102' : 'Meist heiter mit geringer Temperaturänderung.',
    '103' : 'Zunehmend bewölkt und kälter. Niederschlag möglich innerhalb 12 bis 24 Stunden und möglicher Windrichtungswechsel auf W, NW, oder N.',
    '104' : 'Zunehmend bewölkt mit geringer Temperaturänderung. Niederschlag möglich innerhalb 12 bis 24 Stunden und möglicher Windrichtungswechsel auf W, NW, oder N.',
    '105' : 'Teils wolkig mit geringer Temperaturänderung.',
    '106' : 'Meist heiter mit geringer Temperaturänderung.',
    '107' : 'Zunehmend bewölkt und kälter. Niederschlag möglich innerhalb 6 Stunden und möglicher Windrichtungswechsel auf W, NW, oder N.',
    '108' : 'Zunehmend bewölkt mit geringer Temperaturänderung. Niederschlag möglich innerhalb 6 Stunden und möglicher Windrichtungswechsel auf W, NW, oder N.',
    '109' : 'Meist wolkig und kälter. Niederschlag endet innerhalb 12 Stunden und möglicher Windrichtungswechsel auf W, NW, oder N.',
    '110' : 'Meist wolkig und kälter. Windrichtungswechsel möglich auf W, NW, oder N.',
    '111' : 'Meist wolkig mit geringer Temperaturänderung. Niederschlag endet innerhalb 12 Stunden und möglicher Windrichtungswechsel auf W, NW, oder N.',
    '112' : 'Meist wolkig mit geringer Temperaturänderung. Windrichtungswechsel möglich auf W, NW, oder N.',
    '113' : 'Meist wolkig und kälter. Niederschlag endet innerhalb 12 Stunden und möglicher Windrichtungswechsel auf W, NW, oder N.',
    '114' : 'Teils wolkig mit geringer Temperaturänderung.',
    '115' : 'Meist heiter mit geringer Temperaturänderung.',
    '116' : 'Meist wolkig und kälter. Niederschlag möglich innerhalb 24 Stunden und möglicher Windrichtungswechsel auf W, NW, oder N.',
    '117' : 'Meist wolkig mit geringer Temperaturänderung. Niederschlag endet innerhalb 12 Stunden und möglicher Windrichtungswechsel auf W, NW, oder N.',
    '118' : 'Meist wolkig mit geringer Temperaturänderung. Niederschlag möglich innerhalb 24 Stunden und möglicher Windrichtungswechsel auf W, NW, oder N.',
    '119' : 'Aufklarend, kälter und windig. Niederschlag endet innerhalb 6 Stunden.',
    '120' : 'Aufklarend, kälter und windig.',
    '121' : 'Meist wolkig und kälter. Niederschlag endet innerhalb 6 Stunden. Windig mit möglichem Windrichtungswechsel auf W, NW, oder N.',
    '122' : 'Meist wolkig und kälter. Windig mit möglichem Windrichtungswechsel auf W, NW, oder N.',
    '123' : 'Aufklarend, kälter und windig.',
    '124' : 'Teils wolkig mit geringer Temperaturänderung.',
    '125' : 'Meist heiter mit geringer Temperaturänderung.',
    '126' : 'Meist wolkig mit geringer Temperaturänderung. Niederschlag möglich innerhalb 12 Stunden. Windig.',
    '127' : 'Teils wolkig mit geringer Temperaturänderung.',
    '128' : 'Meist heiter mit geringer Temperaturänderung.',
    '129' : 'Zunehmend bewölkt und kälter. Niederschlag möglich innerhalb 12 Stunden, zeitweise heftig. Windig.',
    '130' : 'Meist wolkig und kälter. Niederschlag endet innerhalb 6 Stunden. Windig.',
    '131' : 'Teils wolkig mit geringer Temperaturänderung.',
    '132' : 'Meist heiter mit geringer Temperaturänderung.',
    '133' : 'Meist wolkig und kälter. Niederschlag möglich innerhalb 12 Stunden. Windig.',
    '134' : 'Meist wolkig und kälter. Niederschlag endet in 12 bis 24 Stunden.',
    '135' : 'Meist wolkig und kälter.',
    '136' : 'Meist wolkig und kälter. Niederschlag dauert an, zeitweise heftig. Windig.',
    '137' : 'Teils wolkig mit geringer Temperaturänderung.',
    '138' : 'Meist heiter mit geringer Temperaturänderung.',
    '139' : 'Meist wolkig und kälter. Niederschlag möglich innerhalb 6 bis 12 Stunden. Windig.',
    '140' : 'Meist wolkig mit geringer Temperaturänderung. Niederschlag dauert an, zeitweise heftig. Windig.',
    '141' : 'Teils wolkig mit geringer Temperaturänderung.',
    '142' : 'Meist heiter mit geringer Temperaturänderung.',
    '143' : 'Meist wolkig mit geringer Temperaturänderung. Niederschlag möglich innerhalb 6 bis 12 Stunden. Windig.',
    '144' : 'Teils wolkig mit geringer Temperaturänderung.',
    '145' : 'Meist heiter mit geringer Temperaturänderung.',
    '146' : 'Zunehmend bewölkt mit geringer Temperaturänderung. Niederschlag möglich innerhalb 12 Stunden, zeitweise heftig. Windig.',
    '147' : 'Meist wolkig und kälter. Windig.',
    '148' : 'Meist wolkig und kälter. Niederschlag dauert an, zeitweise heftig. Windig.',
    '149' : 'Teils wolkig mit geringer Temperaturänderung.',
    '150' : 'Meist heiter mit geringer Temperaturänderung.',
    '151' : 'Meist wolkig und kälter. Niederschlag wahrscheinlich, zeitweise heftig. Windig.',
    '152' : 'Meist wolkig mit geringer Temperaturänderung. Niederschlag dauert an, zeitweise heftig. Windig.',
    '153' : 'Meist wolkig mit geringer Temperaturänderung. Niederschlag wahrscheinlich, zeitweise heftig. Windig.',
    '154' : 'Teils wolkig mit geringer Temperaturänderung.',
    '155' : 'Meist heiter mit geringer Temperaturänderung.',
    '156' : 'Zunehmend bewölkt und kälter. Niederschlag möglich innerhalb 6 Stunden. Windig.',
    '157' : 'Zunehmend bewölkt mit geringer Temperaturänderung. Niederschlag möglich innerhalb 6 Stunden. Windig.',
    '158' : 'Zunehmend bewölkt und kälter. Niederschlag dauert an. Windig mit möglichem Windrichtungswechsel auf W, NW, oder N.',
    '159' : 'Teils wolkig mit geringer Temperaturänderung.',
    '160' : 'Meist heiter mit geringer Temperaturänderung.',
    '161' : 'Meist wolkig und kälter. Niederschlag wahrscheinlich. Windig mit möglichem Windrichtungswechsel auf W, NW, oder N.',
    '162' : 'Meist wolkig mit geringer Temperaturänderung. Niederschlag dauert an. Windig mit möglichem Windrichtungswechsel auf W, NW, oder N.',
    '163' : 'Meist wolkig mit geringer Temperaturänderung. Niederschlag wahrscheinlich. Windig mit möglichem Windrichtungswechsel auf W, NW, oder N.',
    '164' : 'Zunehmend bewölkt und kälter. Niederschlag möglich innerhalb 6 Stunden. Windig mit möglichem Windrichtungswechsel auf W, NW, oder N.',
    '165' : 'Teils wolkig mit geringer Temperaturänderung.',
    '166' : 'Meist heiter mit geringer Temperaturänderung.',
    '167' : 'Zunehmend bewölkt und kälter. Niederschlag möglich innerhalb 6 Stunden und möglicher Windrichtungswechsel auf W, NW, oder N.',
    '168' : 'Zunehmend bewölkt mit geringer Temperaturänderung. Niederschlag möglich innerhalb 6 Stunden. Windig mit möglichem Windrichtungswechsel auf W, NW, oder N.',
    '169' : 'Zunehmend bewölkt mit geringer Temperaturänderung. Niederschlag möglich innerhalb 6 Stunden und möglicher Windrichtungswechsel auf W, NW, oder N.',
    '170' : 'Teils wolkig mit geringer Temperaturänderung.',
    '171' : 'Meist heiter mit geringer Temperaturänderung.',
    '172' : 'Zunehmend bewölkt und kälter. Niederschlag möglich innerhalb 6 Stunden. Windig mit möglichem Windrichtungswechsel auf W, NW, oder N.',
    '173' : 'Zunehmend bewölkt mit geringer Temperaturänderung. Niederschlag möglich innerhalb 6 Stunden. Windig mit möglichem Windrichtungswechsel auf W, NW, oder N.',
    '174' : 'Teils wolkig mit geringer Temperaturänderung.',
    '175' : 'Meist heiter mit geringer Temperaturänderung.',
    '176' : 'Zunehmend bewölkt und kälter. Niederschlag möglich innerhalb 12 bis 24 Stunden. Windig mit möglichem Windrichtungswechsel auf W, NW, oder N.',
    '177' : 'Zunehmend bewölkt mit geringer Temperaturänderung. Niederschlag möglich innerhalb 12 bis 24 Stunden. Windig mit möglichem Windrichtungswechsel auf W, NW, oder N.',
    '178' : 'Meist wolkig und kälter. Niederschlag zeitweise heftig und endet innerhalb 12 Stunden. Windig mit möglichem Windrichtungswechsel auf W, NW, oder N.',
    '179' : 'Teils wolkig mit geringer Temperaturänderung.',
    '180' : 'Meist heiter mit geringer Temperaturänderung.',
    '181' : 'Meist wolkig und kälter. Niederschlag möglich innerhalb 6 bis 12 Stunden, zeitweise heftig. Windig mit möglichem Windrichtungswechsel auf W, NW, oder N.',
    '182' : 'Meist wolkig mit geringer Temperaturänderung. Niederschlag endet innerhalb 12 Stunden. Windig mit möglichem Windrichtungswechsel auf W, NW, oder N.',
    '183' : 'Meist wolkig mit geringer Temperaturänderung. Niederschlag möglich innerhalb 6 bis 12 Stunden, zeitweise heftig. Windig mit möglichem Windrichtungswechsel auf W, NW, oder N.',
    '184' : 'Meist wolkig und kälter. Niederschlag dauert an.',
    '185' : 'Teils wolkig mit geringer Temperaturänderung.',
    '186' : 'Meist heiter mit geringer Temperaturänderung.',
    '187' : 'Meist wolkig und kälter. Niederschlag wahrscheinlich. Windig mit möglichem Windrichtungswechsel auf W, NW, oder N.',
    '188' : 'Meist wolkig mit geringer Temperaturänderung. Niederschlag dauert an.',
    '189' : 'Meist wolkig mit geringer Temperaturänderung. Niederschlag wahrscheinlich.',
    '190' : 'Teils wolkig mit geringer Temperaturänderung.',
    '191' : 'Meist heiter mit geringer Temperaturänderung.',
    '192' : 'Meist wolkig und kälter. Niederschlag möglich innerhalb 12 Stunden, zeitweise heftig. Windig.',
    '193' : 'FORECAST REQUIRES 3 HOURS OF RECENT DATA',
    '194' : 'Meist heiter und kälter.',
    '195' : 'Meist heiter und kälter.',
    '196' : 'Meist heiter und kälter.',
    }

class vantageText(SearchList):

    def __init__(self, generator):
        SearchList.__init__(self, generator)

    def get_extension_list(self, timespan, db_lookup):
        """Returns a search list extension with additions.
        timespan: An instance of weeutil.weeutil.TimeSpan. This holds
                  the start and stop times of the domain of valid times.
        db_lookup: Function that returns a database manager given a
                   data binding.
        """

        # First, create a TimespanBinder object for all time. This one is easy
        # because the object timespan already holds all valid times to be
        # used in the report.
        vantageForecastText = 'a'
        #_row = db_lookup().getSql("SELECT MAX(dateTime), forecastRule FROM archive")
        _row = db_lookup().getSql("SELECT forecastRule FROM archive ORDER BY dateTime DESC LIMIT 1")

        data_text = str(int(_row[0]))

        #log.info(" Roule Worte is %s", data_text)

        try:
            vantageForecastText = davis_fr_dict[data_text]

            #log.info("Text is %s", vantageForecastText)

        except:
            vantageForecastText = 'Could not decode Vantage forecast code'

        search_list_extension = {'vantageText': vantageForecastText}

        # Return our vantage data
        return [search_list_extension]
