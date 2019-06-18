from .windows import ManagedWindow
from PyQt5.QtGui import QIntValidator, QDoubleValidator
import os


class PreparationAdvancedWindow(ManagedWindow):

    def __init__(self, name, window_manager):
        path = os.path.join(os.path.dirname(__file__), 'preparation_advanced.ui')
        super().__init__(name, path, window_manager)
        self.setFixedSize(self.size())
        self.setup_file_selectors()
        self.phEdit.setValidator(QDoubleValidator(0.0, 14.0, 1, self.phEdit))
        self.sphereSizeEdit.setValidator(QIntValidator())

    def setup_file_selectors(self):
        self.enlightenEdit.set_directory_mode(True)
        self.enlightenEdit.set_validator(self.enlighten_validator)
        self.enlightenEdit.set_invalid_tooltip(
            "Not a valid Enlighten path. Check that\n"
            "the path contains prep.py script."
        )
        self.amberEdit.set_directory_mode(True)
        self.amberEdit.set_validator(self.amber_validator)
        self.amberEdit.set_invalid_tooltip(
            "Not a valid Amber path. Check that the path contains 'bin'\n"
            "directory with antechamber, pdb4amber and reduce executables."
        )

    @staticmethod
    def enlighten_validator(path):
        return (os.path.isdir(path) and
                os.path.isfile(os.path.join(path, 'prep.py')))

    @staticmethod
    def amber_validator(path):
        amber_bin_path = os.path.join(path, 'bin')
        if not os.path.isdir(amber_bin_path):
            return False
        for filename in ('antechamber', 'pdb4amber', 'reduce'):
            if not os.path.isfile(os.path.join(amber_bin_path, filename)):
                return False
        return True

    def bind(self, controller):
        controller.bind_lineEdit('enlighten_path', self.enlightenEdit)
        controller.bind_lineEdit('amber_path', self.amberEdit)
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
