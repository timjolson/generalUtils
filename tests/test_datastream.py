import pytest
import os
import logging
from collections import namedtuple
import numpy as np

from generalUtils.datastream import DataStream

dict1 = {'a': [], 'b': []}
dict2 = {'a': 1, 'b': 1}
dict3 = {'a': [2, 3], 'b': [2, 3]}

point_test = namedtuple('point_test', 'a, b')
ntup1 = point_test([], [])
ntup2 = point_test([1], [1])
ntup3 = point_test([2, 3], [2, 3])

tup1 = ([], [])
tup2 = ([1], [1])
tup3 = ([2, 3], [2, 3])

np1 = (np.array([]), np.array([]))
np2 = (np.array([1]), np.array([1]))
np3 = (np.array([2, 3]), np.array([2, 3]))

set_to_test = [(dict1, ntup1, tup1, np1),
               (dict2, ntup2, tup2, np2),
               (dict3, ntup3, tup3, np3)]

logging.basicConfig(filename='logs/test_datastream.log', filemode='w', level=logging.DEBUG)



def addpoints(ds):
    ds.add_point({'a': 0, 'b': 0, 'c': 0})
    ds.add_point(1, None, 1)
    ds.add_point(a=2, b=1, c=None)
    ds.add_point(ds.Point(3,2,2))


def check_post_add_points(ds):
    assert np.all(np.equal(ds.points['a'], [0, 1, 2, 3]))
    assert np.all(np.equal(ds.points['b'], [0, None, 1, 2]))
    assert np.all(np.equal(ds.points['c'], [0, 1, None, 2]))


def check_datastreams_equal(one, two):
    logging.debug('check_datastreams_equal')
    logging.debug(f"Vars: {vars(one), vars(two)}")
    logging.debug(f"points {one.points, two.points}")

    for key in one.points.keys():
        logging.debug(f"checking '{key}'")
        logging.debug(f"{one.points[key], two.points[key]}")
        assert np.all(np.equal(one.points[key], two.points[key]))
    logging.debug(f"Point: {one.Point, two.Point}")
    assert one.Point._fields == two.Point._fields
    return True


def test_constructors():
    logging.debug('---------------Begin test_constructors()')
    ds = DataStream()

    for d, nt, t, nmpy in set_to_test:
        logging.debug((d, nt, t, nmpy))

        check_datastreams_equal(DataStream.from_dict(d), DataStream.from_tuple(nt))
        check_datastreams_equal(DataStream.from_tuple(t), DataStream.from_tuple(nmpy))
        check_datastreams_equal(DataStream.from_tuple(nt), DataStream.from_tuple(t))


def test_constructors_error():
    logging.debug('---------------Begin test_constructors_error()')
    with pytest.raises(TypeError):
        try:
            DataStream.from_dict(ntup3)
        except Exception as e:
            logging.error(e)
            raise
    with pytest.raises(TypeError):
        try:
            DataStream.from_dict(tup3)
        except Exception as e:
            logging.error(e)
            raise
    with pytest.raises(TypeError):
        try:
            DataStream.from_dict(np3)
        except Exception as e:
            logging.error(e)
            raise

    with pytest.raises(TypeError):
        try:
            DataStream.from_tuple(dict3)
        except Exception as e:
            logging.error(e)
            raise


def test_add_point():
    logging.debug('---------------Begin test_add_point()')
    ds = DataStream()

    addpoints(ds)
    check_post_add_points(ds)


def test_add_point_error():
    logging.debug('---------------Begin test_add_point_error()')
    ds = DataStream()
    addpoints(ds)

    with pytest.raises(TypeError):
        try:
            ds.add_point((0,1))
        except Exception as e:
            logging.debug(e)
            raise
    with pytest.raises(TypeError):
        try:
            ds.add_point(0, 1)
        except Exception as e:
            logging.debug(e)
            raise
    with pytest.raises(TypeError):
        try:
            ds.add_point(a=0, b=1)
        except Exception as e:
            logging.debug(e)
            raise
    with pytest.raises(TypeError):
        try:
            ds.add_point({'b':99, 'c':10})
        except Exception as e:
            logging.debug(e)
            raise
    with pytest.raises(TypeError):
        try:
            ds.add_point(ds.Point(a=0, b=1))
        except Exception as e:
            logging.debug(e)
            raise
    with pytest.raises(TypeError):
        try:
            ds.add_point(ds.Point(b=10, c=99))
        except Exception as e:
            logging.debug(e)
            raise


def test_record_file():
    logging.debug('---------------Begin test_record_file()')

    file = './logs/datastream_test_record_file.log'
    try:
        os.remove(file)
    except:
        pass

    ds = DataStream(record_to_file=file)

    ds.add_point(dict2)
    assert open(file, 'r').read() == (os.linesep).join(['a,b', '1,1'])+os.linesep

    ds.add_point(dict2)
    assert open(file, 'r').read() == (os.linesep).join(['a,b', '1,1', '1,1'])+os.linesep

    #TODO : handle header writing/loading
