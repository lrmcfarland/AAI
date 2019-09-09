#!/usr/bin/env python

"""Calculates the position of the moon for the given datetime.

Uses algorithms from:
    Astronomical Algorithms 2ed, Jean Meeus 1998




"""

from __future__ import absolute_import # for python 2 and 3


import math

import coords

import Transforms.EclipticEquatorial
import Transforms.EquatorialHorizon
import Transforms.utils


class Error(Exception):
    pass



# table 47.A Meeus pp. 339-340

table_47a = ({'D': 0, 'Msun': 0, 'Mmoon': 1, 'F': 0, 'Csin':6288774, 'Ccos':-20905355},
             {'D': 2, 'Msun': 0, 'Mmoon':-1, 'F': 0, 'Csin':1274027, 'Ccos': -3699111},
             {'D': 2, 'Msun': 0, 'Mmoon': 0, 'F': 0, 'Csin': 658314, 'Ccos': -2955968},
             {'D': 0, 'Msun': 0, 'Mmoon': 2, 'F': 0, 'Csin': 213618, 'Ccos':  -569925},

             {'D': 0, 'Msun': 1, 'Mmoon': 0, 'F': 0, 'Csin':-185116, 'Ccos':    48888},
             {'D': 0, 'Msun': 0, 'Mmoon': 0, 'F': 2, 'Csin':-114332, 'Ccos':    -3149},
             {'D': 2, 'Msun': 0, 'Mmoon':-2, 'F': 0, 'Csin':  58793, 'Ccos':   246158},
             {'D': 2, 'Msun':-1, 'Mmoon':-1, 'F': 0, 'Csin':  57066, 'Ccos':  -152138},

             {'D': 2, 'Msun': 0, 'Mmoon': 1, 'F': 0, 'Csin':  53322, 'Ccos':  -170733},
             {'D': 2, 'Msun':-1, 'Mmoon': 0, 'F': 0, 'Csin':  45758, 'Ccos':  -204586},
             {'D': 0, 'Msun': 1, 'Mmoon':-1, 'F': 0, 'Csin': -40923, 'Ccos':  -129620},
             {'D': 1, 'Msun': 0, 'Mmoon': 0, 'F': 0, 'Csin': -34720, 'Ccos':   108743},

             {'D': 0, 'Msun': 1, 'Mmoon': 1, 'F': 0, 'Csin': -30383, 'Ccos':   104755},
             {'D': 2, 'Msun': 0, 'Mmoon': 0, 'F':-2, 'Csin':  15327, 'Ccos':    10321},
             {'D': 0, 'Msun': 0, 'Mmoon': 1, 'F': 2, 'Csin': -12528, 'Ccos':        0},
             {'D': 0, 'Msun': 0, 'Mmoon': 1, 'F':-2, 'Csin':  10980, 'Ccos':    79661},

             {'D': 4, 'Msun': 0, 'Mmoon':-1, 'F': 0, 'Csin':  10675, 'Ccos':   -34782},
             {'D': 0, 'Msun': 0, 'Mmoon': 3, 'F': 0, 'Csin':  10034, 'Ccos':   -23210},
             {'D': 4, 'Msun': 0, 'Mmoon':-2, 'F': 0, 'Csin':   8548, 'Ccos':   -21636},
             {'D': 2, 'Msun': 1, 'Mmoon':-1, 'F': 0, 'Csin':  -7888, 'Ccos':    24208},

             {'D': 2, 'Msun': 1, 'Mmoon': 0, 'F': 0, 'Csin':  -6766, 'Ccos':    30824},
             {'D': 1, 'Msun': 0, 'Mmoon':-1, 'F': 0, 'Csin':  -5163, 'Ccos':    -8379},
             {'D': 1, 'Msun': 1, 'Mmoon': 0, 'F': 0, 'Csin':   4987, 'Ccos':   -16675},
             {'D': 2, 'Msun':-1, 'Mmoon': 1, 'F': 0, 'Csin':   4036, 'Ccos':   -12831},

             {'D': 2, 'Msun': 0, 'Mmoon': 2, 'F': 0, 'Csin':   3994, 'Ccos':   -10445},
             {'D': 4, 'Msun': 0, 'Mmoon': 0, 'F': 0, 'Csin':   3861, 'Ccos':   -11650},
             {'D': 2, 'Msun': 0, 'Mmoon':-3, 'F': 0, 'Csin':   3665, 'Ccos':    14403},
             {'D': 0, 'Msun': 1, 'Mmoon':-2, 'F': 0, 'Csin':  -2689, 'Ccos':    -7003},

             {'D': 2, 'Msun': 0, 'Mmoon':-1, 'F': 2, 'Csin':  -2602, 'Ccos':        0},
             {'D': 2, 'Msun':-1, 'Mmoon':-2, 'F': 0, 'Csin':   2390, 'Ccos':    10056},
             {'D': 1, 'Msun': 0, 'Mmoon': 1, 'F': 0, 'Csin':  -2348, 'Ccos':     6322},
             {'D': 2, 'Msun':-2, 'Mmoon': 0, 'F': 0, 'Csin':   2236, 'Ccos':    -9884},

             {'D': 0, 'Msun': 1, 'Mmoon': 2, 'F': 0, 'Csin':  -2120, 'Ccos':     5751},
             {'D': 0, 'Msun': 2, 'Mmoon': 0, 'F': 0, 'Csin':  -2069, 'Ccos':        0},
             {'D': 2, 'Msun':-2, 'Mmoon':-1, 'F': 0, 'Csin':   2048, 'Ccos':    -4950},
             {'D': 2, 'Msun': 0, 'Mmoon': 1, 'F':-2, 'Csin':  -1773, 'Ccos':     4130},

             {'D': 2, 'Msun': 0, 'Mmoon': 0, 'F': 2, 'Csin':  -1595, 'Ccos':        0},
             {'D': 4, 'Msun':-1, 'Mmoon':-1, 'F': 0, 'Csin':   1215, 'Ccos':    -3958},
             {'D': 0, 'Msun': 0, 'Mmoon': 2, 'F': 2, 'Csin':  -1110, 'Ccos':        0},
             {'D': 3, 'Msun': 0, 'Mmoon':-1, 'F': 0, 'Csin':   -892, 'Ccos':     3258},

             {'D': 2, 'Msun': 1, 'Mmoon': 1, 'F': 0, 'Csin':   -810, 'Ccos':     2616},
             {'D': 4, 'Msun':-1, 'Mmoon':-2, 'F': 0, 'Csin':    759, 'Ccos':    -1897},
             {'D': 0, 'Msun': 2, 'Mmoon':-1, 'F': 0, 'Csin':   -713, 'Ccos':    -2117},
             {'D': 2, 'Msun': 2, 'Mmoon':-1, 'F': 0, 'Csin':   -700, 'Ccos':     2354},

             {'D': 2, 'Msun': 1, 'Mmoon':-2, 'F': 0, 'Csin':    691, 'Ccos':        0},
             {'D': 2, 'Msun':-1, 'Mmoon': 0, 'F':-2, 'Csin':    596, 'Ccos':        0},
             {'D': 4, 'Msun': 0, 'Mmoon': 1, 'F': 0, 'Csin':    549, 'Ccos':    -1423},
             {'D': 0, 'Msun': 0, 'Mmoon': 4, 'F': 0, 'Csin':    537, 'Ccos':    -1117},

             {'D': 4, 'Msun':-1, 'Mmoon': 0, 'F': 0, 'Csin':    520, 'Ccos':    -1571},
             {'D': 1, 'Msun': 0, 'Mmoon':-2, 'F': 0, 'Csin':   -487, 'Ccos':    -1739},
             {'D': 2, 'Msun': 1, 'Mmoon': 0, 'F':-2, 'Csin':   -399, 'Ccos':        0},
             {'D': 0, 'Msun': 0, 'Mmoon': 2, 'F':-2, 'Csin':   -381, 'Ccos':    -4421},

             {'D': 1, 'Msun': 1, 'Mmoon': 1, 'F': 0, 'Csin':    351, 'Ccos':        0},
             {'D': 3, 'Msun': 0, 'Mmoon':-2, 'F': 0, 'Csin':   -340, 'Ccos':        0},
             {'D': 4, 'Msun': 0, 'Mmoon':-3, 'F': 0, 'Csin':    330, 'Ccos':        0},
             {'D': 2, 'Msun':-1, 'Mmoon': 2, 'F': 0, 'Csin':    327, 'Ccos':        0},

             {'D': 0, 'Msun': 2, 'Mmoon': 1, 'F': 0, 'Csin':   -323, 'Ccos':     1165},
             {'D': 1, 'Msun': 1, 'Mmoon':-1, 'F': 0, 'Csin':    299, 'Ccos':        0},
             {'D': 2, 'Msun': 0, 'Mmoon': 3, 'F': 0, 'Csin':    294, 'Ccos':        0},
             {'D': 2, 'Msun': 0, 'Mmoon':-1, 'F':-2, 'Csin':      0, 'Ccos':     8752},

)


# table 47.B Meeus p. 341

table_47b = ({'D': 0, 'Msun': 0, 'Mmoon': 0, 'F': 1, 'Csin':5128122},
             {'D': 0, 'Msun': 0, 'Mmoon': 1, 'F': 1, 'Csin': 280602},
             {'D': 0, 'Msun': 0, 'Mmoon': 1, 'F':-1, 'Csin': 277693},
             {'D': 2, 'Msun': 0, 'Mmoon': 0, 'F':-1, 'Csin': 173237},

             {'D': 2, 'Msun': 0, 'Mmoon':-1, 'F': 1, 'Csin':  55413},
             {'D': 2, 'Msun': 0, 'Mmoon':-1, 'F':-1, 'Csin':  46271},
             {'D': 2, 'Msun': 0, 'Mmoon': 0, 'F': 1, 'Csin':  32573},
             {'D': 0, 'Msun': 0, 'Mmoon': 2, 'F': 1, 'Csin':  17198},

             {'D': 2, 'Msun': 0, 'Mmoon': 1, 'F':-1, 'Csin':   9266},
             {'D': 0, 'Msun': 0, 'Mmoon': 2, 'F':-1, 'Csin':   8822},
             {'D': 2, 'Msun':-1, 'Mmoon': 0, 'F':-1, 'Csin':   8216},
             {'D': 2, 'Msun': 0, 'Mmoon':-2, 'F':-1, 'Csin':   4324},

             {'D': 2, 'Msun': 0, 'Mmoon': 1, 'F': 1, 'Csin':   4200},
             {'D': 2, 'Msun': 1, 'Mmoon': 0, 'F':-1, 'Csin':  -3359},
             {'D': 2, 'Msun':-1, 'Mmoon':-1, 'F': 1, 'Csin':   2463},
             {'D': 2, 'Msun':-1, 'Mmoon': 0, 'F': 1, 'Csin':   2211},

             {'D': 2, 'Msun':-1, 'Mmoon':-1, 'F':-1, 'Csin':   2065},
             {'D': 0, 'Msun': 1, 'Mmoon':-1, 'F':-1, 'Csin':  -1870},
             {'D': 4, 'Msun': 0, 'Mmoon':-1, 'F':-1, 'Csin':   1828},
             {'D': 0, 'Msun': 1, 'Mmoon': 0, 'F': 1, 'Csin':  -1794},

             {'D': 0, 'Msun': 0, 'Mmoon': 0, 'F': 3, 'Csin':  -1749},
             {'D': 0, 'Msun': 1, 'Mmoon':-1, 'F': 1, 'Csin':  -1565},
             {'D': 1, 'Msun': 0, 'Mmoon': 0, 'F': 1, 'Csin':  -1491},
             {'D': 0, 'Msun': 1, 'Mmoon': 1, 'F': 1, 'Csin':  -1475},

             {'D': 0, 'Msun': 1, 'Mmoon': 1, 'F':-1, 'Csin':  -1410},
             {'D': 0, 'Msun': 1, 'Mmoon': 0, 'F':-1, 'Csin':  -1344},
             {'D': 1, 'Msun': 0, 'Mmoon': 0, 'F':-1, 'Csin':  -1335},
             {'D': 0, 'Msun': 0, 'Mmoon': 3, 'F': 1, 'Csin':   1107},

             {'D': 4, 'Msun': 0, 'Mmoon': 0, 'F':-1, 'Csin':   1021},
             {'D': 4, 'Msun': 0, 'Mmoon':-1, 'F': 1, 'Csin':    833},


             # second column

             {'D': 0, 'Msun': 0, 'Mmoon': 1, 'F':-3, 'Csin':    777},
             {'D': 4, 'Msun': 0, 'Mmoon':-2, 'F': 1, 'Csin':    671},
             {'D': 2, 'Msun': 0, 'Mmoon': 0, 'F':-3, 'Csin':    607},
             {'D': 2, 'Msun': 0, 'Mmoon': 2, 'F':-1, 'Csin':    596},

             {'D': 2, 'Msun':-1, 'Mmoon': 1, 'F':-1, 'Csin':    491},
             {'D': 2, 'Msun': 0, 'Mmoon':-2, 'F': 1, 'Csin':   -451},
             {'D': 0, 'Msun': 0, 'Mmoon': 3, 'F':-1, 'Csin':    439},
             {'D': 2, 'Msun': 0, 'Mmoon': 2, 'F': 1, 'Csin':    422},

             {'D': 2, 'Msun': 0, 'Mmoon':-3, 'F':-1, 'Csin':    421},
             {'D': 2, 'Msun': 1, 'Mmoon':-1, 'F': 1, 'Csin':   -366},
             {'D': 2, 'Msun': 1, 'Mmoon': 0, 'F': 1, 'Csin':   -351},
             {'D': 4, 'Msun': 0, 'Mmoon': 0, 'F': 1, 'Csin':    331},

             {'D': 2, 'Msun':-1, 'Mmoon': 1, 'F': 1, 'Csin':    315},
             {'D': 2, 'Msun':-2, 'Mmoon': 0, 'F':-1, 'Csin':    302},
             {'D': 0, 'Msun': 0, 'Mmoon': 1, 'F': 3, 'Csin':   -283},
             {'D': 2, 'Msun': 1, 'Mmoon': 1, 'F':-1, 'Csin':   -229},

             {'D': 1, 'Msun': 1, 'Mmoon': 0, 'F':-1, 'Csin':    223},
             {'D': 1, 'Msun': 1, 'Mmoon': 0, 'F': 1, 'Csin':    223},
             {'D': 0, 'Msun': 1, 'Mmoon':-2, 'F':-1, 'Csin':   -220},
             {'D': 2, 'Msun': 1, 'Mmoon':-1, 'F':-1, 'Csin':   -220},

             {'D': 1, 'Msun': 0, 'Mmoon': 1, 'F': 1, 'Csin':   -185},
             {'D': 2, 'Msun':-1, 'Mmoon':-2, 'F':-1, 'Csin':    181},
             {'D': 0, 'Msun': 1, 'Mmoon': 2, 'F': 1, 'Csin':   -177},
             {'D': 4, 'Msun': 0, 'Mmoon':-2, 'F':-1, 'Csin':    176},

             {'D': 4, 'Msun':-1, 'Mmoon':-1, 'F':-1, 'Csin':    166},
             {'D': 1, 'Msun': 0, 'Mmoon': 1, 'F':-1, 'Csin':   -164},
             {'D': 4, 'Msun': 0, 'Mmoon': 1, 'F':-1, 'Csin':    132},
             {'D': 1, 'Msun': 0, 'Mmoon':-1, 'F':-1, 'Csin':   -119},

             {'D': 4, 'Msun':-1, 'Mmoon': 0, 'F':-1, 'Csin':    115},
             {'D': 2, 'Msun':-2, 'Mmoon': 0, 'F': 1, 'Csin':    107},

)


def LunarLongLatRange(a_datetime):
    """Calculates the ecliptical longitude, latitude and distance to the moon

    Meeus pp. 337-343

    Args:
        a_datetime (coords.datetime): The time of the observation.

    Returns: the ecliptical longitude (degrees), latitude (degrees) and range (in meters)
    """

    JD, JDo = Transforms.SiderealTime.USNO_C163.JulianDate0(a_datetime)

    T = Transforms.utils.JulianCentury(a_datetime)

    # -----------------------------------------------------
    # ----- L: Moon's mean longitude. Meeus eqn. 47.1 -----
    # -----------------------------------------------------

    L = coords.angle(218.3164477 + 481267.881234*T - 0.0015786*T*T + T*T*T/538841.0 - T*T*T*T/65194000.0)
    L.normalize(0, 360)


    # -----------------------------------------------------------
    # ----- D: Mean elongation of the Moon. Meeus eqn. 47.2 -----
    # -----------------------------------------------------------

    D = coords.angle(297.8501921 + 445267.1114034*T - 0.0018819*T*T + T*T*T/545868.0 - T*T*T*T/113065000.0)
    D.normalize(0, 360)

    # -----------------------------------------------------
    # ----- Msun: Sun's mean anomaly. Meeus eqn. 47.3 -----
    # -----------------------------------------------------

    Msun = coords.angle(357.5291092 + 35999.0502909*T - 0.0001536*T*T + T*T*T/24490000.0)
    Msun.normalize(0, 360)

    # -------------------------------------------------------
    # ----- Mmoon: Moon's mean anomaly. Meeus eqn. 47.4 -----
    # -------------------------------------------------------

    Mmoon = coords.angle(134.9633964 + 477198.8675055*T + 0.0087414*T*T + T*T*T/69699.0 - T*T*T*T/14712000.0)
    Mmoon.normalize(0, 360)

    # -----------------------------------------------------------
    # ----- F: Moon's argument of latitude. Meeus eqn. 47.5 -----
    # -----------------------------------------------------------

    F = coords.angle(93.2720950 + 483202.0175233*T - 0.0036539*T*T - T*T*T/3526000.0 + T*T*T*T/863310000.0)
    F.normalize(0, 360)

    # ------------------------------
    # ----- E: Meeus eqn. 47.6 -----
    # ------------------------------

    E = coords.angle(1.0 - 0.002516*T - 0.0000074*T*T)
    E.normalize(0, 360)
    E2 = E*E # to save time later


    # ----------------------------
    # ----- A1: Meeus p. 338 -----
    # ----------------------------

    A1 = coords.angle(119.75 + 131.849*T)
    A1.normalize(0, 360)

    # ----------------------------
    # ----- A2: Meeus p. 338 -----
    # ----------------------------

    A2 = coords.angle(53.09 + 479264.290*T)
    A2.normalize(0, 360)

    # ----------------------------
    # ----- A3: Meeus p. 338 -----
    # ----------------------------

    A3 = coords.angle(313.45 + 481266.484*T)
    A3.normalize(0, 360)

    # ----------------------
    # ----- Additive l -----
    # ----------------------

    deltaLF = L - F
    addL = 3958.0*math.sin(A1.radians) + 1962.0*math.sin(deltaLF.radians) + 318.0*math.sin(A2.radians)

    # ----------------------
    # ----- Additive b -----
    # ----------------------

    A1minusF    = A1 - F
    A1plusF     = A1 + F
    LminusMmoon = L - Mmoon
    LplusMmoon  = L + Mmoon

    addB = -2235.0*math.sin(L.radians) \
        + 382.0*math.sin(A3.radians) \
        + 175.0*math.sin(A1minusF.radians) \
        + 175.0*math.sin(A1plusF.radians) \
        + 127.0*math.sin(LminusMmoon.radians) \
        - 115.0*math.sin(LplusMmoon.radians)



    # ===================
    # ----- Sigma l -----
    # ===================


    sigmaL = 0

    for record in table_47a:

        bar = coords.angle(record['D']*D.degrees + record['Msun']*Msun.degrees + record['Mmoon']*Mmoon.degrees + record['F']*F.degrees)

        if record['Msun'] == 1 or record['Msun'] == -1:

            sigmaL += record['Csin'] * E.degrees * math.sin(bar.radians)

        elif record['Msun'] == 2 or record['Msun'] == -2:

            sigmaL += record['Csin'] * E2.degrees * math.sin(bar.radians)

        else:

            sigmaL += record['Csin'] * math.sin(bar.radians)


    # ===================
    # ----- Sigma r -----
    # ===================

    sigmaR = 0

    for record in table_47a:

        bar = coords.angle(record['D']*D.degrees + record['Msun']*Msun.degrees + record['Mmoon']*Mmoon.degrees + record['F']*F.degrees)

        if record['Msun'] == 1 or record['Msun'] == -1:

            sigmaR += record['Ccos'] * E.degrees * math.cos(bar.radians)

        elif record['Msun'] == 2 or record['Msun'] == -2:

            sigmaR += record['Ccos'] * E2.degrees * math.cos(bar.radians)

        else:

            sigmaR += record['Ccos'] * math.cos(bar.radians)


    # ===================
    # ----- Sigma b -----
    # ===================

    sigmaB = 0

    for record in table_47b:

        bar = coords.angle(record['D']*D.degrees + record['Msun']*Msun.degrees + record['Mmoon']*Mmoon.degrees + record['F']*F.degrees)

        if record['Msun'] == 1 or record['Msun'] == -1:

            sigmaB += record['Csin'] * E.degrees * math.sin(bar.radians)

        elif record['Msun'] == 2 or record['Msun'] == -2:

            sigmaB += record['Csin'] * E2.degrees * math.sin(bar.radians)

        else:

            sigmaB += record['Csin'] * math.sin(bar.radians)


    # ecliptical longitude

    elong = coords.angle(L.degrees + sigmaL/1e6)

    # ecliptical latitude beta

    elat = coords.angle(sigmaB/1e6)

    # distance d

    distance = 385000.56 + sigmaR/1e3 # in kilometers


    return elong, elat, distance



def EclipticCoords(a_datetime):
    """Calculate the location of the sun in ecliptic coordinates

    Args:

    an_observer (coords.spherical): the latitude (in degrees) and
    longitude of an observer as a spherical coordinate where theta
    is the complement of latitude and longitude is measured
    positive east. See utils.latlon2spherical.

    a_datetime (coords.datetime): The time of the observation.

    Returns (coords.spherical): the position of the sun in horizon coordinates.
    """

    elong, elat, distance = LunarLongLatRange(a_datetime)
    moon_ec = coords.spherical(distance, elat.complement(), elong)

    return moon_ec


def EquatorialCoords(a_datetime):
    """Calculate the location of the moon relaive to an observer in
       equatorial coordinates

    Args:

    an_observer (coords.spherical): the latitude (in degrees) and
    longitude of an observer as a spherical coordinate where theta
    is the complement of latitude and longitude is measured
    positive east. See utils.latlon2spherical.

    a_datetime (coords.datetime): The time of the observation.

    Returns (coords.spherical): the position of the sun in horizon coordinates.

    """

    moon_ec = EclipticCoords(a_datetime)
    moon_eq = Transforms.EclipticEquatorial.toEquatorial(moon_ec, a_datetime)

    return moon_eq


def HorizontalCoords(an_observer, a_datetime):
    """Calculate the location of the sun relaive to an observer

    Args:

    an_observer (coords.spherical): the latitude (in degrees) and
    longitude of an observer as a spherical coordinate where theta
    is the complement of latitude and longitude is measured
    positive east. See utils.latlon2spherical.

    a_datetime (coords.datetime): The time of the observation.

    Returns (coords.spherical): the position of the sun in horizon coordinates.
    """

    moon_eq = EquatorialCoords(a_datetime)
    moon_hz = Transforms.EquatorialHorizon.toHorizon(moon_eq, an_observer, a_datetime)

    return moon_hz


# ================
# ===== main =====
# ================


if __name__ == '__main__':


    a_datetime = coords.datetime('2019-08-18T14:29:00')

    # a_datetime = coords.datetime('1992-04-12T00:00')

    a_datetime = coords.datetime('1992-04-12T00:00')

    print('Test date: {}'.format(a_datetime))

    ecLon, ecLat, distance = EclipticCoords(a_datetime)

    print('ecLon {}'.format(ecLon.degrees))
    print('ecLat {}'.format(ecLat.degrees))
    print('distance {}'.format(distance))

    moon_sph = Transforms.utils.latlon2spherical(ecLat, ecLon)
    moon_eq = Transforms.EclipticEquatorial.Meeus.toEquatorial(moon_sph, a_datetime)

    print('dec {}'.format(Transforms.utils.get_declination(moon_eq)))
    print('RA {}'.format(Transforms.utils.get_RA(moon_eq)))

