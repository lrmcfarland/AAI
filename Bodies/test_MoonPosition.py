"""Unit tests for Moon Position calculations"""

from __future__ import absolute_import # for python 2 and 3

import math
import time
import unittest

import coords
import MoonPosition

import Transforms.utils


class MoonPositionsTests(unittest.TestCase):
    """Test Moon Position calculations"""

    def setUp(self):
        """Set up test parameters."""

        self.places = 12

        self.mlc404 = Transforms.utils.latlon2spherical(a_latitude=coords.angle(37, 24),
                                                        a_longitude=coords.angle(-122, 4, 56))

        return


    def test_meeus_1992_04_12(self):
        """Meeus p. 342

        TODO obliquity is calculated differently from Meeus

        """

        a_datetime = coords.datetime('1992-04-12T00:00:00')

        ecLon, ecLat, distance = MoonPosition.EclipticCoords(a_datetime)

        self.assertAlmostEqual(133.16061721952093, ecLon.degrees, self.places) # Meeus p. 342    133.162655 + TODO nutation
        self.assertAlmostEqual(-3.227006655576363, ecLat.degrees, self.places) # Meeus p. 342     -3.229126
        self.assertAlmostEqual(368409.6848161269, distance, self.places)     # Meeus p. 342 368409.7 km

        moon_sph = Transforms.utils.latlon2spherical(ecLat, ecLon)
        moon_eq = Transforms.EclipticEquatorial.Meeus.toEquatorial(moon_sph, a_datetime)

        self.assertAlmostEqual(8.978830825564946, Transforms.utils.get_RA(moon_eq).degrees, self.places) # Meeus p. 342
        self.assertEqual('08:58:43.791', str(Transforms.utils.get_RA(moon_eq))) # Meeus p. 342 08:58:45.2


        self.assertAlmostEqual(13.772019869740845, Transforms.utils.get_declination(moon_eq).degrees, self.places) # Meeus p. 342 13.768368
        self.assertEqual('13:46:19.2715', str(Transforms.utils.get_declination(moon_eq))) # Meeus p. 342 13:46:06

        return


if __name__ == '__main__':
    unittest.main()
