from .windows import ManagedWindow
import os


class PreparationTab(ManagedWindow):

    def __init__(self, name, window_manager):
        path = os.path.join(os.path.dirname(__file__), 'preparation.ui')
        super().__init__(name, path, window_manager)
        self.pdbFileEdit.set_validator(self.pdb_validator)
        self.outputEdit.set_directory_mode(True)

    @staticmethod
    def pdb_validator(filename):
        ext = os.path.splitext(filename)[-1]
        return os.path.isfile(filename) and ext.lower() == '.pdb'

    def bind(self, controller):
        prep_advanced = self.window_manager['prep_advanced']
        self.advancedOptionsButton.clicked.connect(prep_advanced.show)
