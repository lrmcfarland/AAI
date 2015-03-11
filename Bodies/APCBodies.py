#!/usr/bin/env python

""" Transforms from Astronomy on the Personal Computer (APC)
    by Montenbruck and Pfleger

to test: ./pylaunch.sh test_APCBodies.py

TODO: not all of my implementations of this are working. Check unittests.
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


    TODO generating data for an analemma:

    maximum altitude (minimum colatitude) is 2015-07-21 not 2015-06-21

    colatitude snaps from 70 to 79 on 2015-01-04.
    azimuth snaps from 178 to 97 on 2015-01-04.
    L snaps from 4.9 to 0.01 at the same time. Frac?

    """

    T = utils.JulianCentury(a_datetime)
    eps = coords.angle(EclipticEquatorial.eps(a_datetime))

    M = 2*math.pi * Frac(0.993133 + 99.997361*T) # Mean anomaly
    L = 2*math.pi * Frac(0.7859453 * M/(2*math.pi) + (6893.0*math.sin(M) + 72.0*math.sin(2.0*M) + 6191.2*T)/1296.0e3)

    sun_azimuth = coords.angle()
    sun_azimuth.radians = L

    sun = coords.spherical(1, coords.angle(90), sun_azimuth)

    sun_eq = EclipticEquatorial.toEquatorial(sun, a_datetime)

    return sun_eq
