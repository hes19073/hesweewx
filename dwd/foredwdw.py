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
import ftplib                           # ftp connect
import sys
import codecs
import time

stdout_encoding = sys.stdout.encoding or sys.getfilesystemencoding

#*********************************************************************
# FTP Server Parameter
#*********************************************************************
ftpserver = 'ftp-outgoing2.dwd.de'    # Server
ftpuser = 'gds22308'
ftppw =  'LRhDjtBa'

# for Mecklenburg-Vorpommern VHDL30_DWPH_ddhhmm_thml
# aktuell um 04:30 06:30 10:30 15:30 17:30 20:30

tag00 = 'VHDL30_DWPH_'

tagdat = time.strftime("%d")
tagstu = time.strftime("%H")

lt = time.localtime()
lt_dst = lt[8]

if lt_dst == 1:
    tagstu = '%0.2d' % (int(tagstu) - 2)
else:
    tagstu = '%0.2d' % (int(tagstu) - 1)

#tagstu = '%0.2d' % (int(tagstu) - 2)    # DWD in UTC Time
tagstu = str(tagstu)                    # Anpassung bei Sommerzeit '-2'

# test
#tagdat = "19"
#tagstu = "14"

t0 = tag00 + tagdat + tagstu + "30"

ftppath_local = "/home/dwd/filelist/"
ftppath = 'gds/specials/forecasts/text'  # Warnmeldungen – VHDL30_DWPH   MVP

ftp = ftplib.FTP(ftpserver, ftpuser, ftppw)
ftp.cwd(ftppath)

# Download textfile
#*********************************************************************

_tag0 = "wetter00.txt"

file = open(ftppath_local + _tag0, 'wd')
ftp.retrbinary('RETR '+t0, file.write)

ftp.quit()
quit()
#Ende des Program

