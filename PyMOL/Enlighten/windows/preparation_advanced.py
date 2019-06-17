from .windows import ManagedWindow
import os


class PreparationAdvancedWindow(ManagedWindow):

    def __init__(self, name, window_manager):
        path = os.path.join(os.path.dirname(__file__), 'preparation_advanced.ui')
        super().__init__(name, path, window_manager)

    def bind(self, controller):
        pass
