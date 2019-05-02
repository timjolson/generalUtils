import pytest
from generalUtils.sympy_utils import expr_is_safe


# sample expressions to test
# ( expr, is_safe, causes error in sympy widgets, is valid identifier(variable name) )
expr_safe_check = [
    ('.a ', False, True, False),
    ('abc', True, False, True),
    ('1.1)', True, True, False),
    ('a)', True, True, False),
    ('1234a.', False, True, False),
    ('12a.a', False, True, False),
    ('1.a ', False, True, False),
    ('a.1 ', False, True, False),
    ('12a12.', False, True, False),
    ('2+4.1', True, False, False),
    ('a.a ', False, True, False),
    ('12a12.12a', False, True, False),
    ('.1 ', True, False, False),
    ('a.a', False, True, False),
    ('.a12', False, True, False),
    ('12a12.12', False, True, False),
    ('1212.a', False, True, False),
    ('ab.ab ', False, True, False),
    ('1212.12a', False, True, False),
    ('.ab ', False, True, False),
    ('a', True, False, True),
    ('.12a', False, True, False),
    ('1.ab ', False, True, False),
    ('error', True, False, True),
    ('ab.1 ', False, True, False),
    ('(a', True, True, False),
    ('1.1 ', True, False, False),
    ('a. ', False, True, False),
    ('12.12a', False, True, False),
    ('1. ', True, False, False),
    ('', True, False, False),
    ('ab. ', False, True, False),
    ('text', True, False, True),
    ('text_2', True, False, True),
    ('text2', True, False, True),
    ('text2a', True, False, True),
    ('text2.', False, True, False),
]


def test_expr_is_safe():
    # test each expression
    for expr in expr_safe_check:
        assert expr_is_safe(expr[0]) is expr[1]
        # also test expr inside a function
        assert expr_is_safe(f"sin({expr[0]})") is expr[1]
