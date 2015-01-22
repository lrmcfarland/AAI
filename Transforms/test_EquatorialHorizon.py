"""Unit tests for Right Ascension, declination, Ecliptic and Equatorial transforms


to run:  ./pylaunch.sh test_EquatorialHorizon.py
verbose: ./pylaunch.sh test_EquatorialHorizon.py -v
filter:  ./pylaunch.sh test_EquatorialHorizon.py -v EquatorialHorizonTests.test_sirius_2014_12_31T20_41_41
debug:   ./pylaunch.sh -m pdb test_EquatorialHorizon.py -v EquatorialHorizonTests.test_sirius_2014_12_31T20_41_41

(Pdb) n # until import

> /Users/lrm/src/Astronomy/Transforms/test_EquatorialHorizon.py(20)<module>()
-> import EquatorialHorizon
(Pdb)
> /Users/lrm/src/Astronomy/Transforms/test_EquatorialHorizon.py(21)<module>()
-> import utils
(Pdb) b EquatorialHorizon.EquatorialHorizon.toHorizon
Breakpoint 1 at /Users/lrm/src/Astronomy/Transforms/EquatorialHorizon.py:77
(Pdb) c
test_sirius_2014_12_31T20_41_41 (__main__.EquatorialHorizonTests)
Test RA/dec of Sirius 2014-12-31T20:41:41 ... > /Users/lrm/src/Astronomy/Transforms/EquatorialHorizon.py(95)toHorizon()
-> debug = False
(Pdb)


"""

import math
import time
import unittest

import coords
import EquatorialHorizon
import utils


class EquatorialHorizonTests(unittest.TestCase):
    """Test equatorial horizon transforms"""

    def setUp(self):
        """Set up test parameters."""

        self.places = 13 # limit 15

        self.sirius = utils.radec2spherical(a_right_ascension=coords.angle(6, 45, 8.9173),
                                            a_declination=coords.angle(-16, 42, 58.017))


    def assertSpacesAreEqual(self, lhs_space, rhs_space):
        """Space assert helper method with limited places."""
        self.assertAlmostEqual(lhs_space.r, rhs_space.r, places=self.places)
        self.assertAlmostEqual(lhs_space.theta.value, rhs_space.theta.value, places=self.places)
        self.assertAlmostEqual(lhs_space.phi.value, rhs_space.phi.value, places=self.places)


    def test_sirius_2014_12_31T20_41_41(self):
        """Test RA/dec of Sirius 2014-12-31T20:41:41

        From my iPhone theodolite app (not very precise):
        Date & Time: Wed Dec 31 20:41:41 PST 2014
        Position: +037.40015* / -122.08219*
        Altitude: 56ft
        Azimuth/Bearing: 127* S53E 2258mils (True)
        Elevation Angle: +18.1*

        from http://www.convertalot.com/celestial_horizon_co-ordinates_calculator.html

        azimuth: 127.59
        altitude: 16.81

        from http://www.stargazing.net/mas/al_az.htm

        azimuth: 127* 24' 16"
        altitude: 16* 41' 31"

        """

        an_observer = coords.spherical(1, coords.latitude(37, 24), coords.angle(-122, 4, 57))

        a_datetime = coords.datetime('2014-12-31T20:41:41')

        sirius_hz = EquatorialHorizon.toHorizon(self.sirius, an_observer, a_datetime)

        self.assertEqual('17:54:28.6306', str(coords.angle(90) - sirius_hz.theta))
        self.assertEqual('128:52:13.836', str(sirius_hz.phi))

        sirius_eq = EquatorialHorizon.toEquatorial(sirius_hz, an_observer, a_datetime)

        self.assertSpacesAreEqual(self.sirius, sirius_eq)


    def test_sirius_2015_01_01T00_00_00(self):
        """Test RA/dec of Sirius 2015-01-01T00:00:00

        By happy coincidence, Sirius was on/near my local
        meridian, due south, at midnight new years eve when I measured
        it with my theodolite app at 8:41 pm above.
        """

        an_observer = coords.spherical(1, coords.latitude(37, 24), coords.angle(-122, 4, 57))

        a_datetime = coords.datetime('2015-01-01T00:00:00')

        sirius_hz = EquatorialHorizon.toHorizon(self.sirius, an_observer, a_datetime)

        self.assertEqual('35:52:34.9412', str(coords.angle(90) - sirius_hz.theta))
        self.assertEqual('178:52:5.91641', str(sirius_hz.phi))

        sirius_eq = EquatorialHorizon.toEquatorial(sirius_hz, an_observer, a_datetime)

        self.assertSpacesAreEqual(self.sirius, sirius_eq)


    def test_sirius_2015_01_01T06_00_00(self):
        """Test RA/dec of Sirius 2015-01-01T06:00:00"""

        an_observer = coords.spherical(1, coords.latitude(37, 24), coords.angle(-122, 4, 57))

        a_datetime = coords.datetime('2015-01-01T06:00:00')

        sirius_hz = EquatorialHorizon.toHorizon(self.sirius, an_observer, a_datetime)

        self.assertEqual('-9:30:43.9809', str(coords.angle(90) - sirius_hz.theta))
        self.assertEqual('256:10:20.4311', str(sirius_hz.phi))

        sirius_eq = EquatorialHorizon.toEquatorial(sirius_hz, an_observer, a_datetime)

        self.assertSpacesAreEqual(self.sirius, sirius_eq)



    def test_sirius_2015_01_01T12_00_00(self):
        """Test RA/dec of Sirius 2015-01-01T12:00:00"""


        an_observer = coords.spherical(1, coords.latitude(37, 24), coords.angle(-122, 4, 57))

        a_datetime = coords.datetime('2015-01-01T12:00:00')

        sirius_hz = EquatorialHorizon.toHorizon(self.sirius, an_observer, a_datetime)

        self.assertEqual('-69:18:43.4107', str(coords.angle(90) - sirius_hz.theta))
        self.assertEqual('358:44:25.2683', str(sirius_hz.phi))

        sirius_eq = EquatorialHorizon.toEquatorial(sirius_hz, an_observer, a_datetime)

        self.assertSpacesAreEqual(self.sirius, sirius_eq)


    def test_sirius_2015_01_01T21_00_00(self):
        """Test RA/dec of Sirius 2015-01-01T21:00:00"""

        an_observer = coords.spherical(1, coords.latitude(37, 24), coords.angle(-122, 4, 57))

        a_datetime = coords.datetime('2015-01-01T21:00:00')

        sirius_hz = EquatorialHorizon.toHorizon(self.sirius, an_observer, a_datetime)

        self.assertEqual('21:14:52.8586', str(coords.angle(90) - sirius_hz.theta))
        self.assertEqual('133:17:44.3899', str(sirius_hz.phi))

        sirius_eq = EquatorialHorizon.toEquatorial(sirius_hz, an_observer, a_datetime)

        self.assertSpacesAreEqual(self.sirius, sirius_eq)



    @unittest.skip('hacking')
    def test_sirius_hacking(self):
        """Test RA/dec of Sirius"""

        an_observer = coords.spherical(1, coords.latitude(37, 24), coords.angle(-122, 4, 57))

        a_datetime = coords.datetime('2015-01-01T00:00:00')

        sirius_hz = EquatorialHorizon.toHorizon(self.sirius, an_observer, a_datetime)

        print '\nsirius', sirius_hz



    @unittest.skip('hacking')
    def test_to_equatorial_hacking(self):
        """Test altitude azimuth to RA, dec."""

        an_object = coords.spherical(1, coords.angle(90) - coords.angle(35, 52, 34.9412),
                                     coords.angle(178, 52, 5.91641))

        an_observer = coords.spherical(1, coords.latitude(37, 24), coords.angle(-122, 4, 57))

        a_datetime = coords.datetime('2015-01-01T00:00:00')

        sirius_eq = EquatorialHorizon.toEquatorial(an_object, an_observer, a_datetime)

        print '\nsirius', sirius_eq



# TODO tests in the southern hemisphere


if __name__ == '__main__':
    unittest.main()
