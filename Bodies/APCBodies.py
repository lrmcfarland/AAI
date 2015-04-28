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

    print 'A datetime: ', a_datetime
    print 'An observer:', an_observer

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
