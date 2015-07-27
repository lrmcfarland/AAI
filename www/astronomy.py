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


def split_date(a_datepicker_string):
    """Splits the datepicker string

    ASSUMES format ISO8601
    Returns a list of year, month, day
    """
    val = flask.request.values.get(a_datepicker_string)
    return val.split('-')


def split_angle(an_angle_string):
    """Splits an angle string of deg:min:sec

    TODO: validate string here?

    Returns a list of deg, min, sec
    """
    val = flask.request.values.get(an_angle_string)
    return val.split(':')


# ---------------
# ----- app -----
# ---------------

app = flask.Flask(__name__) # must be before decorators

@app.route("/")
def home():
    """Application's home"""

    return flask.render_template('home.html')


@app.route("/observer")
def observer():
    """observer's location in space and time"""

    flask.session['foo'] = 'bar' # how to set a session variable. TODO rm

    return flask.render_template('observer.html')


@app.route("/sun_position")
def sun_position():

    try:

        dms = split_angle('obs_latitude')
        a_latitude = coords.angle(float(dms[0]),
                                  float(dms[1]),
                                  float(dms[2]))


        dms = split_angle('obs_longitude')
        a_longitude = coords.angle(float(dms[0]),
                                   float(dms[1]),
                                   float(dms[2]))


        ymd = split_date('obs_date')
        hms = split_angle('obs_time')
        a_datetime = coords.datetime(float(ymd[0]),
                                     float(ymd[1]),
                                     float(ymd[2]),
                                     float(hms[0]),
                                     float(hms[1]),
                                     float(hms[2]),
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
