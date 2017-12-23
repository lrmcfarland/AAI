#!/usr/bin/env python

"""The Astronomical Algorithms Implemented in C++ and Python Web UI using Flask

To run: ./pylaunch.sh aai.py

with rotating logging: ./pylaunch.sh aai.py -l debug --loghandler rotating --logfilename ./logs/aai-flask.log
"""

import argparse
import flask
import logging
import logging.handlers
import re

import coords

import Transforms.EclipticEquatorial
import Transforms.EquatorialHorizon
import Transforms.utils

import Bodies.SunPosition


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


class Error(Exception):
    pass


def request_float(a_float_str):
    """Gets the float of string from the request args

    Args:
        a_float_str (str): float as string

    Returns: the float
    Raises: ValueError if not found
    """

    a_float = flask.request.args.get(a_float_str, type=float)

    app.logger.debug('request float: %s: %s', a_float_str, a_float)

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

    app.logger.debug('request angle: %s: %s', an_angle_key, an_angle_value)

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

    app.logger.debug('datetime: %s', a_datetime)

    return a_datetime


def calculate_sun_position(a_latitude, a_longitude, a_datetime, is_dst):
    """Calculate the sun position.

    Args:
        a_latitude (coords.angle): observer's latitude
        a_longitude (coords.angle): observer's longitude
        a_datetime (coords.datetime): observer's time
        a_dst (bool): daylight savings time


    return results dictionary
    """

    app.logger.debug('calculate sun position lat: %s,  long: %s, datetime: %s',
                     a_latitude, a_longitude, a_datetime)

    result = dict()
    result['latitude'] = str(a_latitude)
    result['longitude'] = str(a_longitude)
    result['datetime'] = str(a_datetime)
    result['dst'] = is_dst

    result['eot'] = str(Bodies.SunPosition.EquationOfTime(a_datetime))
    result['obliquity'] = str(Transforms.EclipticEquatorial.obliquity(a_datetime))

    an_observer = Transforms.utils.latlon2spherical(a_latitude, a_longitude)

    rising, transit, setting = Bodies.SunPosition.SunRiseAndSet(an_observer, a_datetime)

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


    ecliptic_longitude, R = Bodies.SunPosition.SolarLongitude(a_datetime)

    sun_ec = coords.spherical(R, coords.angle(90), ecliptic_longitude)
    sun_eq = Transforms.EclipticEquatorial.toEquatorial(sun_ec, a_datetime)
    sun_hz = Transforms.EquatorialHorizon.toHorizon(sun_eq, an_observer, a_datetime)

    result['dec'] = str(coords.angle(90) - sun_eq.theta)

    result['R'] = R
    result['ecliptic_longitude'] = str(ecliptic_longitude)

    result['azimuth'] = ''.join((str(Transforms.utils.get_azimuth(sun_hz)),
                                 ' (', str(Transforms.utils.get_azimuth(sun_hz).value), ')'))


    result['altitude'] = ''.join((str(Transforms.utils.get_altitude(sun_hz)),
                                  ' (', str(Transforms.utils.get_altitude(sun_hz).value), ')'))


    return result


# ===============
# ===== app =====
# ===============

app = flask.Flask(__name__) # must be before decorators

app.config.from_pyfile('conf/aai-flask.cfg')


@app.route("/")
def home():
    """Application's home"""

    return flask.render_template('home.html')


@app.route("/accuracy")
def accuracy():
    """Accuracy page"""

    return flask.render_template('accuracy.html')

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

        is_dst = True if flask.request.args.get('dst') == 'on' else False

        result = calculate_sun_position(request_angle('latitude'),
                                        request_angle('longitude'),
                                        request_datetime('date',
                                                         'time',
                                                         request_float('timezone'),
                                                         is_dst),
                                        is_dst)

    except (TypeError, ValueError, RuntimeError) as err:

        app.logger.error(err)
        flask.flash(err)
        return flask.render_template('flashes.html')

    return flask.render_template('sun_position_form_out.html', **result)


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

        is_dst = True if flask.request.args.get('dst') == 'true' else False

        result = calculate_sun_position(request_angle('latitude'),
                                        request_angle('longitude'),
                                        request_datetime('date',
                                                         'time',
                                                         request_float('timezone'),
                                                         is_dst),
                                        is_dst)

    except (TypeError, ValueError, RuntimeError) as err:

        app.logger.error(err)
        result = {'error': str(err)}

    return flask.jsonify(**result)

# ---------------------
# ----- sun chart -----
# ---------------------


@app.route("/sun_position_chart")
def sun_position_chart():
    """Plot the sun position for the observer's location in space and time"""

    return flask.render_template('sun_position_chart.html')


@app.route("/api/v1/sun_position_data")
def sun_position_data():
    """Get the sun position chart for the given day as JSON

    for example:

    curl http://0.0.0.0:8080/api/v1/sun_position_data\?latitude=37\&longitude=-122\&date=2017-12-11\&time=14\%3A37\%3A54\&timezone=-8\&dst=false

    result.datetime
          .sun_date_label
          .sun_marker_time
          .sun_marker_altitude
          .sun_marker_azimuth
          .rising
          .transit
          .setting
          .altitude_data_24h[time, current, vernal, summer, autumnal, winter]

    """

    app.logger.info('/api/v1/sun_positon_data: %s', flask.request.args)

    try:

        result = dict()

        an_observer = Transforms.utils.latlon2spherical(request_angle('latitude'),
                                                        request_angle('longitude'))

        result['observer'] = str(an_observer) # TODO format?

        is_dst = True if flask.request.args.get('dst') == 'true' else False

        a_datetime = request_datetime('date',
                                      'time',
                                      request_float('timezone'),
                                      is_dst)

        result['datetime'] = str(a_datetime)

        plot_time_marker = coords.datetime(a_datetime.year, a_datetime.month, a_datetime.day)
        plot_time_marker.timezone = a_datetime.timezone
        plot_time_marker += a_datetime.timezone * 1.0/24 # to center plot at local noon

        result['sun_marker_time'] = 24.0 * (a_datetime - plot_time_marker) # distance on x-axis to plot sun marker

        vernal_equinox = coords.datetime(a_datetime.year, 3, 20) # TODO not every year
        vernal_equinox.timezone = a_datetime.timezone
        vernal_equinox += a_datetime.timezone * 1.0/24 # to center plot at local noon

        summer_solstice = coords.datetime(a_datetime.year, 6, 20) # TODO not every year
        summer_solstice.timezone = a_datetime.timezone
        summer_solstice += a_datetime.timezone * 1.0/24 # to center plot at local noon

        autumnal_equinox = coords.datetime(a_datetime.year, 9, 22) # TODO not every year
        autumnal_equinox.timezone = a_datetime.timezone
        autumnal_equinox += a_datetime.timezone * 1.0/24 # to center plot at local noon

        winter_solstice = coords.datetime(a_datetime.year, 12, 21) # TODO not every year
        winter_solstice.timezone = a_datetime.timezone
        winter_solstice += a_datetime.timezone * 1.0/24 # to center plot at local noon

        result['sun_date_label'] = '{year}-{month}-{day}'.format(year=plot_time_marker.year,
                                                                 month=plot_time_marker.month,
                                                                 day=plot_time_marker.day),
        npts = 24*4

        if is_dst:
            dtime = 1
            result['sun_marker_time'] += 1
        else:
            dtime = 0

        altitude = list()

        for d in range(0, npts + 1):

            sun_ct = Bodies.SunPosition.SunPosition(an_observer, plot_time_marker)
            sun_ve = Bodies.SunPosition.SunPosition(an_observer, vernal_equinox)
            sun_ss = Bodies.SunPosition.SunPosition(an_observer, summer_solstice)
            sun_ae = Bodies.SunPosition.SunPosition(an_observer, autumnal_equinox)
            sun_ws = Bodies.SunPosition.SunPosition(an_observer, winter_solstice)


            altitude.append([dtime,
                             Transforms.utils.get_altitude(sun_ve).value,
                             Transforms.utils.get_altitude(sun_ss).value,
                             Transforms.utils.get_altitude(sun_ae).value,
                             Transforms.utils.get_altitude(sun_ws).value,
                             Transforms.utils.get_altitude(sun_ct).value # needs to be last for sun position marker
                         ]
            )


            dtime += 1.0/npts*24

            plot_time_marker += 1.0/npts
            vernal_equinox += 1.0/npts
            summer_solstice += 1.0/npts
            autumnal_equinox += 1.0/npts
            winter_solstice += 1.0/npts

        result['altitude_data_24h'] = altitude # list

        # get rise, transit, set time
        rts = calculate_sun_position(request_angle('latitude'),
                                     request_angle('longitude'),
                                     request_datetime('date',
                                                      'time',
                                                      request_float('timezone'),
                                                      is_dst),
                                     is_dst)

        result['sun_marker_altitude'] = rts['altitude']
        result['sun_marker_azimuth']  = rts['azimuth']
        result['rising']   = rts['rising']
        result['transit']  = rts['transit']
        result['setting']  = rts['setting']


    except Bodies.SunPosition.Error as err:

        result['sun_marker_altitude'] = str(err)
        result['sun_marker_azimuth']  = str(err)
        result['rising']   = str(err)
        result['transit']  = str(err)
        result['setting']  = str(err)

    except (TypeError, ValueError, RuntimeError) as err:

        app.logger.error(err)
        result = {'error': str(err)}

    return flask.jsonify(**result)



# ----------------------------
# ----- eq hz transforms -----
# ----------------------------


@app.route("/eqhz_transforms")
def eqhz_transforms():
    """Transform equatorial to horizontal coordinates at observer's location in space and time"""

    return flask.render_template('eqhz_transforms.html')


@app.route("/api/v1/radec2azalt")
def radec2azalt():
    """Transform Right Ascension, Declination to Azimuth, Altitude Coordinates"""

    app.logger.info('rdec2azalt: %s', flask.request.args)

    try:

        result = dict()

        an_observer = Transforms.utils.latlon2spherical(request_angle('latitude'),
                                                        request_angle('longitude'))

        result['observer'] = str(an_observer)

        is_dst = True if flask.request.args.get('dst') == 'true' else False

        a_datetime = request_datetime('date',
                                      'time',
                                      request_float('timezone'),
                                      is_dst)

        result['datetime'] = str(a_datetime)

        body_eq = Transforms.utils.radec2spherical(request_angle('ra'), request_angle('dec'))

        body_hz = Transforms.EquatorialHorizon.toHorizon(body_eq, an_observer, a_datetime)

        result['azimuth'] = Transforms.utils.get_azimuth(body_hz).value
        result['altitude'] = Transforms.utils.get_altitude(body_hz).value


    except (TypeError, ValueError, RuntimeError) as err:

        app.logger.error(err)
        result = {'error': str(err)}

    return flask.jsonify(**result)


@app.route("/api/v1/azalt2radec")
def azalt2radec():
    """Transform Azimuth, Altitude to Right Ascension, Declination Coordinates"""

    app.logger.info('azalt2radec: %s', flask.request.args)

    try:

        result = dict()

        an_observer = Transforms.utils.latlon2spherical(request_angle('latitude'),
                                                        request_angle('longitude'))

        result['observer'] = str(an_observer)

        is_dst = True if flask.request.args.get('dst') == 'true' else False

        a_datetime = request_datetime('date',
                                      'time',
                                      request_float('timezone'),
                                      is_dst)

        result['datetime'] = str(a_datetime)


        body_hz = Transforms.utils.azalt2spherical(request_angle('azimuth'), request_angle('altitude'))

        body_eq = Transforms.EquatorialHorizon.toEquatorial(body_hz, an_observer, a_datetime)

        result['ra'] = Transforms.utils.get_RA(body_eq).value
        result['dec'] = Transforms.utils.get_declination(body_eq).value

    except (TypeError, ValueError, RuntimeError) as err:

        app.logger.error(err)
        result = {'error': str(err)}

    return flask.jsonify(**result)


# ================
# ===== main =====
# ================

if __name__ == "__main__":

    """Run stand alone in flask"""


    loglevels = {'debug': logging.DEBUG,
                 'info': logging.INFO,
                 'warn': logging.WARN,
                 'error': logging.ERROR}


    loghandlers = {'stream': 'stream',
                   'rotating': 'rotating'}


    defaults = {'debug': False,
                'host':'0.0.0.0',
                'logfilename': '/opt/starbug.com/logs/flask',
                'loghandler': 'stream',
                'loglevel': 'warn',
                'port': 8080,
    }

    parser = argparse.ArgumentParser(description='vArmour simple flask server')

    parser.add_argument('-d', '--debug', action='store_true',
                        dest='debug', default=defaults['debug'],
                        help='flask debug (default: %(default)s)')

    parser.add_argument('--host', type=str, dest='host', default=defaults['host'],
                        metavar='host',
                        help='host IP to serve (default: %(default)s)')

    parser.add_argument('--logfilename', type=str, dest='logfilename', default=defaults['logfilename'],
                        metavar='logfilename',
                        help='name of log file (default: %(default)s)')

    parser.add_argument('--loghandler', choices=list(loghandlers.keys()),
                        dest='loghandler', default=defaults['loghandler'],
                        metavar='HANDLER',
                        help='logging handler choice: %(keys)s (default: %(default)s)' % {
                            'keys':', '.join(list(loghandlers.keys())), 'default':'%(default)s'})

    parser.add_argument('-l', '--loglevel', choices=list(loglevels.keys()),
                        dest='loglevel', default=defaults['loglevel'],
                        metavar='LEVEL',
                        help='logging level choice: %(keys)s (default: %(default)s)' % {
                            'keys':', '.join(list(loglevels.keys())), 'default':'%(default)s'})

    parser.add_argument('-p', '--port', type=int, dest='port', default=defaults['port'],
                        help='port (default: %(default)s)')

    args = parser.parse_args()

    # ----- set up logging -----

    if args.loghandler == 'stream':

        log_handler = logging.StreamHandler()

    elif args.loghandler == 'rotating':

        log_handler = logging.handlers.RotatingFileHandler(args.logfilename,
                                                           maxBytes=1000000,
                                                           backupCount=10) # TODO from cli

    else:
        parser.error('unsupported log handler %s', args.loghandler)


    log_handler.setFormatter(
        logging.Formatter(
            '[%(asctime)s %(levelname)s %(filename)s %(lineno)s] %(message)s'))


    if app.config['SECRET_KEY'] == 'changeme': # TODO meh
        raise Error('change flask secret key in www/conf/aai-flask.cfg from default')

    app.logger.addHandler(log_handler)
    app.logger.setLevel(loglevels[args.loglevel])



    # -------------------
    # ----- run app -----
    # -------------------

    app.run(host=args.host, port=args.port, debug=args.debug)
