from .windows import ManagedWindow
from qt_wrapper import QtGui
from validators import PositiveIntegerValidator
import os


class DynamicsTab(ManagedWindow):

    def __init__(self, name, window_manager, main):
        path = os.path.join(os.path.dirname(__file__), 'dynamics.ui')
        super().__init__(name, path, window_manager)
        self.directorySelector.set_directory_mode(True)
        self.directorySelector.lineEdit.textChanged.connect(self.systemList.set_directory)
        self.systemList.selected.connect(self.select_system)
        self.systemList.unselected.connect(self.unselect_system)
        main.currentChanged.connect(self.systemList.update)
        self.timeEdit.setValidator(QtGui.QIntValidator())
        self.timeEdit.set_validator(PositiveIntegerValidator('Simulation length'))
        self.unselect_system()

    def select_system(self, item):
        ON_SELECT_CALLBACK_DICT = {'PREP': self.prep_system_selected,
                                   'RELAX': self.relax_system_selected,
                                   'DYNAM': self.dynam_system_selected}
        ON_SELECT_CALLBACK_DICT[item.tag]()

    def unselect_system(self):
        self.runButton.setEnabled(False)
        self.loadButton.setEnabled(False)
        self.hideTimeInput()

    def prep_system_selected(self):
        self.runButton.setEnabled(True)
        self.loadButton.setEnabled(True)
        self.hideTimeInput()
        self.runButton.setText('Run relaxation')
        self.loadButton.setText('Load system')

    def relax_system_selected(self):
        self.runButton.setEnabled(True)
        self.loadButton.setEnabled(True)
        self.showTimeInput()
        self.runButton.setText('Run dynamics')
        self.loadButton.setText('Load system')

    def dynam_system_selected(self):
        self.runButton.setEnabled(False)
        self.loadButton.setEnabled(True)
        self.hideTimeInput()
        self.loadButton.setText('Load trajectory')

    def showTimeInput(self):
        self.timeLabel1.show()
        self.timeLabel2.show()
        self.timeEdit.show()

    def hideTimeInput(self):
        self.timeLabel1.hide()
        self.timeLabel2.hide()
        self.timeEdit.hide()

    def bind(self, controller):
        controller.bind_file_selector('working_dir', self.directorySelector)
        controller.bind_lineEdit('dynam.simulation_time', self.timeEdit)
        controller.update('dynam.simulation_time', '50')
        self.systemList.selected.connect(
            lambda item: controller.update('dynam.system_name', item.name)
        )
        self.systemList.selected.connect(
            lambda item: controller.update('dynam.tag', item.tag)
        )
        self.runButton.clicked.connect(self.run_and_update(controller.run_dynam))
        self.loadButton.clicked.connect(controller.load_dynam)
        self.removeButton.clicked.connect(self.run_and_update(controller.remove_system))

    def run_and_update(self, callback):
        def result():
            callback()
            self.systemList.update()
        return result
