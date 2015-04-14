"""Test transform utilities

to run:  ./pylaunch.sh test_utils.py
verbose: ./pylaunch.sh test_utils.py -v
filter:  ./pylaunch.sh test_utils.py UtilsTests.test_get_latitude_npole
debug:   ./pylaunch.sh -m pdb test_utils.py

(Pdb) n
> /Users/lrm/src/Astronomy/Transforms/test_utils.py(12)<module>()
-> import math

repeat until

(Pdb)
> /Users/lrm/src/Astronomy/Transforms/test_utils.py(17)<module>()
-> import utils
(Pdb) b utils.get_latitude
Breakpoint 1 at /Users/lrm/src/Astronomy/Transforms/utils.py:14
(Pdb) c
..> /Users/lrm/src/Astronomy/Transforms/utils.py(23)get_latitude()
-> if not isinstance(a_point, coords.spherical):

"""

import math
import time
import unittest

import coords
import utils

class UtilsTests(unittest.TestCase):
    """Test utilities."""

    def setUp(self):
        """Set up test parameters."""

        self.places = 5


    def test_get_latitude_npole(self):
        """Test get_latitude north pole"""
        a_point = coords.spherical(1)
        a_latitude = utils.get_latitude(a_point)
        self.assertEqual(90, a_latitude.value)


    def test_get_latitude_equator(self):
        """Test get_latitude equator"""
        a_point = coords.spherical(1, coords.angle(90))
        a_latitude = utils.get_latitude(a_point)
        self.assertEqual(0, a_latitude.value)


    def test_get_latitude_spole(self):
        """Test get_latitude south pole"""
        a_point = coords.spherical(1, coords.angle(180))
        a_latitude = utils.get_latitude(a_point)
        self.assertEqual(-90, a_latitude.value)


    def test_get_longitude_prime_meridian(self):
        """Test get_latitude prime meridian"""
        a_point = coords.spherical(1)
        a_longitude = utils.get_longitude(a_point)
        self.assertEqual(0, a_longitude.value)


    def test_get_longitude_dateline(self):
        """Test get_latitude date line"""
        a_point = coords.spherical(1, coords.angle(0), coords.angle(180))
        a_longitude = utils.get_longitude(a_point)
        self.assertEqual(180, a_longitude.value)


    def test_get_longitude_45_east(self):
        """Test get_latitude 45 east"""
        a_point = coords.spherical(1, coords.angle(0), coords.angle(45))
        a_longitude = utils.get_longitude(a_point)
        self.assertEqual(45, a_longitude.value)


    def test_get_longitude_45_west(self):
        """Test get_latitude 45 west"""
        a_point = coords.spherical(1, coords.angle(0), coords.angle(-45))
        a_longitude = utils.get_longitude(a_point)
        self.assertEqual(315, a_longitude.value)


    def test_get_RA_45_east(self):
        """Test get_RA 45 east"""
        a_point = coords.spherical(1, coords.angle(0), coords.angle(45))
        a_right_ascension = utils.get_RA(a_point)
        self.assertEqual(3, a_right_ascension.value)


    def test_get_RA_45_west(self):
        """Test get_RA 45 west"""
        a_point = coords.spherical(1, coords.angle(0), coords.angle(-45))
        a_right_ascension = utils.get_RA(a_point)
        self.assertEqual(21, a_right_ascension.value)


    def test_radec2spherical_1(self):
        """Test RA 1, dec 0"""
        a_point = utils.radec2spherical(a_right_ascension=coords.angle(1),
                                                 a_declination=coords.angle(0))

        self.assertAlmostEqual(90, a_point.theta.value)
        self.assertAlmostEqual(15, a_point.phi.value)
        self.assertAlmostEqual(1, utils.get_RA(a_point).value)


    def test_JulianCentury_2000(self):
        """Test Julian Century 2000"""
        a_datetime = coords.datetime('2000-01-01T12:00:00')
        a_Julian_century = utils.JulianCentury(a_datetime)
        self.assertEqual(0, a_Julian_century)


    def test_JulianCentury_2100(self):
        """Test Julian Century 2100"""
        a_datetime = coords.datetime('2100-01-01T12:00:00')
        a_Julian_century = utils.JulianCentury(a_datetime)
        self.assertEqual(1, a_Julian_century)

if __name__ == '__main__':
    unittest.main()
