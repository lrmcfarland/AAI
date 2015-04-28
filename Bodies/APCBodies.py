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
from Transforms import utils


def Frac(x):
    return x - math.floor(x)


def Modulo(x, y):
    return y * cls.Frac(x/y)


def MiniSun(a_datetime):
    """Calculates the Sun's RA and declination


    from p. 39

    """

    T = utils.JulianCentury(a_datetime)
    eps = coords.angle(EclipticEquatorial.eps(a_datetime))

    M = 2*math.pi * Frac(0.993133 + 99.997361*T) # Mean anomaly
    L = 2*math.pi * Frac(0.7859453 * M/(2*math.pi) + (6893.0*math.sin(M) + 72.0*math.sin(2.0*M) + 6191.2*T)/1296.0e3)

    sun_azimuth = coords.angle()
    sun_azimuth.radians = L

    sun_ec = coords.spherical(1, coords.angle(90), sun_azimuth)

    return sun_ec
