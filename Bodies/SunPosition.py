#!/usr/bin/env python

"""Calculates the position of the sun for the given datetime.

http://en.wikipedia.org/wiki/Position_of_the_Sun


to calculate:
    http://www.nrel.gov/docs/fy08osti/34302.pdf

to validate:

    http://www.esrl.noaa.gov/gmd/grad/solcalc/

to run:

$ ./pylaunch.sh SunPosition.py -v -- 37:24 -122:04:57 2015-03-21T12:57:00-08


Note: use -- to end options and allow for negative coordinates.


to plot:

$ ./pylaunch.sh SunPosition.py -- 37:24 0 2015-03-21T00:00:00 > altitude_2015.03.21.txt

> altitude <- read.table("altitude_2015.12.21.txt")
> altitude2 <- read.table("altitude_2015.06.21.txt")
> altitude3 <- read.table("altitude_2015.03.21.txt")
> plot(altitude$V1, altitude$V2, type="l", xlab="time", ylab="altitude", ylim=c(-100, 100), col="blue")
> lines(altitude2$V1, altitude2$V2, type="l", col="red")
> lines(altitude3$V1, altitude3$V2, type="l", col="green")
> title("Sun altitude at 37 Latitude")


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


def EquationOfTime(a_datetime, is_verbose=False):
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

    sun_ra = utils.get_RA(sun_eq)

    eot.value = gast.value - utils.get_RA(sun_eq).value

    ut = a_datetime.UT()

    if is_verbose:
        print # linefeed TODO rm
        print 'datetime', a_datetime
        print 'UT', ut, type(ut)
        print 'gast', gast
        print 'sun ra', sun_ra, sun_ra.value
        print 'eot', eot, eot.value*60
        eot.normalize(0, 24)
        print 'eot', eot, eot.value*60

    return eot


# ================
# ===== main =====
# ================


if __name__ == '__main__':

    # -------------------------
    # ----- parse options -----
    # -------------------------

    import optparse

    defaults = {'isVerbose': False}

    usage = '%prog [options] <latitude> <longitude> <datetime>'

    parser = optparse.OptionParser(usage=usage)

    parser.add_option('-v', '--verbose',
                      action='store_true', dest='verbose',
                      default=defaults['isVerbose'],
                      help='verbose [%default]')

    options, args = parser.parse_args()

    # ----- validate -----

    if len(args) < 3:
        parser.error('missing object and/or datetime.')

    an_observer = utils.latlon2spherical(a_latitude=utils.parse_angle_arg(args[0]),
                                         a_longitude=utils.parse_angle_arg(args[1]))

    a_datetime = coords.datetime(args[2])

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
        print 'an_observer', an_observer # TODO rm
        print 'sun hz', sun_hz # TODO rm

        print 'az', utils.get_azimuth(sun_hz), 'alt', utils.get_altitude(sun_hz)

        eot = EquationOfTime(a_datetime)

        print 'Equation of time', a_datetime, eot # TODO rm


    # a days worth of azimuth and altitude
    if False:

        current_datetime = coords.datetime()

        for d in xrange(0, 100):

            current_datetime.fromJulianDate(a_datetime.toJulianDate() + 0.01*d)

            ecliptic_longitude, R = SolarLongitude(current_datetime)

            sun_ec = coords.spherical(R, coords.angle(90), ecliptic_longitude)
            sun_eq = EclipticEquatorial.toEquatorial(sun_ec, current_datetime)
            sun_hz = EquatorialHorizon.toHorizon(sun_eq, an_observer, current_datetime)

            # print current_datetime,
            print 0.01*d,
            # print utils.get_azimuth(sun_hz),
            print utils.get_altitude(sun_hz).value



    # years worth of equation of time
    if False:

        current_date = a_datetime

        for d in xrange(1, 365):

            current_date += 1

            eot = EquationOfTime(current_date, is_verbose=options.verbose)

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
