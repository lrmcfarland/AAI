#!/usr/bin/env python

"""Transforming ecliptic and equitorial coordinates

Equitorial Coordinate System http://en.wikipedia.org/wiki/Equatorial_coordinate_system
    right ascension http://en.wikipedia.org/wiki/Right_ascension
    declination http://en.wikipedia.org/wiki/Declination

Ecliptic Coordinate System http://en.wikipedia.org/wiki/Ecliptic_coordinate_system
    ecliptic longitude
    ecliptic latitude

to run: ./pylaunch.sh ecliptic.py

See also:
    http://en.wikipedia.org/wiki/Ecliptic
    http://en.wikipedia.org/wiki/Axial_tilt
    http://lambda.gsfc.nasa.gov/toolbox/tb_converters_ov.cfm
"""

import math
import coords

class EclipticEquitorialTransforms(object):

    """Transforms Cartesian space vectors to/from equitorial/ecliptic coordinates

    ASSUMES: The x-axis points to vernal equinox. Positive rotations are right hand rule,
    Y x Z = X, i.e. counter clockwise looking down X.
    """

    # x axis points to vernal equinox (the first point of Aries in this epoch)
    equinox_axis = coords.rotator(coords.Ux)

    # obliquiy of the ecliptic terms are from http://en.wikipedia.org/wiki/Axial_tilt
    obe = list()
    obe.append(coords.angle(23, 26, 21.45))
    obe.append(coords.angle(-1)*coords.angle(0, 0, 46.815)) # TODO no unary minus in boost wrappers
    obe.append(coords.angle(-1)*coords.angle(0, 0, 0.0006))
    obe.append(coords.angle(0, 0, 0.00181))
    # TODO more terms, updated


    def eps(self, a_datetime):
        """Calculates the obliquty of the ecliptic given the datetime"""
        T = (a_datetime.toJulianDate() - a_datetime.J2000)/36525.0
        the_eps = 0
        for i in xrange(len(self.obe)):
            the_eps += self.obe[i].value * math.pow(T, i)
        return the_eps


    def _xform(self, a_vector, a_datetime, a_direction):
        """Transforms a vector ecliptic to/from equitorial/ecliptic coordinates.

        Args:
        a_vector: the vector to transform
        a_datetime: the time of the transformation
        a_direction: +1 to equitorial, -1 to ecliptic

        Returns a vector in the transformed coordinates
        """
        if isinstance(a_vector, coords.spherical):
            the_rotatee = coords.Cartesian(a_vector)
        else:
            the_rotatee = a_vector

        the_rotated = self.equinox_axis.rotate(the_rotatee,
                                               coords.angle(a_direction * self.eps(a_datetime)))

        if isinstance(a_vector, coords.spherical):
            return coords.spherical(the_rotated)
        else:
            return the_rotated


    def toEcliptic(self, a_vector, a_datetime):
        """Transforms a_vector from equitorial to ecliptic coordinates

        Returns a Cartesian vector in eliptic coordinates
        """
        return self._xform(a_vector, a_datetime, -1.0)


    def toEquitorial(self, a_vector, a_datetime):
        """Transforms a_vector from ecliptic to equitorial coordinates

        Returns a Cartesian vector in equitorial coordinates
        """
        return self._xform(a_vector, a_datetime, 1.0)


    @staticmethod
    def theta2latitude(an_angle):
        """Converts spherical coordinate theta (angle to +z axis) to latitude/declination"""
        return coords.angle(90 - an_angle.theta.value)


    @staticmethod
    def phi2longitude(an_angle):
        """Converts spherical coordinate phi (angle to +x axis of projection in xy plane) to longitude"""
        if an_angle.phi.value < 0:
            return coords.angle(360 + an_angle.phi.value)
        else:
            return coords.angle(an_angle.phi.value)


if __name__ == '__main__':

    # Actuals from http://lambda.gsfc.nasa.gov/toolbox/tb_coordconv.cfm

    eceq_xform = EclipticEquitorialTransforms()

    j2000 = coords.datetime('2000-01-01T00:00:00')

    print "For datetime:", j2000

    print '='*20
    print 'J2000 Equator, 15'
    # Actual: Celestial J2000 +00:00:00.00 Latitude(deg)   +15:00:00.00 Longitude(deg)
    #         Ecliptic  J2000 -05:54:33.13 Latitude(deg)   +13:48:41.83 Longitude(deg)
    some_point = coords.spherical(1, coords.latitude(0), coords.angle(15))
    print 'some point:', some_point

    some_point_ec = eceq_xform.toEcliptic(some_point, j2000)
    print 'Ecliptic(some point)', some_point_ec
    print 'latitude:', EclipticEquitorialTransforms.theta2latitude(some_point_ec),
    print 'longitude:', EclipticEquitorialTransforms.phi2longitude(some_point_ec)
    # latitude: -5:54:33.1307 longitude: 13:48:41.825 Good

    # Actual: Ecliptic  J2000 +00:00:00.00 Latitude(deg)   +15:00:00.00 Longitude(deg)
    #         Celestial J2000 +05:54:33.13 Latitude(deg)   +13:48:41.83 Longitude(deg)
    some_point_eq = eceq_xform.toEquitorial(some_point, j2000)
    print 'Equitorial(some point)', some_point_eq
    print 'latitude:', EclipticEquitorialTransforms.theta2latitude(some_point_eq),
    print 'longitude:', EclipticEquitorialTransforms.phi2longitude(some_point_eq)
    # latitude: 05:54:33.1307 longitude: 13:48:41.825 Good


    j2015 = coords.datetime('2015-01-01T00:00:00')

    print "For datetime:", j2015

    print '='*20
    print 'J2015 latitude -30, longitude 30'
    # Actual: Celestial J2015 -30:00:00.00 Latitude(deg)   +30:00:00.00 Longitude(deg)
    #         Ecliptic  J2015 -39:07:20.02 Latitude(deg)   +14:49:05.74 Longitude(deg)
    some_point = coords.spherical(1, coords.declination(-30), coords.angle(30))
    print 'some point:', some_point

    some_point_ec = eceq_xform.toEcliptic(some_point, j2015)
    print 'Ecliptic(some point)', some_point_ec
    print 'latitude:', EclipticEquitorialTransforms.theta2latitude(some_point_ec),
    print 'longitude:', EclipticEquitorialTransforms.phi2longitude(some_point_ec)
    # latitude: -39:07:20.0238 longitude: 14:49:5.73744 Good

    # Actual: Ecliptic  J2015 -30:00:00.00 Latitude(deg)   +30:00:00.00 Longitude(deg)
    #         Celestial J2015 -16:38:58.75 Latitude(deg)   +38:28:49.79 Longitude(deg)
    some_point_eq = eceq_xform.toEquitorial(some_point, j2015)
    print 'Equitorial(some point)', some_point_eq
    print 'latitude:', EclipticEquitorialTransforms.theta2latitude(some_point_eq),
    print 'longitude:', EclipticEquitorialTransforms.phi2longitude(some_point_eq)
    # latitude: -16:38:58.7528 longitude: 38:28:49.7868 Good



