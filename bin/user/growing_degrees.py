#!/usr/bin/python3

# growing_degrees.py
# 2018 Feb 23 . ccr

# ==================================================boilerplate»=====
""" Repertoire of Growing-Degree-Day Calculations

This script is distributed as part of the Phenology Extension to
WeeWX.  WeeWX is maintained by Tom Keffer and Matthew Wall.  This
script is maintained by Chuck Rhode although it may contain portions
copied from Keffer and Wall or directly inspired by them.

Copyright 2018—2021 by Chuck Rhode.

See LICENSE.txt for your rights.

# =================================================«boilerplate======

This script generates a table of growing degree days used for modeling
the emergence of larvae of Cydia pomonella (codling moth).

Also, it provides the logic for several other types of growing degree
day calculations.

"""

# 2020 Sep 29 . ccr . Convert to Python 3.
#             .     . Provide double sine and single and double triangle
#             .     . calculations along with Huber's Method.  Validate
#             .     . against algorithms published at University of
#             .     . California, Agriculture and Natural Resources (UCANR)
#             .     . and Oregon State University (OSU).
# 2019 Mar 24 . ccr . Diagnose bad calculation.
# 2019 Jan 08 . ccr . Change function names.  Provide
#             .     . gdd_single_sine_vertical_cutoff entry point
#             .     . among others.
# 2018 May 28 . ccr . Compare degree days of cooling.


import sys
import math
import decimal

HUNDREDTHS = decimal.Decimal('0.01')

ZERO = 0
SPACE = ' '
NULL = ''
NUL = '\x00'
NA = -1

STDOUT = sys.stdout

FMT = '%3i'


def gdd_single_sine_with_theta(  # 2019 Jan 08
        day_max_temp,
        day_min_temp,
        threshold_temp,
        ):

    """Return growing degree days (GDD) above threshold, given daily max
    and min temps.

    This function is transcribed from a *perl* subroutine:

    o Coop, Len. "Degree-Day Calculation Formulas." 8 May
      2015. Integrated Plant Protection Center, Oregon State U. 27
      Feb. 2018 <http://uspest.org/wea/wea3.html>.

    This function has been verified against various published tables
    of developmental degree days for Cydia pomonella.  It assumes that
    diurnal temperatures follow a single symmetric sine wave.  The
    document (above) references this seminal article:

    o Baskerville, G.L., and P. Emin. "Rapid Estimation of Heat
      Accumulation from Maximum and Minimum Temperatures." _Ecology_
      50 (1969): 514-517.

    I wouldn't say 1969 was early days for general-purpose computing,
    but apparently the journal editors for _Ecology_ were way more
    interested in graphs and numerical tables than in computation
    algorithms.  Although the authors (B&E) mention a FORTRAN program,
    it is not reproduced in the body of the article.

    Here's how it works, though: The sine wave is clipped horizontally
    from below by the threshold temperature.  Growing degree days for
    each day is proportional to the area under the curve above the
    threshold, which thus depends on the threshold and the maximum and
    minimum temperatures for each day.

    The algebra, trigonometry, and Integral Calculus are apparently not
    too exotic but are fairly obscure.  Here follows my  reconstruction.

    
    =====

    If the threshold temp is BELOW the daily min temp, the answer we
    must give is the conventional one:

    dd_conventional = average_temp - threshold

    where average_temp = (max + min) / 2

    ... because the curve is not clipped.

    Below, we're going to use the following ¨simplifying¨ expression, so
    I suppose I ought to define it here.
    
    Let d2 = -2 * dd_conventional =
      2 * threshold - (max + min)
      
    Consider a sine wave from -π/2 to 3π/2 radians with its peak at high
    noon (π/2 radians).

    If the threshold temp is ABOVE the daily min temp, we need to
    integrate over a portion of the curve.  The essential magic is to
    discover the angle θ where the sine wave, scaled and offset to the
    average temperature, crosses this threshold.  Then we can cast away
    the area below the threshold along with the tails of the curve.
    
    Because the sine wave is symmetric about π/2, we need to integrate
    only between -π/2 and π/2.
    
    The definite integral of the sine wave from -π/2 to +π/2 is ZERO
    because half of it is negative, so that doesn't do us much good.
    We'll have to choose a different function.  How about sine + 1?

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

    heat_units = downscale_factor * (upscale_factor * whole_area - clipped_area))

    where:

    whole_area = integral(dt) of (sin(t) + 1) from θ to π/2 =
      (-cos(π/2) - (-cos(θ)) + (π/2 - θ)) =
      (cos(θ) + (π/2 - θ))

    clipped_area = integral(dt) of (threshold - min) from θ to π/2 =
      (threshold - min) * (π/2 - θ)

    thus:

    heat_units = 
      downscale_factor * (upscale_factor * (cos(θ) + (π/2 - θ))) - (threshold - min) * (π/2 - θ) =
      (1 / π) * (((max - min) * (cos(θ) + (π/2 - θ)) / 2) - ((threshold - min) * (π/2 - θ))) =
      (1 / 2π) * ((max - min) * (cos(θ) + (π/2 - θ)) - 2 * (threshold - min) * (π/2 - θ)) =
      (1 / 2π) * ((max - min) * cos(θ) + (max - min) * (π/2 - θ) - 2 * (threshold - min) * (π/2 - θ)) =
      (1 / 2π) * ((max - min) * cos(θ) + ((max - min) - 2 * (threshold - min)) * (π/2 - θ)) =
      (1 / 2π) * ((max - min) * cos(θ) + (max - min - 2 * threshold + 2 * min) * (π/2 - θ)) =
      (1 / 2π) * ((max - min) * cos(θ) + (max - 2 * threshold + min) * (π/2 - θ)) =
      (1 / 2π) * ((max - min) * cos(θ) - (2 * threshold - (max + min)) * (π/2 - θ)) =
      (1 / 2π) * ((max - min) * cos(θ) - d2 * (π/2 - θ))

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

      But there's a fly in this ointment.  We want to have pretty good
      computational accuracy where unit_base is pretty close to ±1, which
      should yield an arcsin result pretty close to ±π/2, but that is just
      where the accuracy of real-world arcsin implementations falls down
      due to inherent granularity of simulating mathematics of continuous
      functions on binary machines, which can handle only discrete values.

    Maybe it would be better to calculate θ using the arctan, instead.

    I think it's just this easy:

    sin(θ) = a / c where the sides of the right triangle are:

    (a * a) + (b * b) = (c * c)

    and, using the same angle:

    tan(θ) = a / b = a / sqrt ((c * c) - (a * a))

    Now θ = arcsin(a / c)

    and, as above, this means:

    a = unit_base and c = 1

    Then, the same angle would be:

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

    It is unreasonable in cooler weather early in the season to require
    that the AVERAGE temperature be above the threshold before recording
    any degree day accumulation because plainly the actual temperature
    may actually be ABOVE the threshold for part of the day even when the
    AVERAGE is less than the threshold.  The single sine wave model
    captures this small amount of heating whereas the conventional model
    does not.  Thus, in the earlier (and the later) portions of the
    season the cumulative growing degree days will (and should) outrun
    the conventional degree days.

    Does it need to be any more complicated?

    The actual GDD could be calculated, given hourly readings, but
    that would be a lot more effort than just collecting the daily max
    and min temps and considering each 24-hour (midnight to midnight)
    day to be independent of preceding and following days.  This seems
    to be accurate enough to predict insect life stages to within a
    few days.  

    An alternative would be to collect max/min readings for 12-hour
    periods.  This technique is called the "double sine" method, but,
    although it requires double the computational effort, it seems not
    to be significantly more accurate at modeling insect development.

    """

    day_sum_temp = day_max_temp + day_min_temp
    day_diff_temp = day_max_temp - day_min_temp
    theta = None
    if day_diff_temp < ZERO:
        result = None
    elif threshold_temp < day_min_temp:
        result = (day_sum_temp * 0.5) - threshold_temp  # dd_conventional
    elif threshold_temp > day_max_temp:
        result = ZERO
    else:
        d2 = threshold_temp + threshold_temp - day_sum_temp  # -2.0 * dd_conventional
        try:  # 2019 Mar 24
            theta = math.atan2(d2, math.sqrt(day_diff_temp * day_diff_temp - d2 * d2))
        except ValueError:
            theta = math.pi
        if (d2 < ZERO ) and (theta > ZERO):
            theta = theta - math.pi
#        if day_diff_temp == ZERO:
#            theta = ZERO
#        else:
#            theta = math.asin(d2 / day_diff_temp)
        result = ((day_diff_temp * math.cos(theta)) - (d2 * ((math.pi * 0.5) - theta))) / (math.pi * 2.0)
    return (result, theta)


def gdd_single_sine_no_cutoff(  # 2019 Jan 08
        day_max_temp,
        day_min_temp,
        threshold_temp,
        **dummies
        ):
    (result, theta) = gdd_single_sine_with_theta(  # 2019 Jan 08
            day_max_temp=day_max_temp,
            day_min_temp=day_min_temp,
            threshold_temp=threshold_temp,
            )
    return result


def gdd_double_sine_no_cutoff(  # 2020 Nov 03
        day_max_temp,
        day_min_temp,
        threshold_temp,
        day_2_min_temp,
        **dummies
        ):
    heat_1 = gdd_single_sine_no_cutoff(
        day_max_temp=day_max_temp,
        day_min_temp=day_min_temp,
        threshold_temp=threshold_temp,
        )
    heat_2 = gdd_single_sine_no_cutoff(
        day_max_temp=day_max_temp,
        day_min_temp=day_2_min_temp,
        threshold_temp=threshold_temp,
        )
    if None in [heat_1, heat_2]:
        result = None
    else:
        result = (heat_1 + heat_2) * 0.5
    return result


def gdd_single_triangle_with_factor(  # 2020 Nov 03
        day_max_temp,
        day_min_temp,
        threshold_temp,
        ):

    """Return growing degree days (GDD) above threshold, given daily max
    and min temps.

    This function is transcribed from a *perl* subroutine:

    o Coop, Len. "Degree-Day Calculation Formulas." 8 May
      2015. Integrated Plant Protection Center, Oregon State U. 27
      Feb. 2018 <http://uspest.org/wea/wea3.html>.

    This function has been verified against various published tables
    of developmental degree days for Cydia pomonella.  It models
    growing degree days as the area of an isosceles triangle one day 
    wide at the base and max - min degrees high.

    The triangle is clipped horizontally from below by the threshold
    temperature.  Growing degree days (heat units) for each day is
    proportional to the area of the triangle above the threshold,
    which thus depends on the threshold and the max and min
    temperatures for each day.

    If the threshold temp is BELOW the daily min temp, the answer we
    must give is the conventional one:

    dd_conventional = average_temp - threshold

    where average_temp = (max + min) / 2.

    Of course, the area of the whole triangle is (max - min) / 2.

    When the threshold temp and the daily min temp are the same, then
    the area of the triangle (heat units) and dd_conventional are the
    same.

    heat_units = dd_conventional
    (max - min) / 2 = ((max + min) / 2) - threshold
    (max - min) / 2 = ((max + min) / 2) - min
    (max - min) = (max + min) - (2 * min)
    (max - min) = max + min - min - min = (max - min)

    So far, so good.
    
    Consider the height of the triangle above the threshold, which is
    smaller by a factor of (max - threshold) / (max - min).  The base
    of the triangle above the threshold is shorter by the same factor.
    Growing degree days should be smaller by factor² to be proportional
    to the area of the triangle above the threshold:

    heat_units = 
      factor² * (max - min) / 2 =
      factor * (max - threshold) / 2 =
      ((max - threshold)² / (max - min)) / 2

    """

    day_sum_temp = day_max_temp + day_min_temp
    day_diff_temp = day_max_temp - day_min_temp
    factor = None
    if day_diff_temp < ZERO:
        result = None
    elif threshold_temp < day_min_temp:
        result = (day_sum_temp * 0.5) - threshold_temp  # dd_conventional
    elif threshold_temp > day_max_temp:
        result = ZERO
    else:
        try:
            factor = (day_max_temp - threshold_temp) / (day_max_temp - day_min_temp)
            result = factor * (day_max_temp - threshold_temp) * 0.5
        except ValueError:
            result = ZERO
    return (result, factor)
    

def gdd_single_triangle_no_cutoff(  # 2020 Nov 03
        day_max_temp,
        day_min_temp,
        threshold_temp,
        **dummies
        ):
    (result, factor) = gdd_single_triangle_with_factor(
            day_max_temp=day_max_temp,
            day_min_temp=day_min_temp,
            threshold_temp=threshold_temp,
            )
    return result


def gdd_double_triangle_no_cutoff(  # 2020 Nov 03
        day_max_temp,
        day_min_temp,
        threshold_temp,
        day_2_min_temp,
        **dummies
        ):
    heat_1 = gdd_single_triangle_no_cutoff(
        day_max_temp=day_max_temp,
        day_min_temp=day_min_temp,
        threshold_temp=threshold_temp,
        )
    heat_2 = gdd_single_triangle_no_cutoff(
        day_max_temp=day_max_temp,
        day_min_temp=day_2_min_temp,
        threshold_temp=threshold_temp,
        )
    if None in [heat_1, heat_2]:
        result = None
    else:
        result = (heat_1 + heat_2) * 0.5
    return result


def dd_conventional(  # 2018 Jan 08
        day_max_temp,
        day_min_temp,
        threshold_temp,
        **dummies
        ):

    """Calculate degree days of cooling (DD).

    This is a heating, ventilation, and air-conditioning (HVAC) rule of
    thumb and is often held out as an adequate and easily grasped
    substitute for calculating growing degree days.

    """

    day_sum_temp = day_max_temp + day_min_temp
    day_diff_temp = day_max_temp - day_min_temp
    if day_diff_temp < ZERO:
        result = None
    else:
        result = (day_sum_temp * 0.5) - threshold_temp
        if result < ZERO:
            result = ZERO
    return result

    
def gdd_single_sine_horizontal_cutoff(  # 2019 Jan 08
        day_max_temp,
        day_min_temp,
        threshold_temp,
        cutoff_temp,
        **dummies
        ):
    
    """Implement both lower and upper threshold temps.

    Test the gdd_single_sine_horizontal_cutoff function.

    >>> int(gdd_single_sine_horizontal_cutoff(50, 48, 50, 88 ) + 0.5)
    0
    >>> int(gdd_single_sine_horizontal_cutoff(50, 50, 50, 88 ) + 0.5)
    0
    >>> gdd_single_sine_horizontal_cutoff(50, 52, 50, 88) is None
    True
    >>> int(gdd_single_sine_horizontal_cutoff(52, 48, 50, 88 ) + 0.5)
    1
    >>> int(gdd_single_sine_horizontal_cutoff(52, 48, 50, 88 ) + 0.5)
    1
    >>> int(gdd_single_sine_horizontal_cutoff(55, 48, 50, 88 ) + 0.5)
    2
    >>> int(gdd_single_sine_horizontal_cutoff(52, 51, 50, 88 ) + 0.5)
    2
    >>> int(gdd_single_sine_horizontal_cutoff(55, 51, 50, 88 ) + 0.5)
    3
    >>> int(gdd_single_sine_horizontal_cutoff(52, 52, 50, 88 ) + 0.5)
    2
    >>> int(gdd_single_sine_horizontal_cutoff(54, 48, 50, 88 ) + 0.5)
    2
    >>> int(gdd_single_sine_horizontal_cutoff(54, 50, 50, 88 ) + 0.5)
    2
    >>> int(gdd_single_sine_horizontal_cutoff(54, 52, 50, 88 ) + 0.5)
    3
    >>> int(gdd_single_sine_horizontal_cutoff(86, 48, 50, 88 ) + 0.5)
    17
    >>> int(gdd_single_sine_horizontal_cutoff(86, 50, 50, 88 ) + 0.5)
    18
    >>> int(gdd_single_sine_horizontal_cutoff(86, 52, 50, 88 ) + 0.5)
    19
    >>> int(gdd_single_sine_horizontal_cutoff(88, 48, 50, 88 ) + 0.5)
    18
    >>> int(gdd_single_sine_horizontal_cutoff(91, 48, 50, 88 ) + 0.5)
    19
    >>> int(gdd_single_sine_horizontal_cutoff(91, 51, 50, 88 ) + 0.5)
    21
    >>> int(gdd_single_sine_horizontal_cutoff(88, 50, 50, 88 ) + 0.5)
    19
    >>> int(gdd_single_sine_horizontal_cutoff(88, 51, 50, 88 ) + 0.5)
    20
    >>> int(gdd_single_sine_horizontal_cutoff(88, 52, 50, 88 ) + 0.5)
    20
    >>> int(gdd_single_sine_horizontal_cutoff(90, 48, 50, 88 ) + 0.5)
    19
    >>> int(gdd_single_sine_horizontal_cutoff(90, 50, 50, 88 ) + 0.5)
    20
    >>> int(gdd_single_sine_horizontal_cutoff(90, 52, 50, 88 ) + 0.5)
    21
    >>> int(gdd_single_sine_horizontal_cutoff(86, 86, 50, 88 ) + 0.5)
    36
    >>> gdd_single_sine_horizontal_cutoff(86, 88, 50, 88) is None
    True
    >>> gdd_single_sine_horizontal_cutoff(86, 90, 50, 88) is None
    True
    >>> int(gdd_single_sine_horizontal_cutoff(88, 86, 50, 88 ) + 0.5)
    37
    >>> int(gdd_single_sine_horizontal_cutoff(88, 88, 50, 88 ) + 0.5)
    38
    >>> gdd_single_sine_horizontal_cutoff(88, 90, 50, 88) is None
    True
    >>> int(gdd_single_sine_horizontal_cutoff(90, 86, 50, 88 ) + 0.5)
    37
    >>> int(gdd_single_sine_horizontal_cutoff(90, 88, 50, 88 ) + 0.5)
    38
    >>> int(gdd_single_sine_horizontal_cutoff(90, 90, 50, 88 ) + 0.5)
    38
    
    """

    dd_threshold = gdd_single_sine_no_cutoff(
        day_max_temp=day_max_temp,
        day_min_temp=day_min_temp,
        threshold_temp=threshold_temp,
        )
    dd_cutoff = gdd_single_sine_no_cutoff(
        day_max_temp=day_max_temp,
        day_min_temp=day_min_temp,
        threshold_temp=cutoff_temp,
        )
    if None in [dd_threshold, dd_cutoff]:
        result = None
    else:
        result = dd_threshold - dd_cutoff
        if result < ZERO:
            result = ZERO
    return result


def gdd_single_triangle_horizontal_cutoff(  # 2020 Nov 04
        day_max_temp,
        day_min_temp,
        threshold_temp,
        cutoff_temp,
        **dummies
        ):
    dd_threshold = gdd_single_triangle_no_cutoff(
        day_max_temp=day_max_temp,
        day_min_temp=day_min_temp,
        threshold_temp=threshold_temp,
        )
    dd_cutoff = gdd_single_triangle_no_cutoff(
        day_max_temp=day_max_temp,
        day_min_temp=day_min_temp,
        threshold_temp=cutoff_temp,
        )
    if None in [dd_threshold, dd_cutoff]:
        result = None
    else:
        result = dd_threshold - dd_cutoff
        if result < ZERO:
            result = ZERO
    return result

    
def gdd_double_sine_horizontal_cutoff(  # 2020 Nov 03
        day_max_temp,
        day_min_temp,
        threshold_temp,
        cutoff_temp,
        day_2_min_temp,
        **dummies
        ):
    heat_1 = gdd_single_sine_horizontal_cutoff(
        day_max_temp=day_max_temp,
        day_min_temp=day_min_temp,
        threshold_temp=threshold_temp,
        cutoff_temp=cutoff_temp,
        )
    heat_2 = gdd_single_sine_horizontal_cutoff(
        day_max_temp=day_max_temp,
        day_min_temp=day_2_min_temp,
        threshold_temp=threshold_temp,
        cutoff_temp=cutoff_temp,
        )
    if None in [heat_1, heat_2]:
        result = None
    else:
        result = (heat_1 + heat_2) * 0.5
    return result


def gdd_double_triangle_horizontal_cutoff(  # 2020 Nov 03
        day_max_temp,
        day_min_temp,
        threshold_temp,
        cutoff_temp,
        day_2_min_temp,
        **dummies
        ):
    heat_1 = gdd_single_triangle_horizontal_cutoff(
        day_max_temp=day_max_temp,
        day_min_temp=day_min_temp,
        threshold_temp=threshold_temp,
        cutoff_temp=cutoff_temp,
        )
    heat_2 = gdd_single_triangle_horizontal_cutoff(
        day_max_temp=day_max_temp,
        day_min_temp=day_2_min_temp,
        threshold_temp=threshold_temp,
        cutoff_temp=cutoff_temp,
        )
    if None in [heat_1, heat_2]:
        result = None
    else:
        result = (heat_1 + heat_2) * 0.5
    return result


def gdd_huber(  # 2020 Oct 2
        day_max_temp,
        day_min_temp,
        threshold_temp,
        cutoff_temp,
        day_2_min_temp,
        scale = 'F',
        **dummies
        ):

    """Huber's method

    Deduct 0.3°F from dd_conventional when max and min are both within
    the threshold—cutoff range.

    Note the scale parameter.  Make scale='C' if you want calculations
    in centigrade, not Fahrenheit.

    """
    
    def as_centigrade_scale(fahrenheit):
        return fahrenheit * 5.0 / 9.0

    def to_01(degree):
        return decimal.Decimal(degree).quantize(HUNDREDTHS, rounding=decimal.ROUND_05UP)

    if (to_01(day_max_temp) <= to_01(cutoff_temp)) and (to_01(day_min_temp) >= to_01(threshold_temp)):
        result = dd_conventional(
            day_max_temp=day_max_temp,
            day_min_temp=day_min_temp,
            threshold_temp=threshold_temp,
            cutoff_temp=cutoff_temp,
            )
        if result is None:
            pass
        else:
            if scale.lower() in ['f', 'fahrenheit']:
                result -= 0.3
            else:
                result -= as_centigrade_scale(0.3)
            if result < ZERO:
                result = ZERO
    else:
        result = gdd_single_sine_horizontal_cutoff(
            day_max_temp=day_max_temp,
            day_min_temp=day_min_temp,
            threshold_temp=threshold_temp,
            cutoff_temp=cutoff_temp,
            )
    return result
    
    
def gdd_single_sine_vertical_cutoff(  # 2018 Jan 09
        day_max_temp,
        day_min_temp,
        threshold_temp,
        cutoff_temp,
        **dummies
        ):

    """Implement a vertical cutoff.

    """
    
    (dd_threshold, theta_1) = gdd_single_sine_with_theta(
        day_max_temp=day_max_temp,
        day_min_temp=day_min_temp,
        threshold_temp=threshold_temp,
        )
    (dd_cutoff, theta_2) = gdd_single_sine_with_theta(
        day_max_temp=day_max_temp,
        day_min_temp=day_min_temp,
        threshold_temp=cutoff_temp,
        )
    if None in [dd_threshold, dd_cutoff]:
        result = None
    else:
        result = dd_threshold - dd_cutoff
        if (day_max_temp < cutoff_temp):
            pass
        elif (cutoff_temp < day_min_temp):
            result = ZERO
        else:

            # integral(dt) of (cutoff - min) from θ to π/2
            
            rectangle = (math.pi * 0.5 - theta_2) * (cutoff_temp - threshold_temp) / math.pi
            result -= rectangle
            if result < ZERO:
                result = ZERO
    return result


def gdd_single_triangle_vertical_cutoff(  # 2020 Nov 04
        day_max_temp,
        day_min_temp,
        threshold_temp,
        cutoff_temp,
        **dummies
        ):
    (dd_threshold, factor_1) = gdd_single_triangle_with_factor(
        day_max_temp=day_max_temp,
        day_min_temp=day_min_temp,
        threshold_temp=threshold_temp,
        )
    (dd_cutoff, factor_2) = gdd_single_triangle_with_factor(
        day_max_temp=day_max_temp,
        day_min_temp=day_min_temp,
        threshold_temp=cutoff_temp,
        )
    if None in [dd_threshold, dd_cutoff]:
        result = None
    else:
        result = dd_threshold - dd_cutoff
        if (day_max_temp < cutoff_temp):
            pass
        elif (cutoff_temp < day_min_temp):
            result = ZERO
        else:
            rectangle = factor_2 * (cutoff_temp - threshold_temp)
            result -= rectangle
            if result < ZERO:
                result = ZERO
    return result


def gdd_double_sine_vertical_cutoff(  # 2020 Nov 03
        day_max_temp,
        day_min_temp,
        threshold_temp,
        cutoff_temp,
        day_2_min_temp,
        **dummies
        ):
    heat_1 = gdd_single_sine_vertical_cutoff(
        day_max_temp=day_max_temp,
        day_min_temp=day_min_temp,
        threshold_temp=threshold_temp,
        cutoff_temp=cutoff_temp,
        )
    heat_2 = gdd_single_sine_vertical_cutoff(
        day_max_temp=day_max_temp,
        day_min_temp=day_2_min_temp,
        threshold_temp=threshold_temp,
        cutoff_temp=cutoff_temp,
        )
    if None in [heat_1, heat_2]:
        result = None
    else:
        result = (heat_1 + heat_2) * 0.5
    return result


def gdd_double_triangle_vertical_cutoff(  # 2020 Nov 03
        day_max_temp,
        day_min_temp,
        threshold_temp,
        cutoff_temp,
        day_2_min_temp,
        **dummies
        ):
    heat_1 = gdd_single_triangle_vertical_cutoff(
        day_max_temp=day_max_temp,
        day_min_temp=day_min_temp,
        threshold_temp=threshold_temp,
        cutoff_temp=cutoff_temp,
        )
    heat_2 = gdd_single_triangle_vertical_cutoff(
        day_max_temp=day_max_temp,
        day_min_temp=day_2_min_temp,
        threshold_temp=threshold_temp,
        cutoff_temp=cutoff_temp,
        )
    if None in [heat_1, heat_2]:
        result = None
    else:
        result = (heat_1 + heat_2) * 0.5
    return result


def gdd_single_sine_intermediate_cutoff(  # 2019 Jan 08
        day_max_temp,
        day_min_temp,
        threshold_temp,
        cutoff_temp,
        **dummies
        ):
    
    """Implement an intermediate cutoff.

    """
    
    dd_threshold = gdd_single_sine_no_cutoff(
        day_max_temp=day_max_temp,
        day_min_temp=day_min_temp,
        threshold_temp=threshold_temp,
        )
    dd_cutoff = gdd_single_sine_no_cutoff(
        day_max_temp=day_max_temp,
        day_min_temp=day_min_temp,
        threshold_temp=cutoff_temp,
        )
    if None in [dd_threshold, dd_cutoff]:
        result = None
    else:
        result = dd_threshold - 2.0 * dd_cutoff
        if result < ZERO:
            result = ZERO
    return result


def gdd_single_triangle_intermediate_cutoff(  # 2019 Jan 08
        day_max_temp,
        day_min_temp,
        threshold_temp,
        cutoff_temp,
        **dummies
        ):
    dd_threshold = gdd_single_triangle_no_cutoff(
        day_max_temp=day_max_temp,
        day_min_temp=day_min_temp,
        threshold_temp=threshold_temp,
        )
    dd_cutoff = gdd_single_triangle_no_cutoff(
        day_max_temp=day_max_temp,
        day_min_temp=day_min_temp,
        threshold_temp=cutoff_temp,
        )
    if None in [dd_threshold, dd_cutoff]:
        result = None
    else:
        result = dd_threshold - 2.0 * dd_cutoff
        if result < ZERO:
            result = ZERO
    return result


def gdd_double_sine_intermediate_cutoff(  # 2020 Nov 03
        day_max_temp,
        day_min_temp,
        threshold_temp,
        cutoff_temp,
        day_2_min_temp,
        **dummies
        ):
    heat_1 = gdd_single_sine_intermediate_cutoff(
        day_max_temp=day_max_temp,
        day_min_temp=day_min_temp,
        threshold_temp=threshold_temp,
        cutoff_temp=cutoff_temp,
        )
    heat_2 = gdd_single_sine_intermediate_cutoff(
        day_max_temp=day_max_temp,
        day_min_temp=day_2_min_temp,
        threshold_temp=threshold_temp,
        cutoff_temp=cutoff_temp,
        )
    if None in [heat_1, heat_2]:
        result = None
    else:
        result = (heat_1 + heat_2) * 0.5
    return result


def gdd_double_triangle_intermediate_cutoff(  # 2020 Nov 04
        day_max_temp,
        day_min_temp,
        threshold_temp,
        cutoff_temp,
        day_2_min_temp,
        **dummies
        ):
    heat_1 = gdd_single_triangle_intermediate_cutoff(
        day_max_temp=day_max_temp,
        day_min_temp=day_min_temp,
        threshold_temp=threshold_temp,
        cutoff_temp=cutoff_temp,
        )
    heat_2 = gdd_single_triangle_intermediate_cutoff(
        day_max_temp=day_max_temp,
        day_min_temp=day_2_min_temp,
        threshold_temp=threshold_temp,
        cutoff_temp=cutoff_temp,
        )
    if None in [heat_1, heat_2]:
        result = None
    else:
        result = (heat_1 + heat_2) * 0.5
    return result


def make_table(scale='F', species='Cydia pomonella'):  # 2019 Jan 08

    def as_centigrade(fahrenheit):
        return int(round((fahrenheit - 32.0) * 5.0 / 9.0))
    
    result = []
    result.append('Growing Degree Day (°%s) Table' % scale)
    result.append(NULL)
    range_max_temp = list(range(48, 120, 2))
    range_min_temp = list(range(44, 92, 2))
    if species in ['Cydia pomonella']:
        common_name = 'Codling Moth'
        threshold = 50
        cutoff = 88
        method = gdd_single_sine_horizontal_cutoff
    elif species in ['Choristoneura rosaceana']:
        common_name = 'Obliquebanded Leafroller'
        threshold = 43
        cutoff = 85
        method = gdd_single_sine_vertical_cutoff
    else:
        raise NotImplementedError
    if scale in ['F']:
        pass
    elif scale in ['C']:
        range_max_temp = as_centigrade(range_max_temp)
        range_min_temp = as_centigrade(range_min_temp)
        threshold = as_centigrade(threshold)
        cutoff = as_centigrade(cutoff)
    else:
        raise NotImplementedError
    result.append('For %s (%s)' % (common_name, species))
    result.append('Threshold = %3i°%s' % (threshold, scale))
    result.append('Cutoff = %3i°%s' % (cutoff, scale))
    result.append('Method:  %s' % method.__name__)
    result.append(NULL)
    result.append('  \ Min Daily Temp')
    cols = []
    cols.append('Max')
    for min_temp in range_min_temp:
        cols.append(FMT % round(min_temp))
    result.append(SPACE.join(cols))
    for max_temp in range_max_temp:
        cols = []
        cols.append(FMT % round(max_temp))
        for min_temp in range_min_temp:
            dd_species = method(max_temp, min_temp, threshold, cutoff)
            if dd_species is None:
                cols.append('***')
            else:
                cols.append(FMT % round(dd_species))
        result.append(SPACE.join(cols))
    result.append(NULL)
    return  result


def main_line():
    lines = make_table()
    STDOUT.write('\n'.join(lines))
    return


if __name__ == "__main__":
    import doctest
    doctest.testmod()
    main_line()


# Fin
