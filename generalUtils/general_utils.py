from types import MethodType, FunctionType, LambdaType
from math import sqrt
from types import SimpleNamespace
import os
import sys


def is_func(func):
    """Check if 'func' is an instance of (MethodType, FunctionType, LambdaType)

    :param func: thing to check if it's a function
    :return: bool, whether 'func' is an instance of (MethodType, FunctionType, LambdaType)
    """
    return isinstance(func, (MethodType, FunctionType, LambdaType))


def get_all_funcs(localDict):
    """Get names of all functions in a dictionary. Uses is_func.
    Ignores names starting with dunder '__'

    :param localDict: dictionary to check for functions
    :return: [strings], names of functions in localDict where is_func()==True
    """
    return [x[0] for x in filter(lambda x: is_func(x[1]), localDict.items()) if not x[0].startswith('__')]


def get_all_classes(localDict):
    """Get names of all classes in a dictionary.
    Ignores names starting with dunder '__'

    :param localDict: dictionary to check for classes
    :return: [strings], names of functions in localDict where isinstance(obj, type)==True
    """
    return [x[0] for x in filter(lambda x: isinstance(x[1], type), localDict.items()) if not x[0].startswith('__')]


def apply_default_args(kwargs, defaultargs):
    """Returns (dict, namespace) of defaultargs overridden by kwargs. Any keys in kwargs not in defaultargs
    raise a ValueError

    :param kwargs: dict of kwargs to process
    :param defaultargs: dict of defaults
    :return: dict, SimpleNamespace
    """
    unknown_args = kwargs.keys() - defaultargs.keys()
    if unknown_args:
        raise ValueError(f"Unknown argument(s): {unknown_args}")
    a = defaultargs.copy()
    a.update(kwargs)
    return a, SimpleNamespace(**a)


def constrain_2(val, less_lim, more_lim):
    '''Constrains a value to between less_lim and more_lim'''
    if val < less_lim:
        return less_lim
    elif val > more_lim:
        return more_lim
    else:
        return val


def constrain(val, lim):
    '''Constrains a value to between -1*lim and lim
    '''
    return constrain_2(val, -lim, lim)


def constrain_decider(decider, less_lim, more_lim, output):
    '''Compares decider to less_lim and more_lim, returns a *_lim or output.

    if decider < less_lim:
        return less_lim
    elif decider > more_lim:
        return more_lim
    else:
        return output
    '''
    if decider < less_lim:
        return less_lim
    elif decider > more_lim:
        return more_lim
    else:
        return output


def rescale(val, in_low, in_high, out_low, out_high, outside='raise'):
    """ Rescales val in the input range in_low:in_high to the output range
    out_low:out_high.

    If result is outside the output range:
    outside='raise' : raise exception (default)
    outside='mid' : return middle of output range
    outside='constrain' : return the limiting value at respective end of output range
    outside='ignore' : return result regardless of range
    outside= value or None : return whatever outside is set to
    """

    # calculate new value
    _ret = ((val - in_low) / (in_high - in_low)) * (out_high - out_low) + out_low

    # _ret is outside output range
    if _ret < out_low or _ret > out_high:
        # apply setting
        if outside == 'constrain':
            return constrain_2(_ret, out_low, out_high)
        elif outside == 'mid':
            return (out_high + out_low) / 2  # return middle value
        elif outside == 'ignore':
            return _ret
        elif outside == 'raise':
            raise (
                Exception('Rescaling {} in {}:{} falls outside {}:{}'.format(val, in_low, in_high, out_low, out_high)))
        else:  # value provided
            if _ret < out_low or _ret > out_high:
                return outside  # return provided 'outside' value

    # _ret is inside output range
    return _ret


def deadband_2(val, lower_cutoff, higher_cutoff, default=0.0):
    """Applies a deadband to 'val' between the cutoffs. If 'val' is not
    between cutoffs, returns 'default'"""
    if val > lower_cutoff and val < higher_cutoff:
        return default
    else:
        return val


def deadband(val, range_cutoff, default=0.0):
    """Applies a deadband to 'val' of 'range_cutoff' around 'default'.
    With 'default'=0.0, functions same as:
        if abs(val) < range_cutoff:
            return 0.0
        else:
            :return val
    """
    return deadband_2(val, default - range_cutoff, default + range_cutoff)


def get_timestamp():
    """Gets a human friendly string for the current system time."""
    from datetime import datetime
    from time import time
    return str(datetime.fromtimestamp(time()))


# def intersect_segment_circle(start, end, circle, fudge=0.0):
#     """
#     Test whether a line segment and circle intersect.
#     :param Entity start: The start of the line segment. (Needs x, y attributes)
#     :param Entity end: The end of the line segment. (Needs x, y attributes)
#     :param Entity circle: The circle to test against. (Needs x, y, r attributes)
#     :param float fudge: A fudge factor; additional distance to leave between the segment and circle.
#     :return: True if intersects, False otherwise
#     :rtype: bool
#     """
#     # Derived with SymPy
#     # Parameterize the segment as start + t * (end - start),
#     # and substitute into the equation of a circle
#     # Solve for t
#     dx = end.x - start.x
#     dy = end.y - start.y
#
#     a = dx**2 + dy**2
#     b = -2 * (start.x**2 - start.x*end.x - start.x*circle.x + end.x*circle.x +
#               start.y**2 - start.y*end.y - start.y*circle.y + end.y*circle.y)
#     c = (start.x - circle.x)**2 + (start.y - circle.y)**2
#
#     if a == 0.0:
#         # Start and end are the same point
#         # TODO: replace with generic distance function
#         return start.calculate_distance_between(circle) <= (circle.radius + fudge) ** 2
#
#     # Time along segment when closest to the circle (vertex of the quadratic)
#     t = min(-b / (2 * a), 1.0)
#     if t < 0:
#         return False
#
#     closest_x = start.x + dx * t
#     closest_y = start.y + dy * t
#     #TODO: replace with generic distance function
#     closest_distance = Position(closest_x, closest_y).calculate_distance_between(circle)
#
#     return closest_distance <= (circle.radius + fudge) ** 2


__all__ = ['is_func', 'get_all_funcs', 'get_all_classes', 'apply_default_args',
           'constrain', 'constrain_2', 'constrain_decider', 'rescale', 'deadband', 'deadband_2',
           'get_timestamp']
