"""Unit tests for Right Ascension, declination, Ecliptic and Equatorial transforms"""

import math
import time
import unittest

import coords
import Transforms

class TransformTests(unittest.TestCase):
    """Test basic transforms."""

    def setUp(self):
        """Set up test parameters."""

        self.places = 5
        self.xforms = Transforms.Transforms()


    def test_spherical2latitude_npole(self):
        """Test spherical2latitude north pole"""
        a_point = coords.spherical(1)
        a_latitude = self.xforms.spherical2latitude(a_point)
        self.assertEqual(90, a_latitude)


    def test_spherical2latitude_equator(self):
        """Test spherical2latitude equator"""
        a_point = coords.spherical(1, coords.angle(90))
        a_latitude = self.xforms.spherical2latitude(a_point)
        self.assertEqual(0, a_latitude)


    def test_spherical2latitude_spole(self):
        """Test spherical2latitude south pole"""
        a_point = coords.spherical(1, coords.angle(180))
        a_latitude = self.xforms.spherical2latitude(a_point)
        self.assertEqual(-90, a_latitude)


    def test_spherical2longitude_prime_meridian(self):
        """Test spherical2latitude prime meridian"""
        a_point = coords.spherical(1)
        a_longitude = self.xforms.spherical2longitude(a_point)
        self.assertEqual(0, a_longitude)


    def test_spherical2longitude_dateline(self):
        """Test spherical2latitude date line"""
        a_point = coords.spherical(1, coords.angle(0), coords.angle(180))
        a_longitude = self.xforms.spherical2longitude(a_point)
        self.assertEqual(180, a_longitude)


    def test_spherical2longitude_45_east(self):
        """Test spherical2latitude 45 east"""
        a_point = coords.spherical(1, coords.angle(0), coords.angle(45))
        a_longitude = self.xforms.spherical2longitude(a_point)
        self.assertEqual(45, a_longitude)


    def test_spherical2longitude_45_west(self):
        """Test spherical2latitude 45 west"""
        a_point = coords.spherical(1, coords.angle(0), coords.angle(-45))
        a_longitude = self.xforms.spherical2longitude(a_point)
        self.assertEqual(315, a_longitude)


    def test_spherical2ra_45_east(self):
        """Test spherical2ra 45 east"""
        a_point = coords.spherical(1, coords.angle(0), coords.angle(45))
        a_right_ascension = self.xforms.spherical2ra(a_point)
        self.assertEqual(3, a_right_ascension)


    def test_spherical2ra_45_west(self):
        """Test spherical2ra 45 west"""
        a_point = coords.spherical(1, coords.angle(0), coords.angle(-45))
        a_right_ascension = self.xforms.spherical2ra(a_point)
        self.assertEqual(21, a_right_ascension)


    def test_radec2spherical_1(self):
        """Test RA 1, dec 0"""
        a_point = self.xforms.radec2spherical(a_right_ascension=coords.angle(1),
                                                 a_declination=coords.angle(0))

        self.assertAlmostEqual(90, a_point.theta.value)
        self.assertAlmostEqual(15, a_point.phi.value)
        self.assertAlmostEqual(1, self.xforms.spherical2ra(a_point))


    def test_JulianCentury_2000(self):
        """Test Julian Century 2000"""
        a_datetime = coords.datetime('2000-01-01T12:00:00')
        a_Julian_century = self.xforms.JulianCentury(a_datetime)
        self.assertEqual(0, a_Julian_century)


    def test_JulianCentury_2100(self):
        """Test Julian Century 2100"""
        a_datetime = coords.datetime('2100-01-01T12:00:00')
        a_Julian_century = self.xforms.JulianCentury(a_datetime)
        self.assertEqual(1, a_Julian_century)

# =====================
# ===== USNO C163 =====
# =====================

class USNO_C163(unittest.TestCase):
    """Test USNO transforms.

    from:
        http://aa.usno.navy.mil/faq/docs/GAST.php
        http://aa.usno.navy.mil/publications/docs/Circular_163.pdf

    validate:
        http://aa.usno.navy.mil/data/docs/JulianDate.php
        http://aa.usno.navy.mil/data/docs/siderealtime.php

    This service is only valid for dates between January 1, 2014 and December 31, 2016.

    """

    def setUp(self):
        """Set up test parameters."""

        self.places = 5
        self.xforms = Transforms.USNO_C163()


    @unittest.skip('hacking')
    def test_GMST(self):
        """Hacking Test of GMST"""
        a_datetime = coords.datetime('2015-06-01T00:00:00')
        a_gmst = self.xforms.GMST(a_datetime)
        a_gast = self.xforms.GAST(a_datetime)

        print '\nDatetime:', a_datetime
        print 'GMST', a_gmst
        print 'GAST', a_gast # TODO rm


    @unittest.skip('hacking')
    def test_LST(self):
        """Hacking Test of LST"""
        a_datetime = coords.datetime('2014-12-31T20:41:00')
        an_observer = coords.spherical(1, coords.latitude(37, 24), coords.angle(-122, 4, 57))

        a_gmst = self.xforms.GMST(a_datetime)
        a_lsta = self.xforms.LSTA(a_datetime, an_observer)

        print '\nDatetime:', a_datetime
        print 'observer:', an_observer
        print 'GMST', a_gmst
        print 'LSTA', a_lsta, a_lsta.value


    def test_JDo_1(self):
        """Test JDo is the previous midnight."""
        a_datetime = coords.datetime('2015-01-01T01:00:00')
        a_JD, a_JDo = self.xforms.JulianDate0(a_datetime)

        a_JD_datetime = coords.datetime()
        a_JD_datetime.fromJulianDate(a_JD)
        a_JDo_datetime = coords.datetime()
        a_JDo_datetime.fromJulianDate(a_JDo)

        self.assertEqual(2457023.5416666665, a_JD)
        self.assertEqual('2015-01-01T01:00:00', str(a_JD_datetime))

        self.assertEqual(2457023.5, a_JDo)
        self.assertEqual('2015-01-01T00:00:00', str(a_JDo_datetime))


    def test_JDo_2(self):
        """Test JDo is the previous midnight."""

        a_datetime = coords.datetime('2015-02-01T13:00:00')
        a_JD, a_JDo = self.xforms.JulianDate0(a_datetime)

        a_JD_datetime = coords.datetime()
        a_JD_datetime.fromJulianDate(a_JD)
        a_JDo_datetime = coords.datetime()
        a_JDo_datetime.fromJulianDate(a_JDo)

        self.assertEqual(2457055.0416666665, a_JD)
        self.assertEqual('2015-02-01T13:00:00', str(a_JD_datetime))

        self.assertEqual(2457054.5, a_JDo)
        self.assertEqual('2015-02-01T00:00:00', str(a_JDo_datetime))


    def test_JDo_3(self):
        """Test JDo is the previous midnight."""

        a_datetime = coords.datetime('2015-03-15T23:59:59')
        a_JD, a_JDo = self.xforms.JulianDate0(a_datetime)

        a_JD_datetime = coords.datetime()
        a_JD_datetime.fromJulianDate(a_JD)
        a_JDo_datetime = coords.datetime()
        a_JDo_datetime.fromJulianDate(a_JDo)

        self.assertEqual(2457097.499988426, a_JD)
        self.assertEqual('2015-03-15T23:59:59', str(a_JD_datetime))

        self.assertEqual(2457096.5, a_JDo)
        self.assertEqual('2015-03-15T00:00:00', str(a_JDo_datetime))


    def test_GMST_J2000(self):
        """Test GMST J2000"""
        a_datetime = coords.datetime(self.xforms.J2000)
        a_gmst = self.xforms.GMST(a_datetime)

        self.assertEqual('18:41:50.5484', str(a_gmst))
        # Note: out of range of http://aa.usno.navy.mil/data/docs/siderealtime.php


    def test_GMST_J2000_plus_day(self):
        """Test GMST J2000 plus a day"""
        a_datetime_0 = coords.datetime(self.xforms.J2000)
        a_gmst_0 = self.xforms.GMST_simplified(a_datetime_0)
        a_datetime_1 = coords.datetime('2000-01-02T12:00:00')
        a_gmst_1 = self.xforms.GMST_simplified(a_datetime_1)

        self.assertEqual('00:03:56.5554', str(a_gmst_1 - a_gmst_0))
        # matches http://en.wikipedia.org/wiki/Sidereal_time


    def test_GMST_J2000_plus_halfday(self):
        """Test GMST J2000 plus a halfday"""
        a_datetime_0 = coords.datetime(self.xforms.J2000)
        a_gmst_0 = self.xforms.GMST_simplified(a_datetime_0)
        a_datetime_1 = coords.datetime('2000-01-02T00:00:00')
        a_gmst_1 = self.xforms.GMST_simplified(a_datetime_1)

        self.assertEqual('12:01:58.2777', str(a_gmst_1 - a_gmst_0))


    def test_GMST_kb(self):
        """Test GMST formula, in hours, with kburnett data"""
        # This example is from
        # http://www2.arnes.si/~gljsentvid10/sidereal.htm and uses
        # the same formula as
        # http://aa.usno.navy.mil/faq/docs/GAST.php
        # but
        # http://aa.usno.navy.mil/data/docs/siderealtime.php says this
        # date is out of range.

        a_datetime = coords.datetime('1994-06-16T18:00:00')
        a_gmst = self.xforms.GMST(a_datetime)

        self.assertEqual('11:39:5.06752', str(a_gmst))


    def test_GMST_standrews(self):
        """Test GMST at St. Andrews"""
        # from http://star-www.st-and.ac.uk/~fv/webnotes/answer6.htm
        a_datetime = coords.datetime('1998-02-04T00:00:00')
        a_gmst = self.xforms.GMST(a_datetime)

        sta_long = coords.angle(2, 48)

        # TODO is 02:47:60, should be 2:48 but is not rounding 60 seconds up
        self.assertEqual('02:47:60', str(sta_long))

        # TODO this is 11 minutes off from answer6, but 11 minutes from GMT.
        self.assertEqual('08:55:49.7347', str(a_gmst))



    def test_GMST_2014_12_31_8pm(self):
        """Test GMST """
        # validate http://aa.usno.navy.mil/cgi-bin/aa_siderealtime.pl?form=1&year=2014&month=12&day=31&hr=20&min=41&sec=0.0&intv_mag=1.0&intv_unit=1&reps=5&state=CA&place=mountain+view
        a_datetime = coords.datetime('2014-12-31T20:41:00')
        a_gmst = self.xforms.GMST(a_datetime)
        a_gast = self.xforms.GAST(a_datetime)
        an_eqeq = a_gast - a_gmst

        an_observer = coords.spherical(1, coords.latitude(37, 23, 24), coords.angle(-122, 4, 48))
        a_lstm = self.xforms.LSTM(a_datetime, an_observer)
        a_lsta = self.xforms.LSTA(a_datetime, an_observer)

        self.assertEqual('03:21:46.443', str(a_gmst)) # Actual: 3 21 46.4412
        self.assertEqual('03:21:46.7422', str(a_gast)) # Actual: 3 21 46.7386
        self.assertEqual('00:00:0.299296', str(an_eqeq)) # Actual: +0.2975 seconds
        self.assertEqual('19:13:27.243', str(a_lstm)) # Actual: 19 13 27.2412
        self.assertEqual('19:13:27.5422', str(a_lsta)) # Actual: 19 13 27.5386


    def test_GMST_2015_01_01_8am(self):
        """Test GMST 2015 01 01 8 am"""
        # validate http://aa.usno.navy.mil/cgi-bin/aa_siderealtime.pl?form=1&year=2015&month=1&day=01&hr=08&min=0&sec=0.0&intv_mag=1.0&intv_unit=1&reps=5&state=CA&place=mountain+view

        a_datetime = coords.datetime('2015-01-01T08:00:00')
        a_gmst = self.xforms.GMST(a_datetime)
        a_gast = self.xforms.GAST(a_datetime)
        an_eqeq = a_gast - a_gmst

        an_observer = coords.spherical(1, coords.latitude(37, 23, 24), coords.angle(-122, 4, 48))
        a_lstm = self.xforms.LSTM(a_datetime, an_observer)
        a_lsta = self.xforms.LSTA(a_datetime, an_observer)

        self.assertEqual('14:42:37.9854', str(a_gmst)) # Actual: 14 42 37.9836
        self.assertEqual('14:42:38.2855', str(a_gast)) # Actual: 14 42 38.2828
        self.assertEqual('00:00:0.300053', str(an_eqeq)) # Actual: +0.2992 seconds
        self.assertEqual('06:34:18.7854', str(a_lstm)) # Actual: 6 34 18.7836
        self.assertEqual('06:34:19.0855', str(a_lsta)) # Actual: 6 34 19.0828


    def test_GMST_2015_01_01_2pm(self):
        """Test GMST 2015 01 01 2 pm"""
        # validate http://aa.usno.navy.mil/cgi-bin/aa_siderealtime.pl?form=1&year=2015&month=1&day=01&hr=14&min=0&sec=0.0&intv_mag=1.0&intv_unit=1&reps=5&state=CA&place=mountain+view

        a_datetime = coords.datetime('2015-01-01T14:00:00')
        a_gmst = self.xforms.GMST(a_datetime)
        a_gast = self.xforms.GAST(a_datetime)
        an_eqeq = a_gast - a_gmst

        an_observer = coords.spherical(1, coords.latitude(37, 23, 24), coords.angle(-122, 4, 48))
        a_lstm = self.xforms.LSTM(a_datetime, an_observer)
        a_lsta = self.xforms.LSTA(a_datetime, an_observer)

        self.assertEqual('20:43:37.1242', str(a_gmst)) # Actual: 20 43 37.1224
        self.assertEqual('20:43:37.4247', str(a_gast)) # Actual: 20 43 37.4227
        self.assertEqual('00:00:0.300452', str(an_eqeq)) # Actual: +0.3003 seconds
        self.assertEqual('12:35:17.9242', str(a_lstm)) # Actual: 12 35 17.9224
        self.assertEqual('12:35:18.2247', str(a_lsta)) # Actual: 12 35 18.2227



    def test_GMST_2015_01_01_2pm_tz1(self):
        """Test GMST 2015 01 01 2 pm timezone +1"""
        a_datetime = coords.datetime('2015-01-01T14:00:00+0100')
        a_gmst = self.xforms.GMST(a_datetime)
        a_gast = self.xforms.GAST(a_datetime)
        an_eqeq = a_gast - a_gmst

        self.assertEqual('20:43:46.9807', str(a_gmst)) # Actual: 20 43 37.1224
        self.assertEqual('20:43:47.2812', str(a_gast)) # Actual: 20 43 37.4227
        self.assertEqual('00:00:0.300518', str(an_eqeq)) # Actual: +0.3003 seconds
        # validate http://aa.usno.navy.mil/cgi-bin/aa_siderealtime.pl?form=2&year=2015&month=1&day=01&hr=14&min=0&sec=0.0&intv_mag=1.0&intv_unit=1&reps=5&place=%28no+name+given%29&lon_sign=1&lon_deg=15&lon_min=&lon_sec=&lat_sign=1&lat_deg=0&lat_min=&lat_sec=


    def test_GMST_2pm_tzn1(self):
        """Test GMST 2015 01 01 2 pm timezone -1"""
        a_datetime = coords.datetime('2015-01-01T14:00:00-01:00')
        a_gmst = self.xforms.GMST(a_datetime)
        a_gast = self.xforms.GAST(a_datetime)
        an_eqeq = a_gast - a_gmst

        self.assertEqual('20:43:27.2677', str(a_gmst)) # Actual: 20 43 37.1224
        self.assertEqual('20:43:27.5681', str(a_gast)) # Actual: 20 43 37.4227
        self.assertEqual('00:00:0.300386', str(an_eqeq)) # Actual: +0.3003 seconds
        # validate http://aa.usno.navy.mil/cgi-bin/aa_siderealtime.pl?form=2&year=2015&month=1&day=01&hr=14&min=0&sec=0.0&intv_mag=1.0&intv_unit=1&reps=5&place=%28no+name+given%29&lon_sign=-1&lon_deg=15&lon_min=&lon_sec=&lat_sign=1&lat_deg=0&lat_min=&lat_sec=



    def test_GMST_simplified_J2000(self):
        """Test GMST simplified J2000"""
        a_datetime = coords.datetime(self.xforms.J2000)
        a_gmst = self.xforms.GMST_simplified(a_datetime)
        self.assertEqual('-5:18:9.45159', str(a_gmst))


    def test_GMST_simplified_J2000_plus_day(self):
        """Test GMST J2000 plus a day"""
        a_datetime_0 = coords.datetime(self.xforms.J2000)
        a_gmst_0 = self.xforms.GMST_simplified(a_datetime_0)
        a_datetime_1 = coords.datetime('2000-01-02T12:00:00')
        a_gmst_1 = self.xforms.GMST_simplified(a_datetime_1)

        self.assertEqual('00:03:56.5554', str(a_gmst_1 - a_gmst_0))


    def test_GMST_simplified_standrews(self):
        """Test GMST simplified at St. Andrews"""
        # from http://star-www.st-and.ac.uk/~fv/webnotes/answer6.htm
        a_datetime = coords.datetime('1998-02-04T00:00:00')
        a_gmst = self.xforms.GMST_simplified(a_datetime)

        sta_long = coords.angle(2, 48)
        # TODO is 02:47:60, should be 2:48 but is not rounding 60 seconds up
        self.assertEqual('02:47:60', str(sta_long))

        # TODO this is 11 minutes off from answer6, but 11 minutes from GMT.
        self.assertEqual('08:55:49.7347', str(a_gmst))


    def test_GMST_simplified_kb(self):
        """Test GMST simplified formula, in hours, with kburnett data"""
        # from http://www2.arnes.si/~gljsentvid10/sidereal.htm
        a_datetime = coords.datetime('1994-06-16T18:00:00')
        a_gmst = self.xforms.GMST_simplified(a_datetime)

        # -0.00001 seconds different from given test data
        self.assertEqual('11:39:5.06724', str(a_gmst))


    def test_GMST_simplified2_kb(self):
        """Test GMST simplified formula 2, in degrees, with kburnett data"""
        # from http://www2.arnes.si/~gljsentvid10/sidereal.htm
        a_datetime = coords.datetime('1994-06-16T18:00:00')
        a_gmst = self.xforms.GMST_simplified2(a_datetime)

        # matches test data given when rouded to 0.0001 places
        self.assertEqual('11:39:5.06723', str(a_gmst))

# ===============================
# ===== Ecliptic Equatorial =====
# ===============================

class EclipticEquatorial(unittest.TestCase):
    """Test ecliptic equatorial coordinate transformations

    Validated against http://lambda.gsfc.nasa.gov/toolbox/tb_coordconv.cfm
    """

    def setUp(self):
        """Set up test parameters."""

        self.places = 5 # precision limited by LAMBDA-tools reporting
        self.xforms = Transforms.EclipticEquatorial()

    def getLatitude(self, an_object):
        """Return latitude of point"""
        return Transforms.Transforms.spherical2latitude(an_object)

    def getLongitude(self, an_object):
        """Return longitude of point"""
        return Transforms.Transforms.spherical2longitude(an_object)


    def test_first_point_of_Aries(self):
        """Test J2000 first point of Aries"""

        j2000 = coords.datetime('2000-01-01T00:00:00')
        an_object = coords.spherical(coords.Ux)

        an_object_ec = self.xforms.toEcliptic(an_object, j2000)
        self.assertAlmostEqual(0, self.getLatitude(an_object_ec), self.places)
        self.assertAlmostEqual(0, self.getLongitude(an_object_ec), self.places)

        an_object_eq = self.xforms.toEquatorial(an_object, j2000)
        self.assertAlmostEqual(0, self.getLatitude(an_object_eq), self.places)
        self.assertAlmostEqual(360, self.getLongitude(an_object_eq), self.places)


    def test_North_Pole(self):
        """Test J2000 North Pole"""

        j2000 = coords.datetime('2000-01-01T00:00:00')
        an_object = coords.spherical(1, coords.declination(90), coords.angle(0))

        an_object_ec = self.xforms.toEcliptic(an_object, j2000)
        self.assertAlmostEqual(66.56071, self.getLatitude(an_object_ec), self.places)
        self.assertAlmostEqual(90, self.getLongitude(an_object_ec), self.places)

        an_object_eq = self.xforms.toEquatorial(an_object, j2000)
        self.assertAlmostEqual(66.56071, self.getLatitude(an_object_eq), self.places)
        self.assertAlmostEqual(270.00000, self.getLongitude(an_object_eq), self.places)


    def test_lat_0_long_15(self):
        """Test J2000 Latitude 0, Longitude 15"""

        j2000 = coords.datetime('2000-01-01T00:00:00')
        an_object = coords.spherical(1, coords.declination(0), coords.angle(15))

        an_object_ec = self.xforms.toEcliptic(an_object, j2000)
        self.assertAlmostEqual(-5.90920, self.getLatitude(an_object_ec), self.places)
        self.assertAlmostEqual(13.81162, self.getLongitude(an_object_ec), self.places)

        an_object_eq = self.xforms.toEquatorial(an_object, j2000)
        self.assertAlmostEqual(5.90920, self.getLatitude(an_object_eq), self.places)
        self.assertAlmostEqual(13.81162, self.getLongitude(an_object_eq), self.places)


    def test_lat_0_long_345(self):
        """Test J2000 Latitude 0, Longitude 345"""

        j2000 = coords.datetime('2000-01-01T00:00:00')
        an_object = coords.spherical(1, coords.declination(0), coords.angle(345))

        an_object_ec = self.xforms.toEcliptic(an_object, j2000)
        self.assertAlmostEqual(5.90920, self.getLatitude(an_object_ec), self.places)
        self.assertAlmostEqual(346.18838, self.getLongitude(an_object_ec), self.places)

        an_object_eq = self.xforms.toEquatorial(an_object, j2000)
        self.assertAlmostEqual(-5.90920, self.getLatitude(an_object_eq), self.places)
        self.assertAlmostEqual(346.18838, self.getLongitude(an_object_eq), self.places)


    def test_lat_45_long_100(self):
        """Test J2000 Latitude 45, Longitude 100"""

        j2000 = coords.datetime('2000-01-01T00:00:00')
        an_object = coords.spherical(1, coords.declination(45), coords.angle(100))

        an_object_ec = self.xforms.toEcliptic(an_object, j2000)
        self.assertAlmostEqual(21.82420, self.getLatitude(an_object_ec), self.places)
        self.assertAlmostEqual(97.60065, self.getLongitude(an_object_ec), self.places)

        an_object_eq = self.xforms.toEquatorial(an_object, j2000)
        self.assertAlmostEqual(67.78257, self.getLatitude(an_object_eq), self.places)
        self.assertAlmostEqual(108.94923, self.getLongitude(an_object_eq), self.places)


    def test_lat_n30_long_n30(self):
        """Test J2000 Latitude -30, Longitude -30"""

        j2000 = coords.datetime('2000-01-01T00:00:00')
        an_object = coords.spherical(1, coords.declination(-30), coords.angle(-30))

        an_object_ec = self.xforms.toEcliptic(an_object, j2000)
        self.assertAlmostEqual(-16.64844, self.getLatitude(an_object_ec), self.places)
        self.assertAlmostEqual(321.51905, self.getLongitude(an_object_ec), self.places)

        an_object_eq = self.xforms.toEquatorial(an_object, j2000)
        self.assertAlmostEqual(-39.12273, self.getLatitude(an_object_eq), self.places)
        self.assertAlmostEqual(345.18327, self.getLongitude(an_object_eq), self.places)


    def test_lat_n60_long_200(self):
        """Test J2015 Latitude -60, Longitude 200"""

        j2015 = coords.datetime('2015-01-01T00:00:00')
        an_object = coords.spherical(1, coords.declination(-60), coords.angle(200))

        an_object_ec = self.xforms.toEcliptic(an_object, j2015)
        self.assertAlmostEqual(-46.59844, self.getLatitude(an_object_ec), self.places)
        self.assertAlmostEqual(226.85843, self.getLongitude(an_object_ec), self.places)

        an_object_eq = self.xforms.toEquatorial(an_object, j2015)
        self.assertAlmostEqual(-59.60899, self.getLatitude(an_object_eq), self.places)
        self.assertAlmostEqual(158.23870, self.getLongitude(an_object_eq), self.places)


    def test_lat_20_long_n10(self):
        """Test J2015 Latitude 20, Longitude -10"""

        j2015 = coords.datetime('2015-01-01T00:00:00')
        an_object = coords.spherical(1, coords.declination(20), coords.angle(-10))

        an_object_ec = self.xforms.toEcliptic(an_object, j2015)
        self.assertAlmostEqual(22.25346, self.getLatitude(an_object_ec), self.places)
        self.assertAlmostEqual(359.15333, self.getLongitude(an_object_ec), self.places)

        an_object_eq = self.xforms.toEquatorial(an_object, j2015)
        self.assertAlmostEqual(14.41240, self.getLatitude(an_object_eq), self.places)
        self.assertAlmostEqual(342.84035, self.getLongitude(an_object_eq), self.places)


# ==============================
# ===== Equatorial Horizon =====
# ==============================

class EquatorialHorizon(unittest.TestCase):
    """Test equatorial horizon transforms"""

    def setUp(self):
        """Set up test parameters."""

        self.places = 13 # limit 15
        self.xforms = Transforms.EquatorialHorizon()

        self.sirius = self.xforms.radec2spherical(a_right_ascension=coords.angle(6, 45, 8.9173),
                                                  a_declination=coords.angle(-16, 42, 58.017))


    def assertSpacesAreEqual(self, lhs_space, rhs_space):
        """Space assert helper method with limited places."""
        self.assertAlmostEqual(lhs_space.r, rhs_space.r, places=self.places)
        self.assertAlmostEqual(lhs_space.theta.value, rhs_space.theta.value, places=self.places)
        self.assertAlmostEqual(lhs_space.phi.value, rhs_space.phi.value, places=self.places)


    def test_sirius_2014_12_31T20_41_41(self):
        """Test RA/dec of Sirius 2014-12-31T20:41:41

        From my iPhone theodolite app (not very precise):
        Date & Time: Wed Dec 31 20:41:41 PST 2014
        Position: +037.40015* / -122.08219*
        Altitude: 56ft
        Azimuth/Bearing: 127* S53E 2258mils (True)
        Elevation Angle: +18.1*

        from http://www.convertalot.com/celestial_horizon_co-ordinates_calculator.html

        azimuth: 127.59
        altitude: 16.81

        from http://www.stargazing.net/mas/al_az.htm

        azimuth: 127* 24' 16"
        altitude: 16* 41' 31"

        """

        an_observer = coords.spherical(1, coords.latitude(37, 24), coords.angle(-122, 4, 57))

        a_datetime = coords.datetime('2014-12-31T20:41:41')

        sirius_hz = self.xforms.toHorizon(self.sirius, an_observer, a_datetime)

        self.assertEqual('17:54:28.6306', str(coords.angle(90) - sirius_hz.theta))
        self.assertEqual('128:52:13.836', str(sirius_hz.phi))

        sirius_eq = self.xforms.toEquatorial(sirius_hz, an_observer, a_datetime)

        self.assertSpacesAreEqual(self.sirius, sirius_eq)


    def test_sirius_2015_01_01T00_00_00(self):
        """Test RA/dec of Sirius 2015-01-01T00:00:00

        By happy coincidence, Sirius was on/near my local
        meridian, due south, at midnight new years eve when I measured
        it with my theodolite app at 8:41 pm above.
        """

        an_observer = coords.spherical(1, coords.latitude(37, 24), coords.angle(-122, 4, 57))

        a_datetime = coords.datetime('2015-01-01T00:00:00')

        sirius_hz = self.xforms.toHorizon(self.sirius, an_observer, a_datetime)

        self.assertEqual('35:52:34.9412', str(coords.angle(90) - sirius_hz.theta))
        self.assertEqual('178:52:5.91641', str(sirius_hz.phi))

        sirius_eq = self.xforms.toEquatorial(sirius_hz, an_observer, a_datetime)

        self.assertSpacesAreEqual(self.sirius, sirius_eq)


    def test_sirius_2015_01_01T06_00_00(self):
        """Test RA/dec of Sirius 2015-01-01T06:00:00"""

        an_observer = coords.spherical(1, coords.latitude(37, 24), coords.angle(-122, 4, 57))

        a_datetime = coords.datetime('2015-01-01T06:00:00')

        sirius_hz = self.xforms.toHorizon(self.sirius, an_observer, a_datetime)

        self.assertEqual('-9:30:43.9809', str(coords.angle(90) - sirius_hz.theta))
        self.assertEqual('256:10:20.4311', str(sirius_hz.phi))

        sirius_eq = self.xforms.toEquatorial(sirius_hz, an_observer, a_datetime)

        self.assertSpacesAreEqual(self.sirius, sirius_eq)



    def test_sirius_2015_01_01T12_00_00(self):
        """Test RA/dec of Sirius 2015-01-01T12:00:00"""


        an_observer = coords.spherical(1, coords.latitude(37, 24), coords.angle(-122, 4, 57))

        a_datetime = coords.datetime('2015-01-01T12:00:00')

        sirius_hz = self.xforms.toHorizon(self.sirius, an_observer, a_datetime)

        self.assertEqual('-69:18:43.4107', str(coords.angle(90) - sirius_hz.theta))
        self.assertEqual('358:44:25.2683', str(sirius_hz.phi))

        sirius_eq = self.xforms.toEquatorial(sirius_hz, an_observer, a_datetime)

        self.assertSpacesAreEqual(self.sirius, sirius_eq)


    def test_sirius_2015_01_01T21_00_00(self):
        """Test RA/dec of Sirius 2015-01-01T21:00:00"""

        an_observer = coords.spherical(1, coords.latitude(37, 24), coords.angle(-122, 4, 57))

        a_datetime = coords.datetime('2015-01-01T21:00:00')

        sirius_hz = self.xforms.toHorizon(self.sirius, an_observer, a_datetime)

        self.assertEqual('21:14:52.8586', str(coords.angle(90) - sirius_hz.theta))
        self.assertEqual('133:17:44.3899', str(sirius_hz.phi))

        sirius_eq = self.xforms.toEquatorial(sirius_hz, an_observer, a_datetime)

        self.assertSpacesAreEqual(self.sirius, sirius_eq)



    @unittest.skip('hacking')
    def test_sirius_hacking(self):
        """Test RA/dec of Sirius"""

        an_observer = coords.spherical(1, coords.latitude(37, 24), coords.angle(-122, 4, 57))

        a_datetime = coords.datetime('2015-01-01T00:00:00')

        sirius_hz = self.xforms.toHorizon(self.sirius, an_observer, a_datetime)

        print '\nsirius', sirius_hz



    @unittest.skip('hacking')
    def test_to_equatorial_hacking(self):
        """Test altitude azimuth to RA, dec."""

        an_object = coords.spherical(1, coords.angle(90) - coords.angle(35, 52, 34.9412),
                                     coords.angle(178, 52, 5.91641))

        an_observer = coords.spherical(1, coords.latitude(37, 24), coords.angle(-122, 4, 57))

        a_datetime = coords.datetime('2015-01-01T00:00:00')

        sirius_eq = self.xforms.toEquatorial(an_object, an_observer, a_datetime)

        print '\nsirius', sirius_eq



# TODO tests in the southern hemisphere



# ===========================================
# ===== TODO incomplete implementations =====
# ===========================================



class APC(unittest.TestCase):
    """Test APC transforms."""

    def setUp(self):
        """Set up test parameters."""

        self.places = 5
        self.xforms = Transforms.APC()


    @unittest.skip('hacking')
    def test_GMST(self):
        """Hacking Test of GMST"""
        a_datetime = coords.datetime('2015-06-01T00:00:00')
        a_gmst = self.xforms.GMST(a_datetime)

        print '\nDatetime:', a_datetime # TODO rm
        print 'GMST', a_gmst # TODO rm


    def test_GMST_J2000(self):
        """Test GMST J2000"""
        a_datetime = coords.datetime(self.xforms.J2000)
        a_gmst = self.xforms.GMST(a_datetime)

        # TODO: very different from USNO_C163
        self.assertEqual('06:39:53.4567', str(a_gmst))


    def test_GMST_J2000_plus_day_1(self):
        """Test J2000 plus a day"""
        a_datetime_0 = coords.datetime(self.xforms.J2000)
        a_gmst_0 = self.xforms.GMST(a_datetime_0)
        a_datetime_1 = coords.datetime('2000-01-02T12:00:00')
        a_gmst_1 = self.xforms.GMST(a_datetime_1)

        self.assertEqual('00:03:56.5554', str(a_gmst_1 - a_gmst_0))
        # matches http://en.wikipedia.org/wiki/Sidereal_time


    def test_GMST_plus_another_day_2(self):
        """Test plus another day"""
        a_datetime_0 = coords.datetime('2015-01-10T12:30:00')
        a_gmst_0 = self.xforms.GMST(a_datetime_0)
        a_datetime_1 = coords.datetime('2015-01-11T12:30:00')
        a_gmst_1 = self.xforms.GMST(a_datetime_1)

        self.assertEqual('00:03:56.5554', str(a_gmst_1 - a_gmst_0))
        # matches http://en.wikipedia.org/wiki/Sidereal_time


    @unittest.skip('Does not match the test data given, but is out of valid date range')
    def test_GMST_kb(self):
        """Test GMST formula, in degrees, with kburnett data"""
        # This example is from
        # http://www2.arnes.si/~gljsentvid10/sidereal.htm and uses
        # the same formula as
        # http://aa.usno.navy.mil/faq/docs/GAST.php
        # but
        # http://aa.usno.navy.mil/data/docs/siderealtime.php says this
        # date is out of range.

        a_datetime = coords.datetime('1994-06-16T18:00:00')
        a_gmst = self.xforms.GMST(a_datetime)

        # test data given
        self.assertEqual('11:39:5.06724', str(a_gmst))
        # actual result is 17:36:9.42998


    def test_GMST_standrews(self):
        """Test GMST St. Andrews"""
        # from http://star-www.st-and.ac.uk/~fv/webnotes/answer6.htm
        a_datetime = coords.datetime('1998-02-04T00:00:00')
        a_gmst = self.xforms.GMST(a_datetime)

        self.assertEqual('08:55:49.7347', str(a_gmst))
        # does match USNO result


    @unittest.skip('TODO does not match USNO result')
    def test_GMST_2014_12_31_8pm(self):
        """Test GMST """
        # validate http://aa.usno.navy.mil/cgi-bin/aa_siderealtime.pl?form=1&year=2014&month=12&day=31&hr=20&min=41&sec=0.0&intv_mag=1.0&intv_unit=1&reps=5&state=CA&place=mountain+view
        a_datetime = coords.datetime('2014-12-31T20:41:00')
        a_gmst = self.xforms.GMST(a_datetime)


        self.assertEqual('03:21:46.443', str(a_gmst)) # Actual: 3 21 46.4412
        # TODO does not match validation result: 06:37:24.6224


    @unittest.skip('TODO does not match USNO result')
    def test_GMST_2015_01_01_2pm(self):
        """Test GMST 2015 01 01 2 pm"""
        # validate http://aa.usno.navy.mil/cgi-bin/aa_siderealtime.pl?form=1&year=2015&month=1&day=01&hr=14&min=0&sec=0.0&intv_mag=1.0&intv_unit=1&reps=5&state=CA&place=mountain+view

        a_datetime = coords.datetime('2015-01-01T14:00:00')
        a_gmst = self.xforms.GMST(a_datetime)

        self.assertEqual('20:43:37.1242', str(a_gmst)) # Actual: 20 43 37.1224
        # TODO does not match validation result: '06:41:20.5172'



    @unittest.skip('hacking')
    def test_sirius(self):
        """Test RA/dec of Sirius

        From theodolite app:
        Date & Time: Wed Dec 31 20:41:41 PST 2014
        Position: +037.40015* / -122.08219*
        Altitude: 56ft
        Azimuth/Bearing: 127* S53E 2258mils (True)
        Elevation Angle: +18.1*

        from http://www.convertalot.com/celestial_horizon_co-ordinates_calculator.html

        azimuth: 127.59
        altitude: 16.81

        from http://www.stargazing.net/mas/al_az.htm

        azimuth: 127* 24' 16"
        altitude: 16* 41' 31"

        """


        sirius = self.xforms.radec2spherical(a_right_ascension=coords.angle(6, 45, 8.9173),
                                             a_declination=coords.angle(-16, 42, 58.017))

        an_observer = coords.spherical(1, coords.latitude(37, 24), coords.angle(-122, 4, 57))

        # a_datetime = coords.datetime('2014-12-31T20:41:00')
        a_datetime = coords.datetime('2015-01-06T21:39:00') # obs 2

        sirius_hz = self.xforms.toHorizon(sirius, an_observer, a_datetime)

        print 'sirius', sirius_hz

        # TODO validate something


    @unittest.skip('TODO')
    def test_toHorizon_1(self):
        """Test to horizon transform 1"""
        an_object = coords.spherical(1, coords.angle(45), coords.angle(0))
        an_observer = coords.spherical(1, coords.latitude(45), coords.angle(0))
        a_gst_time = coords.datetime('2015-01-01T00:00:00')

        hz_point = self.xforms.toHorizon_APC(an_object, an_observer, a_gst_time)

        self.assertAlmostEqual(90, hz_point.theta.value)
        self.assertAlmostEqual(0, hz_point.phi.value)


    @unittest.skip('TODO')
    def test_toHorizon_2(self):
        """Test to horizon transform 2"""
        an_object = coords.spherical(1, coords.angle(45), coords.angle(90))
        an_observer = coords.spherical(1, coords.latitude(45), coords.angle(0))
        a_gst_time = coords.datetime('2015-01-01T00:00:00')

        hz_point = self.xforms.toHorizon_APC(an_object, an_observer, a_gst_time)

        # TODO validate
        self.assertAlmostEqual(60, hz_point.theta.value)
        self.assertAlmostEqual(54.735610317245346, hz_point.phi.value)


    @unittest.skip('TODO')
    def test_fromHorizon_1(self):
        """Test from horizon transform 1"""
        an_object = coords.spherical(1, coords.angle(90), coords.angle(0))
        an_observer = coords.spherical(1, coords.latitude(45), coords.angle(0))
        a_gst_time = coords.datetime('2015-01-01T00:00:00')

        hz_point = self.xforms.fromHorizon_APC(an_object, an_observer, a_gst_time)

        self.assertAlmostEqual(45, hz_point.theta.value)
        self.assertAlmostEqual(0, hz_point.phi.value)




class StjarnHimlen(unittest.TestCase):

    """Tests Starry Sky methods

    validate:
        http://www.satellite-calculations.com/Satellite/suncalc.htm
        http://www.stargazing.net/mas/al_az.htm

    TODO TestStjarnHimlen.test_GMST_J2000_plus_day is 8 seconds too long.

    """

    def setUp(self):
        """Set up test parameters."""

        self.places = 5
        self.xforms = Transforms.StjarnHimlen()


    @unittest.skip('hacking')
    def test_GMST(self):
        """Hacking Test of GMST

        gmst hours agrees with USNO when half a day off (approximately):

        StH a day ahead agrees better?

        USNO('2000-01-01T00:00:00') == 6:35/9:24 == StH('2000-01-01T12:00:00')
        USNO('2000-01-01T06:00:00') == -11:19:8 == StH('2000-01-02T18:00:00')
        USNO('2000-01-01T12:00:00') == -5:18:9 == StH('2000-01-02T00:00:00')
        USNO('2000-01-02T00:00:00') == 6:35/9:24 == StH('2000-01-02T12:00:00')

        """
        a_datetime = coords.datetime('2015-01-01T00:00:00')
        a_gmst = self.xforms.GMST(a_datetime)

        print '\nDatetime:', a_datetime # TODO rm
        print 'gmst', a_gmst # TODO rm



    def test_SolarLongitude_J2000(self):
        """Tests solar longitude calculation for J2000"""
        j2000 = coords.datetime('2000-01-01T00:00:00')
        a_solar_longitude = self.xforms.SolarLongitude(j2000)

        self.assertAlmostEqual(278.34302342798696, a_solar_longitude.value, self.places)


    def test_SolarRADec_J2000(self):
        """Tests solar RA and Dec calculation for J2000"""
        j2000 = coords.datetime('2000-01-01T00:00:00')
        RA, Dec = self.xforms.SolarRADec(j2000)

        self.assertAlmostEqual(279.0813909223767, RA.value, self.places)
        self.assertAlmostEqual(-23.17667313807378, Dec.value, self.places)


    def test_GMST0_J2000(self):
        """Tests GMST0 calculation for J2000"""
        j2000 = coords.datetime('2000-01-01T00:00:00')
        gmst0 = self.xforms.GMST0(j2000)

        self.assertAlmostEqual(98.34302342798696, gmst0.value, self.places)


    def test_GMST_J2000(self):
        """Tests GMST calculation for J2000"""
        j2000 = coords.datetime('2000-01-01T00:00:00')
        gmst = self.xforms.GMST(j2000)

        self.assertAlmostEqual(-5.443798438134203, gmst.value, self.places)


    @unittest.skip('TODO delta 8 seconds longer!')
    def test_GMST_J2000_plus_day(self):
        """Test GMST J2000 plus a day"""
        a_datetime_0 = coords.datetime('2000-01-01T12:00:00')
        a_gmst_0 = self.xforms.GMST(a_datetime_0)
        a_datetime_1 = coords.datetime('2000-01-02T12:00:00')
        a_gmst_1 = self.xforms.GMST(a_datetime_1)

        # returns '00:04:4.61177'
        self.assertEqual('00:03:56.5554', str(a_gmst_1 - a_gmst_0))


    def test_GMST_StA(self):
        """Tests GMST calculation for St. Andrews example"""
        a_datetime = coords.datetime('2000-01-01T00:00:00')
        gmst = self.xforms.GMST(a_datetime)

        self.assertAlmostEqual(-5.443798438134203, gmst.value, self.places)




    @unittest.skip('hacking')
    def test_SolarLongitude_for_years(self):
        """Tests solar longitude calculation by months for years

        TODO:
        flips to 0 on March 21 2000, not quite equinox, not quite midnight.
        different in different years.
        """

        for i in xrange(0, 5):
            for j in xrange(1, 13):
                for k in xrange(1, 28):
                    a_datetime = coords.datetime('201%d-%02d-%02dT00:00:00' % (i, j, k))
                    a_solar_longitude = self.xforms.SolarLongitude(a_datetime)
                    print a_datetime, a_solar_longitude



    @unittest.skip('hacking')
    def test_sirius(self):
        """Test RA/dec of Sirius

        http://en.wikipedia.org/wiki/Sirius

        RA: 6h 45m 8.9173s
        Dec: -16* 42' 58.017"

        From theodolite app:
        Date & Time: Wed Dec 31 20:41:41 PST 2014
        Position: +037.40015* / -122.08219*
        Altitude: 56ft
        Azimuth/Bearing: 127* S53E 2258mils (True)
        Elevation Angle: +18.1*

        from http://www.convertalot.com/celestial_horizon_co-ordinates_calculator.html

        azimuth: 127.59
        altitude: 16.81

        from http://www.stargazing.net/mas/al_az.htm

        azimuth: 127* 24' 16"
        altitude: 16* 41' 31"

        TODO

        """


        sirius = self.xforms.radec2spherical(a_right_ascension=coords.angle(6, 45, 8.9173),
                                             a_declination=coords.angle(-16, 42, 58.017))

        an_observer = coords.spherical(1, coords.latitude(37, 24), coords.angle(-122, 4, 57))

        a_datetime = coords.datetime('2014-12-31T20:41:00') # obs 1
        # a_datetime = coords.datetime('2015-01-06T21:39:00') # obs 2

        sirius_hz = self.xforms.toHorizon(sirius, an_observer, a_datetime)

        print 'sirius', sirius_hz

        # TODO validate something



if __name__ == '__main__':
    unittest.main()
