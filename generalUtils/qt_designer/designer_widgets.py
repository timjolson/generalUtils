from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.Qt import pyqtProperty, QSize, QPainter, QRectF, QPointF, QPen
from PyQt5.QtWidgets import QDoubleSpinBox, QGridLayout, QLabel, QWidget
from math import cos, sin, pi


class GeoLocationWidget(QWidget):
    """GeoLocationWidget(QWidget)
    Modified from https://doc.qt.io/archives/qq/qq26-pyqtdesigner.html
    to work with PyQt5

    Provides a custom geographical location widget.
    """

    # Signals can be created in the class definition in advance, or made on-the-fly (see __init__)
    latitudeChanged = pyqtSignal(float)
    longitudeChanged = pyqtSignal(float)

    def __init__(self, parent=None):

        QWidget.__init__(self, parent)

        latitudeLabel = QLabel(self.tr("Latitude:"))
        self.latitudeSpinBox = QDoubleSpinBox()
        self.latitudeSpinBox.setRange(-90.0, 90.0)
        self.latitudeSpinBox.setDecimals(5)

        longitudeLabel = QLabel(self.tr("Longitude:"))
        self.longitudeSpinBox = QDoubleSpinBox()
        self.longitudeSpinBox.setRange(-180.0, 180.0)
        self.longitudeSpinBox.setDecimals(5)

        # Connect callbacks on spinBoxes to signals to be automatically emitted
        #
        # Signals can be made on-the-fly
        # self.connect(self.latitudeSpinBox, pyqtSignal("valueChanged(double)"),
        #              self, pyqtSignal("latitudeChanged(double)"))

        # Signals can be created in the class definition in advance
        self.latitudeSpinBox.valueChanged.connect(self.latitudeChanged)
        self.longitudeSpinBox.valueChanged.connect(self.longitudeChanged)

        layout = QGridLayout(self)
        layout.addWidget(latitudeLabel, 0, 0)
        layout.addWidget(self.latitudeSpinBox, 0, 1)
        layout.addWidget(longitudeLabel, 1, 0)
        layout.addWidget(self.longitudeSpinBox, 1, 1)

    # The latitude property is implemented with the latitude() and setLatitude()
    # methods, and contains the latitude of the user.
    def latitude(self):
        return self.latitudeSpinBox.value()

    @pyqtSlot(float)
    def setLatitude(self, latitude):
        if latitude != self.latitudeSpinBox.value():
            self.latitudeSpinBox.setValue(latitude)
            # self.emit(pyqtSignal("latitudeChanged(double)"), latitude)
            self.latitudeChanged.emit(latitude)
    latitude = pyqtProperty("double", latitude, setLatitude)

    # The longitude property is implemented with the longitude() and setlongitude()
    # methods, and contains the longitude of the user.
    def longitude(self):
        return self.longitudeSpinBox.value()

    @pyqtSlot(float)
    def setLongitude(self, longitude):
        if longitude != self.longitudeSpinBox.value():
            self.longitudeSpinBox.setValue(longitude)
            # self.emit(pyqtSignal("longitudeChanged(double)"), longitude)
            self.longitudeChanged.emit(longitude)
    longitude = pyqtProperty("double", longitude, setLongitude)


class GlobeWidget(QWidget):

    def __init__(self, parent=None):

        QWidget.__init__(self, parent)

        self._angle = 0
        self._divisions = 24
        self._latitude = 0
        self._longitude = 0
        self._position_shown = False

    def sizeHint(self):
        return QSize(200, 200)

    def paintEvent(self, event):
        cx = self.width() * 0.5
        cy = self.height() * 0.5
        sx = self.width() * 0.4
        sy = self.height() * 0.4
        size = min(sx, sy)

        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(event.rect(), Qt.white)

        step = int(360.0 / self._divisions)

        for latitude in range(-90 + step, 90, step):
            a = cos(latitude / 180.0 * pi)
            y = sin(latitude / 180.0 * pi)
            for angle in range(90 - (self._angle % step), -90, -step):
                x = sin(angle / 180.0 * pi) * a
                z = cos(angle / 180.0 * pi) * a
                scrx = cx + (size * x) * (1 + 0.1 * z)
                scry = cy - (size * y) * (1 + 0.1 * z)
                painter.drawEllipse(scrx - 1, scry - 1, 2, 2)

        rect = QRectF(cx - size - 2, cy - size - 2, size * 2 + 4, size * 2 + 4)

        pen = QPen(Qt.DashLine)
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawEllipse(rect)

        for special_angle in (-180, 0, 180):
            if special_angle - 90 < self._angle < special_angle + 90:
                b = sin((special_angle - self._angle) / 180.0 * pi)
                c = cos((special_angle - self._angle) / 180.0 * pi)

                points = []

                for latitude in range(-90, 91):
                    a = cos(latitude / 180.0 * pi)
                    x = a * b
                    z = a * c
                    y = sin(latitude / 180.0 * pi)
                    scrx = cx + (size * x) * (1 + 0.1 * z)
                    scry = cy - (size * y) * (1 + 0.1 * z)
                    points.append(QPointF(scrx, scry))

                painter.drawPolyline(*points)

        if self._position_shown:
            angle = (self._longitude - self._angle) % 360

            if angle < 90 or angle > 270:
                a = cos(self._latitude / 180.0 * pi)
                y = sin(self._latitude / 180.0 * pi)
                x = sin((self._longitude - self._angle) / 180.0 * pi) * a
                z = cos((self._longitude - self._angle) / 180.0 * pi) * a
                scrx = cx + (size * x) * (1 + 0.1 * z)
                scry = cy - (size * y) * (1 + 0.1 * z)
                painter.setPen(Qt.red)
                painter.setBrush(Qt.red)
                painter.drawEllipse(scrx - 2, scry - 2, 4, 4)

        painter.end()

    def angle(self):
        return self._angle

    @pyqtSlot(int, name='setAngle')
    def setAngle(self, angle):
        self._angle = max(-180, min(angle, 180))
        self.update()
    angle = pyqtProperty("int", angle, setAngle)

    def divisions(self):
        return self._divisions

    @pyqtSlot(int, name='setDivisions')
    def setDivisions(self, divisions):
        if 4 <= divisions <= 360:
            self._divisions = divisions
            self.update()
    divisions = pyqtProperty("int", divisions, setDivisions)

    def latitude(self):
        return self._latitude

    @pyqtSlot(float, name='setLatitude')
    def setLatitude(self, latitude):
        self._latitude = max(-90.0, min(latitude, 90.0))
        if self.positionShown:
            self.update()
    latitude = pyqtProperty("double", latitude, setLatitude)

    def longitude(self):
        return self._longitude

    @pyqtSlot(float, name='setLongitude')
    def setLongitude(self, longitude):
        self._longitude = max(-180.0, min(longitude, 180.0))
        if self.positionShown:
            self.update()
    longitude = pyqtProperty("double", longitude, setLongitude)

    def positionShown(self):
        return self._position_shown

    @pyqtSlot()
    def setPositionShown(self, enabled):
        self._position_shown = enabled
        self.update()
    positionShown = pyqtProperty("bool", positionShown, setPositionShown)

