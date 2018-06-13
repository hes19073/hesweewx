#!/usr/bin/python

from sys import argv
from mx.DateTime import *

def DateFormat(string, date):
    print string + ": " + str(date.day) + '.' + str(ostern.month) + '.' + str(ostern.year)

if len(argv) <= 1 :
    year = now().year
else:
    year = int(argv[1])

d=(((255 - 11 * (year % 19)) - 21) % 30) + 21
if d > 48:
    d+=1

delta = d + 6 -  ((year + (year - ((year % 4))) / 4) + d + 1) % 7

ostern = DateTime(year,3,1) + delta

DateFormat("Aschermittwoch", ostern - 46)
DateFormat("Karfreitag", ostern - 2)
DateFormat("Ostern", ostern)
DateFormat("Ostermontag", ostern + 1)
DateFormat("Himmelfahrt", ostern + 39)
DateFormat("Pfingstsonntag", ostern + 49)
DateFormat("Pfingstmontag", ostern + 50)
# of calcEastern1()
