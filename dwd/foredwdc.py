#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Autor : Hartmut Schweidler
# Date : 11.12.2016
#*********************************************************************

import textwrap
import os, sys
import fnmatch                          # match names
import ftplib                           # ftp connect
import locale
import codecs

sourcepathf = '/home/dwd/filelist/'
targetpath = '/home/weewx/dwd/'

#*********************************************************************


myfile = open(sourcepathf + 'wetter0.txt', 'r')

newfile = ''
for line in myfile:
    line = line.decode("windows-1252") #codierung der Seiten per 01.12.2016
    line = line.encode("utf-8")
    line = line.replace(chr(1), ' ')   # Steuerzeichen SOH aus Textanfang entfernen
    line = line.replace(chr(3), ' ')   # Steuerzeichen ETX aus Textende entfernen
    line = line.replace('\r\n', '\n')
    line = line.replace('. ', '.\n')
    newfile = newfile + line
myfile.close()

outfile = open(targetpath + 'wetter0.txt',  "w")
outfile.write('#encoding UTF-8')
outfile.write( '\n' )
outfile.write(newfile)
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
myfile.close()

outfile = open(targetpath + 'wetter1.txt',  "w")
outfile.write('#encoding UTF-8')
outfile.write( '\n' )
outfile.write(newfile)
outfile.close()

# *********************************************************
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
myfile.close()

outfile = open(targetpath + 'wetter2.txt',  "w")
outfile.write('#encoding UTF-8')
outfile.write( '\n' )
outfile.write(newfile)
outfile.close()

# *****************************************************************
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

myfile.close()

outfile = open(targetpath + 'wetter3.txt',  "w")
outfile.write('#encoding UTF-8')
outfile.write( '\n' )
outfile.write(newfile)
#outfile.write( "\nHES\n" )
outfile.close()

# ********************************************************************
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
myfile.close()

outfile = open(targetpath + 'wetter4.txt',  "w")
outfile.write('#encoding UTF-8')
outfile.write( '\n' )
outfile.write(newfile)
outfile.write( "\nQuelle: Deutscher Wetterdienst      Zeit: UTC\n" )
outfile.close()
