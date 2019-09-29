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


    def assertSpacesAreEqual(self, lhs_space, rhs_space, places=12, delta=None):
        """Space assert helper method with limited places.

        default 12 works for most.
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
        self.assertAlmostEqual(15.12502164977829, venus_hz.theta.complement().degrees)

        # Meeus: 68.0337 measured from south
        self.assertAlmostEqual(68.0335491018803 + 180, venus_hz.phi.degrees)

        venus_eq = Transforms.EquatorialHorizon.toEquatorial(venus_hz, usno, a_datetime)

        self.assertAlmostEqual(-6.719891666666669, venus_eq.theta.complement().degrees)
        self.assertAlmostEqual(23.319337500000056, venus_eq.phi.RA, delta=1)

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

        self.assertEqual(16.813794241451888, sirius_hz.theta.complement().degrees)
        self.assertEqual(127.53668547673463, sirius_hz.phi.degrees)

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
        self.assertEqual(35.82372767190791, sirius_hz.theta.complement().degrees)

        # convertalot has 176.8388
        # http://www.stargazing.net has 159:29:35
        self.assertEqual(176.7983213260165, sirius_hz.phi.degrees)

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
        # this is 25:50:15.7818
        self.assertEqual(25.837717155453788, sirius_hz.theta.complement().degrees)

        # convertalot has 177.1526
        # http://www.stargazing.net has 161:20:22
        # this is 177:06:57.4295
        self.assertEqual(177.1159526380051, sirius_hz.phi.degrees)

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
        # this is 55:46:46.5697
        self.assertEqual(55.77960268086638, sirius_hz.theta.complement().degrees)

        # convertalot has 175.4386
        # http://www.stargazing.net has 151:48:55
        # this is 175:22:52.6989
        self.assertEqual(175.3813052419757, sirius_hz.phi.degrees)

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
        # this is 87:19:13.4142
        self.assertEqual(87.32039282432778, sirius_hz.theta.complement().degrees)

        # convertalot has 75.0877
        # http://www.stargazing.net has 90:49:36
        # this is 75:36:50.4176
        self.assertEqual(75.61400487954215, sirius_hz.phi.degrees)

        sirius_eq = Transforms.EquatorialHorizon.toEquatorial(sirius_hz, an_observer, a_datetime)

        self.assertSpacesAreEqual(self.sirius, sirius_eq, 12)

        return


    def test_sirius_2015_01_01T06_00_00(self):
        """Test RA/dec of Sirius 2015-01-01T06:00:00

        TODO: validate
        """

        a_datetime = coords.datetime('2015-01-01T06:00:00-08')

        sirius_hz = Transforms.EquatorialHorizon.toHorizon(self.sirius, self.mlc404, a_datetime)

        self.assertEqual(-8.163203278636573, sirius_hz.theta.complement().degrees)
        self.assertEqual(255.16133834965282, sirius_hz.phi.degrees)

        sirius_eq = Transforms.EquatorialHorizon.toEquatorial(sirius_hz, self.mlc404, a_datetime)

        self.assertSpacesAreEqual(self.sirius, sirius_eq)

        return


    def test_sirius_2015_01_01T12_00_00(self):
        """Test RA/dec of Sirius 2015-01-01T12:00:00

        TODO: validate
        """

        a_datetime = coords.datetime('2015-01-01T12:00:00-08')

        sirius_hz = Transforms.EquatorialHorizon.toHorizon(self.sirius, self.mlc404, a_datetime)

        self.assertEqual(-69.22390534164711, sirius_hz.theta.complement().degrees)
        self.assertEqual(354.00379188870545, sirius_hz.phi.degrees)

        sirius_eq = Transforms.EquatorialHorizon.toEquatorial(sirius_hz, self.mlc404, a_datetime)

        self.assertSpacesAreEqual(self.sirius, sirius_eq)

        return


    def test_sirius_2015_01_01T21_00_00(self):
        """Test RA/dec of Sirius 2015-01-01T21:00:00

        TODO: validate
        """

        a_datetime = coords.datetime('2015-01-01T21:00:00-08')

        sirius_hz = Transforms.EquatorialHorizon.toHorizon(self.sirius, self.mlc404, a_datetime)

        self.assertEqual(20.22283964580123, sirius_hz.theta.complement().degrees)
        self.assertEqual(131.8743636461398, sirius_hz.phi.degrees)

        sirius_eq = Transforms.EquatorialHorizon.toEquatorial(sirius_hz, self.mlc404, a_datetime)

        self.assertSpacesAreEqual(self.sirius, sirius_eq, places=12)

        return


    def test_sirius_2015_01_25T18_41_43(self):
        """Test RA/dec of Sirius 2015-01-25T18:41:43

        TODO: validate
        """

        a_datetime = coords.datetime('2015-01-25T18:41:43-08')

        sirius_hz = Transforms.EquatorialHorizon.toHorizon(self.sirius, self.mlc404, a_datetime)

        self.assertEqual(13.302334306322493, sirius_hz.theta.complement().degrees)
        self.assertEqual(123.56028959199841, sirius_hz.phi.degrees)

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

        self.assertEqual(32.4793615897622, rigel_hz.theta.complement().degrees)
        self.assertEqual(134.39183589599364, rigel_hz.phi.degrees)

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

        # starwalk has 7:14:07, this is 07:12:59.6683
        self.assertEqual(7.216574514195472, venus_hz.theta.complement().degrees)

        # starwalk has 246:42:18, this is 246:43:19.2959
        self.assertEqual(246.7220266352129, venus_hz.phi.degrees)

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

        # starwalk has 79:19:17, this is 79:17:43.1787
        self.assertEqual(79.29532740421266, castor_hz.theta.complement().degrees)

        # starwalk has 118:06:19, this is 117:40:45.2907
        self.assertAlmostEqual(117.67924742061244, castor_hz.phi.degrees)

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

        # starwalk has 37:45:56, this is 37:42:48.5173
        self.assertEqual(37.71347701529356, polaris_hz.theta.complement().degrees)

        # starwalk has 359:09:47, this is 359:09:36.8436
        self.assertEqual(359.16023434085207, polaris_hz.phi.degrees)

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

        # starwalk has -30:21:21, this is -30:20:20.4192
        self.assertEqual(-30.339005322141443, alpha_crucis_hz.theta.complement().degrees)

        # starwalk has 148:33:49, this is 148:33:52.6635
        self.assertEqual(148.56462874067802, alpha_crucis_hz.phi.degrees)

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
