#!/usr/bin/env python

"""Transforms coordinates, Ecliptic, Equatorial and Horizontal

to run: ./pylaunch.sh Transforms.py

References:

Sidereal Time
    http://en.wikipedia.org/wiki/Sidereal_time
    http://aa.usno.navy.mil/faq/docs/GAST.php
    http://aa.usno.navy.mil/data/docs/JulianDate.php
    http://aa.usno.navy.mil/publications/docs/Circular_163.pdf
    http://www.usno.navy.mil/USNO/astronomical-applications/publications/Circular_179.pdf

Celestial Coordinate System
    http://en.wikipedia.org/wiki/Celestial_coordinate_system#Transformation_of_coordinates
    http://en.wikipedia.org/wiki/Celestial_coordinate_system#Equatorial_.E2.86.90.E2.86.92_horizontal

Equatorial Coordinate System
    http://en.wikipedia.org/wiki/Equatorial_coordinate_system

Ecliptic Coordinate System
    http://en.wikipedia.org/wiki/Ecliptic
    http://en.wikipedia.org/wiki/Ecliptic_coordinate_system
    http://en.wikipedia.org/wiki/Axial_tilt

Validation:
    http://lambda.gsfc.nasa.gov/toolbox/tb_converters_ov.cfm
    http://aa.usno.navy.mil/cgi-bin/aa_jdconv.pl
    http://aa.usno.navy.mil/data/docs/siderealtime.php

See also:
    http://star-www.st-and.ac.uk/~fv/webnotes/chapter7.htm
    http://stjarnhimlen.se/english.html
    http://www2.arnes.si/~gljsentvid10/sidereal.htm

"""

import math
import coords

class Error(Exception):
    pass

class Transforms(object):
    """Base class for transforms"""

    J2000 = coords.datetime('2000-01-01T12:00:00') # starts at noon
    sidereal_day = coords.angle(23, 56, 4.0916)


    def __init__(self, *args, **kwargs):
        super(Transforms, self).__init__(*args, **kwargs)


    @staticmethod
    def spherical2latitude(a_point):
        """Spherical to latitude

        Converts spherical coordinate theta (angle to +z axis) to
        latitude/declination.

        """

        if not isinstance(a_point, coords.spherical):
            raise Error('a coordinate must be an instance of coords.spherical')

        return 90 - a_point.theta.value


    @staticmethod
    def spherical2longitude(a_point):
        """Spherical to longitude

        Converts spherical coordinate phi (angle to +x axis of
        projection in xy plane) to longitude.

        """

        if not isinstance(a_point, coords.spherical):
            raise Error('a coordinate must be an instance of coords.spherical')

        if a_point.phi.value < 0:
            return 360 + a_point.phi.value
        else:
            return a_point.phi.value


    @classmethod
    def spherical2ra(cls, a_point):
        """Spherical to right ascension

        Converts spherical coordinate phi (angle to +x axis of
        projection in xy plane) to right ascension.

        """

        return cls.spherical2longitude(a_point)/15.0


    @staticmethod
    def radec2spherical(a_right_ascension, a_declination, a_radius = 1):
        """returns a spherical coordinate with the given right ascension and declination"""

        return coords.spherical(a_radius, coords.angle(90.0) - a_declination,
                                coords.angle(a_right_ascension.value * 15))

    @classmethod
    def JulianCentury(cls, a_datetime):
        return (a_datetime.toJulianDate() - a_datetime.J2000)/36525.0


class USNO_C163(Transforms):
    """Transforms from the U.S. Naval Observatory

    from:
        http://aa.usno.navy.mil/faq/docs/GAST.php
        http://aa.usno.navy.mil/publications/docs/Circular_163.pdf

    validate with:
        http://aa.usno.navy.mil/data/docs/siderealtime.php

    TODO USNO_C179
    http://www.usno.navy.mil/USNO/astronomical-applications/publications/Circular_179.pdf

    """

    @classmethod
    def JulianDate0(cls, a_datetime):
        """Julian date of the previous midnight

        Returns the Julian Date and its previous midnight
        """

        JD = a_datetime.toJulianDate()
        JDfloor = math.floor(JD)

        # Must end in 0.5
        if JD - JDfloor > 0.5:
            JDo = JDfloor + 0.5
        else:
            JDo = JDfloor - 0.5

        return JD, JDo


    @classmethod
    def GMST(cls, a_datetime):
        """Greenwich mean sidereal time

        returns GMST in hours
        """

        JD, JDo = cls.JulianDate0(a_datetime)

        D = JD - a_datetime.J2000
        Do = JDo - a_datetime.J2000
        H = (JD - JDo)*24
        T = D/36525

        gmst = 6.697374558 + 0.06570982441908*Do + 1.00273790935*H + 0.000026*T*T

        gmst_hours = coords.angle(gmst - a_datetime.timezone())
        gmst_hours.normalize(0, 24)

        return gmst_hours


    @classmethod
    def GMST_simplified(cls, a_datetime):
        """Greenwich mean sidereal time, simplified form

        Returns GMST in hours
        """

        D = a_datetime.toJulianDate() - cls.J2000.toJulianDate()
        gmst = 18.697374558 + 24.06570982441908 * D # in hours
        gmst_hours = coords.angle(gmst)
        gmst_hours.normalize(-12, 12)

        return gmst_hours


    @classmethod
    def GMST_simplified2(cls, a_datetime):
        """Greenwich mean sidereal time, simplified

        This is the same as GMST_USNO but in degrees instead of hours,
        i.e. the terms are the same but divided by 15.

        from: http://www2.arnes.si/~gljsentvid10/sidereal.htm
        Keith Burnett (kburnett@btinternet.com) - 29 Jan 2002
        implementing Meeus formula 11.4

        This works for test data given in the example, but the date is
        out of range for validation from
        http://aa.usno.navy.mil/data/docs/siderealtime.php

        The APC algorithm also gives different results for the test
        date (see test_Transforms.py, USNO_test_GMST_kb.test_GMST_kb
        vs. APC.test_GMST_kb

        Returns GMST in hours

        """

        D = a_datetime.toJulianDate() - cls.J2000.toJulianDate()
        gmst = 280.46061837 + 360.98564736629 * D # in degrees
        gmst_angle = coords.angle(gmst)
        gmst_angle.normalize(-180, 180)
        gmst_hours = coords.angle(gmst_angle.value/15.0)

        return gmst_hours


    @classmethod
    def GAST(cls, a_datetime):
        """Greenwich apparent sidereal time"""

        gmst = cls.GMST(a_datetime)

        JD, JDo = cls.JulianDate0(a_datetime)
        D = JD - a_datetime.J2000
        eps = coords.angle(23.4393 - 0.0000004*D) # TODO JPL eps?
        L = coords.angle(280.47 + 0.98565*D)
        omega = coords.angle(125.04 - 0.052954*D)
        eqeq = coords.angle((-0.000319*math.sin(omega.radians) - 0.000024*math.sin(2*L.radians))*math.cos(eps.radians))

        gast = gmst + eqeq

        return gast


    @classmethod
    def LSTM(cls, a_datetime, an_observer):
        """Local sidereal time, mean

        Args:

        a_datetime: local date and time of the observation.

        an_observer: the latitude (90 - theta) and longitude (phi,
                     positive east of the prime meridian) of an
                     observer as a spherical coordinate (unit radius)

        """

        gmst = cls.GMST(a_datetime)
        lst = gmst + coords.angle(an_observer.phi.value/15)
        lst.normalize(0, 24)
        return lst


    @classmethod
    def LSTA(cls, a_datetime, an_observer):
        """Local sidereal time, apparent

        Args:

        a_datetime: local date and time of the observation.

        an_observer: the latitude (90 - theta) and longitude (phi,
                     positive east of the prime meridian) of an
                     observer as a spherical coordinate (unit radius)

        """

        gast = cls.GAST(a_datetime)
        lst = gast + coords.angle(an_observer.phi.value/15)
        lst.normalize(0, 24)
        return lst


class StjarnHimlen(Transforms):
    """Starry Sky: How to convert Equatorial to Horizontal coordinates.

    from http://stjarnhimlen.se/comp/ppcomp.html

    Another method to help me sort out what is wrong with the others.
    Tack Paul!

    TODO: The solar calculations agree with
    http://www.satellite-calculations.com/Satellite/suncalc.htm,
    but the GMST delta is about 8 seconds too long see
    TestStjarnHimlen.test_GMST_J2000_plus_day

    """

    @classmethod
    def SolarLongitude(cls, a_datetime):
        """Calculate the longitude of the sun for the given date

        returns the sun's longitude
        """

        d = a_datetime.toJulianDate() - a_datetime.J2000

        w = 282.9404 + 4.70935E-5 * d # argument of perihelion
        e = 0.016709 - 1.151E-9 * d # eccentricity
        M = coords.angle(356.0470 + 0.9856002585 * d) # mean anomaly
        E = coords.angle(M.value + e * (180/math.pi) * math.sin(M.radians) * ( 1.0 + e * math.cos(M.radians) ))

        xv = math.cos(E.radians) - e
        yv = math.sqrt(1.0 - e*e) * math.sin(E.radians)

        v = math.atan2(yv, xv)*180/math.pi

        lonsun = coords.angle(v + w)
        lonsun.normalize(0, 360) # flips to 0 on March 21 2000, not quite equinox

        return lonsun


    def SolarRADec(cls, a_datetime):
        """Calculate the right ascension and declination of the sun for the given date

        returns the sun's RA and declination
        """

        d = a_datetime.toJulianDate() - a_datetime.J2000

        w = 282.9404 + 4.70935E-5 * d # argument of perihelion
        e = 0.016709 - 1.151E-9 * d # eccentricity
        M = coords.angle(356.0470 + 0.9856002585 * d) # mean anomaly
        E = coords.angle(M.value + e * (180/math.pi) * math.sin(M.radians) * ( 1.0 + e * math.cos(M.radians) ))

        xv = math.cos(E.radians) - e
        yv = math.sqrt(1.0 - e*e) * math.sin(E.radians)

        v = math.atan2(yv, xv)*180/math.pi

        lonsun = coords.angle(v + w)

        r = math.sqrt( xv*xv + yv*yv)

        xs = r * math.cos(lonsun.radians)
        ys = r * math.sin(lonsun.radians)

        ecl = coords.angle(23.4393 - 3.563E-7 * d) # TODO use JPL obliquity of the ecliptic?

        xe = xs
        ye = ys * math.cos(ecl.radians)
        ze = ys * math.sin(ecl.radians)

        RA = coords.angle(math.atan2(ye, xe)*180/math.pi)
        RA.normalize(0, 360)

        Dec = coords.angle(math.atan2(ze, math.sqrt(xe*xe+ye*ye))*180/math.pi)

        return RA, Dec # TODO as coords.spherical(1, Longitue(Dec), RA)?


    @classmethod
    def GMST0(cls, a_datetime):
        """Calculate the Greenwich mean siderial time at Greenwich"""

        lonsun = cls.SolarLongitude(a_datetime)
        gmst0 = coords.angle(lonsun.value + 180) # TODO noon or midnight vs. GMST USNO
        gmst0.normalize(0, 360) # TODO as hours?

        return gmst0

    @classmethod
    def GMST(cls, a_datetime):
        """Calculate the Greenwich mean siderial time at location"""

        gmst0 = cls.GMST0(a_datetime)

        d = a_datetime.toJulianDate() - a_datetime.J2000

        gmst = coords.angle(gmst0.value/15 + d*24) # cls.sidereal_day.value) # TODO siderial day?
        gmst.normalize(-12, 12) # TODO as degrees?

        return gmst


    @classmethod
    def toHorizon(cls, an_object, an_observer, a_local_datetime):
        """Transforms a vector from equatorial to ecliptic coordinates.

        from http://stjarnhimlen.se/comp/ppcomp.html


        Args:

        an_object: the vector to transform in theta (90 - declination),
                   phi (RA * 15). See self.radec2spherical.

        an_observer: the latitude (90 - theta) and longitude (positive
                     east of the prime meridian) of an observer as a
                     spherical coordinate (unit radius)

        a_local_datetime: local date and time of the observation.

        Returns a spherical coordinate vector in the transformed coordinates

        """

        print # linefeed
        print 'object', an_object # TODO rm
        print 'observer', an_observer # TODO rm
        print 'a time', a_local_datetime # TODO rm

        # Big difference which GMST is being used! Stjarn Himeln's day
        # is 8 seconds longer that actual.

        gmst = cls.GMST(a_local_datetime)

        # gmst = USNO.GMST(a_local_datetime)

        print 'gmst', gmst # TODO rm

        lst = gmst.value + an_observer.phi.value/15

        # lst = 19.2242 # TODO USNO LSTA for 2014-12-31T20:41:00

        print 'lst', lst # TODO rm

        ha = coords.angle(360*(lst - an_object.phi.value/15)/24) # degrees?
        ha.normalize(-180, 180)

        print 'ha', ha, ha.radians

        dec = coords.angle(90 - an_object.theta.value)

        print 'dec', dec

        x = math.cos(ha.radians) * math.cos(dec.radians)
        y = math.sin(ha.radians) * math.cos(dec.radians)
        z = math.sin(dec.radians)

        xhor = x * math.sin(math.pi/2 - an_observer.theta.radians) - z * math.cos(math.pi/2 - an_observer.theta.radians)
        yhor = y
        zhor = x * math.cos(math.pi/2 - an_observer.theta.radians) + z * math.sin(math.pi/2 - an_observer.theta.radians)

        az = coords.angle((math.atan2(yhor, xhor) + math.pi)*180/math.pi)

        print 'az', az

        alt = coords.angle(math.asin(zhor)*180/math.pi) # or

        print 'alt', alt

        alt = coords.angle(math.atan2(zhor, math.sqrt(xhor*xhor + yhor*yhor))*180/math.pi)

        print 'alt', alt




class APC(Transforms):
    """Transforms from Astronomy on the Personal Computer

    by Montenbruck and Pfleger
    """

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

        from Montenbruck and Pfleger, Astronomy on the Personal Computer, p. 40

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


class EquatorialHorizon(Transforms):

    """Transforms 3D space vectors to/from ecliptic/equatorial coordinates"""

    horizon_axis = coords.rotator(coords.Uy)

    @classmethod
    def toHorizon(cls, an_object, an_observer, a_local_datetime):
        """Transforms a vector from equatorial to ecliptic coordinates.

        from http://star-www.st-and.ac.uk/~fv/webnotes/chapter7.htm

        But I think it is incorrect in calculating the Local Hour Angle.
        I observed Sirius on New Years Eve 2015 at 8pm and measured its
        altitude and azimuth using a theodolite app on my iPhone. I got

        Date & Time: Wed Dec 31 20:41:41 PST 2014
        Position: +037.40015* / -122.08219*
        Altitude: 56ft
        Azimuth/Bearing: 127* S53E 2258mils (True)
        Elevation Angle: +18.1*

        By happy coincidence, Sirius was on/near my local
        meridian. due south, at midnight new years eve when I measured
        it with my theodolite app at 8:41 pm above.

        According to http://star-www.st-and.ac.uk/~fv/webnotes/chapter6.htm
        an alternative definition of LST is "Local Sidereal Time =
        Right Ascension of whichever stars are on the meridian."
        Therefore, local sidereal time == right ascension of Sirius ==
        6* 45' 9"

        But according to http://aa.usno.navy.mil/data/docs/siderealtime.php
        this is my Greenwich Mean Sidereal Time; my local sidereal
        time is 22h 32m 59.9s.


        If I let my Local Hour Angle = GMST - RA(star) this matches my
        observed results.


        Args:

        an_object: the vector to transform in theta (90 - declination),
                   phi (RA * 15). See self.radec2spherical.

        an_observer: the latitude (90 - theta) and longitude (positive
                     east of the prime meridian) of an observer as a
                     spherical coordinate (unit radius)

        a_local_datetime: local date and time of the observation.

        Returns a spherical coordinate vector in the transformed coordinates

        """

        if not isinstance(an_object, coords.spherical):
            raise Error('vector must be in spherical coordinates') # TODO for now

        if not isinstance(an_observer, coords.spherical):
            raise Error('observer must be in spherical coordinates') # TODO for now

        print # linefeed # TODO rm

        print "object's theta (90 - declination) =", an_object.theta.value # TODO rm
        print "object's phi (RA * 15) =", an_object.phi.value # TODO rm

        print "observer's theta (90 - latitude) =", an_observer.theta.value # TODO rm
        print "observer's phi (longitude -W/+E) =", an_observer.phi.value # TODO rm

        print "observer's local time", a_local_datetime # TODO rm

        print # linefeed TODO rm

        gmst = USNO_C163.GMST(a_local_datetime) # hours
        local_hour_angle = coords.angle(gmst.value*15 - an_object.phi.value) # TODO

        print 'local hour angle', local_hour_angle # TODO rm

        print '\nAltitude' # TODO rm
        print 'Cosine rule' # TODO rm

        altitude = coords.angle()

        foo =  math.cos(an_object.theta.radians) * math.cos(an_observer.theta.radians) + \
               math.sin(an_object.theta.radians) * math.sin(an_observer.theta.radians) * \
               math.cos(local_hour_angle.radians)

        altitude.radians = math.pi/2 - math.acos(foo)
        print 'altitude', altitude # TODO rm

        print # linefeed # TODO rm
        print 'Simplified Cosine rule' # TODO rm

        foo =  math.sin(math.pi/2 - an_object.theta.radians) * math.sin(math.pi/2 - an_observer.theta.radians) + \
               math.cos(math.pi/2 - an_object.theta.radians) * math.cos(math.pi/2 - an_observer.theta.radians) * \
               math.cos(local_hour_angle.radians)

        altitude.radians = math.asin(foo)
        print 'altitude', altitude

        print # linefeed # TODO rm
        print 'Azimuth'# linefeed # TODO rm
        azimuth = coords.angle()

        # Azimuth by sine rule, 0 is south
        print 'Sine rule' # TODO rm
        bar = -math.sin(local_hour_angle.radians)*math.cos(math.pi/2 - an_object.theta.radians)/math.cos(altitude.radians)

        azimuth.radians = math.asin(bar)
        azimuth.normalize(0, 360)
        print 'azimuth', azimuth # TODO rm

        print # linefeed # TODO rm

        # Azimuth by cosine rule, 0 is north, angle is counter clock wise (right hand rule)
        print 'Cosine rule' # TODO rm

        bar = (math.sin(math.pi/2 - an_object.theta.radians) - \
               math.sin(math.pi/2 - an_observer.theta.radians)*math.sin(altitude.radians))/ \
              (math.cos(math.pi/2 - an_observer.theta.radians)*math.cos(altitude.radians))

        azimuth.radians = math.acos(bar)
        print 'azimuth', azimuth # TODO rm

        print # linefeed # TODO rm
        print 'Tan rule' # TODO rm
        # Azimuth by tan rule http://en.wikipedia.org/wiki/Celestial_coordinate_system#Equatorial_.E2.86.90.E2.86.92_horizontal

        bar = math.sin(local_hour_angle.radians)/ \
              (math.cos(altitude.radians)*math.sin(math.pi/2 - an_observer.theta.radians) - \
               math.tan(math.pi/2 - an_object.theta.radians) *  math.cos(math.pi/2 - an_observer.theta.radians))

        azimuth.radians = math.tan(bar)
        print 'azimuth', azimuth # TODO rm



    @classmethod
    def toEquatorial(cls, an_object, an_observer, a_local_datetime):
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

        # TODO implement this



class EclipticEquatorial(Transforms):

    """Transforms 3D space vectors to/from ecliptic/equatorial coordinates

    ASSUMES: The x-axis points to vernal equinox. Positive rotations are right hand rule,
    Y x Z = X, i.e. counter clockwise looking down X.

    from:
        http://en.wikipedia.org/wiki/Axial_tilt

    See also:
        http://lambda.gsfc.nasa.gov/toolbox/tb_coordconv.cfm
        http://aa.usno.navy.mil/publications/docs/Circular_163.pdf

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
