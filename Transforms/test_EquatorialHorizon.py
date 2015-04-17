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

        self.mlc404 = coords.spherical(1, coords.latitude(37, 24), coords.angle(-122, 4, 57))

        self.sirius = utils.radec2spherical(a_right_ascension=coords.angle(6, 45, 8.9173),
                                            a_declination=coords.angle(-16, 42, 58.017))

        self.rigel = utils.radec2spherical(a_right_ascension=coords.angle(5, 14, 32.27210),
                                           a_declination=coords.angle(-8, 12, 5.8981))


    def assertSpacesAreEqual(self, lhs_space, rhs_space, places=13):
        """Space assert helper method with limited places.

        default 13 works for most.
        """
        self.assertAlmostEqual(lhs_space.r, rhs_space.r, places)
        self.assertAlmostEqual(lhs_space.theta.value, rhs_space.theta.value, places)
        self.assertAlmostEqual(lhs_space.phi.value, rhs_space.phi.value, places)


    def test_meeus_13b(self):

        """Test Meeus example 13b"""

        usno = coords.spherical(1, coords.latitude(38, 55, 17), coords.angle(-77, 03, 56))
        venus = utils.radec2spherical(coords.latitude(23, 9, 16.641), coords.angle(-6, 43, 11.61))
        a_datetime = coords.datetime('1987-04-10T19:21:00')

        venus_hz = EquatorialHorizon.toHorizon(venus, usno, a_datetime, is_azimuth_south=True)

        # Meeus: 15.1249
        self.assertAlmostEqual(15.12502164977829, utils.get_latitude(venus_hz).value)

        # Meeus: 68.0337
        self.assertAlmostEqual(68.0335491018803, utils.get_longitude(venus_hz).value)

        venus_eq = EquatorialHorizon.toEquatorial(venus_hz, usno, a_datetime, is_azimuth_south=True)

        self.assertAlmostEqual(-6.719891666666669, utils.get_latitude(venus_eq).value)
        self.assertAlmostEqual(22.971575990261428, utils.get_longitude(venus_eq).value/15)


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

        a_datetime = coords.datetime('2014-12-31T20:41:41')

        sirius_hz = EquatorialHorizon.toHorizon(self.sirius, self.mlc404, a_datetime, is_azimuth_south=False)

        self.assertEqual(17.908724266152447, utils.get_latitude(sirius_hz).value)
        self.assertEqual(128.87146834940916, utils.get_longitude(sirius_hz).value)

        sirius_eq = EquatorialHorizon.toEquatorial(sirius_hz, self.mlc404, a_datetime)

        self.assertSpacesAreEqual(self.sirius, sirius_eq)


    def test_sirius_2015_01_01T00_00_00_404mlc(self):
        """Test RA/dec of Sirius 2015-01-01T00:00:00

        By happy coincidence, Sirius was on/near my local
        meridian, due south, at midnight new years eve when I measured
        it with my theodolite app at 8:41 pm above.
        """

        a_datetime = coords.datetime('2015-01-01T00:00:00')

        sirius_hz = EquatorialHorizon.toHorizon(self.sirius, self.mlc404, a_datetime, is_azimuth_south=False)


        # convertalot has 35.8414
        # http://www.stargazing.net has 33:29:59
        self.assertEqual(35.876392134760174, utils.get_latitude(sirius_hz).value)

        # convertalot has 176.8388
        # http://www.stargazing.net has 159:29:35
        self.assertEqual(178.86978502523434, utils.get_longitude(sirius_hz).value)

        sirius_eq = EquatorialHorizon.toEquatorial(sirius_hz, self.mlc404, a_datetime)

        self.assertSpacesAreEqual(self.sirius, sirius_eq)



    @unittest.skip('pending')
    def test_sirius_2015_01_01T00_00_00_47N(self):
        """Test RA/dec of Sirius 2015-01-01T00:00:00

        Same as above but 47 degrees north latitude.
        """

        a_datetime = coords.datetime('2015-01-01T00:00:00')

        sirius_hz = EquatorialHorizon.toHorizon(self.sirius, self.mlc404, a_datetime, is_azimuth_south=False)

        # convertalot has 25.8550
        # http://www.stargazing.net has 24:04:27
        self.assertEqual('25:52:41.2872', str(coords.angle(90) - sirius_hz.theta))

        # convertalot has 177.1526
        # http://www.stargazing.net has 161:20:22
        self.assertEqual('178:58:55.7461', str(sirius_hz.phi))

        sirius_eq = EquatorialHorizon.toEquatorial(sirius_hz, self.mlc404, a_datetime)

        self.assertSpacesAreEqual(self.sirius, sirius_eq)



    @unittest.skip('pending')
    def test_sirius_2015_01_01T00_00_00_17N(self):
        """Test RA/dec of Sirius 2015-01-01T00:00:00

        Same as above but 17 degrees north latitude.
        """

        a_datetime = coords.datetime('2015-01-01T00:00:00')

        sirius_hz = EquatorialHorizon.toHorizon(self.sirius, self.mlc404, a_datetime, is_azimuth_south=False)

        # convertalot has 55.7983
        # http://www.stargazing.net has 51:47:34
        self.assertEqual(55.87088576168508, utils.get_latitude(sirius_hz).value)

        # convertalot has 175.4386
        # http://www.stargazing.net has 151:48:55
        self.assertEqual(178.36762701282893, utils.get_longitude(sirius_hz).value)

        sirius_eq = EquatorialHorizon.toEquatorial(sirius_hz, self.mlc404, a_datetime)

        self.assertSpacesAreEqual(self.sirius, sirius_eq)


    @unittest.skip('azimuth more than 10 degrees out')
    def test_sirius_2015_01_01T00_00_00_17S(self):
        """Test RA/dec of Sirius 2015-01-01T00:00:00

        Same as above but 17 degrees south latitude.
        """

        a_datetime = coords.datetime('2015-01-01T00:00:00')

        sirius_hz = EquatorialHorizon.toHorizon(self.sirius, self.mlc404, a_datetime, is_azimuth_south=False)

        # convertalot has 87.3485
        # http://www.stargazing.net has 73:00:46
        self.assertEqual('88:51:26.7255', str(coords.angle(90) - sirius_hz.theta))

        # convertalot has 75.0877 TODO way out!
        # http://www.stargazing.net has 90:49:36
        self.assertEqual('53:22:32.3603', str(sirius_hz.phi))

        sirius_eq = EquatorialHorizon.toEquatorial(sirius_hz, self.mlc404, a_datetime)

        self.assertSpacesAreEqual(self.sirius, sirius_eq, 12)



    @unittest.skip('pending')
    def test_sirius_2015_01_01T06_00_00(self):
        """Test RA/dec of Sirius 2015-01-01T06:00:00"""

        a_datetime = coords.datetime('2015-01-01T06:00:00')

        sirius_hz = EquatorialHorizon.toHorizon(self.sirius, self.mlc404, a_datetime, is_azimuth_south=False)

        self.assertEqual('-9:30:47.4513', str(coords.angle(90) - sirius_hz.theta))
        self.assertEqual('256:10:23.0204', str(sirius_hz.phi))

        sirius_eq = EquatorialHorizon.toEquatorial(sirius_hz, self.mlc404, a_datetime)

        self.assertSpacesAreEqual(self.sirius, sirius_eq)


    @unittest.skip('pending')
    def test_sirius_2015_01_01T12_00_00(self):
        """Test RA/dec of Sirius 2015-01-01T12:00:00"""


        a_datetime = coords.datetime('2015-01-01T12:00:00')

        sirius_hz = EquatorialHorizon.toHorizon(self.sirius, self.mlc404, a_datetime, is_azimuth_south=False)

        self.assertEqual('-69:18:43.4892', str(coords.angle(90) - sirius_hz.theta))
        self.assertEqual('358:44:37.4789', str(sirius_hz.phi))

        sirius_eq = EquatorialHorizon.toEquatorial(sirius_hz, self.mlc404, a_datetime)

        self.assertSpacesAreEqual(self.sirius, sirius_eq)


    @unittest.skip('pending')
    def test_sirius_2015_01_01T21_00_00(self):
        """Test RA/dec of Sirius 2015-01-01T21:00:00"""

        a_datetime = coords.datetime('2015-01-01T21:00:00')

        sirius_hz = EquatorialHorizon.toHorizon(self.sirius, self.mlc404, a_datetime, is_azimuth_south=False)

        self.assertEqual('21:14:55.4684', str(coords.angle(90) - sirius_hz.theta))
        self.assertEqual('133:17:48.0876', str(sirius_hz.phi))

        sirius_eq = EquatorialHorizon.toEquatorial(sirius_hz, self.mlc404, a_datetime)

        self.assertSpacesAreEqual(self.sirius, sirius_eq)


    @unittest.skip('pending')
    def test_sirius_2015_01_25T18_41_43(self):
        """Test RA/dec of Sirius 2015-01-25T18:41:43"""

        a_datetime = coords.datetime('2015-01-25T18:41:43')

        sirius_hz = EquatorialHorizon.toHorizon(self.sirius, self.mlc404, a_datetime, is_azimuth_south=False)

        self.assertEqual('14:27:17.6489', str(coords.angle(90) - sirius_hz.theta))
        self.assertEqual('124:49:8.81085', str(sirius_hz.phi))

        sirius_eq = EquatorialHorizon.toEquatorial(sirius_hz, self.mlc404, a_datetime)

        self.assertSpacesAreEqual(self.sirius, sirius_eq)


    @unittest.skip('pending')
    def test_rigel_2015_01_25T10_32_29(self):
        """Test RA/dec of Rigel 2015-01-25T18:32:29

        TODO: elivation relative to sirius, 15, is twice expected
        difference in declination of 8. RA also a couple of degrees
        different. Expect 15 get 12.

        """

        a_datetime = coords.datetime('2015-01-25T18:32:29')

        rigel_hz = EquatorialHorizon.toHorizon(self.rigel, self.mlc404, a_datetime, is_azimuth_south=False)

        self.assertEqual('33:27:37.4937', str(coords.angle(90) - rigel_hz.theta))
        self.assertEqual('136:05:56.5843', str(rigel_hz.phi))

        rigel_eq = EquatorialHorizon.toEquatorial(rigel_hz, self.mlc404, a_datetime)

        self.assertSpacesAreEqual(self.rigel, rigel_eq)


    @unittest.skip('pending')
    def test_venus_2015_01_25T18_30_starwalk(self):
        """Test RA/dec of Venus 2015-01-25T18:30

        Azimuth, altitude from star walk

        """

        a_datetime = coords.datetime('2015-01-25T18:30:00')

        venus = utils.radec2spherical(a_right_ascension=coords.angle(22, 03, 21),
                                      a_declination=coords.angle(-13, 36, 04))

        venus_hz = EquatorialHorizon.toHorizon(venus, self.mlc404, a_datetime, is_azimuth_south=False)

        # starwalk has 7:14:07
        self.assertEqual('05:55:52.6292', str(coords.angle(90) - venus_hz.theta))

        # starwalk has 246:42:18
        self.assertEqual('247:50:57.8137', str(venus_hz.phi))

        venus_eq = EquatorialHorizon.toEquatorial(venus_hz, self.mlc404, a_datetime)

        self.assertSpacesAreEqual(venus, venus_eq)


    @unittest.skip('pending')
    def test_castor_2015_03_06T20_00_starwalk(self):
        """Test RA/dec of Castor 2015-03-06T20:00

        http://en.wikipedia.org/wiki/Castor_(star)

        something above the ecliptic

        RA, DEC, Azimuth, altitude from star walk

        """

        a_datetime = coords.datetime('2015-03-06T20:00:00')

        castor = utils.radec2spherical(a_right_ascension=coords.angle(07, 34, 36),
                                       a_declination=coords.angle(31, 53, 17))

        castor_hz = EquatorialHorizon.toHorizon(castor, self.mlc404, a_datetime, is_azimuth_south=False)

        # starwalk has 79:19:17
        self.assertEqual('80:30:1.99978', str(coords.angle(90) - castor_hz.theta))

        # starwalk has 118:06:19
        self.assertEqual('122:40:36.8317', str(castor_hz.phi))

        castor_eq = EquatorialHorizon.toEquatorial(castor_hz, self.mlc404, a_datetime)

        self.assertSpacesAreEqual(castor, castor_eq)



    @unittest.skip('pending')
    def test_polaris_2015_03_06T20_00_starwalk(self):
        """Test RA/dec of Polaris 2015-03-06T20:00

        http://en.wikipedia.org/wiki/Polaris

        something above the ecliptic

        RA, DEC, Azimuth, altitude from star walk

        """

        a_datetime = coords.datetime('2015-03-06T20:00:00')

        polaris = utils.radec2spherical(a_right_ascension=coords.angle(02, 31, 48),
                                        a_declination=coords.angle(89, 15, 51))

        polaris_hz = EquatorialHorizon.toHorizon(polaris, self.mlc404, a_datetime, is_azimuth_south=False)

        # starwalk has 37:45:56
        self.assertEqual('37:41:34.486', str(coords.angle(90) - polaris_hz.theta))

        # starwalk has 359:09:47
        self.assertEqual('359:08:55.0309', str(polaris_hz.phi))

        polaris_eq = EquatorialHorizon.toEquatorial(polaris_hz, self.mlc404, a_datetime)

        self.assertSpacesAreEqual(polaris, polaris_eq, 11)


    @unittest.skip('pending')
    def test_alpha_crucis_2015_03_06T20_00_starwalk(self):
        """Test RA/dec of Alpha_Crucis 2015-03-06T20:00

        http://en.wikipedia.org/wiki/Alpha_Crucis

        something very below the ecliptic

        RA, DEC, Azimuth, altitude from star walk

        """

        a_datetime = coords.datetime('2015-03-06T20:00:00')

        alpha_crucis = utils.radec2spherical(a_right_ascension=coords.angle(12, 26, 35),
                                             a_declination=coords.angle(-63, 05, 55))

        alpha_crucis_hz = EquatorialHorizon.toHorizon(alpha_crucis, self.mlc404, a_datetime, is_azimuth_south=False)

        # starwalk has -30, 21, 21
        self.assertEqual('-29:36:58.3633', str(coords.angle(90) - alpha_crucis_hz.theta))

        # starwalk has 148:33:49
        self.assertEqual('148:56:34.1279', str(alpha_crucis_hz.phi))

        alpha_crucis_eq = EquatorialHorizon.toEquatorial(alpha_crucis_hz, self.mlc404, a_datetime)

        self.assertSpacesAreEqual(alpha_crucis, alpha_crucis_eq)



    @unittest.skip('hacking')
    def test_sirius_hacking(self):
        """Test RA/dec of Sirius"""

        a_datetime = coords.datetime('2015-01-01T00:00:00')

        sirius_hz = EquatorialHorizon.toHorizon(self.sirius, self.mlc404, a_datetime, is_azimuth_south=False)

        print '\nsirius', sirius_hz



    @unittest.skip('hacking')
    def test_to_equatorial_hacking(self):
        """Test altitude azimuth to RA, dec."""

        an_object = coords.spherical(1, coords.angle(90) - coords.angle(35, 52, 34.9412),
                                     coords.angle(178, 52, 5.91641))

        a_datetime = coords.datetime('2015-01-01T00:00:00')

        sirius_eq = EquatorialHorizon.toEquatorial(an_object, self.mlc404, a_datetime)

        print '\nsirius', sirius_eq



# TODO tests in the southern hemisphere


if __name__ == '__main__':
    unittest.main()
