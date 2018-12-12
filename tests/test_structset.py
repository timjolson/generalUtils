import pytest
from generalUtils import StructSet


def test_constructor():
    a = StructSet()
    assert str(a) == 'StructSet()'

    a = StructSet({'a': 'A'})
    assert str(a) == "StructSet(a='A')"

    a = StructSet(a='A')
    assert str(a) == "StructSet(a='A')"

    with pytest.raises(ValueError):
        a = StructSet({'a': 1, 'b': 2}, c=3)

    b=StructSet({'b':'B'})
    assert str(b) == "StructSet(b='B')"

    c=StructSet(c='C')
    assert str(c) == "StructSet(c='C')"


def test_eq():
    a = StructSet(a='A')
    b = StructSet({'b': 'B'})
    c = StructSet(c='C')

    assert StructSet(a='A', b='B') == StructSet(b='B', a='A')

    A = {'a':'A'}
    B = {'b':'B'}
    C = {'c':'C'}

    assert (a == a) is True
    assert (a == b) is False
    assert (a == c) is False
    assert (a == A) is True
    assert (a == B) is False
    assert (a == C) is False
    assert (b == a) is False
    assert (b == b) is True
    assert (b == c) is False
    assert (b == A) is False
    assert (b == B) is True
    assert (b == C) is False
    assert (c == a) is False
    assert (c == b) is False
    assert (c == c) is True
    assert (c == A) is False
    assert (c == B) is False
    assert (c == C) is True


def test_neq():
    a = StructSet(a='A')
    b = StructSet({'b': 'B'})
    c = StructSet(c='C')

    A = {'a': 'A'}
    B = {'b': 'B'}
    C = {'c': 'C'}

    assert (a != a) is False
    assert (a != b) is True
    assert (a != c) is True
    assert (a != A) is False
    assert (a != B) is True
    assert (a != C) is True
    assert (b != a) is True
    assert (b != b) is False
    assert (b != c) is True
    assert (b != A) is True
    assert (b != B) is False
    assert (b != C) is True
    assert (c != a) is True
    assert (c != b) is True
    assert (c != c) is False
    assert (c != A) is True
    assert (c != B) is True
    assert (c != C) is False


def test_add():
    a = StructSet(a='A')
    b = StructSet({'b': 'B'})
    c = StructSet(c='C')

    assert a+a == a
    assert b+b == b
    assert c+c == c
    assert c+a == StructSet(c='C', a='A') == StructSet(a='A', c='C')
    assert a+c == StructSet(a='A', c='C')
    assert b+a == StructSet(b='B', a='A')
    assert a+b == StructSet(a='A', b='B')
    assert b+c == StructSet(b='B', c='C')
    assert c+b == StructSet(c='C', b='B')


def test_iadd():
    a = StructSet(a='A')
    b = StructSet({'b': 'B'})
    c = StructSet(c='C')

    c += b
    assert c == StructSet(c='C', b='B')
    a += c
    assert a == StructSet(a='A', c='C', b='B')


def test_sub():
    a = StructSet(a='A')
    b = StructSet({'b': 'B'})
    c = StructSet(c='C')

    assert c-a == c
    assert a-c == a
    assert b-a == b
    assert a-b == a
    assert b-c == b
    assert c-b == c

    a = StructSet(a='A')
    b = StructSet({'b': 'B'})
    c = StructSet(c='C')
    d = StructSet(d='D')
    assert c-a == c
    assert a-c == a

    c += d
    assert c-d == StructSet(c='C')
    assert c-d-c == StructSet()


def test_isub():
    a = StructSet(a='A')
    b = StructSet({'b': 'B'})
    c = StructSet(c='C')

    a += b
    c += b

    assert c == StructSet(c='C', b='B')
    c -= b
    assert c == StructSet(c='C')
    c -= a
    assert c == StructSet(c='C')
    c -= c
    assert c == StructSet()


def test_add_dict():
    a = StructSet(a='A')
    b = StructSet({'b': 'B'})
    c = StructSet(c='C')

    A = {'a': 'A'}
    B = {'b': 'B'}
    C = {'c': 'C'}

    assert a+A == a
    assert a+B == StructSet(a='A', b='B')
    assert a+C == StructSet(a='A', c='C')
    assert b+B == b
    assert b+C == StructSet(b='B', c='C')
    assert c+A == StructSet(c='C', a='A')
    assert c+B == StructSet(c='C', b='B')
    assert c+C == c


def test_iadd_dict():
    a = StructSet(a='A')
    b = StructSet({'b': 'B'})
    c = StructSet(c='C')

    A = {'a': 'A'}
    B = {'b': 'B'}
    C = {'c': 'C'}

    c += B
    assert c == StructSet(c='C', b='B')
    a += C
    assert a == StructSet(a='A', b='B', c='C')


def test_sub_dict():
    a = StructSet(a='A')
    b = StructSet({'b': 'B'})
    c = StructSet(c='C')

    A = {'a': 'A'}
    B = {'b': 'B'}
    C = {'c': 'C'}
    D = A.copy()
    D.update(C)

    assert a - C == a
    assert a - B == a
    assert a - A == StructSet()

    assert b - A == b
    assert b - C == b
    assert b - B == StructSet()

    assert c - A == c
    assert c - B == c
    assert c - C == StructSet()

    assert b - D == b
    assert c - D == StructSet()
    assert a - D == c


def test_isub_dict():
    a = StructSet(a='A')
    b = StructSet({'b': 'B'})
    c = StructSet(c='C')

    A = {'a': 'A'}
    B = {'b': 'B'}
    C = {'c': 'C'}

    a += b
    c += b

    assert c == StructSet(c='C', b='B')
    c -= B
    assert c == StructSet(c='C')
    c -= A
    assert c == StructSet(c='C')
    c -= C
    assert c == StructSet()


def test_eq_dict():
    a = StructSet(a='A')
    b = StructSet({'b': 'B'})
    c = StructSet(c='C')

    A = {'a':'A'}
    B = {'b':'B'}
    C = {'c':'C'}

    assert (A == a) is True
    assert (A == b) is False
    assert (A == c) is False
    assert (A == A) is True
    assert (A == B) is False
    assert (A == C) is False
    assert (B == a) is False
    assert (B == b) is True
    assert (B == c) is False
    assert (B == A) is False
    assert (B == B) is True
    assert (B == C) is False
    assert (C == a) is False
    assert (C == b) is False
    assert (C == c) is True
    assert (C == A) is False
    assert (C == B) is False
    assert (C == C) is True


def test_neq_dict():
    a = StructSet(a='A')
    b = StructSet({'b': 'B'})
    c = StructSet(c='C')

    A = {'a':'A'}
    B = {'b':'B'}
    C = {'c':'C'}

    assert (A != a) is False
    assert (A != b) is True
    assert (A != c) is True
    assert (A != A) is False
    assert (A != B) is True
    assert (A != C) is True
    assert (B != a) is True
    assert (B != b) is False
    assert (B != c) is True
    assert (B != A) is True
    assert (B != B) is False
    assert (B != C) is True
    assert (C != a) is True
    assert (C != b) is True
    assert (C != c) is False
    assert (C != A) is True
    assert (C != B) is True
    assert (C != C) is False


def test_end():
    a = StructSet(a='A')
    b = StructSet({'b': 'B'})
    c = StructSet(c='C')

    A = {'a':'A'}
    B = {'b':'B'}
    C = {'c':'C'}

    a += A
    a += B
    a += C
    b += A
    b += B
    b += C
    c += A
    c += B
    c += C

    a -= A
    a -= B
    a -= C
    b -= A
    b -= B
    b -= C
    c -= A
    c -= B
    c -= C

    assert c == StructSet()
