import logging
import os
import sys
import io
import string
import numpy as np
_ascii_fields = string.ascii_letters[23:26] + string.ascii_letters[0:23]


class DataStream():
    def __init__(self, data=None, record_to_file=None, pause=False, file_format='csv'):
        self.pause = pause
        self._keys = ()
        self._file_inited = False
        self._recorder = lambda *x, **y: None
        self.file_format = file_format
        self.set_record_file(record_to_file, format=file_format)

        if data is None:
            self.points = np.array([], dtype=np.float64)
        else:
            self.points, self._keys = self._process_data(data)

    def add_points(self, *data, **kwargs):
        if not data and not kwargs:
            raise ValueError("No point provided")
        elif not data and kwargs:
            data = kwargs

        if len(data) == 1:
            data = data[0]

        data, names = self._process_data(data)
        self.points = np.concatenate([self.points, data], 1)
        if not self.pause and self._recorder:
            for p in data:
                self._recorder(self._format_point(p))

    def add_point(self, *data, **kwargs):
        if not data and not kwargs:
            raise ValueError("No point provided")
        elif not data and kwargs:
            data = kwargs

        if len(data) == 1:
            data = data[0]

        print('data', data, type(data))
        data, names = self._process_data(data)
        print('data', data, type(data), data.shape, 'names', names, 'points', self.points.shape)
        oldlength = self.points.size
        if oldlength == 0:
            self.points = data.copy()
        else:
            self.points = np.concatenate([self.points, data], 1)
        self._record_point(data)

    def start_recording(self):
        self.pause = False

    def stop_recording(self):
        self.pause = True

    def set_record_file(self, file, format='csv'):
        # TODO: handle header loading

        if file is None:
            return
        if isinstance(file, str):
            file = os.path.abspath(file)
            if not os.path.exists(file):  # file does not exist
                os.makedirs(os.path.dirname(file), exist_ok=True)  # make directory
                open(file, 'w').close()
            self._recorder = lambda msg: open(file, 'a').write(msg + os.linesep)
        elif isinstance(file, io.IOBase):
            self._recorder = lambda msg: file.write(msg + os.linesep)
        elif isinstance(file, logging.Logger):
            self._recorder = lambda msg: file.info(msg)
        elif isinstance(file, logging.Handler):
            def make_record(msg):
                return logging.getLogRecordFactory()(
                    file._name, file._name, file.level, 'DataStream', 0, msg, (), sys.exc_info()
                )
            self._recorder = lambda msg: file.handle(make_record(msg))
        elif callable(file):
            self._recorder = file
        else:
            raise NotImplementedError(f"Don't know how to handle record_to_file={type(file)}")

        self.file_format = format
        self.file = file

    def keys(self):
        for k in self._keys:
            yield k

    def _format_point(self, point):
        print('format', point)
        point = point.flatten()
        if self.file_format == 'csv':
            msg = ','.join(str(v) for v in point)
        elif self.file_format == 'dict':
            msg = str({k: v for k, v in zip(self._keys, point)})
        elif self.file_format == 'list':
            msg = str(list(point))
        else:
            raise NotImplementedError(f"File format '{self.file_format}' not recognized")
        return msg

    def _init_file(self):
        # TODO: handle header loading

        if self.file_format in ['csv', 'list']:
            header = ','.join((k if ',' not in k else f"\"{k}\"") for k in map(str, self._keys))
            self._recorder(header)
        elif self.file_format == 'dict':
            pass
        else:
            raise NotImplementedError(f"Unsupported format: '{self.file_format}'")
        self._file_inited = True

    def _record_point(self, point):
        if not self.pause and self._recorder:
            if not self._file_inited:
                self._init_file()
            self._recorder(self._format_point(point))

    @staticmethod
    def _check_list_tuple(things):
        print('check list tuple', type(things), things)
        if len(things) == 0:
            return

        sample = things[0]
        if isinstance(sample, (int, float, np.number)):
            return
        # if len(sample) > 1: # and hasattr(sample[0], '__iter__'):
        #     raise TypeError('Data arrays must not be multi-dimensional.')

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

    def _process_data(self, data):
        if hasattr(data, '_fields') and isinstance(data, tuple):  # namedtuple
            names = data._fields
            sample = data
        elif isinstance(data, dict):
            names, vv = [], []
            for k, v in data.items():
                names.append(k)
                vv.append(v)
            data = vv
            sample = data[0]
        elif isinstance(data, tuple):
            names = [_ascii_fields[i] for i in range(len(data))]
            sample = data[0]
        elif isinstance(data, (np.ndarray, list)):
            if isinstance(data, list):
                data = np.array(data).T
            try:
                names = data.dtype['names']  # structured array
            except KeyError:
                names = [_ascii_fields[i] for i in range(len(data))]
            sample = data[:, 0]
        elif isinstance(data, DataStream):
            names = list(data.keys())
            data = data.points.copy()
            sample = data[:, 0]
        else:
            raise NotImplementedError((type(data), data))

        if isinstance(sample, np.ndarray):
            self._check_numpy_array(data)
        elif isinstance(sample, (list, tuple)):
            self._check_list_tuple(data)
        elif isinstance(sample, (int, float, np.number)):
            data = np.array(data, dtype=np.float64).T.reshape(len(names), 1)
        else:
            raise NotImplementedError(f"Sample incorrect type {type(sample)}")

        if self._keys:  # we have column names
            sdata = np.zeros_like(data)
            for i, k in enumerate(self._keys):  # sort incoming data columns
                try:
                    sdata[i, :] = data[names.index(k)]
                except ValueError as e:
                    raise ValueError(f"{k} value not provided")
            return sdata, self._keys
        else:
            self._keys = tuple(names)
        return np.asarray(data, dtype=np.float64), tuple(names)

    def __getattr__(self, attr):
        try:
            return self.__dict__[attr]
        except KeyError:
            return getattr(self.points, attr)

    def __getitem__(self, items):
        if isinstance(items, str):
            if items in self._keys:
                items = list(self.keys()).index(items)
        elif isinstance(items, tuple):
            kk = list(self.keys())
            items = tuple((kk.index(i) if isinstance(i, str) else i) for i in items)
        elif isinstance(items, (int, slice)):
            pass
        else:
            raise NotImplementedError((type(items), items))
        return self.points.__getitem__(items)

    def __repr__(self):
        if self.points.size > 0:
            dd = {k: self.points[i] for i, k in enumerate(self._keys)}
        else:
            dd = {}
        return f"{type(self).__name__}({dd})"


__all__ = ['DataStream']
