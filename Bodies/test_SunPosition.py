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

from __future__ import absolute_import # for python 2 and 3

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

        sun = SunPosition.HorizontalCoords(self.mlc404, a_datetime)

        self.assertAlmostEqual(243.30488300565906, sun.phi.degrees, self.places)

        sextant_alt = coords.angle(Transforms.utils.parse_angle_arg('70:10')/2)
        self.assertAlmostEqual(sextant_alt.degrees, sun.theta.complement().degrees, delta=1)

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

        sun = SunPosition.HorizontalCoords(self.mlc404, a_datetime)

        self.assertAlmostEqual(268.1014512724721, sun.phi.degrees, self.places)

        sextant_alt = coords.angle(Transforms.utils.parse_angle_arg('44:32')/2)
        self.assertAlmostEqual(sextant_alt.degrees, sun.theta.complement().degrees, delta=1)

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

        sun = SunPosition.HorizontalCoords(self.mlc404, a_datetime)

        self.assertAlmostEqual(95.79970206137686, sun.phi.degrees, self.places)

        sextant_alt = coords.angle(Transforms.utils.parse_angle_arg('66:46')/2)
        self.assertAlmostEqual(sextant_alt.degrees, sun.theta.complement().degrees, delta=2)

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
        self.assertAlmostEqual(-3.901196866415546, eot.degrees*60, self.places)

        return


    def test_2015_02_11T12_00(self):
        """Test Equation of time 2015-02-11T12:00:00

        first local minimum of the year

        validate with http://www.esrl.noaa.gov/gmd/grad/solcalc/
        """

        a_datetime = coords.datetime(2015, 2, 11, 12)
        eot = SunPosition.EquationOfTime(a_datetime)

        # NOAA says -14.24 minutes
        self.assertAlmostEqual(-14.212711856485711, eot.degrees*60, self.places)

        return


    def test_2015_03_20T12_00(self):
        """Test Equation of time 2015-03-20T12:00:00

        validate with http://www.esrl.noaa.gov/gmd/grad/solcalc/
        """

        a_datetime = coords.datetime(2015, 3, 20, 12)
        eot = SunPosition.EquationOfTime(a_datetime)

        # NOAA says -7.44 minutes
        self.assertAlmostEqual(-7.563513810377245, eot.degrees*60, self.places)

        return


    def test_2015_05_14T12_00(self):
        """Test Equation of time 2015-05-14T12:00:00

        first local maximum of the year

        validate with http://www.esrl.noaa.gov/gmd/grad/solcalc/
        """

        a_datetime = coords.datetime(2015, 5, 14, 12)
        eot = SunPosition.EquationOfTime(a_datetime)

        # NOAA says 3.65 minutes
        self.assertAlmostEqual(3.6588472510257475, eot.degrees*60, self.places)

        return


    def test_2015_07_26T12_00(self):
        """Test Equation of time 2015-07-26T12:00:00

        second local minimum of the year

        validate with http://www.esrl.noaa.gov/gmd/grad/solcalc/
        """

        a_datetime = coords.datetime(2015, 7, 26, 12)
        eot = SunPosition.EquationOfTime(a_datetime)

        # NOAA says -6.54 minutes
        self.assertAlmostEqual(-6.5354183954768175, eot.degrees*60, self.places)

        return


    def test_2015_11_03T12_00(self):
        """Test Equation of time 2015-11-03T12:00:00

        second local maximum of the year

        validate with http://www.esrl.noaa.gov/gmd/grad/solcalc/
        """

        a_datetime = coords.datetime(2015, 11, 3, 12)
        eot = SunPosition.EquationOfTime(a_datetime)

        # NOAA says 16.48 minutes
        self.assertAlmostEqual(16.43786410739647, eot.degrees*60, self.places)

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

        self.assertEqual('1988-03-20T12:26:09.3', str(rising)) # Meeus p. 104: 12:25
        self.assertEqual('1988-03-20T19:40:17.5', str(transit)) # Meeus p. 104: 19:41
        self.assertEqual('1988-03-20T02:54:25.8', str(setting)) # Meeus p. 104: 02:55

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

        self.assertEqual('2015-05-22T04:25:49.8+0100', str(rising))  # NOAA 04:24
        self.assertEqual('2015-05-22T11:58:26.9+0100', str(transit)) # NOAA 11:56:39
        self.assertEqual('2015-05-22T19:31:03.9+0100', str(setting)) # NOAA 19:30

        return


    def test_timezone_n1(self):
        """Tests timezone -1"""

        an_observer = Transforms.utils.latlon2spherical(a_latitude = coords.angle(45),
                                                        a_longitude = coords.angle(-15))

        a_datetime = coords.datetime('2015-05-22T12:00:00-01')

        rising, transit, setting = SunPosition.SunRiseAndSet(an_observer, a_datetime)

        self.assertEqual('2015-05-22T04:26:05.0-0100', str(rising))  # NOAA 04:24
        self.assertEqual('2015-05-22T11:58:47.0-0100', str(transit)) # NOAA 11:56:39
        self.assertEqual('2015-05-22T19:31:28.9-0100', str(setting)) # NOAA 19:30

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

        self.assertEqual('04:25:11.96', '{:02}:{:02}:{:05.2f}'.format(rising.hour, rising.minute, rising.second))
        self.assertEqual('11:57:36.69', '{:02}:{:02}:{:05.2f}'.format(transit.hour, transit.minute, transit.second))
        self.assertEqual('19:30:01.42', '{:02}:{:02}:{:05.2f}'.format(setting.hour, setting.minute, setting.second))

        return


    def test_timezone_n6(self):
        """Tests timezone -6"""

        an_observer = Transforms.utils.latlon2spherical(a_latitude = coords.angle(45),
                                                        a_longitude = coords.angle(-90))

        a_datetime = coords.datetime('2015-05-22T12:00:00-06')

        rising, transit, setting = SunPosition.SunRiseAndSet(an_observer, a_datetime)

        self.assertEqual('04:26:42.95', '{:02}:{:02}:{:05.2f}'.format(rising.hour, rising.minute, rising.second))    # NOAA 04:24
        self.assertEqual('11:59:37.19', '{:02}:{:02}:{:05.2f}'.format(transit.hour, transit.minute, transit.second)) # NOAA 11:56:40
        self.assertEqual('19:32:31.42', '{:02}:{:02}:{:05.2f}'.format(setting.hour, setting.minute, setting.second))  # NOAA 19:30

        return


    def test_wrong_date_2018jan31(self):
        """Tests wrong dy 2018jan31"""

        a_datetime = coords.datetime('2018-01-31T12:55:00-08')
        rising, transit, setting = SunPosition.SunRiseAndSet(self.mlc404, a_datetime)

        self.assertEqual('07:15:31.66', '{:02}:{:02}:{:05.2f}'.format(rising.hour, rising.minute, rising.second))
        self.assertEqual('12:25:14.61', '{:02}:{:02}:{:05.2f}'.format(transit.hour, transit.minute, transit.second))
        self.assertEqual('17:34:57.56', '{:02}:{:02}:{:05.2f}'.format(setting.hour, setting.minute, setting.second))

        return


    def test_wrong_date_2018feb01(self):
        """Tests wrong day 2018feb01"""

        a_datetime = coords.datetime('2018-02-01T12:55:00-08')

        rising, transit, setting = SunPosition.SunRiseAndSet(self.mlc404, a_datetime)

        self.assertEqual('07:14:41.50', '{:02}:{:02}:{:05.2f}'.format(rising.hour, rising.minute, rising.second))
        self.assertEqual('12:25:22.64', '{:02}:{:02}:{:05.2f}'.format(transit.hour, transit.minute, transit.second))
        self.assertEqual('17:36:03.78', '{:02}:{:02}:{:05.2f}'.format(setting.hour, setting.minute, setting.second))


        return


    def test_wrong_rising_2018feb28(self):
        """Tests 2018feb28 += 1 is noonp

        TODO special test case 2018-02-28T10:55:00-08 fails noop
        2018-02-27T06:41:52.695-08 + 1 error in += implementation for
        leap day?

        """

        a_datetime = coords.datetime('2018-02-28T10:55:00-08')

        rising, transit, setting = SunPosition.SunRiseAndSet(self.mlc404, a_datetime)

        self.assertEqual('06:43:35.75', '{:02}:{:02}:{:05.2f}'.format(rising.hour, rising.minute, rising.second))
        self.assertEqual('12:23:54.37', '{:02}:{:02}:{:05.2f}'.format(transit.hour, transit.minute, transit.second))
        self.assertEqual('18:04:13.00', '{:02}:{:02}:{:05.2f}'.format(setting.hour, setting.minute, setting.second))

        return


    def test_2018mar01(self):
        """Tests wrong day 2018mar01"""

        a_datetime = coords.datetime('2018-03-01T10:00:00-08')

        rising, transit, setting = SunPosition.SunRiseAndSet(self.mlc404, a_datetime)

        self.assertEqual('06:42:07.31', '{:02}:{:02}:{:05.2f}'.format(rising.hour, rising.minute, rising.second))
        self.assertEqual('12:23:34.21', '{:02}:{:02}:{:05.2f}'.format(transit.hour, transit.minute, transit.second))
        self.assertEqual('18:05:01.11', '{:02}:{:02}:{:05.2f}'.format(setting.hour, setting.minute, setting.second))

        return



    def test_mlc_2018apr18_0700(self):
        """Tests wrong day observer timezone less than current hour

        This is one of four tests bracketing the problem of getting
        the wrong date depending on the timezone: -122 latitude (-8
        timezone) but before 8 am getting the previous day.

        this hits plus1 in rising and transit and plus2 in setting

        """

        a_datetime = coords.datetime('2018-04-18T07:00:00-08') # no DST

        rising, transit, setting = SunPosition.SunRiseAndSet(self.mlc404, a_datetime)

        self.assertEqual('05:31:45.75', '{:02}:{:02}:{:05.2f}'.format(rising.hour, rising.minute, rising.second))
        self.assertEqual('12:10:07.33', '{:02}:{:02}:{:05.2f}'.format(transit.hour, transit.minute, transit.second))
        self.assertEqual('18:48:28.91', '{:02}:{:02}:{:05.2f}'.format(setting.hour, setting.minute, setting.second))

        return


    def test_mlc_2018apr18_0900(self):
        """Tests wrong day observer timezone greater than current hour

        This is one of four tests bracketing the problem of getting
        the wrong date depending on the timezone: -122 latitude (-8
        timezone) but after 8 am getting the correct day.

        """

        a_datetime = coords.datetime('2018-04-18T09:00:00-08') # no DST

        rising, transit, setting = SunPosition.SunRiseAndSet(self.mlc404, a_datetime)

        self.assertEqual('05:31:58.74', '{:02}:{:02}:{:05.2f}'.format(rising.hour, rising.minute, rising.second))
        self.assertEqual('12:10:25.94', '{:02}:{:02}:{:05.2f}'.format(transit.hour, transit.minute, transit.second))
        self.assertEqual('18:48:53.14', '{:02}:{:02}:{:05.2f}'.format(setting.hour, setting.minute, setting.second))

        return


    def test_antimlc_2018apr18_1700(self):
        """Tests wrong day observer timezone greater than current hour

        This is one of four tests bracketing the problem of getting
        the wrong date depending on the timezone: +122 latitude (+8
        timezone) but after 4 pm getting the wrong day.

        this hits minus2 in rising and minus1 in transit and setting

        """

        a_datetime = coords.datetime('2018-04-18T17:00:00+08') # no DST

        rising, transit, setting = SunPosition.SunRiseAndSet(self.antimlc404, a_datetime)

        self.assertEqual('05:14:27.36', '{:02}:{:02}:{:05.2f}'.format(rising.hour, rising.minute, rising.second))
        self.assertEqual('11:52:32.06', '{:02}:{:02}:{:05.2f}'.format(transit.hour, transit.minute, transit.second))
        self.assertEqual('18:30:36.76', '{:02}:{:02}:{:05.2f}'.format(setting.hour, setting.minute, setting.second))

        return


    def test_antimlc_2018apr18_1500(self):
        """Tests wrong day observer timezone less than current hour

        This is one of four tests bracketing the problem of getting
        the wrong date depending on the timezone: +122 latitude (+8
        timezone) but before 4 pm getting the correct day.

        """

        a_datetime = coords.datetime('2018-04-18T15:00:00+08') # no DST

        rising, transit, setting = SunPosition.SunRiseAndSet(self.antimlc404, a_datetime)

        self.assertEqual('05:14:14.39', '{:02}:{:02}:{:05.2f}'.format(rising.hour, rising.minute, rising.second))
        self.assertEqual('11:52:13.46', '{:02}:{:02}:{:05.2f}'.format(transit.hour, transit.minute, transit.second))
        self.assertEqual('18:30:12.53', '{:02}:{:02}:{:05.2f}'.format(setting.hour, setting.minute, setting.second))

        return


    def test_antimlc_2018oct18_1500(self):
        """Test for in the fall"""

        a_datetime = coords.datetime('2018-10-18T15:00:00+08') # no DST

        rising, transit, setting = SunPosition.SunRiseAndSet(self.antimlc404, a_datetime)


        self.assertEqual('06:03:31.51', '{:02}:{:02}:{:05.2f}'.format(rising.hour, rising.minute, rising.second))
        self.assertEqual('11:38:01.14', '{:02}:{:02}:{:05.2f}'.format(transit.hour, transit.minute, transit.second))
        self.assertEqual('17:12:30.76', '{:02}:{:02}:{:05.2f}'.format(setting.hour, setting.minute, setting.second))

        return


    def test_mlc_2018aug31_1000(self):
        """Test for mlc 2018aug31 1000"""

        a_datetime = coords.datetime('2018-08-31T10:00:00-08') # no DST

        rising, transit, setting = SunPosition.SunRiseAndSet(self.mlc404, a_datetime)

        self.assertEqual('05:41:07.94', '{:02}:{:02}:{:05.2f}'.format(rising.hour, rising.minute, rising.second))
        self.assertEqual('12:11:32.03', '{:02}:{:02}:{:05.2f}'.format(transit.hour, transit.minute, transit.second))
        self.assertEqual('18:41:56.12', '{:02}:{:02}:{:05.2f}'.format(setting.hour, setting.minute, setting.second))

        return


    def test_mlc_2018apr20_0600(self):
        """Test for mlc 2018apr20

        Rising off by a day in old algorithm
        This works for current time 7 am and onward.
        """

        a_datetime = coords.datetime('2018-04-20T06:00:00-08') # no DST

        rising, transit, setting = SunPosition.SunRiseAndSet(self.mlc404, a_datetime)

        self.assertEqual('05:28:59.27', '{:02}:{:02}:{:05.2f}'.format(rising.hour, rising.minute, rising.second))
        self.assertEqual('12:09:32.26', '{:02}:{:02}:{:05.2f}'.format(transit.hour, transit.minute, transit.second))
        self.assertEqual('18:50:05.25', '{:02}:{:02}:{:05.2f}'.format(setting.hour, setting.minute, setting.second))

        return


    def test_mlc_2018apr20_1800(self):
        """Test for mlc 2018apr20 1800

        Rising off by a day in old algorithm
        """

        a_datetime = coords.datetime('2018-04-20T18:00:00-08') # no DST

        rising, transit, setting = SunPosition.SunRiseAndSet(self.mlc404, a_datetime)

        self.assertEqual('05:26:21.50', '{:02}:{:02}:{:05.2f}'.format(rising.hour, rising.minute, rising.second))
        self.assertEqual('12:07:27.80', '{:02}:{:02}:{:05.2f}'.format(transit.hour, transit.minute, transit.second))
        self.assertEqual('18:48:34.10', '{:02}:{:02}:{:05.2f}'.format(setting.hour, setting.minute, setting.second))

        return


    def test_mlc_2018apr22_0600(self):
        """Test for setting off by a day in the old algorithm"""

        a_datetime = coords.datetime('2018-04-22T06:00:00-08') # no DST

        rising, transit, setting = SunPosition.SunRiseAndSet(self.mlc404, a_datetime)

        self.assertEqual('05:26:22.56', '{:02}:{:02}:{:05.2f}'.format(rising.hour, rising.minute, rising.second))
        self.assertEqual('12:09:08.20', '{:02}:{:02}:{:05.2f}'.format(transit.hour, transit.minute, transit.second))
        self.assertEqual('18:51:53.84', '{:02}:{:02}:{:05.2f}'.format(setting.hour, setting.minute, setting.second))

        return


    def test_mlc_2018apr22_2000(self):
        """Test for setting off by a day in the old algorithm"""

        a_datetime = coords.datetime('2018-04-22T20:00:00-08') # no DST

        rising, transit, setting = SunPosition.SunRiseAndSet(self.mlc404, a_datetime)

        self.assertEqual('05:23:58.94', '{:02}:{:02}:{:05.2f}'.format(rising.hour, rising.minute, rising.second))
        self.assertEqual('12:07:22.95', '{:02}:{:02}:{:05.2f}'.format(transit.hour, transit.minute, transit.second))
        self.assertEqual('18:50:46.97', '{:02}:{:02}:{:05.2f}'.format(setting.hour, setting.minute, setting.second))

        return



if __name__ == '__main__':
    unittest.main()
