#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests the AAI web interface

This needs location of the coords python wrappers set in pylaunch.sh

to run: ./bin/pylaunch.sh test_aai.py -v


Reference:

http://flask.pocoo.org/docs/0.12/api/#test-client

"""

import json
import unittest

import aai

aai_instance = aai.factory('conf/aai-flask.cfg') # TODO something


class AAITests(unittest.TestCase):

    def setUp(self):
        self.app = aai_instance.test_client()
        self.app.testing = True


    def test_home_page(self):
        """Test home page"""
        response = self.app.get('/')
        self.assertEqual('200 OK', response.status)
        self.assertEqual(200, response.status_code)
        self.assertIn(b'<h1>Astronomical Algorithms Implemented</h1>', response.data)

    # ----------------------
    # ----- transforms -----
    # ----------------------


    # ----- latitude2decimal -----

    def test_latitude2decimal_dms1(self):
        """Test latitude2decimal degrees:minutes:seconds"""

        response = self.app.get('/api/v1/latitude2decimal?latitude=37:30:30')

        self.assertEqual('200 OK', response.status)
        self.assertEqual(200, response.status_code)

        jresp = json.loads(response.data)
        self.assertEqual(0, len(jresp['errors']))
        self.assertAlmostEqual(37.5083333333, float(jresp['latitude']))


    def test_latitude2decimal_d1(self):
        """Test latitude2decimal degrees:minutes:seconds"""

        response = self.app.get('/api/v1/latitude2decimal?latitude=45')

        self.assertEqual('200 OK', response.status)
        self.assertEqual(200, response.status_code)

        jresp = json.loads(response.data)
        self.assertEqual(0, len(jresp['errors']))
        self.assertAlmostEqual(45.0, float(jresp['latitude']))


    def test_latitude2decimal_dm1(self):
        """Test latitude2decimal degrees:minutes:seconds"""

        response = self.app.get('/api/v1/latitude2decimal?latitude=-45:30')

        self.assertEqual('200 OK', response.status)
        self.assertEqual(200, response.status_code)

        jresp = json.loads(response.data)
        self.assertEqual(0, len(jresp['errors']))
        self.assertAlmostEqual(-45.5, float(jresp['latitude']))


    def test_latitude2decimal_err1(self):
        """Test latitude2decimal unsupported format"""

        response = self.app.get('/api/v1/latitude2decimal?latitude=we36asdf')

        self.assertEqual('200 OK', response.status)
        self.assertEqual(200, response.status_code)

        jresp = json.loads(response.data)

        self.assertEqual(1, len(jresp['errors']))
        self.assertEqual(u'unsupported format for latitude: we36asdf', jresp['errors'][0])


    # -----------------------
    # ----- standardize -----
    # -----------------------

    def test_standardize_n1(self):
        """Test standardize normal one"""

        response = self.app.get('/api/v1/standardize?latitude=37:30:45&longitude=-122:45:30&date=2018-01-11&time=10%3A14%3A56.123&timezone=-8&dst=false&ra=6:30:30&dec=10:30:45&az=12:15:30&alt=-6:15')

        self.assertEqual('200 OK', response.status)
        self.assertEqual(200, response.status_code)

        jresp = json.loads(response.data)

        self.assertEqual('2018-01-11T10:14:56.123-08', jresp['params']['iso8601'])
        self.assertAlmostEqual(-6.25, float(jresp['params']['alt']))
        self.assertAlmostEqual(12.2583333333, float(jresp['params']['az']))
        self.assertAlmostEqual(10.5125, float(jresp['params']['dec']))
        self.assertAlmostEqual(37.5125, float(jresp['params']['latitude']))
        self.assertAlmostEqual(-122.758333333, float(jresp['params']['longitude']))
        self.assertAlmostEqual(6.50833333333, float(jresp['params']['ra']))


    def test_standardize_n2(self):
        """Test standardize normal with dst"""

        response = self.app.get('/api/v1/standardize?latitude=37:30&longitude=-122:45:30.1&date=2018-08-21&time=13%3A45&timezone=-8&dst=true&ra=6:30&dec=10&az=12:15:30&alt=6:15')

        self.assertEqual('200 OK', response.status)
        self.assertEqual(200, response.status_code)

        jresp = json.loads(response.data)

        self.assertEqual(u'2018-08-21T12:45:00-08', jresp['params']['iso8601'])
        self.assertAlmostEqual(6.25, float(jresp['params']['alt']))
        self.assertAlmostEqual(12.2583333333, float(jresp['params']['az']))
        self.assertAlmostEqual(10, float(jresp['params']['dec']))
        self.assertAlmostEqual(37.5, float(jresp['params']['latitude']))
        self.assertAlmostEqual(-122.758361111, float(jresp['params']['longitude']))
        self.assertAlmostEqual(6.5, float(jresp['params']['ra']))


    def test_standardize_err1(self):
        """Test standardize error incomplete date time key set"""

        response = self.app.get('/api/v1/standardize?latitude=37:30:45&longitude=-122:45:30&date=2018-01-11&time=10%3A14%3A56')

        self.assertEqual('200 OK', response.status)
        self.assertEqual(200, response.status_code)

        jresp = json.loads(response.data)

        self.assertEqual(1, len(jresp['warnings']))
        self.assertEqual(u'Incomplete datetime key set', jresp['warnings'][0])


    def test_standardize_err2(self):
        """Test standardize unsupported data type"""

        response = self.app.get('/api/v1/standardize?latitude=37:30:45&longitude=-122:45:30&date=2018-01-11&time=10%3A14%3A56&timezone=-8&dst=false&ra=6:30:30&dec=10:30:45&az=12:15:30&alt=-6:15&foo=bar&baz=10')

        self.assertEqual('200 OK', response.status)
        self.assertEqual(200, response.status_code)

        jresp = json.loads(response.data)

        # TODO order from sorted dict ok?
        self.assertEqual(2, len(jresp['warnings']))
        self.assertEqual(u'Unsupported standard type baz: 10', jresp['warnings'][0])
        self.assertEqual(u'Unsupported standard type foo: bar', jresp['warnings'][1])

        self.assertEqual('2018-01-11T10:14:56-08', jresp['params']['iso8601'])
        self.assertAlmostEqual(-6.25, float(jresp['params']['alt']))
        self.assertAlmostEqual(12.2583333333, float(jresp['params']['az']))
        self.assertAlmostEqual(10.5125, float(jresp['params']['dec']))
        self.assertAlmostEqual(37.5125, float(jresp['params']['latitude']))
        self.assertAlmostEqual(-122.758333333, float(jresp['params']['longitude']))
        self.assertAlmostEqual(6.50833333333, float(jresp['params']['ra']))


    def test_standardize_err3(self):
        """Test standardize multiple format errors"""

        response = self.app.get('/api/v1/standardize?latitude=37&longitude=-122:45&date=2018-07-11&time=10%3A30&timezone=-8&dst=true&ra=-6:15&dec=***10:30:45&az=str12:15:30&alt=asdf-6:15')

        self.assertEqual('200 OK', response.status)
        self.assertEqual(200, response.status_code)

        jresp = json.loads(response.data)

        # TODO order from sorted dict ok?
        self.assertEqual(3, len(jresp['errors']))
        self.assertEqual(u'unsupported format for alt: asdf-6:15', jresp['errors'][0])
        self.assertEqual(u'unsupported format for az: str12:15:30', jresp['errors'][1])
        self.assertEqual(u'unsupported format for dec: ***10:30:45', jresp['errors'][2])

        self.assertEqual(u'2018-07-11T09:30:00-08', jresp['params']['iso8601'])

        self.assertAlmostEqual(37, float(jresp['params']['latitude']))
        self.assertAlmostEqual(-122.75, float(jresp['params']['longitude']))
        self.assertAlmostEqual(-6.25, float(jresp['params']['ra']))


    # ----- radec2azalt -----


    def test_radec2azalt_2018_01_11(self):
        """radec2azalt data for 2018 jan 11"""
        response = self.app.get('/api/v1/radec2azalt?latitude=37&longitude=-122&date=2018-01-11&time=10%3A14%3A56&timezone=-8&dst=false&ra=0&dec=0')

        self.assertEqual('200 OK', response.status)
        self.assertEqual(200, response.status_code)

        xform_data = json.loads(response.data)

        self.assertEqual(u'2018-01-11T10:14:56-08', xform_data[u'datetime'])
        self.assertAlmostEqual(-6.159799566504844, xform_data[u'altitude'])
        self.assertAlmostEqual(85.3351397270823, xform_data[u'azimuth'])


    # ----- azalt2radec -----

    def test_azalt2radec_2018_01_11(self):
        """azalt2radec data for 2018 jan 11"""
        response = self.app.get('/api/v1/azalt2radec?latitude=37&longitude=-122&date=2018-01-11&time=10%3A14%3A56&timezone=-8&dst=false&azimuth=85.3351397270823&altitude=-6.159799566504844')

        self.assertEqual('200 OK', response.status)
        self.assertEqual(200, response.status_code)

        xform_data = json.loads(response.data)

        self.assertEqual(u'2018-01-11T10:14:56-08', xform_data[u'datetime'])
        self.assertAlmostEqual(0, xform_data[u'ra'])
        self.assertAlmostEqual(0, xform_data[u'dec'])



    # --------------------------------
    # ----- daily solar altitude -----
    # --------------------------------

    def test_daily_solar_altitude_404mlc_2017_12_11(self):
        """sun daily solar altitude for 2017 dec 11"""
        response = self.app.get('/api/v1/daily_solar_altitude?latitude=37&longitude=-122&date=2017-12-11&time=14%3A37%3A54&timezone=-8&dst=false')
        self.assertEqual('200 OK', response.status)
        self.assertEqual(200, response.status_code)

        position_data = json.loads(response.data)

        self.assertEqual(u'218:05:11.8683 (218.086630087)', position_data[u'sun_marker_azimuth'])

        self.assertAlmostEqual(14.616666666666667, position_data[u'sun_marker_time'])


    def test_daily_solar_altitude_404mlc_2018_01_03(self):
        """sun daily solar altitude for 2018 jan 03"""
        response = self.app.get('/api/v1/daily_solar_altitude?latitude=37&longitude=-122&date=2018-01-03&time=14%3A37%3A54&timezone=-8&dst=false')
        self.assertEqual('200 OK', response.status)
        self.assertEqual(200, response.status_code)

        position_data = json.loads(response.data)

        self.assertAlmostEqual(14.616666666666667, position_data[u'sun_marker_time'])


    def test_daily_solar_altitude_404mlc_2018_02_03(self):
        """sun daily solar altitude for 2018 feb 03

        this had a problem with the sun marker time calculation that caused it to be > 24 hrs
        """
        response = self.app.get('/api/v1/daily_solar_altitude?latitude=37&longitude=-122&date=2018-02-03&time=14%3A37%3A54&timezone=-8&dst=false')
        self.assertEqual('200 OK', response.status)
        self.assertEqual(200, response.status_code)

        position_data = json.loads(response.data)

        self.assertAlmostEqual(14.616666666666667, position_data[u'sun_marker_time'])


    def test_daily_solar_altitude_404mlc_2018_03_03(self):
        """sun daily solar altitude for 2018 mar 03"""
        response = self.app.get('/api/v1/daily_solar_altitude?latitude=37&longitude=-122&date=2018-03-03&time=14%3A37%3A54&timezone=-8&dst=false')
        self.assertEqual('200 OK', response.status)
        self.assertEqual(200, response.status_code)

        position_data = json.loads(response.data)

        self.assertAlmostEqual(14.616666666666667, position_data[u'sun_marker_time'])


    def test_daily_solar_altitude_below_horizon(self):
        """test error object below horizon"""
        response = self.app.get('/api/v1/daily_solar_altitude?latitude=97&longitude=-122&date=2018-02-19&time=11%3A24%3A35&timezone=-8&dst=false')

        self.assertEqual('200 OK', response.status)
        self.assertEqual(200, response.status_code)

        position_data = json.loads(response.data)

        self.assertEqual(u'object is below the horizon from this observation point', position_data[u'sun_marker_azimuth'])



    def test_daily_solar_altitude_bad_longitude(self):
        """test error object below horizon"""
        response = self.app.get('/api/v1/daily_solar_altitude?latitude=badlongitude&longitude=-122asdf&date=2018-02-19&time=11%3A24%3A35&timezone=-8&dst=false')

        self.assertEqual('200 OK', response.status)
        self.assertEqual(200, response.status_code)

        position_data = json.loads(response.data)

        self.assertEqual(1, len(position_data['errors']))
        self.assertEqual(u'unsupported format for latitude: badlongitude', position_data[u'errors'][0])


    def test_daily_solar_altitude_incomplete_parameters(self):
        """test error object below horizon"""
        response = self.app.get('/api/v1/daily_solar_altitude?latitude=37')

        self.assertEqual('200 OK', response.status)
        self.assertEqual(200, response.status_code)

        position_data = json.loads(response.data)

        self.assertEqual(1, len(position_data['errors']))
        self.assertEqual(u'expected string or buffer', position_data[u'errors'][0])



if __name__ == '__main__':
    unittest.main()
