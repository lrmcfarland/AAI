#!/usr/bin/env python

""" Transforms from Astronomy on the Personal Computer (APC)
    by Montenbruck and Pfleger

to run:

TODO $ ./pylaunch.sh APCBodies.py -v -- 37:24 -122:04:57 2015-03-21T12:57:00-08


to validate:

    http://www.esrl.noaa.gov/gmd/grad/solcalc/

to test: ./pylaunch.sh test_APCBodies.py

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

    Returns the position of the sun in ecliptic coordinates (coords.spherical)
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


def MiniMoon(a_datetime):
    """Calculates the moon's RA and declination for the given datetime.

    from APC pp. 38-39

    Returns the position of the sun in ecliptic coordinates (coords.spherical)
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

    moon_ec = coords.spherical(1, apc_theta.complement(), apc_phi)

    return moon_ec




# ================
# ===== main =====
# ================


if __name__ == '__main__':

    # -------------------------
    # ----- parse options -----
    # -------------------------

    import optparse

    bodies = ('sun', 'moon')

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

    print 'A datetime: ', a_datetime
    print 'An observer:', an_observer

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


    else:

        print 'unknown option'
