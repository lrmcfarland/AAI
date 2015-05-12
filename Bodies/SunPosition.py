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

Altitude:

$ ./pylaunch.sh SunPosition.py -- 37:24 0 2015-03-21T00:00:00 > altitude_2015.03.20.txt

Note: Series starts at midnight and 0 longitude to center noon w/o time zone.

$ r

> altitude03 <- read.table("altitude_2015.03.20.txt")
> altitude06 <- read.table("altitude_2015.06.21.txt")
> altitude09 <- read.table("altitude_2015.09.23.txt")
> altitude12 <- read.table("altitude_2015.12.22.txt")
> plot(altitude03$V1, altitude03$V3, type="l", xlab="time of day", ylab="altitude in degrees", ylim=c(-100, 100), col="light green")
> lines(altitude06$V1, altitude06$V3, type="l", col="pink")
> lines(altitude09$V1, altitude09$V3, type="l", col="orange")
> lines(altitude12$V1, altitude12$V3, type="l", col="light blue")
> legend("topright", c("vernal equinox", "summer solstice", "autumnal equinox", "winter solstice"), lwd=c(1,1), col=c("light green", "red", "orange", "light blue"))
> title("Solar altitude at 37N latitude")
> grid()


Analemma:

$ ./pylaunch.sh SunPosition.py -o analemma -- 45 0 2015-01-01T12:00:00 > analemma.txt

Note: Series starts at noon and 0 longitude to center noon w/o time zone.

> analemma <- read.table("analemma.txt")
> plot(analemma$V1, analemma$V2, type="l", xlab="Azimuth in degrees", ylab="Altitude in degrees", col="red")
> title("Analemma at 37N, 2015")
> grid()



EoT:

> eot <- read.table("eot.txt")
> plot(eot$V1, eot$V3, type="l", xlab="day of year", ylab="minutes", col="green")
> title("Equation of time 2015")
> grid()


"""

import math

import coords

from Transforms import EclipticEquatorial
from Transforms import EquatorialHorizon
from Transforms import SiderealTime
from Transforms import utils


class Error(Exception):
    pass


def SolarLongitude(a_datetime):
    """Calculate the longitude of the sun for the given date

    from http://en.wikipedia.org/wiki/Position_of_the_Sun

    Args:

    a_datetime (coords.datetime): The time of the observation.

    Returns (float, float): A tuple of the sun's longitude and distance in AU
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


def SunPosition(an_observer, a_datetime):
    """Calculate the location of the sun relaive to an observer

    Args:

    an_observer (coords.spherical): the latitude and longitude
    (positive east of the prime meridian) of an observer as a
    spherical coordinate where theta is the complement of latitude and
    longitude is measured positive east in degrees.

    a_datetime (coords.datetime): The time of the observation.

    Returns (coords.spherical): the position of the sun in horizon coordinates.
    """

    ecliptic_longitude, R = SolarLongitude(a_datetime)

    sun_ec = coords.spherical(R, coords.angle(90), ecliptic_longitude)
    sun_eq = EclipticEquatorial.toEquatorial(sun_ec, a_datetime)
    sun_hz = EquatorialHorizon.toHorizon(sun_eq, an_observer, a_datetime)

    return sun_hz


def RiseAndSet(an_object, an_observer, a_datetime):
    """Rise and set times

    Args:

    an_object (coords.spherical): in degrees from RA/dec.

    an_observer (coords.spherical): the latitude and longitude
    (positive east of the prime meridian) of an observer as a
    spherical coordinate where theta is the complement of latitude and
    longitude is measured positive east in degrees.

    a_datetime (coords.datetime): The time of the observation.

    Returns
    """


    JD, JDo = SiderealTime.USNO_C163.JulianDate0(a_datetime)

    midnight = coords.datetime()
    midnight.fromJulianDate(JDo)

    gmst = SiderealTime.USNO_C163.GMST(midnight)
    print 'usno gmst', gmst, 'in degrees', gmst.value * 15


    if False:
        altitude = 0 # TODO configurable to astronomical, nautical, civil et al.,

        observer_latitude = utils.get_latitude(an_observer)
        observer_longitude = utils.get_longitude(an_observer)

        object_RA = coords.angle(utils.get_RA(an_object).value * 15) # in degrees
        object_declination = utils.get_declination(an_object)

    else:
        # Meeus ex. 15.a

        altitude = coords.angle(-0.5667) # TODO configurable to astronomical, nautical, civil et al.,

        observer_latitude = coords.angle(42.3333)
        observer_longitude = coords.angle(-71.0833)

        object_RA = coords.angle(41.73129) # in degrees
        object_declination = coords.angle(18.44092)


    cos_hour_angle = (math.sin(altitude.radians) - \
                      math.sin(observer_latitude.radians)*math.sin(object_declination.radians)) \
        / math.cos(observer_latitude.radians)*math.cos(object_declination.radians)

    # TODO error check for circumpolar situations: cos_hour_angle not > -1 and < 1.
    print 'cos hour angle', cos_hour_angle


    hour_angle = coords.angle(math.acos(cos_hour_angle))
    print 'hour angle', hour_angle, 'for altitude', altitude

    print 'Object RA', object_RA
    print 'Observer Lattude', observer_latitude


    m0 = coords.angle((object_RA + observer_latitude - gmst).value/360.0)

    m0.normalize(0, 1)
    print 'm0', m0.value # TODO rm

    transit = gmst.value * 15 + 360.985647 * m0.value
    print 'transit', transit, 'in hours', transit/15 - 8 # TODO time zone adjust


    m1 = m0.value - hour_angle.value/360
    print 'm1', m1,  # TODO rm

    sunrise = gmst.value + 360.985647 * m1
    print 'sunrise', sunrise, 'in hours', sunrise/15 - 8 # TODO time zone adjust

    m2 = m0.value + hour_angle.value/360
    print 'm2', m2 # TODO rm

    sunset = gmst.value + 360.985647 * m2
    print 'sunset', sunset



    return None # TODO


def EquationOfTime(a_datetime):
    """Calcuate the equation of time

    from http://en.wikipedia.org/wiki/Equation_of_time

    TODO: Only valid at for noon. Rounds to nearest half day.

    Args:

    a_datetime (coords.datetime): The time of the observation.

    Returns (coords.angle): equation of time as an angle in degrees. *60 for minutes.
    """

    noon = coords.datetime()
    noon.fromJulianDate(math.floor(a_datetime.toJulianDate()))
    gast = SiderealTime.USNO_C163.GAST(noon)

    ecliptic_longitude, R = SolarLongitude(noon)

    sun_ec = coords.spherical(R, coords.angle(90), ecliptic_longitude)
    sun_eq = EclipticEquatorial.toEquatorial(sun_ec, noon)

    eot = coords.angle()

    sun_ra = utils.get_RA(sun_eq)

    if gast.value - sun_ra.value < 12:
        eot.value = gast.value - sun_ra.value

    elif gast.value - sun_ra.value >= 12:
        eot.value = gast.value - sun_ra.value - 24

    else:
        raise Error('unsupported EoT case')

    return eot


# ================
# ===== main =====
# ================


if __name__ == '__main__':

    # -------------------------
    # ----- parse options -----
    # -------------------------

    import optparse

    output_modes = ('altitude', 'analemma', 'eot', 'default')

    defaults = {'isVerbose': False,
                'output mode': 'default'}

    usage = '%prog [options] <latitude> <longitude> <datetime>'

    parser = optparse.OptionParser(usage=usage)

    parser.add_option('-v', '--verbose',
                      action='store_true', dest='verbose',
                      default=defaults['isVerbose'],
                      help='verbose [%default]')

    parser.add_option('-o', '--output-mode',
                      action='store', dest='output_mode',
                      type='choice', choices=output_modes,
                      default=defaults['output mode'],
                      help='output mode %s' % (output_modes,))

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

    if options.output_mode.lower() == 'altitude':

        # a days worth of azimuth and altitude

        current_datetime = coords.datetime()

        for d in xrange(0, 100):

            current_datetime.fromJulianDate(a_datetime.toJulianDate() + 0.01*d)

            sun = SunPosition(current_datetime, an_observer)

            print 0.01*d,
            print current_datetime,
            # print utils.get_azimuth(sun),
            print utils.get_altitude(sun).value


    elif options.output_mode.lower() == 'analemma':

        # a years worth of analemma data

        current_datetime = a_datetime

        # TODO duration option
        for d in xrange(1, 365):

            current_datetime += 1

            sun = SunPosition(current_datetime, an_observer)
            eot = EquationOfTime(current_datetime)

            print eot.value*60 + 180, utils.get_altitude(sun).value


    elif options.output_mode.lower() == 'eot':

        # years worth of equation of time data

        current_date = a_datetime

        # TODO duration option
        for d in xrange(1, 365):

            current_date += 1
            eot = EquationOfTime(current_date)

            print d, current_date, eot.value * 60


    else:

        # azimuth, altitude

        print 'A datetime: ', a_datetime, ''.join(('(', str(a_datetime.toJulianDate()), ')'))
        print 'An observer:', an_observer

        ecliptic_longitude, R = SolarLongitude(a_datetime)
        print 'Ecliptic longitude:', ecliptic_longitude
        print 'Distance in AU:', R

        sun_ec = coords.spherical(R, coords.angle(90), ecliptic_longitude)
        print 'Sun in ecliptic coordinates:\n\t', sun_ec


        sun_eq = EclipticEquatorial.toEquatorial(sun_ec, a_datetime)
        print 'Obliquity of the ecliptic:\n\t', EclipticEquatorial.obliquity(a_datetime)
        print 'Sun in equatorial coordinates:\n\t', sun_eq

        sun_hz = EquatorialHorizon.toHorizon(sun_eq, an_observer, a_datetime)
        print 'Sun in horizon coordinates:\n\t', sun_hz

        eot = EquationOfTime(a_datetime)
        print 'Equation of time (minutes):', eot.value * 60

        print 'Azimuth (degrees):', utils.get_azimuth(sun_hz),
        print ''.join(('(', str(utils.get_azimuth(sun_hz).value), ')'))
        print 'Altitude (degrees):', utils.get_altitude(sun_hz),
        print ''.join(('(', str(utils.get_altitude(sun_hz).value), ')'))


        foo = RiseAndSet(sun_ec, an_observer, a_datetime)

        print foo
