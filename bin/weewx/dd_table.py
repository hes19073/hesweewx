#!/usr/bin/python
# -*- coding: utf-8 -*-

# dd_table.py
# 2018 Feb 23 . ccr

"""Print Degree-Day Table.

This script generates a table of degree-days used for modeling the
emergence of larvae of Cydia pomonella (codling moth).

"""

from __future__ import division
import math

ZERO = 0
SPACE = ' '
NULL = ''
NUL = '\x00'
NA = -1

FMT = '%3i'


def dd(day_max_temp, day_min_temp, base_temp):

    """Return degree days above threshold (base_temp), given daily max and
    min temps.

    This function is transcribed from a *perl* subroutine:

    o Coop, Len. "Degree-Day Calculation Formulas." 8 May
      2015. Integrated Plant Protection Center, Oregon State U. 27
      Feb. 2018 <http://uspest.org/wea/wea3.html>.

    This function has been verified against various published tables of
    developmental degree days for Cydia pomonella.  It assumes that
    diurnal temperatures follow a symmetric sine wave.  The document
    (above) references this seminal article:

    o Baskerville, G.L., and P. Emin. "Rapid Estimation of Heat
      Accumulation from Maximum and Minimum Temperatures." _Ecology_
      50 (1969): 514-517.

    I wouldn´t say 1969 was early days for general-purpose computing,
    but apparently the journal editors for _Ecology_ were way more
    interested in graphs and numerical tables than in computation
    algorithms.  Although the authors (B&E) mention a FORTRAN program,
    it is not reproduced in the body of the article.

    Here´s how it works, though: The sine wave is clipped horizontally
    from below by the threshold (base) temperature.  Degree days is
    proportional to the area under the curve above the threshold, which
    thus depends on the threshold and the maximum and minimum
    temperatures for each day.

    The algebra, trigonometry, and Integral Calculus are apparently not
    too exotic but are fairly obscure.  Here follows my  reconstruction.

    
    =====

    If the threshold temp is BELOW the daily min temp, the answer we
    must give is the conventional one:

    average_temp = (max + min) / 2

    dd_conventional = average_temp - threshold

    ... because the curve is not clipped.

    Below, we´re going to use the following ¨simplifying¨ expression, so
    I suppose I ought to define it here.
    
    Let d2 = -2 * dd_conventional =
      2 * threshold - (max + min))
      
    Consider a sine wave from -π/2 to 3π/2 radians with its peak at high
    noon (π/2 rad).

    If the threshold temp is ABOVE the daily min temp, we need to
    integrate over a portion of the curve.  The essential magic is to
    discover the angle θ where the sine wave, scaled and offset to the
    average temperature, crosses this threshold.  Then we can cast away
    the area below the threshold along with the tails of the curve.
    
    Because the sine wave is symmetric about π/2, we need to integrate
    only between θ and π/2.
    
    The definite integral of the sine wave from -π/2 to +π/2 is ZERO
    because half of it is negative, so that doesn´t do us much good.
    We´ll have to choose a different function.  How about sine + 1?

    The definite integral of (sine + 1) from -π/2 to +π/2 is:

    -cos(π/2) - (-cos(-π/2)) + π/2 - (-π/2) = π

    This is the area under the curve.  To normalize the calculations to
    follow, we have to multiply by this:

    downscale_factor = 1 / π

    When threshold temp == min temp and θ == -π/2, the answer we must
    give is dd_conventional.  This becomes our upscale_factor:

    upscale_factor = ((max + min) / 2) - threshold =
      (max + min - 2 * threshold) / 2 =
      (max + min - 2 * min) / 2 =
      (max - min) / 2

    The following formula is similar to that given by B&E in their
    Fig. 1.B:

    heat_units = downscale_factor * upscale_factor * (whole_area - clipped_area)

    where:

    whole_area = (integral(dt) of sin(t) + 1 from θ to π/2) =
      (-cos(π/2) - (-cos(θ)) + (π/2 - θ)) =
      (cos(θ) + (π/2 - θ))

    clipped_area = integral(dt) of 2 * (threshold - min) / (max - min) from θ to π/2 =
      integral(dt) of (threshold - min) / upscale_factor from θ to π/2 =
      integral(dt) of threshold - min from θ to π/2 / upscale_factor =
      (threshold - min) * (π/2 - θ) / upscale_factor
      
    thus:

    heat_units = downscale_factor * upscale_factor *
        ((cos(θ) + (π/2 - θ)) - (threshold - min) * (π/2 - θ) / upscale_factor) =
      downscale_factor * (upscale_factor * (cos(θ) + (π/2 - θ)) - (threshold - min) * (π/2 - θ)) =
      (1 / π) * (((max - min) * (cos(θ) + (π/2 - θ)) / 2) - ((threshold - min) * (π/2 - θ))) =
      (1 / 2π) * ((max - min) * (cos(θ) + (π/2 - θ)) - 2 * (threshold - min) * (π/2 - θ)) =
      (1 / 2π) * ((max - min) * cos(θ) + (max - min) * (π/2 - θ) - 2 * (threshold - min) * (π/2 - θ)) =
      (1 / 2π) * ((max - min) * cos(θ) + ((max - min) - 2 * (threshold - min)) * (π/2 - θ)) =
      (1 / 2π) * ((max - min) * cos(θ) + (max - min - 2 * threshold + 2 * min) * (π/2 - θ)) =
      (1 / 2π) * ((max - min) * cos(θ) + (max - 2 * threshold + min) * (π/2 - θ)) =
      (1 / 2π) * ((max - min) * cos(θ) - (2 * threshold - (max + min)) * (π/2 - θ)) =
      (1 / 2π) * ((max - min) * cos(θ) - (d2 * (π/2 - θ))

    ... which is the result calculated by this function!

    
    =====
    QED
    =====

    
    Now, for the essential magic we need to compute:

    θ = arcsin(unit_base)

    ... where unit_base is the threshold temp scaled to the sine wave
    (not sine + 1):

    unit_base = 2 * (threshold - min) / (max - min) - 1 =
      (2 * (threshold - min) - (max - min)) / (max - min) =
      (2 * threshold - 2 * min - max + min) / (max - min) =
      (2 * threshold - min - max) / (max - min) =
      (2 * threshold - (max + min)) / (max - min) =
      d2 / (max - min)      

    But there´s a fly in this ointment.  We want to have pretty good
    computational accuracy where unit_base is pretty close to ±1, which
    should yield an arcsin result pretty close to ±π/2, but that is just
    where the accuracy of real-world arcsin implementations falls down
    due to inherent granularity of simulating math on binary machines.

    Maybe it would be better to calculate θ using the arctan, instead.

    I think it´s just this easy :

    sin(θ) = a / c where the sides of the right triangle are:

    (a * a) + (b * b) = (c * c)

    and, using the same angle:

    tan(θ) = a / b = a / sqrt ((c * c) - (a * a))

    Now θ = arcsin(a / c)

    and we can choose any values we want for a and c to make that so, so
    it´s handy to pick:

    a = unit_base and c = 1

    and then, the same angle would be:

    θ = arctan(a / sqrt((c * c) - (a * a)))

    θ = arctan(unit_base / sqrt((1 * 1) - (unit_base * unit_base))) =
      arctan((d2 / (max - min)) / sqrt(1 - (d2 / (max - min)) * (d2 / (max - min)))) =
      arctan(d2 / sqrt((max - min) * (max - min) - d2 * d2))

    ... which, if I have not deluded myself, is the formula for θ used
    by the *perl* function referenced above and is thus the formula
    that this script uses, too.  (In practice however, using the arcsin
    yields identical results rounded to the nearest integer.)
    
    =====

        
    Does it need to be this complicated?

    It is unreasonable in cooler weather early in the season to
    attribute 24 hours of heating to a day on which the maximum
    temperature is only one or two degrees above the threshold because
    likely the temperature was above the threshold for only a few hours.
    This sine wave model attributes a smaller amount of heating to just
    that portion of the day.

    It is a refinement beyond modeling a flat 24-hour average.

    Does it need to be any more complicated?

    The actual DD could be calculated, given hourly readings, but that
    would be a lot more effort than just collecting the daily max and
    min temps and considering each 24-hour (midnight to midnight) day to
    be independent of preceding and following days.  This seems to be
    accurate enough to predict insect life stages to within a few days.
    An alternative would be to collect max/min readings for 12-hour
    periods.

    """

    day_sum_temp = day_max_temp + day_min_temp
    day_diff_temp = day_max_temp - day_min_temp
    if day_diff_temp < ZERO:
        result = None
    elif base_temp < day_min_temp:
        result = (day_sum_temp / 2.0) - base_temp
    elif base_temp > day_max_temp:
        result = ZERO
    else:
        d2 = base_temp + base_temp - day_sum_temp
        theta = math.atan2(d2, math.sqrt(day_diff_temp * day_diff_temp - d2 * d2))
        if (d2 < ZERO ) and (theta > ZERO):
            theta = theta - math.pi
#        if day_diff_temp == ZERO:
#            theta = ZERO
#        else:
#            theta = math.asin(d2 / day_diff_temp)
        result = ((day_diff_temp * math.cos(theta)) - (d2 * ((math.pi / 2.0) - theta))) / (math.pi * 2.0)
    return result


def dd_clipped(day_max_temp_f, day_min_temp_f, threshold_temp_f, ceiling_temp_f):

    """Implement both lower and upper threshold temps.

    Test the dd function.

    >>> int(dd_clipped(50, 48, 50, 88 ) + 0.5)
    0
    >>> int(dd_clipped(50, 50, 50, 88 ) + 0.5)
    0
    >>> dd_clipped(50, 52, 50, 88) is None
    True
    >>> int(dd_clipped(52, 48, 50, 88 ) + 0.5)
    1
    >>> int(dd_clipped(52, 48, 50, 88 ) + 0.5)
    1
    >>> int(dd_clipped(55, 48, 50, 88 ) + 0.5)
    2
    >>> int(dd_clipped(52, 51, 50, 88 ) + 0.5)
    2
    >>> int(dd_clipped(55, 51, 50, 88 ) + 0.5)
    3
    >>> int(dd_clipped(52, 52, 50, 88 ) + 0.5)
    2
    >>> int(dd_clipped(54, 48, 50, 88 ) + 0.5)
    2
    >>> int(dd_clipped(54, 50, 50, 88 ) + 0.5)
    2
    >>> int(dd_clipped(54, 52, 50, 88 ) + 0.5)
    3
    >>> int(dd_clipped(86, 48, 50, 88 ) + 0.5)
    17
    >>> int(dd_clipped(86, 50, 50, 88 ) + 0.5)
    18
    >>> int(dd_clipped(86, 52, 50, 88 ) + 0.5)
    19
    >>> int(dd_clipped(88, 48, 50, 88 ) + 0.5)
    18
    >>> int(dd_clipped(91, 48, 50, 88 ) + 0.5)
    19
    >>> int(dd_clipped(91, 51, 50, 88 ) + 0.5)
    21
    >>> int(dd_clipped(88, 50, 50, 88 ) + 0.5)
    19
    >>> int(dd_clipped(88, 51, 50, 88 ) + 0.5)
    20
    >>> int(dd_clipped(88, 52, 50, 88 ) + 0.5)
    20
    >>> int(dd_clipped(90, 48, 50, 88 ) + 0.5)
    19
    >>> int(dd_clipped(90, 50, 50, 88 ) + 0.5)
    20
    >>> int(dd_clipped(90, 52, 50, 88 ) + 0.5)
    21
    >>> int(dd_clipped(86, 86, 50, 88 ) + 0.5)
    36
    >>> dd_clipped(86, 88, 50, 88) is None
    True
    >>> dd_clipped(86, 90, 50, 88) is None
    True
    >>> int(dd_clipped(88, 86, 50, 88 ) + 0.5)
    37
    >>> int(dd_clipped(88, 88, 50, 88 ) + 0.5)
    38
    >>> dd_clipped(88, 90, 50, 88) is None
    True
    >>> int(dd_clipped(90, 86, 50, 88 ) + 0.5)
    37
    >>> int(dd_clipped(90, 88, 50, 88 ) + 0.5)
    38
    >>> int(dd_clipped(90, 90, 50, 88 ) + 0.5)
    38

    """

    dd_threshold = dd(day_max_temp_f, day_min_temp_f, threshold_temp_f)
    dd_ceiling = dd(day_max_temp_f, day_min_temp_f, ceiling_temp_f)
    if None in [dd_threshold, dd_ceiling]:
        result = None
    else:
        result = dd_threshold - dd_ceiling
    return result


def make_table():
    result = []
    result.append('Degree Day (F) Table')
    result.append(NULL)
    range_max_temp_f = range(48, 120, 2)
    range_min_temp_f = range(34, 92, 2)
    result.append('  \ Min Daily Temp')
    cols = []
    cols.append('Max')
    for min_temp_f in range_min_temp_f:
        cols.append(FMT % min_temp_f)
    result.append(SPACE.join(cols))
    for max_temp_f in range_max_temp_f:
        cols = []
        cols.append(FMT % max_temp_f)
        for min_temp_f in range_min_temp_f:
            dd_cydia = dd_clipped(max_temp_f, min_temp_f, 50, 88)
            if dd_cydia is None:
                cols.append('***')
            else:
                cols.append(FMT % dd_cydia)
        result.append(SPACE.join(cols))
    return  result


def main_line():
    lines = make_table()
    print '\n'.join(lines)
    return


if __name__ == "__main__":
    import doctest
    doctest.testmod()
    main_line()


# Fin
