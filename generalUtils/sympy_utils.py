import re


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


__all__ = ['expr_is_safe', 'expr_safe_check']
