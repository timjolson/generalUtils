import logging
import os
import sys
import io
import string
import numpy as np
_ascii_fields = string.ascii_letters[23:26] + string.ascii_letters[0:23]


class DataStream():
    def __init__(self, data=None, record_to_file=None, pause=None, file_format='csv'):
        self._keys = ()
        self._file_inited = False
        self._recorder = lambda *x, **y: None
        self.file_format = file_format
        self.pause = pause if (pause is not None) else (record_to_file is None)
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
        elif len(data) == 1:
            data = data[0]

        data, names = self._process_data(data)
        oldlength = self.points.size
        if oldlength == 0:
            self.points = data.copy()
        else:
            self.points = np.concatenate([self.points, data], 1)
        if not self.pause and self._recorder:
            if not self._file_inited:
                self._init_file()
            for p in data.T:
                self._recorder(self._format_point(p))

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

    def _process_data(self, data):
        names = []
        dt = data_type(data)
        if dt == 'empty':
            data = np.array([])
        elif dt == 'listOfLists':
            sample = data[0]
            if hasattr(data, '_fields'):  # namedtuple
                names = data._fields
            elif hasattr(sample, '_fields'):  # namedtuple
                names = sample._fields
            else:
                names = self._keys or [_ascii_fields[i] for i in range(len(data))]
        elif dt == 'listOfDicts':
            sample = data[0]
            names = list(sample.keys())
            vv = []
            for k in sample.keys():  # curve names
                pp = []  # data for curve
                for p in data:  # each data point
                    pp.append(p[k])  # coordinate
                vv.append(pp)  # data for curve
            data = vv
        elif dt == 'listOfValues':
            if hasattr(data, '_fields'):  # namedtuple
                names = data._fields
            else:
                names = self._keys or [_ascii_fields[i] for i in range(len(data))]
            data = [[d] for d in data]
        elif dt == 'dictOfLists':
            names, data = list(data.keys()), list(data.values())
        elif dt == 'dictOfValues':
            names, data = list(data.keys()), [[d] for d in data.values()]
        elif dt == 'recarray':
            names = data.dtype['names']
        elif dt == 'ndarray':
            names = self._keys or [_ascii_fields[i] for i in range(len(data))]
        elif dt == 'DataStream':
            names = tuple(data._keys)
            data = data.points.copy()
        else:
            raise NotImplementedError(f"Cannot handle '{dt}' {data}")

        if self._keys and len(self._keys) != len(data): raise ValueError(
            f"Improper data count ({len(data)}) provided, need ({len(self._keys)})")

        data = np.array(data, dtype=np.float64)

        if self._keys:  # we have column names
            sdata = np.ones_like(data)*np.nan  # sorted data

            for i, k in enumerate(self._keys):  # sort incoming data columns
                sdata[i, :] = data[names.index(k)][:]
            return sdata, self._keys
        else:  # set data column names
            self._keys = tuple(names)
            return data.copy(), tuple(names)

    def __getattr__(self, attr):
        try:
            return self.__dict__[attr]
        except KeyError:
            return getattr(self.points, attr)

    def __getitem__(self, items):
        if isinstance(items, str):
            if items in self._keys:
                items = self._keys.index(items)
            else:
                # force KeyError
                a = dict()[items]
        elif isinstance(items, tuple):
            if isinstance(items[0], str):
                # handle string indexing -> column name
                if len(items) > 1:
                    items = self._keys.index(items[0]), *items[1:]
                else:
                    items = self._keys.index(items[0]),
        return self.points.__getitem__(items)

    def __setitem__(self, key, value):
        if isinstance(key, str):
            if key in self._keys:
                key = self._keys.index(key)
            else:
                # force KeyError
                a = dict()[key]
        elif isinstance(key, tuple):
            if isinstance(key[0], str):
                # handle string indexing -> column name
                if len(key) > 1:
                    key = self._keys.index(key[0]), *key[1:]
                else:
                    key = self._keys.index(key[0]),
        return self.points.__setitem__(key, value)

    def __len__(self):
        return self.points.__len__()

    def __repr__(self):
        if self.points.size > 0:
            dd = {k: self.points[i] for i, k in enumerate(self._keys)}
        else:
            dd = {k:[] for i, k in enumerate(self._keys)}
        return f"{type(self).__name__}({dd})"


def data_type(obj):
    # inspired by pyqtgraph.graphicsitems.PlotDataItem
    if hasattr(obj, '__len__') and len(obj) == 0:
        return 'empty'
    if isinstance(obj, DataStream):
        return 'DataStream'
    if isinstance(obj, dict):
        first = obj[list(obj.keys())[0]]
        if is_sequence(first):
            return 'dictOfLists'
        else:
            return 'dictOfValues'
    elif is_sequence(obj):
        first = obj[0]

        if (hasattr(obj, 'implements') and obj.implements('MetaArray')):
            return 'MetaArray'
        elif isinstance(obj, np.ndarray):
            if obj.ndim == 1:
                if obj.dtype.names is None:
                    return 'listOfValues'
                else:
                    return 'recarray'
            # elif obj.ndim == 2 and obj.dtype.names is None and obj.shape[1] == 2:
            #     return 'Nx2array'
            elif obj.ndim == 2:
                return 'ndarray'
            else:
                raise Exception('array shape must be (N,) or (N,2); got %s instead' % str(obj.shape))
        elif isinstance(first, dict):
            return 'listOfDicts'
        elif is_sequence(first):
            return 'listOfLists'
        else:
            return 'listOfValues'


def is_sequence(obj):
    # inspired by pyqtgraph.graphicsitems.PlotDataItem
    return hasattr(obj, '__iter__') or isinstance(obj, np.ndarray) or (
                hasattr(obj, 'implements') and obj.implements('MetaArray'))


__all__ = ['DataStream']
