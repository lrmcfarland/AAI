"""Unit tests for Right Ascension, declination, Ecliptic and Equatorial transforms

to run:  ./pylaunch.sh test_APCTransforms.py
verbose: ./pylaunch.sh test_APCTransforms.py -v
filter:  ./pylaunch.sh test_APCTransforms.py -v test_GMST
debug:   ./pylaunch.sh -m pdb test_APCTransforms.py

next until import module:

(Pdb) n
> /Users/lrm/src/Astronomy/Transforms/test_APCTransforms.py(25)<module>()
-> import APCTransforms
(Pdb) b APCTransforms.APCTransforms.GMST
Breakpoint 1 at /Users/lrm/src/Astronomy/Transforms/APCTransforms.py:17


"""

import math
import time
import unittest

import coords
import APCBodies

from Transforms import EclipticEquatorial
from Transforms import EquatorialHorizon
from Transforms import utils


class APCBodyTests(unittest.TestCase):
    """Test APC body calculations"""


    def setUp(self):
        """Set up test parameters."""

        self.places = 12

        self.mlc404 = utils.latlon2spherical(a_latitude=coords.angle(37, 24),
                                             a_longitude=coords.angle(-122, 4, 56))


    def test_minisun_2015_01_01T1200(self):
        """Test mini sun 2015-01-01T12:00:00-08

        validate with http://www.esrl.noaa.gov/gmd/grad/solcalc/
        and SunPosition.SunPosition
        """

        a_datetime = coords.datetime('2015-01-01T12:00:00-08')

        sun_ec = APCBodies.MiniSun(a_datetime)
        sun_eq = EclipticEquatorial.toEquatorial(sun_ec, a_datetime)
        sun_hz = EquatorialHorizon.toHorizon(sun_eq, self.mlc404, a_datetime)

        # noaa: 176.85
        # SunPosition: 176.93209352
        self.assertAlmostEqual(176.26017129238437, utils.get_azimuth(sun_hz).value, self.places)

        # noaa: 29.59
        # SunPosition: 29.5085142925
        self.assertAlmostEqual(29.52550042910097, utils.get_altitude(sun_hz).value, self.places)


    def test_minimoon_2015_04_29T1700(self):
        """Test mini moon

        """

        a_datetime = coords.datetime('2015-04-29T17:00:00-07')

        moon_ec = APCBodies.MiniMoon(a_datetime)
        moon_eq = EclipticEquatorial.toEquatorial(moon_ec, a_datetime)
        moon_hz = EquatorialHorizon.toHorizon(moon_eq, self.mlc404, a_datetime)

        # Star Walk: 96:22:55
        self.assertAlmostEqual(98.63462904038198, utils.get_azimuth(moon_hz).value, self.places)

        # Star Walk: 10:29:00
        self.assertAlmostEqual(16.786314348482563, utils.get_altitude(moon_hz).value, self.places)


if __name__ == '__main__':
    unittest.main()
