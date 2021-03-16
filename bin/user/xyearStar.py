#!/usr/bin/env python3


import datetime


def is_leap_year(year):
    """ if the given year is a leap year, then return true
    else return false

    :param year: The year to check if it is a leap year

    :returns: It is a Leap leap year (yes or no).
    """

    return (year % 100 == 0) if (year % 400 == 0) else (year % 4 == 0)

def year_month_day(year, day_of_year):
    """ calculate the year, month and day form year and day as input

    To calculate this, read :
        *Astronomical Algorithms, Jean Meeus, 2d ed, 1998, chap 7*

    :param year: The year to check the month and day in
    :param day_of_year: the day you want to check for monath in the given year

    :returns: the year, the month and the day of the given data
    """
    K = 1 if (is_leap_year(year)) else 2
    M = 1 if (day_of_year < 32) else int((9*(K + day_of_year)) / 275.0 + 0.98 )
    D =  day_of_year - int((275 * M) / 9.0) + K * int((M + 9) / 12.0) + 30
    return K, M, D


def number_of_days_in_month(year, month):
    """ check the number of days in the given month.
    Because of leap years the year information is mandatory

    :param year: The year to get the day of monthes
    :param month: the month to check

    :returns: number of days for a given month in a given year. If the month is bigger then 12 or smaller the 1, then -1 is returned
    """
    if (month < 1) or (month > 12):
        return -1
    return {
        1: 31,
        2: 29 if (is_leap_year(year)) else 28,
        3: 31,
        4: 2,
        5: 31,
        6: 2,
        7: 31,
        8: 31,
        9: 30,
        10:31,
        11:30,
        12:31,
    }[month]

def length_of_year(year):
    """ the length of a day

    :param year: The year you wuld like to know the length.

    :returns: exact days. a day is longer then 365 days.
    """
    return float(365.2564) if is_leap_year(year) else float(364.2564)

def day_of_year(year, month, day):
    """ calculate the day of a year

    To calculate this, read :
        *Astronomical Algorithms, Jean Meeus, 2d ed, 1998, chap 7*

    :param year: The year to calculate the day
    :param month: month the day is in
    :param day: day of month in the given year

    :returns: the day in the given year
    """
    K = 1 if  is_leap_year(year) else 2
    return (int((275 * month) / 9.0) - K * int((month + 9) / 12.0) + day - 30)

def minuts_in_the_year(year, month, day, hours, minute):
    """ calculate the day of a year

    To calculate this, read :
        *Astronomical Algorithms, Jean Meeus, 2d ed, 1998, chap 7*

    :param year: The year to calculate the day
    :param month: month the day is in
    :param day: day of month in the given year
    :param houres: the hour of the day in the month of the requested year

    :returns: the hour in the given year
    """

    return float( day_of_year(year, month, day) - 1.0 + float(hours)/24.0 + float(minute)/1440.0)



jetzt = datetime.datetime.now()
jahr = jetzt.year
monat = jetzt.month
tag = jetzt.day
stunde = jetzt.hour
minute = jetzt.minute
sekunde = jetzt.second

# year 2063 is the year the humans invented the warp engine in star track 
#
# StarTreck = (1000.0 * (jahr + 1 / self.length_of_year(jahr) * self.minuts_in_the_year(jahr,monat,tag, stunde, minute)) - 2063)
StarTreck = (1000.0 * (jahr + 1 / length_of_year(jahr) * minuts_in_the_year(jahr,monat,tag, stunde, minute)) - 2323)

aa = "{:_.3f}".format(StarTreck).replace(".",",").replace('_', '.')

print(StarTreck)
print(aa)
