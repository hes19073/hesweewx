#! /usr/bin/env python
# -*- coding: utf-8 -*-

#*********************************************************************
# Connect DWD FTP Server and download Forecast und Warnlagen
# Autor : Hartmut Schweidler
# Date  : 04.12.2016
#*********************************************************************
# Server : ftp-outgoing2.dwd.de
# User : 
# PW: 
# Interpreter : python 2.7
#*********************************************************************
# imported libraries
# NEU  https://opendata.dwd.de/weather/text_forecasts/html/

import fnmatch                          # match names
import ftplib                           # ftp connect
import sys
import codecs
import time

stdout_encoding = sys.stdout.encoding or sys.getfilesystemencoding

#*********************************************************************
# FTP Server Parameter
#*********************************************************************
ftpserver = 'opendata.dwd.de'    # Server
ftpuser = 'anonymous'
ftppw = 'anonymous'

tag0 = 'VHDL50_DWPH_'
tag1 = 'VHDL51_DWPH_'
tag2 = 'VHDL52_DWPH_'
tag3 = 'VHDL53_DWPH_'
tag4 = 'VHDL54_DWPH_'
tagdat = time.strftime("%d")
tagstu = time.strftime("%H")

lt = time.localtime()
lt_dst = lt[8]

if lt_dst == 1:
    tagstu = '%0.2d' % (int(tagstu) - 2)
else:
    tagstu = '%0.2d' % (int(tagstu) - 1)

tagstu = str(tagstu)

t0 = tag0 + tagdat + tagstu + "34_html"
t1 = tag1 + tagdat + tagstu + "34_html"
t2 = tag2 + tagdat + tagstu + "34_html"
t3 = tag3 + tagdat + tagstu + "34_html"
t4 = tag4 + tagdat + tagstu + "34_html"

ftppath_local = "/home/dwd/filelist/"

ftppath = '/weather/text_forecasts/html/'

ftp = ftplib.FTP(ftpserver, ftpuser, ftppw)
ftp.cwd(ftppath)                             #changing to forecasts

# Download textfile  
#*********************************************************************

_tag0 = "wetter0.txt"
_tag1 = "wetter1.txt"
_tag2 = "wetter2.txt"
_tag3 = "wetter3.txt"
_tag4 = "wetter4.txt"

file = open(ftppath_local + _tag0, 'wd')
ftp.retrbinary('RETR '+t0, file.write)

file = open(ftppath_local + _tag1, 'wd')
ftp.retrbinary('RETR '+t1, file.write)

file = open(ftppath_local + _tag2, 'wd')
ftp.retrbinary('RETR '+t2, file.write)

file = open(ftppath_local + _tag3, 'wd')
ftp.retrbinary('RETR '+t3, file.write)

file = open(ftppath_local + _tag4, 'wd')
ftp.retrbinary('RETR '+t4, file.write)

ftp.quit()
quit()
#Ende des Program

