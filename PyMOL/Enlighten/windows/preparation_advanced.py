from .windows import ManagedWindow
from qt_wrapper import QtGui
import os


class PreparationAdvancedWindow(ManagedWindow):

    def __init__(self, name, window_manager):
        path = os.path.join(os.path.dirname(__file__), 'preparation_advanced.ui')
        super().__init__(name, path, window_manager)
        self.setFixedSize(self.size())
        self.phEdit.setValidator(QtGui.QDoubleValidator(0.0, 14.0, 1, self.phEdit))
        self.sphereSizeEdit.setValidator(QtGui.QIntValidator())

    def bind(self, controller):
        controller.bind_atom_selector('prep.advanced.center', self.atomSelector)
        controller.bind_lineEdit('prep.advanced.ph', self.phEdit)
        controller.bind_slider('prep.advanced.sphere_size', self.sphereSizeSlider)
        controller.listen('prep.advanced.sphere_size',
                          lambda value: self.sphereSizeEdit.setText(str(value)))
        self.sphereSizeEdit.textChanged.connect(self.update_slider)
        controller.update('prep.advanced.center', '')
        controller.update('prep.advanced.ph', '7.0')
        controller.update('prep.advanced.sphere_size', 20)

    def update_slider(self, value):
        try:
            self.sphereSizeSlider.setValue(int(value))
        except ValueError:
            pass
