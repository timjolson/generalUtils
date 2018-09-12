from generalUtils import isFunc, getAllClasses, getAllFuncs, expr_is_safe, distance
# from generalUtils import *
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


def test_expr_is_safe():
    # test each expression
    for expr in expr_safe_check:
        assert expr_is_safe(expr[0]) is expr[1]
        # also test expr inside a function
        assert expr_is_safe(f"sin({expr[0]})") is expr[1]


def test_getAllClasses(d = locals()):
    assert getAllClasses(d) == ['Klass']


def test_getAllFuncs(d = locals()):
    print(getAllFuncs(d))
    assert set(getAllFuncs(d)) == \
           {'test_getAllFuncs', 'getAllFuncs', 'isFunc', 'funct', 'getAllClasses',
                'test_getAllClasses', 'test_isFunc', 'expr_is_safe', 'test_expr_is_safe',
                'lam', 'meth', 'distance'
            }
