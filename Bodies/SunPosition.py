#!/usr/bin/env python

"""Calculates the position of the sun for the given datetime.

http://en.wikipedia.org/wiki/Position_of_the_Sun

azimuth ok-ish, elevation 10 degrees off


to calculate:
    http://www.nrel.gov/docs/fy08osti/34302.pdf

to validate:

    http://www.esrl.noaa.gov/gmd/grad/solcalc/


to run: ./pylaunch.sh SunPosition.py -- 37:24 -122:4:57 2015-12-22T00:00:00

Note: use -- to end options and allow for negative coordinates.


to plot:

> analemma <- read.table("analemma.txt")
> plot(analemma$V2, analemma$V1, type="l", xlab="azimuth", ylab="altitude", col="red")
> title("Analemma, 37N")

> eot <- read.table("eot.txt")
> plot(eot$V1, eot$V3, type="l", xlab="day of year", ylab="minutes", col="blue")
> title("Equation of Time, 2015")


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
    g.normalize(0, 360)

    # ecliptic longitude
    ecliptic_longitude = coords.angle(L.value + 1.915*math.sin(g.radians) + 0.020*math.sin(2.0*g.radians))

    # distance to sun in AU
    R = 1.00014 - 0.01671*math.cos(g.radians) - 0.00014*math.cos(2.0*g.radians)

    return ecliptic_longitude, R


def EquationOfTime(a_datetime):
    """Calcuate the equation of time

    http://en.wikipedia.org/wiki/Equation_of_time

    "A mathematical discontinuity exists at noon."

    Rounds to nearst half day.

    Returns: equation of time as a coords angle.
    """

    noon = coords.datetime()
    noon.fromJulianDate(math.floor(a_datetime.toJulianDate()))

    gast = GMST.USNO_C163.GAST(noon)
    ecliptic_longitude, R = SolarLongitude(noon)

    sun_ec = coords.spherical(R, coords.angle(90), ecliptic_longitude)
    sun_eq = EclipticEquatorial.toEquatorial(sun_ec, noon)

    eot = coords.angle()

    eot.value = gast.value - utils.get_ra(sun_eq)

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

    an_observer = coords.spherical(1, a_latitude, a_longitude)

    # ----------------------------------
    # ----- calculate sun position -----
    # ----------------------------------

    # azimuth, altitude
    if True:
        ecliptic_longitude, R = SolarLongitude(a_datetime)
        print 'ecliptic longitude', ecliptic_longitude

        sun_ec = coords.spherical(R, coords.angle(90), ecliptic_longitude)
        print 'sun ec', sun_ec # TODO rm

        sun_eq = EclipticEquatorial.toEquatorial(sun_ec, a_datetime)
        print 'sun eq', sun_eq # TODO rm

        sun_hz = EquatorialHorizon.toHorizon(sun_eq, an_observer, a_datetime)
        print 'sun hz', sun_hz # TODO rm

        print 'az', sun_hz.phi, 'alt', coords.angle(90) - sun_hz.theta

        eot = EquationOfTime(a_datetime)

        print 'Equation of time', a_datetime, eot # TODO rm



    # years worth of equation of time
    if False:

        current_date = a_datetime

        for d in xrange(1, 365):

            current_date += 1

            eot = EquationOfTime(current_date)

            # TODO equation of time blows up near the vernal equinox
            if d < 79 or d > 81:
                print d, current_date, eot.value*60



    # analemma
    if False:

        current_date = a_datetime

        for d in xrange(1, 365):

            current_date += 1

            ecliptic_longitude, R = SolarLongitude(current_date)

            sun_ec = coords.spherical(R, coords.angle(90), ecliptic_longitude)
            sun_eq = EclipticEquatorial.toEquatorial(sun_ec, current_date)
            sun_hz = EquatorialHorizon.toHorizon(sun_eq, an_observer, current_date)

            # switch to astronomer coordinates
            eot = EquationOfTime(current_date)

            alt = coords.angle(90) - sun_hz.theta

            # TODO equation of time blows up near the vernal equinox
            if d < 79 or d > 81:
                print alt.value, eot.value*60 + 180
