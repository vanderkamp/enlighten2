from .windows import ManagedWindow
import os


class DynamicsTab(ManagedWindow):

    def __init__(self, name, window_manager):
        path = os.path.join(os.path.dirname(__file__), 'dynamics.ui')
        super().__init__(name, path, window_manager)
        self.directorySelector.set_directory_mode(True)
        self.directorySelector.lineEdit.textChanged.connect(self.systemList.set_directory)
        self.systemList.selected.connect(self.select_system)
        self.systemList.unselected.connect(self.unselect_system)
        self.unselect_system()

    def select_system(self, item):
        ON_SELECT_CALLBACK_DICT = {'PREP': self.prep_system_selected,
                                   'RELAX': self.relax_system_selected,
                                   'DYNAM': self.dynam_system_selected}
        ON_SELECT_CALLBACK_DICT[item.tag]()

    def unselect_system(self):
        self.runButton.setEnabled(False)
        self.loadButton.setEnabled(False)

    def prep_system_selected(self):
        self.runButton.setEnabled(True)
        self.loadButton.setEnabled(True)
        self.runButton.setText('Run relaxation')
        self.loadButton.setText('Load system')

    def relax_system_selected(self):
        self.runButton.setEnabled(True)
        self.loadButton.setEnabled(True)
        self.runButton.setText('Run dynamics')
        self.loadButton.setText('Load trajectory')

    def dynam_system_selected(self):
        self.runButton.setEnabled(False)
        self.loadButton.setEnabled(True)
        self.loadButton.setText('Load trajectory')

    def bind(self, controller):
        controller.bind_file_selector('working_dir', self.directorySelector)
        self.systemList.selected.connect(
            lambda item: controller.update('dynam.system_name', item.name)
        )
        self.systemList.selected.connect(
            lambda item: controller.update('dynam.tag', item.tag)
        )
        self.runButton.clicked.connect(controller.run_dynam)
        self.loadButton.clicked.connect(controller.load_trajectory)
