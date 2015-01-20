#!/usr/bin/env python

""" Transforms from Astronomy on the Personal Computer (APC)
    by Montenbruck and Pfleger

    TODO: not all of my implementations of this are working. Check unittests.
"""

import math
import coords

import Transforms

class APCTransforms(object):

    horizon_axis = coords.rotator(coords.Uy)

    @classmethod
    def Frac(cls, x):
        return x - math.floor(x)


    @classmethod
    def Modulo(cls, x, y):
        return y * cls.Frac(x/y)


    @classmethod
    def GMST(cls, a_datetime):
        """Greenwich mean sidereal time

        APC p. 40

        Returns GMST in hours
        """

        MJD  = a_datetime.toJulianDate() - a_datetime.ModifiedJulianDate
        MJDo = math.floor(MJD)

        UT   = (MJD - MJDo) * 86400.0

        To   = (MJDo - 51544.5)/36525.0
        T    = (MJD  - 51544.5)/36525.0

        gmst = 24110.54841 + 8640184.812866*To + 1.0027379093*UT + (0.093104 - 6.2e-6*T)*T*T # in seconds

        gmst_angle = coords.angle(gmst/3600.0)

        gmst_angle.normalize(0, 24)

        return gmst_angle


    @classmethod
    def _xform(cls, an_object, an_observer, a_local_datetime, a_direction):
        """Transforms a vector to/from equatorial/ecliptic coordinates.

        TODO my implementation of this APC algorithm isn't working

        Args:

        an_object: the vector to transform in theta (90 - declination),
                   phi (RA * 15). See self.radec2spherical.

        an_observer: the latitude (90 - theta) and longitude (positive
                     east of the prime meridian) of an observer as a
                     spherical coordinate (unit radius)

        a_local_datetime: local date and time of the observation.

        a_direction: +1 to horizon, -1 from horizon

        Returns a vector in the transformed coordinates

        """

        if not isinstance(an_object, coords.spherical):
            raise Error('vector must be in spherical coordinates')

        if not isinstance(an_observer, coords.spherical):
            raise Error('observer must be in spherical coordinates')


        gmst = cls.GMST(a_local_datetime)

        hour_angle = coords.angle(gmst.value*15 - an_object.phi.value)

        the_local_vector = coords.spherical(an_object.r, an_object.theta, hour_angle)

        the_rotatee = coords.Cartesian(the_local_vector)


        the_rotated = cls.horizon_axis.rotate(the_rotatee,
                                              coords.angle(a_direction * an_observer.theta.value))

        the_result = coords.spherical(the_rotated)

        # "Note that Azimuth (A) is measured from the South point, turning positive to the West."
        # adjust azimuth to phi from the north
        the_result.phi += coords.angle(180)

        return the_result


    @classmethod
    def toHorizon(cls, an_object, an_observer, a_local_datetime):
        """Transforms an equatorial vector into one in the horizon coordinate system"""
        return cls._xform(an_object, an_observer, a_local_datetime, -1.0)


    @classmethod
    def toEquatorial(cls, an_object, an_observer, a_local_datetime):
        """Transforms a horizon vector into one in the equatorial coordinate system"""
        return cls._xform(an_object, an_observer, a_local_datetime, 1.0)




    @classmethod
    def MiniSun(cls, a_datetime):
        """Calculates the Sun's RA and declination


        from p. 39


        TODO generating data for an analemma:

        maximum altitude (minimum colatitude) is 2015-07-21 not 2015-06-21

        colatitude snaps from 70 to 79 on 2015-01-04.
        azimuth snaps from 178 to 97 on 2015-01-04.
        L snaps from 4.9 to 0.01 at the same time. Frac?

        """

        T = Transforms.Transforms.JulianCentury(a_datetime)
        eps = coords.angle(Transforms.EclipticEquatorial.eps(a_datetime))

        M = 2*math.pi * cls.Frac(0.993133 + 99.997361*T) # Mean anomaly
        L = 2*math.pi * cls.Frac(0.7859453 * M/(2*math.pi) + (6893.0*math.sin(M) + 72.0*math.sin(2.0*M) + 6191.2*T)/1296.0e3)

        sun_azimuth = coords.angle()
        sun_azimuth.radians = L

        sun = coords.spherical(1, coords.angle(90), sun_azimuth)

        sun_eq = Transforms.EclipticEquatorial.toEquatorial(sun, a_datetime)

        return sun_eq
