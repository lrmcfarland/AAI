#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Unit tests for Stjarn Himlen transforms

To Run




"""

from __future__ import absolute_import  # for python 2 and 3

import math
import time
import unittest

import starbug.coords as coords
import AAI.Bodies.StjarnHimlen

import AAI.Transforms.utils


class StjarnHimlenTests(unittest.TestCase):

    """Tests Starry Sky methods

    validate:
        http://www.satellite-calculations.com/Satellite/suncalc.htm
        http://www.stargazing.net/mas/al_az.htm

    TODO TestStjarnHimlen.test_GMST_J2000_plus_day is 8 seconds too long.

    """

    def setUp(self):
        """Set up test parameters."""

        self.places = 5


    @unittest.skip('hacking')
    def test_GMST(self):
        """Hacking Test of GMST

        gmst hours agrees with USNO when half a day off (approximately):

        StH a day ahead agrees better?

        USNO('2000-01-01T00:00:00') == 6:35/9:24 == StH('2000-01-01T12:00:00')
        USNO('2000-01-01T06:00:00') == -11:19:8 == StH('2000-01-02T18:00:00')
        USNO('2000-01-01T12:00:00') == -5:18:9 == StH('2000-01-02T00:00:00')
        USNO('2000-01-02T00:00:00') == 6:35/9:24 == StH('2000-01-02T12:00:00')

        """
        a_datetime = coords.datetime('2015-01-01T00:00:00')
        a_gmst = AAI.Bodies.StjarnHimlen.GMST(a_datetime)


    def test_SolarLongitude_J2000(self):
        """Tests solar longitude calculation for J2000"""
        j2000 = coords.datetime('2000-01-01T00:00:00')
        a_solar_longitude = AAI.Bodies.StjarnHimlen.SolarLongitude(j2000)

        self.assertAlmostEqual(278.34302342798696, a_solar_longitude.value, self.places)


    def test_SolarRADec_J2000(self):
        """Tests solar RA and Dec calculation for J2000"""
        j2000 = coords.datetime('2000-01-01T00:00:00')
        RA, Dec = AAI.Bodies.StjarnHimlen.SolarRADec(j2000)

        self.assertAlmostEqual(279.0813909223767, RA.value, self.places)
        self.assertAlmostEqual(-23.17667313807378, Dec.value, self.places)


    def test_GMST0_J2000(self):
        """Tests GMST0 calculation for J2000"""
        j2000 = coords.datetime('2000-01-01T00:00:00')
        gmst0 = AAI.Bodies.StjarnHimlen.GMST0(j2000)

        self.assertAlmostEqual(98.34302342798696, gmst0.value, self.places)


    def test_GMST_J2000(self):
        """Tests GMST calculation for J2000"""
        j2000 = coords.datetime('2000-01-01T00:00:00')
        gmst = AAI.Bodies.StjarnHimlen.GMST(j2000)

        self.assertAlmostEqual(-5.443798438134203, gmst.value, self.places)


    @unittest.skip('TODO delta 8 seconds longer!')
    def test_GMST_J2000_plus_day(self):
        """Test GMST J2000 plus a day"""
        a_datetime_0 = coords.datetime('2000-01-01T12:00:00')
        a_gmst_0 = AAI.Bodies.StjarnHimlen.GMST(a_datetime_0)
        a_datetime_1 = coords.datetime('2000-01-02T12:00:00')
        a_gmst_1 = AAI.Bodies.StjarnHimlen.GMST(a_datetime_1)

        # returns '00:04:4.61177'
        self.assertEqual('00:03:56.5554', str(a_gmst_1 - a_gmst_0))


    def test_GMST_StA(self):
        """Tests GMST calculation for St. Andrews example"""
        a_datetime = coords.datetime('2000-01-01T00:00:00')
        gmst = AAI.Bodies.StjarnHimlen.GMST(a_datetime)

        self.assertAlmostEqual(-5.443798438134203, gmst.value, self.places)




    @unittest.skip('hacking')
    def test_SolarLongitude_for_years(self):
        """Tests solar longitude calculation by months for years

        TODO:
        flips to 0 on March 21 2000, not quite equinox, not quite midnight.
        different in different years.
        """

        for i in xrange(0, 5):
            for j in xrange(1, 13):
                for k in xrange(1, 28):
                    a_datetime = coords.datetime('201%d-%02d-%02dT00:00:00' % (i, j, k))
                    a_solar_longitude = AAI.Bodies.StjarnHimlen.SolarLongitude(a_datetime)
                    print(a_datetime, a_solar_longitude)



    @unittest.skip('hacking')
    def test_sirius(self):
        """Test RA/dec of Sirius

        http://en.wikipedia.org/wiki/Sirius

        RA: 6h 45m 8.9173s
        Dec: -16* 42' 58.017"

        From theodolite app:
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

        TODO

        """


        sirius = Transforms.utils.radec2spherical(a_right_ascension=coords.angle(6, 45, 8.9173),
                                                  a_declination=coords.angle(-16, 42, 58.017))

        an_observer = coords.spherical(1, coords.latitude(37, 24), coords.angle(-122, 4, 57))

        a_datetime = coords.datetime('2014-12-31T20:41:00') # obs 1
        # a_datetime = coords.datetime('2015-01-06T21:39:00') # obs 2

        sirius_hz = AAI.Bodies.StjarnHimlen.toHorizon(sirius, an_observer, a_datetime)

        print('sirius', sirius_hz)

        # TODO validate something



if __name__ == '__main__':
    unittest.main()
