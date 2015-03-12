#!/usr/bin/env python

"""Calculates the position of the sun for the given datetime.

http://en.wikipedia.org/wiki/Position_of_the_Sun

to run: ./pylaunch.sh SunPosition.py -- 37:24 -122:4:57 2015-12-22T00:00:00

Note: use -- to end options and allow for negative coordinates.

"""

import math

import coords

from Transforms import EclipticEquatorial
from Transforms import EquatorialHorizon
from Transforms import GMST
from Transforms import utils


def SolarLongitude(a_datetime):
    """Calculate the longitude of the sun for the given date

    http://en.wikipedia.org/wiki/Position_of_the_Sun

    returns the sun's longitude and distance in AU
    """

    n = a_datetime.toJulianDate() - a_datetime.J2000

    # mean longitude
    L = coords.angle(280.460 + 0.9856474*n)
    L.normalize(0, 360)

    # ecliptic longitude
    g = coords.angle(357.528 + 0.9856003*n)
    g.normalize(0, 365)

    # ecliptic longitude
    ecliptic_longitude = coords.angle(L.value + 1.915*math.sin(g.radians) + 0.020*math.sin(2.0*g.radians))

    # distance to sun in AU
    R = 1.00014 - 0.01671*math.cos(g.radians) - 0.00014*math.cos(2.0*g.radians)

    return ecliptic_longitude, R


def EquationOfTime(a_datetime):
    """Calcuate the equation of time

    http://en.wikipedia.org/wiki/Equation_of_time

    Returns: equation of time in degrees.
    """

    gast = GMST.USNO_C163.GAST(a_datetime)

    ecliptic_longitude, R = SolarLongitude(a_datetime)

    sun_ec = coords.spherical(R, coords.angle(90), ecliptic_longitude)

    sun_eq = EclipticEquatorial.toEquatorial(sun_ec, a_datetime)

    sun_ra = utils.get_ra(sun_eq)

    eot = gast.value - sun_ra # TODO - UT + offset

    # TODO correction for not noon? LAST?
    # TODO hack for discontinuity at vernal equinox?

    return eot




# ================
# ===== main =====
# ================


if __name__ == '__main__':

    # -------------------------
    # ----- parse options -----
    # -------------------------

    import optparse

    defaults = {}

    usage = '%prog [options] <latitude> <longitude> <datetime>'

    parser = optparse.OptionParser(usage=usage)

    options, args = parser.parse_args()

    # ----- validate -----

    if len(args) < 3:
        parser.error('missing object and/or datetime.')

    a_latitude = utils.parse_angle_arg(args[0])
    a_longitude = utils.parse_angle_arg(args[1])

    a_datetime = coords.datetime(args[2])


    # ----------------------------------
    # ----- calculate sun position -----
    # ----------------------------------



    ecliptic_longitude, R = SolarLongitude(a_datetime)

    sun_ec = coords.spherical(R, coords.angle(90), ecliptic_longitude)

    sun_eq = EclipticEquatorial.toEquatorial(sun_ec, a_datetime)

    an_observer = coords.spherical(1, a_latitude, a_longitude)

    sun_hz = EquatorialHorizon.toHorizon(sun_eq, an_observer, a_datetime)

    print 'sun alt', coords.angle(90) - sun_hz.theta # TODO rm

    eot = EquationOfTime(a_datetime)

    print 'eot', eot # TODO rm


    for d in xrange(1, 365): # skips some days

        a_datetime += 1

        eot = EquationOfTime(a_datetime)

        print eot # TODO rm
