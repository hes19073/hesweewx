#! /usr/bin/env python
# -*- coding: utf-8 -*-

#*********************************************************************
# Connect DWD FTP Server and download Warnlagen
# Autor : Hartmut Schweidler
# Date  : 29.12.2017
#*********************************************************************
# Server : https://opendata.dwd.de
# Interpreter : python 2.7
#*********************************************************************
# imported libraries
import ftplib                           # ftp connect
import urllib2
import fnmatch
import ssl
import os, sys
import codecs
import locale
import time

from ftplib import FTP

stdout_encoding = sys.stdout.encoding or sys.getfilesystemencoding

#*********************************************************************
# FTP Server Parameter
#*********************************************************************
ftpserver = 'opendata.dwd.de'    # Server
ftpuser = 'anonymous'
ftppw = 'anonymous@'
# for Mecklenburg-Vorpommern VHDL30_DWPH_ddhhmm
#tag00 = 'VHDL30_DWPH_'

datapath_local = "/home/dwd/filelist/"
ftppath = '/weather/alerts/txt/PD/'      # Wettermeldungen - VHDL30_DWPH

ftp = ftplib.FTP(ftpserver, ftpuser, ftppw)

ftp.cwd(ftppath)

filedwd = datapath_local + 'dwd_warn.txt'

filelist = []
line = ftp.retrlines("NLST",filelist.append)     # read filenames and write into list of files
filelist = sorted(filelist,reverse=True)           # Absteigende Sortierung der Namen

myfile = open(filedwd,'w')

for item in filelist:
    if fnmatch.fnmatch(item, 'VHDL30_DWPH*'):    # filter for files with specific characters

        myfile.write(item+"\n")

myfile.close()

# Download textfile
#*********************************************************************
myfile = open(filedwd,'r')
inlist = myfile.readlines()              # Using .readlines()

filelistfile =  []

for i in inlist:
    filelistfile.append(i.rstrip('\n'))  # Das Zeichen \n entgernen
myfile.close()

for takefile in filelistfile:
    try:
      if fnmatch.fnmatch(takefile, '*'):
        #print ('* Download : %s' %(takefile))

        ftp.retrlines('RETR '+takefile, open('/home/dwd/filelist/dwd_wa.txt', 'wb').write)
        break                 # nur das erste Element herunterleden

    except :
        #print ('Failed to download FTP file: %s' %(takefile))
        ftp.close()

ftp.quit()


stdout_encoding = sys.stdout.encoding or sys.getfilesystemencoding

sourcepathf = '/home/dwd/filelist/'
targetpath = '/home/weewx/dwd/'
# ********************************************************************
myfile = open(sourcepathf + 'dwd_wa.txt', 'r')

newfile = ''
for line in myfile:
    line = line.replace(chr(1), ' ')   # Steuerzeichen SOH aus Textanfang entfernen
    line = line.replace(chr(3), ' ')   # Steuerzeichen ETX aus Textende entfernen
    line = line.decode("windows-1252")
    line = line.encode("utf-8")
    line = line[21:]
    line = line.replace(chr(13), '<br />')
    newfile = newfile + line
myfile.close()

outfile = open(targetpath + 'dwd_30.txt',  "w")
outfile.write('#encoding UTF-8')
outfile.write( '\n' )
outfile.write(newfile)
outfile.write( "\nQuelle: Deutscher Wetterdienst\n" )
outfile.close()

quit()

# ende
