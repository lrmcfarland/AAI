#!/usr/bin/env python

"""Starry Sky: How to convert Equatorial to Horizontal coordinates.

from http://stjarnhimlen.se/comp/ppcomp.html

Another method to help me sort out what is wrong with the others.
Tack Paul!

TODO: The solar calculations agree with
http://www.satellite-calculations.com/Satellite/suncalc.htm,
but the GMST delta is about 8 seconds too long see
TestStjarnHimlen.test_GMST_J2000_plus_day

References:

    http://stjarnhimlen.se/english.html

"""

import math
import coords


def SolarLongitude(a_datetime):
    """Calculate the longitude of the sun for the given date

    returns the sun's longitude
    """

    d = a_datetime.toJulianDate() - a_datetime.J2000

    w = 282.9404 + 4.70935E-5 * d # argument of perihelion
    e = 0.016709 - 1.151E-9 * d # eccentricity
    M = coords.angle(356.0470 + 0.9856002585 * d) # mean anomaly
    E = coords.angle(M.degrees + e * (180/math.pi) * math.sin(M.radians) * ( 1.0 + e * math.cos(M.radians) ))

    xv = math.cos(E.radians) - e
    yv = math.sqrt(1.0 - e*e) * math.sin(E.radians)

    v = math.atan2(yv, xv)*180/math.pi

    lonsun = coords.angle(v + w)
    lonsun.normalize(0, 360) # flips to 0 on March 21 2000, not quite equinox

    return lonsun


def SolarRADec(a_datetime):
    """Calculate the right ascension and declination of the sun for the given date

    returns the sun's RA and declination
    """

    d = a_datetime.toJulianDate() - a_datetime.J2000

    w = 282.9404 + 4.70935E-5 * d # argument of perihelion
    e = 0.016709 - 1.151E-9 * d # eccentricity
    M = coords.angle(356.0470 + 0.9856002585 * d) # mean anomaly
    E = coords.angle(M.degrees + e * (180/math.pi) * math.sin(M.radians) * ( 1.0 + e * math.cos(M.radians) ))

    xv = math.cos(E.radians) - e
    yv = math.sqrt(1.0 - e*e) * math.sin(E.radians)

    v = math.atan2(yv, xv)*180/math.pi

    lonsun = coords.angle(v + w)

    r = math.sqrt( xv*xv + yv*yv)

    xs = r * math.cos(lonsun.radians)
    ys = r * math.sin(lonsun.radians)

    ecl = coords.angle(23.4393 - 3.563E-7 * d) # TODO use JPL obliquity of the ecliptic?

    xe = xs
    ye = ys * math.cos(ecl.radians)
    ze = ys * math.sin(ecl.radians)

    RA = coords.angle(math.atan2(ye, xe)*180/math.pi)
    RA.normalize(0, 360)

    Dec = coords.angle(math.atan2(ze, math.sqrt(xe*xe+ye*ye))*180/math.pi)

    return RA, Dec # TODO as coords.spherical(1, Longitue(Dec), RA)?


def GMST0(a_datetime):
    """Calculate the Greenwich mean siderial time at Greenwich"""

    lonsun = SolarLongitude(a_datetime)
    gmst0 = coords.angle(lonsun.degrees + 180) # TODO noon or midnight vs. GMST USNO
    gmst0.normalize(0, 360) # TODO as hours?

    return gmst0


def GMST(a_datetime):
    """Calculate the Greenwich mean siderial time at location"""

    gmst0 = GMST0(a_datetime)

    d = a_datetime.toJulianDate() - a_datetime.J2000

    gmst = coords.angle(gmst0.degrees/15 + d*24) # sidereal_day.degrees) # TODO siderial day?
    gmst.normalize(-12, 12) # TODO as degrees?

    return gmst


def toHorizon(an_object, an_observer, a_local_datetime):
    """Transforms a vector from equatorial to ecliptic coordinates.

    from http://stjarnhimlen.se/comp/ppcomp.html

    TODO: not working yet.

    Args:

    an_object: the vector to transform in theta (90 - declination),
    phi (RA * 15). See utils.radec2spherical.

    an_observer (coords.spherical): the latitude (in degrees) and
    longitude of an observer as a spherical coordinate where theta
    is the complement of latitude and longitude is measured
    positive east. See utils.latlon2spherical.

    a_local_datetime: local date and time of the observation.

    Returns a spherical coordinate vector in the transformed coordinates

    """

    print # linefeed
    print 'object', an_object # TODO rm
    print 'observer', an_observer # TODO rm
    print 'a time', a_local_datetime # TODO rm

    # Big difference which GMST is being used! Stjarn Himeln's day
    # is 8 seconds longer that USNO's.

    gmst = GMST(a_local_datetime)

    # gmst = USNO.GMST(a_local_datetime)

    print 'gmst', gmst # TODO rm

    lst = gmst.degrees + an_observer.phi.degrees/15

    # lst = 19.2242 # TODO USNO LSTA for 2014-12-31T20:41:00

    print 'lst', lst # TODO rm

    ha = coords.angle(360*(lst - an_object.phi.degrees/15)/24) # degrees?
    ha.normalize(-180, 180)

    print 'ha', ha, ha.radians

    dec = coords.angle(90 - an_object.theta.degrees)

    print 'dec', dec

    x = math.cos(ha.radians) * math.cos(dec.radians)
    y = math.sin(ha.radians) * math.cos(dec.radians)
    z = math.sin(dec.radians)

    xhor = x * math.sin(math.pi/2 - an_observer.theta.radians) - z * math.cos(math.pi/2 - an_observer.theta.radians)
    yhor = y
    zhor = x * math.cos(math.pi/2 - an_observer.theta.radians) + z * math.sin(math.pi/2 - an_observer.theta.radians)

    az = coords.angle((math.atan2(yhor, xhor) + math.pi)*180/math.pi)

    print 'az', az

    alt = coords.angle(math.asin(zhor)*180/math.pi) # or

    print 'alt', alt

    alt = coords.angle(math.atan2(zhor, math.sqrt(xhor*xhor + yhor*yhor))*180/math.pi)

    print 'alt', alt
