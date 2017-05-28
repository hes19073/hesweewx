#! /usr/bin/env python
# -*- coding: utf-8 -*-

#*********************************************************************
# Connect DWD FTP Server and download Pollen
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

# for Mecklenburg-Vorpommern pollen s_b31fg.xml
# aktuell um 09:00 UTC

t0 = "s_b31fg.xml"

ftppath_local = "/home/dwd/filelist/"
ftppath = 'gds/specials/alerts/health'  # Pollenmeldungen – s_b31fg.xml   MVP

ftp = ftplib.FTP(ftpserver, ftpuser, ftppw)
ftp.cwd(ftppath)

# Download textfile
#*********************************************************************

_tag0 = "pollen0.xml"

file = open(ftppath_local + _tag0, 'wd')
ftp.retrbinary('RETR '+t0, file.write)

ftp.quit()
quit()
#Ende des Program

