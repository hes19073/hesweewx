#
#    Copyright (c) 2009-2020 Tom Keffer <tkeffer@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

"""Various weather related formulas and utilities."""

from __future__ import absolute_import
from __future__ import print_function

import logging
import collections

import math
import time
import ephem
import weewx.uwxutils
from weeutil.weeutil import TimeSpan
from math import sin
from datetime import datetime

import weewx.units
from weewx.units import CtoK, CtoF, FtoC, mph_to_knot, kph_to_knot, mps_to_knot
from weewx.units import INHG_PER_MBAR, METER_PER_FOOT, METER_PER_MILE, MM_PER_INCH
from weewx.units import ValueTuple, mps_to_mph, kph_to_mph

log = logging.getLogger(__name__)


def dewpointF(T, R):
    """Calculate dew point.

    T: Temperature in Fahrenheit

    R: Relative humidity in percent.

    Returns: Dewpoint in Fahrenheit
    Examples:

    >>> print("%.1f" % dewpointF(68, 50))
    48.7
    >>> print("%.1f" % dewpointF(32, 50))
    15.5
    >>> print("%.1f" % dewpointF(-10, 50))
    -23.5
    """

    if T is None or R is None:
        return None

    TdC = dewpointC(FtoC(T), R)

    return CtoF(TdC) if TdC is not None else None


def dewpointC(T, R):
    """Calculate dew point.
    http://en.wikipedia.org/wiki/Dew_point

    T: Temperature in Celsius

    R: Relative humidity in percent.

    Returns: Dewpoint in Celsius
    """

    if T is None or R is None:
        return None
    R = R / 100.0
    try:
        _gamma = 17.27 * T / (237.7 + T) + math.log(R)
        TdC = 237.7 * _gamma / (17.27 - _gamma)
    except (ValueError, OverflowError):
        TdC = None
    return TdC


def windchillF(T_F, V_mph):
    """Calculate wind chill.
    http://www.nws.noaa.gov/om/cold/wind_chill.shtml

    T_F: Temperature in Fahrenheit

    V_mph: Wind speed in mph

    Returns Wind Chill in Fahrenheit
    """

    if T_F is None or V_mph is None:
        return None

    # only valid for temperatures below 50F and wind speeds over 3.0 mph
    if T_F >= 50.0 or V_mph <= 3.0:
        return T_F

    WcF = 35.74 + 0.6215 * T_F + (-35.75 + 0.4275 * T_F) * math.pow(V_mph, 0.16)
    return WcF


def windchillC(T_C, V_kph):
    """Wind chill, metric version.

    T: Temperature in Celsius

    V: Wind speed in kph

    Returns wind chill in Celsius"""

    if T_C is None or V_kph is None:
        return None

    T_F = CtoF(T_C)
    V_mph = 0.621371192 * V_kph

    WcF = windchillF(T_F, V_mph)

    return FtoC(WcF) if WcF is not None else None


def heatindexF(T, R, algorithm='new'):
    """Calculate heat index.
    https://www.wpc.ncep.noaa.gov/html/heatindex_equation.shtml

    T: Temperature in Fahrenheit

    R: Relative humidity in percent

    Returns heat index in Fahrenheit

    Examples (Expected values obtained from https://www.wpc.ncep.noaa.gov/html/heatindex.shtml):

    >>> print("%0.0f" % heatindexF(75.0, 50.0))
    75
    >>> print("%0.0f" % heatindexF(80.0, 50.0))
    81
    >>> print("%0.0f" % heatindexF(80.0, 95.0))
    88
    >>> print("%0.0f" % heatindexF(90.0, 50.0))
    95
    >>> print("%0.0f" % heatindexF(90.0, 95.0))
    127

    """

    if T is None or R is None:
        return None

    if algorithm == 'new':
        # Formula only valid for temperatures over 40F:
        if T <= 40.0:
            return T

        # Use simplified formula
        hi_F = 0.5 * (T + 61.0 + ((T - 68.0) * 1.2) + (R * 0.094))

        # Apply full formula if the above, averaged with temperature, is greater than 80F:
        if (hi_F + T) / 2.0 >= 80.0:
            hi_F = -42.379 \
                   + 2.04901523 * T \
                   + 10.14333127 * R \
                   - 0.22475541 * T * R \
                   - 6.83783e-3 * T ** 2 \
                   - 5.481717e-2 * R ** 2 \
                   + 1.22874e-3 * T ** 2 * R \
                   + 8.5282e-4 * T * R ** 2 \
                   - 1.99e-6 * T ** 2 * R ** 2
            # Apply an adjustment for low humidities
            if R < 13 and 80 < T < 112:
                adjustment = ((13 - R) / 4.0) * math.sqrt((17 - abs(T - 95.)) / 17.0)
                hi_F -= adjustment
            # Apply an adjustment for high humidities
            elif R > 85 and 80 <= T < 87:
                adjustment = ((R - 85) / 10.0) * ((87 - T) / 5.0)
                hi_F += adjustment
    else:
        # Formula only valid for temperatures 80F or more, and RH 40% or more:
        if T < 80.0 or R < 40.0:
            return T

        hi_F = -42.379 \
               + 2.04901523 * T \
               + 10.14333127 * R \
               - 0.22475541 * T * R \
               - 6.83783e-3 * T ** 2 \
               - 5.481717e-2 * R ** 2 \
               + 1.22874e-3 * T ** 2 * R \
               + 8.5282e-4 * T * R ** 2 \
               - 1.99e-6 * T ** 2 * R ** 2
        if hi_F < T:
            hi_F = T

    return hi_F


def heatindexC(T_C, R, algorithm='new'):
    if T_C is None or R is None:
        return None
    T_F = CtoF(T_C)
    hi_F = heatindexF(T_F, R, algorithm)
    return FtoC(hi_F)


def heating_degrees(t, base):
    return max(base - t, 0) if t is not None else None


def cooling_degrees(t, base):
    return max(t - base, 0) if t is not None else None


def altimeter_pressure_US(SP_inHg, Z_foot, algorithm='aaASOS'):
    """Calculate the altimeter pressure, given the raw, station pressure in inHg and the altitude
    in feet.
        
    Examples:
    >>> print("%.2f" % altimeter_pressure_US(28.0, 0.0))
    28.00
    >>> print("%.2f" % altimeter_pressure_US(28.0, 1000.0))
    29.04
    """
    if SP_inHg is None or Z_foot is None:
        return None
    if SP_inHg <= 0.008859:
        return None
    return weewx.uwxutils.TWxUtilsUS.StationToAltimeter(SP_inHg, Z_foot,
                                                        algorithm=algorithm)


def altimeter_pressure_Metric(SP_mbar, Z_meter, algorithm='aaASOS'):
    """Convert from (uncorrected) station pressure to altitude-corrected
    pressure.

    Examples:
    >>> print("%.1f" % altimeter_pressure_Metric(948.08, 0.0))
    948.2
    >>> print("%.1f" % altimeter_pressure_Metric(948.08, 304.8))
    983.4
    """
    if SP_mbar is None or Z_meter is None:
        return None
    if SP_mbar <= 0.3:
        return None
    return weewx.uwxutils.TWxUtils.StationToAltimeter(SP_mbar, Z_meter,
                                                      algorithm=algorithm)


def _etterm(elev_meter, t_C):
    """Calculate elevation/temperature term for sea level calculation."""
    t_K = CtoK(t_C)
    return math.exp(-elev_meter / (t_K * 29.263))


def sealevel_pressure_Metric(sp_mbar, elev_meter, t_C):
    """Convert station pressure to sea level pressure.  This implementation was copied from wview.

    sp_mbar - station pressure in millibars

    elev_meter - station elevation in meters

    t_C - temperature in degrees Celsius

    bp - sea level pressure (barometer) in millibars
    """
    if sp_mbar is None or elev_meter is None or t_C is None:
        return None
    pt = _etterm(elev_meter, t_C)
    bp_mbar = sp_mbar / pt if pt != 0 else 0
    return bp_mbar


def sealevel_pressure_US(sp_inHg, elev_foot, t_F):
    if sp_inHg is None or elev_foot is None or t_F is None:
        return None
    sp_mbar = sp_inHg / INHG_PER_MBAR
    elev_meter = elev_foot * METER_PER_FOOT
    t_C = FtoC(t_F)
    slp_mbar = sealevel_pressure_Metric(sp_mbar, elev_meter, t_C)
    slp_inHg = slp_mbar * INHG_PER_MBAR
    return slp_inHg


def calculate_delta(newtotal, oldtotal, delta_key='rain'):
    """Calculate the differential given two cumulative measurements."""
    if newtotal is not None and oldtotal is not None:
        if newtotal >= oldtotal:
            delta = newtotal - oldtotal
        else:
            log.info("'%s' counter reset detected: new=%s old=%s", delta_key,
                     newtotal, oldtotal)
            delta = None
    else:
        delta = None
    return delta


# For backwards compatibility:
calculate_rain = calculate_delta
calculate_snow = calculate_delta


def solar_rad_Bras(lat, lon, altitude_m, ts=None, nfac=2):
    """Calculate maximum solar radiation using Bras method
    http://www.ecy.wa.gov/programs/eap/models.html

    lat, lon - latitude and longitude in decimal degrees

    altitude_m - altitude in meters

    ts - timestamp as unix epoch

    nfac - atmospheric turbidity (2=clear, 4-5=smoggy)

    Example:

    >>> for t in range(0,24):
    ...    print("%.2f" % solar_rad_Bras(42, -72, 0, t*3600+1422936471))
    0.00
    0.00
    0.00
    0.00
    0.00
    0.00
    0.00
    0.00
    1.86
    100.81
    248.71
    374.68
    454.90
    478.76
    443.47
    353.23
    220.51
    73.71
    0.00
    0.00
    0.00
    0.00
    0.00
    0.00
    """
    from weewx.almanac import Almanac
    if ts is None:
        ts = time.time()
    sr = 0.0
    try:
        alm = Almanac(ts, lat, lon, altitude_m)
        el = alm.sun.alt  # solar elevation degrees from horizon
        R = alm.sun.earth_distance
        # NREL solar constant W/m^2
        nrel = 1367.0
        # radiation on horizontal surface at top of atmosphere (bras eqn 2.9)
        sinel = math.sin(math.radians(el))
        io = sinel * nrel / (R * R)
        if sinel >= 0:
            # optical air mass (bras eqn 2.22)
            m = 1.0 / (sinel + 0.15 * math.pow(el + 3.885, -1.253))
            # molecular scattering coefficient (bras eqn 2.26)
            a1 = 0.128 - 0.054 * math.log(m) / math.log(10.0)
            # clear-sky radiation at earth surface W / m^2 (bras eqn 2.25)
            sr = io * math.exp(-nfac * a1 * m)
    except (AttributeError, ValueError, OverflowError):
        sr = None
    return sr


def solar_rad_RS(lat, lon, altitude_m, ts=None, atc=0.8):
    """Calculate maximum solar radiation
    Ryan-Stolzenbach, MIT 1972
    http://www.ecy.wa.gov/programs/eap/models.html

    lat, lon - latitude and longitude in decimal degrees

    altitude_m - altitude in meters

    ts - time as unix epoch

    atc - atmospheric transmission coefficient (0.7-0.91)

    Example:

    >>> for t in range(0,24):
    ...    print("%.2f" % solar_rad_RS(42, -72, 0, t*3600+1422936471))
    0.00
    0.00
    0.00
    0.00
    0.00
    0.00
    0.00
    0.00
    0.09
    79.31
    234.77
    369.80
    455.66
    481.15
    443.44
    346.81
    204.64
    52.63
    0.00
    0.00
    0.00
    0.00
    0.00
    0.00
    """
    from weewx.almanac import Almanac
    if atc < 0.7 or atc > 0.91:
        atc = 0.8
    if ts is None:
        ts = time.time()
    sr = 0.0
    try:
        alm = Almanac(ts, lat, lon, altitude_m)
        el = alm.sun.alt  # solar elevation degrees from horizon
        R = alm.sun.earth_distance
        z = altitude_m
        nrel = 1367.0  # NREL solar constant, W/m^2
        sinal = math.sin(math.radians(el))
        if sinal >= 0:  # sun must be above horizon
            rm = math.pow((288.0 - 0.0065 * z) / 288.0, 5.256) \
                 / (sinal + 0.15 * math.pow(el + 3.885, -1.253))
            toa = nrel * sinal / (R * R)
            sr = toa * math.pow(atc, rm)
    except (AttributeError, ValueError, OverflowError):
        sr = None
    return sr


def cloudbase_Metric(t_C, rh, altitude_m):
    """Calculate the cloud base in meters

    t_C - temperature in degrees Celsius

    rh - relative humidity [0-100]

    altitude_m - altitude in meters
    """
    dp_C = dewpointC(t_C, rh)
    if dp_C is None:
        return None
    cb = (t_C - dp_C) * 1000 / 2.5
    return altitude_m + cb * METER_PER_FOOT if cb is not None else None


def cloudbase_US(t_F, rh, altitude_ft):
    """Calculate the cloud base in feet

    t_F - temperature in degrees Fahrenheit

    rh - relative humidity [0-100]

    altitude_ft - altitude in feet
    """
    dp_F = dewpointF(t_F, rh)
    if dp_F is None:
        return None
    cb = altitude_ft + (t_F - dp_F) * 1000.0 / 4.4
    return cb


def humidexC(t_C, rh):
    """Calculate the humidex
    Reference (look under heading "Humidex"):
    http://climate.weather.gc.ca/climate_normals/normals_documentation_e.html?docID=1981

    t_C - temperature in degree Celsius

    rh - relative humidity [0-100]

    Examples:
    >>> print("%.2f" % humidexC(30.0, 80.0))
    43.64
    >>> print("%.2f" % humidexC(30.0, 20.0))
    30.00
    >>> print("%.2f" % humidexC(0, 80.0))
    0.00
    >>> print(humidexC(30.0, None))
    None
    """
    try:
        dp_C = dewpointC(t_C, rh)
        dp_K = CtoK(dp_C)
        e = 6.11 * math.exp(5417.7530 * (1 / 273.16 - 1 / dp_K))
        h = 0.5555 * (e - 10.0)
    except (ValueError, OverflowError, TypeError):
        return None

    return t_C + h if h > 0 else t_C


def humidexF(t_F, rh):
    """Calculate the humidex in degree Fahrenheit

    t_F - temperature in degree Fahrenheit

    rh - relative humidity [0-100]
    """
    if t_F is None:
        return None
    h_C = humidexC(FtoC(t_F), rh)
    return CtoF(h_C) if h_C is not None else None


def apptempC(t_C, rh, ws_mps):
    """Calculate the apparent temperature in degree Celsius

    t_C - temperature in degree Celsius

    rh - relative humidity [0-100]

    ws_mps - wind speed in meters per second

    http://www.bom.gov.au/info/thermal_stress/#atapproximation
      AT = Ta + 0.33*e - 0.70*ws - 4.00
    where
      AT and Ta (air temperature) are deg-C
      e is water vapor pressure
      ws is wind speed (m/s) at elevation of 10 meters
      e = rh / 100 * 6.105 * exp(17.27 * Ta / (237.7 + Ta))
      rh is relative humidity

    http://www.ncdc.noaa.gov/societal-impacts/apparent-temp/
      AT = -2.7 + 1.04*T + 2.0*e -0.65*v
    where
      AT and T (air temperature) are deg-C
      e is vapor pressure in kPa
      v is 10m wind speed in m/sec
    """
    if t_C is None:
        return None
    if rh is None or rh < 0 or rh > 100:
        return None
    if ws_mps is None or ws_mps < 0:
        return None
    try:
        e = (rh / 100.0) * 6.105 * math.exp(17.27 * t_C / (237.7 + t_C))
        at_C = t_C + 0.33 * e - 0.7 * ws_mps - 4.0
    except (ValueError, OverflowError):
        at_C = None
    return at_C


def apptempF(t_F, rh, ws_mph):
    """Calculate apparent temperature in degree Fahrenheit

    t_F - temperature in degree Fahrenheit

    rh - relative humidity [0-100]

    ws_mph - wind speed in miles per hour
    """
    if t_F is None:
        return None
    if rh is None or rh < 0 or rh > 100:
        return None
    if ws_mph is None or ws_mph < 0:
        return None
    t_C = FtoC(t_F)
    ws_mps = ws_mph * METER_PER_MILE / 3600.0
    at_C = apptempC(t_C, rh, ws_mps)
    return CtoF(at_C) if at_C is not None else None


def beaufort(ws_kts):
    """Return the beaufort number given a wind speed in knots"""
    if ws_kts is None:
        return None
    elif ws_kts < 1:
        return 0
    elif ws_kts < 4:
        return 1
    elif ws_kts < 7:
        return 2
    elif ws_kts < 11:
        return 3
    elif ws_kts < 17:
        return 4
    elif ws_kts < 22:
        return 5
    elif ws_kts < 28:
        return 6
    elif ws_kts < 34:
        return 7
    elif ws_kts < 41:
        return 8
    elif ws_kts < 48:
        return 9
    elif ws_kts < 56:
        return 10
    elif ws_kts < 64:
        return 11
    return 12


weewx.units.conversionDict['mile_per_hour']['beaufort'] = lambda x: beaufort(mph_to_knot(x))
weewx.units.conversionDict['knot']['beaufort'] = beaufort
weewx.units.conversionDict['km_per_hour']['beaufort'] = lambda x: beaufort(kph_to_knot(x))
weewx.units.conversionDict['meter_per_second']['beaufort'] = lambda x: beaufort(mps_to_knot(x))
weewx.units.default_unit_format_dict['beaufort'] = "%d"


def equation_of_time(doy):
    """Equation of time in minutes. Plus means sun leads local time.

    Example (1 October):
    >>> print("%.4f" % equation_of_time(274))
    0.1889
    """
    b = 2 * math.pi * (doy - 81) / 364.0
    return 0.1645 * math.sin(2 * b) - 0.1255 * math.cos(b) - 0.025 * math.sin(b)


def hour_angle(t_utc, longitude, doy):
    """Solar hour angle at a given time in radians.

    t_utc: The time in UTC.
    longitude: the longitude in degrees
    doy: The day of year

    Returns hour angle in radians. 0 <= omega < 2*pi

    Example:
    >>> print("%.4f radians" % hour_angle(15.5, -16.25, 274))
    0.6821 radians
    >>> print("%.4f radians" % hour_angle(0, -16.25, 274))
    2.9074 radians
    """
    Sc = equation_of_time(doy)
    omega = (math.pi / 12.0) * (t_utc + longitude / 15.0 + Sc - 12)
    if omega < 0:
        omega += 2.0 * math.pi
    return omega


def solar_declination(doy):
    """Solar declination for the day of the year in radians

    Example (1 October is the 274th day of the year):
    >>> print("%.6f" % solar_declination(274))
    -0.075274
    """
    return 0.409 * math.sin(2.0 * math.pi * doy / 365 - 1.39)


def sun_radiation(doy, latitude_deg, longitude_deg, tod_utc, interval):
    """Extraterrestrial radiation. Radiation at the top of the atmosphere

    doy: Day-of-year

    latitude_deg, longitude_deg: Lat and lon in degrees

    tod_utc: Time-of-day (UTC) at the end of the interval in hours (0-24)

    interval: The time interval over which the radiation is to be calculated in hours

    Returns the (average?) solar radiation over the time interval in MJ/m^2/hr

    Example:
    >>> print("%.3f" % sun_radiation(doy=274, latitude_deg=16.217,
    ...                              longitude_deg=-16.25, tod_utc=16.0, interval=1.0))
    3.543
    """

    # Solar constant in MJ/m^2/hr
    Gsc = 4.92

    delta = solar_declination(doy)

    earth_distance = 1.0 + 0.033 * math.cos(2.0 * math.pi * doy / 365.0)  # dr

    start_utc = tod_utc - interval
    stop_utc = tod_utc
    start_omega = hour_angle(start_utc, longitude_deg, doy)
    stop_omega = hour_angle(stop_utc, longitude_deg, doy)

    latitude_radians = math.radians(latitude_deg)

    part1 = (stop_omega - start_omega) * math.sin(latitude_radians) * math.sin(delta)
    part2 = math.cos(latitude_radians) * math.cos(delta) * (math.sin(stop_omega)
                                                            - math.sin(start_omega))

    # http://www.fao.org/docrep/x0490e/x0490e00.htm Eqn 28
    Ra = (12.0 / math.pi) * Gsc * earth_distance * (part1 + part2)

    if Ra < 0:
        Ra = 0

    return Ra


def longwave_radiation(Tmin_C, Tmax_C, ea, Rs, Rso, rh):
    """Calculate the net long-wave radiation.
    Ref: http://www.fao.org/docrep/x0490e/x0490e00.htm Eqn 39

    Tmin_C: Minimum temperature during the calculation period
    Tmax_C: Maximum temperature during the calculation period
    ea: Actual vapor pressure in kPa
    Rs: Measured radiation. See below for units.
    Rso: Calculated clear-wky radiation. See below for units.
    rh: Relative humidity in percent

    Because the formula uses the ratio of Rs to Rso, their actual units do not matter,
    so long as they use the same units.

    Returns back radiation in MJ/m^2/day

    Example:
    >>> print("%.1f mm/day" % longwave_radiation(Tmin_C=19.1, Tmax_C=25.1, ea=2.1,
    ...     Rs=14.5, Rso=18.8, rh=50))
    3.5 mm/day

    Night time example. Set rh = 40% to reproduce the Rs/Rso ratio of 0.8 used in the paper.
    >>> print("%.1f mm/day" % longwave_radiation(Tmin_C=28, Tmax_C=28, ea=3.402,
    ...     Rs=0, Rso=0, rh=40))
    2.4 mm/day
    """
    # Calculate temperatures in Kelvin:
    Tmin_K = Tmin_C + 273.16
    Tmax_K = Tmax_C + 273.16

    # Stefan-Boltzman constant in MJ/K^4/m^2/day
    sigma = 4.903e-09

    # Use the ratio of measured to expected radiation as a measure of cloudiness, but
    # only if it's daylight
    if Rso:
        cloud_factor = Rs / Rso
    else:
        # If it's nighttime (no expected radiation), then use this totally made up formula
        if rh > 80:
            # Humid. Lots of clouds
            cloud_factor = 0.3
        elif rh > 40:
            # Somewhat humid. Modest cloud cover
            cloud_factor = 0.5
        else:
            # Low humidity. No clouds.
            cloud_factor = 0.8

    # Calculate the longwave (back) radiation (Eqn 39). Result will be in MJ/m^2/day.
    Rnl_part1 = sigma * (Tmin_K ** 4 + Tmax_K ** 4) / 2.0
    Rnl_part2 = (0.34 - 0.14 * math.sqrt(ea))
    Rnl_part3 = (1.35 * cloud_factor - 0.35)
    Rnl = Rnl_part1 * Rnl_part2 * Rnl_part3

    return Rnl


def evapotranspiration_Metric(Tmin_C, Tmax_C, rh_min, rh_max, sr_mean_wpm2,
                              ws_mps, wind_height_m, latitude_deg, longitude_deg, altitude_m,
                              timestamp):
    """Calculate the rate of evapotranspiration during a one hour time period.
    Ref: http://www.fao.org/docrep/x0490e/x0490e00.htm.
    (The document http://edis.ifas.ufl.edu/ae459 is also helpful)

    Tmin_C: Minimum temperature during the hour in degrees Celsius

    Tmax_C: Maximum temperature during the hour in degrees Celsius

    rh_min: Minimum relative humidity during the hour in percent.

    rh_max: Maximum relative humidity during the hour in percent.

    sr_mean_wpm2: Mean solar radiation during the hour in watts per sq meter

    ws_mps: Average wind speed during the hour in meters per second

    wind_height_m: Height in meters at which windspeed is measured

    latitude_deg, longitude_deg: Latitude, longitude of the station in degrees

    altitude_m: Altitude of the station in meters.

    timestamp: The time, as unix epoch time, at the end of the hour.

    Returns: Evapotranspiration in mm/hr

    Example (Example 19 in the reference document):
    >>> sr_mean_wpm2 = 680.56     # == 2.45 MJ/m^2/hr
    >>> timestamp = 1475337600    # 1-Oct-2016 at 16:00UTC
    >>> print("ET0 = %.2f mm/hr" % evapotranspiration_Metric(Tmin_C=38, Tmax_C=38,
    ...                                rh_min=52, rh_max=52,
    ...                                sr_mean_wpm2=sr_mean_wpm2, ws_mps=3.3, wind_height_m=2,
    ...                                latitude_deg=16.217, longitude_deg=-16.25, altitude_m=8,
    ...                                timestamp=timestamp))
    ET0 = 0.63 mm/hr

    Another example, this time for night
    >>> sr_mean_wpm2 = 0.0        # night time
    >>> timestamp = 1475294400    # 1-Oct-2016 at 04:00UTC (0300 local)
    >>> print("ET0 = %.2f mm/hr" % evapotranspiration_Metric(Tmin_C=28, Tmax_C=28,
    ...                                rh_min=90, rh_max=90,
    ...                                sr_mean_wpm2=sr_mean_wpm2, ws_mps=3.3, wind_height_m=2,
    ...                                latitude_deg=16.217, longitude_deg=-16.25, altitude_m=8,
    ...                                timestamp=timestamp))
    ET0 = 0.03 mm/hr
    """
    if None in (Tmin_C, Tmax_C, rh_min, rh_max, sr_mean_wpm2, ws_mps,
                latitude_deg, longitude_deg, timestamp):
        return None

    if wind_height_m is None:
        wind_height_m = 2.0
    if altitude_m is None:
        altitude_m = 0.0

    # Numerator and denominator terms for the reference crop type
    cn = 37
    cd = 0.34
    # Albedo. for grass reference crop
    albedo = 0.23

    # figure out the day of year [1-366] from the timestamp
    doy = time.localtime(timestamp)[7] - 1
    # Calculate the UTC time-of-day in hours
    time_tt_utc = time.gmtime(timestamp)
    tod_utc = time_tt_utc.tm_hour + time_tt_utc.tm_min / 60.0 + time_tt_utc.tm_sec / 3600.0

    # Calculate mean temperature
    tavg_C = (Tmax_C + Tmin_C) / 2.0

    # Mean humidity
    rh_avg = (rh_min + rh_max) / 2.0

    # Adjust windspeed for height
    u2 = 4.87 * ws_mps / math.log(67.8 * wind_height_m - 5.42)

    # Calculate the atmospheric pressure in kPa
    p = 101.3 * math.pow((293.0 - 0.0065 * altitude_m) / 293.0, 5.26)
    # Calculate the psychrometric constant in kPa/C (Eqn 8)
    gamma = 0.665e-03 * p

    # Calculate mean saturation vapor pressure, converting from hPa to kPa (Eqn 12)
    etmin = weewx.uwxutils.TWxUtils.SaturationVaporPressure(Tmin_C, 'vaTeten') / 10.0
    etmax = weewx.uwxutils.TWxUtils.SaturationVaporPressure(Tmax_C, 'vaTeten') / 10.0
    e0T = (etmin + etmax) / 2.0

    # Calculate the slope of the saturation vapor pressure curve in kPa/C (Eqn 13)
    delta = 4098.0 * (0.6108 * math.exp(17.27 * tavg_C / (tavg_C + 237.3))) / \
            ((tavg_C + 237.3) * (tavg_C + 237.3))

    # Calculate actual vapor pressure from relative humidity (Eqn 17)
    ea = (etmin * rh_max + etmax * rh_min) / 200.0

    # Convert solar radiation from W/m^2 to MJ/m^2/hr
    Rs = sr_mean_wpm2 * 3.6e-3

    # Net shortwave (measured) radiation in MJ/m^2/hr (eqn 38)
    Rns = (1.0 - albedo) * Rs

    # Extraterrestrial radiation in MJ/m^2/hr
    Ra = sun_radiation(doy, latitude_deg, longitude_deg, tod_utc, interval=1.0)
    # Clear sky solar radiation in MJ/m^2/hr (eqn 37)
    Rso = (0.75 + 2e-5 * altitude_m) * Ra

    # Longwave (back) radiation. Convert from MJ/m^2/day to MJ/m^2/hr (Eqn 39):
    Rnl = longwave_radiation(Tmin_C, Tmax_C, ea, Rs, Rso, rh_avg) / 24.0

    # Calculate net radiation at the surface in MJ/m^2/hr (Eqn. 40)
    Rn = Rns - Rnl

    # Calculate the soil heat flux. (see section "For hourly or shorter 
    # periods" in http://www.fao.org/docrep/x0490e/x0490e07.htm#radiation 
    G = 0.1 * Rn if Rs else 0.5 * Rn

    # Put it all together. Result is in mm/hr (Eqn 53)    
    ET0 = (0.408 * delta * (Rn - G) + gamma * (cn / (tavg_C + 273)) * u2 * (e0T - ea)) \
          / (delta + gamma * (1 + cd * u2))

    # We don't allow negative ET's
    if ET0 < 0:
        ET0 = 0

    return ET0


def evapotranspiration_US(Tmin_F, Tmax_F, rh_min, rh_max,
                          sr_mean_wpm2, ws_mph, wind_height_ft,
                          latitude_deg, longitude_deg, altitude_ft, timestamp):
    """Calculate the rate of evapotranspiration during a one hour time period,
    returning result in inches/hr.

    Tmin_F: Minimum temperature during the hour in degrees Fahrenheit

    Tmax_F: Maximum temperature during the hour in degrees Fahrenheit

    rh_min: Minimum relative humidity during the hour in percent.

    rh_max: Maximum relative humidity during the hour in percent.

    sr_mean_wpm2: Mean solar radiation during the hour in watts per sq meter

    ws_mph: Average wind speed during the hour in miles per hour

    wind_height_ft: Height in feet at which windspeed is measured

    latitude_deg, longitude_deg: Latitude, longitude of the station in degrees

    altitude_ft: Altitude of the station in feet.

    timestamp: The time, as unix epoch time, at the end of the hour.

    Returns: Evapotranspiration in inches/hr

    Example (using data from HR station):
    >>> sr_mean_wpm2 = 860
    >>> timestamp = 1469829600  # 29-July-2016 22:00 UTC (15:00 local time)
    >>> print("ET0 = %.3f in/hr" % evapotranspiration_US(Tmin_F=87.8, Tmax_F=89.1,
    ...                                rh_min=34, rh_max=38,
    ...                                sr_mean_wpm2=sr_mean_wpm2, ws_mph=9.58, wind_height_ft=6,
    ...                                latitude_deg=45.7, longitude_deg=-121.5, altitude_ft=700,
    ...                                timestamp=timestamp))
    ET0 = 0.028 in/hr
    """
    try:
        Tmin_C = FtoC(Tmin_F)
        Tmax_C = FtoC(Tmax_F)
        ws_mps = ws_mph * METER_PER_MILE / 3600.0
        wind_height_m = wind_height_ft * METER_PER_FOOT
        altitude_m = altitude_ft * METER_PER_FOOT
    except TypeError:
        return None
    evt = evapotranspiration_Metric(Tmin_C=Tmin_C, Tmax_C=Tmax_C,
                                    rh_min=rh_min, rh_max=rh_max, sr_mean_wpm2=sr_mean_wpm2,
                                    ws_mps=ws_mps, wind_height_m=wind_height_m,
                                    latitude_deg=latitude_deg, longitude_deg=longitude_deg,
                                    altitude_m=altitude_m, timestamp=timestamp)
    return evt / MM_PER_INCH if evt is not None else None


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


def winddruck_Metric(dp_C, t_C, p_mbar, ws_kph):
    """Calculate the windDruck in N per m2

    dp_C - dewpoint in degree Celsius

    t_C - temperature in degree Celsius

    p_mbar - pressure in hPa or mbar

    vms - windSpeed in km per hour
          must in  m per second

    wd = cp * airdensity / 2 * vms2
    wd - winddruck
    cp - Druckbeiwert (dimensionslos) = 1
    """

    if dp_C is None or t_C is None or p_mbar is None or ws_kph is None:
        return None

    dp = dp_C
    Tk = t_C + 273.15

    if ws_kph < 1:
        vms = 0.2
    elif ws_kph < 6:
        vms = 1.5
    elif ws_kph < 12:
        vms = 3.3
    elif ws_kph < 20:
        vms = 5.4
    elif ws_kph < 29:
        vms = 7.9
    elif ws_kph < 39:
        vms = 10.7
    elif ws_kph < 50:
        vms = 13.8
    elif ws_kph < 62:
        vms = 17.1
    elif ws_kph < 75:
        vms = 20.7
    elif ws_kph < 89:
        vms = 24.7
    elif ws_kph < 103:
        vms = 28.5
    elif ws_kph < 117:
        vms = 32.7
    elif ws_kph >= 117:
        vms = ws_kph * 0.277777778

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
    ws_kph = ws_mph * 1.609344

    wdru_C = winddruck_Metric(dp_C, t_C, p_mbar, ws_kph)

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


def deltaT_Metric(t_C, RH, PP):
    #  deltaT Aenderung Lufttemperatur
    #  t_C = outTemp
    #  RH = outHumidity
    #  PP = pressure

    if t_C is None or RH is None or PP is None:
        return None

    Tdc = ((t_C - (14.55 + 0.114 * t_C) * (1 - (0.01 * RH)) - ((2.5 + 0.007 * t_C) * (1 - (0.01 * RH))) ** 3 - (15.9 + 0.117 * t_C) * (1 - (0.01 * RH)) ** 14))
    E = (6.11 * 10 ** (7.5 * Tdc / (237.7 + Tdc)))
    WBc = (((0.00066 * PP) * t_C) + ((4098 * E) / ((Tdc + 237.7) ** 2) * Tdc)) / ((0.00066 * PP) + (4098 * E) / ((Tdc + 237.7) ** 2))
    deltaT_C = t_C - WBc

    return deltaT_C if deltaT_C is not None else None


def deltaT_US(t_F, RH, p_inHg):
    #  deltaT calculations == delta Lufttemperatur
    #  t_F = temperatur degree F
    #  RH = outHumidity
    #  p_inHg = pressure in inHg

    if t_F is None or RH is None or p_inHg is None:
        return None

    t_C = FtoC(t_F)
    p_mbar = p_inHg / INHG_PER_MBAR
    deltaT_C = deltaT_Metric(t_C, RH, p_mbar)

    return CtoF(deltaT_C) if deltaT_C is not None else None


def cbindex_Metric(t_C, RH):
    # Chandler Burning Index calculations
    #  t_C = outTemp
    #  RH = outHumidity

    if t_C is None or RH is None:
        return None

    cbIndex = max(0.0, round((((110 - 1.373 * RH) - 0.54 * (10.20 - t_C)) * (124 * 10**(-0.0142 * RH)))/60, 1))
    # cbIndex = round(cdIn, 1)

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

    # t_C is outTemp in C

    if t_C is None:
        return None

    """ ueber Wasser t_C -45 C bis 60 C
       ddM_C = 6.112 * math.exp(17.62 * t_C / (243.12 + t_C))
       ueber Eis t_C -65 C bis 0.01 C
       ddM_C = 6.112 * math.exp(22.46 * t_C / (272.62 + t_C))
    """
    if t_C < 0.0:

        dd_C = 6.112 * math.exp(22.46 * t_C / (272.62 + t_C))

    else:

        dd_C = 6.112 * math.exp(17.62 * t_C / (243.12 + t_C))

    return dd_C


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


def da_Metric(t_C, p_mbar):
    # Density altitude calculations
    #  t_C = outTemp
    #  p_mbar =  pressure
    # Elevation = 53.6 meter = 175 ft
    # QNH = pressure
    # Druckhoehe(PA_da) = Elevation + (1013.25-QNH) * 30 gerundet faktor 28ft
    # Dichtehöhe = PA_da + 120 * (aktuelle Temp. - [15 - PA_da * 2°/1000 ft])
    # allgemein vereinfacht DA =  PA + 120 * ΔT
    # da_ft = (Elevation + (1013.25 - p_mbar) * 30) + ((t_C - (15 - (Elevation + (1013.25 - p_mbar) * 30) * 2 / 1000)) * 120)

    if t_C is None or p_mbar is None:
        return None

    PA_da = 175 + (1013.25 - p_mbar) * 28
    dT_da = t_C - (15 - PA_da * 2 / 1000.0)
    DH_da = 120 * (t_C - (15 - PA_da * 2 / 1000.0))
    da_ft = PA_da + DH_da
    da_me = da_ft * 0.3048

    return da_me if da_me is not None else None


def da_US(t_F, p_inHg):
    #  Density altitude calculations
    #  t_F = temperatur degree F
    #  p_inHg = pressure

    if t_F is None or p_inHg is None:
        return None

    t_C = FtoC(t_F)
    p_mbar = p_inHg / INHG_PER_MBAR
    da_m = da_Metric(t_C, p_mbar)
    da_fo = da_m * 3.28084
    da_fo = round(da_fo, 1)

    return da_fo if da_fo is not None else None


def thw_Metric(t_C, RH, ws_kph):
    """ Uses the air temperature, relative humidity, and wind speed
    (THW = temperature-humidity-wind) to calculate a
    potentially more accurate "felt-air temperature." This is not as accurate, however, as the THSW index, which
    can only be calculated when solar radiation information is available. It uses `calculate_heat_index` and then
    applies additional calculations to it using the wind speed. As such, it returns `None` for input temperatures below
    70 degrees Fahrenheit. The additional calculations come from web forums rumored to contain the proprietary
    Davis Instruments THW index formulas.
    hi is the heat index as calculated by `calculate_heat_index`
    WS is the wind speed in miles per hour
    :param temperature: The temperature in degrees Fahrenheit
    :type temperature: int | long | decimal.Decimal
    :param relative_humidity: The relative humidity as a percentage (88.2 instead of 0.882)
    :type relative_humidity: int | long | decimal.Decimal
    :param wind_speed: The wind speed in miles per hour
    :type wind_speed: int | long | decimal.Decimal
    :return: The THW index temperature in degrees Fahrenheit to one decimal place, or `None` if the temperature is
     less than 70F
    :rtype: decimal.Decimal
    """
    t_F = CtoF(t_C)
    hi_F = heatindexF(t_F, RH)
    WS = kph_to_mph(ws_kph)

    if not hi_F:
        return None

    hi = hi_F - (1.072 * WS)
    thw_C = FtoC(hi)

    return round(thw_C, 1) if thw_C is not None else None


def thw_US(t_F, RH, ws_mph):

    if t_F is None or ws_mph is None or RH is None:
        return None

    hi_F = heatindexF(t_F, RH)
    thw_F = hi_F - (1.072 * ws_mph)

    return round(thw_F, 1) if thw_F is not None else None


def thsw_Metric(t_C, RH, ws_kph, rahes):
    """ Tc is the temperature in degrees Celsius
        RH is the relative humidity percentage
        QD is the direct thermal radiation in watts absorbed per square meter of surface area
        Qd is the diffuse thermal radiation in watts absorbed per square meter of surface area
        Q1 is the thermal radiation in watts absorbed per square meter of surface area as measured by a pyranometer;
                it represents "global radiation" (QD + Qd)
        Q2 is the direct and diffuse radiation in watts absorbed per square meter of surface on the human body
        Q3 is the ground-reflected radiation in watts absorbed per square meter of surface on the human body
        Q is total thermal radiation that affects apparent temperature
        WS is the wind speed in meters per second
        E is the water vapor pressure
        Thsw is the THSW index temperature """

    if t_C is None or ws_kph is None or RH is None or rahes is None:
        return None

    Qd = rahes * 0.25
    Q2 = Qd / 7
    Q3 = rahes / 28
    Q = Q2 + Q3
    WS = ws_kph * 0.277777778
    E = RH / 100 * 6.105 * math.exp(17.27 * t_C / (237.7 + t_C))
    thsw_C = t_C + (0.348 * E) - (0.70 * WS) + ((0.70 * Q) / (WS + 10)) - 4.25

    return round(thsw_C, 1) if thsw_C is not None else None


def thsw_US(t_F, RH, ws_mph, rahes):

    if t_F is None or ws_mph is None or RH is None or rahes is None:
        return None

    t_C = FtoC(t_F)
    ws_kph = ws_mph * 1.609344
    thsw_C = thsw_Metric(t_C, RH, ws_kph, rahes)
    thsw_F = CtoF(thsw_C)

    return round(thsw_F, 1) if thsw_F is not None else None


if __name__ == "__main__":

    import doctest

    if not doctest.testmod().failed:
        print("PASSED")
