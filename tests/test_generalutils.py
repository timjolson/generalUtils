import pytest
from generalUtils import is_func, get_all_classes, get_all_funcs, apply_default_args


# helpers: sample function, lambda, class, object, call
class Klass():
    def __init__(self):
        pass
    def klassMethod(self):
        pass

obj = Klass()
meth = obj.klassMethod
lam = lambda x: x
def funct(x):
    return [x]


def test_is_func():
    # Positive / True
    assert is_func(lambda x: [x])
    assert is_func(lam)
    assert is_func(funct)
    assert is_func(Klass.klassMethod)
    assert is_func(obj.klassMethod)
    assert is_func(meth)

    # Negative / False
    assert not is_func('')
    assert not is_func([])
    assert not is_func(1)
    assert not is_func(dict())
    assert not is_func(('', '', ''))


def test_get_all_classes(d=locals()):
    assert get_all_classes(d) == ['Klass']


def test_apply_default_args():
    default = {'a':1, 'b':2, 'c':3}
    kw_ab = {'a':0, 'b':1}
    kw_ad = {'a':0, 'd':4}

    d, ns = apply_default_args(kw_ab, default)
    assert isinstance(d, dict)
    assert all(k in d.keys() for k in default.keys())
    assert d['a'] == 0
    assert d['b'] == 1
    assert d['c'] == 3
    assert ns.a == 0
    assert ns.b == 1
    assert ns.c == 3

    with pytest.raises(ValueError):
        apply_default_args(kw_ad, default)


def test_get_all_funcs(d=locals()):
    correct_set = {'test_get_all_funcs', 'get_all_funcs', 'is_func', 'funct', 'get_all_classes',
                   'test_get_all_classes', 'test_is_func',
                   'lam', 'meth', 'apply_default_args', 'test_apply_default_args',
            }

    print(set(get_all_funcs(d)) - correct_set)
    assert set(get_all_funcs(d)) == correct_set
