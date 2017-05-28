#! /usr/bin/env python
# -*- coding: utf-8 -*-

#*********************************************************************
# Connect DWD FTP Server and download Warnlagen
# Autor : Hartmut Schweidler
# Date  : 19.12.2016
#*********************************************************************
# Server : ftp-outgoing2.dwd.de
# User :   gdXXXXXX
# PW :     xjxjxjxj
# Interpreter : python 2.7
#*********************************************************************
# imported libraries
import os, sys
import fnmatch                          # match names
import ftplib                           # ftp connect
import locale
import codecs

stdout_encoding = sys.stdout.encoding or sys.getfilesystemencoding

sourcepathf = '/home/dwd/filelist/'
targetpath = '/home/weewx/dwd/'
# ********************************************************************
myfile = open(sourcepathf + 'wetter00.txt', 'r')

newfile = ''
for line in myfile:
    line = line.replace(chr(1), ' ')   # Steuerzeichen SOH aus Textanfang entfernen
    line = line.replace(chr(3), ' ')   # Steuerzeichen ETX aus Textende entfernen
    line = line.decode("windows-1252")
    line = line.encode("utf-8")
    line = line.replace('\r\n', '\n')
    #line = line.replace('. ', '.\n')
    newfile = newfile + line
myfile.close()

outfile = open(targetpath + 'wetter00.txt',  "w")
outfile.write('#encoding UTF-8')
outfile.write( '\n' )
outfile.write(newfile)
#outfile.write( "\nQuelle: Deutscher Wetterdienst      Zeit: UTC\n" )
outfile.close()


