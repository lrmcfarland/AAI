#!/usr/bin/env python

"""Transforms 3D space vectors to/from ecliptic/equatorial coordinates

This uses spherical trigonometry from:

    http://en.wikipedia.org/wiki/Celestial_coordinate_system#Equatorial_.E2.86.90.E2.86.92_horizontal


to run: /pylaunch.sh EquatorialHorizon.py -- 6:45:09 -16:42:58 37:24 -122:04:57 2014-12-31T20:41:41

where -- ends options and allows -16 to be a negative number and not option -1.

References:

Celestial Coordinate System
    http://en.wikipedia.org/wiki/Celestial_coordinate_system#Transformation_of_coordinates
    http://en.wikipedia.org/wiki/Celestial_coordinate_system#Equatorial_.E2.86.90.E2.86.92_horizontal

Equatorial Coordinate System
    http://en.wikipedia.org/wiki/Equatorial_coordinate_system



With input from http://star-www.st-and.ac.uk/~fv/webnotes/chapter7.htm,
but I think "chapter7" is incorrect in calculating the Local Hour Angle.

I observed Sirius on New Years Eve 2015 at 8pm and measured its
altitude and azimuth using a theodolite app on my iPhone. I
got:

    Date & Time: Wed Dec 31 20:41:41 PST 2014
    Position: +037.40015* / -122.08219*
    Altitude: 56ft
    Azimuth/Bearing: 127* S53E 2258mils (True)
    Elevation Angle: +18.1*

By happy coincidence, Sirius was on/near my local meridian, due
south, at midnight new years eve, 3 hours after I measured it with
my theodolite app at 8:41 pm above.

According to http://star-www.st-and.ac.uk/~fv/webnotes/chapter6.htm
an alternative definition of LST is "Local Sidereal Time = Right
Ascension of whichever stars are on the meridian."  Therefore,
local sidereal time == right ascension of Sirius == 6* 45' 9"

But according to    http://aa.usno.navy.mil/data/docs/siderealtime.php
this is my Greenwich Mean Sidereal Time; my local sidereal time is 22h 32m
59.9s.

If I let my Local Hour Angle = GMST - RA(star) this matches my
observed results.

"""

import math
import coords

import GMST
import utils


class Error(Exception):
    pass


def toHorizon(an_object, an_observer, a_local_datetime, verbose=False):
    """Transforms a vector from equatorial to horizon coordinates.

    Args:

    an_object: the vector to transform in theta (90 - declination),
               phi (RA * 15). See self.radec2spherical.

    an_observer: the latitude (90 - theta) and longitude (positive
                 east of the prime meridian) of an observer as a
                 spherical coordinate (unit radius)

    a_local_datetime: local date and time of the observation.

    verbose: verbose mode

    Returns a spherical coordinate vector in the transformed coordinates

    """

    if not isinstance(an_object, coords.spherical):
        raise Error('vector must be in spherical coordinates')

    if not isinstance(an_observer, coords.spherical):
        raise Error('observer must be in spherical coordinates')

    gmst = GMST.USNO_C163.GMST(a_local_datetime) # hours
    local_hour_angle = coords.angle(gmst.value*15 - an_object.phi.value)

    if verbose:
        print 'GMST', gmst
        print 'Local Hour Angle', local_hour_angle

    # Altitude = 90 - theta
    theta = coords.angle()

    altitude =  math.cos(an_object.theta.radians) * math.cos(an_observer.theta.radians) + \
                math.sin(an_object.theta.radians) * math.sin(an_observer.theta.radians) * \
                math.cos(local_hour_angle.radians)

    theta.radians = math.acos(altitude)

    if verbose:
        altitude = coords.angle()
        altitude.radians = math.pi/2 - math.acos(altitude)
        print 'altitude', altitude

    # Azimuth = phi - 180
    # "Note that Azimuth (A) is measured from the South point, turning positive to the West."
    phi = coords.angle()

    nom = math.sin(local_hour_angle.radians)
    den = (math.cos(local_hour_angle.radians)*math.sin(math.pi/2 - an_observer.theta.radians) - \
           math.tan(math.pi/2 - an_object.theta.radians) *  math.cos(math.pi/2 - an_observer.theta.radians))

    phi.radians = math.pi + math.atan2(nom, den)

    if verbose:
        azimuth = coords.angle()
        azimuth.radians = math.atan2(nom, den)
        print 'azimuth', azimuth

    return coords.spherical(1, theta, phi)



def toEquatorial(an_object, an_observer, a_local_datetime, verbose=False):
    """Transforms a vector from horizon to equatorial coordinates.

    Args:

    an_object: the vector to transform in theta (90 - altitude),
               phi (azimuth). See self.radec2spherical.

    an_observer: the latitude and longitude (positive west of the
                 prime meridian) of an observer as a spherical
                 coordinate (unit radius)

    a_local_datetime: local date and time of the observation.

    verbose: verbose mode

    Returns a spherical coordinate vector in the transformed coordinates
    """

    if not isinstance(an_object, coords.spherical):
        raise Error('vector must be in spherical coordinates')

    if not isinstance(an_observer, coords.spherical):
        raise Error('observer must be in spherical coordinates')

    gmst = GMST.USNO_C163.GMST(a_local_datetime) # hours

    if verbose:
        print 'GMST', gmst

    # declination = 90 - theta
    theta = coords.angle()

    altitude =  math.cos(an_object.theta.radians) * math.cos(an_observer.theta.radians) - \
                math.sin(an_object.theta.radians) * math.sin(an_observer.theta.radians) * \
                math.cos(an_object.phi.radians - math.pi)

    theta.radians = math.acos(altitude)

    if verbose:
        declination = coords.angle()
        declination.radians = math.pi/2 - math.acos(altitude)
        print 'declination', declination

    # Azimuth = phi - 180
    # "Note that Azimuth (A) is measured from the South point, turning positive to the West."
    phi = coords.angle()

    nom = math.sin(an_object.phi.radians - math.pi)
    den = (math.cos(an_object.phi.radians - math.pi)*math.sin(math.pi/2 - an_observer.theta.radians) + \
           math.tan(math.pi/2 - an_object.theta.radians) *  math.cos(math.pi/2 - an_observer.theta.radians))


    azimuth = math.atan2(nom, den)

    phi.radians = gmst.radians*15 - azimuth
    phi.normalize(0, 360)

    if verbose:
        ra = coords.angle()
        ra.radians = gmst.radians*15 - math.atan2(nom, den)
        ra /= coords.angle(15)
        print 'R.A.', ra

    return coords.spherical(1, theta, phi)


# ================
# ===== main =====
# ================


if __name__ == '__main__':

    # -------------------------
    # ----- parse options -----
    # -------------------------

    import optparse

    defaults = {'toEquatorial' : False,
                'verbose': False}

    usage = '%prog [options] <RA as deg:min:sec> <dec as deg:min:sec> <observer latitude as deg:min:sec> <observer longitude as deg:min:sec> <a datetime>'

    parser = optparse.OptionParser(usage=usage)

    parser.add_option('-v', '--verbose',
                      action='store_true', dest='verbose',
                      default=defaults['verbose'],
                      help='verbose [%default]')

    parser.add_option('--toEquatorial',
                      action='store_true', dest='toEquatorial',
                      default=defaults['toEquatorial'],
                      help='to equatorial [%default]')

    options, args = parser.parse_args()

    # ----- validate -----

    if len(args) < 5:
        parser.error('missing object RA, DEC or observer latitude, longitude or datetime.')

    RA = utils.parse_angle_arg(args[0])
    dec = utils.parse_angle_arg(args[1])

    lat = utils.parse_angle_arg(args[2])
    lon = utils.parse_angle_arg(args[3])

    an_object = utils.radec2spherical(a_right_ascension=RA, a_declination=dec)
    an_observer = coords.spherical(1, coords.angle(90) - lat, lon)

    a_datetime = coords.datetime(args[4])

    # TODO validate toEquatorial/toHorizon option logic

    # ---------------------
    # ----- transform -----
    # ---------------------

    if options.toEquatorial == True:
        result = toEquatorial(an_object, an_observer, a_datetime, options.verbose)

    else:
        result = toHorizon(an_object, an_observer, a_datetime, options.verbose)


    print result

    # TODO add print options for output in RA and Dec
