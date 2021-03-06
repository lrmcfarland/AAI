#!/usr/bin/env python

"""Utilities for transforms"""

import math
import re

import coords


class Error(Exception):
    pass


angle_re = re.compile(r'(-){0,1}(\d+)(:\d+){0,1}(:\d+\.?\d+){0,1}') # TODO limits 0-360, 0-60, etc

def parse_angle_arg(an_arg):
    """Parse angle arg as a string of dd:mm:ss.sss"""

    degrees = 0
    minutes = 0
    seconds = 0

    if not angle_re.match(an_arg):
        raise Error('Unsupported angle format: %s' % (an_arg,))

    words = an_arg.split(':')

    if len(words) == 3:
        degrees = float(words[0])
        minutes = float(words[1])
        seconds = float(words[2])
    elif len(words) == 2:
        degrees = float(words[0])
        minutes = float(words[1])
    elif len(words) == 1:
        degrees = float(words[0])
    else:
        raise Error('Unsupported format')

    result = coords.angle(degrees, minutes, seconds)

    return result


def JulianCentury(a_datetime):
    """Calculates the Julian century relative to J2000 of the given date

    Meeus eq. 22.1, p. 143

    Args:

        a_datetime: local date and time of the observation in coords.datetime

    Returns a double equal to the Julian century.
    """
    return (a_datetime.toJulianDate() - a_datetime.J2000)/36525.0


def azalt2spherical(an_azimuth, an_altitude, a_radius=1):
    """Converts a given altitude and azimuth into spherical coordinates

    Args:

        Azimuth (coords.angle): is measured from the anti-meridian
    (north, positive east following IAU standard) and is converted
    into degrees and assigned to phi.

        Altitude (coords.angle): is measured from the horizon is
    converted to theta measured from the north pole.

    Returns coords.spherical.
    """

    return coords.spherical(a_radius, an_altitude.complement(), an_azimuth)


def latlon2spherical(a_latitude, a_longitude, a_radius=1):
    """Converts a given latitude and longitude into spherical coordinates

    Args:

        latitude (coords.angle): is measured in degrees from the
    equator and is converted to theta measured from the axis of the
    north pole.

        longitude (coords.angle): is measured in degrees from the
    prime merdian.

    Returns coords.spherical.
    """

    return coords.spherical(a_radius, a_latitude.complement(),
                            coords.angle(a_longitude))


def radec2spherical(a_right_ascension, a_declination, a_radius=1):
    """Converts a given right ascension and declination into spherical coordinates

    Args:

        Right ascension (coords.angle): is measured in hours from the
    vernal equinox and converted into degrees.

        Declination (coords.angle): is measured in degrees from the
    ecliptic and is converted to theta measured from the axis of the
    north pole.

    Returns coords.spherical.
    """

    if a_right_ascension.RA < 0 or a_right_ascension.RA > 24:
        raise Error('Right Ascension out of range: %s' % (a_right_ascension,))

    return coords.spherical(a_radius, a_declination.complement(), a_right_ascension * 15)
