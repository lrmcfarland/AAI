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


class MiniSun(unittest.TestCase):
    """Test mini sun calculations"""


    def setUp(self):
        """Set up test parameters."""

        self.places = 12

        self.mlc404 = utils.latlon2spherical(a_latitude=coords.angle(37, 24),
                                             a_longitude=coords.angle(-122, 4, 56))


    def test_2015_01_01T1200(self):
        """Test mini sun 2015-01-01T12:00:00-08

        validate with http://www.esrl.noaa.gov/gmd/grad/solcalc/
        and SunPosition.SunPosition
        """

        a_datetime = coords.datetime('2015-01-01T12:00:00-08')

        sun_hz = APCBodies.SunPosition(self.mlc404, a_datetime)

        # noaa: 176.85
        # SunPosition: 176.93209352
        self.assertAlmostEqual(176.26017129238437, utils.get_azimuth(sun_hz).value, self.places)

        # noaa: 29.59
        # SunPosition: 29.5085142925
        self.assertAlmostEqual(29.52550042910097, utils.get_altitude(sun_hz).value, self.places)


    def test_2015_04_29T1200(self):
        """Test mini sun 2015-04-29T12:00:00-07

        validate with http://www.esrl.noaa.gov/gmd/grad/solcalc/
        and SunPosition.SunPosition
        """

        a_datetime = coords.datetime('2015-04-29T12:00:00-07')

        sun_hz = APCBodies.SunPosition(self.mlc404, a_datetime)

        # noaa: 143.1
        # SunPosition: 143.257198509
        self.assertAlmostEqual(80.82240618150763, utils.get_azimuth(sun_hz).value, self.places)
        # TODO: way out

        # noaa: 62.89
        # SunPosition: 62.7193776732
        self.assertAlmostEqual(28.074501187751423, utils.get_altitude(sun_hz).value, self.places)
        # TODO: way out


    def test_sextant_2015_05_01(self):
        """Test against sextant measurement

        The sun angle is measured with a sextant using a swimming pool
        as an artificial horizon.

        Calm morning, no wind, clear image.

        Sextant reading 66:46/2 = 33:23         (33.3833333333)  degrees altitude
        SunPosition             = 32:36:24.6968 (32.6068602091)  degrees altitude
        APC mini sun            = -3:55:13.4557 (-3.92040435387) degrees altitude TODO way out!

        Star Walk               = 32:49:24 degrees altitude, 95:55:24 degrees azimuth
        TODO taken from 37:27N, -122:11, adjust to 404 MLC
        """

        a_datetime = coords.datetime('2015-05-01T09:05:00-07')

        sun = APCBodies.SunPosition(self.mlc404, a_datetime)

        # TODO way out from Star Walk
        self.assertAlmostEqual(56.3810698513805, utils.get_azimuth(sun).value, self.places)
        self.assertAlmostEqual(-3.9202205930785112, utils.get_altitude(sun).value, delta=2)





    def test_RiseAndSet(self):
        """Rise and Set

        TODO move to own class?
        """

        a_datetime = coords.datetime('2015-05-01T09:05:00-07')

        sun_ec = APCBodies.MiniSun(a_datetime)
        sun_eq = EclipticEquatorial.toEquatorial(sun_ec, a_datetime)


        foo = APCBodies.RiseAndSetTimes(sun_eq, self.mlc404, a_datetime)


        print 'rise and set', foo # TODO





class MiniMoon(unittest.TestCase):
    """Test mini moon calculations"""


    def setUp(self):
        """Set up test parameters."""

        self.places = 12

        self.mlc404 = utils.latlon2spherical(a_latitude=coords.angle(37, 24),
                                             a_longitude=coords.angle(-122, 4, 56))


    def test_2015_04_29T2200(self):
        """Test mini moon

        The sun angle is measured with a sextant using a swimming pool
        as an artificial horizon.

        A light wind blurred the reflected image

        Sextant reading 105:51.4 (105.85666)/2 = 52.9283333333 degrees altitude
        APC mini moon                          = 55.3244811435 degrees altitude
        Star Walk                              = 52:53:10 degrees altitude, 172:15:43 degrees azimuth
        http://www.dailymoonposition.com       = 52 altitude, 186 azimuth
        """

        a_datetime = coords.datetime('2015-04-29T22:00:00-07')

        moon_hz = APCBodies.MoonPosition(self.mlc404, a_datetime)

        self.assertAlmostEqual(182.38480914363294, utils.get_azimuth(moon_hz).value, self.places)
        self.assertAlmostEqual(55.32447196217382, utils.get_altitude(moon_hz).value, self.places)


    def test_2015_04_30T1830(self):
        """Test mini moon

        The moon angle is measured with a sextant using a swimming pool
        as an artificial horizon.

        Too bright to see the moon in the reflection. Estimated
        location looking location between chimneys on surrounding roofs.

        Sextant reading 40:04.1 (40.068)/2     = 20.034 degrees altitude
        Compass reading 91 magnetic
        APC mini moon                          = 23.17296504771049 degrees altitude
        Star Walk                              = 17:14:46 degrees altitude, 107:19:08 degrees azimuth
        http://www.dailymoonposition.com       = 16 degrees altitude, 121 degrees azimuth

        """

        a_datetime = coords.datetime('2015-04-30T18:30:00-07')

        moon_hz = APCBodies.MoonPosition(self.mlc404, a_datetime)

        self.assertAlmostEqual(109.72031148537829, utils.get_azimuth(moon_hz).value, self.places)
        self.assertAlmostEqual(23.17296504771049, utils.get_altitude(moon_hz).value, self.places)



if __name__ == '__main__':
    unittest.main()
