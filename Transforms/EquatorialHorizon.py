#!/usr/bin/env python

"""Transforms 3D space vectors to/from ecliptic/equatorial coordinates

Conventions (different from Meeus):
        timezone is added to UTC, e.g. UTC (00:00) = local time (16:00 PST day - 1) + time zone (-08)
        Azimuth is from the North positive east in degrees when stored in a coords.spherical object (Navigator's not Astronomer's preference).
        Longitude is positive east in degrees, e.g. MV is -122 Latitude
        Theta is from the north pole in degrees
        altitude is in degrees from the horizon
        RA is in hours from the x-axis (vernal equinox) when stored in a coords.spherical
        declination is in degrees from the ecliptic.


to run: /pylaunch.sh EquatorialHorizon.py -- 6:45:09 -16:42:58 37:24 -122:04:57 2014-12-31T20:41:41

where -- ends options and allows -16 to be a negative number and not option -1.

$ ./pylaunch.sh EquatorialHorizon.py -v -- 23:09:16.641 -6:43:11.61 38:55:17 -77:03:56 1987-04-10T19:21:00
# COORDS_ROOT not set. Using ..
# coords.so: ../Coordinates/Python/Manual/build/lib.macosx-10.9-intel-2.7/coords.so
# DYLD_LIBRARY_PATH :../Coordinates/libCoords
# PYTHONPATH :../Coordinates/Python/Manual/build/lib.macosx-10.9-intel-2.7:..

Datetime: 2446896.30625
GAST: 08:34:56.8371
Local hour angle: 64.3519283778
Observer longitude: -77.0655555556
Object latitude: -6.71989166667
Altitude: 15:07:30.0779 ( 15.1250216498 )
Azimuth: 248:02:0.776767 ( 248.033549102 )
Azimuth: 248:02:0.776767 ( 68:02:0.776767  south) , Altitude: 15:07:30.0779

$ ./pylaunch.sh EquatorialHorizon.py -v --toEquatorial -- 248:02:0.776767 15:07:30.0779 38:55:17 -77:03:56 1987-04-10T19:21:00
# COORDS_ROOT not set. Using ..
# coords.so: ../Coordinates/Python/Manual/build/lib.macosx-10.9-intel-2.7/coords.so
# DYLD_LIBRARY_PATH :../Coordinates/libCoords
# PYTHONPATH :../Coordinates/Python/Manual/build/lib.macosx-10.9-intel-2.7:..

Datetime: 2446896.30625
GAST: 08:34:56.8371
Local hour angle: 64.3519283858
Object declination -6:43:11.61
Object longitude: 347:19:9.61497 ( 347.319337492 )
Object R.A.: 23:09:16.641 ( 23.1546224995 )
Equatorial Latitude: -6:43:11.61 , Longitude: 347:19:9.61497


References:

Astronomical Algorithms 2ed, Jean Meeus ISBN 0-943396-61-1

Celestial Coordinate System
    http://en.wikipedia.org/wiki/Celestial_coordinate_system#Transformation_of_coordinates
    http://en.wikipedia.org/wiki/Celestial_coordinate_system#Equatorial_.E2.86.90.E2.86.92_horizontal

Equatorial Coordinate System
    http://en.wikipedia.org/wiki/Equatorial_coordinate_system

"""

import math
import coords

import GMST
import utils


class Error(Exception):
    pass


def toHorizon(an_object, an_observer, a_local_datetime, is_verbose=False):
    """Transforms a coordinate vector from equatorial to horizon coordinates.

    Astronomical Algorithms 2ed, Jean Meeus ISBN 0-943396-61-1

    TODO: validate RA in hours?
    TODO: positive east IAU vs. Meeus positive west issue, p. 93

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

    is_verbose (bool): verbose mode.

    Returns (coords.spherical): the object in the transformed coordinates.
    """

    if not isinstance(an_object, coords.spherical):
        raise Error('vector must be in spherical coordinates')

    if not isinstance(an_observer, coords.spherical):
        raise Error('observer must be in spherical coordinates')

    gast = GMST.USNO_C163.GAST(a_local_datetime) - coords.angle(a_local_datetime.timezone()) # hours

    local_hour_angle = coords.angle(gast.value*15 + an_observer.phi.value - an_object.phi.value)
    local_hour_angle.normalize(0, 360)

    # Meeus 13.6
    sinaltitude = math.sin(utils.get_latitude(an_observer).radians)  \
                  * math.sin(utils.get_declination(an_object).radians) \
                  + math.cos(utils.get_latitude(an_observer).radians)  \
                  * math.cos(utils.get_declination(an_object).radians) \
                  * math.cos(local_hour_angle.radians)

    theta = coords.angle(coords.angle().rad2deg(math.pi/2 - math.asin(sinaltitude)))


    # Meeus 13.5
    nom = math.sin(local_hour_angle.radians)
    den = math.cos(local_hour_angle.radians) \
          * math.sin(utils.get_latitude(an_observer).radians) \
          - math.tan(utils.get_declination(an_object).radians) \
          * math.cos(utils.get_latitude(an_observer).radians)

    # "Note that Azimuth (A) is measured from the South point, turning positive to the West."
    phi = coords.angle(coords.angle().rad2deg(math.atan2(nom, den) + math.pi))

    if is_verbose:
        print 'Datetime:', a_local_datetime.toJulianDate()
        print 'GAST:', gast
        print 'Local hour angle:', local_hour_angle.value
        print 'Observer longitude:', utils.get_longitude(an_observer).value
        print 'Object latitude:', utils.get_latitude(an_object).value
        print 'Altitude:', theta.complement(), '(', theta.complement().value, ')' # Altitude = 90 - theta
        print 'Azimuth:', phi, '(', phi.value, ')'

    return coords.spherical(1, theta, phi)


def toEquatorial(an_object, an_observer, a_local_datetime, is_verbose=False):
    """Transforms a coordinate vector from horizon to equatorial coordinates.

    Astronomical Algorithms 2ed, Jean Meeus ISBN 0-943396-61-1

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

    is_verbose (bool): verbose mode.

    Returns (coords.spherical): the object in the transformed coordinates.
    """

    if not isinstance(an_object, coords.spherical):
        raise Error('vector must be in spherical coordinates')

    if not isinstance(an_observer, coords.spherical):
        raise Error('observer must be in spherical coordinates')

    altitude = an_object.theta.complement()

    # The calculation assumes "that Azimuth (A) is measured from the
    # South point, turning positive to the West". coords.spherical
    # assumes azimuth is measured from the x-axis as north.
    azimuth = coords.angle(an_object.phi.value - 180)

    # Meeus, p. 94
    sindec = math.sin(utils.get_latitude(an_observer).radians) \
             * math.sin(altitude.radians) \
             - math.cos(utils.get_latitude(an_observer).radians) \
             * math.cos(altitude.radians) \
             * math.cos(azimuth.radians)

    object_dec = coords.angle(coords.angle().rad2deg(math.asin(sindec)))

    # Meeus, p. 94
    nom = math.sin(azimuth.radians)
    den = math.cos(azimuth.radians) \
          * math.sin(utils.get_latitude(an_observer).radians) \
          + math.tan(altitude.radians) \
          * math.cos(utils.get_latitude(an_observer).radians)

    local_hour_angle = coords.angle(coords.angle().rad2deg(math.atan2(nom, den)))
    local_hour_angle.normalize(0, 360)

    gast = GMST.USNO_C163.GAST(a_local_datetime) - coords.angle(a_local_datetime.timezone()) # hours

    object_longitude = coords.angle(15.0*gast.value + an_observer.phi.value - local_hour_angle.value )
    object_longitude.normalize(0, 360)

    object_ra = coords.angle(24.0*object_longitude.value/360.0)

    if is_verbose:
        print 'Datetime:', a_local_datetime.toJulianDate()
        print 'GAST:', gast
        print 'Local hour angle:', local_hour_angle.value
        print 'Object declination', object_dec
        print 'Object longitude:', object_longitude, '(', object_longitude.value, ')'
        print 'Object R.A.:', object_ra, '(', object_ra.value, ')'

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
                'isVerbose': False}

    usage = ' '.join(('%prog [options]',
                      '<RA/azimuth as hr|deg:min:sec>',
                      '<dec/altitude as deg:min:sec>',
                      '<observer latitude as deg:min:sec>',
                      '<observer longitude as deg:min:sec +west>',
                      '<a datetime>'))

    parser = optparse.OptionParser(usage=usage)

    parser.add_option('--toEquatorial',
                      action='store_true', dest='toEquatorial',
                      default=defaults['toEquatorial'],
                      help='az alt to equatorial [%default]')

    parser.add_option('-v', '--verbose',
                      action='store_true', dest='verbose',
                      default=defaults['isVerbose'],
                      help='verbose [%default]')

    options, args = parser.parse_args()

    # ----- validate -----

    if len(args) < 5:
        parser.error('missing object RA, DEC or observer latitude, longitude or datetime.')


    an_observer = utils.latlon2spherical(a_latitude=utils.parse_angle_arg(args[2]),
                                         a_longitude=utils.parse_angle_arg(args[3]))

    a_datetime = coords.datetime(args[4])

    # TODO validate toEquatorial/toHorizon option logic

    # ---------------------
    # ----- transform -----
    # ---------------------

    if options.toEquatorial is True:

        an_object = utils.azalt2spherical(an_azimuth=utils.parse_angle_arg(args[0]),
                                          an_altitude=utils.parse_angle_arg(args[1]))

        result = toEquatorial(an_object, an_observer, a_datetime, is_verbose=options.verbose)

        print 'Equatorial Latitude:', utils.get_latitude(result),
        print ', Longitude:', utils.get_longitude(result),

    else:

        an_object = utils.radec2spherical(a_right_ascension=utils.parse_angle_arg(args[0]),
                                          a_declination=utils.parse_angle_arg(args[1]))

        result = toHorizon(an_object, an_observer, a_datetime, is_verbose=options.verbose)

        print 'Azimuth:', utils.get_azimuth(result),
        print '(', utils.get_azimuth(result, is_relative2south=True), ' south)',
        print ', Altitude:', utils.get_altitude(result)
