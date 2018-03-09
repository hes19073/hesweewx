#! /usr/bin/env python
# -*- coding: utf-8 -*-

#*********************************************************************
# Connect DWD HTTP Server and download Warnlagen
# Autor : Hartmut Schweidler
# Date  : 30.12.2017
#*********************************************************************
# Server : http://opendata.dwd.de
# Interpreter : python 2.7
#*********************************************************************
# Versionsnummer ausgeben
version = "0.8"

#*********************************************************************
# imported libraries
import fnmatch                          # match names
import ftplib                           # ftp connect
import os, sys
import locale
import codecs

#*********************************************************************
# FTP Server Parameter
#*********************************************************************
ftpserver = 'opendata.dwd.de'    # Server
ftpuser = 'anonymous'
ftppw = 'anonymous@'

ftppath = '/weather/text_forecasts/txt/'

filepath = "/home/dwd/filelist/"               # Linux
filelisttxt = filepath + 'dwd_fo10.txt'

ftp = ftplib.FTP(ftpserver, ftpuser, ftppw)

ftp.cwd(ftppath)                             #changing to forecasts

#*********************************************************************
# Read filelist 10 Tage Forecast Deutschland
#*********************************************************************
filelist = []                                     # list for filenames
ftp.cwd(ftppath)                                  # changing to directory
line = ftp.retrlines("NLST",filelist.append)      # read filenames and write into list of files
filelist = sorted(filelist,reverse=True)          # Absteigende Sortierung der Namen

#*********************************************************************
# Create textfile with filenames  Forecast - 10 Tage Deutschland
#*********************************************************************

myfile = open(filelisttxt,'w')

for item in filelist:
    if fnmatch.fnmatch(item, 'ber01-VHDL17_DWOG*'):         # VHDL17_DWOG  filter 
        myfile.write(item+"\n")

myfile.close()

#*********************************************************************
# Download textfile with filenames from saved filelist.file  
# 10 Tage fuer Deutschland VHDL17_DWOG
#*********************************************************************
myfile = open(filelisttxt,'r')
inlist = myfile.readlines()              # Using .readlines()

filelistfile =  []

for i in inlist:
    filelistfile.append(i.rstrip('\n'))  # Das Zeichen \n entfernen

myfile.close()

ftp.cwd(ftppath) 

for takefile in filelistfile: 
    try: 
       if fnmatch.fnmatch(takefile, '*'):

        ftp.retrlines('RETR '+takefile, open('/home/dwd/filelist/dwd_10.txt', 'wb').write)
        break                          # nur ein element
        
    except :
        #print ('Failed to download FTP file: %s' %(takefile)) 
        ftp.close() 


ftp.quit()


stdout_encoding = sys.stdout.encoding or sys.getfilesystemencoding

sourcepathf = '/home/dwd/filelist/'
targetpath = '/home/weewx/dwd/'
# ********************************************************************
myfile = open(sourcepathf + 'dwd_10.txt', 'r')

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

outfile = open(targetpath + 'dwd_10.txt',  "w")
outfile.write('#encoding UTF-8')
outfile.write( '\n' )
outfile.write(newfile)
outfile.close()

quit()
#Ende des Program
