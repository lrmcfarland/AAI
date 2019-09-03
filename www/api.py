#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""AAI API

    azalt2radec

    radec2azalt

    daily_solar_altitude

    curl http://0.0.0.0:8080/api/v1/daily_solar_altitude\?latitude=37\&longitude=-122\&date=2017-12-11\&time=14\%3A37\%3A54\&timezone=-8\&dst=false



TODO more details

"""

import flask

import coords
import re
import utils

import Bodies.MoonPosition
import Bodies.SunPosition
import Transforms.EclipticEquatorial
import Transforms.EquatorialHorizon
import Transforms.utils

# -------------------
# ----- globals -----
# -------------------

api = flask.Blueprint('api', __name__, url_prefix='/api/v1')

# ----------------------
# ----- transforms -----
# ----------------------


@api.route("/dms2dec")
def dms2dec():

    """Converts a string of deg[:min[:sec]] to decimal degrees

    Returns: JSON
        result.degrees
        result.errors = list()
    """
    result = {'errors': list()}
    try:
        dms = utils.request_angle('dms', flask.request)
        result['dec'] = str(dms.getDegrees())
    except (utils.Error, TypeError, ValueError, RuntimeError) as err:
        result['errors'].append(str(err))

    return flask.jsonify(**result)


@api.route("/dec2dms")
def dec2dms():

    """Converts decimal degrees into a string of deg[:min[:sec]]

    Returns: JSON
        result.degrees
        result.errors = list()
    """
    result = {'errors': list()}
    try:
        dec = utils.request_angle('dec', flask.request)
        result['dms'] = str(dec)
    except (utils.Error, TypeError, ValueError, RuntimeError) as err:
        result['errors'].append(str(err))

    return flask.jsonify(**result)


@api.route("/standardize")
def standardize():

    """Converts parameters from starbug format strings to standard format

    for example: deg[:min[:sec]] string into a float of degrees

    intended for use with a database

    warns if it is not an expected paramter
    error if the format is wrong

    TODO hardcoded keys

    Returns: JSON

        result.alt et. al
        ...

        result.errors = list()
        result.warnings = list()

    """

    result = {'params': dict(), 'errors': list(), 'warnings': list()}

    # ----- datetime stuff -----
    std_datetime = None

    if 'time' in flask.request.args and \
       'date' in flask.request.args and \
       'timezone' in flask.request.args and \
       'dst' in flask.request.args:

        try:

            std_datetime = utils.request_datetime('date', 'time', 'timezone', 'dst', flask.request)
            result['params']['iso8601'] = str(std_datetime)

        except (utils.Error, TypeError, KeyError, ValueError, RuntimeError) as err:
            result['errors'].append(str(err))

    else:
        result['warnings'].append('Incomplete datetime key set')

    # ----- azalt stuff -----
    if 'azalt' in flask.request.args and flask.request.args['azalt'] == 'true':

        if std_datetime is not None and \
           'az' in flask.request.args and \
           'alt' in flask.request.args and \
           'latitude' in flask.request.args and \
           'longitude' in flask.request.args:

            try:
                an_observer = Transforms.utils.latlon2spherical(
                    utils.request_angle('latitude', flask.request),
                    utils.request_angle('longitude', flask.request))

                body_hz = Transforms.utils.azalt2spherical(utils.request_angle('az', flask.request),
                                                           utils.request_angle('alt', flask.request))

                body_eq = Transforms.EquatorialHorizon.toEquatorial(body_hz, an_observer, std_datetime)

                result['params']['ra'] = Transforms.utils.get_RA(body_eq).degrees # TODO use angle.RA
                result['params']['dec'] = Transforms.utils.get_declination(body_eq).degrees # TODO use angle.RA

            except (utils.Error, TypeError, KeyError, ValueError, AttributeError) as err:
                result['errors'].append(str(err))

        else:
            result['errors'].append('Incomplete az alt key set')


    # non-datetime stuff
    # TODO ra dec overwritten if azalt is true ok?
    for key, val in sorted(flask.request.args.items()):

        try:

            if key in ('alt', 'az', 'dec', 'latitude', 'longitude', 'ra'):

                if val == '':
                    continue

                std_val = utils.request_angle(key, flask.request)
                result['params'][key] = str(std_val.getDegrees())

            elif key in ('azalt', 'date', 'dst', 'notes', 'observer', 'target', 'time', 'timezone'):
                pass

            else:
                result['warnings'].append('Unsupported standard type {}: {}'.format(key, val))

        except (utils.Error, TypeError, ValueError, RuntimeError) as err:
            result['errors'].append(str(err))
            continue

    return flask.jsonify(**result)


@api.route("/azalt2radec")
def azalt2radec():
    """Transform Azimuth, Altitude to Right Ascension, Declination Coordinates"""

    result = {'errors': list()}

    try:

        an_observer = Transforms.utils.latlon2spherical(utils.request_angle('latitude', flask.request),
                                                        utils.request_angle('longitude', flask.request))

        result['observer'] = str(an_observer)

        a_datetime = utils.request_datetime('date','time', 'timezone','dst', flask.request)

        result['datetime'] = str(a_datetime)


        body_hz = Transforms.utils.azalt2spherical(utils.request_angle('azimuth', flask.request),
                                                   utils.request_angle('altitude', flask.request))

        body_eq = Transforms.EquatorialHorizon.toEquatorial(body_hz, an_observer, a_datetime)

        result['ra'] = Transforms.utils.get_RA(body_eq).degrees
        result['dec'] = Transforms.utils.get_declination(body_eq).degrees

    except (TypeError, ValueError, RuntimeError, utils.Error) as err:
        result['errors'].append(str(err))

    return flask.jsonify(**result)


@api.route("/radec2azalt")
def radec2azalt():
    """Transform Right Ascension, Declination to Azimuth, Altitude Coordinates"""

    result = {'errors': list()}

    try:
        an_observer = Transforms.utils.latlon2spherical(utils.request_angle('latitude', flask.request),
                                                        utils.request_angle('longitude', flask.request))

        result['observer'] = str(an_observer)

        is_dst = True if flask.request.args.get('dst') == 'true' else False

        a_datetime = utils.request_datetime('date','time', 'timezone','dst', flask.request)

        result['datetime'] = str(a_datetime)

        body_eq = Transforms.utils.radec2spherical(utils.request_angle('ra', flask.request),
                                                   utils.request_angle('dec', flask.request))

        body_hz = Transforms.EquatorialHorizon.toHorizon(body_eq, an_observer, a_datetime)

        result['azimuth'] = Transforms.utils.get_azimuth(body_hz).degrees
        result['altitude'] = Transforms.utils.get_altitude(body_hz).degrees


    except (TypeError, ValueError, RuntimeError, utils.Error) as err:
        result['errors'].append(str(err))

    return flask.jsonify(**result)



# -----------------------------
# ----- sun position data -----
# -----------------------------

@api.route("/solar/ecliptic_coords")
def solar_ecliptic_coords():
    """Calculate the azimuth and altitude of the sun for an observer at a_datetime"""

    result = {'errors': list()}

    try:

        is_dst = True if flask.request.args.get('dst') == 'true' else False
        a_datetime = utils.request_datetime('date','time', 'timezone','dst', flask.request)
        result['datetime'] = str(a_datetime)

        sun_ec = Bodies.SunPosition.EclipticCoords(a_datetime)

        result['longitude'] = str(Transforms.utils.get_longitude(sun_ec).degrees)
        result['latitude'] =  str(Transforms.utils.get_latitude(sun_ec).degrees)

    except (TypeError, ValueError, RuntimeError, utils.Error) as err:
        result['errors'].append(str(err))

    return flask.jsonify(**result)



@api.route("/solar/equatorial_coords")
def solar_equatorial_coords(an_observer, a_datetime):
    """Calculate the azimuth and altitude of the sun for an observer at a_datetime"""

    result = {'errors': list()}

    try:

        is_dst = True if flask.request.args.get('dst') == 'true' else False
        a_datetime = utils.request_datetime('date','time', 'timezone','dst', flask.request)
        result['datetime'] = str(a_datetime)

        sun_eq = Bodies.SunPosition.EquatorialCoords(a_datetime)

        result['declination'] = str(Transforms.utils.get_declination(sun_eq).degrees)
        result['RA'] = str(Transforms.utils.get_RA(sun_eq).degrees)

    except (TypeError, ValueError, RuntimeError, utils.Error) as err:
        result['errors'].append(str(err))

    return flask.jsonify(**result)


@api.route("/solar/horizontal_coords")
def solar_horizontal_coords(an_observer, a_datetime):
    """Calculate the azimuth and altitude of the sun for an observer at a_datetime

    Args:
        an_observer (coords.spherical): an observer locatioin
        a_datetime (coords.datetime): time of obsevation
    """
    result = {'errors': list()}

    try:
        an_observer = Transforms.utils.latlon2spherical(utils.request_angle('latitude', flask.request),
                                                        utils.request_angle('longitude', flask.request))
        result['observer'] = str(an_observer)

        is_dst = True if flask.request.args.get('dst') == 'true' else False
        a_datetime = utils.request_datetime('date','time', 'timezone','dst', flask.request)
        result['datetime'] = str(a_datetime)

        sun_eq = Bodies.SunPosition.HorizontalCoords(an_observer, a_datetime)

        result['azimuth'] = str(Transforms.utils.get_azimuth(sun_hz).degrees)
        result['altitude'] = str(Transforms.utils.get_altitude(sun_hz).degrees)

    except (TypeError, ValueError, RuntimeError, utils.Error) as err:
        result['errors'].append(str(err))

    return flask.jsonify(**result)



# --------------------------------
# ----- solar daily altitude -----
# --------------------------------

@api.route("/solar_daily_altitude")
def solar_daily_altitude():
    """Get the sun position chart for the given day as JSON

    result.datetime
          .date_label
          .sun_marker_time
          .sun_marker_altitude
          .sun_marker_azimuth
          .rising
          .transit
          .setting
          .altitude_data_24h[time, current, vernal, summer, autumnal, winter]

    """

    result = {'errors': list()}

    try:

        an_observer = Transforms.utils.latlon2spherical(utils.request_angle('latitude', flask.request),
                                                        utils.request_angle('longitude', flask.request))

        result['observer'] = str(an_observer) # TODO format? XML from c++ operator::<<()
        result['latitude'] = utils.request_angle('latitude', flask.request).degrees
        result['longitude'] = utils.request_angle('longitude', flask.request).degrees

        a_datetime = utils.request_datetime('date','time', 'timezone','dst', flask.request)

        result['datetime'] = str(a_datetime)

        result['current_date'] = '{}-{:02}-{:02}'.format(a_datetime.year, a_datetime.month, a_datetime.day)
        result['current_time'] = '{:02}:{:02}:{:05.2f}'.format(a_datetime.hour, a_datetime.minute, a_datetime.second)
        result['current_timezone'] = '{}'.format(a_datetime.timezone)

        result['sun_marker_time'] = a_datetime.hour + a_datetime.minute/60.0 # distance on x-axis to plot sun marker

        vernal_equinox = coords.datetime(a_datetime.year, 3, 20)
        vernal_equinox.timezone = a_datetime.timezone
        vernal_equinox += a_datetime.timezone * 1.0/24 # to center plot at local noon

        summer_solstice = coords.datetime(a_datetime.year, 6, 20)
        summer_solstice.timezone = a_datetime.timezone
        summer_solstice += a_datetime.timezone * 1.0/24 # to center plot at local noon

        autumnal_equinox = coords.datetime(a_datetime.year, 9, 22)
        autumnal_equinox.timezone = a_datetime.timezone
        autumnal_equinox += a_datetime.timezone * 1.0/24 # to center plot at local noon

        winter_solstice = coords.datetime(a_datetime.year, 12, 21)
        winter_solstice.timezone = a_datetime.timezone
        winter_solstice += a_datetime.timezone * 1.0/24 # to center plot at local noon

        result['date_label'] = '{year}-{month}-{day}'.format(year=a_datetime.year,
                                                             month=a_datetime.month,
                                                             day=a_datetime.day),
        npts = 24*4

        is_dst = True if flask.request.args.get('dst') == 'true' else False

        if is_dst:
            dtime = 1
            result['sun_marker_time'] += 1
        else:
            dtime = 0

        altitude = list()

        current_time = coords.datetime(a_datetime.year, a_datetime.month, a_datetime.day)
        current_time.timezone = a_datetime.timezone
        current_time += a_datetime.timezone * 1.0/24 # to center plot at local noon

        for d in range(0, npts + 1):

            sun_ct = Bodies.SunPosition.HorizontalCoords(an_observer, current_time)
            sun_ve = Bodies.SunPosition.HorizontalCoords(an_observer, vernal_equinox)
            sun_ss = Bodies.SunPosition.HorizontalCoords(an_observer, summer_solstice)
            sun_ae = Bodies.SunPosition.HorizontalCoords(an_observer, autumnal_equinox)
            sun_ws = Bodies.SunPosition.HorizontalCoords(an_observer, winter_solstice)

            altitude.append([dtime,
                             Transforms.utils.get_altitude(sun_ve).degrees,
                             Transforms.utils.get_altitude(sun_ss).degrees,
                             Transforms.utils.get_altitude(sun_ae).degrees,
                             Transforms.utils.get_altitude(sun_ws).degrees,
                             Transforms.utils.get_altitude(sun_ct).degrees # needs to be last for sun position marker
                         ]
            )


            dtime += 1.0/npts*24

            current_time += 1.0/npts
            vernal_equinox += 1.0/npts
            summer_solstice += 1.0/npts
            autumnal_equinox += 1.0/npts
            winter_solstice += 1.0/npts

        result['altitude_data_24h'] = altitude # list

        rts = get_sun_rise_transit_set(utils.request_angle('latitude', flask.request),
                                       utils.request_angle('longitude', flask.request),
                                       utils.request_datetime('date',
                                                              'time',
                                                              'timezone',
                                                              'dst',
                                                              flask.request),
                                       is_dst)


        result['sun_marker_altitude'] = '{}'.format(str(rts['altitude']))
        result['sun_marker_azimuth']  = '{}'.format(str(rts['azimuth']))

        result['rising']   = rts['rising']
        result['transit']  = rts['transit']
        result['setting']  = rts['setting']


    except Bodies.SunPosition.Error as err:

        result['sun_marker_altitude'] = str(err)
        result['sun_marker_azimuth']  = str(err)
        result['rising']   = str(err)
        result['transit']  = str(err)
        result['setting']  = str(err)

    except (utils.Error, TypeError, ValueError, RuntimeError) as err:
        result['errors'].append(str(err))

    return flask.jsonify(**result)


def get_sun_rise_transit_set(a_latitude, a_longitude, a_datetime, is_dst):
    """Calculate the sun position at rise, transit and set.

    Args:
        a_latitude (coords.angle): observer's latitude
        a_longitude (coords.angle): observer's longitude
        a_datetime (coords.datetime): observer's time
        a_dst (bool): daylight saving time


    return results dictionary
    """

    result = dict()
    result['latitude'] = a_latitude
    result['longitude'] = a_longitude
    result['datetime'] = a_datetime
    result['dst'] = is_dst

    result['eot'] = Bodies.SunPosition.EquationOfTime(a_datetime)
    result['obliquity'] = Transforms.EclipticEquatorial.obliquity(a_datetime)

    an_observer = Transforms.utils.latlon2spherical(a_latitude, a_longitude)

    rising, transit, setting = Bodies.SunPosition.SunRiseAndSet(an_observer, a_datetime)

    # TODO this hack messes with leap day
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


    result['rising'] = '{:02}:{:02}:{:05.2f}'.format(rising.hour, rising.minute, rising.second)
    result['transit'] = '{:02}:{:02}:{:05.2f}'.format(transit.hour, transit.minute, transit.second)
    result['setting'] = '{:02}:{:02}:{:05.2f}'.format(setting.hour, setting.minute, setting.second)


    sun_azalt = get_sun_azalt(an_observer, a_datetime)

    result['azimuth'] = '{}'.format(sun_azalt['azimuth'])
    result['altitude'] = '{}'.format(sun_azalt['altitude'])


    return result


# solar azimuth


def get_sun_azalt(an_observer, a_datetime):
    """Calculate the azimuth and altitude of the sun for an observer at a_datetime

    TODO duplication in SunPosition and above

    Args:
        an_observer (coords.spherical): an observer locatioin
        a_datetime (coords.datetime): time of obsevation
    """
    result = dict()

    ecliptic_longitude, R = Bodies.SunPosition.SolarLongitudeRange(a_datetime)

    sun_ec = coords.spherical(R, coords.angle(90), ecliptic_longitude)
    sun_eq = Transforms.EclipticEquatorial.toEquatorial(sun_ec, a_datetime)
    sun_hz = Transforms.EquatorialHorizon.toHorizon(sun_eq, an_observer, a_datetime)

    result['dec'] = str(coords.angle(90) - sun_eq.theta)

    result['R'] = R
    result['ecliptic_longitude'] = str(ecliptic_longitude)

    result['azimuth'] = Transforms.utils.get_azimuth(sun_hz)
    result['altitude'] = Transforms.utils.get_altitude(sun_hz)

    return result


@api.route("/sun_rise_set_azimuths")
def sun_rise_set_azimuths():
    """Get the sun rise and set azimuths"""

    result = {'errors': list()}

    try:

        an_observer = Transforms.utils.latlon2spherical(utils.request_angle('latitude', flask.request),
                                                        utils.request_angle('longitude', flask.request))

        result['observer'] = str(an_observer) # TODO format? XML from c++ operator::<<()
        result['latitude'] = utils.request_angle('latitude', flask.request).degrees
        result['longitude'] = utils.request_angle('longitude', flask.request).degrees

        a_datetime = utils.request_datetime('date','time', 'timezone','dst', flask.request)

        result['current_date'] = '{}-{:02}-{:02}'.format(a_datetime.year, a_datetime.month, a_datetime.day)
        result['current_time'] = '{:02}:{:02}:{:05.2f}'.format(a_datetime.hour, a_datetime.minute, a_datetime.second)
        result['current_timezone'] = '{}'.format(a_datetime.timezone)

        is_dst = True if flask.request.args.get('dst') == 'true' else False


        rts = get_sun_rise_transit_set(utils.request_angle('latitude', flask.request),
                                       utils.request_angle('longitude', flask.request),
                                       utils.request_datetime('date',
                                                              'time',
                                                              'timezone',
                                                              'dst',
                                                              flask.request),
                                       is_dst)




        result['current_altitude_str'] = '{}'.format(str(rts['altitude']))
        result['current_azimuth_str']  = '{}'.format(str(rts['azimuth']))

        result['rising']   = rts['rising']
        result['transit']  = rts['transit']
        result['setting']  = rts['setting']


        # TODO does not support fractional time zones like India yet
        if a_datetime.timezone < 0:
            timezone = '{:03}'.format(int(a_datetime.timezone))
        else:
            timezone = '+{:02}'.format(int(a_datetime.timezone))


        a_rising_datetime = coords.datetime('{}-{:02}-{:02}T{}{}'.format(a_datetime.year, a_datetime.month, a_datetime.day,
                                                                         result['rising'], timezone))

        a_transit_datetime = coords.datetime('{}-{:02}-{:02}T{}{}'.format(a_datetime.year, a_datetime.month, a_datetime.day,
                                                                          result['transit'], timezone))

        a_setting_datetime = coords.datetime('{}-{:02}-{:02}T{}{}'.format(a_datetime.year, a_datetime.month, a_datetime.day,
                                                                          result['setting'], timezone))


        rising_azalt = get_sun_azalt(an_observer, a_rising_datetime)
        transit_azalt = get_sun_azalt(an_observer, a_transit_datetime)
        setting_azalt = get_sun_azalt(an_observer, a_setting_datetime)

        result['rising_azimuth'] = rising_azalt['azimuth'].degrees
        result['transit_azimuth'] = transit_azalt['azimuth'].degrees
        result['setting_azimuth'] = setting_azalt['azimuth'].degrees

        # string version for JSON

        result['rising_azimuth_str'] = str(rising_azalt['azimuth'])
        result['rising_time_str'] = str(rts['rising'])

        result['transit_azimuth_str'] = str(transit_azalt['azimuth'])
        result['transit_time_str'] = str(rts['transit'])

        result['setting_azimuth_str'] = str(setting_azalt['azimuth'])
        result['setting_time_str'] = str(rts['setting'])


    except (utils.Error, TypeError, ValueError, RuntimeError) as err:
        result['errors'].append(str(err))

    return flask.jsonify(**result)


# -----------------------------
# ----- moon position data -----
# -----------------------------

@api.route("/lunar/ecliptic_coords")
def lunar_ecliptic_coords():
    """Calculate the azimuth and altitude of the moon for an observer at a_datetime"""

    result = {'errors': list()}

    try:

        is_dst = True if flask.request.args.get('dst') == 'true' else False
        a_datetime = utils.request_datetime('date','time', 'timezone','dst', flask.request)
        result['datetime'] = str(a_datetime)

        moon_ec = Bodies.MoonPosition.EclipticCoords(a_datetime)

        result['longitude'] = str(Transforms.utils.get_longitude(moon_ec).degrees)
        result['latitude'] =  str(Transforms.utils.get_latitude(moon_ec).degrees)

    except (TypeError, ValueError, RuntimeError, utils.Error) as err:
        result['errors'].append(str(err))

    return flask.jsonify(**result)


@api.route("/lunar/equatorial_coords")
def lunar_equatorial_coords(an_observer, a_datetime):
    """Calculate the azimuth and altitude of the moon for an observer at a_datetime"""

    result = {'errors': list()}

    try:

        is_dst = True if flask.request.args.get('dst') == 'true' else False
        a_datetime = utils.request_datetime('date','time', 'timezone','dst', flask.request)
        result['datetime'] = str(a_datetime)

        moon_eq = Bodies.MoonPosition.EquatorialCoords(a_datetime)

        result['declination'] = str(Transforms.utils.get_declination(moon_eq).degrees)
        result['RA'] = str(Transforms.utils.get_RA(moon_eq).degrees)

    except (TypeError, ValueError, RuntimeError, utils.Error) as err:
        result['errors'].append(str(err))

    return flask.jsonify(**result)


@api.route("/lunar/horizontal_coords")
def lunar_horizontal_coords(an_observer, a_datetime):
    """Calculate the azimuth and altitude of the moon for an observer at a_datetime

    Args:
        an_observer (coords.spherical): an observer locatioin
        a_datetime (coords.datetime): time of obsevation
    """
    result = {'errors': list()}

    try:
        an_observer = Transforms.utils.latlon2spherical(utils.request_angle('latitude', flask.request),
                                                        utils.request_angle('longitude', flask.request))
        result['observer'] = str(an_observer)

        is_dst = True if flask.request.args.get('dst') == 'true' else False
        a_datetime = utils.request_datetime('date','time', 'timezone','dst', flask.request)
        result['datetime'] = str(a_datetime)

        moon_eq = Bodies.MoonPosition.HorizontalCoords(an_observer, a_datetime)

        result['azimuth'] = str(Transforms.utils.get_azimuth(moon_hz).degrees)
        result['altitude'] = str(Transforms.utils.get_altitude(moon_hz).degrees)


    except (TypeError, ValueError, RuntimeError, utils.Error) as err:
        result['errors'].append(str(err))

    return flask.jsonify(**result)


def get_moon_rise_transit_set(a_latitude, a_longitude, a_datetime, is_dst):
    """Calculate the moon position at local rise, transit set

    Args:
        a_latitude (coords.angle): observer's latitude
        a_longitude (coords.angle): observer's longitude
        a_datetime (coords.datetime): observer's time
        a_dst (bool): daylight saving time


    return results dictionary
    """

    result = dict()
    result['latitude'] = a_latitude
    result['longitude'] = a_longitude
    result['datetime'] = a_datetime
    result['dst'] = is_dst

    an_observer = Transforms.utils.latlon2spherical(a_latitude, a_longitude)

    moon_eq = Bodies.MoonPosition.EquatorialCoords(a_datetime)

    rising, transit, setting = Bodies.SunPosition.RiseAndSet(moon_eq, an_observer, a_datetime)

    # TODO this hack messes with leap day
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


    result['rising'] = '{:02}:{:02}:{:05.2f}'.format(rising.hour, rising.minute, rising.second)
    result['transit'] = '{:02}:{:02}:{:05.2f}'.format(transit.hour, transit.minute, transit.second)
    result['setting'] = '{:02}:{:02}:{:05.2f}'.format(setting.hour, setting.minute, setting.second)

    return result


# --------------------------------
# ----- lunar daily altitude -----
# --------------------------------



@api.route("/lunar_daily_altitude")
def lunar_daily_altitude():
    """Get the moon position chart for the given day as JSON


    result.datetime
          .sun_date_label
          .sun_marker_time
          .sun_marker_altitude
          .sun_marker_azimuth
          .sun_rising
          .sun_transit
          .sun_setting
          .moon_date_label
          .moon_marker_time
          .moon_marker_altitude
          .moon_marker_azimuth
          .moon_rising
          .moon_transit
          .moon_setting
          .altitude_data_24h[time, sun, moon ]

    """

    result = {'errors': list()}

    try:

        an_observer = Transforms.utils.latlon2spherical(utils.request_angle('latitude', flask.request),
                                                        utils.request_angle('longitude', flask.request))

        result['observer'] = str(an_observer) # TODO format? XML from c++ operator::<<()
        result['latitude'] = utils.request_angle('latitude', flask.request).degrees
        result['longitude'] = utils.request_angle('longitude', flask.request).degrees

        a_datetime = utils.request_datetime('date','time', 'timezone','dst', flask.request)

        result['datetime'] = str(a_datetime)

        result['current_date'] = '{}-{:02}-{:02}'.format(a_datetime.year, a_datetime.month, a_datetime.day)
        result['current_time'] = '{:02}:{:02}:{:05.2f}'.format(a_datetime.hour, a_datetime.minute, a_datetime.second)
        result['current_timezone'] = '{}'.format(a_datetime.timezone)


        sun_ec_position = Bodies.SunPosition.EclipticCoords(a_datetime)
        result['sun_ec_latitude']  = str(Transforms.utils.get_latitude(sun_ec_position).degrees)
        result['sun_ec_latitude_dms']  = str(Transforms.utils.get_latitude(sun_ec_position))
        result['sun_ec_longitude']  = str(Transforms.utils.get_longitude(sun_ec_position).degrees)
        result['sun_ec_longitude_dms']  = str(Transforms.utils.get_longitude(sun_ec_position))

        result['sun_range'] = '{:6.4f}'.format((sun_ec_position.r / 6.6845871226706E-12)/ 299792458.0) # AU/(AU/m)/m/light-second

        sun_eq_position = Transforms.EclipticEquatorial.toEquatorial(sun_ec_position, a_datetime)
        result['sun_eq_ra']  = str(Transforms.utils.get_RA(sun_eq_position).degrees)
        result['sun_eq_ra_dms']  = str(Transforms.utils.get_RA(sun_eq_position))
        result['sun_eq_dec']  = str(Transforms.utils.get_declination(sun_eq_position).degrees)
        result['sun_eq_dec_dms']  = str(Transforms.utils.get_declination(sun_eq_position))

        sun_hz_position = Transforms.EquatorialHorizon.toHorizon(sun_eq_position, an_observer, a_datetime)
        result['sun_altitude']  = str(Transforms.utils.get_altitude(sun_hz_position).degrees)
        result['sun_altitude_dms']  = str(Transforms.utils.get_altitude(sun_hz_position))
        result['sun_azimuth']  = str(Transforms.utils.get_azimuth(sun_hz_position).degrees)
        result['sun_azimuth_dms']  = str(Transforms.utils.get_azimuth(sun_hz_position))


        moon_ec_position = Bodies.MoonPosition.EclipticCoords(a_datetime)
        result['moon_ec_latitude']  = str(Transforms.utils.get_latitude(moon_ec_position).degrees)
        result['moon_ec_latitude_dms']  = str(Transforms.utils.get_latitude(moon_ec_position))
        result['moon_ec_longitude']  = str(Transforms.utils.get_longitude(moon_ec_position).degrees)
        result['moon_ec_longitude_dms']  = str(Transforms.utils.get_longitude(moon_ec_position))

        result['moon_range'] = '{:6.4f}'.format(moon_ec_position.r / 299792.458) # km / (km/light-second)

        moon_eq_position = Transforms.EclipticEquatorial.toEquatorial(moon_ec_position, a_datetime)
        result['moon_eq_ra']  = str(Transforms.utils.get_RA(moon_eq_position).degrees)
        result['moon_eq_ra_dms']  = str(Transforms.utils.get_RA(moon_eq_position))
        result['moon_eq_dec']  = str(Transforms.utils.get_declination(moon_eq_position).degrees)
        result['moon_eq_dec_dms']  = str(Transforms.utils.get_declination(moon_eq_position))

        moon_hz_position = Transforms.EquatorialHorizon.toHorizon(moon_eq_position, an_observer, a_datetime)
        result['moon_altitude']  = str(Transforms.utils.get_altitude(moon_hz_position).degrees)
        result['moon_altitude_dms']  = str(Transforms.utils.get_altitude(moon_hz_position))
        result['moon_azimuth']  = str(Transforms.utils.get_azimuth(moon_hz_position).degrees)
        result['moon_azimuth_dms']  = str(Transforms.utils.get_azimuth(moon_hz_position))



        # ----- plot data -----

        npts = 24*4

        is_dst = True if flask.request.args.get('dst') == 'true' else False

        if is_dst:
            dtime = 1
        else:
            dtime = 0

        moon_azal = list()

        current_time = coords.datetime(a_datetime.year, a_datetime.month, a_datetime.day)
        current_time.timezone = a_datetime.timezone
        current_time += a_datetime.timezone * 1.0/24 # to center plot at local noon

        daily_sun_azimuth = list()
        daily_sun_altitude = list()

        daily_moon_azimuth = list()
        daily_moon_altitude = list()

        for i in range(0, npts):

            current_time += 1.0/npts # previous day on 0?

            current_sun_position_hz = Bodies.SunPosition.HorizontalCoords(an_observer, current_time)

            # break wrap
            if i > 0:

                # opposite in southern hemisphere
                if utils.request_angle('latitude', flask.request).degrees < 0:
                    if Transforms.utils.get_azimuth(current_sun_position_hz).degrees > daily_sun_azimuth[-1]:
                        daily_sun_azimuth.append(None)

                else:

                    if Transforms.utils.get_azimuth(current_sun_position_hz).degrees < daily_sun_azimuth[-1]:
                        daily_sun_azimuth.append(None)

            daily_sun_azimuth.append(Transforms.utils.get_azimuth(current_sun_position_hz).degrees)
            daily_sun_altitude.append(Transforms.utils.get_altitude(current_sun_position_hz).degrees)


            current_moon_position_hz = Bodies.MoonPosition.HorizontalCoords(an_observer, current_time)

            # break wrap
            if i > 0:

                # opposite in southern hemisphere
                if utils.request_angle('latitude', flask.request).degrees < 0:
                    if Transforms.utils.get_azimuth(current_moon_position_hz).degrees > daily_moon_azimuth[-1]:
                        daily_moon_azimuth.append(None)

                else:

                    if Transforms.utils.get_azimuth(current_moon_position_hz).degrees < daily_moon_azimuth[-1]:
                        daily_moon_azimuth.append(None)

            daily_moon_azimuth.append(Transforms.utils.get_azimuth(current_moon_position_hz).degrees)
            daily_moon_altitude.append(Transforms.utils.get_altitude(current_moon_position_hz).degrees)



        result['daily_sun_azimuth'] = daily_sun_azimuth
        result['daily_sun_altitude'] = daily_sun_altitude

        result['daily_moon_azimuth'] = daily_moon_azimuth
        result['daily_moon_altitude'] = daily_moon_altitude


        # ----- rise, transit, set -----

        sun_rts = get_sun_rise_transit_set(utils.request_angle('latitude', flask.request),
                                           utils.request_angle('longitude', flask.request),
                                           utils.request_datetime('date',
                                                                  'time',
                                                                  'timezone',
                                                                  'dst',
                                                                  flask.request),
                                           is_dst)

        result['sun_rising']   = sun_rts['rising']
        result['sun_transit']  = sun_rts['transit']
        result['sun_setting']  = sun_rts['setting']


        moon_rts = get_moon_rise_transit_set(utils.request_angle('latitude', flask.request),
                                             utils.request_angle('longitude', flask.request),
                                             utils.request_datetime('date',
                                                                    'time',
                                                                    'timezone',
                                                                    'dst',
                                                                    flask.request),
                                             is_dst)

        result['moon_rising']   = moon_rts['rising']
        result['moon_transit']  = moon_rts['transit']
        result['moon_setting']  = moon_rts['setting']


    except (Bodies.SunPosition.Error, utils.Error, TypeError, ValueError, RuntimeError) as err:
        result['errors'].append(str(err))

    return flask.jsonify(**result)
