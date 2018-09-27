from types import FunctionType

import logging
from copy import copy


def show(vars):
    """Help function to finish off tests, pass 'locals()' """
    qtbot, widget = vars['qtbot'], vars['widget']
    widget.show()
    qtbot.addWidget(widget)
    qtbot.waitExposed(widget)


def check_error_typed(widget, *args, **kwargs):
    """Returns 'ERROR' if widget.text() == 'error', False otherwise"""
    logging.debug('check_error_typed')
    if widget.text() == 'error':
        return 'ERROR'
    return False


def change_title_on_typing(widget, *args, **kwargs):
    """Sets widget.window().setWindowTitle() to change window title to widget.text()"""
    logging.debug('change text to: ' + widget.text())
    widget.window().setWindowTitle(widget.text())


def change_label_on_typing(widget, *args, **kwargs):
    """Uses widget.setLabel() to change the QLabel to widget.text()"""
    logging.debug('change label to: ' + widget.text())
    widget.setLabel(widget.text())


def change_color_on_option(widget, *args, **kwargs):
    """Uses widget.setColors() to change QLineEdit colors to (widget.getSelected(), 'black')"""
    logging.debug('change_color')
    widget.setColors((widget.getSelected(), 'black'))


def set_title_on_error(widget, *args, **kwargs):
    """Set window title to 'ERROR'"""
    widget.window().setWindowTitle('ERROR')


def do_whats_typed(widget, *args, **kwargs):
    """Performs an action on widget, depending on widget.text().
    'error': widget.setError(True)
    'fixed': widget.setReadOnly(True)
    'disabled': widget.setEnabled(False)
    'close': widget.window().close()
    'auto': widget.setAutoColors()
    'color': widget.setColors(('pink', 'black'))

    Otherwise:
        Provide a color name string (e.g. 'red' OR 'blue')
            widget.setColors((widget.text(), 'black'))
        No action specified for widget.text()
            pass
    """
    logging.debug('do_whats_typed')
    do = {
        'error': (lambda x: widget.setError(True)),
        'fixed': (lambda x: widget.setReadOnly(True)),
        'disabled': (lambda x: widget.setEnabled(False)),
        'close': (lambda x: widget.window().close()),
        'auto': (lambda x: widget.setAutoColors()),
        'color': (lambda x: widget.setColors(('pink', 'black')))
    }
    if widget.text() in do.keys():
        do[widget.text()](widget)
    elif not widget.text() in do.keys() and widget.text().upper() in [i for c in colorList for i in c[0]]:
        widget.setColors((widget.text(), 'black'))
    else:
        pass

# sample expressions to test
# ( expr, is_safe, causes error in sympy widgets, is valid identifier(variable name) )
expr_safe_check = [
    ('.a ', False, True, False),
    ('abc', True, False, True),
    ('1.1)', True, True, False),
    ('a)', True, True, False),
    ('1234a.', False, True, False),
    ('12a.a', False, True, False),
    ('1.a ', False, True, False),
    ('a.1 ', False, True, False),
    ('12a12.', False, True, False),
    ('2+4.1', True, False, False),
    ('a.a ', False, True, False),
    ('12a12.12a', False, True, False),
    ('.1 ', True, False, False),
    ('a.a', False, True, False),
    ('.a12', False, True, False),
    ('12a12.12', False, True, False),
    ('1212.a', False, True, False),
    ('ab.ab ', False, True, False),
    ('1212.12a', False, True, False),
    ('.ab ', False, True, False),
    ('a', True, False, True),
    ('.12a', False, True, False),
    ('1.ab ', False, True, False),
    ('error', True, False, True),
    ('ab.1 ', False, True, False),
    ('(a', True, True, False),
    ('1.1 ', True, False, False),
    ('a. ', False, True, False),
    ('12.12a', False, True, False),
    ('1. ', True, False, False),
    ('', True, False, False),
    ('ab. ', False, True, False),
    ('text', True, False, True),
    ('text_2', True, False, True),
    ('text2', True, False, True),
    ('text2a', True, False, True),
    ('text2.', False, True, False),
]


try:
    from PyQt5 import QtCore
except ImportError:
    pass
else:
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


    try:
        from entryWidget import EntryWidget
        from generalUtils import colorList
    except ImportError:
        pass
    else:
        test_strings = ['str0', 'str1', 'str2', ['not a string']]
        test_options_good = ['opt1', 'opt2', 'opt3']
        test_options_bad = ['opt1', ['not a string']]
        test_options_colors = ['red', 'blue', 'green']
        test_color_tuple = copy(EntryWidget.defaultColors['error'])
        test_color_tuple_good = ('blue', 'white')
        test_color_tuple_bad = ('blue', ['not a string'])
        test_color_dict = copy(EntryWidget.defaultColors)
        test_color_dict_good = copy(EntryWidget.defaultColors)
        test_color_dict_good.update({'default': (test_color_tuple_good)})
        test_color_dict_bad = copy(EntryWidget.defaultColors)
        test_color_dict_bad.update({'default': (test_color_tuple_bad)})


__all__ = [k for k, v in locals().items() if isinstance(v, (dict, tuple, list, FunctionType))]
