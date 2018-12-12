from types import MethodType, FunctionType, LambdaType
from math import sqrt
from types import SimpleNamespace


def isFunc(func):
    """Check if 'func' is an instance of (MethodType, FunctionType, LambdaType)

    :param func: thing to check if it's a function
    :return: bool, whether 'func' is an instance of (MethodType, FunctionType, LambdaType)
    """
    return isinstance(func, (MethodType, FunctionType, LambdaType))


def getAllFuncs(localDict):
    """Get names of all functions in a dictionary. Uses isFunc.
    Ignores names starting with dunder '__'

    :param localDict: dictionary to check for functions
    :return: [strings], names of functions in localDict where isFunc()==True
    """
    return [x[0] for x in filter(lambda x: isFunc(x[1]), localDict.items()) if not x[0].startswith('__')]


def getAllClasses(localDict):
    """Get names of all classes in a dictionary.
    Ignores names starting with dunder '__'

    :param localDict: dictionary to check for classes
    :return: [strings], names of functions in localDict where isinstance(obj, type)==True
    """
    return [x[0] for x in filter(lambda x: isinstance(x[1], type), localDict.items()) if not x[0].startswith('__')]


def tupleDistance(x, y):
    """Calculate tupleDistance between tuple values.

    :param x: (int, int, int), rgb tuple
    :param y: (int, int, int), rgb tuple
    :return: float, sum of distances between each pair of elements
    """
    assert len(x)==len(y)
    sum = 0
    for i in range(len(x)):
        sum += (x[i]-y[i])**2
    sum = sqrt(sum)
    return sum


def applyDefaultArgs(kwargs, defaultargs):
    """Returns (dict, namespace) of defaultargs overridden by kwargs. Any keys in kwargs not in defaultargs
    raise a TypeError

    :param kwargs: dict of kwargs to process
    :param defaultargs: dict of defaults
    :return: dict, SimpleNamespace
    """
    unknown_args = kwargs.keys() - defaultargs.keys()
    if unknown_args:
        raise TypeError(f"Unknown argument(s): {unknown_args}")
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


def gettimestamp():
    """Gets a human friendly string for the current system time."""
    from datetime import datetime
    from time import time
    return str(datetime.fromtimestamp(time()))


def ArgFunc(func, *args, **kwargs):
    """Returns callable reference to func, with args and kwargs attached.

    obj = ArgFunc(function, arguments, keyword arguments)

    obj() := func(*args, **kwargs)
    """
    return _ArgFunc(func, *args, **kwargs).run


class _ArgFunc():
    '''A class with function reference and arguments storage for ease of use.
    When constructed, obj.run can be used where a lambda could go.

    obj = ArgFunc(function, arguments, keyword arguments)

    .run() runs function, supplying all arguments to it as parameters
    '''

    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        self.func(*self.args, **self.kwargs)


def ensure_file(path):
    # TODO: update this function and it's calls to take a normal path string instead of list
    """Takes a path string representing a relative file path and name, creates
    the file if it does not exist, and returns the OS-specific tuple of strings:
        (absolute file location, absolute filepath+name)
    """
    assert isinstance(path, str), 'provide a filename string (directory optional)'
    from os.path import abspath, dirname, basename, isfile, isdir
    from os import makedirs

    result = SimpleNamespace()
    result.fullpath = abspath(path)
    result.filedir = dirname(result.fullpath)
    result.filename = basename(result.fullpath)
    assert result.filename != ''

    if isdir(result.filedir):
        result.made_dir = False
    else:
        makedirs(result.filedir)
        result.made_dir = True

    if not isfile(result.fullpath):
        with open(result.fullpath, 'a') as f:
            f.close()
        result.made_file = True
    else:
        result.made_file = False

    return result


__all__ = ['isFunc', 'getAllFuncs', 'getAllClasses', 'tupleDistance', 'applyDefaultArgs',
           'constrain', 'constrain_2', 'constrain_decider', 'rescale', 'deadband', 'deadband_2',
           'gettimestamp', 'ensure_file']
