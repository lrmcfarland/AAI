"""Unit tests for Right Ascension, declination, Ecliptic Equitorial Transforms"""

import math
import time
import unittest

import coords
import Transforms

class TestTransforms(unittest.TestCase):
    """Test RA declination transforms.

    """

    def setUp(self):
        """Set up test parameters."""

        self.places = 5 # precision limited by LAMBDA-tools reporting
        self.xforms = Transforms.Transforms()


    def test_radec2spherical_1(self):
        """Test RA 1, dec 0"""
        some_point = self.xforms.radec2spherical(a_right_ascension=coords.angle(1),
                                                 a_declination=coords.angle(0))

        self.assertAlmostEqual(90, some_point.theta.value)
        self.assertAlmostEqual(15, some_point.phi.value)
        self.assertAlmostEqual(1, self.xforms.spherical2ra(some_point))


    def test_radec2spherical_sirius(self):
        """Test RA/dec of Sirius"""

        some_point = self.xforms.radec2spherical(a_right_ascension=coords.angle(6, 45, 8.9173),
                                                 a_declination=coords.angle(-16, 42, 58.017))

        # TODO validate
        self.assertAlmostEqual(106.71611583333333, some_point.theta.value)
        self.assertAlmostEqual(101.28715541666668, some_point.phi.value)
        self.assertAlmostEqual(6.752477027777778, self.xforms.spherical2ra(some_point))



class TestEcEqXforms(unittest.TestCase):
    """Test ecliptic equitorial coordinate transformations

    Validated against: http://lambda.gsfc.nasa.gov/toolbox/tb_coordconv.cfm
    """

    def setUp(self):
        """Set up test parameters."""

        self.places = 5 # precision limited by LAMBDA-tools reporting
        self.eceq_xform = Transforms.EclipticEquitorial()

    def getLatitude(self, a_point):
        """Return latitude of point"""
        return Transforms.Transforms.spherical2latitude(a_point)

    def getLongitude(self, a_point):
        """Return longitude of point"""
        return Transforms.Transforms.spherical2longitude(a_point)


    def test_first_point_of_Aries(self):
        """Test J2000 first point of Aries"""

        j2000 = coords.datetime('2000-01-01T00:00:00')
        some_point = coords.spherical(coords.Ux)

        some_point_ec = self.eceq_xform.toEcliptic(some_point, j2000)
        self.assertAlmostEqual(0, self.getLatitude(some_point_ec), self.places)
        self.assertAlmostEqual(0, self.getLongitude(some_point_ec), self.places)

        some_point_eq = self.eceq_xform.toEquitorial(some_point, j2000)
        self.assertAlmostEqual(0, self.getLatitude(some_point_eq), self.places)
        self.assertAlmostEqual(360, self.getLongitude(some_point_eq), self.places)


    def test_North_Pole(self):
        """Test J2000 North Pole"""

        j2000 = coords.datetime('2000-01-01T00:00:00')
        some_point = coords.spherical(1, coords.declination(90), coords.angle(0))

        some_point_ec = self.eceq_xform.toEcliptic(some_point, j2000)
        self.assertAlmostEqual(66.56071, self.getLatitude(some_point_ec), self.places)
        self.assertAlmostEqual(90, self.getLongitude(some_point_ec), self.places)

        some_point_eq = self.eceq_xform.toEquitorial(some_point, j2000)
        self.assertAlmostEqual(66.56071, self.getLatitude(some_point_eq), self.places)
        self.assertAlmostEqual(270.00000, self.getLongitude(some_point_eq), self.places)


    def test_lat_0_long_15(self):
        """Test J2000 Latitude 0, Longitude 15"""

        j2000 = coords.datetime('2000-01-01T00:00:00')
        some_point = coords.spherical(1, coords.declination(0), coords.angle(15))

        some_point_ec = self.eceq_xform.toEcliptic(some_point, j2000)
        self.assertAlmostEqual(-5.90920, self.getLatitude(some_point_ec), self.places)
        self.assertAlmostEqual(13.81162, self.getLongitude(some_point_ec), self.places)

        some_point_eq = self.eceq_xform.toEquitorial(some_point, j2000)
        self.assertAlmostEqual(5.90920, self.getLatitude(some_point_eq), self.places)
        self.assertAlmostEqual(13.81162, self.getLongitude(some_point_eq), self.places)


    def test_lat_0_long_345(self):
        """Test J2000 Latitude 0, Longitude 345"""

        j2000 = coords.datetime('2000-01-01T00:00:00')
        some_point = coords.spherical(1, coords.declination(0), coords.angle(345))

        some_point_ec = self.eceq_xform.toEcliptic(some_point, j2000)
        self.assertAlmostEqual(5.90920, self.getLatitude(some_point_ec), self.places)
        self.assertAlmostEqual(346.18838, self.getLongitude(some_point_ec), self.places)

        some_point_eq = self.eceq_xform.toEquitorial(some_point, j2000)
        self.assertAlmostEqual(-5.90920, self.getLatitude(some_point_eq), self.places)
        self.assertAlmostEqual(346.18838, self.getLongitude(some_point_eq), self.places)


    def test_lat_45_long_100(self):
        """Test J2000 Latitude 45, Longitude 100"""

        j2000 = coords.datetime('2000-01-01T00:00:00')
        some_point = coords.spherical(1, coords.declination(45), coords.angle(100))

        some_point_ec = self.eceq_xform.toEcliptic(some_point, j2000)
        self.assertAlmostEqual(21.82420, self.getLatitude(some_point_ec), self.places)
        self.assertAlmostEqual(97.60065, self.getLongitude(some_point_ec), self.places)

        some_point_eq = self.eceq_xform.toEquitorial(some_point, j2000)
        self.assertAlmostEqual(67.78257, self.getLatitude(some_point_eq), self.places)
        self.assertAlmostEqual(108.94923, self.getLongitude(some_point_eq), self.places)


    def test_lat_n30_long_n30(self):
        """Test J2000 Latitude -30, Longitude -30"""

        j2000 = coords.datetime('2000-01-01T00:00:00')
        some_point = coords.spherical(1, coords.declination(-30), coords.angle(-30))

        some_point_ec = self.eceq_xform.toEcliptic(some_point, j2000)
        self.assertAlmostEqual(-16.64844, self.getLatitude(some_point_ec), self.places)
        self.assertAlmostEqual(321.51905, self.getLongitude(some_point_ec), self.places)

        some_point_eq = self.eceq_xform.toEquitorial(some_point, j2000)
        self.assertAlmostEqual(-39.12273, self.getLatitude(some_point_eq), self.places)
        self.assertAlmostEqual(345.18327, self.getLongitude(some_point_eq), self.places)


    def test_lat_n60_long_200(self):
        """Test J2015 Latitude -60, Longitude 200"""

        j2015 = coords.datetime('2015-01-01T00:00:00')
        some_point = coords.spherical(1, coords.declination(-60), coords.angle(200))

        some_point_ec = self.eceq_xform.toEcliptic(some_point, j2015)
        self.assertAlmostEqual(-46.59844, self.getLatitude(some_point_ec), self.places)
        self.assertAlmostEqual(226.85843, self.getLongitude(some_point_ec), self.places)

        some_point_eq = self.eceq_xform.toEquitorial(some_point, j2015)
        self.assertAlmostEqual(-59.60899, self.getLatitude(some_point_eq), self.places)
        self.assertAlmostEqual(158.23870, self.getLongitude(some_point_eq), self.places)


    def test_lat_20_long_n10(self):
        """Test J2015 Latitude 20, Longitude -10"""

        j2015 = coords.datetime('2015-01-01T00:00:00')
        some_point = coords.spherical(1, coords.declination(20), coords.angle(-10))

        some_point_ec = self.eceq_xform.toEcliptic(some_point, j2015)
        self.assertAlmostEqual(22.25346, self.getLatitude(some_point_ec), self.places)
        self.assertAlmostEqual(359.15333, self.getLongitude(some_point_ec), self.places)

        some_point_eq = self.eceq_xform.toEquitorial(some_point, j2015)
        self.assertAlmostEqual(14.41240, self.getLatitude(some_point_eq), self.places)
        self.assertAlmostEqual(342.84035, self.getLongitude(some_point_eq), self.places)



if __name__ == '__main__':
    unittest.main()
