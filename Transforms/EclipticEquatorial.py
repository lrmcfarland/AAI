#!/usr/bin/env python

"""Transforms coordinates to/from Ecliptic, Equatorial


References:

Celestial Coordinate System
    http://en.wikipedia.org/wiki/Celestial_coordinate_system#Transformation_of_coordinates
    http://en.wikipedia.org/wiki/Celestial_coordinate_system#Equatorial_.E2.86.90.E2.86.92_horizontal

Equatorial Coordinate System
    http://en.wikipedia.org/wiki/Equatorial_coordinate_system

Ecliptic Coordinate System
    http://en.wikipedia.org/wiki/Ecliptic
    http://en.wikipedia.org/wiki/Ecliptic_coordinate_system
    http://en.wikipedia.org/wiki/Axial_tilt

Validation:
    http://lambda.gsfc.nasa.gov/toolbox/tb_converters_ov.cfm

"""

import math
import coords

import GMST
import utils

class Error(Exception):
    pass


class EclipticEquatorial(object):

    """Transforms 3D space vectors to/from ecliptic/equatorial coordinates

    ASSUMES: The x-axis points to vernal equinox. Positive rotations are right hand rule,
    Y x Z = X, i.e. counter clockwise looking down X.

    from:
        http://en.wikipedia.org/wiki/Axial_tilt

    See also:
        http://lambda.gsfc.nasa.gov/toolbox/tb_coordconv.cfm
        http://aa.usno.navy.mil/publications/docs/Circular_163.pdf

    """

    # x axis points to vernal equinox (the first point of Aries in this epoch)
    equinox_axis = coords.rotator(coords.Ux)

    # obliquity of the ecliptic terms are from http://en.wikipedia.org/wiki/Axial_tilt
    obe = list()
    obe.append(coords.angle(23, 26, 21.45))
    obe.append(coords.angle(-1)*coords.angle(0, 0, 46.815)) # TODO no unary minus in boost wrappers
    obe.append(coords.angle(-1)*coords.angle(0, 0, 0.0006))
    obe.append(coords.angle(0, 0, 0.00181))
    # TODO more terms, updated


    def __init__(self, *args, **kwargs):
        super(EclipticEquatorial, self).__init__(*args, **kwargs)


    @classmethod
    def eps(cls, a_datetime):
        """Calculates the obliquity of the ecliptic given the datetime"""
        T = utils.JulianCentury(a_datetime)
        the_eps = 0
        for i in xrange(len(cls.obe)):
            the_eps += cls.obe[i].value * math.pow(T, i)
        return the_eps


    @classmethod
    def _xform(cls, an_object, a_datetime, a_direction):
        """Transforms a vector to/from equatorial/ecliptic coordinates.

        Args:
        an_object: the vector to transform. May be Cartesian or spherical.
        a_datetime: the time of the transformation
        a_direction: +1 to equatorial, -1 to ecliptic

        Returns a vector in the transformed coordinates
        """

        if isinstance(an_object, coords.spherical):
            the_rotatee = coords.Cartesian(an_object)
        else:
            the_rotatee = an_object

        the_rotated = cls.equinox_axis.rotate(the_rotatee,
                                              coords.angle(a_direction * cls.eps(a_datetime)))

        if isinstance(an_object, coords.spherical):
            return coords.spherical(the_rotated)
        else:
            return the_rotated


    @classmethod
    def toEcliptic(cls, an_object, a_datetime):
        """Transforms an_object from equatorial to ecliptic coordinates

        Returns a Cartesian vector in eliptic coordinates
        """
        return cls._xform(an_object, a_datetime, -1.0)


    @classmethod
    def toEquatorial(cls, an_object, a_datetime):
        """Transforms an_object from ecliptic to equatorial coordinates

        Returns a Cartesian vector in equatorial coordinates
        """
        return cls._xform(an_object, a_datetime, 1.0)

