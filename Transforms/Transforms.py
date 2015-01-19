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

        Returns a double value equal to the latitude.
        """

        if not isinstance(a_point, coords.spherical):
            raise Error('a coordinate must be an instance of coords.spherical')

        return 90 - a_point.theta.value


    @staticmethod
    def spherical2longitude(a_point):
        """Spherical to longitude

        Converts spherical coordinate phi (angle to +x axis of
        projection in xy plane) to longitude.

        Returns a double value equal to the longitude.
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

        Returns a double value equal to the right ascension.
        """

        return cls.spherical2longitude(a_point)/15.0


    @staticmethod
    def radec2spherical(a_right_ascension, a_declination, a_radius = 1):
        """Converts a given right ascension and declination into spherical coordinates

        Declination measured from the ecliptic is converted to theta
        measured from the north pole.

        Right ascension measured in hours is converted into degrees and assigned
        to phi.

        Returns the spherical coordinate.

        """
        return coords.spherical(a_radius, coords.angle(90.0) - a_declination,
                                coords.angle(a_right_ascension.value * 15))

    @classmethod
    def JulianCentury(cls, a_datetime):
        """Calculates the Julian century relative to J2000 of the given date

        Args:

        a_datetime: local date and time of the observation.

        Returns a double equal to the Julian century.
        """
        return (a_datetime.toJulianDate() - a_datetime.J2000)/36525.0

# =====================
# ===== USNO C163 =====
# =====================

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
        """Julian date and the previous midnight

        Args:

        a_datetime: local date and time of the observation.

        Returns a tuple of the Julian Date and its previous midnight
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
        """Greenwich mean sidereal time (GMST)

        Args:

        a_datetime: local date and time of the observation.

        Returns GMST as an angle in hours
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

        Args:

        a_datetime: local date and time of the observation.

        Returns GMST as an angle in hours
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

        Args:

        a_datetime: local date and time of the observation.

        Returns GMST as an angle in hours
        """

        D = a_datetime.toJulianDate() - cls.J2000.toJulianDate()
        gmst = 280.46061837 + 360.98564736629 * D # in degrees
        gmst_angle = coords.angle(gmst)
        gmst_angle.normalize(-180, 180)
        gmst_hours = coords.angle(gmst_angle.value/15.0)

        return gmst_hours


    @classmethod
    def GAST(cls, a_datetime):
        """Greenwich apparent sidereal time

        Args:

        a_datetime: local date and time of the observation.

        Returns GMST as an angle in hours
        """

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

        Returns LSTM as an angle in hours
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

        Returns LSTA as an angle in hours
        """

        gast = cls.GAST(a_datetime)
        lst = gast + coords.angle(an_observer.phi.value/15)
        lst.normalize(0, 24)
        return lst


# ===============================
# ===== Ecliptic Equatorial =====
# ===============================


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


# ==============================
# ===== Equatorial Horizon =====
# ==============================

class EquatorialHorizon(Transforms):

    """Transforms 3D space vectors to/from ecliptic/equatorial coordinates

    This uses spherical trigonometry.

    from:
        http://en.wikipedia.org/wiki/Celestial_coordinate_system#Equatorial_.E2.86.90.E2.86.92_horizontal

    With input from http://star-www.st-and.ac.uk/~fv/webnotes/chapter7.htm,
    but I think "chapter7" is incorrect in calculating the Local Hour Angle.

    I observed Sirius on New Years Eve 2015 at 8pm and measured its
    altitude and azimuth using a theodolite app on my iPhone. I
    got:

        Date & Time: Wed Dec 31 20:41:41 PST 2014
        Position: +037.40015* / -122.08219*
        Altitude: 56ft
        Azimuth/Bearing: 127* S53E 2258mils (True)
        Elevation Angle: +18.1*

    By happy coincidence, Sirius was on/near my local meridian, due
    south, at midnight new years eve, 3 hours after I measured it with
    my theodolite app at 8:41 pm above.

    According to http://star-www.st-and.ac.uk/~fv/webnotes/chapter6.htm
    an alternative definition of LST is "Local Sidereal Time = Right
    Ascension of whichever stars are on the meridian."  Therefore,
    local sidereal time == right ascension of Sirius == 6* 45' 9"

    But according to    http://aa.usno.navy.mil/data/docs/siderealtime.php
    this is my Greenwich Mean Sidereal Time; my local sidereal time is 22h 32m
    59.9s.

    If I let my Local Hour Angle = GMST - RA(star) this matches my
    observed results.
    """

    horizon_axis = coords.rotator(coords.Uy)

    @classmethod
    def toHorizon(cls, an_object, an_observer, a_local_datetime):
        """Transforms a vector from equatorial to ecliptic coordinates.

        Args:

        an_object: the vector to transform in theta (90 - declination),
                   phi (RA * 15). See self.radec2spherical.

        an_observer: the latitude (90 - theta) and longitude (positive
                     east of the prime meridian) of an observer as a
                     spherical coordinate (unit radius)

        a_local_datetime: local date and time of the observation.

        Returns a spherical coordinate vector in the transformed coordinates

        """
        debug = False

        if not isinstance(an_object, coords.spherical):
            raise Error('vector must be in spherical coordinates')

        if not isinstance(an_observer, coords.spherical):
            raise Error('observer must be in spherical coordinates')

        gmst = USNO_C163.GMST(a_local_datetime) # hours
        local_hour_angle = coords.angle(gmst.value*15 - an_object.phi.value)

        # Altitude = 90 - theta
        theta = coords.angle()

        foo =  math.cos(an_object.theta.radians) * math.cos(an_observer.theta.radians) + \
               math.sin(an_object.theta.radians) * math.sin(an_observer.theta.radians) * \
               math.cos(local_hour_angle.radians)

        theta.radians = math.acos(foo)

        if debug:
            altitude = coords.angle()
            altitude.radians = math.pi/2 - math.acos(foo)
            print 'altitude', altitude

        # Azimuth = phi - 180
        # "Note that Azimuth (A) is measured from the South point, turning positive to the West."
        phi = coords.angle()

        nom = math.sin(local_hour_angle.radians)
        den = (math.cos(local_hour_angle.radians)*math.sin(math.pi/2 - an_observer.theta.radians) - \
               math.tan(math.pi/2 - an_object.theta.radians) *  math.cos(math.pi/2 - an_observer.theta.radians))

        phi.radians = math.pi + math.atan2(nom, den)

        if debug:
            azimuth = coords.angle()
            azimuth.radians = math.atan2(nom, den)
            print 'azimuth', azimuth

        return coords.spherical(1, theta, phi)


    @classmethod
    def toEquatorial(cls, an_object, an_observer, a_local_datetime):
        """Transforms a vector from equatorial to ecliptic coordinates.

        Args:

        an_object: the vector to transform in theta (90 - altitude),
                   phi (azimuth). See self.radec2spherical.

        an_observer: the latitude and longitude (positive west of the
                     prime meridian) of an observer as a spherical
                     coordinate (unit radius)

        a_local_datetime: local date and time of the observation.

        Returns a spherical coordinate vector in the transformed coordinates
        """

        debug = False

        if not isinstance(an_object, coords.spherical):
            raise Error('vector must be in spherical coordinates')

        if not isinstance(an_observer, coords.spherical):
            raise Error('observer must be in spherical coordinates')

        gmst = USNO_C163.GMST(a_local_datetime) # hours

        # declination = 90 - theta
        theta = coords.angle()

        foo =  math.cos(an_object.theta.radians) * math.cos(an_observer.theta.radians) - \
               math.sin(an_object.theta.radians) * math.sin(an_observer.theta.radians) * \
               math.cos(an_object.phi.radians - math.pi)

        theta.radians = math.acos(foo)

        if debug:
            declination = coords.angle()
            declination.radians = math.pi/2 - math.acos(foo)
            print 'declination', declination

        # Azimuth = phi - 180
        # "Note that Azimuth (A) is measured from the South point, turning positive to the West."
        phi = coords.angle()

        nom = math.sin(an_object.phi.radians - math.pi)
        den = (math.cos(an_object.phi.radians - math.pi)*math.sin(math.pi/2 - an_observer.theta.radians) + \
               math.tan(math.pi/2 - an_object.theta.radians) *  math.cos(math.pi/2 - an_observer.theta.radians))

        phi.radians = gmst.radians*15 - math.atan2(nom, den)

        if debug:
            ra = coords.angle()
            ra.radians = gmst.radians*15 - math.atan2(nom, den)
            ra /= coords.angle(15)
            print 'R.A.', ra

        return coords.spherical(1, theta, phi)

