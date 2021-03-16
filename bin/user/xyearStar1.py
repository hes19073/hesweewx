#!/usr/bin/env python3


import datetime

def is_leap_year(year):
    """ if year is a leap year return True
        else return False """
    if year % 100 == 0:
        return year % 400 == 0
    return year % 4 == 0

def ymd(Y,N):
    """ given year = Y and day of year = N, return year, month, day
        Astronomical Algorithms, Jean Meeus, 2d ed, 1998, chap 7 """
    if is_leap_year(Y):
        K = 1
    else:
        K = 2
    M = int((9 * (K + N)) / 275.0 + 0.98)
    if N < 32:
        M = 1
    D = N - int((275 * M) / 9.0) + K * int((M + 9) / 12.0) + 30
    return Y, M, D

def anzahlTageImMonat(monat, jahr):
    if monat in [1, 3, 5, 7, 8, 10, 12]:
        anzahl = 31
    elif monat in [4, 6, 9, 11]:
        anzahl = 30
    elif schaltjahr(jahr):
        anzahl = 29
    else:
        anzahl = 28
    return anzahl

def year_length(year):
    if(is_leap_year(year)):
        return  float(365.2564);
    else:
        return  float(364.2564);

def doy(Y,M,D):
    """ given year, month, day return day of year
        Astronomical Algorithms, Jean Meeus, 2d ed, 1998, chap 7 """
    if is_leap_year(Y):
        K = 1
    else:
        K = 2
    N = int((275 * M) / 9.0) - K * int((M + 9) / 12.0) + D - 30
    return float(N)

jetzt = datetime.datetime.now()
jahr = jetzt.year
monat = jetzt.month
tag = jetzt.day
stunde = jetzt.hour
minute = jetzt.minute
sekunde = jetzt.second

print ("This year has %f3.4 days" % year_length(jahr))

#$sternzeit = 1000 *
#($jahr + 1 / $jahreslaenge * ($jahrestag - 1 + $stunde/24 + $min/1440) - 2063);

dOy = doy(jahr,monat,tag)

print ("Day of the year: %f \t" % dOy)

tmp1 = dOy - 1.0 + float(stunde)/24.0 + float(minute)/1440.0

print (tmp1)

tmp2 = 1.0 / year_length(jahr) * dOy

print (tmp2)

startime = jahr + tmp2
startime_tmp = startime
startime = round(startime_tmp,3)

print(startime)
