import pytest
from generalUtils import isFunc, getAllClasses, getAllFuncs, tupleDistance, applyDefaultArgs
from generalUtils.sympy_utils import exprIsSafe
from generalUtils.color_utils import colorList, rgb_to_hex, hex_to_rgb, findColor
from generalUtils.qt_utils import getCurrentColor
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


def test_rgb_vs_hex():
    # check all colors in colorList
    for c in colorList:
        # make sure conversions work
        assert '#'+rgb_to_hex(c[2]) == c[1]
        assert hex_to_rgb(c[1]) == c[2]


def test_findColor():
    # check all colors in colorList
    for C in colorList:
        # possible identifiers are all names in C[0], hex string in C[1], and rgb tuple in C[2]
        clist = C[0] + list((C[1], C[2]))

        # each identifier returns correct color
        for c in clist:
            assert findColor(c) == C

    # check all colors in colorList
    for c in colorList:
        # adjust rgb values slightly to test the search algorithm (which gets closest by rgb tupleDistance)
        assert c == findColor((c[2][0]+2, c[2][1]-2, c[2][2]))
        assert c == findColor((c[2][0], c[2][1]+2, c[2][2]-2))
        assert c == findColor((c[2][0]-2, c[2][1], c[2][2]+2))


def test_getAllFuncs(d=locals()):
    correct_set = {'test_getAllFuncs', 'getAllFuncs', 'isFunc', 'funct', 'getAllClasses',
                   'test_getAllClasses', 'test_isFunc', 'exprIsSafe', 'test_exprIsSafe',
                   'lam', 'meth', 'tupleDistance', 'applyDefaultArgs', 'test_applyDefaultArgs',
                   'hex_to_rgb', 'rgb_to_hex', 'test_rgb_vs_hex', 'findColor', 'test_findColor',
                   'getCurrentColor'
            }

    print(set(getAllFuncs(d)) - correct_set)
    assert set(getAllFuncs(d)) == correct_set
