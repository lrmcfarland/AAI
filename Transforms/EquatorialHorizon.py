#!/usr/bin/env python

"""Transforms 3D space vectors to/from ecliptic/equatorial coordinates


TODO in transition to Meeus formulas. Needs to resolve coords.spherical all in degrees or include RA?
TODO create degree/RA child classes of angle to type check this?


This forward/reverse works at this checkpoint:


[Transforms (eqhz2azalt)]$ ./pylaunch.sh EquatorialHorizon.py -v -- 23:09:16.641 -6:43:11.61 38:55:17 -77:03:56 1987-04-10T19:21:00
# COORDS_ROOT not set. Using ..
# coords.so: ../Coordinates/Python/Manual/build/lib.macosx-10.9-intel-2.7/coords.so
# DYLD_LIBRARY_PATH :../Coordinates/libCoords
# PYTHONPATH :../Coordinates/Python/Manual/build/lib.macosx-10.9-intel-2.7:..

GAST 08:34:56.8371
observer longitude -77.0655555556
object latitude -6.71989166667
local hour angle 64.3519283778
altitude: 15:07:30.0779 ( 15.1250216498 )
azimuth: 248:02:0.776767 ( 248.033549102 )
Azimuth: 248:02:0.776767 ( 68:02:0.776767  south) , Altitude: 15:07:30.0779



[Transforms (eqhz2azalt)]$ ./pylaunch.sh EquatorialHorizon.py -v --toEquatorial -- 248:02:0.776767 15:07:30.0779 38:55:17 -77:03:56 1987-04-10T19:21:00
# COORDS_ROOT not set. Using ..
# coords.so: ../Coordinates/Python/Manual/build/lib.macosx-10.9-intel-2.7/coords.so
# DYLD_LIBRARY_PATH :../Coordinates/libCoords
# PYTHONPATH :../Coordinates/Python/Manual/build/lib.macosx-10.9-intel-2.7:..

declination -6:43:11.61
GAST 08:34:56.8371
observer ra -5:08:15.7333
local hour angle 64.3519283858
Object R.A. 23:05:34.1616 ( 23.0928226727 )
Equatorial Latitude: -6:43:11.61 , Longitude: 346:23:32.4243


Works for Sirius when time zone is accounted for:

[mcfarl@usxxmcfarlm1 Transforms (eqhz2azalt)]$ ./pylaunch.sh EquatorialHorizon.py -v -- 6:45:08.9173 -16:42:58.017 37:24 -122:04:57 2015-01-01T08:00:00
# COORDS_ROOT not set. Using ..
# coords.so: ../Coordinates/Python/Manual/build/lib.macosx-10.9-intel-2.7/coords.so
# DYLD_LIBRARY_PATH :../Coordinates/libCoords
# PYTHONPATH :../Coordinates/Python/Manual/build/lib.macosx-10.9-intel-2.7:..

GAST 14:42:38.2855
observer longitude -122.0825
object latitude -16.7161158333
local hour angle 357.289867328
altitude: 35:49:25.4196 ( 35.8237276719 )
azimuth: 176:47:53.9568 ( 176.798321326 )
Azimuth: 176:47:53.9568 ( -3:12:6.04323  south) , Altitude: 35:49:25.4196





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


def toHorizon(an_object, an_observer, a_utc_datetime, is_verbose=False):
    """Transforms a coordinate vector from equatorial to horizon coordinates.

    Args:

    an_object (coords.spherical): in degrees from RA/dec.

    TODO: validate RA in hours?

    an_observer (coords.spherical): the latitude and longitude
    (positive east of the prime azimuth) of an observer as a spherical
    coordinate (unit radius), e.g. CA is 34 latitude, -122 longitude


    TODO: positive east IAU vs. Meeus positive west issue, p. 93

    a_utc_datetime (ISO8601 string): UTC date and time of the
    observation.

    is_verbose (bool): verbose mode.

    Returns: coords.spherical in the transformed coordinates.

    """

    if not isinstance(an_object, coords.spherical):
        raise Error('vector must be in spherical coordinates')

    if not isinstance(an_observer, coords.spherical):
        raise Error('observer must be in spherical coordinates')

    gast = GMST.USNO_C163.GAST(a_utc_datetime) - coords.angle(a_utc_datetime.timezone()) # hours

    local_hour_angle = coords.angle(gast.value*15 + an_observer.phi.value - an_object.phi.value)
    local_hour_angle.normalize(0, 360)

    if is_verbose:
        print 'datetime', a_utc_datetime.toJulianDate()
        print 'GAST', gast
        print 'observer longitude', utils.get_longitude(an_observer).value
        print 'object latitude', utils.get_latitude(an_object).value
        print 'local hour angle', local_hour_angle.value

    # Meeus 13.6
    sinaltitude =  math.sin(utils.get_latitude(an_observer).radians) * \
                   math.sin(utils.get_declination(an_object).radians) + \
                   math.cos(utils.get_latitude(an_observer).radians) * \
                   math.cos(utils.get_declination(an_object).radians) * \
                   math.cos(local_hour_angle.radians)

    theta = coords.angle(coords.angle().rad2deg(math.pi/2 - math.asin(sinaltitude)))

    if is_verbose:
        print 'altitude:', theta.complement(), '(', theta.complement().value, ')' # Altitude = 90 - theta

    # Meeus 13.5
    nom = math.sin(local_hour_angle.radians)
    den = math.cos(local_hour_angle.radians)*math.sin(utils.get_latitude(an_observer).radians) - \
          math.tan(utils.get_declination(an_object).radians) *  math.cos(utils.get_latitude(an_observer).radians)


    # "Note that Azimuth (A) is measured from the South point, turning positive to the West."
    phi = coords.angle(coords.angle().rad2deg(math.atan2(nom, den) + math.pi))

    if is_verbose:
        print 'azimuth:', phi, '(', phi.value, ')'

    return coords.spherical(1, theta, phi)



def toEquatorial(an_object, an_observer, a_utc_datetime, is_verbose=False):
    """Transforms a coordinate vector from horizon to equatorial coordinates.

    Args:

    an_object (coords.spherical): in altitude and azimuth or RA (TODO hours?) and dec. in degrees

    an_observer (coords.spherical): the latitude and longitude
    (positive east of the prime azimuth) of an observer as a spherical
    coordinate (unit radius).

    a_utc_datetime (ISO8601 string): UTC date and time of the
    observation.

    is_verbose (bool): verbose mode.

    Returns: coords.spherical in the transformed coordinates.
    """

    if not isinstance(an_object, coords.spherical):
        raise Error('vector must be in spherical coordinates')

    if not isinstance(an_observer, coords.spherical):
        raise Error('observer must be in spherical coordinates')


    altitude = an_object.theta.complement()

    # The calculation assumes "that Azimuth (A) is measured from the
    # South point, turning positive to the West". coords.spherical
    # assumes azimuth is measured from the north.
    azimuth = coords.angle(an_object.phi.value - 180)

    # Meeus, p. 94
    sindec =  math.sin(utils.get_latitude(an_observer).radians) * math.sin(altitude.radians) - \
              math.cos(utils.get_latitude(an_observer).radians) * math.cos(altitude.radians) * \
              math.cos(azimuth.radians)

    object_dec = coords.angle(coords.angle().rad2deg(math.asin(sindec)))

    if is_verbose:
        print 'declination', object_dec

    # Meeus, p. 94
    nom = math.sin(azimuth.radians)
    den = math.cos(azimuth.radians)  *  math.sin(utils.get_latitude(an_observer).radians) + \
          math.tan(altitude.radians) *  math.cos(utils.get_latitude(an_observer).radians)

    local_hour_angle = coords.angle()
    local_hour_angle.radians = math.atan2(nom, den)
    local_hour_angle.normalize(0, 360)

    gast = GMST.USNO_C163.GAST(a_utc_datetime) - coords.angle(a_utc_datetime.timezone()) # hours

    observer_ra = coords.angle(an_observer.phi.value/15)

    object_ra = coords.angle(gast.value + observer_ra.value - local_hour_angle.value - 12) # 12 for azimuth north
    object_ra.normalize(0, 24)

    if is_verbose:
        print 'datetime', a_utc_datetime.toJulianDate()
        print 'GAST', gast
        print 'observer ra', observer_ra
        print 'local hour angle', local_hour_angle.value
        print 'Object R.A.', object_ra, '(', object_ra.value, ')'

    # return coords.spherical(1, dec.complement(), ra)
    return utils.radec2spherical(a_right_ascension=object_ra, a_declination=object_dec)



# ================
# ===== main =====
# ================


if __name__ == '__main__':

    # -------------------------
    # ----- parse options -----
    # -------------------------

    import optparse

    defaults = {'toEquatorial' : False,
                'isAzimuthSouth': False,
                'isVerbose': False}

    usage = '%prog [options] <RA/azimuth as deg:min:sec> <dec/altitude as deg:min:sec> <observer latitude as deg:min:sec> <observer longitude as deg:min:sec +west> <a datetime>'

    parser = optparse.OptionParser(usage=usage)

    parser.add_option('--toEquatorial',
                      action='store_true', dest='toEquatorial',
                      default=defaults['toEquatorial'],
                      help='to equatorial [%default]')

    parser.add_option('-v', '--verbose',
                      action='store_true', dest='verbose',
                      default=defaults['isVerbose'],
                      help='verbose [%default]')

    options, args = parser.parse_args()

    # ----- validate -----

    if len(args) < 5:
        parser.error('missing object RA, DEC or observer latitude, longitude or datetime.')

    lat = coords.angle(90) - utils.parse_angle_arg(args[2])
    lon = utils.parse_angle_arg(args[3])

    an_observer = coords.spherical(1, lat, lon)

    a_datetime = coords.datetime(args[4])

    # TODO validate toEquatorial/toHorizon option logic

    # ---------------------
    # ----- transform -----
    # ---------------------

    if options.toEquatorial == True:

        an_object = utils.azalt2spherical(an_azimuth=utils.parse_angle_arg(args[0]),
                                          an_altitude=utils.parse_angle_arg(args[1]))

        result = toEquatorial(an_object, an_observer, a_datetime, is_verbose=options.verbose)

        print 'Equatorial Latitude:', utils.get_latitude(result),
        print ', Longitude:', result.phi,

    else:

        an_object = utils.radec2spherical(a_right_ascension=utils.parse_angle_arg(args[0]),
                                          a_declination=utils.parse_angle_arg(args[1]))

        result = toHorizon(an_object, an_observer, a_datetime, is_verbose=options.verbose)

        print 'Azimuth:', result.phi,
        print '(', coords.angle(result.phi.value - 180), ' south)',
        print ', Altitude:', result.theta.complement(),
