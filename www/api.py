#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""AAI API

    sun_position_data

    curl http://0.0.0.0:8080/api/v1/sun_position_data\?latitude=37\&longitude=-122\&date=2017-12-11\&time=14\%3A37\%3A54\&timezone=-8\&dst=false


    radec2azalt

    azalt2radec


TODO more details

"""

import flask

import coords
import utils

import Bodies.SunPosition
import Transforms.EclipticEquatorial
import Transforms.EquatorialHorizon
import Transforms.utils




api = flask.Blueprint('api', __name__, url_prefix='/api/v1')


@api.route("/sun_position_data")
def sun_position_data():
    """Get the sun position chart for the given day as JSON

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

    try:

        result = dict()

        an_observer = Transforms.utils.latlon2spherical(utils.request_angle('latitude', flask.request),
                                                        utils.request_angle('longitude', flask.request))

        result['observer'] = str(an_observer) # TODO format? XML from c++ operator::<<()

        is_dst = True if flask.request.args.get('dst') == 'true' else False

        a_datetime = utils.request_datetime('date',
                                            'time',
                                            utils.request_float('timezone', flask.request),
                                            is_dst,
                                            flask.request)

        result['datetime'] = str(a_datetime)

        result['sun_marker_time'] = a_datetime.hour + a_datetime.minute/60.0 # distance on x-axis to plot sun marker

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

        result['sun_date_label'] = '{year}-{month}-{day}'.format(year=a_datetime.year,
                                                                 month=a_datetime.month,
                                                                 day=a_datetime.day),
        npts = 24*4

        if is_dst:
            dtime = 1
            result['sun_marker_time'] += 1
        else:
            dtime = 0

        altitude = list()

        local_midnight = coords.datetime(a_datetime.year, a_datetime.month, a_datetime.day)
        local_midnight.timezone = a_datetime.timezone
        local_midnight += a_datetime.timezone * 1.0/24 # to center plot at local noon

        for d in range(0, npts + 1):

            sun_ct = Bodies.SunPosition.SunPosition(an_observer, local_midnight)
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

            local_midnight += 1.0/npts
            vernal_equinox += 1.0/npts
            summer_solstice += 1.0/npts
            autumnal_equinox += 1.0/npts
            winter_solstice += 1.0/npts

        result['altitude_data_24h'] = altitude # list

        # get rise, transit, set time
        rts = calculate_sun_position(utils.request_angle('latitude', flask.request),
                                     utils.request_angle('longitude', flask.request),
                                     utils.request_datetime('date',
                                                            'time',
                                                            utils.request_float('timezone', flask.request),
                                                            is_dst,
                                                            flask.request),
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

    except (utils.Error, TypeError, ValueError, RuntimeError) as err:
        result = {'error': str(err)}

    return flask.jsonify(**result)


def calculate_sun_position(a_latitude, a_longitude, a_datetime, is_dst):
    """Calculate the sun position.

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



# ----------------------------
# ----- eq hz transforms -----
# ----------------------------


@api.route("/radec2azalt")
def radec2azalt():
    """Transform Right Ascension, Declination to Azimuth, Altitude Coordinates"""

    try:

        result = dict()

        an_observer = Transforms.utils.latlon2spherical(utils.request_angle('latitude', flask.request),
                                                        utils.request_angle('longitude', flask.request))

        result['observer'] = str(an_observer)

        is_dst = True if flask.request.args.get('dst') == 'true' else False

        a_datetime = utils.request_datetime('date',
                                            'time',
                                            utils.request_float('timezone', flask.request),
                                            is_dst,
                                            flask.request)

        result['datetime'] = str(a_datetime)

        body_eq = Transforms.utils.radec2spherical(utils.request_angle('ra', flask.request),
                                                   utils.request_angle('dec', flask.request))

        body_hz = Transforms.EquatorialHorizon.toHorizon(body_eq, an_observer, a_datetime)

        result['azimuth'] = Transforms.utils.get_azimuth(body_hz).value
        result['altitude'] = Transforms.utils.get_altitude(body_hz).value


    except (TypeError, ValueError, RuntimeError) as err:
        result = {'error': str(err)}

    return flask.jsonify(**result)


@api.route("/azalt2radec")
def azalt2radec():
    """Transform Azimuth, Altitude to Right Ascension, Declination Coordinates"""

    try:

        result = dict()

        an_observer = Transforms.utils.latlon2spherical(utils.request_angle('latitude', flask.request),
                                                        utils.request_angle('longitude', flask.request))

        result['observer'] = str(an_observer)

        is_dst = True if flask.request.args.get('dst') == 'true' else False

        a_datetime = utils.request_datetime('date',
                                            'time',
                                            utils.request_float('timezone', flask.request),
                                            is_dst,
                                            flask.request)

        result['datetime'] = str(a_datetime)


        body_hz = Transforms.utils.azalt2spherical(utils.request_angle('azimuth', flask.request),
                                                   utils.request_angle('altitude', flask.request))

        body_eq = Transforms.EquatorialHorizon.toEquatorial(body_hz, an_observer, a_datetime)

        result['ra'] = Transforms.utils.get_RA(body_eq).value
        result['dec'] = Transforms.utils.get_declination(body_eq).value

    except (TypeError, ValueError, RuntimeError) as err:

        result = {'error': str(err)}

    return flask.jsonify(**result)



