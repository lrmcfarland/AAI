#!/usr/bin/env python

"""Transforms coordinates, Ecliptic, Equatorial and Horizontal

Sidereal Time

    http://en.wikipedia.org/wiki/Sidereal_time
    http://aa.usno.navy.mil/faq/docs/GAST.php
    http://aa.usno.navy.mil/data/docs/JulianDate.php

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
    sidereal_day = coords.angle(23, 56, 4.0916)


    def __init__(self, *args, **kwargs):
        # no instance data members so far.
        super(Transforms, self).__init__(*args, **kwargs)


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

    @classmethod
    def JulianCentury(cls, a_datetime):
        return (a_datetime.toJulianDate() - a_datetime.J2000)/36525.0


    @classmethod
    def GMST_USNO(cls, a_datetime):
        """Greenwich mean sidereal time

        from:
            http://aa.usno.navy.mil/faq/docs/GAST.php
            http://aa.usno.navy.mil/publications/docs/Circular_163.pdf

        see also:
            http://aa.usno.navy.mil/data/docs/JulianDate.php

        returns GMST in hours
        """

        JD = a_datetime.toJulianDate()

        # JDo is the Julian date of the previous midnight. Must end in 0.5
        JDfloor = math.floor(JD)
        if JD - JDfloor > 0.5:
            JDo = JDfloor + 0.5
        else:
            JDo = JDfloor - 0.5

        D = JD - a_datetime.J2000
        Do = JDo - a_datetime.J2000
        H = (JD - JDo)*24
        T = D/36525

        gmst = 6.697374558 + 0.06570982441908*Do + 1.00273790935*H + 0.000026*T*T

        gmst_hours = coords.angle(gmst)
        gmst_hours.normalize(-12, 12)

        return gmst_hours


    @classmethod
    def GMST_USNO_simplified(cls, a_datetime):
        """Greenwich mean sidereal time, simplified form

        from:
            http://aa.usno.navy.mil/faq/docs/GAST.php
            http://aa.usno.navy.mil/publications/docs/Circular_163.pdf


        see also http://en.wikipedia.org/wiki/Sidereal_time

        Returns GMST in hours
        """

        D = a_datetime.toJulianDate() - cls.J2000.toJulianDate()
        gmst = 18.697374558 + 24.06570982441908 * D # in hours
        gmst_hours = coords.angle(gmst)
        gmst_hours.normalize(-12, 12)

        return gmst_hours


    @classmethod
    def GMST_USNO_simplified2(cls, a_datetime):
        """Greenwich mean sidereal time, simplified

        This is the same as GMST_USNO but in degrees instead of hours,
        i.e. the terms are the same but divided by 15.

        from: http://www2.arnes.si/~gljsentvid10/sidereal.htm
        Keith Burnett (kburnett@btinternet.com) - 29 Jan 2002
        implementing Meeus formula 11.4

        This works for test data given above.

        Returns GMST in hours
        """

        D = a_datetime.toJulianDate() - cls.J2000.toJulianDate()
        gmst = 280.46061837 + 360.98564736629 * D # in degrees
        gmst_angle = coords.angle(gmst)
        gmst_angle.normalize(-180, 180)
        gmst_hours = coords.angle(gmst_angle.value/15.0)

        return gmst_hours


    @classmethod
    def GMST_APC(cls, a_datetime):
        """Greenwich mean sidereal time

        from Montenbruck and Pfleger, Astronomy on the Personal Computer, p. 40

        TODO my implementation doesn't match USNO results
        one day difference is much less than the expected 4 minutes

        First term matches USNO with coefficients converteted to hours
        (24110.54841/3600), others need further conversion?


        2451545 == 2000-01-01T12:00:00
        86400 = 60*60*24

        Returns GMST in hours

        """

        MJD = a_datetime.toJulianDate() - a_datetime.ModifiedJulianDate
        MJDo = math.floor(MJD)

        T = (MJD - 51544.5)/36525.0
        To = (MJDo - 51544.5)/36525.0

        UT = (T - To) * 86400.0 # TODO cls.siderial_day.value?

        gmst = 24110.54841 + 8640184.812866*To + 1.0027379093*UT + 0.093104*math.pow(T, 2.0) + 6.2e-6*math.pow(T, 3.0)

        # seconds
        print # linefeed
        print 'APC gmst', gmst # TODO rm

        gmst_hours = gmst/3600.0

        gmst_angle = coords.angle(gmst_hours)
        gmst_angle.normalize(-24, 24)

        return gmst_angle



class EquitorialHorizon(Transforms):

    """Transforms 3D space vectors to/from ecliptic/equatorial coordinates

    See also:
        http://en.wikipedia.org/wiki/Celestial_coordinate_system#Transformation_of_coordinates
        http://en.wikipedia.org/wiki/Celestial_coordinate_system#Equatorial_.E2.86.90.E2.86.92_horizontal

        http://en.wikipedia.org/wiki/Equatorial_coordinate_system
        http://star-www.st-and.ac.uk/~fv/webnotes/chapter7.htm

        http://www.stargazing.net/mas/al_az.htm
        http://stjarnhimlen.se/english.html


    """

    horizon_axis = coords.rotator(coords.Uy)

    def __init__(self, *args, **kwargs):
        super(EquitorialHorizon, self).__init__(*args, **kwargs)


    @classmethod
    def toHorizon_StA(cls, an_object, an_observer, a_local_datetime):
        """Transforms a vector from equatorial to ecliptic coordinates.

        from http://star-www.st-and.ac.uk/~fv/webnotes/chapter7.htm

        TODO: implementation not working

        Args:

        an_object: the vector to transform in theta (90 - declination),
                   phi (RA * 15). See self.radec2spherical.

        an_observer: the latitude and longitude (positive west of the
                     prime meridian) of an observer as a spherical
                     coordinate (unit radius)

        a_local_datetime: local date and time of the observation.

        Returns a spherical coordinate vector in the transformed coordinates
        """

        if not isinstance(an_object, coords.spherical):
            raise Error('vector must be in spherical coordinates') # TODO for now

        if not isinstance(an_observer, coords.spherical):
            raise Error('observer must be in spherical coordinates') # TODO for now

        print # linefeed

        print "an object's theta (90 - declination) =", an_object.theta.value
        print "an object's phi (RA * 15) =", an_object.phi.value

        print "an observers's theta (90 - latitude) =", an_observer.theta.value
        print "an observers's phi (longitude -W/+E) =", an_observer.phi.value

        gmst = Transforms.GMST_USNO(a_local_datetime) # hours

        print 'gmst', gmst, gmst.value # TODO rm

        local_hour_angle = coords.angle(gmst.value*15 + an_observer.phi.value - an_object.phi.value)

        print 'local_hour_angle', local_hour_angle # TODO rm

        print # linefeed
        print 'cos(90 - object declination)', math.cos(an_object.theta.radians)
        print 'sin(object declination)     ', math.sin(math.pi/2 - an_object.theta.radians)

        print # linefeed
        print 'sin(90 - object declination)', math.sin(an_object.theta.radians)
        print 'cos(object declination)     ', math.cos(math.pi/2 - an_object.theta.radians)

        print # linefeed
        print 'cos(90 - observer latitude) ', math.cos(an_observer.theta.radians)
        print 'sin(observer latitude)      ', math.sin(math.pi/2 - an_observer.theta.radians)

        print # linefeed
        print 'sin(90 - observer latitude) ', math.sin(an_observer.theta.radians)
        print 'cos(observer latitude)      ', math.cos(math.pi/2 - an_observer.theta.radians)

        print # linefeed
        print 'Altitude' # linefeed

        foo =  math.cos(an_object.theta.radians) * math.cos(an_observer.theta.radians) + \
               math.sin(an_object.theta.radians) * math.sin(an_observer.theta.radians) * \
               math.cos(local_hour_angle.radians)

        print 'foo 1', foo

        altitude = math.pi/2 - math.acos(foo)
        print 'altitude', altitude

        alt = coords.angle()
        alt.radians = altitude
        print 'alt', alt, alt.radians


        foo =  math.sin(math.pi/2 - an_object.theta.radians) * math.sin(math.pi/2 - an_observer.theta.radians) + \
               math.cos(math.pi/2 - an_object.theta.radians) * math.cos(math.pi/2 - an_observer.theta.radians) * \
               math.cos(local_hour_angle.radians)

        print # linefeed
        print 'foo 2', foo

        altitude = math.asin(foo)
        print 'altitude', altitude

        alt.radians = altitude
        print 'alt', alt, alt.radians

        print # linefeed
        print 'Azimuth'# linefeed

        # Azimuth by sine rule
        bar = -math.sin(local_hour_angle.radians)*math.cos(math.pi/2 - an_object.theta.radians)/math.cos(alt.radians)

        print 'bar 1', bar

        A = coords.angle()

        try:
            azimuth = math.asin(bar)
            print 'azimuth', azimuth
            A.radians = azimuth
            print 'A', A, A.radians
        except ValueError, err:
            print err

        print # linefeed

        # Azimuth by cosine rule

        bar = (math.sin(math.pi/2 - an_object.theta.radians) - \
               math.sin(math.pi/2 - an_observer.theta.radians)*math.sin(alt.radians))/ \
              (math.cos(math.pi/2 - an_observer.theta.radians)*math.cos(alt.radians))

        print 'bar 2', bar

        try:
            azimuth = math.acos(bar)
            print 'azimuth', azimuth
            A.radians = azimuth
            print 'A', A, A.radians
        except ValueError, err:
            print err


        print # linefeed

        # Azimuth by tan rule http://en.wikipedia.org/wiki/Celestial_coordinate_system#Equatorial_.E2.86.90.E2.86.92_horizontal

        bar = math.sin(local_hour_angle.radians)/ \
              (math.cos(alt.radians)*math.sin(math.pi/2 - an_observer.theta.radians) - \
               math.tan(math.pi/2 - an_object.theta.radians) *  math.cos(math.pi/2 - an_observer.theta.radians))

        print 'bar 3', bar

        try:
            azimuth = math.asin(bar)
            print 'azimuth', azimuth
            A.radians = azimuth
            print 'A', A, A.radians
        except ValueError, err:
            print err



    @classmethod
    def toEquitorial(cls, an_object, an_observer, a_local_datetime):
        """Transforms a vector from equatorial to ecliptic coordinates.

        from http://star-www.st-and.ac.uk/~fv/webnotes/chapter7.htm

        Args:

        an_object: the vector to transform in theta (90 - altitude),
                   phi (azimuth). See self.radec2spherical.

        an_observer: the latitude and longitude (positive west of the
                     prime meridian) of an observer as a spherical
                     coordinate (unit radius)

        a_local_datetime: local date and time of the observation.

        Returns a spherical coordinate vector in the transformed coordinates
        """

        if not isinstance(an_object, coords.spherical):
            raise Error('vector must be in spherical coordinates') # TODO for now

        if not isinstance(an_observer, coords.spherical):
            raise Error('observer must be in spherical coordinates') # TODO for now

        print # linefeed






    @classmethod
    def _xform_APC(cls, an_object, an_observer, a_local_datetime, a_direction):
        """Transforms a vector to/from equatorial/ecliptic coordinates.

        TODO my implementation of this APC algorithm isn't working

        Args:

        an_object: the vector to transform in theta (90 - declination),
                   phi (RA * 15). See self.radec2spherical.

        an_observer: the latitude and longitude (positive west of the
                     prime meridian) of an observer as a spherical
                     coordinate (unit radius)

        a_local_datetime: local date and time of the observation.

        a_direction: +1 to horizon, -1 from horizon

        Returns a vector in the transformed coordinates

        """

        if not isinstance(an_object, coords.spherical):
            raise Error('vector must be in spherical coordinates') # TODO for now

        if not isinstance(an_observer, coords.spherical):
            raise Error('observer must be in spherical coordinates') # TODO for now


        gmst = Transforms.GMST_USNO_simplified(a_local_datetime)

        hour_angle = coords.angle(gmst.value*15 + an_observer.phi.value - an_object.phi.value)
        hour_angle.normalize(0, 360)

        the_local_vector = coords.spherical(an_object.r, an_object.theta, hour_angle)

        the_rotatee = coords.Cartesian(the_local_vector)


        the_rotated = cls.horizon_axis.rotate(the_rotatee,
                                              coords.angle(a_direction * an_observer.theta.value))

        return coords.spherical(the_rotated)


    @classmethod
    def toHorizon_APC(cls, an_object, an_observer, a_local_datetime):
        """Transforms an equatorial vector into one in the horizon coordinate system"""
        return cls._xform_APC(an_object, an_observer, a_local_datetime, 1.0)


    @classmethod
    def fromHorizon_APC(cls, an_object, an_observer, a_local_datetime):
        """Transforms a horizon vector into one in the equatorial coordinate system"""
        return cls._xform_APC(an_object, an_observer, a_local_datetime, -1.0)




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

    # obliquity of the ecliptic terms are from http://en.wikipedia.org/wiki/Axial_tilt
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
        """Calculates the obliquity of the ecliptic given the datetime"""
        T = cls.JulianCentury(a_datetime)
        the_eps = 0
        for i in xrange(len(cls.obe)):
            the_eps += cls.obe[i].value * math.pow(T, i)
        return the_eps


    @classmethod
    def _xform(cls, an_object, a_datetime, a_direction):
        """Transforms a vector to/from equatorial/ecliptic coordinates.

        Args:
        an_object: the vector to transform. May be Cartesian or spherical.
        a_datetime: the time of the transformation
        a_direction: +1 to equatorial, -1 to ecliptic

        Returns a vector in the transformed coordinates
        """

        if isinstance(an_object, coords.spherical):
            the_rotatee = coords.Cartesian(an_object)
        else:
            the_rotatee = an_object

        the_rotated = cls.equinox_axis.rotate(the_rotatee,
                                              coords.angle(a_direction * cls.eps(a_datetime)))

        if isinstance(an_object, coords.spherical):
            return coords.spherical(the_rotated)
        else:
            return the_rotated


    @classmethod
    def toEcliptic(cls, an_object, a_datetime):
        """Transforms an_object from equatorial to ecliptic coordinates

        Returns a Cartesian vector in eliptic coordinates
        """
        return cls._xform(an_object, a_datetime, -1.0)


    @classmethod
    def toEquatorial(cls, an_object, a_datetime):
        """Transforms an_object from ecliptic to equatorial coordinates

        Returns a Cartesian vector in equatorial coordinates
        """
        return cls._xform(an_object, a_datetime, 1.0)



class StjarnHimlen(object):
    """Starry Sky

    from http://stjarnhimlen.se/comp/ppcomp.html

    How to convert Equitorial to Horizontal coordinates.
    Another method to help me sort out what is wrong with the others.

    Tack Paul!

    """

    def SolarLongitude(self, a_datetime):
        """Compute the position of the sun from the date"""

        print # linefeed
        print a_datetime # TODO rm

        d = a_datetime.toJulianDate() - a_datetime.J2000
        print 'd', d # TODO rm

        N = coords.angle(0.0) # longitude of the ascending node
        i = coords.angle(0.0) # inclination to the eclipitic
        w = coords.angle(282.9404 + 4.70935E-5 * d) # argument of perihelion
        w.normalize(0, 360)

        a = 1.000000 #  semi-major axis, or mean disntance from the Sun (AU)
        e = 0.016709 - 1.151E-9 * d # eccentricity

        print 'e', e

        M = coords.angle(356.0470 + 0.9856002585 * d) # mean anomaly
        M.normalize(0, 360)


        E = coords.angle(M.value + e *(180/math.pi) * math.sin(M.radians) * ( 1.0 + e * math.cos(M.radians) ))

        print 'E', E # TODO rm
        # E.normalize(0, 360) # TODO? Not necessary, sin/cos this
        print 'E.normalized', E # TODO rm

        xv = math.cos(E.radians) - e
        yv = math.sqrt(1.0 - e*e) * math.sin(E.radians)

        v = math.atan2(yv, xv)

        lonsun = v + w.value

        gmst0 = coords.angle(lonsun + 180)
        print 'gmst0', gmst0
        gmst0.normalize(0, 360)
        print 'gmst0 normalized', gmst0

        # TODO unnecessary from here to the return. Separate method?

        r = math.sqrt( xv*xv + yv*yv)

        print 'v', v # TODO rm
        print 'r', r # TODO rm
        print 'lonsun', lonsun # TODO rm

        xs = r * math.cos(lonsun)
        ys = r * math.sin(lonsun)

        ecl = coords.angle(23.4393 - 3.563E-7 * d) # TODO use JPL obliquit of the ecliptic?

        xe = xs
        ye = ys * math.cos(ecl.radians)
        ze = ys * math.sin(ecl.radians)

        RA = coords.angle(math.atan2(ye, xe))
        Dec = coords.angle(math.atan2(ze, math.sqrt(xe*xe+ye*ye)))

        print 'RA', RA, 'Dec', Dec # TODO rm

        return lonsun


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
