from types import MethodType, FunctionType, LambdaType
from math import sqrt
from copy import copy
from types import SimpleNamespace
import re


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


def distance(x, y):
    """Calculate distance between tuple values.

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


def expr_is_safe(expr_string):
    """Returns whether the string is safe to 'eval()'.
    Detects improper use of '.' attribute access

    :param expr_string: string to check for safety
    :return: True if safe, False otherwise
    """
    assert isinstance(expr_string, str), 'Provide a string expression to verify is safe'
    string = 'expr_string'
    for r in '()+-*/':
        if r in expr_string:
            string += ".replace('" + r + "', ' " + r + " ')"
    expr_string = eval(string, globals(), {'expr_string':expr_string})

    # return re.search(r"((\d*((?=\D)\S)+\d*)+[.])|([.](\d*((?=\D)\S)+))", expr_string) is None
    # return re.search(r"((((?=\D)\S)+\d*)+[.])|([.]\d*((?=[\D])\S)+)", expr_string) is None
    return re.search(r"(((?=\D)\S)+\d*)+[.]|[.]\d*((?=[\D])\S)+", expr_string) is None


def apply_default_args(kwargs, defaultargs):
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


__all__ = ['isFunc', 'getAllFuncs', 'getAllClasses', 'distance', 'expr_is_safe', 'apply_default_args']
