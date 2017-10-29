#!/usr/bin/python
# -*- coding: utf-8 -*-
# xcolor.py 1396 2017-10-21 05:08:45Z hes $
# Copyright 2017 Hartmut Schweidler


from weewx.cheetahgenerator import SearchList
import weeutil.weeutil

class MyDecorator(SearchList):
    """My search list extension"""

    def __init__(self, generator):
        SearchList.__init__(self, generator)
        self.table_dict = generator.skin_dict['IndexColors']

    def decoratorColorStub(self, type, value):
        table_options = weeutil.weeutil.accumulateLeaves(self.table_dict[type])
        table = zip(table_options['maxvalues'], table_options['colors'])
        value = self.decoFunction(value, table)

        if value == "-" :
            htmlLine = ""

        else :
            htmlLine ="background-color:%s" % value

        return htmlLine

    def decoratorTextStub(self, type, value):
        table_options = weeutil.weeutil.accumulateLeaves(self.table_dict[type])
        table = zip(table_options['maxvalues'], table_options['text1'])
        htmlLine = self.decoFunction(value, table)

        return htmlLine

    def get_extension_list(self, timespan, db_lookup):
        print "get_extension_list"
        # Now create a small dictionary with keys 'UV_color' and 'UV_text':

        search_list_extension = {'decorator_color'   : self.decoratorColorStub,
                                 'decorator_text'    : self.decoratorTextStub}

        # Finally, return our extension as a list:
        return [search_list_extension]

    def decoFunction(self, value, table):
        # print table

        if value is not None:
            for c in table:
                if (value <= int(float(c[0]))):
                    #retval = c[1]
                    #break
                    return c[1]
        else:
           # retval = "#error2" # WHITE TODO decide what we return here ?
        
            return "-"
