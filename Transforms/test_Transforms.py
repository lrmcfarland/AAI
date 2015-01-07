"""Unit tests for Right Ascension, declination, Ecliptic and Equatorial transforms"""

import math
import time
import unittest

import coords
import Transforms

class TestTransforms(unittest.TestCase):
    """Test RA/declination transforms."""

    def setUp(self):
        """Set up test parameters."""

        self.places = 5 # precision limited by LAMBDA-tools reporting
        self.xforms = Transforms.Transforms()


    def test_spherical2latitude_npole(self):
        """Test spherical2latitude north pole"""
        a_point = coords.spherical(1)
        a_latitude = self.xforms.spherical2latitude(a_point)
        self.assertEqual(90, a_latitude)


    def test_spherical2latitude_equator(self):
        """Test spherical2latitude equator"""
        a_point = coords.spherical(1, coords.angle(90))
        a_latitude = self.xforms.spherical2latitude(a_point)
        self.assertEqual(0, a_latitude)


    def test_spherical2latitude_spole(self):
        """Test spherical2latitude south pole"""
        a_point = coords.spherical(1, coords.angle(180))
        a_latitude = self.xforms.spherical2latitude(a_point)
        self.assertEqual(-90, a_latitude)


    def test_spherical2longitude_prime_meridian(self):
        """Test spherical2latitude prime meridian"""
        a_point = coords.spherical(1)
        a_longitude = self.xforms.spherical2longitude(a_point)
        self.assertEqual(0, a_longitude)


    def test_spherical2longitude_dateline(self):
        """Test spherical2latitude date line"""
        a_point = coords.spherical(1, coords.angle(0), coords.angle(180))
        a_longitude = self.xforms.spherical2longitude(a_point)
        self.assertEqual(180, a_longitude)


    def test_spherical2longitude_45_east(self):
        """Test spherical2latitude 45 east"""
        a_point = coords.spherical(1, coords.angle(0), coords.angle(45))
        a_longitude = self.xforms.spherical2longitude(a_point)
        self.assertEqual(45, a_longitude)


    def test_spherical2longitude_45_west(self):
        """Test spherical2latitude 45 west"""
        a_point = coords.spherical(1, coords.angle(0), coords.angle(-45))
        a_longitude = self.xforms.spherical2longitude(a_point)
        self.assertEqual(315, a_longitude)


    def test_spherical2ra_45_east(self):
        """Test spherical2ra 45 east"""
        a_point = coords.spherical(1, coords.angle(0), coords.angle(45))
        a_right_ascension = self.xforms.spherical2ra(a_point)
        self.assertEqual(3, a_right_ascension)


    def test_spherical2ra_45_west(self):
        """Test spherical2ra 45 west"""
        a_point = coords.spherical(1, coords.angle(0), coords.angle(-45))
        a_right_ascension = self.xforms.spherical2ra(a_point)
        self.assertEqual(21, a_right_ascension)


    def test_radec2spherical_1(self):
        """Test RA 1, dec 0"""
        a_point = self.xforms.radec2spherical(a_right_ascension=coords.angle(1),
                                                 a_declination=coords.angle(0))

        self.assertAlmostEqual(90, a_point.theta.value)
        self.assertAlmostEqual(15, a_point.phi.value)
        self.assertAlmostEqual(1, self.xforms.spherical2ra(a_point))


    def test_JulianCentury_2000(self):
        """Test Julian Century 2000"""
        a_datetime = coords.datetime('2000-01-01T12:00:00')
        a_Julian_century = self.xforms.JulianCentury(a_datetime)
        self.assertEqual(0, a_Julian_century)


    def test_JulianCentury_2100(self):
        """Test Julian Century 2100"""
        a_datetime = coords.datetime('2100-01-01T12:00:00')
        a_Julian_century = self.xforms.JulianCentury(a_datetime)
        self.assertEqual(1, a_Julian_century)

    # ----------------------------------------
    # ----- Greenwich Mean Sidereal Time -----
    # ----------------------------------------

    def test_GMST_USNO_J2000(self):
        """Test GMST USNO J2000"""
        a_datetime = coords.datetime(self.xforms.J2000)
        a_gmst = self.xforms.GMST_USNO(a_datetime)

        self.assertEqual('-5:18:9.45159', str(a_gmst))


    def test_GMST_USNO_J2000_plus_day(self):
        """Test GMST USNO J2000 plus a day"""
        a_datetime_0 = coords.datetime(self.xforms.J2000)
        a_gmst_0 = self.xforms.GMST_USNO_simplified(a_datetime_0)
        a_datetime_1 = coords.datetime('2000-01-02T12:00:00')
        a_gmst_1 = self.xforms.GMST_USNO_simplified(a_datetime_1)

        self.assertEqual('00:03:56.5554', str(a_gmst_1 - a_gmst_0))


    def test_GMST_USNO_J2000_plus_halfday(self):
        """Test GMST USNO J2000 plus a halfday"""
        a_datetime_0 = coords.datetime(self.xforms.J2000)
        a_gmst_0 = self.xforms.GMST_USNO_simplified(a_datetime_0)
        a_datetime_1 = coords.datetime('2000-01-02T00:00:00')
        a_gmst_1 = self.xforms.GMST_USNO_simplified(a_datetime_1)

        self.assertEqual('12:01:58.2777', str(a_gmst_1 - a_gmst_0))


    def test_GMST_USNO_standrews(self):
        """Test GMST USNO at St. Andrews"""
        # from http://star-www.st-and.ac.uk/~fv/webnotes/answer6.htm
        a_datetime = coords.datetime('1998-02-04T00:00:00')
        a_gmst = self.xforms.GMST_USNO(a_datetime)

        sta_long = coords.angle(2, 48)
        # TODO is 02:47:60, should be 2:48 but is not rounding 60 seconds up
        self.assertEqual('02:47:60', str(sta_long))

        # TODO this is 11 minutes off from answer6, but 11 minutes from GMT.
        self.assertEqual('08:55:49.7347', str(a_gmst))


    def test_GMST_USNO_kb(self):
        """Test GMST USNO formula, in hours, with kburnett data"""
        # from http://www2.arnes.si/~gljsentvid10/sidereal.htm
        a_datetime = coords.datetime('1994-06-16T18:00:00')
        a_gmst = self.xforms.GMST_USNO(a_datetime)

        # -0.00029 seconds different from given test data.
        # This is higher precision.
        self.assertEqual('11:39:5.06752', str(a_gmst))


    def test_GMST_USNO_8am(self):
        """Test GMST USNO 8 am"""
        a_datetime = coords.datetime('2015-01-01T08:00:00')
        a_gmst = self.xforms.GMST_USNO(a_datetime)

        # TODO validate against something
        self.assertEqual('-9:17:22.0146', str(a_gmst))


    def test_GMST_USNO_2pm(self):
        """Test GMST USNO 2 pm"""
        a_datetime = coords.datetime('2015-01-01T14:00:00')
        a_gmst = self.xforms.GMST_USNO(a_datetime)

        # TODO validate against something
        self.assertEqual('-3:16:22.8758', str(a_gmst))


    def test_GMST_USNO_2pm_tz1(self):
        """Test GMST USNO 2 pm timezone +1"""
        a_datetime = coords.datetime('2015-01-01T14:00:00+0100')
        a_gmst = self.xforms.GMST_USNO(a_datetime)

        # TODO validate against something
        self.assertEqual('-2:16:13.0193', str(a_gmst))


    def test_GMST_USNO_2pm_tzn1(self):
        """Test GMST USNO 2 pm timezone -1"""
        a_datetime = coords.datetime('2015-01-01T14:00:00-01:00')
        a_gmst = self.xforms.GMST_USNO(a_datetime)

        # TODO validate against something
        self.assertEqual('-4:16:32.7323', str(a_gmst))


    def test_GMST_USNO_simplified_J2000(self):
        """Test GMST USNO simplified J2000"""
        a_datetime = coords.datetime(self.xforms.J2000)
        a_gmst = self.xforms.GMST_USNO_simplified(a_datetime)
        self.assertEqual('-5:18:9.45159', str(a_gmst))


    def test_GMST_USNO_simplified_J2000_plus_day(self):
        """Test GMST USNO J2000 plus a day"""
        a_datetime_0 = coords.datetime(self.xforms.J2000)
        a_gmst_0 = self.xforms.GMST_USNO_simplified(a_datetime_0)
        a_datetime_1 = coords.datetime('2000-01-02T12:00:00')
        a_gmst_1 = self.xforms.GMST_USNO_simplified(a_datetime_1)

        self.assertEqual('00:03:56.5554', str(a_gmst_1 - a_gmst_0))


    def test_GMST_USNO_simplified_standrews(self):
        """Test GMST USNO simplified at St. Andrews"""
        # from http://star-www.st-and.ac.uk/~fv/webnotes/answer6.htm
        a_datetime = coords.datetime('1998-02-04T00:00:00')
        a_gmst = self.xforms.GMST_USNO_simplified(a_datetime)

        sta_long = coords.angle(2, 48)
        # TODO is 02:47:60, should be 2:48 but is not rounding 60 seconds up
        self.assertEqual('02:47:60', str(sta_long))

        # TODO this is 11 minutes off from answer6, but 11 minutes from GMT.
        self.assertEqual('08:55:49.7347', str(a_gmst))


    def test_GMST_USNO_simplified_kb(self):
        """Test GMST USNO simplified formula, in hours, with kburnett data"""
        # from http://www2.arnes.si/~gljsentvid10/sidereal.htm
        a_datetime = coords.datetime('1994-06-16T18:00:00')
        a_gmst = self.xforms.GMST_USNO_simplified(a_datetime)

        # -0.00001 seconds different from given test data
        self.assertEqual('11:39:5.06724', str(a_gmst))


    def test_GMST_USNO_simplified2_kb(self):
        """Test GMST USNO simplified formula 2, in degrees, with kburnett data"""
        # from http://www2.arnes.si/~gljsentvid10/sidereal.htm
        a_datetime = coords.datetime('1994-06-16T18:00:00')
        a_gmst = self.xforms.GMST_USNO_simplified2(a_datetime)

        # matches test data given when rouded to 0.0001 places
        self.assertEqual('11:39:5.06723', str(a_gmst))



    def test_GMST_APC_J2000(self):
        """Test GMST APC J2000"""
        a_datetime = coords.datetime(self.xforms.J2000)
        a_gmst = self.xforms.GMST_APC(a_datetime)

        self.assertEqual('06:39:53.4567', str(a_gmst))


    @unittest.skip('TODO')
    def test_GMST_APC_J2000_plus_day(self):
        """Test APC J2000 plus a day"""
        a_datetime_0 = coords.datetime(self.xforms.J2000)
        a_gmst_0 = self.xforms.GMST_APC(a_datetime_0)
        a_datetime_1 = coords.datetime('2000-01-02T12:00:00')
        a_gmst_1 = self.xforms.GMST_APC(a_datetime_1)

        self.assertEqual('00:03:56.5554', str(a_gmst_1 - a_gmst_0))
        self.assertEqual('18:45:47.1038', str(a_gmst_1))


    @unittest.skip('TODO')
    def test_GMST_APC_kb(self):
        """Test GMST APC formula, in degrees, with kburnett data"""
        # from http://www2.arnes.si/~gljsentvid10/sidereal.htm
        a_datetime = coords.datetime('1994-06-16T18:00:00')
        a_gmst = self.xforms.GMST_APC(a_datetime)

        # matches test data given
        self.assertEqual('11:39:5.06724', str(a_gmst))


    @unittest.skip('TODO')
    def test_GMST_APC_standrews(self):
        """Test GMST APC St. Andrews"""
        # from http://star-www.st-and.ac.uk/~fv/webnotes/answer6.htm
        a_datetime = coords.datetime('1998-02-04T00:00:00')
        a_gmst = self.xforms.GMST_APC(a_datetime)

        self.assertEqual('08:55:49.7347', str(a_gmst))


class TestEquitorialHorizon(unittest.TestCase):
    """Test horizon transforms"""

    def setUp(self):
        """Set up test parameters."""

        self.places = 5 # precision limited by LAMBDA-tools reporting
        self.eq2hz_xforms = Transforms.EquitorialHorizon()


    def test_toHorizon_StA_overhead_0(self):
        """Test to horizon transform overhead 0"""
        an_object = self.eq2hz_xforms.radec2spherical(a_right_ascension=coords.angle(1),
                                                      a_declination=coords.angle(10))

        an_observer = coords.spherical(1, coords.latitude(10), coords.angle(15))
        a_datetime = coords.datetime('2000-01-01T17:17:17.33')

        hz_point = self.eq2hz_xforms.toHorizon_StA(an_object, an_observer, a_datetime)


        # TODO validate something


    def test_toHorizon_StA_overhead(self):
        """Test to horizon transform overhead"""
        an_object = self.eq2hz_xforms.radec2spherical(a_right_ascension=coords.angle(3),
                                                      a_declination=coords.angle(40))

        an_observer = coords.spherical(1, coords.latitude(30), coords.angle(40))
        a_datetime = coords.datetime('2000-01-01T17:17:17.33')

        hz_point = self.eq2hz_xforms.toHorizon_StA(an_object, an_observer, a_datetime)


        # TODO validate something



    def test_sirius(self):
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


        sirius = self.eq2hz_xforms.radec2spherical(a_right_ascension=coords.angle(6, 45, 8.9173),
                                                   a_declination=coords.angle(-16, 42, 58.017))

        an_observer = coords.spherical(1, coords.latitude(37, 24), coords.angle(-122, 4, 57))

        a_datetime = coords.datetime('2014-12-31T20:41:00')

        sirius_hz = self.eq2hz_xforms.toHorizon_APC(sirius, an_observer, a_datetime)

        print 'sirius', sirius_hz

        # TODO validate something



    @unittest.skip('TODO')
    def test_toHorizon_APC_1(self):
        """Test APC to horizon transform 1"""
        an_object = coords.spherical(1, coords.angle(45), coords.angle(0))
        an_observer = coords.spherical(1, coords.latitude(45), coords.angle(0))
        a_gst_time = coords.datetime('2015-01-01T00:00:00')

        hz_point = self.eq2hz_xforms.toHorizon_APC(an_object, an_observer, a_gst_time)

        self.assertAlmostEqual(90, hz_point.theta.value)
        self.assertAlmostEqual(0, hz_point.phi.value)


    @unittest.skip('TODO')
    def test_toHorizon_APC_2(self):
        """Test APC to horizon transform 2"""
        an_object = coords.spherical(1, coords.angle(45), coords.angle(90))
        an_observer = coords.spherical(1, coords.latitude(45), coords.angle(0))
        a_gst_time = coords.datetime('2015-01-01T00:00:00')

        hz_point = self.eq2hz_xforms.toHorizon_APC(an_object, an_observer, a_gst_time)

        # TODO validate
        self.assertAlmostEqual(60, hz_point.theta.value)
        self.assertAlmostEqual(54.735610317245346, hz_point.phi.value)


    @unittest.skip('TODO')
    def test_fromHorizon_APC_1(self):
        """Test APC from horizon transform 1"""
        an_object = coords.spherical(1, coords.angle(90), coords.angle(0))
        an_observer = coords.spherical(1, coords.latitude(45), coords.angle(0))
        a_gst_time = coords.datetime('2015-01-01T00:00:00')

        hz_point = self.eq2hz_xforms.fromHorizon_APC(an_object, an_observer, a_gst_time)

        self.assertAlmostEqual(45, hz_point.theta.value)
        self.assertAlmostEqual(0, hz_point.phi.value)




class TestEcEqXforms(unittest.TestCase):
    """Test ecliptic equatorial coordinate transformations

    Validated against http://lambda.gsfc.nasa.gov/toolbox/tb_coordconv.cfm
    """

    def setUp(self):
        """Set up test parameters."""

        self.places = 5 # precision limited by LAMBDA-tools reporting
        self.eceq_xform = Transforms.EclipticEquatorial()

    def getLatitude(self, an_object):
        """Return latitude of point"""
        return Transforms.Transforms.spherical2latitude(an_object)

    def getLongitude(self, an_object):
        """Return longitude of point"""
        return Transforms.Transforms.spherical2longitude(an_object)


    def test_first_point_of_Aries(self):
        """Test J2000 first point of Aries"""

        j2000 = coords.datetime('2000-01-01T00:00:00')
        an_object = coords.spherical(coords.Ux)

        an_object_ec = self.eceq_xform.toEcliptic(an_object, j2000)
        self.assertAlmostEqual(0, self.getLatitude(an_object_ec), self.places)
        self.assertAlmostEqual(0, self.getLongitude(an_object_ec), self.places)

        an_object_eq = self.eceq_xform.toEquatorial(an_object, j2000)
        self.assertAlmostEqual(0, self.getLatitude(an_object_eq), self.places)
        self.assertAlmostEqual(360, self.getLongitude(an_object_eq), self.places)


    def test_North_Pole(self):
        """Test J2000 North Pole"""

        j2000 = coords.datetime('2000-01-01T00:00:00')
        an_object = coords.spherical(1, coords.declination(90), coords.angle(0))

        an_object_ec = self.eceq_xform.toEcliptic(an_object, j2000)
        self.assertAlmostEqual(66.56071, self.getLatitude(an_object_ec), self.places)
        self.assertAlmostEqual(90, self.getLongitude(an_object_ec), self.places)

        an_object_eq = self.eceq_xform.toEquatorial(an_object, j2000)
        self.assertAlmostEqual(66.56071, self.getLatitude(an_object_eq), self.places)
        self.assertAlmostEqual(270.00000, self.getLongitude(an_object_eq), self.places)


    def test_lat_0_long_15(self):
        """Test J2000 Latitude 0, Longitude 15"""

        j2000 = coords.datetime('2000-01-01T00:00:00')
        an_object = coords.spherical(1, coords.declination(0), coords.angle(15))

        an_object_ec = self.eceq_xform.toEcliptic(an_object, j2000)
        self.assertAlmostEqual(-5.90920, self.getLatitude(an_object_ec), self.places)
        self.assertAlmostEqual(13.81162, self.getLongitude(an_object_ec), self.places)

        an_object_eq = self.eceq_xform.toEquatorial(an_object, j2000)
        self.assertAlmostEqual(5.90920, self.getLatitude(an_object_eq), self.places)
        self.assertAlmostEqual(13.81162, self.getLongitude(an_object_eq), self.places)


    def test_lat_0_long_345(self):
        """Test J2000 Latitude 0, Longitude 345"""

        j2000 = coords.datetime('2000-01-01T00:00:00')
        an_object = coords.spherical(1, coords.declination(0), coords.angle(345))

        an_object_ec = self.eceq_xform.toEcliptic(an_object, j2000)
        self.assertAlmostEqual(5.90920, self.getLatitude(an_object_ec), self.places)
        self.assertAlmostEqual(346.18838, self.getLongitude(an_object_ec), self.places)

        an_object_eq = self.eceq_xform.toEquatorial(an_object, j2000)
        self.assertAlmostEqual(-5.90920, self.getLatitude(an_object_eq), self.places)
        self.assertAlmostEqual(346.18838, self.getLongitude(an_object_eq), self.places)


    def test_lat_45_long_100(self):
        """Test J2000 Latitude 45, Longitude 100"""

        j2000 = coords.datetime('2000-01-01T00:00:00')
        an_object = coords.spherical(1, coords.declination(45), coords.angle(100))

        an_object_ec = self.eceq_xform.toEcliptic(an_object, j2000)
        self.assertAlmostEqual(21.82420, self.getLatitude(an_object_ec), self.places)
        self.assertAlmostEqual(97.60065, self.getLongitude(an_object_ec), self.places)

        an_object_eq = self.eceq_xform.toEquatorial(an_object, j2000)
        self.assertAlmostEqual(67.78257, self.getLatitude(an_object_eq), self.places)
        self.assertAlmostEqual(108.94923, self.getLongitude(an_object_eq), self.places)


    def test_lat_n30_long_n30(self):
        """Test J2000 Latitude -30, Longitude -30"""

        j2000 = coords.datetime('2000-01-01T00:00:00')
        an_object = coords.spherical(1, coords.declination(-30), coords.angle(-30))

        an_object_ec = self.eceq_xform.toEcliptic(an_object, j2000)
        self.assertAlmostEqual(-16.64844, self.getLatitude(an_object_ec), self.places)
        self.assertAlmostEqual(321.51905, self.getLongitude(an_object_ec), self.places)

        an_object_eq = self.eceq_xform.toEquatorial(an_object, j2000)
        self.assertAlmostEqual(-39.12273, self.getLatitude(an_object_eq), self.places)
        self.assertAlmostEqual(345.18327, self.getLongitude(an_object_eq), self.places)


    def test_lat_n60_long_200(self):
        """Test J2015 Latitude -60, Longitude 200"""

        j2015 = coords.datetime('2015-01-01T00:00:00')
        an_object = coords.spherical(1, coords.declination(-60), coords.angle(200))

        an_object_ec = self.eceq_xform.toEcliptic(an_object, j2015)
        self.assertAlmostEqual(-46.59844, self.getLatitude(an_object_ec), self.places)
        self.assertAlmostEqual(226.85843, self.getLongitude(an_object_ec), self.places)

        an_object_eq = self.eceq_xform.toEquatorial(an_object, j2015)
        self.assertAlmostEqual(-59.60899, self.getLatitude(an_object_eq), self.places)
        self.assertAlmostEqual(158.23870, self.getLongitude(an_object_eq), self.places)


    def test_lat_20_long_n10(self):
        """Test J2015 Latitude 20, Longitude -10"""

        j2015 = coords.datetime('2015-01-01T00:00:00')
        an_object = coords.spherical(1, coords.declination(20), coords.angle(-10))

        an_object_ec = self.eceq_xform.toEcliptic(an_object, j2015)
        self.assertAlmostEqual(22.25346, self.getLatitude(an_object_ec), self.places)
        self.assertAlmostEqual(359.15333, self.getLongitude(an_object_ec), self.places)

        an_object_eq = self.eceq_xform.toEquatorial(an_object, j2015)
        self.assertAlmostEqual(14.41240, self.getLatitude(an_object_eq), self.places)
        self.assertAlmostEqual(342.84035, self.getLongitude(an_object_eq), self.places)



if __name__ == '__main__':
    unittest.main()
