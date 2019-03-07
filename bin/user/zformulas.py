# coding=utf-8
#
#    Copyright (c) 2016-2017 Hartmut Schweidler
#    Original by Tom Keffer <tkeffer@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#    zformulas.py for weewx

""" Various weather related formulas and utilities.
    weewx module that provides greenDaySum greenDay Time
    also airdensity and so on for new Cals

    ano = datetime.fromtimestamp(dt - 1).year

    data['airdensity'] = user.zformulas.greenDaySum(event.record['outTemp'], event.record['dateTime'])
    data['outTempDay'], data['outTempNight'] = user.zformulars.daynighttemps(event.record['outTemp'], event.record['dateTime'])

    import datetime
    d1 = datetime.date(2008, 3, 12)
    print 'd1:', d1

    d2 = d1.replace(year=2009)
    print 'd2:', d2

    greenDaySum count    tavgS
    greenDay Date        tavg_ts
    coolS count
    warmS count

"""

import sys
import re

import math
import syslog
import time
import ephem
import weewx.uwxutils
import weedb
import weewx
import weewx.engine
import weewx.manager
import weewx.wxformulas
import weeutil.weeutil


from math import sin
from datetime import datetime


INHG_PER_MBAR = 0.0295299830714
METER_PER_FOOT = 0.3048
METER_PER_MILE = 1609.34
MM_PER_INCH = 25.4


def CtoK(x):
    return x + 273.15

def CtoF(x):
    return x * 1.8 + 32.0

def FtoC(x):
    return (x - 32.0) * 5.0 / 9.0

def mps_to_mph(x):
    return x * 3600.0 / METER_PER_MILE

def kph_to_mph(x):
    return x * 1000.0 / METER_PER_MILE

def degtorad(x):
    return x * math.pi / 180.0


def calc_warmSum(self, t_C, dt):
    """ Calculate warmSum

    warm sum is Temp from 01.06.year to 31.08.year
    if outTemp.avg > 20.0
       then from 01.06. to 31.08
       sum = +(outTemp.avg)
    """

    _warmS = []

    # Get year for today
    ano = datetime.fromtimestamp(dt - 1).year

    jun_ano = datetime(ano, 6, 1)
    auge_ano = datetime(ano, 8, 31)

    jun_ano_ts = time.mktime(jun_ano.timetuple())
    auge_ano_ts = time.mktime(auge_ano.timetuple())

    db_manager = self.engine.db_binder.get_manager(data_binding='wx_binding', initialize=True)
    try:
        for tspan in weeutil.weeutil.genDaySpans(jun_ano_ts, auge_ano_ts):
            _row = db_manager.getSql("SELECT dateTime,wsum,sumtime FROM archive_day_outTemp WHERE dateTime>? AND dateTime<=?", (tspan.start, tspan.stop))
            if _row is None or _row[1] is None or _row[2] is None:
                continue

            _warmS.append(_row[1] / _row[2])

        warmS = sum(i for i in _warmS if i > 20.0)

    except weedb.DatabaseError:
        pass

    return warmS


def calc_coolSum(self, t_C, dt):
    """ Calculate coolSum

    cool sum is outTemp from 01.11.year-1 to 31.03.year
    if outTemp.avg < 0.0
       then from 01.11.year-1 to 31.03.year
       sum = +outTemp.avg
    """

    ano = datetime.fromtimestamp(dt - 1).year
    anomo = datetime.fromtimestamp(dt - 1).month

    if anomo < 11:
        maee_ano = datetime(ano, 3, 31)
        nov_ano = datetime(ano-1, 11, 1)
    else:
        maee_ano = datetime.fromtimestamp(dt - 1)
        nov_ano = datetime(ano, 11, 1)

    maee_ano_ts = time.mktime(maee_ano.timetuple())
    nov_ano_ts = time.mktime(nov_ano.timetuple())

    _cooS = []

    db_manager = self.engine.db_binder.get_manager(data_binding='wx_binding', initialize=True)
    try:
        for tspan in weeutil.weeutil.genDaySpans(nov_ano_ts,  maee_ano_ts):
            _row = db_manager.getSql("SELECT dateTime,wsum,sumtime FROM archive_day_outTemp WHERE dateTime>? AND dateTime<=?", (tspan.start, tspan.stop))
            if _row is None or _row[1] is None or _row[2] is None:
               continue

            _cooS.append(_row[1] / _row[2])

        coolS = sum(i for i in _cooS if i < 0.0)
        coolS = abs(coolS)

    except weedb.DatabaseError:
        pass

    return coolS


def calc_greenDaySum(self, t_C, dt):
    """ Calculate greenDaySum and greenDay

    green Day Sum Temp from 01.01.year to 31.04.year
    if outTemp.avg > 0.0
       then from 01.01. to 31.01
       sum = +(outTemp.avg * 0.5)
            from 01.02 to end of Feb
       sum = +(outTemp.avg * 0.75)
            from 01.03. to 31.04
       sum = +outTemp.avg
    if sum > 200.0 then greenDay = current.datetime
    """

    # get year for today
    ano = datetime.fromtimestamp(dt - 1).year

    jan_ano = datetime(ano, 1, 1)
    feb_ano = datetime(ano, 2, 1)
    mae_ano = datetime(ano, 3, 1)
    maee_ano = datetime(ano, 3, 31)

    jan_ano_ts = time.mktime(jan_ano.timetuple())
    feb_ano_ts = time.mktime(feb_ano.timetuple())
    jane_ano_ts = feb_ano_ts - 86400
    mae_ano_ts = time.mktime(mae_ano.timetuple())
    febe_ano_ts = mae_ano_ts - 86400
    maee_ano_ts = time.mktime(maee_ano.timetuple())

    _tavg = []
    tavgS = 0.0
    tavg0 = 0.0
    tavg_ts = None

    db_manager = self.engine.db_binder.get_manager(data_binding='wx_binding', initialize=True)
    try:
        for tspan in weeutil.weeutil.genDaySpans(jan_ano_ts, jane_ano_ts):
            _row = db_manager.getSql("SELECT dateTime,wsum,sumtime FROM archive_day_outTemp WHERE dateTime>? AND dateTime<=?", (tspan.start, tspan.stop))
            if _row is None or _row[1] is None or _row[2] is None:
                continue

            _tavg.append(_row[1] / _row[2])
            tavg0 = _row[1] / _row[2]
            if tavg0 > 0.0:
                tavg0 = tavg0 * 0.5
                tavgS = tavgS + tavg0
                if tavgS >= 200.0 and tavg_ts is None:
                    tavg_ts = _row[0]

        for tspan in weeutil.weeutil.genDaySpans(feb_ano_ts, febe_ano_ts):
            _row = db_manager.getSql("SELECT dateTime,wsum,sumtime FROM archive_day_outTemp WHERE dateTime>? AND dateTime<=?", (tspan.start, tspan.stop))
            if _row is None or _row[1] is None or _row[2] is None:
                continue

            _tavg.append(_row[1] / _row[2])
            tavg0 = _row[1] / _row[2]
            if tavg0 > 0.0:
                tavg0 = tavg0 * 0.75
                tavgS = tavgS + tavg0
                if tavgS >= 200.0 and tavg_ts is None:
                    tavg_ts = _row[0]

        for tspan in weeutil.weeutil.genDaySpans(mae_ano_ts, maie_ano_ts):
            _row = db_manager.getSql("SELECT dateTime,wsum,sumtime FROM archive_day_outTemp WHERE dateTime>? AND dateTime<=?", (tspan.start, tspan.stop))
            if _row is None or _row[1] is None or _row[2] is None:
                continue

            _tavg.append(_row[1] / _row[2])
            tavg0 = _row[1] / _row[2]
            if tavg0 > 0.0:
                tavgS = tavgS + tavg0
                if tavgS >= 200.0 and tavg_ts is None:
                   tavg_ts = _row[0]

    except weedb.DatabaseError:
        pass

    return tavgS, tavg_ts


def density_Metric(dp_C, t_C, p_mbar):
    """Calculate the Air density in in kg per m3

    dp_C - dewpoint in degree Celsius

    t_C - temperature in degree Celsius

    p_mbar - pressure in hPa or mbar
    """

    if dp_C is None or t_C is None or p_mbar is None:
        return None

    dp = dp_C
    Tk = (t_C) + 273.15
    p = (0.99999683 + dp * (-0.90826951E-2 + dp * (0.78736169E-4 +
        dp * (-0.61117958E-6 + dp * (0.43884187E-8 +
        dp * (-0.29883885E-10 + dp * (0.21874425E-12 +
        dp * (-0.17892321E-14 + dp * (0.11112018E-16 +
        dp * (-0.30994571E-19))))))))))
    Pv = 100 * 6.1078 / (p**8)
    Pd = p_mbar * 100 - Pv
    density = round((Pd / (287.05 * Tk)) + (Pv / (461.495 * Tk)), 3)

    return density

def density_US(dp_F, t_F, p_inHg):
    """Calculate the Air Density in kg per m3

    dp_F - dewpoint in degree Fahrenheit

    t_F - temperature in degree Fahrenheit

    p_inHg - pressure in inHg

    calculation airdensity_Metric(dp_C, t_C, p_mbar)
    """

    if dp_F is None or t_F is None or p_inHg is None:
        return None

    t_C = FtoC(t_F)
    dp_C = FtoC(dp_F)
    p_mbar = p_inHg / INHG_PER_MBAR
    aden_C = density_Metric(dp_C, t_C, p_mbar)

    return aden_C if aden_C is not None else None

def winddruck_Metric(dp_C, t_C, p_mbar, vms):
    """Calculate the windDruck in N per m2

    dp_C - dewpoint in degree Celsius

    t_C - temperature in degree Celsius

    p_mbar - pressure in hPa or mbar

    vms - windSpeed in m per second

    wd = cp * airdensity / 2 * vms2
    wd - winddruck
    cp - Druckbeiwert (dimensionslos) = 1
    """

    if dp_C is None or t_C is None or p_mbar is None or vms is None:
        return None

    dp = dp_C
    Tk = t_C + 273.15

    if vms < 1:
        vms = 0.2
    elif vms < 6:
        vms = 1.5
    elif vms < 12:
        vms = 3.3
    elif vms < 20:
        vms = 5.4
    elif vms < 29:
        vms = 7.9
    elif vms < 39:
        vms = 10.7
    elif vms < 50:
        vms = 13.8
    elif vms < 62:
        vms = 17.1
    elif vms < 75:
        vms = 20.7
    elif vms < 89:
        vms = 24.7
    elif vms < 103:
        vms = 28.5
    elif vms < 117:
        vms = 32.7
    elif vms >= 117:
        vms = vms * 0.277777778


    p = (0.99999683 + dp * (-0.90826951E-2 + dp * (0.78736169E-4 +
        dp * (-0.61117958E-6 + dp * (0.43884187E-8 +
        dp * (-0.29883885E-10 + dp * (0.21874425E-12 +
        dp * (-0.17892321E-14 + dp * (0.11112018E-16 +
        dp * (-0.30994571E-19))))))))))

    Pv = 100 * 6.1078 / (p**8)
    Pd = p_mbar * 100 - Pv
    densi = round((Pd / (287.05 * Tk)) + (Pv / (461.495 * Tk)), 3)

    wsms2 = vms * vms

    winddruck = densi / 2 * wsms2

    return winddruck


def winddruck_US(dp_F, t_F, p_inHg, ws_mph):
    """Calculate the Winddruck in N per m2

    dp_F - dewpoint in degree Fahrenheit
    t_F - temperature in degree Fahrenheit
    p_inHg - pressure in inHg
    ws_mph - windSpeed in mile per hour

    """
    if dp_F is None or t_F is None or p_inHg is None or ws_mph is None:
        return None

    t_C = FtoC(t_F)
    dp_C = FtoC(dp_F)
    p_mbar = p_inHg / INHG_PER_MBAR
    vms = ws_mph * METER_PER_MILE / 3600.0

    wdru_C = winddruck_Metric(dp_C, t_C, p_mbar, vms)

    return wdru_C if wdru_C is not None else None

def wetbulb_Metric(t_C, RH, PP):
    #  Wet bulb calculations == Kuehlgrenztemperatur, Feuchtekugeltemperatur
    #  t_C = outTemp
    #  RH = outHumidity
    #  PP = pressure

    if t_C is None or RH is None or PP is None:
         return None

    Tdc = ((t_C - (14.55 + 0.114 * t_C) * (1 - (0.01 * RH)) - ((2.5 + 0.007 * t_C) * (1 - (0.01 * RH))) ** 3 - (15.9 + 0.117 * t_C) * (1 - (0.01 * RH)) ** 14))
    E = (6.11 * 10 ** (7.5 * Tdc / (237.7 + Tdc)))
    WBc = (((0.00066 * PP) * t_C) + ((4098 * E) / ((Tdc + 237.7) ** 2) * Tdc)) / ((0.00066 * PP) + (4098 * E) / ((Tdc + 237.7) ** 2))

    return WBc if WBc is not None else None


def wetbulb_US(t_F, RH, p_inHg):
    #  Wet bulb calculations == Kuehlgrenztemperatur, Feuchtekugeltemperatur
    #  t_F = temperatur degree F
    #  RH = outHumidity
    #  p_inHg = pressure in inHg

    if t_F is None or RH is None or p_inHg is None:
         return None

    t_C = FtoC(t_F)
    p_mbar = p_inHg / INHG_PER_MBAR
    wb_C = wetbulb_Metric(t_C, RH, p_mbar)

    return CtoF(wb_C) if wb_C is not None else None

def cbindex_Metric(t_C, RH):
    # Chandler Burning Index calculations
    #  t_C = outTemp
    #  RH = outHumidity

    if t_C is None or RH is None:
         return None

    cdIn = ((((110 - 1.373 * RH) - 0.54 * (10.20 - t_C)) * (124 * 10**(-0.0142 * RH)))/60.1)
    cbIndex = round(cdIn, 1)

    return cbIndex if cbIndex is not None else None

def cbindex_US(t_F, RH):
    # Chandler Burning Index calculations
    #  t_F = temperatur degree F
    #  RH = outHumidity

    if t_F is None or RH is None:
         return None

    t_C = FtoC(t_F)
    cbI_x = cbindex_Metric(t_C, RH)

    return cbI_x if cbI_x is not None else None

def sunhes(rahes, tihes):
    # sunshine nach radiation und dateTime
    # rahes = radiation
    # tihes = dateTime
    if rahes is None or tihes is None:
         return None

    loc = ephem.Observer()
    loc.lon = '11.341407'
    loc.lat = '53.605963'
    loc.pressure = 0
    loc.date = datetime.utcfromtimestamp(tihes)
    s = ephem.Sun()
    s.compute(loc)
    gS = s.alt

    pR = 1373 * sin(gS) * 0.4

    if rahes is not None and gS > 0.104719755 and rahes > pR:
        sunshineS = 300
    else:
        sunshineS = 0.0

    return sunshineS

def absF_C(t_C, RH):

    # t_C is outTemp in C
    # RH is outHumidity in %
    # RG = 8314.3 J/(kmol * K)
    # mw = 18.016 kg/ kmol
    # return AF absolute Feuchte in Wasserdampf pro m3 Luft

    if t_C is None or RH is None:
        return None

    if t_C >= 0.0:
        a = 7.5
        b = 237.3
    else:
        a = 7.6
        b = 240.7

    # bei Temp unter Null und ueber Eis,    a = 9.5  b = 265.5
    # bei Temp unter Null und ueber Wasser, a = 7.6 and b = 240.7

    mw = 18.016
    RG = 8314.3

    sdd_1 = (a * t_C)/(b + t_C)
    sdd = 6.1078 * pow(10, sdd_1)
    dd = RH/100 * sdd
    dd1 = dd / 6.1078
    AF = 100000 * mw/RG * dd / (t_C + 273.15)

    return AF

def absF_F(t_F, RH):
    # absolut Humidity
    #  t_F = temperatur degree F
    #  RH = outHumidity

    if t_F is None or RH is None:
         return None

    t_C = FtoC(t_F)
    absF_x = absF_C(t_C, RH)

    return absF_x if absF_x is not None else None

def dampfD_C(t_C):

    # t_C is outTemp in degree C

    if t_C is None:
        return None

    """ueber Wasser t_C -45 C bis 60 C
       ddM_C = 6.112 * math.exp(17.62 * t_C / (243.12 + t_C))
       ueber Eis t_C -65 C bis 0.01 C
       ddM_C = 6.112 * math.exp(22.46 * t_C / (272.62 + t_C))
    """

    if t_C < 0.0:
        dd_C = 6.112 * math.exp(22.46 * t_C / (272.62 + t_C))

    else:
        dd_C = 6.112 * math.exp(17.62 * t_C / (243.12 + t_C))

    return dd_C if dd_C is not None else None

def dampfD_F(t_F):

    #  t_F = temperatur degree F

    if t_F is None:
         return None

    t_C = FtoC(t_F)
    dd_C = dampfD_C(t_C)

    return (dd_C * INHG_PER_MBAR) if (dd_C * INHG_PER_MBAR) is not None else None

def sumsimIndex_F(t_F, RH):
    # Summer Simmer Index-Berechnung
    # rel. Luftfeuchte RH
    # temperatur in degree F

    if t_F is None or RH is None:
         return None

    ssI_F = 1.98 * (t_F - (0.55 - 0.0055 * RH) * (t_F - 58)) - 56.83

    return ssI_F if ssI_F is not None else None

def sumsimIndex_C(t_C, RH):
    # Summer Simmer Index-Berechnung
    # rel. Luftfeuchte RH
    # temperatur in degree C

    if t_C is None or RH is None:
        return None

    t_F = CtoF(t_C)

    ssI_F = sumsimIndex_F(t_F, RH)

    ssI_C = FtoC(ssI_F)

    return ssI_C if ssI_C is not None else None


def gddx_C(Tmax, Tmin, xx):
    # Tmax outTemp_max,
    # Tmin outTemp_min,
    # xx BasisTemp 4, 6, 10
    if Tmax is None or Tmin is None:
        return None

    if Tmin < 10.0:
        if Tmax < 30.0:
            if Tmax < 10.0:
                gddx = 0.0
            else:
                gddx = (Tmax + xx) / 2.0 - xx
        else:
            gddx = 20.0

    else:
        if Tmax < 30.0:
            gddx = (Tmax + Tmin) / 2.0 - xx
        else:
            gddx = 20.0

    return gddx if gddx is not None else None


def gddx_F(Tmax, Tmin, xx):

    Tmax_F = CtoF(Tmax)
    Tmin_F = CtoF(Tmin)
    xx_F = CtoF(xx)

    gddxC = gddx_C(Tmax_F, Tmin_F, xx_F)

    gddx_F = CtoF(gddxC) 

    return gddx_F


def da_Metric(t_C, p_mbar):
    # Density altitude calculations
    #  t_C = outTemp
    #  p_mbar =  pressure

    if t_C is None or p_mbar is None:
         return None

    t_F = CtoF(t_C)
    p_inHg = p_mbar * INHG_PER_MBAR
    da_fo = da_US(t_F, p_inHg)

    da_me = da_fo * 0.3048

    return da_me if da_me is not None else None

def da_US(t_F, p_inHg):
    #  Density altitude calculations
    #  t_F = temperatur degree F
    #  p_inHg = pressure

    if t_F is None or p_inHg is None:
         return None

    daIn = 145442.16 * (1 - (((17.326 * p_inHg) / (459.67 + t_F)) ** 0.235))
    daI_x = round(daIn, 1)

    return daI_x if daI_x is not None else None

if __name__ == "__main__":
    
    import doctest

    if not doctest.testmod().failed:
        print("PASSED")
