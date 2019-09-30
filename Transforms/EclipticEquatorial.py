#!/usr/bin/env python

"""Transforms coordinates to/from Ecliptic, Equatorial


ASSUMES: The x-axis points to vernal equinox. Positive rotations are right hand rule,
Y x Z = X, i.e. counter clockwise looking down X.


References:

Celestial Coordinate System
    http://en.wikipedia.org/wiki/Celestial_coordinate_system#Transformation_of_coordinates
    http://en.wikipedia.org/wiki/Celestial_coordinate_system#Equatorial_.E2.86.90.E2.86.92_horizontal
    http://aa.usno.navy.mil/publications/docs/Circular_163.pdf

Equatorial Coordinate System
    http://en.wikipedia.org/wiki/Equatorial_coordinate_system

Ecliptic Coordinate System
    http://en.wikipedia.org/wiki/Ecliptic
    http://en.wikipedia.org/wiki/Ecliptic_coordinate_system
    http://en.wikipedia.org/wiki/Axial_tilt

Validation:
    http://lambda.gsfc.nasa.gov/toolbox/tb_coordconv.cfm

"""

from __future__ import absolute_import # for python 2 and 3

import math
import coords

import Transforms.utils


class Error(Exception):
    pass


# x axis points to vernal equinox (the first point of Aries in this epoch)
equinox_axis = coords.rotator(coords.Cartesian.Ux)

# obliquity of the ecliptic terms are from http://en.wikipedia.org/wiki/Axial_tilt
obe = list()
obe.append(coords.angle(23, 26, 21.45))
obe.append(coords.angle(-1)*coords.angle(0, 0, 46.815)) # TODO no unary minus in boost wrappers
obe.append(coords.angle(-1)*coords.angle(0, 0, 0.0006))
obe.append(coords.angle(0, 0, 0.00181))
# TODO more terms, updated


def obliquity(a_datetime):
    """Calculates the obliquity of the ecliptic given the datetime

    a_datetime (coords.datetime): The time of the observation.
    """
    T = Transforms.utils.JulianCentury(a_datetime)
    eps = 0
    for i in range(len(obe)):
        eps += obe[i] * math.pow(T, i)
    return coords.angle(eps)


def _xform(an_object, a_datetime, a_direction):
    """Transforms a vector to/from equatorial/ecliptic coordinates.

    Args:

    an_object (coords.spherical): the RA and Dec or ecliptic longitude
    and latitude as a spherical coordinate where theta is the
    complement of latitude and longitude is measured positive east in
    degrees.

    a_datetime (coords.datetime): The time of the observation.

    a_direction (int): +1 to equatorial, -1 to ecliptic

    Returns: coords.spherical in the transformed coordinates.
    """

    if not isinstance(an_object, coords.spherical):
        raise Error('object must be in spherical coordinates')

    the_rotatee = coords.Cartesian(an_object)

    the_rotated = equinox_axis.rotate(the_rotatee, coords.angle(a_direction) * obliquity(a_datetime))

    if isinstance(an_object, coords.spherical):
        return coords.spherical(the_rotated)
    else:
        return the_rotated


def toEcliptic(an_object, a_datetime):
    """Transforms an_object from equatorial to ecliptic coordinates

    Args:

    an_object (coords.spherical): the RA and Dec as a spherical
    coordinate where theta is the complement of latitude and longitude
    is measured positive east in degrees.

    a_datetime (coords.datetime): The time of the observation.

    Returns: coords.spherical in the transformed coordinates.

    """
    return _xform(an_object, a_datetime, -1.0)


def toEquatorial(an_object, a_datetime):
    """Transforms an_object from ecliptic to equatorial coordinates

    Args:

    an_object (coords.spherical): the ecliptic longitude and latitude
    as a spherical coordinate where theta is the complement of
    latitude and longitude is measured positive east in degrees.

    a_datetime (coords.datetime): The time of the observation.

    Returns: coords.spherical in the transformed coordinates.

    """
    return _xform(an_object, a_datetime, 1.0)



class Meeus(object):
    """Wrapper for Meeus' implementations

    This works better with his non-IAU conventions.

    See Astronomical Algorithms 2ed. Chapter 13 Transformation of Coordinates

    """

    @staticmethod
    def toEcliptic(an_object, a_datetime):
        """Transform equatorial into ecliptical coordinates

        Args:

        an_object (coords.spherical): the RA and Dec as a spherical
        coordinate where theta is the complement of latitude and
        longitude is measured positive east in degrees.

        a_datetime (coords.datetime): The time of the observation.

        Returns: the object in spherical coordinates based on the ecliptic.

        """

        if not isinstance(an_object, coords.spherical):
            raise Error('object must be in spherical coordinates')

        eps = obliquity(a_datetime) # see above

        a_RA = coords.angle(15.0 * an_object.phi.RA) # convert to degrees

        a_dec = an_object.theta.complement()

        # Meeus eqn. 13.1
        ecLon = coords.angle()
        ecLon.radians = math.atan2(math.sin(a_RA.radians)*math.cos(eps.radians) + math.tan(a_dec.radians)*math.sin(eps.radians), math.cos(a_RA.radians))

        # Meeus eqn. 13.2
        ecLat = coords.angle()
        ecLat.radians = math.asin(math.sin(a_dec.radians)*math.cos(eps.radians) - math.cos(a_dec.radians)*math.sin(eps.radians)*math.sin(a_RA.radians))

        return Transforms.utils.latlon2spherical(ecLat, ecLon)


    @staticmethod
    def toEquatorial(an_object, a_datetime):
        """Transform ecliptical into equatorial coordinates

        Args:

        an_object (coords.spherical): the ecliptic longitude and
        latitude as a spherical coordinate where theta is the
        complement of latitude and longitude is measured positive east
        in degrees.

        a_datetime (coords.datetime): The time of the observation.

        Returns: the object in spherical coordinates based on the ecliptic.

        """

        if not isinstance(an_object, coords.spherical):
            raise Error('object must be in spherical coordinates')

        eps = obliquity(a_datetime) # see above

        a_lat = an_object.theta.complement()
        a_lon = an_object.phi


        # Meeus eqn. 13.3
        eqLon = coords.angle()
        eqLon.radians = math.atan2(math.sin(a_lon.radians)*math.cos(eps.radians) - math.tan(a_lat.radians)*math.sin(eps.radians), math.cos(a_lon.radians))


        # Meeus eqn. 13.4
        eqLat = coords.angle()
        eqLat.radians = math.asin(math.sin(a_lat.radians)*math.cos(eps.radians) + math.cos(a_lat.radians)*math.sin(eps.radians)*math.sin(a_lon.radians))


        return Transforms.utils.latlon2spherical(eqLat, eqLon)






# ================
# ===== main =====
# ================


if __name__ == '__main__':

    # -------------------------
    # ----- parse options -----
    # -------------------------

    import optparse

    defaults = {'toEcliptic' : False}

    usage = '%prog [options] <RA as deg:min:sec> <dec as deg:min:sec> <a datetime>'

    parser = optparse.OptionParser(usage=usage)

    parser.add_option('--toEcliptic',
                      action='store_true', dest='toEcliptic',
                      default=defaults['toEcliptic'],
                      help='to ecliptic [%default]')

    options, args = parser.parse_args()

    # ----- validate -----

    if len(args) < 3:
        parser.error('missing object and/or datetime.')

    an_object = Transforms.utils.radec2spherical(a_right_ascension=utils.parse_angle_arg(args[0]),
                                                 a_declination=utils.parse_angle_arg(args[1]))

    a_datetime = coords.datetime(args[2])

    # TODO validate toEcliptic/toEquatorial option logic

    # ---------------------
    # ----- transform -----
    # ---------------------

    if options.toEcliptic is True:
        result = toEcliptic(an_object, a_datetime)
        print('Ecliptic Latitude:', result.theta.complement(), ', Longitude:', result.phi)

    else:
        result = toEquatorial(an_object, a_datetime)
        print('RA:', result.phi.RA, ', Dec:', result.theta.complement().degrees)
