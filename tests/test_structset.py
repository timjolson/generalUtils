from generalUtils import StructSet


a=StructSet()
print(a)
a=StructSet({'a':'A'})
print(a)
a=StructSet(a='A')
print(a)
try:
    a=StructSet({'a':1,'b':2}, c=3)
except ValueError:
    print('ValueError')

b=StructSet({'b':'B'})
print(b)
c=StructSet(c='C')
print(c)

print('\nadd')
print(a,b,c)
print(a+a)
print(b+b)
print(c+c)
print(c+a)
print(a+c)
print(b+a)
print(a+b)
print(b+c)
print(c+b)

print('\niadd')
print(a,b,c)
c += b
print(a,b,c)
a += c
print(a,b,c)

print('\nsub')
print(a,b,c)
print(c-a)
print(a-c)
print(b-a)
print(a-b)
print(b-c)
print(c-b)

print('\nisub')
print(a,b,c)
a -= b
print(a,b,c)
a -= c
print(a,b,c)
c -= b
print(a,b,c)

print('\n==')
A={'a':'A'}
B={'b':'B'}
C={'c':'C'}
d=StructSet(a='A')
assert (a==d) == True

assert (a==a) == True
assert (a==b) == False
assert (a==c) == False
assert (a==A) == True
assert (a==B) == False
assert (a==C) == False
assert (b==a) == False
assert (b==b) == True
assert (b==c) == False
assert (b==A) == False
assert (b==B) == True
assert (b==C) == False
assert (c==a) == False
assert (c==b) == False
assert (c==c) == True
assert (c==A) == False
assert (c==B) == False
assert (c==C) == True
print('All good')

print('\n!=')
assert (a!=a) == False
assert (a!=b) == True
assert (a!=c) == True
assert (a!=A) == False
assert (a!=B) == True
assert (a!=C) == True
assert (b!=a) == True
assert (b!=b) == False
assert (b!=c) == True
assert (b!=A) == True
assert (b!=B) == False
assert (b!=C) == True
assert (c!=a) == True
assert (c!=b) == True
assert (c!=c) == False
assert (c!=A) == True
assert (c!=B) == True
assert (c!=C) == False
print('All good')

print('**** with dict()s ****')
print('\nadd')
A, B, C, D = {'a':'A'}, {'b':'B'}, {'c':'C'}, {'a':'A'}
print(a+A)
print(a+B)
print(a+C)
print(b+A)
print(b+B)
print(b+C)
print(c+A)
print(c+B)
print(c+C)

print('\niadd')
print(a,b,c)
c += B
print(a,b,c)
a += C
print(a,b,c)

print('\nsub')
a += c
print(a,b,c)
print(c-A)
print(a-C)
print(b-A)
print(a-B)
print(b-C)
print(c-B)

print('\nisub')
print(a,b,c)
a -= B
print(a,b,c)
a -= C
print(a,b,c)
c -= B
print(a,b,c)

print('\ndict()==StructSet()')
A={'a':'A'}
B={'b':'B'}
C={'c':'C'}

assert (A==a) == True
assert (A==b) == False
assert (A==c) == False
assert (A==A) == True
assert (A==B) == False
assert (A==C) == False
assert (B==a) == False
assert (B==b) == True
assert (B==c) == False
assert (B==A) == False
assert (B==B) == True
assert (B==C) == False
assert (C==a) == False
assert (C==b) == False
assert (C==c) == True
assert (C==A) == False
assert (C==B) == False
assert (C==C) == True
print('All good')

print('\ndict()!=StructSet()')
assert (A!=a) == False
assert (A!=b) == True
assert (A!=c) == True
assert (A!=A) == False
assert (A!=B) == True
assert (A!=C) == True
assert (B!=a) == True
assert (B!=b) == False
assert (B!=c) == True
assert (B!=A) == True
assert (B!=B) == False
assert (B!=C) == True
assert (C!=a) == True
assert (C!=b) == True
assert (C!=c) == False
assert (C!=A) == True
assert (C!=B) == True
assert (C!=C) == False
print('All good')

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
