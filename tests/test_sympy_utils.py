import pytest
from generalUtils.sympy_utils import expr_is_safe, expr_safe_check


def test_expr_is_safe():
    # test each expression
    for expr in expr_safe_check:
        assert expr_is_safe(expr[0]) is expr[1]
        # also test expr inside a function
        assert expr_is_safe(f"sin({expr[0]})") is expr[1]
