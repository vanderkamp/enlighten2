from PyQt5 import QtWidgets
from .preparation import PreparationTab
from .dynamics import DynamicsTab


class MainWindow(QtWidgets.QTabWidget):

    def __init__(self, window_manager):
        super().__init__()
        self.window_manager = window_manager
        self.setWindowTitle('Enlighten2')
        self.addTab(PreparationTab('prep', window_manager), 'Preparation')
        self.addTab(DynamicsTab('dynam', window_manager), 'Dynamics')
        self.setMinimumSize(self.sizeHint())

    def closeEvent(self, event):
        self.window_manager.close_all()
