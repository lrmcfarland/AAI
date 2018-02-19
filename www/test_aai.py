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


    def test_radec2azalt_2018_01_11(self):
        """radec2azalt data for 2018 jan 11"""
        response = self.app.get('/api/v1/radec2azalt?latitude=37&longitude=-122&date=2018-01-11&time=10%3A14%3A56&timezone=-8&dst=false&ra=0&dec=0')

        self.assertEqual('200 OK', response.status)
        self.assertEqual(200, response.status_code)

        xform_data = json.loads(response.data)

        self.assertEqual(u'2018-01-11T10:14:56-08', xform_data[u'datetime'])
        self.assertAlmostEqual(-6.159799566504844, xform_data[u'altitude'])
        self.assertAlmostEqual(85.3351397270823, xform_data[u'azimuth'])


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
