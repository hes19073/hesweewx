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
import fnmatch                          # match names
import ftplib                           # ftp connect
import sys
import codecs
import time

stdout_encoding = sys.stdout.encoding or sys.getfilesystemencoding
#*********************************************************************
# FTP Server Parameter
#*********************************************************************
ftpserver = 'ftp-outgoing2.dwd.de'
ftpuser = 'gdsXXXXX'
ftppw =  'myPass'

# for Mecklenburg-Vorpommern VHDL[50, 51, 52, 53, 54]_DWPH_ddhh34_thml

tag0 = 'VHDL50_DWPH_'
tag1 = 'VHDL51_DWPH_'
tag2 = 'VHDL52_DWPH_'
tag3 = 'VHDL53_DWPH_'
tag4 = 'VHDL54_DWPH_'

tagdat = time.strftime("%d")
tagstu = time.strftime("%H")
tagstu = '%0.2d' % (int(tagstu) - 1)
tagstu = str(tagstu)

# test
#tagdat = "04"
#tagstu = "09"

t0 = tag0 + tagdat + tagstu + "34_html"
t1 = tag1 + tagdat + tagstu + "34_html"
t2 = tag2 + tagdat + tagstu + "34_html"
t3 = tag3 + tagdat + tagstu + "34_html"
t4 = tag4 + tagdat + tagstu + "34_html"

ftppath_local = "/home/dwd/filelist/"
ftppath = 'gds/specials/forecasts/text' # Warnmeldungen - VHDL50_DWPH  WARNLAGE POM

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

