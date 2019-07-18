import pytest
import os
import logging
from collections import namedtuple
import numpy as np

from generalUtils.datastream import DataStream

logging.basicConfig(filename='logs/test_datastream.log', filemode='w', level=logging.DEBUG)


def addpointstester(ds):
    # using np.inf instead of None or np.nan so we can check equality between arrays

    logging.debug('addpoints dict')
    ds.add_point({'x': 0, 'y': 0, 'z': 0})
    logging.debug('addpoints items')
    ds.add_point(1, np.inf, 1)
    logging.debug('addpoints kwargs')
    ds.add_point(x=2, y=1, z=np.inf)
    logging.debug('addpoints tuple')
    ds.add_point((3,2,2))


def check_post_add_points(ds):
    # using np.inf instead of None or np.nan so we can check equality between arrays

    logging.debug('post addpoints')
    assert np.array_equal(ds['x'], [0, 1, 2, 3])
    logging.debug('post addpoints')
    assert np.array_equal(ds['y'], np.array([0., np.inf, 1., 2.]))
    logging.debug('post addpoints')
    assert np.array_equal(ds['z'], np.array([0., 1., np.inf, 2.]))


def check_datastreams_equal(one, two):
    logging.debug('check_datastreams_equal')
    logging.debug(f"Vars: {vars(one), vars(two)}")
    logging.debug(f"points {one.points, two.points}")

    for key in one.keys():
        logging.debug(f"checking '{key}'")
        logging.debug((one[key], two[key]))
        assert np.all(np.equal(one[key], two[key]))
    assert one._keys == two._keys
    return True


def test_constructors():
    logging.debug('---------------Begin test_constructors()')
    ds = DataStream()

    dict1 = {'x': [], 'y': []}
    dict2 = {'x': 1.0, 'y': 1.0}
    dict3 = {'x': [2.0, 3.0], 'y': [2.0, 3.0]}

    point_test = namedtuple('point_test', 'x, y')
    ntup1 = point_test([], [])
    ntup2 = point_test(1.0, 1.0)
    ntup3 = point_test([2.0, 3.0], [2.0, 3.0])

    tup1 = ([], [])
    tup2 = (1.0, 1.0)
    tup3 = ([2.0, 3.0], [2.0, 3.0])

    np1 = (np.array([]), np.array([]))
    np2 = (np.array(1.0), np.array(1.0))
    np3 = (np.array([2.0, 3.0]), np.array([2.0, 3.0]))

    set_to_test = [(dict1, ntup1, tup1, np1),
                   (dict2, ntup2, tup2, np2),
                   (dict3, ntup3, tup3, np3)]

    for d, nt, t, nmpy in set_to_test:
        logging.debug(('testing', d, nt, t, nmpy))

        check_datastreams_equal(DataStream(d), DataStream(nt))
        check_datastreams_equal(DataStream(t), DataStream(nmpy))
        check_datastreams_equal(DataStream(nt), DataStream(t))

    Dict = {'x': [1., 4.], 'y': [2., 5], 'z': [3, 6]}
    data = [(10., 11., 12), (13., 14., 15)]
    assert check_datastreams_equal(DataStream(DataStream(Dict)), DataStream(Dict))
    assert check_datastreams_equal(DataStream(DataStream(data)), DataStream(data))


def test_add_point():
    logging.debug('---------------Begin test_add_point()')
    Dict2 = {'x': 7, 'y': 8, 'z': 9}
    data2 = (16, 17, 18)

    arr = DataStream()

    arr.add_point(Dict2)
    assert np.all(arr['x'] == [7])
    assert np.all(arr['y'] == [8])
    assert np.all(arr['z'] == [9])

    arr.add_point(data2)
    assert np.all(arr['x'] == [7,16])
    assert np.all(arr['y'] == [8,17])
    assert np.all(arr['z'] == [9,18])

    ds = DataStream()
    addpointstester(ds)
    check_post_add_points(ds)


def test_add_points():
    logging.debug('---------------Begin test_add_points()')
    Dict = {'x': [1., 4.], 'y': [2., 5], 'z': [3, 6]}
    Dict2 = {'x': 7, 'y': 8, 'z': 9}
    data = [(10., 11., 12), (13., 14., 15)]
    data2 = (16, 17, 18)

    arr = DataStream(Dict)
    assert np.all(arr['x'] == Dict['x'])
    assert np.all(arr['y'] == Dict['y'])
    assert np.all(arr['z'] == Dict['z'])

    arr.add_points(Dict2)
    assert np.all(arr['x'] == [1.,4.,7])
    assert np.all(arr['y'] == [2.,5,8])
    assert np.all(arr['z'] == [3,6,9])

    arr.add_points(data)
    assert np.all(arr['x'] == [1.,4.,7,10.,13])
    assert np.all(arr['y'] == [2.,5,8,11.,14])
    assert np.all(arr['z'] == [3,6,9,12,15])

    arr.add_points(data2)
    assert np.all(arr['x'] == [1.,4.,7,10.,13,16])
    assert np.all(arr['y'] == [2.,5,8,11.,14,17])
    assert np.all(arr['z'] == [3,6,9,12,15,18])


def test_add_point_error():
    logging.debug('---------------Begin test_add_point_error()')
    ds = DataStream()
    addpointstester(ds)

    with pytest.raises(ValueError):
        try:
            ds.add_point((0,1))
        except Exception as e:
            logging.debug(e)
            raise
    with pytest.raises(ValueError):
        try:
            ds.add_point(0, 1)
        except Exception as e:
            logging.debug(e)
            raise
    with pytest.raises(ValueError):
        try:
            ds.add_point(x=0, y=1)
        except Exception as e:
            logging.debug(e)
            raise
    with pytest.raises(ValueError):
        try:
            ds.add_point({'y':99, 'z':10})
        except Exception as e:
            logging.debug(e)
            raise


def test_record_file_csv():
    logging.debug('---------------Begin test_record_file_csv()')

    file = './logs/datastream_test_record_file_csv.log'
    try: os.remove(file)
    except: pass

    dict2 = {'x': 1.0, 'y': 1.0}

    ds = DataStream(record_to_file=file)

    ds.add_point(dict2)
    assert (os.linesep).join(['x,y', '1.0,1.0'])+os.linesep == open(file, 'r').read()

    ds.add_point(dict2)
    assert (os.linesep).join(['x,y', '1.0,1.0', '1.0,1.0'])+os.linesep == open(file, 'r').read()


def test_record_file_dict():
    logging.debug('---------------Begin test_record_file_dict()')

    file = './logs/datastream_test_record_file_dict.log'
    try: os.remove(file)
    except: pass

    dict2 = {'x': 1.0, 'y': 1.0}

    ds = DataStream(record_to_file=file, file_format='dict')
    ds.add_point(dict2)
    assert str({'x':1.0,'y':1.0}) + os.linesep == open(file, 'r').readlines()[-1]

    ds.add_point(dict2)
    assert str({'x':1.0,'y':1.0}) + os.linesep == open(file, 'r').readlines()[-1]


def test_record_file_list():
    logging.debug('---------------Begin test_record_file_list()')

    file = './logs/datastream_test_record_file_list.log'
    try: os.remove(file)
    except: pass

    dict2 = {'x': 1.0, 'y': 1.0}

    ds = DataStream(record_to_file=file, file_format='list')
    ds.add_point(dict2)
    assert 'x,y' + os.linesep + str(list(dict2.values())) + os.linesep == open(file, 'r').read()
    assert str(list(dict2.values())) + os.linesep == open(file, 'r').readlines()[-1]

    ds.add_point(dict2)
    assert str(list(dict2.values())) + os.linesep == open(file, 'r').readlines()[-1]


def test_array_ops():
    Dict = {'x': [1., 4.], 'y': [2., 5], 'z': [3, 6]}
    arr = DataStream(Dict)
    assert arr.dtype == np.float64

    # check by point
    assert np.all(arr[:,0] == [1., 2., 3])
    assert np.all(arr[:,1] == [4., 5., 6])

    # check x
    assert np.all(arr['x'] == arr['x',:])
    assert np.all(arr['x'] == arr[0,:])
    assert np.all(arr['x'] == [1,4])
    assert arr['x',0] == 1 == arr['x'][0]
    assert arr['x',1] == 4 == arr['x'][1]

    # check y
    assert np.all(arr['y'] == arr['y',:])
    assert np.all(arr['y'] == arr[1,:])
    assert np.all(arr['y'] == [2, 5])
    assert arr['y',0] == 2 == arr['y'][0]
    assert arr['y',1] == 5 == arr['y'][1]

    #check z
    assert np.all(arr['z'] == arr['z',:])
    assert np.all(arr['z'] == arr[2,:])
    assert np.all(arr['z'] == [3, 6])
    assert arr['z',0] == 3 == arr['z'][0]
    assert arr['z',1] == 6 == arr['z'][1]

    assert check_datastreams_equal(eval(repr(arr), {}, {'DataStream':DataStream,'array':np.array, 'float64':np.float64}), arr)
