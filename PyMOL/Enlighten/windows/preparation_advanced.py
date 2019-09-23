from .windows import ManagedWindow
from qt_wrapper import QtGui
import os
from validators import EnlightenValidator, AmberValidator


class PreparationAdvancedWindow(ManagedWindow):

    def __init__(self, name, window_manager):
        path = os.path.join(os.path.dirname(__file__), 'preparation_advanced.ui')
        super().__init__(name, path, window_manager)
        self.setFixedSize(self.size())
        self.setup_file_selectors()
        self.phEdit.setValidator(QtGui.QDoubleValidator(0.0, 14.0, 1, self.phEdit))
        self.sphereSizeEdit.setValidator(QtGui.QIntValidator())

    def setup_file_selectors(self):
        self.enlightenSelector.set_directory_mode(True)
        self.enlightenSelector.lineEdit.set_validator(EnlightenValidator())
        self.amberSelector.set_directory_mode(True)
        self.amberSelector.lineEdit.set_validator(AmberValidator())

    def bind(self, controller):
        controller.bind_file_selector('enlighten_path', self.enlightenSelector)
        controller.bind_file_selector('amber_path', self.amberSelector)
        controller.bind_atom_selector('center', self.atomSelector)
        controller.bind_lineEdit('prep.advanced.ph', self.phEdit)
        controller.bind_slider('prep.advanced.sphere_size', self.sphereSizeSlider)
        controller.listen('prep.advanced.sphere_size',
                          lambda value: self.sphereSizeEdit.setText(str(value)))
        self.sphereSizeEdit.textChanged.connect(self.update_slider)

    def update_slider(self, value):
        try:
            self.sphereSizeSlider.setValue(int(value))
        except ValueError:
            pass
