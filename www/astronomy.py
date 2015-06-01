#!/usr/bin/env python

"""The Astronomy Web UI using Flask

To run: ./pylaunch.sh astronomy.py

"""

import flask

import coords

from Transforms import EclipticEquatorial
from Transforms import EquatorialHorizon
from Transforms import SiderealTime
from Transforms import utils

from Bodies import SunPosition


app = flask.Flask(__name__)

@app.route("/")
def home():
    """Application's home"""

    return flask.render_template('home.html')


@app.route("/observer")
def observer():
    """observer's location in space and time"""

    print 'sun position session:', flask.session # TODO rm
    print 'observer request:', flask.request # TODO rm

    flask.session['foo'] = 'bar' # TODO rm

    return flask.render_template('observer.html')


@app.route("/sun_position")
def sun_position():

    print 'sun position session:', flask.session # TODO rm
    print 'sun position request:', flask.request # TODO rm

    # TODO blank is a value error, get with default 0?

    try:
	a_latitude = coords.angle(float(flask.request.values['lat_deg']),
				  float(flask.request.values['lat_min']),
				  float(flask.request.values['lat_sec']))


	a_longitude = coords.angle(float(flask.request.values['lon_deg']),
				   float(flask.request.values['lon_min']),
				   float(flask.request.values['lon_sec']))

	a_datetime = coords.datetime(float(flask.request.values['a_year']),
				     float(flask.request.values['a_month']),
				     float(flask.request.values['a_day']),
				     float(flask.request.values['an_hour']),
				     float(flask.request.values['a_minute']),
				     float(flask.request.values['a_second']),
				     float(flask.request.values['a_timezone']))

	an_observer = utils.latlon2spherical(a_latitude, a_longitude)

        ecliptic_longitude, R = SunPosition.SolarLongitude(a_datetime)

        obliquity = EclipticEquatorial.obliquity(a_datetime)

        sun_ec = coords.spherical(R, coords.angle(90), ecliptic_longitude)
        sun_eq = EclipticEquatorial.toEquatorial(sun_ec, a_datetime)
        sun_hz = EquatorialHorizon.toHorizon(sun_eq, an_observer, a_datetime)

        sun_dec = coords.angle(90) - sun_eq.theta

        eot = SunPosition.EquationOfTime(a_datetime)

        az_str = ''.join((str(utils.get_azimuth(sun_hz)), ' (', str(utils.get_azimuth(sun_hz).value), ')'))

        alt_str = ''.join((str(utils.get_altitude(sun_hz)), ' (', str(utils.get_altitude(sun_hz).value), ')'))

        rising, transit, setting = SunPosition.SunRiseAndSet(an_observer, a_datetime)


    except (ValueError, coords.Error), err:

	app.logger.error(err)
	flask.flash(err)
	return flask.render_template('flashes.html')


    return flask.render_template('position.html',
				 a_latitude=flask.escape(str(a_latitude)),
				 a_longitude=flask.escape(str(a_longitude)),
				 an_observer=flask.escape(str(an_observer)),
				 a_datetime=flask.escape(str(a_datetime)),
                                 an_ecl_long=flask.escape(str(ecliptic_longitude)),
                                 an_r=flask.escape(str(R)),
                                 an_obliquity=flask.escape(str(obliquity)),
                                 a_dec=flask.escape(str(sun_dec)),
                                 an_eot=flask.escape(str(eot)),
                                 an_altitude=flask.escape(str(alt_str)),
                                 an_azimuth=flask.escape(str(az_str)),
                                 a_rising=flask.escape(str(rising)),
                                 a_transit=flask.escape(str(transit)),
                                 a_setting=flask.escape(str(setting))
                             )

# ================
# ===== main =====
# ================

if __name__ == "__main__":

    app.debug = True # TODO Security HOLE!!!

    app.secret_key = 'some key' # TODO more random

    app.run()
