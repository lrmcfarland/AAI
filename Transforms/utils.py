#!/usr/bin/env python

"""Utilities for transforms

"""

import math
import re

import coords


class Error(Exception):
    pass


angle_re = re.compile(r'(-){0,1}(\d+)(:\d+){0,1}(:\d+\.?\d+){0,1}') # TODO limits 0-360, 0-60, etc

def parse_angle_arg(an_arg):
    """Parse angle arg as dd:mm:ss.sss"""

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


def get_latitude(a_point):
    """Spherical to latitude

    Converts spherical coordinate theta (angle to +z axis) to
    latitude/declination.

    Returns an angle with a value equal to the latitude.
    """

    if not isinstance(a_point, coords.spherical):
        raise Error('a coordinate must be an instance of coords.spherical')

    return a_point.theta.complement()


def get_longitude(a_point):
    """Spherical to longitude

    Converts spherical coordinate phi (angle to +x axis of
    projection in xy plane) to longitude.

    Returns an angle with a value equal to the longitude.
    """

    if not isinstance(a_point, coords.spherical):
        raise Error('a coordinate must be an instance of coords.spherical')

    if a_point.phi.value < 0:
        return coords.angle(coords.angle(360) + a_point.phi)
    else:
        return a_point.phi


def get_RA(a_point):
    """Spherical to right ascension

    Converts spherical coordinate phi (angle to +x axis of
    projection in xy plane) to right ascension.

    Returns an angle value equal to the right ascension.
    """

    return coords.angle(get_longitude(a_point).value/15.0)


def radec2spherical(a_right_ascension, a_declination, a_radius = 1):
    """Converts a given right ascension and declination into spherical coordinates

    Declination measured from the ecliptic and is converted to theta
    measured from the north pole.

    Right ascension measured in hours is converted into degrees and assigned
    to phi.

    Returns coords.spherical.
    """
    return coords.spherical(a_radius, coords.angle(90.0) - a_declination,
                            coords.angle(a_right_ascension.value * 15))


def altaz2spherical(an_altitude, an_azimuth, a_radius = 1):
    """Converts a given altitude and azimuth into spherical coordinates

    Altitude is measured from the horizon is converted to theta
    measured from the north pole.

    Azimuth is measured from the meridian and is converted into
    degrees and assigned to phi.

    Returns coords.spherical.
    """
    return coords.spherical(a_radius, coords.angle(90.0) - an_altitude, an_azimuth)


def JulianCentury(a_datetime):
    """Calculates the Julian century relative to J2000 of the given date

    Args:

    a_datetime: local date and time of the observation.

    Returns a double equal to the Julian century.
    """
    return (a_datetime.toJulianDate() - a_datetime.J2000)/36525.0
