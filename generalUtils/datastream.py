import logging
import os
import sys
import csv
import io
import select
import string
import numpy as np
from collections import namedtuple


class DataStream:
    def __init__(self, record_to_file=None, pause=False):
        self.points = {}
        self.Point = None
        self.file_format = 'csv'
        self._file_inited = False
        self._recorder = lambda *x, **y: None
        self.pause = pause
        self.set_record_file(record_to_file)

    def format_point(self, point):
        if self.file_format == 'csv':
            msg = ','.join(str(v) for v in point)
        elif self.file_format == 'dict':
            msg = str({k: v for k, v in zip(point._fields, point)})
        elif self.file_format == 'list':
            msg = str(list(point))
        else:
            raise NotImplementedError(f"File format '{self.file_format}' not recognized")
        return msg

    def record(self, point):
        if not self.pause and self._recorder:
            self._recorder(self.format_point(point))

    def start_recording(self):
        self.pause = False

    def stop_recording(self):
        self.pause = True

    def set_record_file(self, file):
        if file is None:
            return
        if isinstance(file, str):
            file = os.path.abspath(file)
            if not os.path.exists(file):  # file does not exist
                os.makedirs(os.path.dirname(file), exist_ok=True)  # make directory
                open(file, 'w').close()
            self._recorder = lambda msg: open(file, 'a').write(msg+os.linesep)
        elif isinstance(file, io.IOBase):
            self._recorder = lambda msg: file.write(msg+os.linesep)
        elif isinstance(file, logging.Logger):
            self._recorder = lambda msg: file.info(msg)
        elif isinstance(file, logging.Handler):
            def make_record(msg):
                return \
                    logging.getLogRecordFactory()(
                        file._name, file._name, file.level, 'DataStream', 0, msg, (), sys.exc_info()
                    )
            self._recorder = lambda msg: file.handle(make_record(msg))
        elif hasattr(file, 'send'):
            self._recorder = lambda msg: file.send(msg)
        elif hasattr(file, 'write'):
            self._recorder = lambda msg: file.write(msg)
        else:
            raise NotImplementedError(f"Don't know how to handle record_to_file={type(file)}")

        self.file = file

    @staticmethod
    def _check_list_tuple(things):
        if len(things) == 0:
            return

        sample = things[0]
        if len(sample) > 0 and hasattr(sample[0], '__iter__'):
            raise TypeError('Data arrays must not be multi-dimensional.')

        if not all(len(v) == len(sample) for v in things):
            raise ValueError('Not all arrays are the same length.')

    @staticmethod
    def _check_numpy_array(things):
        if len(things) == 0:
            return

        sample = things[0]
        if len(sample.shape) > 1:
            raise TypeError('Data arrays must not be multi-dimensional.')

        if not all(v.shape == sample.shape for v in things):
            raise ValueError('Not all arrays are the same length.')

    @staticmethod
    def _check_types(things):
        if len(set(map(type, things))) not in (0, 1):
            raise TypeError('Not all collections are of same type.')
        return type(things[0])

    @classmethod
    def from_dict(cls, data, **kwargs):
        ds = cls(**kwargs)

        if not isinstance(data, dict):
            raise TypeError(f"{cls.__name__}.from_dict() only accepts a dict type, not {type(data)}")

        ds.Point = namedtuple('Point', data.keys())
        cls._check_types(list(data.values()))

        sample = list(data.values())[0]
        if isinstance(sample, np.ndarray):
            cls._check_numpy_array(list(data.values()))
            ds.points = {k:np.array(v, dtype=np.float64) for k,v in data.items()}

        elif isinstance(sample, (list, tuple)):
            cls._check_list_tuple(list(data.values()))
            ds.points = {k:np.array(v, dtype=np.float64) for k,v in data.items()}

        elif not hasattr(sample, '__iter__') and np.isreal(sample):
            cls._check_types(list(data.values()))
            ds.points = {k:np.array(v, dtype=np.float64) for k,v in data.items()}

        else:
            raise NotImplementedError(f"Data format not recognized: {type(sample)}")

        return ds

    @classmethod
    def from_tuple(cls, data, **kwargs):
        ds = cls(**kwargs)

        if not isinstance(data, tuple):
            raise TypeError(f"{cls.__name__}.from_tuple() only accepts a tuple/namedtuple type, not {type(data)}")

        cls._check_types(data)

        sample = data[0]
        if hasattr(data, '_fields'):  # namedtuple
            if isinstance(sample, np.ndarray):  # numpy arrays
                cls._check_numpy_array(data)
                ds.Point = namedtuple('Point', data._fields)
                ds.points = {k:np.array(v) for k, v in zip(data._fields, data)}
            elif isinstance(sample, (list, tuple)):  # values are list or something
                cls._check_list_tuple(data)
                ds.Point = namedtuple('Point', data._fields)
                ds.points = {k:np.array(v) for k, v in zip(data._fields, data)}
            else:
                raise NotImplementedError(f"Data format not recognized: {type(sample)}")
        else:  # tuple
            if isinstance(sample, np.ndarray):  # numpy arrays
                cls._check_numpy_array(data)
            elif isinstance(sample, (list, tuple)):  # values are list or something
                cls._check_list_tuple(data)
            else:
                raise NotImplementedError(f"Data format not recognized: {type(sample)}")
            import string
            ds.Point = namedtuple('Point', [string.ascii_letters[i] for i in range(len(data))])
            ds.points = {k: np.array(v) for k, v in zip(ds.Point._fields, data)}

        return ds

    def add_point(self, *point, **kwargs):
        point = self.make_point(*point, **kwargs)

        # if self.Point is not None and isinstance(point, self.Point):
        logging.debug(f"add_point({point}, {kwargs}")
        for k, v in zip(point._fields, point):
            logging.debug(f"k,v {k,v}")
            logging.debug(f"points[{k}] {self.points[k]}")
            self.points[k] = np.concatenate([self.points[k], [v]])
        self.record(point)

    def make_point(self, *point, **kwargs):
        if not point and not kwargs:
            raise ValueError("No point provided")
        elif not point and kwargs:
            point = kwargs

        if len(point) == 1 and (not isinstance(point, self.Point) if self.Point is not None else True):
            point = point[0]

        # object points were not yet configured
        if self.Point is None:
            if isinstance(point, dict):
                self.Point = namedtuple('Point', point.keys())
            elif isinstance(point, tuple):
                if hasattr(point, '_fields'):  # namedtuple
                    self.Point = namedtuple('Point', point._fields)
                else:  # tuple
                    self.Point = namedtuple('Point', [string.ascii_letters[i] for i in range(len(point))])
            elif isinstance(point, np.ndarray):
                self.Point = namedtuple('Point', [string.ascii_letters[i] for i in range(point.shape[0])])
            else:
                raise NotImplementedError(f"Data format not recognized: {type(point)}")
            self.points = {k:np.array([]) for k in self.Point._fields}
            if self._file_inited is False and self.file_format == 'csv':
                self._recorder(','.join(self.Point._fields))

        # handle point as tuple, named tuple, kwargs, dict
        if isinstance(point, dict):
            point = self.Point(**point)
        elif isinstance(point, tuple):
            if hasattr(point, '_fields'):  # namedtuple
                point = self.Point(**dict(zip(point._fields, point)))
            else:  # tuple
                point = self.Point._make(point)
        elif isinstance(point, np.ndarray):
            point = self.Point._make(*np.rollaxis(point, 1))
        else:
            raise NotImplementedError(f"Data format not recognized: {type(point)}")

        return point


__all__ = ['DataStream']
