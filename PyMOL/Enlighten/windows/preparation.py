from .windows import ManagedWindow
import os


class PreparationTab(ManagedWindow):

    def __init__(self, name, window_manager):
        path = os.path.join(os.path.dirname(__file__), 'preparation.ui')
        super().__init__(name, path, window_manager)

    def bind(self, controller):
        prep_advanced = self.window_manager['prep_advanced']
        self.runPrepButton.clicked.connect(prep_advanced.show)
