import pyqtgraph as pg
from time import time
import logging
from .datastream import DataStream, linestyles, colors
from .logger_recorder import LogAndRecord


class MyplotWidget(pg.QtGui.QWidget, LogAndRecord):
    """class collects data points and interactively plots them with pyqtgraph.
    Written by Tim Olson - tim.lsn@gmail.com

    obj = MyplotWidget(title, x label, y label, curves, timespan, grid, legend,
            set Y limits, refresh millis, logger, load_file, load_data,
            record_file, datastream, x_axis, display_shift)
        title (string): title for graph
        x and y labels (strings): axes labels
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
                Note: right-most curves will appear on top of others in 'curves'
        timespan (float): duration of data to show (x axis range in seconds)
        grid (bool): whether to show grid on plot
        legend (bool): whether to show legend
        setY (list): manually set y limits ; e.g. [-1,2]
        refresh_ms (float): milliseconds between graph redraw attempts (when interactive)
        logger (picuspy Logger): allows logging mostly for debug purposes
        dstream (DataStream): a DataStream object to store/load/save points and line styles
        x_axis (string): select a curve/channel in the data to serve as x-axis of graph

        #TODO: allow data shifting to accomodate absolute/relative timestamps, maybe other things
        display_shift (float, None, or bool): shifts display of data in x-axis

        load_file, load_data, record_file -- see doc for DataStream, function is identical

        Note:

    #TODO:
    1. not require width every time
    2. allow pause/play
    3. add dials for display ranges
    4. add switching x-axis while running
    5. add display shifting
    """

    def __init__(self, title='DEFAULT TITLE', xlabel='DEFAULT LABEL', ylabel='DEFAULT LABEL',
                 curves=None, timespan=5, setY=None, refresh_ms=1000 / 15, load_file=None,
                 load_data=None, dstream=None, x_axis='x', display_start_time=True,
                 widget_updater=None, logger=None, record_file=None, parent=None):
        """See doc for Myplot"""

        self.get_app()  # create QApplication
        LogAndRecord.__init__(self, logger=logger)  # optional logging or recording
        pg.QtGui.QWidget.__init__(self, parent)  # make widget
        self.setStyleSheet('background-color:black;')  # black background

        self.log(
            'Setup Plot \'{}\' of \'{}\' vs \'{}\''.format(title, ylabel, xlabel),
            logging.INFO
        )

        # integrate a datastream or build one
        if not dstream:
            # make datastream
            self.dstream = DataStream(
                curves=curves, load_data=load_data,
                load_file=load_file, logger=logger, record_file=record_file
            )

            # log the setup
            if load_file: self.log('load_file = {}'.format(load_file), logging.INFO)
            if curves: self.log('curves = {}'.format(curves), logging.INFO)
            if load_data: self.log('data was loaded', logging.INFO)
        else:
            # add a dstream
            assert isinstance(dstream, DataStream), 'dstream must be of type DataStream'
            self.dstream = dstream

        # set options
        self.refresh, self.timespan, self._setY = refresh_ms, timespan, setY
        self._title, self._xlabel, self._ylabel = title, xlabel, ylabel
        self._x_axis, self.display_start_time = x_axis, display_start_time

        # behind the scenes
        self._legend, self._grid, self._pan = True, True, True
        self.inited, self.flag = False, True
        self.checkboxes = dict()

        # store
        self.plots = dict()

        # parent for widget
        self.parent = parent

        # build UI
        self._buildUI()

        # set up updating
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self._update_visual)
        if widget_updater is not None:
            self.timer.timeout.connect(widget_updater)
        self.timer.start(refresh_ms)

    @classmethod
    def get_app(cls):
        """Returns QApplication, makes one if one does not exist"""
        cls.app = pg.QtGui.QApplication.instance()
        if not cls.app:
            import sys
            cls.app = pg.QtGui.QApplication(sys.argv)
        return cls.app

    def show(self, inline=False, *args, **kwargs):
        """Open widget/window"""
        super().show(*args, **kwargs)
        if self.parent is None and inline == False:  # widget is in a window
            MyplotWidget.get_app().exec_()

    def setY(self, a, b):
        """Set Y limits of plot. They are fixed to these values, unless new ones are specified
        or 'setLims' is changed to False.
            setY(-2, 4) == setY(4, -2)"""
        self.setMinY = min(a, b)
        self.setMaxY = max(a, b)
        self.log(
            'setY to {}:{}'.format(self.setMinY, self.setMaxY),
            logging.DEBUG
        )
        self.setLims = True

    @property
    def setLims(self):
        """bool; whether Y limits are fixed or auto-ranged"""
        return self.setLims

    @setLims.setter
    def setLims(self, val):
        assert isinstance(val, bool), 'setLims must be a boolean'
        if val is True:
            self.plt.setYRange(self.setMinY, self.setMaxY)
            self.log(
                'Set Y Range to {}:{}'.format(self.setMinY, self.setMaxY),
                logging.DEBUG
            )
        else:
            self.plt.enableAutoRange('y', True)
            self.log('Auto Y Range Enabled', logging.DEBUG)
        self.flag = True

    def setLabels(self, title, xlab, ylab):
        """Set title, x-label, y-label"""
        self._title = title
        self._xlabel = xlab
        self._ylabel = ylab

    @property
    def title(self):
        """string; window and plot title"""
        return self._title

    @title.setter
    def title(self, title):
        assert type(title) == ''.__class__, 'pass in string'
        self.setWindowTitle(title)
        self.plt.setLabels(top=title)
        self.log('Title changed from \'{}\' to \'{}\''.format(self._title, title), logging.DEBUG)
        self._title = title

    @property
    def xlabel(self):
        """string; x axis label"""
        return self._xlabel

    @xlabel.setter
    def xlabel(self, xlabel):
        assert type(xlabel) == ''.__class__, 'pass in string'
        self.plt.setLabels(bottom=xlabel)
        self.log('X label changed from \'{}\' to \'{}\''.format(self._xlabel, xlabel), logging.DEBUG)
        self._xlabel = xlabel

    @property
    def ylabel(self):
        """string; y axis label"""
        return self._ylabel

    @ylabel.setter
    def ylabel(self, ylabel):
        assert type(ylabel) == ''.__class__, 'pass in string'
        self.plt.setLabels(left=ylabel)
        self.log('Y label changed from \'{}\' to \'{}\''.format(self._ylabel, ylabel), logging.DEBUG)
        self._ylabel = ylabel

    @property
    def grid(self):
        """bool; whether grid is displayed"""
        return self._grid

    @grid.setter
    def grid(self, grid):
        assert type(grid) == True.__class__, 'grid must be bool type'
        self.plt.showGrid(grid, grid, 0.6)
        self.log('Grid changed from \'{}\' to \'{}\''.format(self._grid, grid), logging.DEBUG)
        self._grid = grid

    @property
    def pan(self):
        """bool; whether plot auto-pans to newest data"""
        return self._pan

    @pan.setter
    def pan(self, pan):
        assert type(pan) == True.__class__, 'pan must be bool type'
        self.log('Pan changed from \'{}\' to \'{}\''.format(self._pan, pan), logging.DEBUG)
        self._update_pan()
        self._pan = pan

    @property
    def legend(self):
        """bool; whether legend is displayed"""
        return self._legend

    @legend.setter
    def legend(self, legend):
        assert type(legend) == True.__class__, 'legend must be bool type'
        self.log('Legend changed from \'{}\' to \'{}\''.format(self._legend, legend), logging.DEBUG)
        self._legend = legend
        if legend:
            self._rebuild_legend()
        else:
            self._remove_legend()

    @property
    def widget_updater(self):
        """function; runs at regular intervals to change data"""
        return self._widget_updater

    @widget_updater.setter
    def widget_updater(self, func):
        if func is not None:
            self.log('attached widget updater', logging.DEBUG)
            self.timer.timeout.connect(func)

        self._widget_updater = func

    @property
    def x_axis(self):
        """string; data points' channel to use as x axis"""
        return self._x_axis

    @x_axis.setter
    def x_axis(self, x_axis):
        assert type(x_axis) == ''.__class__, 'X-Axis variable must be a string'
        if len(list(self.dstream.points.values())[0]) > 0:
            assert x_axis in self.dstream.points.keys(), 'X-Axis variable is not present in data'
        self.log('X-Axis changed from \'{}\' to \'{}\''.format(self._x_axis, x_axis), logging.DEBUG)
        self._x_axis = x_axis
        self.flag = True

    @property
    def _next_check_column(self):
        """next line style option"""
        self.last_check_column += 1
        return self.last_check_column

    def _remove_legend(self):
        """Removes legend from plot"""
        try:
            self.legend_obj.scene().removeItem(self.legend_obj)
        except AttributeError:
            pass
        else:
            self.legend_obj = None
        self.log('Removed legend', logging.DEBUG)

    def _rebuild_legend(self):
        """Rebuilds and displays legend to match enabled curves"""
        self.log('Start rebuild legend', logging.DEBUG)
        self._remove_legend()
        if self.plot_list:
            self.legend_obj = self.plt.addLegend()
            for key in self.plot_list:
                self.legend_obj.addItem(self.plots[key], key)
            self.log('Rebuilt legend', logging.DEBUG)
        else:
            self.log('No Legend Entries', logging.DEBUG)

    def add_point(self, *point):
        """Add a data point to the inner DataStream.
        add_point({label:value, label:value, ..., label:value})
            e.g. add_point({'x':1,'y':2,'z':3.8})
        or
        if there are curve labels already
        add_point(n1,n2,...,nN)
            e.g. add_point(0,1,2,3)"""
        # add point to datastream
        newpoint = self.dstream.add_point(*point)

        # add point to plots
        for label in newpoint.keys():
            if label not in self.plots.keys():
                self._curve_to_plot(label)
                box = self._make_check(label, label)
                if label != self.x_axis:
                    self.plot_list.add(label)
                    self._add_check_to_layout(label, box)
                else:
                    self._remove_from_plot(self.x_axis)
        self.flag = True
        self.log('Added point {}'.format(newpoint), logging.DEBUG - 1)

    def _update_pan(self, t=None):
        """Pans the plot to the newest data, showing last 't' range of x-axis data."""
        if t: self.timespan = t

        if len(list(self.dstream.points.values())[0]) > 0:
            start = self._shift(self.dstream.points[self.x_axis][-1]) - self.timespan
            end = self._shift(self.dstream.points[self.x_axis][-1])
            self.plt.setXRange(start, end)
            self.log('X Range set to {}:{}'.format(start, end), logging.DEBUG)
        else:
            self.log('No data points, X Range unchanged', logging.DEBUG)

    def _curve_to_plot(self, label):
        """Creates a plot object from a curve with name 'label', also adds checkbox"""
        opts = self.dstream.curves[label]
        pen = pg.mkPen(color=opts[0], width=int(opts[1]), style=linestyles[opts[2:]])
        self.plots.update({label: self.plt.plot(pen=pen, name=label)})
        self.plots[label].setData(
            self._shift(self.dstream.points[self.x_axis]),
            self.dstream.points[label]
        )
        self.checkboxes.update({label: pg.QtGui.QCheckBox(label)})
        self.checkboxes[label].toggle()
        self.flag = True
        self.log('Made curve \'{}\' ({})'.format(label, opts), logging.DEBUG)

    def _switch(self, key):
        """Switches the bool property named 'key', depending on it's checkbox status"""
        check = self.checkboxes[key].isChecked()
        setattr(self, key, check)
        self.log('Checkbox \'{}\' is \'{}\''.format(key, check), logging.DEBUG)

    def _show_curve(self, key):
        """Displays or hides curve of label 'key' depending on it's checkbox status"""
        if self.checkboxes[key].isChecked():
            self.plt.addItem(self.plots[key])
            self.plot_list.add(key)
            self.log('Showing curve \'{}\''.format(key), logging.DEBUG)
        else:
            self.plt.removeItem(self.plots[key])
            self.plot_list.remove(key)
            self.log('Hiding curve \'{}\''.format(key), logging.DEBUG)

        self.flag = True
        if self.legend: self._rebuild_legend()

    def _make_check(self, key, text, checked=True):
        """Make checkbox for property or curve"""
        self.checkboxes.update({key: pg.QtGui.QCheckBox(text)})
        box = self.checkboxes[key]
        if checked: box.toggle()

        if key in self.dstream.curves.keys():
            box.stateChanged.connect(lambda a, arg=key: self._show_curve(arg))
            box.setStyleSheet('color:{}'.format(colors[self.dstream.curves[key][0]]))
            self.log('Attached curve function to checkbox \'{}\''.format(key), logging.DEBUG)
        else:
            box.stateChanged.connect(lambda a, arg=key: self._switch(arg))
            box.setStyleSheet('color:white')
            self.log('Attached property function to checkbox \'{}\''.format(key), logging.DEBUG)

        self.log('Made checkbox \'{}\''.format(key), logging.DEBUG)
        return box

    def _add_check_to_layout(self, key, box):
        """"Add checkbox 'box' to layout"""
        # widget, row, column, rowspan, col.span, alignment
        self.layout.addWidget(box, 1, self._next_check_column, 1, 1)
        self.log('Added checkbox \'{}\' to layout'.format(key), logging.DEBUG)

    def _remove_check_box(self, key):
        """Remove checkbox from layout"""
        # TODO: get column removed
        self.layout.removeItem(self.checkboxes[key])
        # TODO: shift all boxes right of it to the left
        self.last_check_column -= 1

    def _remove_from_plot(self, key):
        """Remove curve from plot"""
        self.plt.removeItem(self.plots[key])

        try:
            self.plot_list.remove(key)
        except KeyError:
            pass

        self._rebuild_legend()
        self.log('Removed \'{}\' from plot'.format(key), logging.DEBUG)

    def _make_layout(self):
        """Create layout, plot widget"""
        self.layout = pg.QtGui.QGridLayout()
        self.plt = pg.PlotWidget()
        self.layout.addWidget(self.plt, 0, 0, 1, 10)
        self.setLayout(self.layout)
        self.log('Made layout \'{}\''.format(self._title), logging.DEBUG)

    def _buildUI(self):
        """Initialize graphics to display plot"""
        self.log('init_show \'{}\''.format(self._title), logging.DEBUG)
        self._make_layout()
        self.plot_list = set([])
        self.checkboxes = dict()
        self.legend_obj = self.plt.addLegend()
        self.last_check_column = -1
        self.start = time()

        box = self._make_check('grid', 'Grid')
        self._add_check_to_layout('grid', box)
        box = self._make_check('pan', 'Auto-Pan')
        self._add_check_to_layout('pan', box)
        box = self._make_check('legend', 'Legend')
        self._add_check_to_layout('legend', box)

        for c in self.dstream.curves.keys():
            self._curve_to_plot(c)
            self.plot_list.add(c)
            box = self._make_check(c, c)

            if c != self.x_axis:
                self._add_check_to_layout(c, box)

        if self.dstream.curves:
            self._remove_from_plot(self.x_axis)

        if self._setY:
            self.setY(self._setY[0], self._setY[1])
        self.grid = self._grid

        self.plt.setLabels(left=self._ylabel, bottom=self._xlabel, top=self._title)

        self.log(
            'Showing Plot \'{}\' of \'{}\' vs \'{}\''.format(
                self._title, self._ylabel, self._xlabel),
            logging.INFO
        )

        self.last = self.start

    def _shift(self, value):
        """Shift values down by display_start_time"""
        if type(value) == [].__class__:
            _return = []
            for v in value:
                _return.append(self._shift(v))
            return _return
        else:
            return value - \
                   (self.start if self.display_start_time is True else self.display_start_time)

    # TODO: sort data by x-axis when coming from multiple sources?
    def load_from_file(self, load_file):
        """Load data in from a 'record_file'"""
        self.log('Loading file {}'.format(load_file), logging.INFO)
        self.dstream.load_from_file(load_file)

    # TODO: sort data by x-axis when coming from multiple sources?
    def load_from_dict(self, points):
        """Load data in from a dict of lists"""
        self.log('Loading points for {}'.format(points.keys()), logging.INFO)
        self.dstream.load_from_dict(points)

    def save_to_file(self, save_file=None):
        """Save data to a record_file"""
        save = self.dstream.save_to_file(save_file)
        if save:
            self.log('Saved to {}'.format(save), logging.INFO)
        else:
            self.log('Recording already running', logging.INFO)

    def _update_visual(self):
        """Update the display if there is new data"""
        if self.flag:
            try:
                if len(list(self.dstream.points.values())[0]) > 0:
                    X = self._shift(self.dstream.points[self.x_axis])
                    for label in self.plot_list:
                        self.log('update vis {}'.format(label), logging.DEBUG - 1)
                        self.plots[label].setData(X, self.dstream.points[label], clear=True)
                    if self._pan: self._update_pan()
            except IndexError:
                pass
            self.flag = False

    def inline_show(self, *args, **kwargs):
        """Updates the display, returns whether widget is still open/showing"""
        if not self.inited:
            self.show(inline=True, *args, **kwargs)
            self.inited = True

        vis = self.isVisible()

        now = time()
        if now - self.last > self.refresh / 1000:
            self._update_visual()
            self.last = now

        if not vis:
            self.log(
                'Closed Plot \'{}\' of \'{}\' vs \'{}\''.format(
                    self._title, self._ylabel, self._xlabel),
                logging.INFO
            )

        MyplotWidget.app.processEvents()

        return vis


def plot3d(x, y, z, fig=None, zlim=(-10, 10)):
    """
    obj = plot3d(...)
    obj.show()
    """
    import matplotlib.pyplot as plt
    import numpy as np

    if fig is None:
        fig = plt.figure()

    ax = plt.axes(projection='3d')
    x, y = np.meshgrid(x, y)
    ax.plot_surface(x, y, z)
    ax.set_zlim(*zlim)
    return fig


__all__ = ['MyplotWidget', 'plot3d']
