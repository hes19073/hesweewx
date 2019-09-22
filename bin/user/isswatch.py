#
# Copyright (c) 2016 Chris Davies-Barnard <weewx@davies-barnard.co.uk>
#
# See the file LICENSE.txt for your full rights.
#

""" This search list extension offers two extra tags:

    'issnext': The next possible sighting of the ISS (International Space Station).
               This is a single occurance of the isswatch object

    'issall': All the future sightings of the ISS.
              As used in the isswatch skin template.
              This is an array or list of the single objects.

"""

from __future__ import print_function
from __future__ import with_statement

import sys
import syslog
import hashlib
import http.client

import urllib.request, urllib.error, urllib.parse
import xml.etree.ElementTree as ET
import time
import datetime
import re

from urllib.request import urlopen
from weeutil.log import logdbg, loginf, logerr, logcrt
from weewx.cheetahgenerator import SearchList

class ISSAlert(SearchList):
    """Retrieves data from an ISS Station RSS Feed and converts it into a variable that is available for templates."""

    def __init__(self, generator=None):
        SearchList.__init__(self, generator)

    def get_extension_list(self, timespan, db_lookup):
        """Returns a search list extension with two additions. """

        #Pass the RSS feed from the weewx.conf to the processAlertUrl
        issall = self.processAlertRSS(self.generator.config_dict['StdReport']['isswatch']['url'])
        #issall = self.processAlertRSS(self, 'https://spotthestation.nasa.gov/sightings/xml_files/Germany_None_Luneburg.xml')

        #if len(issall) < 10:
        #   search_list_extension = { 'issnext' : None, 'issall' : None }
        #else:
            # Now create a small dictionary :
        #    search_list_extension = { 'issnext' : issall[0], 'issall' : issall }
        search_list_extension = { 'issnext' : issall[0], 'issall' : issall }

        # Finally, return our extension as a list:
        return [search_list_extension]

    def processAlertRSS(self, feedurl):
        #Retrieve the RSS feed
        try:
            feedsource = urlopen(feedurl)
        except urllib.error.HTTPError as e:
            print(('HTTPError = ' + str(e.code)))
        except urllib.error.URLError as e:
            print(('URLError = ' + str(e.reason)))
        except http.client.HTTPException as e:
            print ('HTTPException')
        except Exception:
            import traceback
            print('generic exception: ' + traceback.format_exc())

        feeddata = feedsource.read()
        feedsource.close()

        #Convert into XML Doc
        xmldoc = ET.fromstring(feeddata)
        issall = []
        for sighting in xmldoc.iter('item'):
            newsighting = {
                           'pubdate':sighting.find('pubDate').text,
                           'guid':sighting.find('guid').text,
                           'pubts':self.get_ts(sighting.find('pubDate').text),
                }

            #Split the title to get just the object e.g. ISS, Dragon etc.
            title = sighting.find('title').text.split(" ",1)
            newsighting['title'] = title[1]
            newsighting['title'] = (title[1]).replace('Sighting', 'Sichtung')

            #Cut and Chop the description into its different elements.
            description = re.sub(r'\n\t+', '', sighting.find('description').text)
            description = description.split("<br/>")
            for entry in description:
                if entry != "":
                    metatitle, metaentry = entry.split(":",1)
                    newsighting[metatitle.lower().replace(" ","")] = metaentry.strip()

            #Has the time passed?
            now = time.time()
            from datetime import timedelta
            startDay = datetime.datetime.strptime(title[0],"%Y-%m-%d")
            newsighting['date'] = "{}.{}.{}".format(startDay.day,startDay.month,startDay.year)
            m11 = newsighting['date']
            m12 = newsighting['time']
            dat_time = m11 + " " + m12
            tmp = dat_time.split(" ")
            format12 = '%H:%M'
            format24 = '%H:%M'
            my_hour = datetime.datetime.strptime(tmp[1], format12)
            if (tmp[2] == 'PM'):
                my_hour += timedelta(hours=12)

            newsighting['time'] = my_hour.strftime(format24)

            then = time.mktime(datetime.datetime.strptime(newsighting['date'] + " 00:00:00", "%d.%m.%Y %H:%M:%S").timetuple())

            newsighting['departure'] = (newsighting['departure']).replace('above', '&uuml;ber')
            newsighting['approach'] = (newsighting['approach']).replace('above', '&uuml;ber')
            newsighting['duration'] = (newsighting['duration']).replace('less than', 'weniger als')

            if then > now:
                #Add this sighting to our list of all
                issall.append(newsighting)

        return issall

    def get_ts(self,pubdate):
        """Converts a Pub Date e.g. 19 Jan 2016 17:24:51 GMT into a timestamp"""

        pubdate = re.sub(' GMT$', '', pubdate)
        format = "%d %b %Y %H:%M:%S"
        return time.mktime(datetime.datetime.strptime(pubdate, format).timetuple())

    def clean(self,value):
        print(("Cleaning ",value))


"""This is for testing"""
#PYTHONPATH=bin python bin/user/isswatch.py weewx.conf
if __name__ == '__main__':

        import weewx
        import socket
        import configobj

        weewx.debug = 1
        syslog.openlog('wee_isswatch', syslog.LOG_PID|syslog.LOG_CONS)
        syslog.setlogmask(syslog.LOG_UPTO(syslog.LOG_DEBUG))

        if len(sys.argv) < 1 :
                        print("""Usage: isswatch.py path-to-configuration-file""")
                        sys.exit(weewx.CMD_ERROR)

        try :
                        config_dict = configobj.ConfigObj(sys.argv[1], file_error=True)
        except IOError:
                        print(("Unable to open configuration file ", sys.argv[1]))
                        raise

        socket.setdefaulttimeout(10)

        feedurl = config_dict['StdReport']['isswatch']['url']
        print (feedurl)

        isswatcher = ISSAlert()
        issall = isswatcher.processAlertRSS(feedurl)

        print(issall)
