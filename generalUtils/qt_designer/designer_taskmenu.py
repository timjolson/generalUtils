from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QVariant
from PyQt5.QtCore import Qt, pyqtSignal

from PyQt5.QtDesigner import QExtensionFactory, QPyDesignerTaskMenuExtension, \
    QDesignerFormWindowInterface
from PyQt5.QtWidgets import QAction, QDialog, QGridLayout, QDialogButtonBox
from generalUtils.qt_designer.designer_widgets import GeoLocationWidget


# TaskMenuExtension needs more work, does not seem to function in qtdesigner (may work in qtcreator)
class GeoLocationTaskMenuFactory(QExtensionFactory):
    """GeoLocationTaskMenuFactory(QExtensionFactory)

    Provides a task menu that can be used to access an editor dialog.
    """

    def __init__(self, parent=None):

        QExtensionFactory.__init__(self, parent)

    # This standard factory function returns an object to represent a task
    # menu entry.
    def createExtension(self, obj, iid, parent):

        if iid != "com.trolltech.Qt.Designer.TaskMenu":
            return None

        # We pass the instance of the custom widget to the object representing
        # the task menu entry so that the contents of the custom widget can be
        # modified.
        if isinstance(obj, GeoLocationWidget):
            return GeoLocationMenuEntry(obj, parent)

        return None


class GeoLocationMenuEntry(QPyDesignerTaskMenuExtension):
    """GeoLocationMenuEntry(QPyDesignerTaskMenuExtension)

    Provides a task menu entry to enable details of the geographical location
    to be edited in a dialog.
    """

    def __init__(self, widget, parent):
        QPyDesignerTaskMenuExtension.__init__(self, parent)

        self.widget = widget

        # Create the action to be added to the form's existing task menu
        # and connect it to a slot in this class.
        self.editStateAction = QAction(self.tr("Update Location..."), self)
        self.connect(self.editStateAction, pyqtSignal("triggered()"),
                     self.updateLocation)

    def preferredEditAction(self):
        return self.editStateAction

    def taskActions(self):
        return [self.editStateAction]

    # The updateLocation() slot is called when the action that represents our
    # task menu entry is triggered. We open a dialog, passing the custom widget
    # as an argument.
    def updateLocation(self):
        dialog = GeoLocationDialog(self.widget)
        dialog.exec_()


class GeoLocationDialog(QDialog):
    """GeoLocationDialog(QDialog)

    Provides a dialog that is used to edit the contents of the custom widget.
    """

    def __init__(self, widget, parent=None):
        QDialog.__init__(self, parent)

        # We keep a reference to the widget in the form.
        self.widget = widget

        self.previewWidget = GeoLocationWidget()
        self.previewWidget.latitude = widget.latitude
        self.previewWidget.longitude = widget.longitude

        buttonBox = QDialogButtonBox()
        okButton = buttonBox.addButton(buttonBox.Ok)
        cancelButton = buttonBox.addButton(buttonBox.Cancel)

        self.connect(okButton, pyqtSignal("clicked()"),
                     self.updateWidget)
        self.connect(cancelButton, pyqtSignal("clicked()"),
                     self, pyqtSignal("reject()"))

        layout = QGridLayout()
        layout.addWidget(self.previewWidget, 1, 0, 1, 2)
        layout.addWidget(buttonBox, 2, 0, 1, 2)
        self.setLayout(layout)

        self.setWindowTitle(self.tr("Update Location"))

    # When we update the contents of the custom widget, we access its
    # properties via the QDesignerFormWindowInterface API so that Qt Designer
    # can integrate the changes we make into its undo-redo management.
    def updateWidget(self):
        formWindow = QDesignerFormWindowInterface.findFormWindow(self.widget)

        if formWindow:
            formWindow.cursor().setProperty("latitude",
                                            QVariant(self.previewWidget.latitude))
            formWindow.cursor().setProperty("longitude",
                                            QVariant(self.previewWidget.longitude))

        self.accept()
