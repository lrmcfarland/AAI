#!/usr/bin/env python

""" Transforms from Astronomy on the Personal Computer (APC)
    by Montenbruck and Pfleger

    TODO: not all of my implementations of this are working. Check unittests.
"""

import math
import coords


horizon_axis = coords.rotator(coords.Uy)


def GMST(a_datetime):
    """Greenwich mean sidereal time

    APC p. 40

    Returns GMST in hours
    """

    MJD  = a_datetime.toJulianDate() - a_datetime.ModifiedJulianDate
    MJDo = math.floor(MJD)

    UT   = (MJD - MJDo) * 86400.0

    To   = (MJDo - 51544.5)/36525.0
    T    = (MJD  - 51544.5)/36525.0

    gmst = 24110.54841 + 8640184.812866*To + 1.0027379093*UT + (0.093104 - 6.2e-6*T)*T*T # in seconds

    gmst_angle = coords.angle(gmst/3600.0)

    gmst_angle.normalize(0, 24)

    return gmst_angle


def _xform(an_object, an_observer, a_datetime, a_direction):
    """Transforms a vector to/from equatorial/ecliptic coordinates.

    TODO my implementation of this APC algorithm isn't working

    Args:

    an_object (coords.spherical): the RA and Dec or ecliptic longitude
    and latitude as a spherical coordinate where theta is the
    complement of latitude and longitude is measured positive east in
    degrees.

    an_observer (coords.spherical): the latitude and longitude
    (positive east of the prime meridian) of an observer as a
    spherical coordinate where theta is the complement of latitude and
    longitude is measured positive east in degrees.

    a_datetime (coords.datetime): The time of the observation.

    a_direction (int): +1 to horizon, -1 from horizon

    Returns (coords.spherical): a vector in the transformed coordinates
    """

    if not isinstance(an_object, coords.spherical):
        raise Error('vector must be in spherical coordinates')

    if not isinstance(an_observer, coords.spherical):
        raise Error('observer must be in spherical coordinates')

    gmst = GMST(a_datetime)
    hour_angle = coords.angle(gmst.value*15 - an_object.phi.value)
    the_local_vector = coords.spherical(an_object.r, an_object.theta, hour_angle)
    the_rotatee = coords.Cartesian(the_local_vector)
    the_rotated = horizon_axis.rotate(the_rotatee, coords.angle(a_direction * an_observer.theta.value))
    the_result = coords.spherical(the_rotated)

    # "Note that Azimuth (A) is measured from the South point, turning positive to the West."
    # adjust azimuth to phi from the north
    the_result.phi += coords.angle(180)

    return the_result


def toHorizon(an_object, an_observer, a_datetime):
    """Transforms an equatorial vector into one in the horizon coordinate system

    an_object (coords.spherical): the RA and Dec or ecliptic longitude
    and latitude as a spherical coordinate where theta is the
    complement of latitude and longitude is measured positive east in
    degrees.

    an_observer (coords.spherical): the latitude and longitude
    (positive east of the prime meridian) of an observer as a
    spherical coordinate where theta is the complement of latitude and
    longitude is measured positive east in degrees.

    a_datetime (coords.datetime): The time of the observation.
    """
    return _xform(an_object, an_observer, a_datetime, -1.0)


def toEquatorial(an_object, an_observer, a_datetime):
    """Transforms a horizon vector into one in the equatorial coordinate system

    an_object (coords.spherical): the RA and Dec or ecliptic longitude
    and latitude as a spherical coordinate where theta is the
    complement of latitude and longitude is measured positive east in
    degrees.

    an_observer (coords.spherical): the latitude and longitude
    (positive east of the prime meridian) of an observer as a
    spherical coordinate where theta is the complement of latitude and
    longitude is measured positive east in degrees.

    a_datetime (coords.datetime): The time of the observation.
    """
    return _xform(an_object, an_observer, a_datetime, 1.0)
