#!/usr/bin/env python

"""Transforms from Astronomy on the Personal Computer
    by Montenbruck and Pfleger

    TODO: not working yet.

"""

import math
import coords

class APCTransforms(object):

    horizon_axis = coords.rotator(coords.Uy)

    @classmethod
    def GMST(cls, a_datetime):
        """Greenwich mean sidereal time

        Does not match USNO GMST.
        Does have the correct delta for one day.

        Returns GMST in hours
        """

        MJD = a_datetime.toJulianDate() - a_datetime.ModifiedJulianDate
        MJDo = math.floor(MJD)

        T = (MJD - 51544.5)/36525.0
        To = (MJDo - 51544.5)/36525.0

        UT = (T - To) * 86400.0 # TODO cls.siderial_day.value?

        gmst = 24110.54841 + 8640184.812866*To + 1.0027379093*UT + 0.093104*math.pow(T, 2.0) + 6.2e-6*math.pow(T, 3.0) # in seconds

        gmst_angle = coords.angle()

        if False:
            # TODO almost original formula. Returns hours not
            # degrees. Does not match one day delta of 3:56 minutes
            def Frac(x):
                return x - math.floor(x)

            def Modulo(x, y):
                return y * Frac(x/y)

            gmst_angle.radians = (2*math.pi/86400.0)*Modulo(gmst, 86400.0)
            gmst_angle.normalize(0, 24)

        else:
            gmst_angle.value = gmst/3600.0
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

        hour_angle = coords.angle(gmst.value*15 + an_observer.phi.value - an_object.phi.value)
        hour_angle.normalize(0, 360)

        the_local_vector = coords.spherical(an_object.r, an_object.theta, hour_angle)

        the_rotatee = coords.Cartesian(the_local_vector)


        the_rotated = cls.horizon_axis.rotate(the_rotatee,
                                              coords.angle(a_direction * an_observer.theta.value))

        return coords.spherical(the_rotated)


    @classmethod
    def toHorizon(cls, an_object, an_observer, a_local_datetime):
        """Transforms an equatorial vector into one in the horizon coordinate system"""
        return cls._xform(an_object, an_observer, a_local_datetime, 1.0)


    @classmethod
    def fromHorizon(cls, an_object, an_observer, a_local_datetime):
        """Transforms a horizon vector into one in the equatorial coordinate system"""
        return cls._xform(an_object, an_observer, a_local_datetime, -1.0)


