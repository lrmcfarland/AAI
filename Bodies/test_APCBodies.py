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
from Transforms import EquatorialHorizon


class APCBodyTests(unittest.TestCase):
    """Test APC body calculations"""

    def setUp(self):
        """Set up test parameters."""

        self.places = 5


    def test_analemma(self):
        """Test mini sun

        TODO generating data for an analemma:

        maximum altitude (minimum colatitude) is July 21, not June 21

        azimuth snaps from 178 to 97 on 2015-01-04.
        L snaps from 4.9 to 0.01 at the same time
        """

        an_observer = coords.spherical(1, coords.latitude(37, 24), coords.angle(-122, 4, 57))

        for m in xrange(1, 13):
            for d in xrange(1, 28): # skips some days

                a_datetime = coords.datetime('2015-%02d-%02dT12:00:00' % (m, d))

                print a_datetime,  # TODO rm

                sun_eq = APCBodies.MiniSun(a_datetime)

                sun_hz = EquatorialHorizon.toHorizon(sun_eq, an_observer, a_datetime)

                print 'colatitude', sun_hz.theta, 'azimuth', sun_hz.phi # TODO rm


if __name__ == '__main__':
    unittest.main()
