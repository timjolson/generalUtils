import pytest
# from generalUtils import isFunc, getAllClasses, getAllFuncs, exprIsSafe, tupleDistance
from generalUtils import *
from generalUtils.helpers_for_tests import expr_safe_check


# helpers: sample function, lambda, class, object, method
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


def test_isFunc():
    # Positive / True
    assert isFunc(lambda x: [x])
    assert isFunc(lam)
    assert isFunc(funct)
    assert isFunc(Klass.klassMethod)
    assert isFunc(obj.klassMethod)
    assert isFunc(meth)

    # Negative / False
    assert not isFunc('')
    assert not isFunc([])
    assert not isFunc(1)
    assert not isFunc(dict())
    assert not isFunc(('','',''))


def test_exprIsSafe():
    # test each expression
    for expr in expr_safe_check:
        assert exprIsSafe(expr[0]) is expr[1]
        # also test expr inside a function
        assert exprIsSafe(f"sin({expr[0]})") is expr[1]


def test_getAllClasses(d = locals()):
    assert getAllClasses(d) == ['Klass']


def test_applyDefaultArgs():
    default = {'a':1, 'b':2, 'c':3}
    kw_ab = {'a':0, 'b':1}
    kw_ad = {'a':0, 'd':4}

    d, ns = applyDefaultArgs(kw_ab, default)
    assert isinstance(d, dict)
    assert all(k in d.keys() for k in default.keys())
    assert d['a'] == 0
    assert d['b'] == 1
    assert d['c'] == 3
    assert ns.a == 0
    assert ns.b == 1
    assert ns.c == 3

    with pytest.raises(TypeError):
        applyDefaultArgs(kw_ad, default)


def test_getAllFuncs(d=locals()):
    correct_set = {'test_getAllFuncs', 'getAllFuncs', 'isFunc', 'funct', 'getAllClasses',
                'test_getAllClasses', 'test_isFunc', 'exprIsSafe', 'test_exprIsSafe',
                'lam', 'meth', 'tupleDistance', 'applyDefaultArgs', 'test_applyDefaultArgs'
            }
    print(set(getAllFuncs(d)) - correct_set)
    assert set(getAllFuncs(d)) == correct_set
