#!/usr/bin/env python

"""Calculates the position of the sun for the given datetime.

Uses algorithms from:
    Astronomical Algorithms 2ed, Jean Meeus 1998
    http://en.wikipedia.org/wiki/Position_of_the_Sun
    http://aa.usno.navy.mil/faq/docs/GAST.php

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

> spring <- read.table("./a_place.spring.txt")
> summer <- read.table("./a_place.summer.txt")
> fall <- read.table("./a_place.fall.txt")
> winter <- read.table("./a_place.winter.txt")
> plot(spring$V1, spring$V4, type="l", xlab="time of day", ylab="altitude in degrees", ylim=c(-100, 100), col="light green")
> lines(summer$V1, summer$V4, type="l", col="pink")
> lines(fall$V1, fall$V4, type="l", col="orange")
> lines(winter$V1, winter$V4, type="l", col="light blue")
> legend("topright", c("vernal equinox", "summer solstice", "autumnal equinox", "winter solstice"), lwd=c(1,1), col=c("light green", "red", "orange", "light blue"))
> title("Solar altitude")



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

import Transforms.EclipticEquatorial
import Transforms.EquatorialHorizon
import Transforms.utils


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

    an_observer (coords.spherical): the latitude (in degrees) and
    longitude of an observer as a spherical coordinate where theta
    is the complement of latitude and longitude is measured
    positive east. See utils.latlon2spherical.

    a_datetime (coords.datetime): The time of the observation.

    Returns (coords.spherical): the position of the sun in horizon coordinates.
    """

    ecliptic_longitude, R = SolarLongitude(a_datetime)

    sun_ec = coords.spherical(R, coords.angle(90), ecliptic_longitude)
    sun_eq = Transforms.EclipticEquatorial.toEquatorial(sun_ec, a_datetime)
    sun_hz = Transforms.EquatorialHorizon.toHorizon(sun_eq, an_observer, a_datetime)

    return sun_hz


def EquationOfTime(a_datetime):
    """Calcuate the equation of time

    from http://en.wikipedia.org/wiki/Equation_of_time

    TODO: Only valid for noon. Rounds to nearest half day.

    Args:

    a_datetime (coords.datetime): The time of the observation.

    Returns (coords.angle): equation of time as an angle in degrees. *60 for minutes.
    """

    noon = coords.datetime()
    noon.fromJulianDate(math.floor(a_datetime.toJulianDate()))
    gast = Transforms.SiderealTime.USNO_C163.GAST(noon)

    ecliptic_longitude, R = SolarLongitude(noon)

    sun_ec = coords.spherical(R, coords.angle(90), ecliptic_longitude)
    sun_eq = Transforms.EclipticEquatorial.toEquatorial(sun_ec, noon)

    eot = coords.angle()

    sun_ra = Transforms.utils.get_RA(sun_eq)

    if gast.value - sun_ra.value < 12:
        eot.value = gast.value - sun_ra.value

    elif gast.value - sun_ra.value >= 12:
        eot.value = gast.value - sun_ra.value - 24

    else:
        raise Error('unsupported EoT case')

    return eot


def SunRiseAndSet(an_observer, a_datetime):
    """Sun rise and set times

    Args:

    an_observer (coords.spherical): the latitude (in degrees) and
    longitude of an observer as a spherical coordinate where theta
    is the complement of latitude and longitude is measured
    positive east. See utils.latlon2spherical.


    a_datetime (coords.datetime): The time of the observation.

    Returns (coords.datetime, coords.datetime, coords.datetime) of
    rising, transit and setting in local time.
    """

    ecliptic_longitude, R = SolarLongitude(a_datetime)
    sun_ec = coords.spherical(R, coords.angle(90), ecliptic_longitude)
    sun_eq = Transforms.EclipticEquatorial.toEquatorial(sun_ec, a_datetime)

    return RiseAndSet(sun_eq, an_observer, a_datetime, an_altitude=coords.angle(-0.8333))


def RiseAndSet(an_object, an_observer, a_datetime, an_altitude=coords.angle(0)):
    """Rise and set times

    from Meeus, ch. 15

    # TODO problem with rounding to the wrong date some times of the
    year see test_SunPosition.py for examples. This error moves from
    rising to transit to setting starting 2018-02-01 among other
    times. Is back to being correct by 2016-06-01.

    # TODO more than just sun position, return local time, altitude
    # configurable to astronomical, nautical, civil, star, sun, moon

    # TODO error check for timezone and observer location?

    # TODO more steps on p. 103?
    # TODO set timezone on rising, transit, setting value

    Args:

    an_object: the vector to transform in theta (90 - declination),
    phi (RA * 15). See utils.radec2spherical.

    an_observer (coords.spherical): the latitude (in degrees) and
    longitude of an observer as a spherical coordinate where theta
    is the complement of latitude and longitude is measured
    positive east. See utils.latlon2spherical.

    a_datetime (coords.datetime): The time of the observation.

    an_altitude (coords.angle): The geometric center of the body at
    the time of rising (accounting for atmospheric refraction) where:
        ho = -0.5667 for point sources like stars
        ho = -0.8333 for the Sun.
        ho = +0.125  for the the moon, approximately.


    Returns (coords.datetime, coords.datetime, coords.datetime) of
    rising, transit and setting in local time.

    """

    JD, JDo = Transforms.SiderealTime.USNO_C163.JulianDate0(a_datetime)

    midnight = coords.datetime()
    midnight.fromJulianDate(JDo)

    observer_latitude = Transforms.utils.get_latitude(an_observer)
    observer_longitude = Transforms.utils.get_longitude(an_observer)

    object_RA = coords.angle(Transforms.utils.get_RA(an_object).value * 15) # in degrees
    object_declination = Transforms.utils.get_declination(an_object)

    gmst = Transforms.SiderealTime.USNO_C163.GMST(midnight)
    gmst.value *= 15 # in degrees

    cos_hour_angle = (math.sin(an_altitude.radians) \
        - math.sin(observer_latitude.radians) * math.sin(object_declination.radians)) \
        / (math.cos(observer_latitude.radians) * math.cos(object_declination.radians))

    if cos_hour_angle > 1:
        raise Error('object is circumpolar from this observation point')

    if cos_hour_angle < -1:
        raise Error('object is below the horizon from this observation point')

    hour_angle = coords.angle()
    hour_angle.radians = math.acos(cos_hour_angle)

    # longitude sign convention is IAU, opposite Meeus p. 93
    m0 = coords.angle((object_RA - observer_longitude - gmst).value/360.0)
    m0.normalize(0, 1)

    transit = coords.datetime(midnight.year, midnight.month, midnight.day,
                              0, 0, 0, a_datetime.timezone)
    transit += m0.value
    transit += a_datetime.timezone/24


    m1 = coords.angle(m0.value - hour_angle.value/360)
    m1.normalize(0, 1)

    rising = coords.datetime(midnight.year, midnight.month, midnight.day,
                             0, 0, 0, a_datetime.timezone)
    rising += m1.value
    rising += a_datetime.timezone/24.0

    # TODO a day too early on test_timezone_p6


    m2 = coords.angle(m0.value + hour_angle.value/360)
    # TODO m2.normalize(0, 1) ?
    # TODO a day to late in december if normalizing


    setting = coords.datetime(midnight.year, midnight.month, midnight.day,
                              0, 0, 0, a_datetime.timezone)
    setting += m2.value
    setting += a_datetime.timezone/24

    # TODO hack to fix datetime rounding error

    fixed_rising = coords.datetime(midnight.year, midnight.month, midnight.day,
                                   rising.hour, rising.minute, rising.second, rising.timezone)

    fixed_transit = coords.datetime(midnight.year, midnight.month, midnight.day,
                                    transit.hour, transit.minute, transit.second, transit.timezone)

    fixed_setting = coords.datetime(midnight.year, midnight.month, midnight.day,
                                    setting.hour, setting.minute, setting.second, setting.timezone)


    return fixed_rising, fixed_transit, fixed_setting


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

    an_observer = Transforms.utils.latlon2spherical(a_latitude=Transforms.utils.parse_angle_arg(args[0]),
                                                    a_longitude=Transforms.utils.parse_angle_arg(args[1]))

    a_datetime = coords.datetime(args[2])

    # ----------------------------------
    # ----- calculate sun position -----
    # ----------------------------------

    if options.output_mode.lower() == 'altitude':

        # a days worth of azimuth and altitude

        current_datetime = coords.datetime()

        for d in xrange(0, 100):

            current_datetime.fromJulianDate(a_datetime.toJulianDate() + 0.01*d)

            sun = SunPosition(an_observer, current_datetime)

            print 0.01*d,
            print current_datetime,
            print Transforms.utils.get_azimuth(sun).value,
            print Transforms.utils.get_altitude(sun).value


    elif options.output_mode.lower() == 'analemma':

        # a years worth of analemma data

        current_datetime = a_datetime

        # TODO duration option
        for d in xrange(1, 365):

            current_datetime += 1

            sun = SunPosition(an_observer, current_datetime)
            eot = EquationOfTime(current_datetime)

            print eot.value*60 + 180, Transforms.utils.get_altitude(sun).value


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

        print 'Obliquity of the ecliptic:', Transforms.EclipticEquatorial.obliquity(a_datetime)

        sun_ec = coords.spherical(R, coords.angle(90), ecliptic_longitude)
        print 'Sun in ecliptic coordinates:', sun_ec

        sun_eq = Transforms.EclipticEquatorial.toEquatorial(sun_ec, a_datetime)
        print 'Sun in equatorial coordinates:', sun_eq

        sun_hz = Transforms.EquatorialHorizon.toHorizon(sun_eq, an_observer, a_datetime)
        print 'Sun in horizon coordinates:', sun_hz

        sun_dec = coords.angle(90) - sun_eq.theta
        print 'Solar Declination:', sun_dec, ''.join(('(', str(sun_dec.value), ')'))

        eot = EquationOfTime(a_datetime)
        print 'Equation of time (minutes):', eot.value * 60

        print 'Azimuth (degrees):', Transforms.utils.get_azimuth(sun_hz),
        print ''.join(('(', str(Transforms.utils.get_azimuth(sun_hz).value), ')'))
        print 'Altitude (degrees):', Transforms.utils.get_altitude(sun_hz),
        print ''.join(('(', str(Transforms.utils.get_altitude(sun_hz).value), ')'))


        rising, transit, setting = SunRiseAndSet(an_observer, a_datetime)

        print 'Rising :', rising
        print 'Transit:', transit
        print 'Setting:', setting
