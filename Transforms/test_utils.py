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

from __future__ import absolute_import # for python 2 and 3

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

        return


    def test_JulianCentury_2000(self):
        """Test Julian Century 2000"""
        a_datetime = coords.datetime('2000-01-01T12:00:00')
        a_Julian_century = utils.JulianCentury(a_datetime)
        self.assertEqual(0, a_Julian_century)

        return


    def test_JulianCentury_2100(self):
        """Test Julian Century 2100"""
        a_datetime = coords.datetime('2100-01-01T12:00:00')
        a_Julian_century = utils.JulianCentury(a_datetime)
        self.assertEqual(1, a_Julian_century)

        return


    def test_get_latitude_npole(self):
        """Test get_latitude north pole"""
        a_point = coords.spherical(1)
        a_latitude = utils.get_latitude(a_point)
        self.assertEqual(90, a_latitude.degrees)

        return


    def test_get_latitude_equator(self):
        """Test get_latitude equator"""
        a_point = coords.spherical(1, coords.angle(90))
        a_latitude = utils.get_latitude(a_point)
        self.assertEqual(0, a_latitude.degrees)

        return


    def test_get_latitude_spole(self):
        """Test get_latitude south pole"""
        a_point = coords.spherical(1, coords.angle(180))
        a_latitude = utils.get_latitude(a_point)
        self.assertEqual(-90, a_latitude.degrees)

        return


    def test_get_longitude_prime_meridian(self):
        """Test get_latitude prime meridian"""
        a_point = coords.spherical(1)
        a_longitude = utils.get_longitude(a_point)
        self.assertEqual(0, a_longitude.degrees)

        return


    def test_get_longitude_dateline(self):
        """Test get_latitude date line"""
        a_point = coords.spherical(1, coords.angle(0), coords.angle(180))
        a_longitude = utils.get_longitude(a_point)
        self.assertEqual(180, a_longitude.degrees)

        return


    def test_get_longitude_45_east(self):
        """Test get_latitude 45 east"""
        a_point = coords.spherical(1, coords.angle(0), coords.angle(45))
        a_longitude = utils.get_longitude(a_point)
        self.assertEqual(45, a_longitude.degrees)

        return


    def test_get_longitude_45_west(self):
        """Test get_latitude 45 west"""
        a_point = coords.spherical(1, coords.angle(0), coords.angle(-45))
        a_longitude = utils.get_longitude(a_point)
        self.assertEqual(-45, a_longitude.degrees)

        return


    def test_get_RA_45_east(self):
        """Test get_RA 45 east"""
        a_point = coords.spherical(1, coords.angle(0), coords.angle(45))
        a_right_ascension = a_point.phi.RA
        self.assertEqual(3, a_right_ascension)

        return


    def test_get_RA_45_west(self):
        """Test get_RA 45 west"""
        a_point = coords.spherical(1, coords.angle(0), coords.angle(-45))
        a_right_ascension = a_point.phi.RA
        self.assertEqual(21.0, a_right_ascension)

        return


    def test_azalt2spherical_1(self):
        """Test azimuth, altitude 2 spherical 1"""
        a_point = utils.azalt2spherical(an_azimuth=utils.parse_angle_arg('248:02:0.77676'),
                                        an_altitude=utils.parse_angle_arg('15:07:30.0779'))

        self.assertAlmostEqual(248.03354910000002, a_point.phi.degrees) # azimuth
        self.assertAlmostEqual(15.125021649800004, a_point.theta.complement().degrees) # altiude

        return


    def test_latlon2spherical_1(self):
        """Test latitude, longitude to spherical 1"""
        a_point = utils.latlon2spherical(a_latitude=utils.parse_angle_arg('37:24'),
                                         a_longitude=utils.parse_angle_arg('-122:04:57'))

        self.assertAlmostEqual(37.4, utils.get_latitude(a_point).degrees)
        self.assertAlmostEqual(-122.0825, utils.get_longitude(a_point).degrees)

        return


    def test_radec2spherical_1(self):
        """Test RA, declination 2 spherical 1"""
        a_point = utils.radec2spherical(a_right_ascension=utils.parse_angle_arg('23:09:16.641'),
                                        a_declination=utils.parse_angle_arg('-6:43:11.61'))

        self.assertAlmostEqual(23.154622500000002, a_point.phi.RA)
        self.assertAlmostEqual(-6.719891666666669, a_point.theta.complement().degrees)

        return



class GetAzimuthTests(unittest.TestCase):
    """Test get azimuth"""


    def test_theta0(self):
        """Test at latitude 0, longitude 45 degrees"""

        a_point = coords.spherical(1, coords.angle(0), coords.angle(45))
        self.assertEqual(45, a_point.phi.degrees)

        return


    def test_theta45(self):
        """Test at latitude 45, longitude 45 degrees"""

        a_point = coords.spherical(1, coords.angle(45), coords.angle(45))
        self.assertEqual(45, a_point.phi.degrees)

        return



    def test_theta135(self):
        """Test at latitude 135, longitude 45 degrees"""

        a_point = coords.spherical(1, coords.angle(90+45), coords.angle(45))
        self.assertEqual(45, a_point.phi.degrees)

        return


    def test_theta180(self):
        """Test at latitude 180, longitude 45 degrees"""

        a_point = coords.spherical(1, coords.angle(180), coords.angle(45))
        self.assertEqual(45, a_point.phi.degrees)

        return



if __name__ == '__main__':
    unittest.main()
