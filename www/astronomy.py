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

# ---------------------
# ----- utilities -----
# ---------------------

def get_float(a_key):
    """Get a floating point number from the request

    default to 0 if blank.

    float() raises a ValueError exception if the input string not a
    float.
    """
    if flask.request.values.get(a_key) == '':
        return 0
    else:
        return float(flask.request.values.get(a_key))


def get_string(a_string):
    """Returns the escaped string"""

    return flask.escape(str(a_string))


# ---------------
# ----- app -----
# ---------------

app = flask.Flask(__name__) # must be before decorators

@app.route("/")
def home():
    """Application's home"""

    return flask.render_template('home.html')


@app.route("/get_observer")
def observer():
    """observer's location in space and time"""

    flask.session['foo'] = 'bar' # TODO rm

    return flask.render_template('get_observer.html')


@app.route("/sun_position")
def sun_position():

    try:
        a_latitude = coords.angle(get_float('lat_deg'),
                                  get_float('lat_min'),
                                  get_float('lat_sec'))


        a_longitude = coords.angle(get_float('lon_deg'),
                                   get_float('lon_min'),
                                   get_float('lon_sec'))

        a_datetime = coords.datetime(get_float('a_year'),
                                     get_float('a_month'),
                                     get_float('a_day'),
                                     get_float('an_hour'),
                                     get_float('a_minute'),
                                     get_float('a_second'),
                                     get_float('a_timezone'))

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


    return flask.render_template('sun_position.html',
                                 a_latitude=get_string(a_latitude),
                                 a_longitude=get_string(a_longitude),
                                 an_observer=get_string(an_observer),
                                 a_datetime=get_string(a_datetime),
                                 an_ecl_long=get_string(ecliptic_longitude),
                                 an_r=get_string(R),
                                 an_obliquity=get_string(obliquity),
                                 a_dec=get_string(sun_dec),
                                 an_eot=get_string(eot),
                                 an_altitude=get_string(alt_str),
                                 an_azimuth=get_string(az_str),
                                 a_rising=get_string(rising),
                                 a_transit=get_string(transit),
                                 a_setting=get_string(setting))

# ================
# ===== main =====
# ================

if __name__ == "__main__":

    app.debug = True # TODO Security HOLE!!!

    app.secret_key = 'some key' # TODO more random

    app.run()
