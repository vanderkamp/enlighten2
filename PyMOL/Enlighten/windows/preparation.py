from .windows import ManagedWindow
from PyQt5.QtGui import QIntValidator
import os
from validators import NotEmptyValidator, IntegerValidator, PdbValidator


# temporary mock of pymol
class pymol:
    class cmd:
        @staticmethod
        def get_names(tmp):
            return ['a', 'b', 'c']


class PreparationTab(ManagedWindow):

    PDB_FILE_WIDGETS = ('pdbFileLabel', 'pdbFileEdit')
    PYMOL_OBJECT_WIDGETS = ('pymolObjectLabel', 'pymolObjectCombo')

    def __init__(self, name, window_manager):
        path = os.path.join(os.path.dirname(__file__), 'preparation.ui')
        super().__init__(name, path, window_manager)
        self.setup_file_selectors()
        self.setup_radio_buttons()
        self.setup_objects_list()
        self.ligandChargeEdit.setValidator(QIntValidator())
        self.ligandChargeEdit.set_validator(IntegerValidator())
        self.ligandNameEdit.set_validator(NotEmptyValidator())

    def setup_file_selectors(self):
        self.pdbFileEdit.set_validator(PdbValidator())
        self.outputEdit.set_directory_mode(True)

    def setup_radio_buttons(self):
        self.pdbFileRadio.toggled.connect(self.on_radio_changed)
        self.pdbFileRadio.setChecked(True)

    def setup_objects_list(self):
        objects = pymol.cmd.get_names('objects')
        self.pymolObjectCombo.addItems(objects)
        self.pymolObjectCombo.setCurrentIndex(len(objects) - 1)

    def on_radio_changed(self, value):
        self.toggle_group(self.PDB_FILE_WIDGETS, value)
        self.toggle_group(self.PYMOL_OBJECT_WIDGETS, not value)

    def bind(self, controller):
        controller.bind_radio_button('prep.use_pdb', self.pdbFileRadio)
        controller.bind_radio_button('prep.use_object', self.pymolObjectRadio)

        controller.bind_combo_box('prep.object', self.pymolObjectCombo)
        controller.update('prep.object', self.pymolObjectCombo.currentText())

        controller.bind_lineEdit('prep.pdb', self.pdbFileEdit)
        controller.bind_lineEdit('prep.output_location', self.outputEdit)

        controller.bind_lineEdit('prep.ligand_name', self.ligandNameEdit)
        controller.bind_lineEdit('prep.ligand_charge', self.ligandChargeEdit)
        controller.bind_checkBox('prep.use_struct', self.structCheckBox)

        prep_advanced = self.window_manager['prep_advanced']
        self.advancedOptionsButton.clicked.connect(prep_advanced.show)
        self.websiteButton.clicked.connect(controller.open_enlighten_website)
        self.runPrepButton.clicked.connect(controller.run_prep)
