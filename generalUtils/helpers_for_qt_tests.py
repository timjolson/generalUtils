from types import FunctionType
from PyQt5 import QtCore

import logging
from copy import copy


def show_mouse_click(widget, event, *args, **kwargs):
    """Uses widget.setText() to show if mouse click was Left or Right Click"""
    if event.button() == QtCore.Qt.LeftButton:
        widget.setText('Left Click')
    elif event.button() == QtCore.Qt.RightButton:
        widget.setText('Right Click')


def lock_unlock_entry_mouse(widget, event):
    """Uses widget.setReadOnly(X) to lock the QLineEdit. X = True for Left, False for Right Click"""
    logging.debug('lock unlock entry')
    if event.button() == QtCore.Qt.LeftButton:
        widget.setReadOnly(True)
    elif event.button() == QtCore.Qt.RightButton:
        widget.setReadOnly(False)
    logging.debug('entry on mouse : ' + str(widget._editBox.isReadOnly()))


def lock_unlock_option_mouse(widget, event):
    """Uses widget.setOptionFixed(X) to lock the QComboBox. X = True for Left, False for Right Click"""
    logging.debug('lock unlock option')
    if event.button() == QtCore.Qt.LeftButton:
        widget.setOptionFixed(True)
    elif event.button() == QtCore.Qt.RightButton:
        widget.setOptionFixed(False)
    logging.debug('option on mouse : ' + str(widget._editBox.isReadOnly()))



__all__ = [k for k, v in locals().items() if isinstance(v, (dict, tuple, list, FunctionType))]
