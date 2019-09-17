"""Utils for parsing strings into AAI data formats from a flask request object

TODO: This is identical to what is used in mongodb. make into a common
libary but too small for now.
"""

import flask
import re

import coords

# ===================
# ===== globals =====
# ===================

dms_re = re.compile(r'(?P<degrees>[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?)'
                      '((:(?P<minutes>[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?))?)'
                       '(:(?P<seconds>[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?))?')


# year-month-day
ymd_re = re.compile(r'(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})')

# hour:minute:seconds
hms_re = re.compile(r'(?P<hour>\d{1,2}):(?P<minute>\d{1,2})(:(?P<seconds>\d{0,2}\.*\d+)){0,1}')

# time zone +hhmm
tz_re = re.compile(r'(?P<sign>[+-]){0,1}(?P<hrs>\d{1,2})(:){0,1}(?P<mins>\d\d){0,1}')


# ===================
# ===== classes =====
# ===================


class Error(Exception):
    pass


# =====================
# ===== functions =====
# =====================

def request_float(a_float_str, a_flask_request):
    """Gets the float of string from the request args

    Args:
        a_float_str (str): float as string
        a_flask_request (werkzeug.local.LocalProxy): reference to the flask request object

    Returns: the float
    Raises: Error if not found
    """

    a_float = a_flask_request.args.get(a_float_str, type=float)

    if a_float is None:
        raise Error('{a_float_str} is not a float: {a_value}'.format(
            a_float_str=a_float_str, a_value=flask.request.args.get(a_float_str)))

    return a_float


def safe_get_float(a_match, a_key):
    """Safe get float

    Args:
        a_match (re.match result dictonary): regex with named groups
        a_float_key (str): value to get

    Returns 0 if not found
    Raises: Error if not found
    """

    a_val = a_match.groupdict()[a_key]

    if a_val is None:
        return 0
    else:
        return float(a_val)


def request_angle(an_angle_key, a_flask_request):
    """Gets the degree minute second values from the request args

    Arg:
        an_angle_key (str): one of deg, deg:min, deg:min:sec
        a_flask_request (werkzeug.local.LocalProxy): reference to the flask request object
    Returns: coords.angle
    Raises: Error if not found
    """

    an_angle_value = a_flask_request.args.get(an_angle_key)

    found_dms = dms_re.match(an_angle_value)

    if not found_dms:
        raise Error('unsupported format for {an_angle_key}: {an_angle_value}'.format(**locals()))

    degrees = safe_get_float(found_dms, 'degrees')
    minutes = safe_get_float(found_dms, 'minutes')
    seconds = safe_get_float(found_dms, 'seconds')

    return coords.angle(degrees, minutes, seconds)


def request_datetime(a_date_key, a_time_key, a_timezone_key, a_flask_request):
    """Gets the degree minute second values from the request args

    Assumes daylight saving time has already been accounted for

    Arg:
        a_date_key (str): date key
        a_time_key (str): time key
        a_timezone_key (str): timezone key
        a_flask_request (werkzeug.local.LocalProxy): reference to the flask request object

    Returns: coords.datetime
    Raises: Error if not found
    """

    ymd_match = ymd_re.match(a_flask_request.args[a_date_key])

    if ymd_match is None:
        raise Error('unsupported date format {}'.format(flask.request.args[a_date_key]))

    ymd = ymd_match.groupdict()

    year = int(ymd['year'])
    month = int(ymd['month'])
    day = int(ymd['day'])

    hms_match = hms_re.match(a_flask_request.args[a_time_key])

    if hms_match is None:
        raise Error('unsupported date format {}'.format(flask.request.args[a_date_key]))

    # TODO unneeded
    hms = hms_match.groupdict()

    hour = int(hms['hour'])
    minute = int(hms['minute'])

    if hms['seconds'] is not None:
        seconds = float(hms['seconds'])
    else:
        seconds = 0

    tz_match = tz_re.match(flask.request.args[a_timezone_key])

    if tz_match is None:
        raise Error('unsupported timezone format {}'.format(flask.request.args[a_timezone_key]))

    # TODO unused
    tz_elements = tz_match.groupdict()

    timezone = float(tz_elements['hrs'])

    if tz_elements['mins'] is not None:
        tzmins = float(tz_elements['mins'])/60.0
        if tzmins > 1:
            raise Error('time zone minutes exceeded {}'.format(flask.request.args[a_timezone_key]))
        else:
            timezone += tzmins

    if timezone > 12:
        raise Error('time zone range exceeded {}'.format(flask.request.args[a_timezone_key]))

    if tz_elements['sign'] == '-':
        timezone *= -1


    # TODO construct from float? construct from strings?
    a_datetime = coords.datetime(year, month, day, hour, minute, seconds, str(flask.request.args[a_timezone_key]))

    return a_datetime
