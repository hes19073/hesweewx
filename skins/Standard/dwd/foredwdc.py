#!/usr/bin/env python
# -*- coding: utf-8 -*-
#*********************************************************************
# Connect Baudot Convertierung von Warnmeldungen
# Entfernung Steuerzeichen und ersetzten von CR gegen CRLF
#
# Den ersten Dateiname aus der Textliste einlesen und die Datei mit dem gelesene 
# Namen oeffnen.
#
# Autor : Frank Ulbrich
# Date : 29.09.2016
#*********************************************************************

import textwrap
import os, sys
import fnmatch                          # match names
import ftplib                           # ftp connect
import locale
import codecs

sourcepathw = 'filedownload/warnlagen/'
sourcepathf = '/home/dwd/filelist/'
targetpath = '/home/weewx/dwd/'
#targetpath = 'converted/' 

#*********************************************************************
 

myfile = open(sourcepathf + 'wetter0.txt', 'r')

newfile = ''
for line in myfile:
    #line = line.replace('0xd6', '&Ouml;')
    #line = line.replace('0xf6', '&ouml;')
    #line = line.replace('0xdc', '&Uuml;')
    #line = line.replace('0xfc', '&uuml;')
    #line = line.replace('0xc4', '&Auml;')
    #line = line.replace('0xe4', '&auml;')
    #line = line.replace('0xdf', '&zslig')
    line = line.decode("windows-1252")
    line = line.encode("utf-8")
    line = line.replace(chr(1), ' ')   # Steuerzeichen SOH aus Textanfang entfernen
    line = line.replace(chr(3), ' ')   # Steuerzeichen ETX aus Textende entfernen
    line = line.replace('\r\n', '\n')
    line = line.replace('. ', '.\n') 
    newfile = newfile + line
   
    #print(line)
myfile.close()

outfile = open(targetpath + 'wetter0.txt',  "w")
outfile.write('#encoding UTF-8')
outfile.write( '\n' )
outfile.write(newfile)
#outfile.write( "\nHES\n" )
outfile.close()

# **************************************************************************

myfile = open(sourcepathf + 'wetter1.txt', 'r')

newfile = ''
for line in myfile:

    line = line.decode("windows-1252")
    line = line.encode("utf-8")
    line = line.replace(chr(1), ' ')   # Steuerzeichen SOH aus Textanfang entfernen
    line = line.replace(chr(3), ' ')   # Steuerzeichen ETX aus Textende entfernen
    line = line.replace('\r\n', '\n')
    line = line.replace('. ', '.\n')
    newfile = newfile + line

    #print(line)
myfile.close()

outfile = open(targetpath + 'wetter1.txt',  "w")
outfile.write('#encoding UTF-8')
outfile.write( '\n' )
outfile.write(newfile)
#outfile.write( "\nHES\n" )
outfile.close()

myfile = open(sourcepathf + 'wetter2.txt', 'r')

newfile = ''
for line in myfile:

    line = line.decode("windows-1252")
    line = line.encode("utf-8")
    line = line.replace(chr(1), ' ')   # Steuerzeichen SOH aus Textanfang entfernen
    line = line.replace(chr(3), ' ')   # Steuerzeichen ETX aus Textende entfernen
    line = line.replace('\r\n', '\n')
    line = line.replace('. ', '.\n')
    newfile = newfile + line

    #print(line)
myfile.close()

outfile = open(targetpath + 'wetter2.txt',  "w")
outfile.write('#encoding UTF-8')
outfile.write( '\n' )
outfile.write(newfile)
#outfile.write( "\nHES\n" )
outfile.close()

myfile = open(sourcepathf + 'wetter3.txt', 'r')

newfile = ''
for line in myfile:

    line = line.decode("windows-1252")
    line = line.encode("utf-8")
    line = line.replace(chr(1), ' ')   # Steuerzeichen SOH aus Textanfang entfernen
    line = line.replace(chr(3), ' ')   # Steuerzeichen ETX aus Textende entfernen
    line = line.replace('\r\n', '\n')
    line = line.replace('. ', '.\n')
    newfile = newfile + line

    #print(line)
myfile.close()

outfile = open(targetpath + 'wetter3.txt',  "w")
outfile.write('#encoding UTF-8')
outfile.write( '\n' )
outfile.write(newfile)
#outfile.write( "\nHES\n" )
outfile.close()

myfile = open(sourcepathf + 'wetter4.txt', 'r')

newfile = ''
for line in myfile:

    line = line.decode("windows-1252")
    line = line.encode("utf-8")
    line = line.replace(chr(1), ' ')   # Steuerzeichen SOH aus Textanfang entfernen
    line = line.replace(chr(3), ' ')   # Steuerzeichen ETX aus Textende entfernen
    line = line.replace('\r\n', '\n')
    line = line.replace('. ', '.\n')
    newfile = newfile + line

    #print(line)
myfile.close()

outfile = open(targetpath + 'wetter4.txt',  "w")
outfile.write('#encoding UTF-8')
outfile.write( '\n' )
outfile.write(newfile)
outfile.write( "\nQuelle: Deutscher Wetterdienst      Zeit: UTC\n" )
outfile.close()

