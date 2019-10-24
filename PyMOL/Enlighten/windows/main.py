from qt_wrapper import QtWidgets
from .preparation import PreparationTab
from .preparation_advanced import PreparationAdvancedWindow
from .dynamics import DynamicsTab


class MainWindow(QtWidgets.QTabWidget):

    def __init__(self, window_manager):
        super().__init__()
        self.window_manager = window_manager
        self.setWindowTitle('Enlighten2')
        self.addTab(PreparationTab('prep', window_manager), 'Preparation')
        self.addTab(DynamicsTab('dynam', window_manager, self), 'Dynamics')
        PreparationAdvancedWindow('prep_advanced', window_manager)
        self.setFixedSize(self.sizeHint())

    def closeEvent(self, event):
        self.window_manager.close_all()
