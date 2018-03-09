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

#*********************************************************************
 

myfile = open(sourcepathf + 'wetter0.txt', 'r')

newfile = ''
for line in myfile:
    line = line.decode("windows-1252")
    line = line.encode("utf-8")
    line = line.replace(chr(1), '<p>')   # Steuerzeichen SOH aus Textanfang entfernen
    line = line.replace(chr(3), '</p>')   # Steuerzeichen ETX aus Textende entfernen
    line = line.replace('<pre style="font-family: sans-serif">', ' ')
    line = line.replace('</pre>', ' ')
    line = line.replace('. ', '. <br>') 
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
    line = line.replace(chr(1), '<p>')   # Steuerzeichen SOH aus Textanfang entfernen
    line = line.replace(chr(3), '</p>')   # Steuerzeichen ETX aus Textende entfernen
    #line = line.replace('\r\n', '\n')
    line = line.replace('<pre style="font-family: sans-serif">', ' ')
    line = line.replace('</pre>', ' ')
    line = line.replace('. ', '. <br>')
    newfile = newfile + line

myfile.close()

outfile = open(targetpath + 'wetter1.txt',  "w")
outfile.write('#encoding UTF-8')
outfile.write( '\n' )
outfile.write(newfile)
outfile.close()

myfile = open(sourcepathf + 'wetter2.txt', 'r')

newfile = ''
for line in myfile:

    line = line.decode("windows-1252")
    line = line.encode("utf-8")
    line = line.replace(chr(1), '<p>')   # Steuerzeichen SOH aus Textanfang entfernen
    line = line.replace(chr(3), '</p>')   # Steuerzeichen ETX aus Textende entfernen
    #line = line.replace('\r\n', '\n')
    line = line.replace('<pre style="font-family: sans-serif">', ' ')
    line = line.replace('</pre>', ' ')
    line = line.replace('. ', '. <br>')
    newfile = newfile + line

myfile.close()

outfile = open(targetpath + 'wetter2.txt',  "w")
outfile.write('#encoding UTF-8')
outfile.write( '\n' )
outfile.write(newfile)
outfile.close()

myfile = open(sourcepathf + 'wetter3.txt', 'r')

newfile = ''
for line in myfile:

    line = line.decode("windows-1252")
    line = line.encode("utf-8")
    line = line.replace(chr(1), '<p>')   # Steuerzeichen SOH aus Textanfang entfernen
    line = line.replace(chr(3), '</p>')   # Steuerzeichen ETX aus Textende entfernen
    #line = line.replace('\r\n', '\n')
    line = line.replace('<pre style="font-family: sans-serif">', ' ')
    line = line.replace('</pre>', ' ')
    line = line.replace('. ', '. <br>')
    newfile = newfile + line

myfile.close()

outfile = open(targetpath + 'wetter3.txt',  "w")
outfile.write('#encoding UTF-8')
outfile.write( '\n' )
outfile.write(newfile)
outfile.close()

myfile = open(sourcepathf + 'wetter4.txt', 'r')

newfile = ''
for line in myfile:

    line = line.decode("windows-1252")
    line = line.encode("utf-8")
    line = line.replace(chr(1), ' ')   # Steuerzeichen SOH aus Textanfang entfernen
    line = line.replace(chr(3), ' ')   # Steuerzeichen ETX aus Textende entfernen
    #line = line.replace('\r\n', '\n')
    line = line.replace('<pre style="font-family: sans-serif">', ' ')
    line = line.replace('</pre>', ' ')
    line = line.replace('. ', '. <br>')
    newfile = newfile + line

myfile.close()

outfile = open(targetpath + 'wetter4.txt',  "w")
outfile.write('#encoding UTF-8')
outfile.write( '\n' )
outfile.write(newfile)
outfile.write( "\nQuelle: Deutscher Wetterdienst \n" )
outfile.close()

