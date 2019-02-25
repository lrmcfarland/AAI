#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Unit tests for Right Ascension, declination, Ecliptic and Equatorial transforms

to run:  ./pylaunch.sh test_SiderealTime.py
verbose: ./pylaunch.sh test_SiderealTime.py -v
filter:  ./pylaunch.sh test_SiderealTime.py USNO_C163_Tests.test_GMST_J2000
debug:   ./pylaunch.sh -m pdb test_SiderealTime.py

(Pdb) n # until import
> /Users/lrm/src/Astronomy/Transforms/test_SiderealTime.py(24)<module>()
-> import SiderealTime

(Pdb) b SiderealTime.USNO_C163.GMST
Breakpoint 1 at /Users/lrm/src/Astronomy/Transforms/SiderealTime.py:68
(Pdb) c
s> /Users/lrm/src/Astronomy/Transforms/SiderealTime.py(79)GMST()
-> JD, JDo = cls.JulianDate0(a_datetime)
(Pdb) n
> /Users/lrm/src/Astronomy/Transforms/SiderealTime.py(81)GMST()
-> D = JD - a_datetime.J2000
(Pdb) p JD
2457023.3618055554


"""

import math
import time
import unittest

import starbug.coords as coords
import SiderealTime

class USNO_C163_Tests(unittest.TestCase):

    """Test USNO transforms.

    from:
        http://aa.usno.navy.mil/faq/docs/GAST.php
        http://aa.usno.navy.mil/publications/docs/Circular_163.pdf

    validate:
        http://aa.usno.navy.mil/data/docs/JulianDate.php
        http://aa.usno.navy.mil/data/docs/siderealtime.php

        This service is only valid for dates between January 1, 2014 and December 31, 2016.
    """

    def setUp(self):
        """Set up test parameters."""

        self.places = 5
        self.xforms = SiderealTime.USNO_C163()


    @unittest.skip('hacking')
    def test_GMST(self):
        """Hacking GMST"""
        a_datetime = coords.datetime('2015-06-01T00:00:00')
        a_gmst = self.xforms.GMST(a_datetime)
        a_gast = self.xforms.GAST(a_datetime)


    @unittest.skip('hacking')
    def test_LST(self):
        """Hacking LST"""
        a_datetime = coords.datetime('2014-12-31T20:41:00')
        an_observer = coords.spherical(1, coords.latitude(37, 24), coords.angle(-122, 4, 57))

        a_gmst = self.xforms.GMST(a_datetime)
        a_lsta = self.xforms.LSTA(a_datetime, an_observer)


    def test_JDo_0(self):
        """Test JDo of 00:00 is the current time at midnight."""
        a_datetime = coords.datetime('2015-01-01T00:00:00')
        a_JD, a_JDo = self.xforms.JulianDate0(a_datetime)

        a_JD_datetime = coords.datetime()
        a_JD_datetime.fromJulianDate(a_JD)
        a_JDo_datetime = coords.datetime()
        a_JDo_datetime.fromJulianDate(a_JDo)

        self.assertEqual(2457023.5, a_JD)
        self.assertEqual('2015-01-01T00:00:00', str(a_JD_datetime))

        self.assertEqual(2457023.5, a_JDo)
        self.assertEqual('2015-01-01T00:00:00', str(a_JDo_datetime))


    def test_JDo_1(self):
        """Test JDo of 01:00 is the previous midnight."""
        a_datetime = coords.datetime('2015-01-01T01:00:00')
        a_JD, a_JDo = self.xforms.JulianDate0(a_datetime)

        a_JD_datetime = coords.datetime()
        a_JD_datetime.fromJulianDate(a_JD)
        a_JDo_datetime = coords.datetime()
        a_JDo_datetime.fromJulianDate(a_JDo)

        self.assertEqual(2457023.5416666665, a_JD)
        self.assertEqual('2015-01-01T01:00:00', str(a_JD_datetime))

        self.assertEqual(2457023.5, a_JDo)
        self.assertEqual('2015-01-01T00:00:00', str(a_JDo_datetime))


    def test_JDo_13(self):
        """Test JDo of 13:00 is the previous midnight."""

        a_datetime = coords.datetime('2015-02-01T13:00:00')
        a_JD, a_JDo = self.xforms.JulianDate0(a_datetime)

        a_JD_datetime = coords.datetime()
        a_JD_datetime.fromJulianDate(a_JD)
        a_JDo_datetime = coords.datetime()
        a_JDo_datetime.fromJulianDate(a_JDo)

        self.assertEqual(2457055.0416666665, a_JD)
        self.assertEqual('2015-02-01T13:00:00', str(a_JD_datetime))

        self.assertEqual(2457054.5, a_JDo)
        self.assertEqual('2015-02-01T00:00:00', str(a_JDo_datetime))


    def test_JDo_23(self):
        """Test JDo of 23:00 is the previous midnight."""

        a_datetime = coords.datetime('2015-03-15T23:59:59')
        a_JD, a_JDo = self.xforms.JulianDate0(a_datetime)

        a_JD_datetime = coords.datetime()
        a_JD_datetime.fromJulianDate(a_JD)
        a_JDo_datetime = coords.datetime()
        a_JDo_datetime.fromJulianDate(a_JDo)

        self.assertEqual(2457097.499988426, a_JD)
        self.assertEqual('2015-03-15T23:59:59', str(a_JD_datetime))

        self.assertEqual(2457096.5, a_JDo)
        self.assertEqual('2015-03-15T00:00:00', str(a_JDo_datetime))


    def test_GMST_J2000(self):
        """Test GMST J2000"""
        a_datetime = coords.datetime(self.xforms.J2000)
        a_gmst = self.xforms.GMST(a_datetime)

        self.assertEqual('18:41:50.5484', str(a_gmst))
        # Note: out of range of http://aa.usno.navy.mil/data/docs/siderealtime.php


    def test_GMST_J2000_plus_day(self):
        """Test GMST J2000 plus a day"""
        a_datetime_0 = coords.datetime(self.xforms.J2000)
        a_gmst_0 = self.xforms.GMST_simplified(a_datetime_0)
        a_datetime_1 = coords.datetime('2000-01-02T12:00:00')
        a_gmst_1 = self.xforms.GMST_simplified(a_datetime_1)

        self.assertEqual('00:03:56.5554', str(a_gmst_1 - a_gmst_0))
        # matches http://en.wikipedia.org/wiki/Sidereal_time


    def test_GMST_J2000_plus_halfday(self):
        """Test GMST J2000 plus a halfday"""
        a_datetime_0 = coords.datetime(self.xforms.J2000)
        a_gmst_0 = self.xforms.GMST_simplified(a_datetime_0)
        a_datetime_1 = coords.datetime('2000-01-02T00:00:00')
        a_gmst_1 = self.xforms.GMST_simplified(a_datetime_1)

        self.assertEqual('12:01:58.2777', str(a_gmst_1 - a_gmst_0))


    def test_GMST_kb(self):
        """Test GMST formula, in hours, with kburnett data"""
        # This example is from
        # http://www2.arnes.si/~gljsentvid10/sidereal.htm and uses
        # the same formula as
        # http://aa.usno.navy.mil/faq/docs/GAST.php
        # but
        # http://aa.usno.navy.mil/data/docs/siderealtime.php says this
        # date is out of range.

        a_datetime = coords.datetime('1994-06-16T18:00:00')
        a_gmst = self.xforms.GMST(a_datetime)

        self.assertEqual('11:39:5.06752', str(a_gmst))


    def test_GMST_standrews(self):
        """Test GMST at St. Andrews"""
        # from http://star-www.st-and.ac.uk/~fv/webnotes/answer6.htm
        a_datetime = coords.datetime('1998-02-04T00:00:00')
        a_gmst = self.xforms.GMST(a_datetime)

        sta_long = coords.angle(2, 48)

        # TODO is 02:47:60, should be 2:48 but is not rounding 60 seconds up
        self.assertEqual('02:47:60', str(sta_long))

        # TODO this is 11 minutes off from answer6, but 11 minutes from GMT.
        self.assertEqual('08:55:49.7347', str(a_gmst))



    def test_GMST_2014_12_31_8pm(self):
        """Test GMST """
        # validate http://aa.usno.navy.mil/cgi-bin/aa_siderealtime.pl?form=1&year=2014&month=12&day=31&hr=20&min=41&sec=0.0&intv_mag=1.0&intv_unit=1&reps=5&state=CA&place=mountain+view
        a_datetime = coords.datetime('2014-12-31T20:41:00')
        a_gmst = self.xforms.GMST(a_datetime)
        a_gast = self.xforms.GAST(a_datetime)
        an_eqeq = a_gast - a_gmst

        an_observer = coords.spherical(1, coords.latitude(37, 23, 24), coords.angle(-122, 4, 48))
        a_lstm = self.xforms.LSTM(an_observer, a_datetime)
        a_lsta = self.xforms.LSTA(an_observer, a_datetime)

        self.assertEqual('03:21:46.443', str(a_gmst)) # Actual: 3 21 46.4412
        self.assertEqual('03:21:46.7422', str(a_gast)) # Actual: 3 21 46.7386
        self.assertEqual('00:00:0.299296', str(an_eqeq)) # Actual: +0.2975 seconds
        self.assertEqual('19:13:27.243', str(a_lstm)) # Actual: 19 13 27.2412
        self.assertEqual('19:13:27.5422', str(a_lsta)) # Actual: 19 13 27.5386


    def test_GMST_2015_01_01_8am(self):
        """Test GMST 2015 01 01 8 am"""
        # validate http://aa.usno.navy.mil/cgi-bin/aa_siderealtime.pl?form=1&year=2015&month=1&day=01&hr=08&min=0&sec=0.0&intv_mag=1.0&intv_unit=1&reps=5&state=CA&place=mountain+view

        a_datetime = coords.datetime('2015-01-01T08:00:00')
        a_gmst = self.xforms.GMST(a_datetime)
        a_gast = self.xforms.GAST(a_datetime)
        an_eqeq = a_gast - a_gmst

        an_observer = coords.spherical(1, coords.latitude(37, 23, 24), coords.angle(-122, 4, 48))
        a_lstm = self.xforms.LSTM(an_observer, a_datetime)
        a_lsta = self.xforms.LSTA(an_observer, a_datetime)

        self.assertEqual('14:42:37.9854', str(a_gmst)) # Actual: 14 42 37.9836
        self.assertEqual('14:42:38.2855', str(a_gast)) # Actual: 14 42 38.2828
        self.assertEqual('00:00:0.300053', str(an_eqeq)) # Actual: +0.2992 seconds
        self.assertEqual('06:34:18.7854', str(a_lstm)) # Actual: 6 34 18.7836
        self.assertEqual('06:34:19.0855', str(a_lsta)) # Actual: 6 34 19.0828


    def test_GMST_2015_01_01_2pm(self):
        """Test GMST 2015 01 01 2 pm"""
        # validate http://aa.usno.navy.mil/cgi-bin/aa_siderealtime.pl?form=1&year=2015&month=1&day=01&hr=14&min=0&sec=0.0&intv_mag=1.0&intv_unit=1&reps=5&state=CA&place=mountain+view

        a_datetime = coords.datetime('2015-01-01T14:00:00')
        a_gmst = self.xforms.GMST(a_datetime)
        a_gast = self.xforms.GAST(a_datetime)
        an_eqeq = a_gast - a_gmst

        an_observer = coords.spherical(1, coords.latitude(37, 23, 24), coords.angle(-122, 4, 48))
        a_lstm = self.xforms.LSTM(an_observer, a_datetime)
        a_lsta = self.xforms.LSTA(an_observer, a_datetime)

        self.assertEqual('20:43:37.1242', str(a_gmst)) # Actual: 20 43 37.1224
        self.assertEqual('20:43:37.4247', str(a_gast)) # Actual: 20 43 37.4227
        self.assertEqual('00:00:0.300452', str(an_eqeq)) # Actual: +0.3003 seconds
        self.assertEqual('12:35:17.9242', str(a_lstm)) # Actual: 12 35 17.9224
        self.assertEqual('12:35:18.2247', str(a_lsta)) # Actual: 12 35 18.2227



    def test_GMST_2015_01_01_2pm_tz1(self):
        """Test GMST 2015 01 01 2 pm timezone +1"""
        a_datetime = coords.datetime('2015-01-01T14:00:00+0100')
        a_gmst = self.xforms.GMST(a_datetime)
        a_gast = self.xforms.GAST(a_datetime)
        an_eqeq = a_gast - a_gmst

        self.assertEqual('20:43:46.9807', str(a_gmst)) # Actual: 20 43 37.1224
        self.assertEqual('20:43:47.2812', str(a_gast)) # Actual: 20 43 37.4227
        self.assertEqual('00:00:0.300518', str(an_eqeq)) # Actual: +0.3003 seconds
        # validate http://aa.usno.navy.mil/cgi-bin/aa_siderealtime.pl?form=2&year=2015&month=1&day=01&hr=14&min=0&sec=0.0&intv_mag=1.0&intv_unit=1&reps=5&place=%28no+name+given%29&lon_sign=1&lon_deg=15&lon_min=&lon_sec=&lat_sign=1&lat_deg=0&lat_min=&lat_sec=


    def test_GMST_2pm_tzn1(self):
        """Test GMST 2015 01 01 2 pm timezone -1"""
        a_datetime = coords.datetime('2015-01-01T14:00:00-01:00')
        a_gmst = self.xforms.GMST(a_datetime)
        a_gast = self.xforms.GAST(a_datetime)
        an_eqeq = a_gast - a_gmst

        self.assertEqual('20:43:27.2677', str(a_gmst)) # Actual: 20 43 37.1224
        self.assertEqual('20:43:27.5681', str(a_gast)) # Actual: 20 43 37.4227
        self.assertEqual('00:00:0.300386', str(an_eqeq)) # Actual: +0.3003 seconds
        # validate http://aa.usno.navy.mil/cgi-bin/aa_siderealtime.pl?form=2&year=2015&month=1&day=01&hr=14&min=0&sec=0.0&intv_mag=1.0&intv_unit=1&reps=5&place=%28no+name+given%29&lon_sign=-1&lon_deg=15&lon_min=&lon_sec=&lat_sign=1&lat_deg=0&lat_min=&lat_sec=



    def test_GMST_simplified_J2000(self):
        """Test GMST simplified J2000"""
        a_datetime = coords.datetime(self.xforms.J2000)
        a_gmst = self.xforms.GMST_simplified(a_datetime)
        self.assertEqual('-5:18:9.45159', str(a_gmst))


    def test_GMST_simplified_J2000_plus_day(self):
        """Test GMST J2000 plus a day"""
        a_datetime_0 = coords.datetime(self.xforms.J2000)
        a_gmst_0 = self.xforms.GMST_simplified(a_datetime_0)
        a_datetime_1 = coords.datetime('2000-01-02T12:00:00')
        a_gmst_1 = self.xforms.GMST_simplified(a_datetime_1)

        self.assertEqual('00:03:56.5554', str(a_gmst_1 - a_gmst_0))


    def test_GMST_simplified_standrews(self):
        """Test GMST simplified at St. Andrews"""
        # from http://star-www.st-and.ac.uk/~fv/webnotes/answer6.htm
        a_datetime = coords.datetime('1998-02-04T00:00:00')
        a_gmst = self.xforms.GMST_simplified(a_datetime)

        sta_long = coords.angle(2, 48)
        # TODO is 02:47:60, should be 2:48 but is not rounding 60 seconds up
        self.assertEqual('02:47:60', str(sta_long))

        # TODO this is 11 minutes off from answer6, but 11 minutes from GMT.
        self.assertEqual('08:55:49.7347', str(a_gmst))


    def test_GMST_simplified_kb(self):
        """Test GMST simplified formula, in hours, with kburnett data"""
        # from http://www2.arnes.si/~gljsentvid10/sidereal.htm
        a_datetime = coords.datetime('1994-06-16T18:00:00')
        a_gmst = self.xforms.GMST_simplified(a_datetime)

        # -0.00001 seconds different from given test data
        self.assertEqual('11:39:5.06724', str(a_gmst))


    def test_GMST_simplified2_kb(self):
        """Test GMST simplified formula 2, in degrees, with kburnett data"""
        # from http://www2.arnes.si/~gljsentvid10/sidereal.htm
        a_datetime = coords.datetime('1994-06-16T18:00:00')
        a_gmst = self.xforms.GMST_simplified2(a_datetime)

        # matches test data given when rouded to 0.0001 places
        self.assertEqual('11:39:5.06723', str(a_gmst))


    def test_GMST_meeus_12a(self):
        """Test GMST with Meeus example 12a"""
        # from Astronomical Algorithms, Jean Meeus, pp. 88

        a_datetime = coords.datetime('1987-04-10T00:00:00')
        self.assertEqual(2446895.5, a_datetime.toJulianDate())
        # Meeus: 2446895.5

        a_gmst = self.xforms.GMST(a_datetime)
        self.assertEqual('13:10:46.3668', str(a_gmst))
        # Meeus: 13:10:46.3668

        a_gast = self.xforms.GAST(a_datetime)
        self.assertEqual('13:10:46.1154', str(a_gast))
        # Meeus: 13:10:46.1351. I am using a different algorithm for
        # obliquity of ecliptic (USNOs)


    def test_GMST_meeus_12b(self):
        """Test GMST with Meeus example 12b"""
        # from Astronomical Algorithms, Jean Meeus, pp. 89

        a_datetime = coords.datetime('1987-04-10T19:21:00')
        self.assertEqual(2446896.30625, a_datetime.toJulianDate())
        # Meeus: 2446896.30625

        a_gmst = self.xforms.GMST(a_datetime)
        self.assertEqual('08:34:57.0896', str(a_gmst))
        # Meeus: 08:34:57.0896


if __name__ == '__main__':
    unittest.main()
