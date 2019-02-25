#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Unit tests for Right Ascension, declination, Ecliptic and Equatorial transforms


To Run:

$ PYTHONPATH=../.. ./test_EclipticEquatorial.py
.........
----------------------------------------------------------------------
Ran 9 tests in 0.002s

OK


To Debug:

$ PYTHONPATH=../.. python -m pdb ./test_EclipticEquatorial.py  EclipticEquatorialTests.test_lat_0_long_15
> /Users/lrm/src/starbug/AAI/Transforms/test_EclipticEquatorial.py(26)<module>()
->
(Pdb) n

"""

from __future__ import absolute_import  # for python 2 and 3


import math
import time
import unittest

import starbug.coords as coords
import AAI.Transforms.EclipticEquatorial
import AAI.Transforms.utils


class EclipticEquatorialTests(unittest.TestCase):
    """Test ecliptic equatorial coordinate transformations

    Validated against http://lambda.gsfc.nasa.gov/toolbox/tb_coordconv.cfm
    """

    def setUp(self):
        """Set up test parameters."""

        self.places = 5 # precision limited by LAMBDA-tools reporting


    def test_first_point_of_Aries(self):
        """Test J2000 first point of Aries"""

        j2000 = coords.datetime('2000-01-01T00:00:00')
        an_object = coords.spherical(coords.Cartesian.Ux)

        an_object_ec = AAI.Transforms.EclipticEquatorial.toEcliptic(an_object, j2000)
        self.assertAlmostEqual(0, AAI.Transforms.utils.get_latitude(an_object_ec).value, self.places)
        self.assertAlmostEqual(0, AAI.Transforms.utils.get_longitude(an_object_ec).value, self.places)

        an_object_eq = AAI.Transforms.EclipticEquatorial.toEquatorial(an_object, j2000)
        self.assertAlmostEqual(0, AAI.Transforms.utils.get_latitude(an_object_eq).value, self.places)
        self.assertAlmostEqual(0, AAI.Transforms.utils.get_longitude(an_object_eq).value, self.places)


    def test_North_Pole(self):
        """Test J2000 North Pole"""

        j2000 = coords.datetime('2000-01-01T00:00:00')
        an_object = coords.spherical(1, coords.declination(90), coords.angle(0))

        an_object_ec = AAI.Transforms.EclipticEquatorial.toEcliptic(an_object, j2000)
        self.assertAlmostEqual(66.56071, AAI.Transforms.utils.get_latitude(an_object_ec).value, self.places)
        self.assertAlmostEqual(90, AAI.Transforms.utils.get_longitude(an_object_ec).value, self.places)

        an_object_eq = AAI.Transforms.EclipticEquatorial.toEquatorial(an_object, j2000)
        self.assertAlmostEqual(66.56071, AAI.Transforms.utils.get_latitude(an_object_eq).value, self.places)
        self.assertAlmostEqual(-90, AAI.Transforms.utils.get_longitude(an_object_eq).value, self.places)


    def test_lat_0_long_15(self):
        """Test J2000 Latitude 0, Longitude 15"""

        j2000 = coords.datetime('2000-01-01T00:00:00')
        an_object = coords.spherical(1, coords.declination(0), coords.angle(15))

        an_object_ec = AAI.Transforms.EclipticEquatorial.toEcliptic(an_object, j2000)
        self.assertAlmostEqual(-5.90920, AAI.Transforms.utils.get_latitude(an_object_ec).value, self.places)
        self.assertAlmostEqual(13.81162, AAI.Transforms.utils.get_longitude(an_object_ec).value, self.places)

        an_object_eq = AAI.Transforms.EclipticEquatorial.toEquatorial(an_object, j2000)
        self.assertAlmostEqual(5.90920, AAI.Transforms.utils.get_latitude(an_object_eq).value, self.places)
        self.assertAlmostEqual(13.81162, AAI.Transforms.utils.get_longitude(an_object_eq).value, self.places)


    def test_lat_0_long_345(self):
        """Test J2000 Latitude 0, Longitude 345"""

        j2000 = coords.datetime('2000-01-01T00:00:00')
        an_object = coords.spherical(1, coords.declination(0), coords.angle(345))

        an_object_ec = AAI.Transforms.EclipticEquatorial.toEcliptic(an_object, j2000)
        self.assertAlmostEqual(5.90920, AAI.Transforms.utils.get_latitude(an_object_ec).value, self.places)
        self.assertAlmostEqual(-13.811618068210032, AAI.Transforms.utils.get_longitude(an_object_ec).value, self.places)

        an_object_eq = AAI.Transforms.EclipticEquatorial.toEquatorial(an_object, j2000)
        self.assertAlmostEqual(-5.90920, AAI.Transforms.utils.get_latitude(an_object_eq).value, self.places)
        self.assertAlmostEqual(-13.811618068210034, AAI.Transforms.utils.get_longitude(an_object_eq).value, self.places)


    def test_lat_45_long_100(self):
        """Test J2000 Latitude 45, Longitude 100"""

        j2000 = coords.datetime('2000-01-01T00:00:00')
        an_object = coords.spherical(1, coords.declination(45), coords.angle(100))

        an_object_ec = AAI.Transforms.EclipticEquatorial.toEcliptic(an_object, j2000)
        self.assertAlmostEqual(21.82420, AAI.Transforms.utils.get_latitude(an_object_ec).value, self.places)
        self.assertAlmostEqual(97.60065, AAI.Transforms.utils.get_longitude(an_object_ec).value, self.places)

        an_object_eq = AAI.Transforms.EclipticEquatorial.toEquatorial(an_object, j2000)
        self.assertAlmostEqual(67.78257, AAI.Transforms.utils.get_latitude(an_object_eq).value, self.places)
        self.assertAlmostEqual(108.94923, AAI.Transforms.utils.get_longitude(an_object_eq).value, self.places)


    def test_lat_n30_long_n30(self):
        """Test J2000 Latitude -30, Longitude -30"""

        j2000 = coords.datetime('2000-01-01T00:00:00')
        an_object = coords.spherical(1, coords.declination(-30), coords.angle(-30))

        an_object_ec = AAI.Transforms.EclipticEquatorial.toEcliptic(an_object, j2000)
        self.assertAlmostEqual(-16.64844, AAI.Transforms.utils.get_latitude(an_object_ec).value, self.places)
        self.assertAlmostEqual(-38.480953003793914, AAI.Transforms.utils.get_longitude(an_object_ec).value, self.places)

        an_object_eq = AAI.Transforms.EclipticEquatorial.toEquatorial(an_object, j2000)
        self.assertAlmostEqual(-39.12273, AAI.Transforms.utils.get_latitude(an_object_eq).value, self.places)
        self.assertAlmostEqual(-14.81672658697858, AAI.Transforms.utils.get_longitude(an_object_eq).value, self.places)


    def test_lat_n60_long_200(self):
        """Test J2015 Latitude -60, Longitude 200"""

        j2015 = coords.datetime('2015-01-01T00:00:00')
        an_object = coords.spherical(1, coords.declination(-60), coords.angle(200))

        an_object_ec = AAI.Transforms.EclipticEquatorial.toEcliptic(an_object, j2015)
        self.assertAlmostEqual(-46.59844, AAI.Transforms.utils.get_latitude(an_object_ec).value, self.places)
        self.assertAlmostEqual(-133.14157249262468, AAI.Transforms.utils.get_longitude(an_object_ec).value, self.places)

        an_object_eq = AAI.Transforms.EclipticEquatorial.toEquatorial(an_object, j2015)
        self.assertAlmostEqual(-59.60899, AAI.Transforms.utils.get_latitude(an_object_eq).value, self.places)
        self.assertAlmostEqual(158.23870, AAI.Transforms.utils.get_longitude(an_object_eq).value, self.places)


    def test_lat_20_long_n10(self):
        """Test J2015 Latitude 20, Longitude -10"""

        j2015 = coords.datetime('2015-01-01T00:00:00')
        an_object = coords.spherical(1, coords.declination(20), coords.angle(-10))

        an_object_ec = AAI.Transforms.EclipticEquatorial.toEcliptic(an_object, j2015)
        self.assertAlmostEqual(22.25346, AAI.Transforms.utils.get_latitude(an_object_ec).value, self.places)
        self.assertAlmostEqual(-0.8466711266760562, AAI.Transforms.utils.get_longitude(an_object_ec).value, 0)

        an_object_eq = AAI.Transforms.EclipticEquatorial.toEquatorial(an_object, j2015)
        self.assertAlmostEqual(14.41240, AAI.Transforms.utils.get_latitude(an_object_eq).value, self.places)
        self.assertAlmostEqual(-17.159651455501656, AAI.Transforms.utils.get_longitude(an_object_eq).value, self.places)




    def test_meeus_13a(self):

        """Test Meeus example 13a"""

        pollux = AAI.Transforms.utils.radec2spherical(coords.latitude(7, 45, 18.946), coords.angle(28, 1, 34.26))

        a_datetime = coords.datetime('2015-01-01T00:00:00')

        pollux_ec = AAI.Transforms.EclipticEquatorial.toEcliptic(pollux, a_datetime)

        # Meeus: 6.684170
        self.assertAlmostEqual(6.685962149434033, AAI.Transforms.utils.get_latitude(pollux_ec).value, self.places)

        # Meeus: 113.215630
        self.assertAlmostEqual(113.21571932194666, AAI.Transforms.utils.get_longitude(pollux_ec).value, self.places)



if __name__ == '__main__':
    unittest.main()
