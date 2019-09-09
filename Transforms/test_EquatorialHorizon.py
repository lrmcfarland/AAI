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

from __future__ import absolute_import # for python 2 and 3

import math
import time
import unittest

import coords

import Transforms.EquatorialHorizon
import Transforms.utils


class EquatorialHorizonTests(unittest.TestCase):
    """Test equatorial horizon transforms"""

    def setUp(self):
        """Set up test parameters."""

        self.mlc404 = coords.spherical(1, coords.latitude(37, 24), coords.angle(-122, 4, 57))

        self.sirius = Transforms.utils.radec2spherical(a_right_ascension=coords.angle(6, 45, 8.9173),
                                                       a_declination=coords.angle(-16, 42, 58.017))

        self.rigel = Transforms.utils.radec2spherical(a_right_ascension=coords.angle(5, 14, 32.27210),
                                                      a_declination=coords.angle(-8, 12, 5.8981))

        return


    def assertSpacesAreEqual(self, lhs_space, rhs_space, places=13, delta=None):
        """Space assert helper method with limited places.

        default 13 works for most.
        """
        if delta:
            self.assertAlmostEqual(lhs_space.r, rhs_space.r, delta=delta)
            self.assertAlmostEqual(lhs_space.theta.degrees, rhs_space.theta.degrees, delta=delta)
            self.assertAlmostEqual(lhs_space.phi.degrees, rhs_space.phi.degrees, delta=delta)

        else:
            self.assertAlmostEqual(lhs_space.r, rhs_space.r, places=places)
            self.assertAlmostEqual(lhs_space.theta.degrees, rhs_space.theta.degrees, places=places)
            self.assertAlmostEqual(lhs_space.phi.degrees, rhs_space.phi.degrees, places=places)

        return


    def test_meeus_13b(self):

        """Test Meeus example 13b"""

        usno = coords.spherical(1, coords.latitude(38, 55, 17), coords.angle(-77, 3, 56))
        venus = Transforms.utils.radec2spherical(coords.latitude(23, 9, 16.641), coords.angle(-6, 43, 11.61))
        a_datetime = coords.datetime('1987-04-10T19:21:00')

        venus_hz = Transforms.EquatorialHorizon.toHorizon(venus, usno, a_datetime)

        # Meeus: 15.1249
        self.assertAlmostEqual(15.12502164977829, Transforms.utils.get_latitude(venus_hz).degrees)

        # Meeus: 68.0337 measured from south
        self.assertAlmostEqual(68.0335491018803 + 180, Transforms.utils.get_longitude(venus_hz).degrees)

        venus_eq = Transforms.EquatorialHorizon.toEquatorial(venus_hz, usno, a_datetime)

        self.assertAlmostEqual(-6.719891666666669, Transforms.utils.get_declination(venus_eq).degrees)
        self.assertAlmostEqual(23.319337500000056, Transforms.utils.get_RA(venus_eq).degrees, delta=1)

        self.assertSpacesAreEqual(venus, venus_eq, places=5)

        return


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

        a_datetime = coords.datetime('2014-12-31T20:41:41-08')

        sirius_hz = Transforms.EquatorialHorizon.toHorizon(self.sirius, self.mlc404, a_datetime)

        self.assertEqual(16.39849173155956, Transforms.utils.get_latitude(sirius_hz).degrees)
        self.assertEqual(127.04325555303262, Transforms.utils.get_longitude(sirius_hz).degrees)

        sirius_eq = Transforms.EquatorialHorizon.toEquatorial(sirius_hz, self.mlc404, a_datetime)

        self.assertSpacesAreEqual(self.sirius, sirius_eq)

        return


    def test_sirius_2015_01_01T00_00_00_404mlc(self):
        """Test RA/dec of Sirius 2015-01-01T00:00:00

        By happy coincidence, Sirius was on/near my local
        meridian, due south, at midnight new years eve when I measured
        it with my theodolite app at 8:41 pm above.
        """

        # a_datetime = coords.datetime('2015-01-01T00:00:00') # TODO local time zone
        a_datetime = coords.datetime('2015-01-01T08:00:00') # TODO local time zone

        sirius_hz = Transforms.EquatorialHorizon.toHorizon(self.sirius, self.mlc404, a_datetime)


        # convertalot has 35.8414
        # http://www.stargazing.net has 33:29:59
        self.assertEqual(35.82372767190791, Transforms.utils.get_latitude(sirius_hz).degrees)

        # convertalot has 176.8388
        # http://www.stargazing.net has 159:29:35
        self.assertEqual(176.7983213260165, Transforms.utils.get_longitude(sirius_hz).degrees)

        sirius_eq = Transforms.EquatorialHorizon.toEquatorial(sirius_hz, self.mlc404, a_datetime)

        self.assertSpacesAreEqual(self.sirius, sirius_eq)

        return


    def test_sirius_2015_01_01T00_00_00_47N(self):
        """Test RA/dec of Sirius 2015-01-01T00:00:00

        Same as above but 47 degrees north latitude.
        """

        an_observer = coords.spherical(1, coords.latitude(47, 24), coords.angle(-122, 4, 57))
        a_datetime = coords.datetime('2015-01-01T00:00:00-08')

        sirius_hz = Transforms.EquatorialHorizon.toHorizon(self.sirius, an_observer, a_datetime)

        # convertalot has 25.8550
        # http://www.stargazing.net has 24:04:27
        self.assertEqual(25.81263044474126,  Transforms.utils.get_latitude(sirius_hz).degrees)

        # convertalot has 177.1526
        # http://www.stargazing.net has 161:20:22
        self.assertEqual(176.41734602707757, Transforms.utils.get_longitude(sirius_hz).degrees)

        sirius_eq = Transforms.EquatorialHorizon.toEquatorial(sirius_hz, an_observer, a_datetime)

        self.assertSpacesAreEqual(self.sirius, sirius_eq)

        return


    def test_sirius_2015_01_01T00_00_00_17N(self):
        """Test RA/dec of Sirius 2015-01-01T00:00:00

        Same as above but 17 degrees north latitude.
        """

        an_observer = coords.spherical(1, coords.latitude(17, 24), coords.angle(-122, 4, 57))
        a_datetime = coords.datetime('2015-01-01T00:00:00-08')

        sirius_hz = Transforms.EquatorialHorizon.toHorizon(self.sirius, an_observer, a_datetime)

        # convertalot has 55.7983
        # http://www.stargazing.net has 51:47:34
        self.assertEqual(55.72303697392837, Transforms.utils.get_latitude(sirius_hz).degrees)

        # convertalot has 175.4386
        # http://www.stargazing.net has 151:48:55
        self.assertEqual(174.26757064015055, Transforms.utils.get_longitude(sirius_hz).degrees)

        sirius_eq = Transforms.EquatorialHorizon.toEquatorial(sirius_hz, an_observer, a_datetime)

        self.assertSpacesAreEqual(self.sirius, sirius_eq, places=12)

        return


    def test_sirius_2015_01_01T00_00_00_17S(self):
        """Test RA/dec of Sirius 2015-01-01T00:00:00

        Same as above but 17 degrees south latitude.
        """

        an_observer = coords.spherical(1, coords.latitude(-17, 24), coords.angle(-122, 4, 57))
        a_datetime = coords.datetime('2015-01-01T00:00:00-08')

        sirius_hz = Transforms.EquatorialHorizon.toHorizon(self.sirius, an_observer, a_datetime)

        # convertalot has 87.3485
        # http://www.stargazing.net has 73:00:46
        self.assertEqual(86.7091165016879, Transforms.utils.get_latitude(sirius_hz).degrees)

        # convertalot has 75.0877
        # http://www.stargazing.net has 90:49:36
        self.assertEqual(78.50352226233457, Transforms.utils.get_longitude(sirius_hz).degrees)

        sirius_eq = Transforms.EquatorialHorizon.toEquatorial(sirius_hz, an_observer, a_datetime)

        self.assertSpacesAreEqual(self.sirius, sirius_eq, 12)

        return


    def test_sirius_2015_01_01T06_00_00(self):
        """Test RA/dec of Sirius 2015-01-01T06:00:00

        TODO: validate
        """

        a_datetime = coords.datetime('2015-01-01T06:00:00-08')

        sirius_hz = Transforms.EquatorialHorizon.toHorizon(self.sirius, self.mlc404, a_datetime)

        self.assertEqual(-7.659047114058083, Transforms.utils.get_latitude(sirius_hz).degrees)
        self.assertEqual(254.78103688257121, Transforms.utils.get_longitude(sirius_hz).degrees)

        sirius_eq = Transforms.EquatorialHorizon.toEquatorial(sirius_hz, self.mlc404, a_datetime)

        self.assertSpacesAreEqual(self.sirius, sirius_eq)

        return


    def test_sirius_2015_01_01T12_00_00(self):
        """Test RA/dec of Sirius 2015-01-01T12:00:00

        TODO: validate
        """

        a_datetime = coords.datetime('2015-01-01T12:00:00-08')

        sirius_hz = Transforms.EquatorialHorizon.toHorizon(self.sirius, self.mlc404, a_datetime)

        self.assertEqual(-69.16138963605425, Transforms.utils.get_latitude(sirius_hz).degrees)
        self.assertEqual(352.24085136954625, Transforms.utils.get_longitude(sirius_hz).degrees)

        sirius_eq = Transforms.EquatorialHorizon.toEquatorial(sirius_hz, self.mlc404, a_datetime)

        self.assertSpacesAreEqual(self.sirius, sirius_eq)

        return


    def test_sirius_2015_01_01T21_00_00(self):
        """Test RA/dec of Sirius 2015-01-01T21:00:00

        TODO: validate
        """

        a_datetime = coords.datetime('2015-01-01T21:00:00-08')

        sirius_hz = Transforms.EquatorialHorizon.toHorizon(self.sirius, self.mlc404, a_datetime)

        self.assertEqual(19.832549744165608, Transforms.utils.get_latitude(sirius_hz).degrees)
        self.assertEqual(131.34888940517624, Transforms.utils.get_longitude(sirius_hz).degrees)

        sirius_eq = Transforms.EquatorialHorizon.toEquatorial(sirius_hz, self.mlc404, a_datetime)

        self.assertSpacesAreEqual(self.sirius, sirius_eq, places=12)

        return


    def test_sirius_2015_01_25T18_41_43(self):
        """Test RA/dec of Sirius 2015-01-25T18:41:43

        TODO: validate
        """

        a_datetime = coords.datetime('2015-01-25T18:41:43-08')

        sirius_hz = Transforms.EquatorialHorizon.toHorizon(self.sirius, self.mlc404, a_datetime)

        self.assertEqual(12.866172856786932, Transforms.utils.get_latitude(sirius_hz).degrees)
        self.assertEqual(123.09452281510741, Transforms.utils.get_longitude(sirius_hz).degrees)

        sirius_eq = Transforms.EquatorialHorizon.toEquatorial(sirius_hz, self.mlc404, a_datetime)

        self.assertSpacesAreEqual(self.sirius, sirius_eq, places=12)

        return


    def test_rigel_2015_01_25T10_32_29(self):
        """Test RA/dec of Rigel 2015-01-25T18:32:29

        TODO: elivation relative to sirius, 15, is twice expected
        difference in declination of 8. RA also a couple of degrees
        different. Expect 15 get 12.

        """

        a_datetime = coords.datetime('2015-01-25T18:32:29-08')

        rigel_hz = Transforms.EquatorialHorizon.toHorizon(self.rigel, self.mlc404, a_datetime)

        self.assertEqual(32.104349976543396, Transforms.utils.get_latitude(rigel_hz).degrees)
        self.assertEqual(133.76324019981976, Transforms.utils.get_longitude(rigel_hz).degrees)

        rigel_eq = Transforms.EquatorialHorizon.toEquatorial(rigel_hz, self.mlc404, a_datetime)

        self.assertSpacesAreEqual(self.rigel, rigel_eq, places=12)

        return


    def test_venus_2015_01_25T18_30_starwalk(self):
        """Test RA/dec of Venus 2015-01-25T18:30

        Azimuth, altitude from star walk
        """

        a_datetime = coords.datetime('2015-01-25T18:30:00-08')

        venus = Transforms.utils.radec2spherical(a_right_ascension=coords.angle(22, 3, 21),
                                                 a_declination=coords.angle(-13, 36, 4))

        venus_hz = Transforms.EquatorialHorizon.toHorizon(venus, self.mlc404, a_datetime)

        # starwalk has 7:14:07, this is 07:41:43.1496
        self.assertEqual(7.695319341649835,  Transforms.utils.get_latitude(venus_hz).degrees)

        # starwalk has 246:42:18, this is 246:17:44.4737
        self.assertEqual(246.2956871304181, Transforms.utils.get_longitude(venus_hz).degrees)

        venus_eq = Transforms.EquatorialHorizon.toEquatorial(venus_hz, self.mlc404, a_datetime)

        self.assertSpacesAreEqual(venus, venus_eq)

        return


    def test_castor_2015_03_06T20_00_starwalk(self):
        """Test RA/dec of Castor 2015-03-06T20:00

        http://en.wikipedia.org/wiki/Castor_(star)

        something above the ecliptic

        RA, DEC, Azimuth, altitude from star walk
        """

        a_datetime = coords.datetime('2015-03-06T20:00:00-08:00')

        castor = Transforms.utils.radec2spherical(a_right_ascension=coords.angle(7, 34, 36),
                                                  a_declination=coords.angle(31, 53, 17))

        castor_hz = Transforms.EquatorialHorizon.toHorizon(castor, self.mlc404, a_datetime)

        # starwalk has 79:19:17, this is 78:49:46.7591
        self.assertEqual(78.82965531052908, Transforms.utils.get_latitude(castor_hz).degrees)

        # starwalk has 118:06:19, this is 116:03:33.4654
        self.assertAlmostEqual(116.05929595036575, Transforms.utils.get_longitude(castor_hz).degrees)

        castor_eq = Transforms.EquatorialHorizon.toEquatorial(castor_hz, self.mlc404, a_datetime)

        self.assertSpacesAreEqual(castor, castor_eq)

        return


    def test_polaris_2015_03_06T20_00_starwalk(self):
        """Test RA/dec of Polaris 2015-03-06T20:00

        http://en.wikipedia.org/wiki/Polaris

        something above the ecliptic

        RA, DEC, Azimuth, altitude from star walk

        """

        a_datetime = coords.datetime('2015-03-06T20:00:00-08')

        polaris = Transforms.utils.radec2spherical(a_right_ascension=coords.angle(2, 31, 48),
                                                   a_declination=coords.angle(89, 15, 51))

        polaris_hz = Transforms.EquatorialHorizon.toHorizon(polaris, self.mlc404, a_datetime)

        # starwalk has 37:45:56, this is 37:43:15.9847
        self.assertEqual(37.72110687177799, Transforms.utils.get_latitude(polaris_hz).degrees)

        # starwalk has 359:09:47, this is 359:09:53.2487
        self.assertEqual(359.16479129492996, Transforms.utils.get_longitude(polaris_hz).degrees)

        polaris_eq = Transforms.EquatorialHorizon.toEquatorial(polaris_hz, self.mlc404, a_datetime)

        self.assertSpacesAreEqual(polaris, polaris_eq, places=11)

        return


    def test_alpha_crucis_2015_03_06T20_00_starwalk(self):
        """Test RA/dec of Alpha_Crucis 2015-03-06T20:00

        http://en.wikipedia.org/wiki/Alpha_Crucis

        something very below the ecliptic

        RA, DEC, Azimuth, altitude from star walk

        """

        a_datetime = coords.datetime('2015-03-06T20:00:00-08')

        alpha_crucis = Transforms.utils.radec2spherical(a_right_ascension=coords.angle(12, 26, 35),
                                                        a_declination=coords.angle(-63, 5, 55))

        alpha_crucis_hz = Transforms.EquatorialHorizon.toHorizon(alpha_crucis, self.mlc404, a_datetime)

        # starwalk has -30, 21, 21, this is -30:36:42.4172
        self.assertEqual(-30.611782558848248, Transforms.utils.get_latitude(alpha_crucis_hz).degrees)

        # starwalk has 148:33:49, this is 148:25:38.7502
        self.assertEqual(148.4274306016521, Transforms.utils.get_longitude(alpha_crucis_hz).degrees)

        alpha_crucis_eq = Transforms.EquatorialHorizon.toEquatorial(alpha_crucis_hz, self.mlc404, a_datetime)

        self.assertSpacesAreEqual(alpha_crucis, alpha_crucis_eq)

        return


    @unittest.skip('hacking')
    def test_sirius_hacking(self):
        """Test RA/dec of Sirius"""

        a_datetime = coords.datetime('2015-01-01T00:00:00')

        sirius_hz = Transforms.EquatorialHorizon.toHorizon(self.sirius, self.mlc404, a_datetime)

        print('\nsirius', sirius_hz)

        return

    @unittest.skip('hacking')
    def test_to_equatorial_hacking(self):
        """Test altitude azimuth to RA, dec."""

        an_object = coords.spherical(1, coords.angle(90) - coords.angle(35, 52, 34.9412),
                                     coords.angle(178, 52, 5.91641))

        a_datetime = coords.datetime('2015-01-01T00:00:00')

        sirius_eq = Transforms.EquatorialHorizon.toEquatorial(an_object, self.mlc404, a_datetime)

        print('\nsirius', sirius_eq)

        return


# TODO tests in the southern hemisphere


if __name__ == '__main__':
    unittest.main()
