#!/usr/bin/env python

"""Transforms from Astronomy on the Personal Computer (APC)
    by Montenbruck and Pfleger

This does not give good results for minisun when compared to
SunPosition or Star Walk or sextant readings.

to run:

    ./pylaunch.sh APCBodies.py -v -- 37:24 -122:04:57 2015-03-21T12:57:00-08

to validate:

    http://www.esrl.noaa.gov/gmd/grad/solcalc/

to test:

    ./pylaunch.sh test_APCBodies.py

"""

import math
import coords

from Transforms import EclipticEquatorial
from Transforms import EquatorialHorizon
from Transforms import utils


def Frac(x):
    return x - math.floor(x)


def Modulo(x, y):
    return y * cls.Frac(x/y)


def MiniSun(a_datetime):
    """Calculates the Sun's RA and declination for the given datetime.

    from APC p. 39

    a_datetime (coords.datetime): The time of the observation.

    Returns (coords.spherical): the position of the sun in ecliptic
    coordinates (ecliptic latitude and ecliptic longitude)

    """

    T = utils.JulianCentury(a_datetime)
    eps = coords.angle(EclipticEquatorial.eps(a_datetime))

    M = 2*math.pi * Frac(0.993133 + 99.997361*T) # Mean anomaly
    L = 2*math.pi * Frac(0.7859453 * M/(2*math.pi)
                         + (6893.0*math.sin(M)
                            + 72.0*math.sin(2.0*M)
                            + 6191.2*T)/1296.0e3)

    sun_azimuth = coords.angle()
    sun_azimuth.radians = L

    sun_ec = coords.spherical(1, coords.angle(90), sun_azimuth)

    return sun_ec


def SunPosition(an_observer, a_datetime):
    """Calculates the Sun's relative to the observer

    Args:

    an_observer (coords.spherical): the latitude and longitude
    (positive east of the prime meridian) of an observer as a
    spherical coordinate where theta is the complement of latitude and
    longitude is measured positive east in degrees.

    a_datetime (coords.datetime): The time of the observation.

    Returns (coords.spherical): the position in horizon coordinates.
    """

    sun_ec = MiniSun(a_datetime)
    sun_eq = EclipticEquatorial.toEquatorial(sun_ec, a_datetime)
    sun_hz = EquatorialHorizon.toHorizon(sun_eq, an_observer, a_datetime)

    return sun_hz


def MiniMoon(a_datetime):
    """Calculates the moon's RA and declination for the given datetime.

    from APC pp. 38-39

    a_datetime (coords.datetime): The time of the observation.

    Returns (coords.spherical): the position of the sun in ecliptic coordinates
    """

    T = utils.JulianCentury(a_datetime)

    Lo = Frac(0.606433 + 1336.855225 * T) # mean longitude

    lm = 2*math.pi * Frac(0.374897 + 1325.55241  * T) # Moon's mean anomaly
    ls = 2*math.pi * Frac(0.993133 +   99.997361 * T) # Sun's mean anomaly
    D  = 2*math.pi * Frac(0.827361 + 1236.853086 * T) # Diff. long. Moon - Sun
    F  = 2*math.pi * Frac(0.259086 + 1342.227825 * T) # Distance from ascending node

    # Perturbations in longitude and latitude

    dL = + 22640*math.sin(lm) - 4586*math.sin(lm - 2*D) + 2370*math.sin(2*D) + 769*math.sin(2*lm) \
         - 668*math.sin(ls) - 412*math.sin(2*F) - 212*math.sin(2*lm - 2*D) - 206*math.sin(lm + ls - 2*D) \
         + 192*math.sin(lm + 2*D) - 165*math.sin(ls - 2*D) - 125*math.sin(D) - 110*math.sin(lm + ls) \
         + 148*math.sin(lm - ls) - 55*math.sin(2*F - 2*D)

    apc_phi = coords.angle()
    apc_phi.radians = 2*math.pi * Frac(Lo + dL/1296.0e3) # a.k.a. Polar Az

    Arcs = 3600.0 * 180.0/math.pi

    S = F + (dL + 412*math.sin(2*F) + 541*math.sin(ls)) / Arcs
    h = F - 2*D
    N = - 526*math.sin(h) + 44*math.sin(lm + h) - 31*math.sin(-lm + h) - 23*math.sin(ls + h) \
        + 11*math.sin(-ls + h) - 25*math.sin(-2*lm + F) + 21*math.sin(-lm + F)

    apc_theta = coords.angle()
    apc_theta.radians = (18520.0*math.sin(S) + N) / Arcs # a.k.a. Polar Elev

    moon_ec = coords.spherical(1, apc_theta.complement(), apc_phi) # APC theta is to xy plane, not z axis.

    return moon_ec


def MoonPosition(an_observer, a_datetime):
    """Calculates the Moon's position relative to the observer

    an_observer (coords.spherical): the latitude and longitude
    (positive east of the prime meridian) of an observer as a
    spherical coordinate where theta is the complement of latitude and
    longitude is measured positive east in degrees.

    a_datetime (coords.datetime): The time of the observation.

    Returns (coords.spherical): the position  in horizon coordinates.
    """

    moon_ec = MiniMoon(a_datetime)
    moon_eq = EclipticEquatorial.toEquatorial(moon_ec, a_datetime)
    moon_hz = EquatorialHorizon.toHorizon(moon_eq, an_observer, a_datetime)

    return moon_hz



def RiseAndSetTimes(an_object, an_observer, a_datetime):
    """Calculates the rising and setting times

    APC p. 46

    Ignores refraction and parallax

    an_object (coords.spherical): in degrees from RA/dec.

    an_observer (coords.spherical): the latitude and longitude
    (positive east of the prime meridian) of an observer as a
    spherical coordinate where theta is the complement of latitude and
    longitude is measured positive east in degrees.

    a_datetime (coords.datetime): The time of the observation.

    Returns siderial time
    """


    hour_angle = coords.angle()





    return hour_angle




# ================
# ===== main =====
# ================


if __name__ == '__main__':

    # -------------------------
    # ----- parse options -----
    # -------------------------

    import optparse

    bodies = ('sun', 'moon', 'tbd')

    defaults = {'isVerbose': False,
                'body': 'sun'}

    usage = '%prog [options] <latitude> <longitude> <datetime>'

    parser = optparse.OptionParser(usage=usage)

    parser.add_option('-b', '--body',
                      action='store', dest='body',
                      type='choice', choices=bodies,
                      default=defaults['body'],
                      help='body %s' % (bodies,))

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

    # ------------------------------
    # ----- calculate position -----
    # ------------------------------

    print '# A datetime: ', a_datetime
    print '# An observer:', an_observer

    if options.body.lower() == 'sun':

        sun_ec = MiniSun(a_datetime)
        print 'Sun in ecliptic coordinates:\n\t', sun_ec

        sun_eq = EclipticEquatorial.toEquatorial(sun_ec, a_datetime)
        print 'Sun in equatorial coordinates:\n\t', sun_eq

        sun_hz = EquatorialHorizon.toHorizon(sun_eq, an_observer, a_datetime)
        print 'Sun in horizon coordinates:\n\t', sun_hz

        print 'Azimuth (degrees):', utils.get_azimuth(sun_hz),
        print ''.join(('(', str(utils.get_azimuth(sun_hz).value), ')'))
        print 'Altitude (degrees):', utils.get_altitude(sun_hz),
        print ''.join(('(', str(utils.get_altitude(sun_hz).value), ')'))

    elif options.body.lower() == 'moon':


        moon_ec = MiniMoon(a_datetime)
        print 'Moon in ecliptic coordinates:\n\t', moon_ec

        moon_eq = EclipticEquatorial.toEquatorial(moon_ec, a_datetime)
        print 'Moon in equatorial coordinates:\n\t', moon_eq

        moon_hz = EquatorialHorizon.toHorizon(moon_eq, an_observer, a_datetime)
        print 'Moon in horizon coordinates:\n\t', moon_hz

        print 'Azimuth (degrees):', utils.get_azimuth(moon_hz),
        print ''.join(('(', str(utils.get_azimuth(moon_hz).value), ')'))
        print 'Altitude (degrees):', utils.get_altitude(moon_hz),
        print ''.join(('(', str(utils.get_altitude(moon_hz).value), ')'))


    elif options.body.lower() == 'tbd':

        current_datetime = coords.datetime()

        for d in xrange(0, 100):

            current_datetime.fromJulianDate(a_datetime.toJulianDate() + 0.01*d)

            moon = MoonPosition(current_datetime, an_observer)

            print 0.01*d,
            print current_datetime,
            print utils.get_azimuth(moon).value,
            print utils.get_altitude(moon).value


    else:

        print 'unknown option'
