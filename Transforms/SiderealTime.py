#!/usr/bin/env python

"""Transforms coordinates, Ecliptic, Equatorial and Horizontal

to run: ./pylaunch.sh SiderealTime.py 2017-11-27T12:00

References:

Sidereal Time
    http://en.wikipedia.org/wiki/Sidereal_time
    http://aa.usno.navy.mil/faq/docs/GAST.php
    http://aa.usno.navy.mil/data/docs/JulianDate.php
    http://aa.usno.navy.mil/publications/docs/Circular_163.pdf
    http://www.usno.navy.mil/USNO/astronomical-applications/publications/Circular_179.pdf

Validation:
    http://aa.usno.navy.mil/cgi-bin/aa_jdconv.pl
    http://aa.usno.navy.mil/data/docs/siderealtime.php
"""

import math

import coords
import EclipticEquatorial
import utils


class Error(Exception):
    pass

class USNO_C163(object):
    """Greenwich Mean Sideral Time calculations

    from the U.S. Naval Observatory:
        http://aa.usno.navy.mil/faq/docs/GAST.php
        http://aa.usno.navy.mil/publications/docs/Circular_163.pdf

    validate with:
        http://aa.usno.navy.mil/data/docs/siderealtime.php

    TODO USNO_C179
    http://www.usno.navy.mil/USNO/astronomical-applications/publications/Circular_179.pdf

    """

    J2000 = coords.datetime('2000-01-01T12:00:00') # starts at noon
    sidereal_day = coords.angle(23, 56, 4.0916)

    @classmethod
    def JulianDate0(cls, a_datetime):
        """Julian date and the previous midnight

        Args:

        a_datetime (coords.datetime): The time of the observation.

        Returns (float, float): a tuple of the Julian Date and its
        previous midnight

        """

        JD = a_datetime.toJulianDate()
        JDfloor = math.floor(JD)

        # Must end in 0.5
        if JD - JDfloor >= 0.5:
            JDo = JDfloor + 0.5
        else:
            JDo = JDfloor - 0.5

        return JD, JDo


    @classmethod
    def GMST(cls, a_datetime):
        """Greenwich mean sidereal time (GMST)

        http://aa.usno.navy.mil/faq/docs/GAST.php

        Args:

        a_datetime (coords.datetime): The time of the observation.

        Returns (coords.angle): GMST as an angle in hours
        """

        JD, JDo = cls.JulianDate0(a_datetime)

        D = JD - a_datetime.J2000
        Do = JDo - a_datetime.J2000
        H = (JD - JDo)*24
        T = D/36525

        gmst = 6.697374558 + 0.06570982441908*Do + 1.00273790935*H + 0.000026*T*T

        gmst_hours = coords.angle(gmst - a_datetime.timezone)
        gmst_hours.normalize(0, 24)

        return gmst_hours


    @classmethod
    def GMST_simplified(cls, a_datetime):
        """Greenwich mean sidereal time, simplified form

        http://aa.usno.navy.mil/faq/docs/GAST.php

        Args:

        a_datetime (coords.datetime): The time of the observation.

        Returns (coords.angle): GMST as an angle in hours
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

        a_datetime (coords.datetime): The time of the observation.

        Returns (coords.angle): GMST as an angle in hours
        """

        D = a_datetime.toJulianDate() - cls.J2000.toJulianDate()
        gmst = 280.46061837 + 360.98564736629 * D # in degrees
        gmst_angle = coords.angle(gmst)
        gmst_angle.normalize(-180, 180)
        gmst_hours = coords.angle(gmst_angle.value/15.0)

        return gmst_hours


    @classmethod
    def obliquity(cls, a_datetime):
        """Calculates obliquity of the ecliptic

        using USNO formula.

        Returns (float): obliquity
        """

        JD, JDo = cls.JulianDate0(a_datetime)
        D = JD - a_datetime.J2000

        return coords.angle(23.4393 - 0.0000004*D)


    @classmethod
    def GAST(cls, a_datetime):
        """Greenwich apparent sidereal time

        http://aa.usno.navy.mil/faq/docs/GAST.php

        Args:

        a_datetime: local date and time of the observation.

        Returns GMST as an angle in hours
        """

        gmst = cls.GMST(a_datetime)

        JD, JDo = cls.JulianDate0(a_datetime)
        D = JD - a_datetime.J2000
        eps = cls.obliquity(a_datetime) # TODO JPL eps? EclipticEquatorial.eps(a_datetime)
        L = coords.angle(280.47 + 0.98565*D)
        omega = coords.angle(125.04 - 0.052954*D)
        eqeq = coords.angle((-0.000319*math.sin(omega.radians) - 0.000024*math.sin(2*L.radians))*math.cos(eps.radians))

        gast = gmst + eqeq

        return gast


    @classmethod
    def LSTM(cls, an_observer, a_datetime):
        """Local sidereal time, mean

        Args:

        an_observer (coords.spherical): the latitude (in degrees) and
        longitude of an observer as a spherical coordinate where theta
        is the complement of latitude and longitude is measured
        positive east. See utils.latlon2spherical.

        a_datetime (coords.datetime): The time of the observation.

        Returns (coords.angle): LMST as an angle in hours

        """

        gmst = cls.GMST(a_datetime)
        lst = gmst + coords.angle(an_observer.phi.value/15)
        lst.normalize(0, 24)
        return lst


    @classmethod
    def LSTA(cls, an_observer, a_datetime):
        """Local sidereal time, apparent

        Args:

        an_observer (coords.spherical): the latitude (in degrees) and
        longitude of an observer as a spherical coordinate where theta
        is the complement of latitude and longitude is measured
        positive east. See utils.latlon2spherical.

        a_datetime (coords.datetime): The time of the observation.

        Returns (coords.angle): LSTA as an angle in hours

        """

        gast = cls.GAST(a_datetime)
        lst = gast + coords.angle(an_observer.phi.value/15)
        lst.normalize(0, 24)
        return lst




# ================
# ===== main =====
# ================


if __name__ == '__main__':

    # -------------------------
    # ----- parse options -----
    # -------------------------

    import optparse

    usage = '%prog [options] <datetime> [<latitude> [<longitude>]]'

    parser = optparse.OptionParser(usage=usage)

    options, args = parser.parse_args()

    # ----- validate -----

    if len(args) < 1:
        parser.error('missing datetime.')

    a_datetime = coords.datetime(args[0])

    if len(args) > 1:
        a_latitude = utils.parse_angle_arg(args[1])
    else:
        a_latitude = utils.parse_angle_arg('0')

    if len(args) > 2:
        a_longitude = utils.parse_angle_arg(args[2])
    else:
        a_longitude = utils.parse_angle_arg('0')

    an_observer = coords.spherical(1, a_latitude, a_longitude)

    # ----- results -----

    print a_datetime
    print an_observer

    print 'Julian Date', a_datetime.toJulianDate()

    eps_jpl = EclipticEquatorial.obliquity(a_datetime)
    print 'obliquity JPL: ', eps_jpl, ''.join(('(', str(eps_jpl.value), ')'))

    eps_usno = USNO_C163.obliquity(a_datetime)
    print 'obliquity USNO:', eps_usno, ''.join(('(', str(eps_usno.value), ')'))


    print 'GMST', USNO_C163.GMST(a_datetime)
    print 'GAST', USNO_C163.GAST(a_datetime)
    print 'LSTM', USNO_C163.LSTM(an_observer, a_datetime)
    print 'LSTA', USNO_C163.LSTA(an_observer, a_datetime)
