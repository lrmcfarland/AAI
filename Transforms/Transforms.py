#!/usr/bin/env python

"""Transforms coordinates, Ecliptic, Equatorial and Horizontal


Siderial Time

    http://aa.usno.navy.mil/faq/docs/GAST.php
    http://en.wikipedia.org/wiki/Sidereal_time


Equatorial Coordinate System http://en.wikipedia.org/wiki/Equatorial_coordinate_system
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

class Error(Exception):
    pass

class Transforms(object):
    """Base class for transforms

    Holds various static and class methods
    """

    J2000 = coords.datetime('2000-01-01T12:00:00') # starts at noon
    siderial_day = coords.angle(23, 56, 4.0916)


    def __init__(self, *args, **kwargs):
        # no instance data members so far.
        super(Transforms, self).__init__(*args, **kwargs)


    @classmethod
    def JulianCentury(cls, a_datetime):
        return (a_datetime.toJulianDate() - a_datetime.J2000)/36525.0


    @classmethod
    def GMST_APC(cls, a_datetime):
        """Greenwich mean siderial time

        from Montenbruck and Pfleger, Astronomy on the Personal Computer, p. 40

        2451545 == 2000-01-01T12:00:00
        86400 = 60*60*24

        TODO different from USNO by 2 degrees with kburnett data

        Returns TBD
        """

        MJD = a_datetime.toJulianDate() - a_datetime.ModifiedJulianDate
        MJDo = math.floor(MJD)

        T = (MJD - 51544.5)/36525.0
        To = (MJDo - 51544.5)/36525.0

        UT = (T - To) * 86400.0

        gmst = 24110.54841 + 8640184.812866*To + 1.0027379093*UT + 0.093104*math.pow(T, 2.0) + 6.2e-6*math.pow(T, 3.0)

        gmst_degrees = coords.angle(gmst)
        gmst_degrees.normalize(0, 360)

        return gmst_degrees


    @classmethod
    def GMST_USNO_simplified(cls, a_datetime):
        """Greenwich mean siderial time, simplified form

        from: http://aa.usno.navy.mil/faq/docs/GAST.php
              http://aa.usno.navy.mil/publications/docs/Circular_163.pdf

        see also http://en.wikipedia.org/wiki/Sidereal_time

        Returns GMST in hours

        TODO more complex version: GMST = 6.697374558 + 0.06570982441908 Do + 1.00273790935 H + 0.000026 T*T


        TODO return angle or hours?
        """

        D = a_datetime.toJulianDate() - cls.J2000.toJulianDate()
        gmst_hours = 18.697374558 + 24.06570982441908 * D
        gmst_angle = coords.angle(gmst_hours)
        gmst_angle.normalize(0, 24)

        return gmst_angle



    @classmethod
    def GMST_USNO_simplified2(cls, a_datetime):
        """Greenwich mean siderial time, simplified

        This is the same as GMST_USNO but in degrees instead of hours,
        i.e. the terms are the same but divided by 15.

        from: http://www2.arnes.si/~gljsentvid10/sidereal.htm
        Keith Burnett (kburnett@btinternet.com) - 29 Jan 2002
        implementing Meeus formula 11.4

        This works for test data given above.

        Returns GMST in hours

        TODO return degrees?
        """

        D = a_datetime.toJulianDate() - cls.J2000.toJulianDate()
        gmst_degrees = 280.46061837 + 360.98564736629 * D
        gmst_angle = coords.angle(gmst_degrees)
        gmst_angle.normalize(0, 360)
        gmst_hours = coords.angle(gmst_angle.value/15.0)

        return gmst_hours



    @staticmethod
    def spherical2latitude(a_point):
        """Converts spherical coordinate theta (angle to +z axis) to latitude/declination"""

        if not isinstance(a_point, coords.spherical):
            raise Error('a coordinate must be an instance of coords.spherical')

        return 90 - a_point.theta.value


    @staticmethod
    def spherical2longitude(a_point):
        """Converts spherical coordinate phi (angle to +x axis of projection in xy plane) to longitude"""

        if not isinstance(a_point, coords.spherical):
            raise Error('a coordinate must be an instance of coords.spherical')

        if a_point.phi.value < 0:
            return 360 + a_point.phi.value
        else:
            return a_point.phi.value


    @classmethod
    def spherical2ra(cls, a_point):
        """Converts spherical coordinate phi (angle to +x axis of projection in xy plane) to right ascension"""

        return cls.spherical2longitude(a_point)/15.0


    @staticmethod
    def radec2spherical(a_right_ascension, a_declination, a_radius = 1):
        """returns a spherical coordinate with the given right ascension and declination"""

        return coords.spherical(a_radius, coords.angle(90.0) - a_declination,
                                coords.angle(a_right_ascension.value * 15))



class Horizon(Transforms):

    """Transforms 3D space vectors to/from ecliptic/equatorial coordinates

    See also:

    http://en.wikipedia.org/wiki/Celestial_coordinate_system#Transformation_of_coordinates
    http://en.wikipedia.org/wiki/Equatorial_coordinate_system

    http://star-www.st-and.ac.uk/~fv/webnotes/chapter7.htm

    """

    horizon_axis = coords.rotator(coords.Uy)

    def __init__(self, *args, **kwargs):
        super(Horizon, self).__init__(*args, **kwargs)


    @classmethod
    def _xform_APC(cls, a_vector, an_observer, a_local_datetime, a_direction):
        """Transforms a vector to/from equatorial/ecliptic coordinates.

        TODO my implementation of this APC algorithm isn't working

        Args:

        a_vector: the vector to transform in theta (90 - declination),
                  phi (RA * 15). See self.radec2spherical.

        an_observer: the latitude and longitude (positive west of the
                     prime meridian) of an observer as a spherical
                     coordinate (unit radius)

        a_local_datetime: local date and time of the observation.

        a_direction: +1 to horizon, -1 from horizon

        Returns a vector in the transformed coordinates

        """

        if not isinstance(a_vector, coords.spherical):
            raise Error('vector must be in spherical coordinates') # TODO for now


        gmst = Transforms.GMST_USNO_simplified(a_local_datetime)

        hour_angle = coords.angle(gmst.value + an_observer.phi.value - a_vector.phi.value)
        hour_angle.normalize(0, 360)

        the_local_vector = coords.spherical(a_vector.r, a_vector.theta, hour_angle)

        the_rotatee = coords.Cartesian(the_local_vector)


        the_rotated = cls.horizon_axis.rotate(the_rotatee,
                                              coords.angle(a_direction * an_observer.theta.value))

        return coords.spherical(the_rotated)


    @classmethod
    def toHorizon_APC(cls, a_vector, an_observer, a_local_datetime):
        """Transforms an equatorial vector into one in the horizon coordinate system"""
        return cls._xform_APC(a_vector, an_observer, a_local_datetime, 1.0)


    @classmethod
    def fromHorizon_APC(cls, a_vector, an_observer, a_local_datetime):
        """Transforms a horizon vector into one in the equatorial coordinate system"""
        return cls._xform_APC(a_vector, an_observer, a_local_datetime, -1.0)


    @classmethod
    def toHorizon(cls, a_vector, an_observer, a_local_datetime):
        """Transforms a vector to/from equatorial/ecliptic coordinates.

        from http://star-www.st-and.ac.uk/~fv/webnotes/chapter7.htm

        Args:

        a_vector: the vector to transform in theta (90 - declination),
                  phi (RA * 15). See self.radec2spherical.

        an_observer: the latitude and longitude (positive west of the
                     prime meridian) of an observer as a spherical
                     coordinate (unit radius)

        a_local_datetime: local date and time of the observation.

        a_direction: +1 to horizon, -1 from horizon

        Returns a vector in the transformed coordinates

        """

        if not isinstance(a_vector, coords.spherical):
            raise Error('vector must be in spherical coordinates') # TODO for now

        # TODO positional astronomy



class EclipticEquatorial(Transforms):

    """Transforms 3D space vectors to/from ecliptic/equatorial coordinates

    ASSUMES: The x-axis points to vernal equinox. Positive rotations are right hand rule,
    Y x Z = X, i.e. counter clockwise looking down X.

    See also:
    http://aa.usno.navy.mil/publications/docs/Circular_163.pdf
    http://lambda.gsfc.nasa.gov/toolbox/tb_coordconv.cfm
    http://en.wikipedia.org/wiki/Axial_tilt

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

    def __init__(self, *args, **kwargs):
        super(EclipticEquatorial, self).__init__(*args, **kwargs)


    @classmethod
    def eps(cls, a_datetime):
        """Calculates the obliquty of the ecliptic given the datetime"""
        T = cls.JulianCentury(a_datetime)
        the_eps = 0
        for i in xrange(len(cls.obe)):
            the_eps += cls.obe[i].value * math.pow(T, i)
        return the_eps


    @classmethod
    def _xform(cls, a_vector, a_datetime, a_direction):
        """Transforms a vector to/from equatorial/ecliptic coordinates.

        Args:
        a_vector: the vector to transform. May be Cartesian or spherical.
        a_datetime: the time of the transformation
        a_direction: +1 to equatorial, -1 to ecliptic

        Returns a vector in the transformed coordinates
        """

        if isinstance(a_vector, coords.spherical):
            the_rotatee = coords.Cartesian(a_vector)
        else:
            the_rotatee = a_vector

        the_rotated = cls.equinox_axis.rotate(the_rotatee,
                                              coords.angle(a_direction * cls.eps(a_datetime)))

        if isinstance(a_vector, coords.spherical):
            return coords.spherical(the_rotated)
        else:
            return the_rotated


    @classmethod
    def toEcliptic(cls, a_vector, a_datetime):
        """Transforms a_vector from equatorial to ecliptic coordinates

        Returns a Cartesian vector in eliptic coordinates
        """
        return cls._xform(a_vector, a_datetime, -1.0)


    @classmethod
    def toEquatorial(cls, a_vector, a_datetime):
        """Transforms a_vector from ecliptic to equatorial coordinates

        Returns a Cartesian vector in equatorial coordinates
        """
        return cls._xform(a_vector, a_datetime, 1.0)



if __name__ == '__main__':

    # Actuals from http://lambda.gsfc.nasa.gov/toolbox/tb_coordconv.cfm

    eceq_xform = EclipticEquatorial()

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
    print 'latitude:', EclipticEquatorialTransforms.theta2latitude(some_point_ec),
    print 'longitude:', EclipticEquatorialTransforms.phi2longitude(some_point_ec)
    # latitude: -5:54:33.1307 longitude: 13:48:41.825 Good

    # Actual: Ecliptic  J2000 +00:00:00.00 Latitude(deg)   +15:00:00.00 Longitude(deg)
    #         Celestial J2000 +05:54:33.13 Latitude(deg)   +13:48:41.83 Longitude(deg)
    some_point_eq = eceq_xform.toEquatorial(some_point, j2000)
    print 'Equatorial(some point)', some_point_eq
    print 'latitude:', EclipticEquatorialTransforms.theta2latitude(some_point_eq),
    print 'longitude:', EclipticEquatorialTransforms.phi2longitude(some_point_eq)
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
    print 'latitude:', EclipticEquatorialTransforms.theta2latitude(some_point_ec),
    print 'longitude:', EclipticEquatorialTransforms.phi2longitude(some_point_ec)
    # latitude: -39:07:20.0238 longitude: 14:49:5.73744 Good

    # Actual: Ecliptic  J2015 -30:00:00.00 Latitude(deg)   +30:00:00.00 Longitude(deg)
    #         Celestial J2015 -16:38:58.75 Latitude(deg)   +38:28:49.79 Longitude(deg)
    some_point_eq = eceq_xform.toEquatorial(some_point, j2015)
    print 'Equatorial(some point)', some_point_eq
    print 'latitude:', EclipticEquatorialTransforms.theta2latitude(some_point_eq),
    print 'longitude:', EclipticEquatorialTransforms.phi2longitude(some_point_eq)
    # latitude: -16:38:58.7528 longitude: 38:28:49.7868 Good
