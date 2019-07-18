import pytest
import os
import logging
from collections import namedtuple
import numpy as np

from generalUtils.datastream import DataStream, data_type

logging.basicConfig(filename='logs/test_datastream.log', filemode='w', level=logging.INFO)

# test data
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
VALUES1 = np.array([[],[]])
VALUES2 = np.array([[1.0],[1.0]])
VALUES3 = np.array([[2.0,3.0],[2.0,3.0]])
KEYS = {'x', 'y'}


def add_point_tester(ds):
    # using np.inf instead of None or np.nan so we can check equality between arrays

    logging.debug('addpoints dict')
    ds.add_points({'x': 0, 'y': 0, 'z': 0})
    logging.debug('addpoints items')
    ds.add_points(1, np.inf, 1)
    logging.debug('addpoints kwargs')
    ds.add_points(x=2, y=1, z=np.inf)
    logging.debug('addpoints tuple')
    ds.add_points((3, 2, 2))


def check_post_add_point(ds):
    # using np.inf instead of None or np.nan so we can check equality between arrays

    logging.debug('post addpoints')
    assert np.array_equal(ds['x'], [0, 1, 2, 3])
    logging.debug('post addpoints')
    assert np.array_equal(ds['y'], np.array([0., np.inf, 1., 2.]))
    logging.debug('post addpoints')
    assert np.array_equal(ds['z'], np.array([0., 1., np.inf, 2.]))


def check_datastreams_equal(one, two):
    logging.debug('check_datastreams_equal')
    logging.debug(f"keys {one._keys, two._keys}")
    logging.debug(f"points {one.points, two.points}")

    assert set(one._keys) == set(two._keys)
    assert np.all(one.points == two.points)


def test_base_constructor():
    logging.debug('---------------Begin test_base_constructor()')
    ds = DataStream()
    assert ds.dtype == np.float64


def test_dataType():
    logging.debug('---------------Begin test_dataType()')

    assert data_type(dict1) == 'dictOfLists'
    assert data_type(dict2) == 'dictOfValues'

    assert data_type(ntup1) == 'listOfLists'
    assert data_type(ntup2) == 'listOfValues'

    assert data_type(tup1) == 'listOfLists'
    assert data_type(tup2) == 'listOfValues'

    assert data_type(np1) == 'listOfLists'
    assert data_type(np2) == 'listOfLists'

    assert data_type(DataStream()) == 'empty'

    assert data_type(DataStream([[], [], []])) == 'DataStream'


def test_constructor_point():
    logging.debug('---------------Begin test_constructor_point()')

    for data in [dict1, ntup1, tup1, np1]:
        ds = DataStream(data)
        assert data_type(ds) == 'DataStream'
        assert np.all(ds.points == VALUES1)
        assert set(ds.keys()) == KEYS

    for data in [dict2, ntup2, tup2, np2]:
        ds = DataStream(data)
        assert data_type(ds) == 'DataStream'
        assert np.all(ds.points == VALUES2)
        assert set(ds.keys()) == KEYS


def test_constructor_points():
    logging.debug('---------------Begin test_constructor_points()')

    for data in [dict3, ntup3, tup3, np3]:
        ds = DataStream(data)
        assert data_type(ds) == 'DataStream'
        assert np.all(ds.points == VALUES3)
        assert set(ds.keys()) == KEYS


def test_add_points():
    logging.debug('---------------Begin test_add_points()')

    ds = DataStream()
    add_point_tester(ds)
    check_post_add_point(ds)

    ds = DataStream()
    ds.add_points(1,2)
    # assert np.all(ds.points == np.array([[1],[2]]))
    ds.add_points({'x':3,'y':4})
    # assert np.all(ds.points == np.array([[1,3],[2,4]]))
    ds.add_points((5,6))
    # assert np.all(ds.points == np.array([[1,3,5],[2,4,6]]))
    ds.add_points([[7],[8]])
    # assert np.all(ds.points == np.array([[1,3,5,7],[2,4,6,8]]))
    ds.add_points(y=10,x=9)
    # assert np.all(ds.points == np.array([[1,3,5,7,9],[2,4,6,8,10]]))
    ds.add_points([(11),(12)])
    # assert np.all(ds.points == np.array([[1,3,5,7,9,11],[2,4,6,8,10,12]]))
    ds.add_points(np.array([[13],[14]]))
    # assert np.all(ds.points == np.array([[1,3,5,7,9,11,13],[2,4,6,8,10,12,14]]))

    assert np.all(ds['x'] == [1,3,5,7,9,11,13])
    assert np.all(ds['y'] == [2,4,6,8,10,12,14])
    assert np.all(ds[:,0] == [1,2])
    assert np.all(ds[:,1] == [3,4])
    assert np.all(ds[:,2] == [5,6])
    assert np.all(ds[:,3] == [7,8])
    assert np.all(ds[:,4] == [9,10])
    assert np.all(ds[:,5] == [11,12])
    assert np.all(ds[:,6] == [13,14])


def test_extend_points():
    logging.debug('---------------Begin test_extend_points()')

    ds = DataStream()
    add_point_tester(ds)
    check_post_add_point(ds)

    ds = DataStream()
    ds.add_points([1,3], [2,4])
    # assert np.all(ds.points == np.array([[1,3],[2,4]]))
    ds.add_points({'x':[5,7], 'y':[6,8]})
    # assert np.all(ds.points == np.array([[1,3,5,7],[2,4,6,8]]))
    ds.add_points(y=[10,12], x=[9,11])
    # assert np.all(ds.points == np.array([[1,3,5,7,9,11],[2,4,6,8,10,12]]))
    ds.add_points(np.array([[13,15],[14,16]]))
    # assert np.all(ds.points == np.array([[1,3,5,7,9,11,13,15],[2,4,6,8,10,12,14,16]]))

    assert np.all(ds['x'] == [1,3,5,7,9,11,13,15])
    assert np.all(ds['y'] == [2,4,6,8,10,12,14,16])
    assert np.all(ds[:,0] == [1,2])
    assert np.all(ds[:,1] == [3,4])
    assert np.all(ds[:,2] == [5,6])
    assert np.all(ds[:,3] == [7,8])
    assert np.all(ds[:,4] == [9,10])
    assert np.all(ds[:,5] == [11,12])
    assert np.all(ds[:,6] == [13,14])
    assert np.all(ds[:,7] == [15,16])


def test_add_point_error():
    logging.debug('---------------Begin test_add_point_error()')
    ds = DataStream()
    add_point_tester(ds)

    logging.debug('---------------Start exceptions')
    with pytest.raises(ValueError):
        try:
            ds.add_points((0, 1))
        except Exception as e:
            logging.debug(e)
            raise
    with pytest.raises(ValueError):
        try:
            ds.add_points(0, 1)
        except Exception as e:
            logging.debug(e)
            raise
    with pytest.raises(ValueError):
        try:
            ds.add_points(x=0, y=1)
        except Exception as e:
            logging.debug(e)
            raise
    with pytest.raises(ValueError):
        try:
            ds.add_points({'y':99, 'z':10})
        except Exception as e:
            logging.debug(e)
            raise
    with pytest.raises(ValueError):
        try:
            ds.add_points((0, 1, 2, 3))
        except Exception as e:
            logging.debug(e)
            raise
    with pytest.raises(ValueError):
        try:
            ds.add_points(0, 1, 2, 3)
        except Exception as e:
            logging.debug(e)
            raise
    with pytest.raises(ValueError):
        try:
            ds.add_points(x=0, y=1, z=2, w=3)
        except Exception as e:
            logging.debug(e)
            raise
    with pytest.raises(ValueError):
        try:
            ds.add_points({'x':0, 'y':99, 'z':10, 'w':1})
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

    ds.add_points(dict2)
    assert open(file, 'r').read() == (os.linesep).join(['x,y', '1.0,1.0'])+os.linesep

    ds.add_points(dict2)
    assert open(file, 'r').read() == (os.linesep).join(['x,y', '1.0,1.0', '1.0,1.0'])+os.linesep


def test_record_file_dict():
    logging.debug('---------------Begin test_record_file_dict()')

    file = './logs/datastream_test_record_file_dict.log'
    try: os.remove(file)
    except: pass

    dict2 = {'x': 1.0, 'y': 1.0}

    ds = DataStream(record_to_file=file, file_format='dict')
    ds.add_points(dict2)
    assert str({'x':1.0,'y':1.0}) + os.linesep == open(file, 'r').readlines()[-1]

    ds.add_points(dict2)
    assert str({'x':1.0,'y':1.0}) + os.linesep == open(file, 'r').readlines()[-1]


def test_record_file_list():
    logging.debug('---------------Begin test_record_file_list()')

    file = './logs/datastream_test_record_file_list.log'
    try: os.remove(file)
    except: pass

    dict2 = {'x': 1.0, 'y': 1.0}

    ds = DataStream(record_to_file=file, file_format='list')
    ds.add_points(dict2)
    assert 'x,y' + os.linesep + str(list(dict2.values())) + os.linesep == open(file, 'r').read()
    assert str(list(dict2.values())) + os.linesep == open(file, 'r').readlines()[-1]

    ds.add_points(dict2)
    assert str(list(dict2.values())) + os.linesep == open(file, 'r').readlines()[-1]


def test_array_read_ops():
    Dict = {'x': [1., 4.], 'y': [2., 5], 'z': [3, 6]}
    ds = DataStream(Dict)

    # check by point
    assert np.all(ds[:,0] == [1., 2., 3])
    assert np.all(ds[:,1] == [4., 5., 6])

    # check x
    assert np.all(ds['x'] == ds['x',:])
    assert np.all(ds['x'] == ds[0,:])
    assert np.all(ds['x'] == [1,4])
    assert ds['x',0] == 1 == ds['x'][0]
    assert ds['x',1] == 4 == ds['x'][1]

    # check y
    assert np.all(ds['y'] == ds['y',:])
    assert np.all(ds['y'] == ds[1,:])
    assert np.all(ds['y'] == [2, 5])
    assert ds['y',0] == 2 == ds['y'][0]
    assert ds['y',1] == 5 == ds['y'][1]

    #check z
    assert np.all(ds['z'] == ds['z',:])
    assert np.all(ds['z'] == ds[2,:])
    assert np.all(ds['z'] == [3, 6])
    assert ds['z',0] == 3 == ds['z'][0]
    assert ds['z',1] == 6 == ds['z'][1]

    with pytest.raises(IndexError):
        print(ds[0,'z'])
    with pytest.raises(IndexError):
        print(ds[:,'x'])

    check_datastreams_equal(eval(repr(ds), {}, {'DataStream':DataStream, 'array':np.array}), ds)


def test_array_set_ops():
    Dict = {'x': [1., 4.], 'y': [2., 5], 'z': [3, 6]}
    ds_constructed = DataStream(Dict)

    # [key] =
    ds = DataStream({'x':[0,0],'y':[0,0],'z':[0,0]})
    ds['x'] = Dict['x']
    assert np.all(ds_constructed['x'] == ds['x'])

    ds['y'] = Dict['y']
    assert np.all(ds_constructed['y'] == ds['y'])

    assert np.all(ds_constructed.points == ds.points) == False  # 'is' doesn't want to work here

    ds['z'] = Dict['z']
    assert np.all(ds_constructed['z'] == ds['z'])
    assert np.all(ds_constructed.points == ds.points)

    # [key, :] =
    ds = DataStream({'x':[0,0],'y':[0,0],'z':[0,0]})
    ds['x',:] = Dict['x']
    assert np.all(ds_constructed['x'] == ds['x'])

    ds['y',:] = Dict['y']
    assert np.all(ds_constructed['y'] == ds['y'])

    assert np.all(ds_constructed.points == ds.points) == False  # 'is' doesn't want to work here

    ds['z',:] = Dict['z']
    assert np.all(ds_constructed['z'] == ds['z'])
    assert np.all(ds_constructed.points == ds.points)

    # [key][:] =
    ds = DataStream({'x':[0,0],'y':[0,0],'z':[0,0]})
    ds['x'][:] = Dict['x']
    assert np.all(ds_constructed['x'] == ds['x'])

    ds['y'][:] = Dict['y']
    assert np.all(ds_constructed['y'] == ds['y'])

    assert np.all(ds_constructed.points == ds.points) == False  # 'is' doesn't want to work here

    ds['z'][:] = Dict['z']
    assert np.all(ds_constructed['z'] == ds['z'])
    assert np.all(ds_constructed.points == ds.points)

