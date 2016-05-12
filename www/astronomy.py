#!/usr/bin/env python

"""The Astronomy Web UI using Flask

To run: ./pylaunch.sh astronomy.py

see README for running on apache with mod_wsgi

Notes:


"""

import flask
import re

import coords

from Transforms import EclipticEquatorial
from Transforms import EquatorialHorizon
from Transforms import SiderealTime
from Transforms import utils

from Bodies import SunPosition


# ----- module scope -----

dms_re = re.compile(r'(?P<degrees>[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?)'
                      '((:(?P<minutes>[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?))?)'
                       '(:(?P<seconds>[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?))?')

# TODO re.VERBOSE
# TODO stricter formatting 12:3x4:45 passes

# works for 10, 1:23, 12:23:45

# TODO limit range to 24 hrs., 60 minutes and seconds. missing lower parts
# TODO utf-8 degrees


# ---------------------
# ----- utilities -----
# ---------------------

def request_float(a_float_str):
    """Gets the float of string from the request args

    Returns: the float
    Raises: ValueError if not found
    """

    a_float = flask.request.args.get(a_float_str, type=float)

    if a_float is None:
        raise ValueError('{a_float_str} is not a float: {a_value}'.format(
            a_float_str=a_float_str, a_value=flask.request.args.get(a_float_str)))

    return a_float


def safe_get_float(a_match, a_key):
    """Safe get float

    Args:
    a_match (re.match result dictonary): regex with named groups
    a_float_key (str): value to get

    Returns 0 if not found
    Raises error if not float-able
    """

    a_val = a_match.groupdict()[a_key]

    if a_val is None:
        return 0
    else:
        return float(a_val)


def request_angle(an_angle_key):
    """Gets the degree minute second values from the request args

    Arg:
    an_angle_key (str): one of deg, deg:min, deg:min:sec

    Returns: coords.angle
    Raises: value exception on format error
    """

    an_angle_value = flask.request.args.get(an_angle_key)

    app.logger.debug('request angle: {an_angle_key}: {an_angle_value}'.format(**locals()))

    found_dms = dms_re.match(an_angle_value)

    if not found_dms:
        raise ValueError(
            'unsupported format for {an_angle_key}: {an_angle_value}'.format(**locals()))

    degrees = safe_get_float(found_dms, 'degrees')
    minutes = safe_get_float(found_dms, 'minutes')
    seconds = safe_get_float(found_dms, 'seconds')

    return coords.angle(degrees, minutes, seconds)


def request_datetime(a_date_key, a_time_key, a_timezone, is_dst):
    """Gets the degree minute second values from the request args

    Arg:
    a_date_key (str): yyyy-mm-dd
    a_time_key (str): hr:min:sec
    a_timezone (float): -12 to 12
    is_dst (bool): daylight savings time

    Returns: coords.datetime
    Raises: value exception on format error
    """

    app.logger.debug('request date: {a_date_key} {a_time_key} {a_timezone} {is_dst}'.format(
        **locals()))

    # TODO regex validation

    ymd = flask.request.args.get(a_date_key).split('-') # ASSUMES: yyyy-mm-dd format

    hms = flask.request.args.get(a_time_key).split(':') # ASSUMES: hh:mm:ss.ss
    while len(hms) < 3:
        hms.append('0')

    a_datetime = coords.datetime(int(ymd[0]),
                                 int(ymd[1]),
                                 int(ymd[2]),
                                 int(hms[0]),
                                 int(hms[1]),
                                 float(hms[2]),
                                 a_timezone)
    if is_dst:
        a_datetime -= 1.0/24

    return a_datetime


def calculate_sun_position(a_latitude, a_longitude, a_datetime, is_dst):
    """Calculate the sun position.

    Notes:
    app.logger.debug('datetime: {a_datetime}'.format(**locals())) # TODO rm


    Args:
    a_latitude (coords.angle): observer's latitude
    a_longitude (coords.angle): observer's longitude
    a_datetime (coords.datetime): observer's time
    a_dst (bool): daylight savings time


    return results dictionary
    """

    result = dict()
    result['latitude'] = str(a_latitude)
    result['longitude'] = str(a_longitude)
    result['datetime'] = str(a_datetime)
    result['dst'] = is_dst

    result['eot'] = str(SunPosition.EquationOfTime(a_datetime))
    result['obliquity'] = str(EclipticEquatorial.obliquity(a_datetime))

    an_observer = utils.latlon2spherical(a_latitude, a_longitude)

    rising, transit, setting = SunPosition.SunRiseAndSet(an_observer, a_datetime)

    if is_dst:

        rising = coords.datetime(rising.year,
                                 rising.month,
                                 rising.day,
                                 rising.hour + 1,
                                 rising.minute,
                                 rising.second,
                                 rising.timezone)

        transit = coords.datetime(transit.year,
                                  transit.month,
                                  transit.day,
                                  transit.hour + 1,
                                  transit.minute,
                                  transit.second,
                                  transit.timezone)

        setting = coords.datetime(setting.year,
                                  setting.month,
                                  setting.day,
                                  setting.hour + 1,
                                  setting.minute,
                                  setting.second,
                                  setting.timezone)


    result['rising'] = str(rising)
    result['transit'] = str(transit)
    result['setting'] = str(setting)


    ecliptic_longitude, R = SunPosition.SolarLongitude(a_datetime)

    sun_ec = coords.spherical(R, coords.angle(90), ecliptic_longitude)
    sun_eq = EclipticEquatorial.toEquatorial(sun_ec, a_datetime)
    sun_hz = EquatorialHorizon.toHorizon(sun_eq, an_observer, a_datetime)

    result['dec'] = str(coords.angle(90) - sun_eq.theta)

    result['R'] = R
    result['ecliptic_longitude'] = str(ecliptic_longitude)

    result['azimuth'] = ''.join((str(utils.get_azimuth(sun_hz)),
                                 ' (', str(utils.get_azimuth(sun_hz).value), ')'))


    result['altitude'] = ''.join((str(utils.get_altitude(sun_hz)),
                                  ' (', str(utils.get_altitude(sun_hz).value), ')'))


    return result


# ===============
# ===== app =====
# ===============

app = flask.Flask(__name__) # must be before decorators

app.secret_key = 'seti2001' # TODO more random


@app.route("/")
def home():
    """Application's home"""

    return flask.render_template('home.html')

# -----------------------------
# ----- sun position ajax -----
# -----------------------------

@app.route("/sun_position_ajax")
def sun_position_ajax():
    """Use AJAX to send observer's location to the server"""

    flask.session['foo'] = 'bar' # how to set a session variable. TODO rm

    return flask.render_template('sun_position_ajax.html')


@app.route("/get_sun_position_ajax")
def get_sun_position_ajax():
    """Get sun position

    This was written to handle a JQuery AJAX call to connect a button
    click event to send a get request with parameters for:

    latitude, longitude, date, time timezone, dst

    The server does calculation and return the sun position data as a
    JSON object.

    If there is an exception, this returns an error key with the
    message as the value in the same JSON object. The caller is
    expected to handle it as they see fit.

    """

    try:

        # input :checked selector returns 'true' and 'false'
        # val() is 'no' or None
        is_dst = True if flask.request.args.get('dst') == 'true' else False

        result = calculate_sun_position(request_angle('latitude'),
                                        request_angle('longitude'),
                                        request_datetime('date',
                                                         'time',
                                                         request_float('timezone'),
                                                         is_dst),
                                        is_dst)

    except (ValueError, RuntimeError) as err:

        app.logger.error(err)
        result = {'error': str(err)}

    return flask.jsonify(**result)

# ------------------------------
# ----- sun position forms -----
# ------------------------------

@app.route("/sun_position_form_in")
def sun_position_form_in():
    """A form for submitting an observer's location in space and time"""

    return flask.render_template('sun_position_form_in.html')


@app.route("/get_sun_position_form")
def get_sun_position_form():
    """Get the sun position for the form example.

    This uses a html form to provide the input with the name to connect the

        <input type=text name=of_latitude>

    via flask

        val = flask.request.values.get('latitude')

    And returns a page of results:

        flask.render_template('sun_position.html', a_latitude = my_latitude, et. al)

    """

    try:

        # input :checked selector returns 'true' and 'false'
        # val() is 'no' or None
        is_dst = True if flask.request.args.get('dst') == 'on' else False

        result = calculate_sun_position(request_angle('latitude'),
                                        request_angle('longitude'),
                                        request_datetime('date',
                                                         'time',
                                                         request_float('timezone'),
                                                         is_dst),
                                        is_dst)

    except (ValueError, RuntimeError) as err:

        app.logger.error(err)
        flask.flash(err)
        return flask.render_template('flashes.html')

    return flask.render_template('sun_position_form_out.html', **result)


# ---------------------
# ----- sun chart -----
# ---------------------


@app.route("/sun_chart")
def sun_chart():
    """Plot the sun position for the observer's location in space and time"""

    return flask.render_template('sun_chart.html')


@app.route("/get_sun_position_chart")
def sun_position_chart():
    """Get the sun position chart for the given day"""

    try:

        result = dict()

        an_observer = utils.latlon2spherical(request_angle('latitude'),
                                             request_angle('longitude'))

        result['observer'] = str(an_observer) # TODO format?

        is_dst = True if flask.request.args.get('dst') == 'true' else False

        a_datetime = request_datetime('date',
                                      'time',
                                      request_float('timezone'),
                                      is_dst)

        result['datetime'] = str(a_datetime)

        JD, JDo = SiderealTime.USNO_C163.JulianDate0(a_datetime)

        current_time = coords.datetime()
        current_time.fromJulianDate(JDo) # the last midnight of the current datetime
        current_time.timezone = a_datetime.timezone

        current_time += a_datetime.timezone * 1.0/24 # to center plot at noon

        sun_position = list()

        sun_position.append(['time', 'altitude'])


        npts = 24*4

        for d in range(0, npts):

            sun = SunPosition.SunPosition(an_observer, current_time)

            # TODO sun_position.append([current_time.toJulianDate(), utils.get_altitude(sun).value])

            if is_dst:
                dtime = current_time.hour + 1 + current_time.minute/60.0
            else:
                dtime = current_time.hour + current_time.minute/60.0

            sun_position.append([dtime, utils.get_altitude(sun).value])

            print current_time, dtime,  utils.get_altitude(sun).value # TODO rm

            current_time += 1.0/npts


        result['position'] = sun_position



    except (ValueError, RuntimeError) as err:

        app.logger.error(err)
        result = {'error': str(err)}

    return flask.jsonify(**result)



# ================
# ===== main =====
# ================

if __name__ == "__main__":

    """Run stand alone in flask"""

    # TODO argparse host, port, log level

    # when all else fails:  app.debug = True # TODO Security HOLE!!!

    app.run(host='0.0.0.0', port=5000, debug=True)
