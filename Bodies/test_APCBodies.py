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
        """Test mini sun

        validate with SunPosition.SunPosition and
        http://www.esrl.noaa.gov/gmd/grad/solcalc/

        """

        an_observer = coords.spherical(1, coords.latitude(37, 24), coords.angle(-122, 4, 57))

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




    @unittest.skip('todo')
    def test_analemma(self):
        """Test mini sun

        TODO generating data for an analemma:

        maximum altitude (minimum colatitude) is July 21, not June 21

        azimuth snaps from 178 to 97 on 2015-01-04.
        L snaps from 4.9 to 0.01 at the same time
        """

        an_observer = coords.spherical(1, coords.latitude(37, 24), coords.angle(-122, 4, 57))

        a_datetime = coords.datetime('2015-01-01T12:00:00')

        for d in xrange(1, 365):

            a_datetime += 1

            print a_datetime,  # TODO rm

            sun_eq = APCBodies.MiniSun(a_datetime)

            sun_hz = EquatorialHorizon.toHorizon(sun_eq, an_observer, a_datetime)

            print 'colatitude', sun_hz.theta, 'azimuth', sun_hz.phi # TODO rm


if __name__ == '__main__':
    unittest.main()
