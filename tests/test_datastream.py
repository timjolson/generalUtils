import pytest
from generalUtils.datastream import DataStream
#TODO: use pytest


X = [i for i in range(4)]
Y = [i + 1 for i in range(4)]
Z = [i ** 2 for i in range(3)]

# ~ c,ld,lf,r
# ~ _
# ~ c
# ~ c,ld
# ~ c,lf
# ~ c,r
# ~ c,ld,lf
# ~ c,ld,r
# ~ c,ld,lf,r
# ~ c,lf,r
# ~ ld
# ~ ld,lf
# ~ ld,r
# ~ ld,lf,r
# ~ lf
# ~ lf,r
# ~ r

print('Make DataStream')
ds = DataStream()


def addpoints_test():
    print(ds.curves)
    print(ds.points)
    ds.add_point({'x': 0, 'y': 0, 'z': 0})
    ds.add_point({'x': 0, 'z': 0})
    ds.add_point({'x': 0, 'y': 0})
    ds.add_point(1, 1, 1)
    ds.add_point(2, 2)
    ds.add_point(3, 3, 3, 3)
    print(ds.curves)
    print(ds.points)


addpoints_test()

print('\nDataStream with a curves')
ds = DataStream(
    curves={'x': 'b3l', 'y': 'g2-.', 'z': 'k3-..'}
)

addpoints_test()

print('\nDataStream with curves, load_data')
ds = DataStream(
    curves={'x': 'b3l', 'y': 'g2-.', 'z': 'k3-..'},
    load_data={'x': X, 'y': Y, 'z': Z}
)

addpoints_test()

print('\nDataStream with curves, load_file')
ds = DataStream(
    curves={'x': 'b3l', 'y': 'g2-.', 'z': 'k3-..'},
    load_file='logs/streams/test.log'
)

addpoints_test()

print('\nDataStream with curves, record_file')
ds = DataStream(
    curves={'x': 'b3l', 'y': 'g2-.', 'z': 'k3-..'},
    record_file='logs/streams/test2.log'
)

addpoints_test()

print('\nDataStream with curves, load_data, load_file')
ds = DataStream(
    curves={'x': 'b3l', 'y': 'g2-.', 'z': 'k3-..'},
    load_data={'x': X, 'y': Y, 'z': Z},
    load_file='logs/streams/test.log'
)

addpoints_test()

print('\nDataStream with curves, load_data, record_file')
ds = DataStream(
    curves={'x': 'b3l', 'y': 'g2-.', 'z': 'k3-..'},
    load_data={'x': X, 'y': Y, 'z': Z},
    load_file='logs/streams/test.log'
)

addpoints_test()

print('\nDataStream with everything')
ds = DataStream(
    curves={'x': 'b3l', 'y': 'g2-.', 'z': 'k3-..'},
    record_file='logs/streams/test2.log',
    load_data={'x': X, 'y': Y, 'z': Z},
    load_file='logs/streams/test.log'
)

addpoints_test()

print('\nDataStream with curves, load_file, record_file')
ds = DataStream(
    curves={'x': 'b3l', 'y': 'g2-.', 'z': 'k3-..'},
    record_file='logs/streams/test.log',
    load_file='logs/streams/test.log'
)

addpoints_test()

print('\nDataStream with load_data')
ds = DataStream(
    load_data={'x': X, 'y': Y, 'z': Z}
)

addpoints_test()

print('\nDataStream with load_data and load_file')
ds = DataStream(
    load_data={'x': X, 'y': Y, 'z': Z},
    load_file='logs/streams/test2.log'
)

addpoints_test()

print('\nDataStream with load_data and record_file')
ds = DataStream(
    record_file='logs/streams/test.log',
    load_data={'x': X, 'y': Y, 'z': Z}
)

addpoints_test()

print('\nDataStream with load_data, load_file and record_file')
ds = DataStream(
    load_data={'x': X, 'y': Y, 'z': Z},
    record_file='logs/streams/test2.log',
    load_file='logs/streams/test2.log'
)

addpoints_test()

print('\nDataStream with load_file')
ds = DataStream(
    load_file='logs/streams/test.log'
)

addpoints_test()

print('\nDataStream with load_file and record_file')
ds = DataStream(
    record_file='logs/streams/test.log',
    load_file='logs/streams/test2.log'
)

addpoints_test()

print('\nDataStream with record_file')
ds = DataStream(
    record_file='logs/streams/test.log',
)

addpoints_test()