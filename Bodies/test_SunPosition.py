"""Unit tests for Sun Position calculations

to run:  ./pylaunch.sh test_SunPosition.py
verbose: ./pylaunch.sh test_SunPosition.py -v
filter:  ./pylaunch.sh test_SunPosition.py -v RiseAndSetTests.test_Meeus_15a
debug:   ./pylaunch.sh -m pdb test_SunPosition.py

next until import module:

(Pdb) n
> /Users/lrm/src/Astronomy/Transforms/test_SunPosition.py(25)<module>()
-> import SunPosition
(Pdb) b SunPosition.SunPosition.EquationOfTime
Breakpoint 1 at /Users/lrm/src/Astronomy/Transforms/SunPosition.py:17
"""

import math
import time
import unittest

import coords
import SunPosition

import Transforms.utils


class SunPositionsTests(unittest.TestCase):
    """Test Sun Position calculations"""

    def setUp(self):
        """Set up test parameters."""

        self.places = 12

        self.mlc404 = Transforms.utils.latlon2spherical(a_latitude=coords.angle(37, 24),
                                                        a_longitude=coords.angle(-122, 4, 56))

        return


    def test_sextant_2015_03_27(self):
        """Test against sextant measurement

        The sun angle is measured with a sextant using a swimming pool
        as an artificial horizon.

        A light wind blurred the reflected image, sextant calibration rough

        Sextant reading 70:10/2 = 35:05         (35.0833333333) degrees altitude
        SunPosition             = 34:14:17.1205 (34.2380890297) degrees altitude
        APC mini sun            = 71:24:47.9738 (71.41332606)   degrees altitude TODO way out!

        Star Walk               = 34:18:36 degrees altitude, 243:18:47 degrees azimuth
        TODO taken from 37:27N, -122:11 adjust, to 404 MLC


        Note: PDT

        TODO improve precision, but problem largely in sextant user
        """

        a_datetime = coords.datetime('2015-03-27T16:24:00-07')

        sun = SunPosition.SunPosition(self.mlc404, a_datetime)

        self.assertAlmostEqual(243.07115892922118, Transforms.utils.get_azimuth(sun).value, self.places)

        sextant_alt = coords.angle(Transforms.utils.parse_angle_arg('70:10').value/2)
        self.assertAlmostEqual(sextant_alt.value, Transforms.utils.get_altitude(sun).value, delta=1)

        return


    def test_sextant_2015_04_20(self):
        """Test against sextant measurement

        The sun angle is measured with a sextant using a swimming pool
        as an artificial horizon.

        A light wind blurred the reflected image

        Sextant reading 44:32/2 = 22:15:60      (22.2666666667) degrees altitude
        SunPosition             = 21:51:14.4322 (21.8540089561) degrees altitude
        APC mini sun            = 70:57:2.90548 (70.9508070789) degrees altitude TODO way out!

        Star Walk               = 22:22:12 degrees altitude, 267:44:43 degrees azimuth
        TODO taken from 37:27N, -122:11 adjust, to 404 MLC

        Note: PDT
        """

        a_datetime = coords.datetime('2015-04-20T17:52:00-07')

        sun = SunPosition.SunPosition(self.mlc404, a_datetime)

        self.assertAlmostEqual(267.90829781482097, Transforms.utils.get_azimuth(sun).value, self.places)

        sextant_alt = coords.angle(Transforms.utils.parse_angle_arg('44:32').value/2)
        self.assertAlmostEqual(sextant_alt.value, Transforms.utils.get_altitude(sun).value, delta=1)

        return


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

        sun = SunPosition.SunPosition(self.mlc404, a_datetime)

        self.assertAlmostEqual(95.95981144985676, Transforms.utils.get_azimuth(sun).value, self.places)

        sextant_alt = coords.angle(Transforms.utils.parse_angle_arg('66:46').value/2)
        self.assertAlmostEqual(sextant_alt.value, Transforms.utils.get_altitude(sun).value, delta=2)

        return


class EquationOfTimeTests(unittest.TestCase):
    """Test Equatoin of Time calculations"""

    def setUp(self):
        """Set up test parameters."""

        self.places = 12

        return


    def test_2015_01_01T12_00(self):
        """Test Equation of time 2015-01-01T12:00:00

        validate with http://www.esrl.noaa.gov/gmd/grad/solcalc/
        """

        a_datetime = coords.datetime('2015-01-02T12:00:00')
        eot = SunPosition.EquationOfTime(a_datetime)

        # NOAA says -3.59 minutes
        self.assertAlmostEqual(-3.901196866415546, eot.value*60, self.places)

        return


    def test_2015_02_11T12_00(self):
        """Test Equation of time 2015-02-11T12:00:00

        first local minimum of the year

        validate with http://www.esrl.noaa.gov/gmd/grad/solcalc/
        """

        a_datetime = coords.datetime(2015, 02, 11, 12)
        eot = SunPosition.EquationOfTime(a_datetime)

        # NOAA says -14.24 minutes
        self.assertAlmostEqual(-14.212711856485711, eot.value*60, self.places)

        return


    def test_2015_03_20T12_00(self):
        """Test Equation of time 2015-03-20T12:00:00

        validate with http://www.esrl.noaa.gov/gmd/grad/solcalc/
        """

        a_datetime = coords.datetime(2015, 03, 20, 12)
        eot = SunPosition.EquationOfTime(a_datetime)

        # NOAA says -7.44 minutes
        self.assertAlmostEqual(-7.563513810377245, eot.value*60, self.places)

        return


    def test_2015_05_14T12_00(self):
        """Test Equation of time 2015-05-14T12:00:00

        first local maximum of the year

        validate with http://www.esrl.noaa.gov/gmd/grad/solcalc/
        """

        a_datetime = coords.datetime(2015, 05, 14, 12)
        eot = SunPosition.EquationOfTime(a_datetime)

        # NOAA says 3.65 minutes
        self.assertAlmostEqual(3.6588472510257475, eot.value*60, self.places)

        return


    def test_2015_07_26T12_00(self):
        """Test Equation of time 2015-07-26T12:00:00

        second local minimum of the year

        validate with http://www.esrl.noaa.gov/gmd/grad/solcalc/
        """

        a_datetime = coords.datetime(2015, 07, 26, 12)
        eot = SunPosition.EquationOfTime(a_datetime)

        # NOAA says -6.54 minutes
        self.assertAlmostEqual(-6.5354183954768175, eot.value*60, self.places)

        return


    def test_2015_11_03T12_00(self):
        """Test Equation of time 2015-11-03T12:00:00

        second local maximum of the year

        validate with http://www.esrl.noaa.gov/gmd/grad/solcalc/
        """

        a_datetime = coords.datetime(2015, 11, 03, 12)
        eot = SunPosition.EquationOfTime(a_datetime)

        # NOAA says 16.48 minutes
        self.assertAlmostEqual(16.43786410739647, eot.value*60, self.places)

        return


class RiseAndSetTests(unittest.TestCase):
    """Test rise and set calculations"""

    def setUp(self):
        """Set up test parameters."""

        self.places = 12

        return


    def test_Meeus_15a(self):
        """Tests with Meeus 15.a data

        TODO this is also showing datetime rounding error, setting a
        day later, with out the hack described in
        SunPosition.RiseAndSet

        """

        a_datetime = coords.datetime('1988-03-20T00:00:00')

        boston = Transforms.utils.latlon2spherical(a_latitude = coords.angle(42.3333),
                                                   a_longitude = coords.angle(-71.0833))

        venus = Transforms.utils.radec2spherical(coords.angle(41.73129/15), coords.angle(18.44092))


        rising, transit, setting = SunPosition.RiseAndSet(venus, boston, a_datetime, coords.angle(-0.5667))

        self.assertEqual('1988-03-20T12:26:9.28415', str(rising))
        self.assertEqual('1988-03-20T19:40:17.533', str(transit))
        self.assertEqual('1988-03-20T02:54:25.782', str(setting))

        return


    def test_polaris_1(self):
        """Tests circumpolar exception to high"""

        polaris = Transforms.utils.radec2spherical(coords.angle(2, 31, 49.09), coords.angle(89, 15, 50.8))

        mlc404 = Transforms.utils.latlon2spherical(a_latitude=coords.angle(37, 24),
                                                   a_longitude=coords.angle(-122, 4, 56))

        a_datetime = coords.datetime('2015-05-25T00:00:00-07')

        self.assertRaises(SunPosition.Error, SunPosition.RiseAndSet, polaris, mlc404, a_datetime, coords.angle(-0.5667))

        return


    def test_polaris_2(self):
        """Tests circumpolar exception to low"""

        antipolaris = Transforms.utils.radec2spherical(coords.angle(2, 31, 49.09), coords.angle(-89, 15, 50.8))

        mlc404 = Transforms.utils.latlon2spherical(a_latitude=coords.angle(37, 24),
                                                   a_longitude=coords.angle(-122, 4, 56))

        a_datetime = coords.datetime('2015-05-25T00:00:00-07')

        self.assertRaises(SunPosition.Error, SunPosition.RiseAndSet, antipolaris, mlc404, a_datetime, coords.angle(-0.5667))

        return


class SunRiseAndSetTests(unittest.TestCase):
    """Test sunrise and set calculations"""

    def setUp(self):
        """Set up test parameters."""

        self.places = 12

        self.mlc404 = Transforms.utils.latlon2spherical(a_latitude=coords.angle(37, 24),
                                                        a_longitude=coords.angle(-122, 4, 56))

        self.antimlc404 = Transforms.utils.latlon2spherical(a_latitude=coords.angle(37, 24),
                                                            a_longitude=coords.angle(122, 4, 56))
        return


    def test_timezone_p1(self):
        """Tests timezone +1"""

        an_observer = Transforms.utils.latlon2spherical(a_latitude = coords.angle(45),
                                                        a_longitude = coords.angle(15))

        a_datetime = coords.datetime('2015-05-22T12:00:00+01')

        rising, transit, setting = SunPosition.SunRiseAndSet(an_observer, a_datetime)

        self.assertEqual('2015-05-22T04:26:4.97515+01', str(rising))  # NOAA 04:24
        self.assertEqual('2015-05-22T11:58:46.9625+01', str(transit)) # NOAA 11:56:39
        self.assertEqual('2015-05-22T19:31:28.9499+01', str(setting)) # NOAA 19:30

        return


    def test_timezone_n1(self):
        """Tests timezone -1"""

        an_observer = Transforms.utils.latlon2spherical(a_latitude = coords.angle(45),
                                                        a_longitude = coords.angle(-15))

        a_datetime = coords.datetime('2015-05-22T12:00:00-01')

        rising, transit, setting = SunPosition.SunRiseAndSet(an_observer, a_datetime)

        self.assertEqual('2015-05-22T04:25:49.8102-01', str(rising))  # NOAA 04:24
        self.assertEqual('2015-05-22T11:58:26.8797-01', str(transit)) # NOAA 11:56:39
        self.assertEqual('2015-05-22T19:31:3.94921-01', str(setting)) # NOAA 19:30

        return


    def test_timezone_p6(self):
        """Tests timezone +6

        TODO this is also showing datetime rounding error, rising a
        day later, with out the hack described in
        SunPosition.RiseAndSet

        """

        an_observer = Transforms.utils.latlon2spherical(a_latitude = coords.angle(45),
                                                        a_longitude = coords.angle(90))

        a_datetime = coords.datetime('2015-05-22T12:00:00+06')

        rising, transit, setting = SunPosition.SunRiseAndSet(an_observer, a_datetime)

        self.assertEqual('2015-05-22T04:26:42.9486+06', str(rising))  # NOAA 04:25
        self.assertEqual('2015-05-22T11:59:37.1856+06', str(transit)) # NOAA 11:56:38
        self.assertEqual('2015-05-22T19:32:31.4226+06', str(setting)) # NOAA 19:29

        return


    def test_timezone_n6(self):
        """Tests timezone -6"""

        an_observer = Transforms.utils.latlon2spherical(a_latitude = coords.angle(45),
                                                        a_longitude = coords.angle(-90))

        a_datetime = coords.datetime('2015-05-22T12:00:00-06')

        rising, transit, setting = SunPosition.SunRiseAndSet(an_observer, a_datetime)

        self.assertEqual('2015-05-22T04:25:11.9585-06', str(rising))  # NOAA 04:24
        self.assertEqual('2015-05-22T11:57:36.6885-06', str(transit)) # NOAA 11:56:40
        self.assertEqual('2015-05-22T19:30:1.41858-06', str(setting)) # NOAA 19:30

        return


    def test_wrong_date_2018jan31(self):
        """Tests wrong dy 2018jan31"""

        a_datetime = coords.datetime('2018-01-31T12:55:00-08')
        rising, transit, setting = SunPosition.SunRiseAndSet(self.mlc404, a_datetime)

        self.assertEqual('2018-01-31T07:13:26.5023-08', str(rising))
        self.assertEqual('2018-01-31T12:22:31.1063-08', str(transit))
        self.assertEqual('2018-01-31T17:31:35.7103-08', str(setting))

        return


    def test_wrong_date_2018feb01(self):
        """Tests wrong day 2018feb01"""

        a_datetime = coords.datetime('2018-02-01T12:55:00-08')

        rising, transit, setting = SunPosition.SunRiseAndSet(self.mlc404, a_datetime)

        self.assertEqual('2018-02-01T07:12:37.4165-08', str(rising))
        self.assertEqual('2018-02-01T12:22:39.6759-08', str(transit))
        self.assertEqual('2018-02-01T17:32:41.9353-08', str(setting)) # was 2018-01-31

        return

    @unittest.skip('fails +1 to date!?!?! leap day?')
    def test_wrong_rising_2018feb28(self):
        """Tests 2018feb28 += 1 is noonp

        TODO special test case 2018-02-28T10:55:00-08 fails noop
        2018-02-27T06:41:52.695-08 + 1 error in += implementation for
        leap day?

        """

        a_datetime = coords.datetime('2018-02-28T10:55:00-08')

        rising, transit, setting = SunPosition.SunRiseAndSet(self.mlc404, a_datetime)

        self.assertEqual('2018-02-28T06:41:52.695-08', str(rising))
        self.assertEqual('2018-02-28T12:21:24.1057-08', str(transit))
        self.assertEqual('2018-02-28T18:00:55.5163-08', str(setting))

        return


    def test_2018mar01(self):
        """Tests wrong day 2018mar01"""

        a_datetime = coords.datetime('2018-03-01T10:00:00-08')

        rising, transit, setting = SunPosition.SunRiseAndSet(self.mlc404, a_datetime)

        self.assertEqual('2018-03-01T06:40:24.7133-08', str(rising))
        self.assertEqual('2018-03-01T12:21:4.26997-08', str(transit))
        self.assertEqual('2018-03-01T18:01:43.8267-08', str(setting))

        return





    def test_mlc_2018apr18_7am(self):
        """Tests wrong day observer timezone less than current hour

        This is one of four tests bracketing the problem of getting
        the wrong date depending on the timezone: -122 latitude (-8
        timezone) but before 8 am getting the previous day.

        this hits plus1 in rising and transit and plus2 in setting

        """

        a_datetime = coords.datetime('2018-04-18T07:00:00-08') # no DST

        rising, transit, setting = SunPosition.SunRiseAndSet(self.mlc404, a_datetime)

        self.assertEqual('2018-04-18T05:33:58.6014-08', str(rising))
        self.assertEqual('2018-04-18T12:11:35.1228-08', str(transit))
        self.assertEqual('2018-04-18T18:49:11.6441-08', str(setting))

        return


    def test_mlc_2018apr18_9am(self):
        """Tests wrong day observer timezone greater than current hour

        This is one of four tests bracketing the problem of getting
        the wrong date depending on the timezone: -122 latitude (-8
        timezone) but after 8 am getting the correct day.

        """

        a_datetime = coords.datetime('2018-04-18T09:00:00-08') # no DST

        rising, transit, setting = SunPosition.SunRiseAndSet(self.mlc404, a_datetime)

        self.assertEqual('2018-04-18T05:30:14.9913-08', str(rising)) # TODO should be same as test_2018apr18_7am?
        self.assertEqual('2018-04-18T12:07:57.1532-08', str(transit))
        self.assertEqual('2018-04-18T18:45:39.3151-08', str(setting))

        return


    def test_antimlc_2018apr18_5pm(self):
        """Tests wrong day observer timezone greater than current hour

        This is one of four tests bracketing the problem of getting
        the wrong date depending on the timezone: +122 latitude (+8
        timezone) but after 4 pm getting the wrong day.

        this hits minus2 in rising and minus1 in transit and setting

        """

        a_datetime = coords.datetime('2018-04-18T17:00:00+08') # no DST

        rising, transit, setting = SunPosition.SunRiseAndSet(self.antimlc404, a_datetime)

        self.assertEqual('2018-04-18T05:12:14.7203+08', str(rising))
        self.assertEqual('2018-04-18T11:51:4.37649+08', str(transit))
        self.assertEqual('2018-04-18T18:29:54.0326+08', str(setting))

        return


    def test_antimlc_2018apr18_3pm(self):
        """Tests wrong day observer timezone less than current hour

        This is one of four tests bracketing the problem of getting
        the wrong date depending on the timezone: +122 latitude (+8
        timezone) but before 4 pm getting the correct day.

        """

        a_datetime = coords.datetime('2018-04-18T15:00:00+08') # no DST

        rising, transit, setting = SunPosition.SunRiseAndSet(self.antimlc404, a_datetime)

        self.assertEqual('2018-04-18T05:15:58.2673+08', str(rising))
        self.assertEqual('2018-04-18T11:54:42.3127+08', str(transit))
        self.assertEqual('2018-04-18T18:33:26.3581+08', str(setting))

        return




    def test_antimlc_2018oct18_3pm(self):
        """Test for in the fall"""

        a_datetime = coords.datetime('2018-10-18T15:00:00+08') # no DST

        rising, transit, setting = SunPosition.SunRiseAndSet(self.antimlc404, a_datetime)

        self.assertEqual('2018-10-18T06:06:47.3352+08', str(rising))
        self.assertEqual('2018-10-18T11:40:31.1913+08', str(transit))
        self.assertEqual('2018-10-18T17:14:15.0475+08', str(setting))

        return



    def test_mlc_2018aug31_10am(self):
        """Test for in august"""

        a_datetime = coords.datetime('2018-08-31T10:00:00-08') # no DST

        rising, transit, setting = SunPosition.SunRiseAndSet(self.mlc404, a_datetime)

        self.assertEqual('2018-08-31T05:37:57.0511-08', str(rising))
        self.assertEqual('2018-08-31T12:09:6.82784-08', str(transit))
        self.assertEqual('2018-08-31T18:40:16.6046-08', str(setting))

        return




if __name__ == '__main__':
    unittest.main()
