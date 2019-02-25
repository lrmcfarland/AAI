#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Calculates the position of the sun for the given datetime.

Uses algorithms from:
    Astronomical Algorithms 2ed, Jean Meeus 1998
    http://en.wikipedia.org/wiki/Position_of_the_Sun
    http://aa.usno.navy.mil/faq/docs/GAST.php




"""

from __future__ import absolute_import  # for python 2 and 3

import math

import starbug.coords as coords

import AAI.Transforms.EclipticEquatorial
import AAI.Transforms.EquatorialHorizon
import AAI.Transforms.utils


class Error(Exception):
    pass


def SolarLongitude(a_datetime):
    """Calculate the longitude of the sun for the given date

    from http://en.wikipedia.org/wiki/Position_of_the_Sun

    Args:

    a_datetime (coords.datetime): The time of the observation.

    Returns (float, float): A tuple of the sun's longitude and distance in AU
    """

    n = a_datetime.toJulianDate() - a_datetime.J2000

    # mean longitude
    L = coords.angle(280.460 + 0.9856474*n)
    L.normalize(0, 360)

    # ecliptic longitude
    g = coords.angle(357.528 + 0.9856003*n)
    g.normalize(0, 360)

    # ecliptic longitude
    ecliptic_longitude = coords.angle(L.value + 1.915*math.sin(g.radians) + 0.020*math.sin(2.0*g.radians))

    # distance to sun in AU
    R = 1.00014 - 0.01671*math.cos(g.radians) - 0.00014*math.cos(2.0*g.radians)

    return ecliptic_longitude, R


def SunPosition(an_observer, a_datetime):
    """Calculate the location of the sun relaive to an observer

    Args:

    an_observer (coords.spherical): the latitude (in degrees) and
    longitude of an observer as a spherical coordinate where theta
    is the complement of latitude and longitude is measured
    positive east. See utils.latlon2spherical.

    a_datetime (coords.datetime): The time of the observation.

    Returns (coords.spherical): the position of the sun in horizon coordinates.
    """

    ecliptic_longitude, R = SolarLongitude(a_datetime)

    sun_ec = coords.spherical(R, coords.angle(90), ecliptic_longitude)
    sun_eq = AAI.Transforms.EclipticEquatorial.toEquatorial(sun_ec, a_datetime)
    sun_hz = AAI.Transforms.EquatorialHorizon.toHorizon(sun_eq, an_observer, a_datetime)

    return sun_hz


def EquationOfTime(a_datetime):
    """Calcuate the equation of time

    from http://en.wikipedia.org/wiki/Equation_of_time

    TODO: Only valid for noon. Rounds to nearest half day.

    Args:

    a_datetime (coords.datetime): The time of the observation.

    Returns (coords.angle): equation of time as an angle in degrees. *60 for minutes.
    """

    noon = coords.datetime()
    noon.fromJulianDate(math.floor(a_datetime.toJulianDate()))
    gast = AAI.Transforms.SiderealTime.USNO_C163.GAST(noon)

    ecliptic_longitude, R = SolarLongitude(noon)

    sun_ec = coords.spherical(R, coords.angle(90), ecliptic_longitude)
    sun_eq = AAI.Transforms.EclipticEquatorial.toEquatorial(sun_ec, noon)

    eot = coords.angle()

    sun_ra = AAI.Transforms.utils.get_RA(sun_eq)

    if gast.value - sun_ra.value < 12:
        eot.value = gast.value - sun_ra.value

    elif gast.value - sun_ra.value >= 12:
        eot.value = gast.value - sun_ra.value - 24

    else:
        raise Error('unsupported EoT case')

    return eot


def SunRiseAndSet(an_observer, a_datetime):
    """Sun rise and set times

    Args:

    an_observer (coords.spherical): the latitude (in degrees) and
    longitude of an observer as a spherical coordinate where theta
    is the complement of latitude and longitude is measured
    positive east. See utils.latlon2spherical.


    a_datetime (coords.datetime): The time of the observation.

    Returns (coords.datetime, coords.datetime, coords.datetime) of
    rising, transit and setting in local time.
    """

    ecliptic_longitude, R = SolarLongitude(a_datetime)
    sun_ec = coords.spherical(R, coords.angle(90), ecliptic_longitude)
    sun_eq = AAI.Transforms.EclipticEquatorial.toEquatorial(sun_ec, a_datetime)

    return RiseAndSet(sun_eq, an_observer, a_datetime, an_altitude=coords.angle(-0.8333))


def RiseAndSet(an_object, an_observer, a_datetime, an_altitude=coords.angle(0)):
    """Rise and set times

    from Meeus, ch. 15

    WARNING: I found adding the m0, m1 and m2 could mess with my timezone
    adjustments by up to 2 days, hence the adjustments.

    TODO try not normalizing m0, m1 or m2

    TODO more than just sun position, return local time, altitude
    configurable to astronomical, nautical, civil, star, sun, moon

    TODO error check for timezone and observer location?

    Args:

    an_object: the vector to transform in theta (90 - declination),
    phi (RA * 15). See utils.radec2spherical.

    an_observer (coords.spherical): the latitude (in degrees) and
    longitude of an observer as a spherical coordinate where theta
    is the complement of latitude and longitude is measured
    positive east. See utils.latlon2spherical.

    a_datetime (coords.datetime): The time of the observation.

    an_altitude (coords.angle): The geometric center of the body at
    the time of rising (accounting for atmospheric refraction) where:
        ho = -0.5667 for point sources like stars
        ho = -0.8333 for the Sun.
        ho = +0.125  for the the moon, approximately.


    Returns (coords.datetime, coords.datetime, coords.datetime) of
    rising, transit and setting in local time.

    """

    JD, JDo = AAI.Transforms.SiderealTime.USNO_C163.JulianDate0(a_datetime)

    midnight = coords.datetime()
    midnight.fromJulianDate(JDo)

    observer_latitude = AAI.Transforms.utils.get_latitude(an_observer)
    observer_longitude = AAI.Transforms.utils.get_longitude(an_observer)

    object_RA = coords.angle(AAI.Transforms.utils.get_RA(an_object).value * 15) # in degrees
    object_declination = AAI.Transforms.utils.get_declination(an_object)

    gmst = AAI.Transforms.SiderealTime.USNO_C163.GMST(midnight)
    gmst.value *= 15 # in degrees

    cos_hour_angle = (math.sin(an_altitude.radians) \
        - math.sin(observer_latitude.radians) * math.sin(object_declination.radians)) \
        / (math.cos(observer_latitude.radians) * math.cos(object_declination.radians))

    if cos_hour_angle > 1:
        raise Error('object is circumpolar from this observation point')

    if cos_hour_angle < -1:
        raise Error('object is below the horizon from this observation point')

    hour_angle = coords.angle()
    hour_angle.radians = math.acos(cos_hour_angle)

    # -------------------
    # ----- transit -----
    # -------------------

    # longitude sign convention is IAU, opposite Meeus p. 93
    m0 = coords.angle((object_RA - observer_longitude - gmst).value/360.0)
    m0.normalize(0, 1)

    transit_utc = coords.datetime()
    transit_utc.fromJulianDate(JDo + m0.value)


    if not a_datetime.timezone:
        transit_loc = transit_utc

    else:

        transit_loc = coords.datetime(midnight.year, midnight.month, midnight.day,
                                      transit_utc.hour, transit_utc.minute, transit_utc.second,
                                      a_datetime.timezone)

        transit_loc += a_datetime.timezone/24

        # can be two days off! and infinite failure for 2018-02-28 +=1
        # TODO bug in last day in feb += 1?


        if transit_loc.toJulianDate() - a_datetime.toJulianDate() > 1.5:
            transit_loc -= 2 # test case TODO

        elif transit_loc.toJulianDate() - a_datetime.toJulianDate() > 0.5:
            transit_loc -= 1 # test case 2018-04-18T17:00:00+08

        elif transit_loc.toJulianDate() - a_datetime.toJulianDate() < -1.5:
            transit_loc += 2 # test case TODO

        elif transit_loc.toJulianDate() - a_datetime.toJulianDate() < -0.5:
            transit_loc += 1 # test case 2018-04-18T07:00:00-08

        elif math.fabs(transit_loc.toJulianDate() - a_datetime.toJulianDate()) < 0.5:
            pass

        else:
            raise Error('transit: unsupported timezone mod case {}'.format(a_datetime))

    # ------------------
    # ----- rising -----
    # ------------------

    m1 = coords.angle(m0.value - hour_angle.value/360)
    m1.normalize(0, 1)

    rising_utc = coords.datetime()
    rising_utc.fromJulianDate(JDo + m1.value)

    if not a_datetime.timezone:
        rising_loc = rising_utc

    else:

        rising_loc = coords.datetime(midnight.year, midnight.month, midnight.day,
                                     rising_utc.hour, rising_utc.minute, rising_utc.second,
                                     a_datetime.timezone)

        rising_loc += a_datetime.timezone/24

        # TODO de-hack this
        
        if rising_loc.toJulianDate() - a_datetime.toJulianDate() > 1.5:
            rising_loc -= 2 # test case 2018-04-18T17:00:00+08

        elif rising_loc.toJulianDate() - a_datetime.toJulianDate() > 0.5:
            rising_loc -= 1 # test case 2015-05-22T12:00:00+06, 2018-10-18T15:00:00+08,

        elif rising_loc.toJulianDate() - a_datetime.toJulianDate() < -1.5:
            rising_loc += 2 # test case TODO

        elif rising_loc.toJulianDate() - a_datetime.toJulianDate() < -1.0:
            rising_loc += 1 # test case 2018-04-18T07:00:00-08

        elif rising_loc.toJulianDate() - a_datetime.toJulianDate() < -0.5:
            pass

        elif rising_loc.toJulianDate() - a_datetime.toJulianDate() < 0.5:
            pass

        else:
            raise Error('rising: unsupported timezone mod case {}'.format(a_datetime))



    # -------------------
    # ----- setting -----
    # -------------------

    m2 = coords.angle(m0.value + hour_angle.value/360)
    m2.normalize(0, 1)

    setting_utc = coords.datetime()
    setting_utc.fromJulianDate(JDo + m2.value)

    if not a_datetime.timezone:
        setting_loc = setting_utc

    else:

        setting_loc = coords.datetime(midnight.year, midnight.month, midnight.day,
                                      setting_utc.hour, setting_utc.minute, setting_utc.second,
                                      a_datetime.timezone)

        setting_loc += a_datetime.timezone/24

        # TODO de-hack this

        if setting_loc.toJulianDate() - a_datetime.toJulianDate() > 1.5:
            setting_loc -= 2 # test case TODO

        elif setting_loc.toJulianDate() - a_datetime.toJulianDate() > 0.5:
            setting_loc -= 1 # test case 2018-04-18T17:00:00+08

        elif setting_loc.toJulianDate() - a_datetime.toJulianDate() < -1.5:
            setting_loc += 2 # test case 2018-04-18T07:00:00-08

        elif setting_loc.toJulianDate() - a_datetime.toJulianDate() < -1.25: # TODO meh?!?
            setting_loc += 2 # test case

        elif setting_loc.toJulianDate() - a_datetime.toJulianDate() < -0.5:
            setting_loc += 1 # test case 2018-01-31T12:55:00-08,
                             # 2018-02-01T12:55:00-08,
                             # 2018-04-18T09:00:00-08,
                             # 2015-05-22T12:00:00-06,
                             # 2018-03-01T10:00:00-08

        elif setting_loc.toJulianDate() - a_datetime.toJulianDate() < 0.5:
            pass

        else:
            raise Error('setting: unsupported timezone mod case {}'.format(a_datetime))

    return rising_loc, transit_loc, setting_loc


# ================
# ===== main =====
# ================


if __name__ == '__main__':

    # -------------------------
    # ----- parse options -----
    # -------------------------

    import optparse

    output_modes = ('altitude', 'analemma', 'eot', 'default')

    defaults = {'isVerbose': False,
                'output mode': 'default'}

    usage = '%prog [options] <latitude> <longitude> <datetime>'

    parser = optparse.OptionParser(usage=usage)

    parser.add_option('-v', '--verbose',
                      action='store_true', dest='verbose',
                      default=defaults['isVerbose'],
                      help='verbose [%default]')

    parser.add_option('-o', '--output-mode',
                      action='store', dest='output_mode',
                      type='choice', choices=output_modes,
                      default=defaults['output mode'],
                      help='output mode %s' % (output_modes,))

    options, args = parser.parse_args()

    # ----- validate -----

    if len(args) < 3:
        parser.error('missing object and/or datetime.')

    an_observer = AAI.Transforms.utils.latlon2spherical(a_latitude=AAI.Transforms.utils.parse_angle_arg(args[0]),
                                                        a_longitude=AAI.Transforms.utils.parse_angle_arg(args[1]))

    a_datetime = coords.datetime(args[2])

    # ----------------------------------
    # ----- calculate sun position -----
    # ----------------------------------

    if options.output_mode.lower() == 'altitude':

        # a days worth of azimuth and altitude

        current_datetime = coords.datetime()

        for d in xrange(0, 100):

            current_datetime.fromJulianDate(a_datetime.toJulianDate() + 0.01*d)

            sun = SunPosition(an_observer, current_datetime)

            print(0.01*d,)
            print(current_datetime,)
            print(AAI.Transforms.utils.get_azimuth(sun).value,)
            print(AAI.Transforms.utils.get_altitude(sun).value)


    elif options.output_mode.lower() == 'analemma':

        # a years worth of analemma data

        current_datetime = a_datetime

        # TODO duration option
        for d in xrange(1, 365):

            current_datetime += 1

            sun = SunPosition(an_observer, current_datetime)
            eot = EquationOfTime(current_datetime)

            print(eot.value*60 + 180, AAI.Transforms.utils.get_altitude(sun).value)


    elif options.output_mode.lower() == 'eot':

        # years worth of equation of time data

        current_date = a_datetime

        # TODO duration option
        for d in xrange(1, 365):

            current_date += 1
            eot = EquationOfTime(current_date)

            print(d, current_date, eot.value * 60)


    else:

        # azimuth, altitude

        print('A datetime: ', a_datetime, ''.join(('(', str(a_datetime.toJulianDate()), ')')))
        print('An observer:', an_observer)

        ecliptic_longitude, R = SolarLongitude(a_datetime)
        print('Ecliptic longitude:', ecliptic_longitude)
        print('Distance in AU:', R)

        print('Obliquity of the ecliptic:', AAI.Transforms.EclipticEquatorial.obliquity(a_datetime))

        sun_ec = coords.spherical(R, coords.angle(90), ecliptic_longitude)
        print('Sun in ecliptic coordinates:', sun_ec)

        sun_eq = AAI.Transforms.EclipticEquatorial.toEquatorial(sun_ec, a_datetime)
        print('Sun in equatorial coordinates:', sun_eq)

        sun_hz = AAI.Transforms.EquatorialHorizon.toHorizon(sun_eq, an_observer, a_datetime)
        print('Sun in horizon coordinates:', sun_hz)

        sun_dec = coords.angle(90) - sun_eq.theta
        print('Solar Declination:', sun_dec, ''.join(('(', str(sun_dec.value), ')')))

        eot = EquationOfTime(a_datetime)
        print('Equation of time (minutes):', eot.value * 60)

        print('Azimuth (degrees):', AAI.Transforms.utils.get_azimuth(sun_hz),)
        print(''.join(('(', str(AAI.Transforms.utils.get_azimuth(sun_hz).value), ')')))
        print('Altitude (degrees):', AAI.Transforms.utils.get_altitude(sun_hz),)
        print(''.join(('(', str(AAI.Transforms.utils.get_altitude(sun_hz).value), ')')))


        rising, transit, setting = SunRiseAndSet(an_observer, a_datetime)

        print('Rising :', rising)
        print('Transit:', transit)
        print('Setting:', setting)
