#!/usr/bin/python

import sys
import subprocess

from subprocess import Popen, PIPE

import time
import threading
import signal
import Queue
import os.path
import syslog
#import Adafruit_BMP.BMP085 as BMP085
import getopt

# Class begin ========================
class AsynchronousFileReader(threading.Thread):
    #
    #Helper class to implement asynchronous reading of a file
    #in a separate thread. Pushes read lines on a queue to
    #be consumed in another thread.
    #
    def __init__(self, fd, queue):
        assert isinstance(queue, Queue.Queue)
        assert callable(fd.readline)
        threading.Thread.__init__(self)
        self._fd = fd
        self._queue = queue

    def run(self):
        #The body of the tread: read lines and put them on the queue.'''
        for line in iter(self._fd.readline, ''):
            self._queue.put(line)

    def eof(self):
        #Check whether there is no more content to expect.'''
        return not self.is_alive() and self._queue.empty()
# End Class ===========================
#
# Print routine when debugflag is set, to log and/or to screen when tty is used
def printdebug(str):
    global debug
    if len(str)==0:
    	return
    if debug:
        if sys.stdout.isatty():
            print (str)
        syslog.syslog(str)
    return
    
# Get BMP180 data
#def get_bmp180():
#    global data
#    data['barometer']= str(float(sensor.read_pressure()/100))
#    data['altimeter']= str(int( sensor.read_altitude()))
#    data['pressure'] = str(float(sensor.read_sealevel_pressure()/100))

# Print data[]
def print_data():
    global rain
    global rainnew
    global data
    global datafile
    missed=""
    #set rainfall since begin interval
    if rainnew<>"":
    	data["rain"]=str(float(rain)-float(rain))
    	printdebug( "Updated: rain "+rainnew+" - "+rain+" = "+ data['rain'])
    	rain=rainnew
    	rainnew=""    	
    #now get latest BMP180 data
    #get_bmp180()
    #if debug also show what data has no readings
    if debug==1:#if debugging also write out what data is not received
        for x in data:
            if data[x]=="":
                missed= missed+" "+str(x)
        if missed=="":
            missed=" None"
        printdebug("Missed sensors:"+missed)
    
    printdebug( "Open exportfile: " +datafile)
    fo = open(datafile, "wb+")    
    fo.write("Date="+ str(int(time.time()))+"\n")
    printdebug("Date=" + str(int(time.time())))
    fo.write("usUnits=17"+"\n") 
    printdebug("usUnits=17")
    for x in data:
        if data[x]<>"":
            vdata= str(x)+"="+data[x]+"\n"
            fo.write(vdata)
            printdebug(vdata.rstrip())
            data[x]=""
    printdebug( "Close file: " +datafile)
    fo.close()
#       
# PROCESS DATA ========================
#
 
def process_data(msg):
    global data
    global rain
    global rainnew
    msg=msg.rstrip()#first strip off cr/lf
    printdebug ("Process: "+msg)
    sline=msg.split()
    #AlectoV1 Wind Sensor 43: Wind speed 0 units = 0.00 m/s: Wind gust 0 units = 0.00 m/s: Direction 90 degrees: Battery OK
    if 'Fine Offset WH1080 weather station' in msg:
    	
        device=sline[5]
        device=device.rstrip(':')
        data['windDir']=sline[21]
        data['windSpeed']=sline[11]
        data['windGust']=sline[18]
        printdebug( "Updated: windDir windSpeed windGust: "+ data['windDir']+" "+  data['windSpeed']+" "+  data['windGust'] )

    if 'Fine Offset WH1080 weather station' in msg:
                #2015-07-02 06:37:34 LaCrosse TX Sensor 3c: Temperature 20.0 C / 68.0 F
                #2015-07-02 12:22:37 LaCrosse TX Sensor 3f: Humidity 58.0%
                device=sline[5]
                device=device.rstrip(':')
                d_data=sline[7]
                d_data=d_data.rstrip('%')
                printdebug ("Detected LaCrosse TX Sensor "+d_data)
                #sensordata = (device,sline[6],d_data,'')
                if device=="3f" and sline[6]=='Temperature':
                    data['outTemp']=d_data
                    printdebug( "Updated: outTemp: "+ data['outTemp'])
                if device=="7e" and sline[6]=='Temperature':
                    data['inTemp']=d_data
                    printdebug( "Updated: inTemp: "+ data['inTemp'])
                if device=="3f" and sline[6]=='Humidity':
                    data['outHumidity']=d_data
                    printdebug( "Updated: outHum: "+ data['outHumidity'])
	#3f buiten 7e binnen hum temp
    if 'AlectoV1 Sensor' in msg:
        #2015-07-02 12:56:37 AlectoV1 Sensor 43 Channel 1: Temperature 29.3 C: Humidity 49 : Battery OK    
        device=sline[4]
        device=device.rstrip(':')
        printdebug("Detected AlectoV1 Sensor")
        if device== "43" and sline[7]=='Temperature':#zolder
            data["extraTemp1"]=sline[8]
            printdebug( "Updated: extraTemp1: "+ data['extraTemp1'])
        if device== "43" and sline[10]=='Humidity':#zolder
            data["extraHumid1"]=sline[11]
            printdebug( "Updated: extraHumid1: "+ data['extraHumid1'])
        if device== "247" and sline[7]=='Temperature':#kelder
            data["extraTemp2"]=sline[8]
            printdebug( "Updated: extraTemp2: "+ data['extraTemp2'])
        if device== "247" and sline[10]=='Humidity':#kelder
            data["extraHumid2"]=sline[11]
            printdebug( "Updated: extraHumid2: "+ data['extraHumid2'] )
    if 'Fine Offset WH1080 weather station' in msg:
        #2015-07-02 12:23:42 AlectoV1 Rain Sensor 133: Rain 0.00 mm/m2: Battery OK
        # mm per unit (update interval)needs to be calculated 
        printdebug ("Detected Rain sensor")
        device=sline[5]
        device=device.rstrip(':')
        if rain=="": #initial setting. measurements compared to last measurement
        	rain=sline[7]
        	printdebug ("Updated: Set inital counter to: "+rain+" mm")
    
        else:
        	rainnew=sline[7]
        	printdebug ("Updated: Rainvalue: "+ rainnew)
    
#====================================
#End data handler
#
def signal_handler(signal, frame):
        global process
        os.kill(process.pid, 9)#signal.SIGUSR1)
        # sys.exit(0)
        #Continue exit process main loop

#============================================
if __name__ == '__main__':
    #capture control-c and kill signal
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    datafile="/home/weewx/datafile"#export file to write
    interval_write_datafile=120# write file each 60 secs
    rain=""#holds last evaluated level
    rainnew=""#holds last transmitted level
    frequency="433920000"
    debug=0
    #get options
    try:
      opts, args = getopt.getopt(sys.argv[1:],"do:f:",["debug","ofile=","frequency="])
    except getopt.GetoptError:
      print 'Usage: -d or --debug, -o <outputfile> --ofile <outputfile> -f <frequency> --frequency <frequency>'
      sys.exit(2)
    for opt, arg in opts:
        if opt in("-d","--debug"):
            debug=1
        elif opt in ("-o", "--ofile"):
         datafile = arg
        elif opt in ("-f", "--frequency"):
         frequency = arg
    
    #
    printtime=time.time()
    exportdata=1
    #sensor = BMP085.BMP085()
    command=["/home/rtl_433/src/rtl_433","-R 32","-f"+frequency]
    if sys.stdout.isatty():
        print("Started on console. Sending info to terminal session")
    else:
        syslog.syslog("Started as daemon. No output send to stdout")
    syslog.syslog("Frequency: "+frequency)
    if debug:
    	syslog.syslog("Debug: ON")
    else:
    	syslog.syslog("Debug: off")
    
    data={'outTemp':"", 'inTemp':"", 'outHumidity':"", 'rain':"", 'extraHumid1':"", 'extraTemp1':"", 'windDir':"", 'windGust':"", 'windSpeed':"", 'altimeter':"", 'barometer':"", 'pressure':"", 'extraHumid2':"", 'extraTemp2':""}
    
    process = subprocess.Popen(command, stdout=subprocess.PIPE, preexec_fn=os.setsid)
    # Launch the asynchronous readers of the process' stdout and stderr.
    stdout_queue = Queue.Queue()
    stdout_reader = AsynchronousFileReader(process.stdout, stdout_queue)
    stdout_reader.start()
    #main queue loop
    # Check the queues if we received some output (until there is nothing more to get).
    while not stdout_reader.eof():
        # Show what we received from standard output.
        while not stdout_queue.empty():
            process_data(stdout_queue.get())    
        # Sleep a bit before asking the readers again.
        time.sleep(.1)
        if (time.time()-printtime)>interval_write_datafile:
            #print(int(time.time()-printtime))
            print_data()
            printtime=time.time()
    # end main loop
    #
    syslog.syslog("Normal exitchain")
    # Let's be tidy and join the threads we've started.
    stdout_reader.join()
    # Close subprocess' file descriptors.
    process.stdout.close()
    syslog.syslog("Exit program")

