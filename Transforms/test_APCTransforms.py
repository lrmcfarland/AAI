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

from __future__ import absolute_import # for python 2 and 3

import math
import time
import unittest

import coords

import Transforms.APCTransforms
import Transforms.utils


class APCTransformTests(unittest.TestCase):
    """Test APC transforms."""

    def setUp(self):
        """Set up test parameters."""

        self.places = 5
        self.J2000 = '2000-01-01T00:00:00'
        return


    @unittest.skip('hacking')
    def test_GMST(self):
        """Hacking Test of GMST"""
        a_datetime = coords.datetime('2015-06-01T00:00:00')
        a_gmst = Transforms.APCTransforms.GMST(a_datetime)

        print('\nDatetime:', a_datetime) # TODO rm
        print('GMST', a_gmst) # TODO rm

        return


    def test_GMST_J2000(self):
        """Test GMST J2000"""
        a_datetime = coords.datetime(self.J2000)
        a_gmst = Transforms.APCTransforms.GMST(a_datetime)

        # TODO does not match USNO result which is not valid at this date.
        self.assertEqual('06:39:52.3', str(a_gmst))
        return


    def test_GMST_plus_day_2000(self):
        """Test J2000 plus a day"""
        a_datetime_0 = coords.datetime('2000-01-01T00:00:00')
        a_gmst_0 = Transforms.APCTransforms.GMST(a_datetime_0)
        a_datetime_1 = coords.datetime('2000-01-02T00:00:00')
        a_gmst_1 = Transforms.APCTransforms.GMST(a_datetime_1)

        self.assertEqual('00:03:56.6', str(a_gmst_1 - a_gmst_0))
        return


    def test_GMST_plus_day_2005(self):
        """Test J2000 plus a day"""
        a_datetime_0 = coords.datetime('2005-01-01T00:00:00')
        a_gmst_0 = Transforms.APCTransforms.GMST(a_datetime_0)
        a_datetime_1 = coords.datetime('2005-01-02T00:00:00')
        a_gmst_1 = Transforms.APCTransforms.GMST(a_datetime_1)

        self.assertEqual('00:03:56.6', str(a_gmst_1 - a_gmst_0))
        return


    def test_GMST_plus_day_2015(self):
        """Test plus another day"""
        a_datetime_0 = coords.datetime('2015-01-10T12:30:00')
        a_gmst_0 = Transforms.APCTransforms.GMST(a_datetime_0)
        a_datetime_1 = coords.datetime('2015-01-11T12:30:00')
        a_gmst_1 = Transforms.APCTransforms.GMST(a_datetime_1)

        self.assertEqual('00:03:56.6', str(a_gmst_1 - a_gmst_0))
        # matches http://en.wikipedia.org/wiki/Sidereal_time
        return


    def test_GMST_kb(self):
        """Test GMST formula, in degrees, with kburnett data"""
        # This example is from
        # http://www2.arnes.si/~gljsentvid10/sidereal.htm and uses
        # the same formula as
        # http://aa.usno.navy.mil/faq/docs/GAST.php
        # but
        # http://aa.usno.navy.mil/data/docs/siderealtime.php says this
        # date is out of range.

        a_datetime = coords.datetime('1994-06-16T18:00:00')
        a_gmst = Transforms.APCTransforms.GMST(a_datetime)

        # almost matches test data given above: 11h 39m 05.0675s
        self.assertEqual('11:39:05.1', str(a_gmst))
        return


    def test_GMST_standrews(self):
        """Test GMST St. Andrews"""
        # from http://star-www.st-and.ac.uk/~fv/webnotes/answer6.htm
        a_datetime = coords.datetime('1998-02-04T00:00:00')
        a_gmst = Transforms.APCTransforms.GMST(a_datetime)

        self.assertEqual('08:55:49.7', str(a_gmst))
        return


    def test_GMST_2014_12_31_8pm(self):
        """Test GMST """
        # validate http://aa.usno.navy.mil/cgi-bin/aa_siderealtime.pl?form=1&year=2014&month=12&day=31&hr=20&min=41&sec=0.0&intv_mag=1.0&intv_unit=1&reps=5&state=CA&place=mountain+view
        a_datetime = coords.datetime('2014-12-31T20:41:00')
        a_gmst = Transforms.APCTransforms.GMST(a_datetime)

        self.assertEqual('03:21:46.4', str(a_gmst)) # Actual: 3 21 46.4412

        return

    def test_GMST_2015_01_01_2pm(self):
        """Test GMST 2015 01 01 2 pm"""
        # validate http://aa.usno.navy.mil/cgi-bin/aa_siderealtime.pl?form=1&year=2015&month=1&day=01&hr=14&min=0&sec=0.0&intv_mag=1.0&intv_unit=1&reps=5&state=CA&place=mountain+view

        a_datetime = coords.datetime('2015-01-01T14:00:00')
        a_gmst = Transforms.APCTransforms.GMST(a_datetime)

        self.assertEqual('20:43:37.1', str(a_gmst)) # Actual: 20 43 37.1224

        return

    @unittest.skip('TODO')
    def test_sirius_2014_12_31T20_41_41(self):
        """Test RA/dec of Sirius

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

        """


        sirius = Transforms.utils.radec2spherical(a_right_ascension=coords.angle(6, 45, 8.9173),
                                                  a_declination=coords.angle(-16, 42, 58.017))

        print('\nsirius', sirius)

        an_observer = coords.spherical(1, coords.latitude(37, 24), coords.angle(-122, 4, 57))

        a_datetime = coords.datetime('2014-12-31T20:41:00')

        sirius_hz = Transforms.APCTransforms.toHorizon(sirius, an_observer, a_datetime)

        print('sirius hz', sirius_hz)

        # TODO close, but still several minutes difference from USNO results

        self.assertEqual('17:48:06.9', str(coords.angle(90) - sirius_hz.theta))
        self.assertEqual('128:44:20.4', str(sirius_hz.phi))

        sirius_eq = Transforms.APCTransforms.toEquatorial(sirius_hz, an_observer, a_datetime)

        print('sirius eq', sirius_eq) # TODO not inverting correctly,
                                      # ~10 degrees difference in theta and phi

        # TODO validate something
        return


    @unittest.skip('TODO')
    def test_toHorizon_1(self):
        """Test to horizon transform 1"""
        an_object = coords.spherical(1, coords.angle(45), coords.angle(0))
        an_observer = coords.spherical(1, coords.latitude(45), coords.angle(0))
        a_gst_time = coords.datetime('2015-01-01T00:00:00')

        hz_point = Transforms.APCTransforms.toHorizon(an_object, an_observer, a_gst_time)

        self.assertAlmostEqual(90, hz_point.theta.value)
        self.assertAlmostEqual(0, hz_point.phi.value)
        return


    @unittest.skip('TODO')
    def test_toHorizon_2(self):
        """Test to horizon transform 2"""
        an_object = coords.spherical(1, coords.angle(45), coords.angle(90))
        an_observer = coords.spherical(1, coords.latitude(45), coords.angle(0))
        a_gst_time = coords.datetime('2015-01-01T00:00:00')

        hz_point = Transforms.APCTransforms.toHorizon(an_object, an_observer, a_gst_time)

        self.assertAlmostEqual(60, hz_point.theta.value)
        self.assertAlmostEqual(54.735610317245346, hz_point.phi.value)
        return


    @unittest.skip('TODO')
    def test_fromHorizon_1(self):
        """Test from horizon transform 1"""
        an_object = coords.spherical(1, coords.angle(90), coords.angle(0))
        an_observer = coords.spherical(1, coords.latitude(45), coords.angle(0))
        a_gst_time = coords.datetime('2015-01-01T00:00:00')

        hz_point = Transforms.APCTransforms.toEquatorial(an_object, an_observer, a_gst_time)

        self.assertAlmostEqual(45, hz_point.theta.value)
        self.assertAlmostEqual(0, hz_point.phi.value)
        return


if __name__ == '__main__':
    unittest.main()
