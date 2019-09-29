"""Unit tests for Right Ascension, declination, Ecliptic and Equatorial transforms

to run:  ./pylaunch.sh test_EclipticEquatorial.py
verbose: ./pylaunch.sh test_EclipticEquatorial.py -v
filter:  ./pylaunch.sh test_EclipticEquatorial.py EclipticEquatorialTests.test_lat_0_long_15
debug:   ./pylaunch.sh -m pdb test_EclipticEquatorial.py EclipticEquatorialTests.test_lat_0_long_15

(Pdb) n # until import

(Pdb) n
> /Users/lrm/src/Astronomy/Transforms/test_EclipticEquatorial.py(17)<module>()
-> import EclipticEquatorial
(Pdb) n
> /Users/lrm/src/Astronomy/Transforms/test_EclipticEquatorial.py(18)<module>()
-> import utils

(Pdb) b EclipticEquatorial.EclipticEquatorial._xform
Breakpoint 1 at /Users/lrm/src/Astronomy/Transforms/EclipticEquatorial.py:76
(Pdb) c
> /Users/lrm/src/Astronomy/Transforms/EclipticEquatorial.py(88)_xform()
-> if isinstance(an_object, coords.spherical):

"""

from __future__ import absolute_import # for python 2 and 3

import math
import time
import unittest

import coords
import Transforms.EclipticEquatorial
import Transforms.utils


class EclipticEquatorialTests(unittest.TestCase):
    """Test ecliptic equatorial coordinate transformations

    Validated against http://lambda.gsfc.nasa.gov/toolbox/tb_coordconv.cfm
    """

    def setUp(self):
        """Set up test parameters."""

        self.places = 5 # precision limited by LAMBDA-tools reporting

        return


    def test_first_point_of_Aries(self):
        """Test J2000 first point of Aries"""

        j2000 = coords.datetime('2000-01-01T00:00:00')
        an_object = coords.spherical(coords.Cartesian.Ux)

        an_object_ec = Transforms.EclipticEquatorial.toEcliptic(an_object, j2000)
        self.assertAlmostEqual(0, Transforms.utils.get_latitude(an_object_ec).degrees, self.places)
        self.assertAlmostEqual(0, Transforms.utils.get_longitude(an_object_ec).degrees, self.places)

        an_object_eq = Transforms.EclipticEquatorial.toEquatorial(an_object, j2000)
        self.assertAlmostEqual(0, Transforms.utils.get_latitude(an_object_eq).degrees, self.places)
        self.assertAlmostEqual(0, Transforms.utils.get_longitude(an_object_eq).degrees, self.places)

        return


    def test_North_Pole(self):
        """Test J2000 North Pole"""

        j2000 = coords.datetime('2000-01-01T00:00:00')
        an_object = coords.spherical(1, coords.declination(90), coords.angle(0))

        an_object_ec = Transforms.EclipticEquatorial.toEcliptic(an_object, j2000)
        self.assertAlmostEqual(66.56071, Transforms.utils.get_latitude(an_object_ec).degrees, self.places)
        self.assertAlmostEqual(90, Transforms.utils.get_longitude(an_object_ec).degrees, self.places)

        an_object_eq = Transforms.EclipticEquatorial.toEquatorial(an_object, j2000)
        self.assertAlmostEqual(66.56071, Transforms.utils.get_latitude(an_object_eq).degrees, self.places)
        self.assertAlmostEqual(-90, Transforms.utils.get_longitude(an_object_eq).degrees, self.places)

        return


    def test_lat_0_long_15(self):
        """Test J2000 Latitude 0, Longitude 15"""

        j2000 = coords.datetime('2000-01-01T00:00:00')
        an_object = coords.spherical(1, coords.declination(0), coords.angle(15))

        an_object_ec = Transforms.EclipticEquatorial.toEcliptic(an_object, j2000)
        self.assertAlmostEqual(-5.90920, Transforms.utils.get_latitude(an_object_ec).degrees, self.places)
        self.assertAlmostEqual(13.81162, Transforms.utils.get_longitude(an_object_ec).degrees, self.places)

        an_object_eq = Transforms.EclipticEquatorial.toEquatorial(an_object, j2000)
        self.assertAlmostEqual(5.90920, Transforms.utils.get_latitude(an_object_eq).degrees, self.places)
        self.assertAlmostEqual(13.81162, Transforms.utils.get_longitude(an_object_eq).degrees, self.places)

        return


    def test_lat_0_long_345(self):
        """Test J2000 Latitude 0, Longitude 345"""

        j2000 = coords.datetime('2000-01-01T00:00:00')
        an_object = coords.spherical(1, coords.declination(0), coords.angle(345))

        an_object_ec = Transforms.EclipticEquatorial.toEcliptic(an_object, j2000)
        self.assertAlmostEqual(5.90920, Transforms.utils.get_latitude(an_object_ec).degrees, self.places)
        self.assertAlmostEqual(-13.811618068210032, Transforms.utils.get_longitude(an_object_ec).degrees, self.places)

        an_object_eq = Transforms.EclipticEquatorial.toEquatorial(an_object, j2000)
        self.assertAlmostEqual(-5.90920, Transforms.utils.get_latitude(an_object_eq).degrees, self.places)
        self.assertAlmostEqual(-13.811618068210034, Transforms.utils.get_longitude(an_object_eq).degrees, self.places)

        return


    def test_lat_45_long_100(self):
        """Test J2000 Latitude 45, Longitude 100"""

        j2000 = coords.datetime('2000-01-01T00:00:00')
        an_object = coords.spherical(1, coords.declination(45), coords.angle(100))

        an_object_ec = Transforms.EclipticEquatorial.toEcliptic(an_object, j2000)
        self.assertAlmostEqual(21.82420, Transforms.utils.get_latitude(an_object_ec).degrees, self.places)
        self.assertAlmostEqual(97.60065, Transforms.utils.get_longitude(an_object_ec).degrees, self.places)

        an_object_eq = Transforms.EclipticEquatorial.toEquatorial(an_object, j2000)
        self.assertAlmostEqual(67.78257, Transforms.utils.get_latitude(an_object_eq).degrees, self.places)
        self.assertAlmostEqual(108.94923, Transforms.utils.get_longitude(an_object_eq).degrees, self.places)

        return


    def test_lat_n30_long_n30(self):
        """Test J2000 Latitude -30, Longitude -30"""

        j2000 = coords.datetime('2000-01-01T00:00:00')
        an_object = coords.spherical(1, coords.declination(-30), coords.angle(-30))

        an_object_ec = Transforms.EclipticEquatorial.toEcliptic(an_object, j2000)
        self.assertAlmostEqual(-16.64844, Transforms.utils.get_latitude(an_object_ec).degrees, self.places)
        self.assertAlmostEqual(-38.480953003793914, Transforms.utils.get_longitude(an_object_ec).degrees, self.places)

        an_object_eq = Transforms.EclipticEquatorial.toEquatorial(an_object, j2000)
        self.assertAlmostEqual(-39.12273, Transforms.utils.get_latitude(an_object_eq).degrees, self.places)
        self.assertAlmostEqual(-14.81672658697858, Transforms.utils.get_longitude(an_object_eq).degrees, self.places)

        return


    def test_lat_n60_long_200(self):
        """Test J2015 Latitude -60, Longitude 200"""

        j2015 = coords.datetime('2015-01-01T00:00:00')
        an_object = coords.spherical(1, coords.declination(-60), coords.angle(200))

        an_object_ec = Transforms.EclipticEquatorial.toEcliptic(an_object, j2015)
        self.assertAlmostEqual(-46.59844, Transforms.utils.get_latitude(an_object_ec).degrees, self.places)
        self.assertAlmostEqual(-133.14157249262468, Transforms.utils.get_longitude(an_object_ec).degrees, self.places)

        an_object_eq = Transforms.EclipticEquatorial.toEquatorial(an_object, j2015)
        self.assertAlmostEqual(-59.60899, Transforms.utils.get_latitude(an_object_eq).degrees, self.places)
        self.assertAlmostEqual(158.23870, Transforms.utils.get_longitude(an_object_eq).degrees, self.places)

        return


    def test_lat_20_long_n10(self):
        """Test J2015 Latitude 20, Longitude -10"""

        j2015 = coords.datetime('2015-01-01T00:00:00')
        an_object = coords.spherical(1, coords.declination(20), coords.angle(-10))

        an_object_ec = Transforms.EclipticEquatorial.toEcliptic(an_object, j2015)
        self.assertAlmostEqual(22.25346, Transforms.utils.get_latitude(an_object_ec).degrees, self.places)
        self.assertAlmostEqual(-0.8466711266760562, Transforms.utils.get_longitude(an_object_ec).degrees, 0)

        an_object_eq = Transforms.EclipticEquatorial.toEquatorial(an_object, j2015)
        self.assertAlmostEqual(14.41240, Transforms.utils.get_latitude(an_object_eq).degrees, self.places)
        self.assertAlmostEqual(-17.159651455501656, Transforms.utils.get_longitude(an_object_eq).degrees, self.places)

        return


    def test_meeus_13a(self):

        """Test Meeus example 13a"""

        pollux = Transforms.utils.radec2spherical(coords.latitude(7, 45, 18.946), coords.angle(28, 1, 34.26))

        a_datetime = coords.datetime('2015-01-01T00:00:00')

        pollux_ec = Transforms.EclipticEquatorial.toEcliptic(pollux, a_datetime)

        # Meeus: 6.684170
        self.assertAlmostEqual(6.685962149434033, Transforms.utils.get_latitude(pollux_ec).degrees, self.places)

        # Meeus: 113.215630
        self.assertAlmostEqual(113.21571932194666, Transforms.utils.get_longitude(pollux_ec).degrees, self.places)


        return



class MeeusEclipticEquatorialTests(unittest.TestCase):
    """Test ecliptic equatorial coordinate transformations"""

    def setUp(self):
        """Set up test parameters."""

        self.places = 8

        return


    def test_meeus_13a(self):

        """Test Meeus example 13a

        I use a different formula (see EclipticEquatorial.py) for and
        get a different value for the obliquity of the ecliptic on
        this date. Meeus has 23.4392911 vs. 23.4373411286. If I
        hardcode this I get 6.669018753709949 for the declination and
        113.215629227584 for RA.
        """

        a_datetime = coords.datetime('2015-01-01T00:00:00')

        pollux = Transforms.utils.radec2spherical(coords.latitude(7, 45, 18.946), coords.angle(28, 1, 34.26))

        pollux_ec = Transforms.EclipticEquatorial.Meeus.toEcliptic(pollux, a_datetime)

        # Meeus: 6.684170
        self.assertAlmostEqual(6.685962149434033, Transforms.utils.get_latitude(pollux_ec).degrees, self.places)

        # Meeus: 113.215630
        self.assertAlmostEqual(113.21571932194666, Transforms.utils.get_longitude(pollux_ec).degrees, self.places)

        return


    def test_meeus_reverse_13a(self):

        """Test Meeus example 13a in reverse"""

        a_datetime = coords.datetime('2015-01-01T00:00:00')

        pollux = Transforms.utils.latlon2spherical(coords.latitude(6.68417), coords.angle(113.21563))

        pollux_ec = Transforms.EclipticEquatorial.Meeus.toEquatorial(pollux, a_datetime)

        # Meeus: 07:45:18.946 vs. my 07:45:18.8357
        self.assertAlmostEqual(7.755232144485258, pollux_ec.phi.RA, self.places)

        # Meeus 28.026183
        self.assertAlmostEqual(28.02443543646086, pollux_ec.theta.complement().degrees, self.places)

        return





if __name__ == '__main__':
    unittest.main()
