#encoding UTF-8
## calendar.inc  2015-02-23 18:24:18Z hes $

#import platform
#import sys
#import calendar
#import datetime
#import re

#set today = datetime.date.today()
#set $ano = today.year
#set $mon = today.month
#set $hes = today.day
#set $c = calendar.HTMLCalendar()
#set $cc =  $c.formatmonth($ano, $mon)
##set $hes = str($hes)
##set $dc = re.sub($hes,'<b>'+$hes+'</b>', $cc)
 $cc


