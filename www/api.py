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
        an_observer = Transforms.utils.latlon2spherical(utils.request_angle('latitude', flask.request),
                                                        utils.request_angle('longitude', flask.request))

        result['observer'] = str(an_observer)

        is_dst = True if flask.request.args.get('dst') == 'true' else False

        a_datetime = utils.request_datetime('date','time', 'timezone','dst', flask.request)

        result['datetime'] = str(a_datetime)


        ecliptic_longitude, R = Bodies.SunPosition.SolarLongitude(a_datetime)

        sun_ec = coords.spherical(R, coords.angle(90), ecliptic_longitude)

        result['R'] = R
        result['longitude'] = str(ecliptic_longitude)
        result['latitude'] = str(Transforms.utils.get_declination(sun_ec))


    except (TypeError, ValueError, RuntimeError, utils.Error) as err:
        result['errors'].append(str(err))

    return flask.jsonify(**result)



@api.route("/solar/equatorial_coords")
def solar_equatorial_coords(an_observer, a_datetime):
    """Calculate the azimuth and altitude of the sun for an observer at a_datetime"""

    result = {'errors': list()}

    try:
        an_observer = Transforms.utils.latlon2spherical(utils.request_angle('latitude', flask.request),
                                                        utils.request_angle('longitude', flask.request))

        result['observer'] = str(an_observer)

        is_dst = True if flask.request.args.get('dst') == 'true' else False

        a_datetime = utils.request_datetime('date','time', 'timezone','dst', flask.request)

        result['datetime'] = str(a_datetime)

        ecliptic_longitude, R = Bodies.SunPosition.SolarLongitude(a_datetime)

        sun_ec = coords.spherical(R, coords.angle(90), ecliptic_longitude)
        sun_eq = Transforms.EclipticEquatorial.toEquatorial(sun_ec, a_datetime)

        result['declination'] = str(Transforms.utils.get_declination(sun_eq))
        result['RA'] = str(Transforms.utils.get_RA(sun_eq))

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

        ecliptic_longitude, R = Bodies.SunPosition.SolarLongitude(a_datetime)

        sun_ec = coords.spherical(R, coords.angle(90), ecliptic_longitude)
        sun_eq = Transforms.EclipticEquatorial.toEquatorial(sun_ec, a_datetime)
        sun_hz = Transforms.EquatorialHorizon.toHorizon(sun_eq, an_observer, a_datetime)

        result['azimuth'] = str(Transforms.utils.get_azimuth(sun_hz))
        result['altitude'] = str(Transforms.utils.get_altitude(sun_hz))

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


        result['sun_marker_altitude'] = ''.join((str(rts['altitude']), ' (', str(rts['altitude'].degrees), ')'))
        result['sun_marker_azimuth']  = ''.join((str(rts['azimuth']), ' (', str(rts['azimuth'].degrees), ')'))

        result['rising']   = str(rts['rising'])  # JSON-able
        result['transit']  = str(rts['transit']) # JSON-able
        result['setting']  = str(rts['setting']) # JSON-able


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


    result['rising'] = rising
    result['transit'] = transit
    result['setting'] = setting


    sun_azalt = get_sun_azalt(an_observer, a_datetime)

    result['azimuth'] = sun_azalt['azimuth']
    result['altitude'] = sun_azalt['altitude']

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


    ecliptic_longitude, R = Bodies.SunPosition.SolarLongitude(a_datetime)

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

        result['datetime'] = str(a_datetime)

        is_dst = True if flask.request.args.get('dst') == 'true' else False


        rts = get_sun_rise_transit_set(utils.request_angle('latitude', flask.request),
                                       utils.request_angle('longitude', flask.request),
                                       utils.request_datetime('date',
                                                              'time',
                                                              'timezone',
                                                              'dst',
                                                              flask.request),
                                       is_dst)


        current_azalt = get_sun_azalt(an_observer, a_datetime)
        rising_azalt = get_sun_azalt(an_observer, rts['rising'])
        transit_azalt = get_sun_azalt(an_observer, rts['transit'])
        setting_azalt = get_sun_azalt(an_observer, rts['setting'])

        result['current_azimuth'] = current_azalt['azimuth'].degrees
        result['rising_azimuth'] = rising_azalt['azimuth'].degrees
        result['transit_azimuth'] = transit_azalt['azimuth'].degrees
        result['setting_azimuth'] = setting_azalt['azimuth'].degrees

        # string version for JSON

        result['current_azimuth_str'] = str(current_azalt['azimuth'])
        result['current_time_str'] = str(a_datetime)

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
        an_observer = Transforms.utils.latlon2spherical(utils.request_angle('latitude', flask.request),
                                                        utils.request_angle('longitude', flask.request))

        result['observer'] = str(an_observer)

        is_dst = True if flask.request.args.get('dst') == 'true' else False

        a_datetime = utils.request_datetime('date','time', 'timezone','dst', flask.request)

        result['datetime'] = str(a_datetime)

        elong, elat, distance = Bodies.MoonPosition.EclipticCoords(a_datetime)

        moon_ec = coords.spherical(R, elat, elong)

        result['R'] = R
        result['longitude'] = str(ecliptic_longitude)
        result['latitude'] = str(Transforms.utils.get_declination(moon_ec))


    except (TypeError, ValueError, RuntimeError, utils.Error) as err:
        result['errors'].append(str(err))

    return flask.jsonify(**result)



@api.route("/lunar/equatorial_coords")
def lunar_equatorial_coords(an_observer, a_datetime):
    """Calculate the azimuth and altitude of the moon for an observer at a_datetime"""

    result = {'errors': list()}

    try:
        an_observer = Transforms.utils.latlon2spherical(utils.request_angle('latitude', flask.request),
                                                        utils.request_angle('longitude', flask.request))

        result['observer'] = str(an_observer)

        is_dst = True if flask.request.args.get('dst') == 'true' else False

        a_datetime = utils.request_datetime('date','time', 'timezone','dst', flask.request)

        result['datetime'] = str(a_datetime)

        elong, elat, distance = Bodies.MoonPositionEclipticCoords(a_datetime)

        moon_ec = coords.spherical(R, elat, elong)
        moon_eq = Transforms.EclipticEquatorial.toEquatorial(moon_ec, a_datetime)

        result['declination'] = str(Transforms.utils.get_declination(moon_eq))
        result['RA'] = str(Transforms.utils.get_RA(moon_eq))

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

        elong, elat, distance = EclipticCoords(a_datetime)

        moon_ec = coords.spherical(R, elat, elong)
        moon_eq = Transforms.EclipticEquatorial.toEquatorial(moon_ec, a_datetime)
        moon_hz = Transforms.EquatorialHorizon.toHorizon(moon_eq, an_observer, a_datetime)

        result['azimuth'] = str(Transforms.utils.get_azimuth(moon_hz))
        result['altitude'] = str(Transforms.utils.get_altitude(moon_hz))

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


    elong, elat, distance = Bodies.MoonPosition.EclipticCoords(a_datetime)

    moon_ec = coords.spherical(distance, elat, elong)
    moon_eq = Transforms.EclipticEquatorial.toEquatorial(moon_ec, a_datetime)


    rising, transit, setting = Bodies.SunPosition.RiseAndSet(moon_eq, an_observer, a_datetime)

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


    result['rising'] = rising
    result['transit'] = transit
    result['setting'] = setting


    sun_azalt = get_sun_azalt(an_observer, a_datetime)

    result['azimuth'] = sun_azalt['azimuth']
    result['altitude'] = sun_azalt['altitude']

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

        result['sun_marker_time'] = a_datetime.hour + a_datetime.minute/60.0 # distance on x-axis to plot sun marker

        result['date_label'] = '{year}-{month}-{day}'.format(year=a_datetime.year,
                                                             month=a_datetime.month,
                                                             day=a_datetime.day)



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

            sun_position = Bodies.SunPosition.HorizontalCoords(an_observer, current_time)
            moon_position = Bodies.MoonPosition.HorizontalCoords(an_observer, current_time)

            # TODO azimuth vs altitude over time

            altitude.append([dtime,
                             Transforms.utils.get_altitude(moon_position).degrees, # TODO needs to be last for sun position marker?
                             Transforms.utils.get_altitude(sun_position).degrees  # TODO needs to be last for sun position marker?
                         ]
            )


            dtime += 1.0/npts*24

            current_time += 1.0/npts


        result['altitude_data_24h'] = altitude # list



        sun_rts = get_sun_rise_transit_set(utils.request_angle('latitude', flask.request),
                                           utils.request_angle('longitude', flask.request),
                                           utils.request_datetime('date',
                                                                  'time',
                                                                  'timezone',
                                                                  'dst',
                                                                  flask.request),
                                           is_dst)


        result['sun_marker_altitude'] = ''.join((str(sun_rts['altitude']), ' (', str(sun_rts['altitude'].degrees), ')'))
        result['sun_marker_azimuth']  = ''.join((str(sun_rts['azimuth']), ' (', str(sun_rts['azimuth'].degrees), ')'))

        result['sun_rising']   = str(sun_rts['rising'])  # JSON-able
        result['sun_transit']  = str(sun_rts['transit']) # JSON-able
        result['sun_setting']  = str(sun_rts['setting']) # JSON-able


        # TODO moon
        moon_rts = get_sun_rise_transit_set(utils.request_angle('latitude', flask.request),
                                             utils.request_angle('longitude', flask.request),
                                             utils.request_datetime('date',
                                                                    'time',
                                                                    'timezone',
                                                                    'dst',
                                                                    flask.request),
                                             is_dst)


        result['moon_marker_altitude'] = ''.join((str(moon_rts['altitude']), ' (', str(moon_rts['altitude'].degrees), ')'))
        result['moon_marker_azimuth']  = ''.join((str(moon_rts['azimuth']), ' (', str(moon_rts['azimuth'].degrees), ')'))

        result['moon_rising']   = str(moon_rts['rising'])  # JSON-able
        result['moon_transit']  = str(moon_rts['transit']) # JSON-able
        result['moon_setting']  = str(moon_rts['setting']) # JSON-able


    except Bodies.SunPosition.Error as err:

        result['sun_marker_altitude'] = str(err)
        result['sun_marker_azimuth']  = str(err)
        result['sun_rising']   = str(err)
        result['sun_transit']  = str(err)
        result['sun_setting']  = str(err)

        result['moon_marker_altitude'] = str(err)
        result['moon_marker_azimuth']  = str(err)
        result['moon_rising']   = str(err)
        result['moon_transit']  = str(err)
        result['moon_setting']  = str(err)

    except (utils.Error, TypeError, ValueError, RuntimeError) as err:
        result['errors'].append(str(err))

    return flask.jsonify(**result)
