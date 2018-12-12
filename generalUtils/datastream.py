from .logger_recorder import Recorder, LogAndRecord
from .general_utils import ensure_file

try:
    from pyqtgraph.Qt import QtCore
except ImportError:
    linestyles = {
        'l': 'QtCore.Qt.SolidLine',
        '-': 'QtCore.Qt.DashLine',
        '.': 'QtCore.Qt.DotLine',
        '-.': 'QtCore.Qt.DashDotLine',
        '-..': 'QtCore.Qt.DashDotDotLine',
    }
else:
    linestyles = {
        'l':QtCore.Qt.SolidLine,
        '-':QtCore.Qt.DashLine,
        '.':QtCore.Qt.DotLine,
        '-.':QtCore.Qt.DashDotLine,
        '-..':QtCore.Qt.DashDotDotLine,
    }

colors = {
    'y':'yellow',
    'w':'white',
    'b':'blue',
    'r':'red',
    'g':'green',
    # 'k':'black' # background is black
    }


class DataStream(LogAndRecord):
    '''DataStream collects data points and plotting styles for each curve or channel.
    Written by Tim Olson - tim.lsn@gmail.com
    
    obj = DataStream(curves, record_file, load_data, load_file)

        curves (dict): dictionary of curve names and styles {name:style}
                style = 'cwt' where:
                    c= single letter color, one of:
                            r=red, b=blue, g=green, y=yellow, w=white
                    w= single digit line width
                    t= line style, one of:
                        'l' = solid line (lowercase L)
                        '-' = dashed line
                        '.' = dotted line
                        '-.' = dash-dot line
                        '-..' = dash-dot-dot line
                e.g. {'error':'r2-.','position':'b3l'}
                Note: right-most curves will appear on top of others

        record_file (file path list):
            file to save points into (see Logger example for file path info)
        load_data (dict of lists):
            data to pre-load, format {name:[values],name:[values],...}
        load_file (file path list):
            file to pre-load point from (see Logger example for file path info)

    Note: if a load_file is specified, it's points will load before load_data

    Note: adding points or load_data will add the labels from those respective
        points to the DataStream. If no 'curves' is specified, each curve will
        be assigned a default style.

    #TODO:
    0. Move styles to plotting (don't need graphical info to store data points)
    1. not require width every time
    2. add default curve labels
    '''
    
    def __init__(self, curves=None, load_data=None, load_file=None, **logrecord):
        '''See doc for DataStream'''
        LogAndRecord.__init__(self, **logrecord)

        self.curves = dict() if not curves else curves
        self.points = dict() if not curves else \
            {c:l for c,l in zip(curves.keys(), [list() for k in curves.keys()])}
        self.reload_data = dict() if not curves else \
            {c: l for c, l in zip(curves.keys(), [list() for k in curves.keys()])}

        self.num_colors, self.num_styles = len(colors), len(linestyles)
        self.last_color, self.last_style = self.num_colors-1, self.num_styles-1
        self.colors, self.linestyles = list(colors.keys()), list(linestyles.keys())

        if load_file: self.load_from_file(load_file)
        self.load_file = load_file
        
        if load_data: self.load_from_dict(load_data)
        self.load_data = load_data

    @property
    def _next_color(self):
        '''next color option'''
        self.last_color = np.mod(self.last_color + 1, self.num_colors)
        return self.colors[self.last_color]
    @property
    def _next_style(self):
        '''next line style option'''
        self.last_style = np.mod(self.last_style + 1, self.num_styles)
        return self.linestyles[self.last_style]
    
    def add_point(self, *point):
        '''Add a data point to the DataStream.
        add_point({label:value, label:value, ..., label:value})
        e.g. add_point({'x':1,'y':2,'z':3.8})
        or
        if there are curve labels already
        add_point(n1,n2,...,nN)
        e.g. add_point(0,1,2,3)

        #TODO: add default curve labels
        '''
        if isinstance(point[0], dict):
            for label, value in point[0].items():
                if label not in self.curves.keys():
                    self.curves.update({label:'{}2{}'.format(self._next_color, self._next_style)})
                    self.points.update({label:[value]})
                else:
                    self.points[label].append(value)
            self.record(point[0])
            return point[0]
        elif isinstance(point, tuple):
            tempdict = dict()
            if self.curves:
                for label,value in zip(self.curves.keys(),point):
                    self.points[label].append(value)
                    tempdict.update({label:value})
                self.record(tempdict)
                return tempdict
            #TODO: add default curve labels
            raise Exception('DataStream has no labels, doesn\'t know what to do with provided point')
        raise Exception('DataStream.add_point(point), point is incorrect format')
    
    def _reload_point(self, label, value):
        if label not in self.curves.keys():
            self.curves.update({label:'{}2{}'.format(self._next_color, self._next_style)})
        if label not in self.points.keys():
            self.points.update({label:[]})
        if label not in self.reload_data.keys():
            self.reload_data.update({label:[]})
        self.points[label].append(value)
        self.reload_data[label].append(value)

    def load_from_dict(self, points):
        '''Loads data points from a dict() in format
        {curve_name:[values], curve_name:[values],...}
        '''
        if not self.curves:
            self.curves= {label:'{}2{}'.format(c,s) for label,c,s in zip(points.keys(),self.colors,self.linestyles)}

        self.load_data = points

        for label, values in points.items():
            if label not in self.points.keys():
                self.points.update({label: []})
            # for value in values:
            self.points[label].extend(values)

    def load_from_file(self, load_file):
        '''Loads data points from a file (see Logger for file format).
        load_file contains one point per line, in format:
        curve,value;curve2,value;...
        curve,value;curve2,value;...
        '''
        file = ensure_file(load_file)
        with open(file.fullpath,'r') as f:
            lines = f.readlines()
        for l in lines:
            entries = l.split(';')
            entries.remove('\n')
            for entry in entries:
                p = entry.split(',')
                self._reload_point(p[0], float(p[1]))

    def save_to_file(self, save_file=None):
        '''Saves DataStream points to a file. If a record_file is already in
        place, saves to save_file as a backup (if provided). If there is no
        record_file already, connects save_file as the new record_file, storing
        all existing points and recording all future points. Returns new filename
        if backing-up or added file as record_file, else returns None.'''
        if save_file and not self.recorder:  # add file to record to
            self.recorder = Recorder(save_file)
            self.record = self.recorder.log
            record = self.record  # temporary record function
            _return = save_file
        elif self.recorder and not save_file:  # no new file, recorder exists
            # has been recording
            return None
        elif save_file and self.recorder:  # both exist, save backup
            recorder = Recorder(save_file)
            record = recorder.log  # temporary record function
            _return = save_file
        else:
            raise Exception('Provide file to save to')

        for idx in range(max([len(self.points[k]) for k in self.points.keys()])):
            tempdict = dict()
            for label in self.points.keys():
                tempdict.update({label:self.points[label][idx]})
            record(tempdict)
        return _return


__all__ = ['DataStream', 'linestyles', 'colors']
