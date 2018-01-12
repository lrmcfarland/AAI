"""Utils for parsing strings into AAI data formats from a flask request object

TODO: This is identical to what is used in mongodb. make into a common
libary but too small for now.
"""

import re
import coords

dms_re = re.compile(r'(?P<degrees>[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?)'
                      '((:(?P<minutes>[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?))?)'
                       '(:(?P<seconds>[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?))?')

# TODO re.VERBOSE
# TODO stricter formatting 12:3x4:45 passes

# works for 10, 1:23, 12:23:45

# TODO limit range to 24 hrs., 60 minutes and seconds. missing lower parts
# TODO utf-8 degrees


class Error(Exception):
    pass


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


def request_datetime(a_date_key, a_time_key, a_timezone, is_dst, a_flask_request):
    """Gets the degree minute second values from the request args

    Arg:
        a_date_key (str): yyyy-mm-dd
        a_time_key (str): hr:min:sec
        a_timezone (float): -12 to 12
        is_dst (bool): daylight savings time
        a_flask_request (werkzeug.local.LocalProxy): reference to the flask request object

    Returns: coords.datetime
    Raises: Error if not found
    """

    # TODO regex validation

    ymd = a_flask_request.args.get(a_date_key).split('-') # ASSUMES: yyyy-mm-dd format

    hms = a_flask_request.args.get(a_time_key).split(':') # ASSUMES: hh:mm:ss.ss
    while len(hms) < 3:
        hms.append('0')

    a_datetime = coords.datetime(int(ymd[0]),
                                 int(ymd[1]),
                                 int(ymd[2]),
                                 int(hms[0]),
                                 int(hms[1]),
                                 float(hms[2]),
                                 a_timezone)
    if is_dst:
        a_datetime -= 1.0/24

    return a_datetime


