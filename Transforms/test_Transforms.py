"""Unit tests for Right Ascension, declination, Ecliptic and Equatorial transforms"""

import math
import time
import unittest

import coords
import Transforms

class TestTransforms(unittest.TestCase):
    """Test RA/declination transforms."""

    def setUp(self):
        """Set up test parameters."""

        self.places = 5 # precision limited by LAMBDA-tools reporting
        self.xforms = Transforms.Transforms()


    def test_radec2spherical_1(self):
        """Test RA 1, dec 0"""
        a_point = self.xforms.radec2spherical(a_right_ascension=coords.angle(1),
                                                 a_declination=coords.angle(0))

        self.assertAlmostEqual(90, a_point.theta.value)
        self.assertAlmostEqual(15, a_point.phi.value)
        self.assertAlmostEqual(1, self.xforms.spherical2ra(a_point))

    def test_GMST_USNO_simplified_0(self):
        """Test GMST USNO 0"""
        a_datetime = coords.datetime('2000-01-01T00:00:00')
        a_gmst = self.xforms.GMST_USNO_simplified(a_datetime)

        # TODO assert something

    def test_GMST_USNO_simplified_1(self):
        """Test GMST USNO 1"""
        a_datetime = coords.datetime('2000-01-01T01:00:00')
        a_gmst = self.xforms.GMST_USNO_simplified(a_datetime)

        # TODO assert something

    def test_GMST_USNO_simplified_2(self):
        """Test GMST USNO 2"""
        a_datetime = coords.datetime('2000-01-01T12:00:00')
        a_gmst = self.xforms.GMST_USNO_simplified(a_datetime)

        # TODO assert something

    def test_GMST_USNO_simplified_3(self):
        """Test GMST USNO 3"""
        a_datetime = coords.datetime('2001-01-01T12:00:00')
        a_gmst = self.xforms.GMST_USNO_simplified(a_datetime)

        # TODO assert something


    def test_GMST_USNO_simplified_standrews(self):
        """Test GMST USNO at St. Andrews"""
        # from http://star-www.st-and.ac.uk/~fv/webnotes/answer6.htm
        a_datetime = coords.datetime('1998-02-04T00:00:00')
        a_gmst = self.xforms.GMST_USNO_simplified(a_datetime)

        sta_long = coords.angle(2, 48)
        print 'St. Andrews longitude', sta_long, sta_long.value # TODO is 02:47:60, should be 2:48: round seconds up

        # this is 11 minutes off from answer6, but 11 minutes from
        # GMT. Used simpler LST (8h45m) for easier calculation by hand?
        self.assertEqual('08:55:49.7347', str(a_gmst))



    def test_GMST_USNO_simplified_kb1(self):
        """Test GMST USNO simplified formula, in hours, with kburnett data"""
        # from http://www2.arnes.si/~gljsentvid10/sidereal.htm
        a_datetime = coords.datetime('1994-06-16T18:00:00')
        a_gmst = self.xforms.GMST_USNO_simplified2(a_datetime)

        # matches test data given
        self.assertEqual('11:39:5.06723', str(a_gmst))



    def test_GMST_USNO_simplified2_kb2(self):
        """Test GMST USNO simplified formula 2, in degrees, with kburnett data"""
        # from http://www2.arnes.si/~gljsentvid10/sidereal.htm
        a_datetime = coords.datetime('1994-06-16T18:00:00')
        a_gmst = self.xforms.GMST_USNO_simplified(a_datetime)

        # matches test data given
        # TODO rounding difference in seconds from above
        self.assertEqual('11:39:5.06724', str(a_gmst))



    def test_GMST_APC_kb3(self):
        """Test GMST APC formula, in degrees, with kburnett data"""
        # from http://www2.arnes.si/~gljsentvid10/sidereal.htm
        a_datetime = coords.datetime('1994-06-16T18:00:00')
        a_gmst = self.xforms.GMST_APC(a_datetime)

        # matches test data given
        self.assertEqual('11:39:5.06724', str(a_gmst))



    def test_GMST_APC_standrews(self):
        """Test GMST APC St. Andrews"""
        # from http://star-www.st-and.ac.uk/~fv/webnotes/answer6.htm
        a_datetime = coords.datetime('1998-02-04T00:00:00')
        a_gmst = self.xforms.GMST_APC(a_datetime)

        # TODO assert something


    def test_GMST_APC_0(self):
        """Test GMST APC 0"""
        a_datetime = coords.datetime('2000-01-01T12:00:00')
        a_gmst = self.xforms.GMST_APC(a_datetime)

        # TODO assert something

    def test_GMST_APC_1(self):
        """Test GMST APC 1"""
        a_datetime = coords.datetime('2000-01-01T13:00:00')
        a_gmst = self.xforms.GMST_APC(a_datetime)

        # TODO assert something


class TestHorizon(unittest.TestCase):
    """Test horizon transforms"""

    def setUp(self):
        """Set up test parameters."""

        self.places = 5 # precision limited by LAMBDA-tools reporting
        self.hz_xforms = Transforms.Horizon()
        self.eceq_xforms = Transforms.EclipticEquatorial()

    @unittest.skip('TODO')
    def test_toHorizon_APC_1(self):
        """Test to horizon transform 1"""
        a_point = coords.spherical(1, coords.angle(45), coords.angle(0))
        an_observer = coords.spherical(1, coords.latitude(45), coords.angle(0))
        a_gst_time = coords.datetime('2015-01-01T00:00:00')

        hz_point = self.hz_xforms.toHorizon_APC(a_point, an_observer, a_gst_time)

        self.assertAlmostEqual(90, hz_point.theta.value)
        self.assertAlmostEqual(0, hz_point.phi.value)


    @unittest.skip('TODO')
    def test_toHorizon_APC_2(self):
        """Test to horizon transform 2"""
        a_point = coords.spherical(1, coords.angle(45), coords.angle(90))
        an_observer = coords.spherical(1, coords.latitude(45), coords.angle(0))
        a_gst_time = coords.datetime('2015-01-01T00:00:00')

        hz_point = self.hz_xforms.toHorizon_APC(a_point, an_observer, a_gst_time)

        # TODO validate
        self.assertAlmostEqual(60, hz_point.theta.value)
        self.assertAlmostEqual(54.735610317245346, hz_point.phi.value)


    @unittest.skip('TODO')
    def test_fromHorizon_APC_1(self):
        """Test from horizon transform 1"""
        a_point = coords.spherical(1, coords.angle(90), coords.angle(0))
        an_observer = coords.spherical(1, coords.latitude(45), coords.angle(0))
        a_gst_time = coords.datetime('2015-01-01T00:00:00')

        hz_point = self.hz_xforms.fromHorizon_APC(a_point, an_observer, a_gst_time)

        self.assertAlmostEqual(45, hz_point.theta.value)
        self.assertAlmostEqual(0, hz_point.phi.value)


    def test_radec2spherical_APC_sirius(self):
        """Test RA/dec of Sirius

        From theodolite app:
        Date & Time: Wed Dec 31 20:41:41 PST 2014
        Position: +037.40015* / -122.08219*
        Altitude: 56ft
        Azimuth/Bearing: 127* S53E 2258mils (True)
        Elevation Angle: +18.1*

        """

        a_gst_time = coords.datetime('2014-12-31T20:41:00')

        an_observer = coords.spherical(1, coords.latitude(37, 24), coords.angle(-122, 4, 57))

        sirius = self.hz_xforms.radec2spherical(a_right_ascension=coords.angle(6, 45, 8.9173),
                                                a_declination=coords.angle(-16, 42, 58.017))

        sirius_eq = self.eceq_xforms.toEquatorial(sirius, a_gst_time)

        sirius_hz = self.hz_xforms.toHorizon_APC(sirius, an_observer, a_gst_time)


        print 'sirius', sirius
        print 'sirius eq', sirius_eq
        print 'sirius hz', sirius_hz
        print 'sirius dec', 90 - sirius_hz.theta.value

        # TODO validate



class TestEcEqXforms(unittest.TestCase):
    """Test ecliptic equatorial coordinate transformations

    Validated against http://lambda.gsfc.nasa.gov/toolbox/tb_coordconv.cfm
    """

    def setUp(self):
        """Set up test parameters."""

        self.places = 5 # precision limited by LAMBDA-tools reporting
        self.eceq_xform = Transforms.EclipticEquatorial()

    def getLatitude(self, a_point):
        """Return latitude of point"""
        return Transforms.Transforms.spherical2latitude(a_point)

    def getLongitude(self, a_point):
        """Return longitude of point"""
        return Transforms.Transforms.spherical2longitude(a_point)


    def test_first_point_of_Aries(self):
        """Test J2000 first point of Aries"""

        j2000 = coords.datetime('2000-01-01T00:00:00')
        a_point = coords.spherical(coords.Ux)

        a_point_ec = self.eceq_xform.toEcliptic(a_point, j2000)
        self.assertAlmostEqual(0, self.getLatitude(a_point_ec), self.places)
        self.assertAlmostEqual(0, self.getLongitude(a_point_ec), self.places)

        a_point_eq = self.eceq_xform.toEquatorial(a_point, j2000)
        self.assertAlmostEqual(0, self.getLatitude(a_point_eq), self.places)
        self.assertAlmostEqual(360, self.getLongitude(a_point_eq), self.places)


    def test_North_Pole(self):
        """Test J2000 North Pole"""

        j2000 = coords.datetime('2000-01-01T00:00:00')
        a_point = coords.spherical(1, coords.declination(90), coords.angle(0))

        a_point_ec = self.eceq_xform.toEcliptic(a_point, j2000)
        self.assertAlmostEqual(66.56071, self.getLatitude(a_point_ec), self.places)
        self.assertAlmostEqual(90, self.getLongitude(a_point_ec), self.places)

        a_point_eq = self.eceq_xform.toEquatorial(a_point, j2000)
        self.assertAlmostEqual(66.56071, self.getLatitude(a_point_eq), self.places)
        self.assertAlmostEqual(270.00000, self.getLongitude(a_point_eq), self.places)


    def test_lat_0_long_15(self):
        """Test J2000 Latitude 0, Longitude 15"""

        j2000 = coords.datetime('2000-01-01T00:00:00')
        a_point = coords.spherical(1, coords.declination(0), coords.angle(15))

        a_point_ec = self.eceq_xform.toEcliptic(a_point, j2000)
        self.assertAlmostEqual(-5.90920, self.getLatitude(a_point_ec), self.places)
        self.assertAlmostEqual(13.81162, self.getLongitude(a_point_ec), self.places)

        a_point_eq = self.eceq_xform.toEquatorial(a_point, j2000)
        self.assertAlmostEqual(5.90920, self.getLatitude(a_point_eq), self.places)
        self.assertAlmostEqual(13.81162, self.getLongitude(a_point_eq), self.places)


    def test_lat_0_long_345(self):
        """Test J2000 Latitude 0, Longitude 345"""

        j2000 = coords.datetime('2000-01-01T00:00:00')
        a_point = coords.spherical(1, coords.declination(0), coords.angle(345))

        a_point_ec = self.eceq_xform.toEcliptic(a_point, j2000)
        self.assertAlmostEqual(5.90920, self.getLatitude(a_point_ec), self.places)
        self.assertAlmostEqual(346.18838, self.getLongitude(a_point_ec), self.places)

        a_point_eq = self.eceq_xform.toEquatorial(a_point, j2000)
        self.assertAlmostEqual(-5.90920, self.getLatitude(a_point_eq), self.places)
        self.assertAlmostEqual(346.18838, self.getLongitude(a_point_eq), self.places)


    def test_lat_45_long_100(self):
        """Test J2000 Latitude 45, Longitude 100"""

        j2000 = coords.datetime('2000-01-01T00:00:00')
        a_point = coords.spherical(1, coords.declination(45), coords.angle(100))

        a_point_ec = self.eceq_xform.toEcliptic(a_point, j2000)
        self.assertAlmostEqual(21.82420, self.getLatitude(a_point_ec), self.places)
        self.assertAlmostEqual(97.60065, self.getLongitude(a_point_ec), self.places)

        a_point_eq = self.eceq_xform.toEquatorial(a_point, j2000)
        self.assertAlmostEqual(67.78257, self.getLatitude(a_point_eq), self.places)
        self.assertAlmostEqual(108.94923, self.getLongitude(a_point_eq), self.places)


    def test_lat_n30_long_n30(self):
        """Test J2000 Latitude -30, Longitude -30"""

        j2000 = coords.datetime('2000-01-01T00:00:00')
        a_point = coords.spherical(1, coords.declination(-30), coords.angle(-30))

        a_point_ec = self.eceq_xform.toEcliptic(a_point, j2000)
        self.assertAlmostEqual(-16.64844, self.getLatitude(a_point_ec), self.places)
        self.assertAlmostEqual(321.51905, self.getLongitude(a_point_ec), self.places)

        a_point_eq = self.eceq_xform.toEquatorial(a_point, j2000)
        self.assertAlmostEqual(-39.12273, self.getLatitude(a_point_eq), self.places)
        self.assertAlmostEqual(345.18327, self.getLongitude(a_point_eq), self.places)


    def test_lat_n60_long_200(self):
        """Test J2015 Latitude -60, Longitude 200"""

        j2015 = coords.datetime('2015-01-01T00:00:00')
        a_point = coords.spherical(1, coords.declination(-60), coords.angle(200))

        a_point_ec = self.eceq_xform.toEcliptic(a_point, j2015)
        self.assertAlmostEqual(-46.59844, self.getLatitude(a_point_ec), self.places)
        self.assertAlmostEqual(226.85843, self.getLongitude(a_point_ec), self.places)

        a_point_eq = self.eceq_xform.toEquatorial(a_point, j2015)
        self.assertAlmostEqual(-59.60899, self.getLatitude(a_point_eq), self.places)
        self.assertAlmostEqual(158.23870, self.getLongitude(a_point_eq), self.places)


    def test_lat_20_long_n10(self):
        """Test J2015 Latitude 20, Longitude -10"""

        j2015 = coords.datetime('2015-01-01T00:00:00')
        a_point = coords.spherical(1, coords.declination(20), coords.angle(-10))

        a_point_ec = self.eceq_xform.toEcliptic(a_point, j2015)
        self.assertAlmostEqual(22.25346, self.getLatitude(a_point_ec), self.places)
        self.assertAlmostEqual(359.15333, self.getLongitude(a_point_ec), self.places)

        a_point_eq = self.eceq_xform.toEquatorial(a_point, j2015)
        self.assertAlmostEqual(14.41240, self.getLatitude(a_point_eq), self.places)
        self.assertAlmostEqual(342.84035, self.getLongitude(a_point_eq), self.places)



if __name__ == '__main__':
    unittest.main()
