from .windows import ManagedWindow
from qt_wrapper import QtGui, WITH_PYMOL
import os
from validators import NotEmptyValidator, IntegerValidator, PdbValidator
from widgets.form import Form


class PreparationTab(ManagedWindow):

    PDB_FILE_WIDGETS = ('pdbFileLabel', 'pdbFileSelector')
    PYMOL_OBJECT_WIDGETS = ('pymolObjectLabel', 'pymolObjectCombo')

    def __init__(self, name, window_manager):
        path = os.path.join(os.path.dirname(__file__), 'preparation.ui')
        super().__init__(name, path, window_manager)
        self.setup_file_selectors()
        self.setup_radio_buttons()
        self.setup_objects_list()
        self.ligandChargeEdit.setValidator(QtGui.QIntValidator())
        self.ligandChargeEdit.set_validator(IntegerValidator('Ligand charge'))
        self.ligandNameEdit.set_validator(NotEmptyValidator('Ligand name'))

    def setup_file_selectors(self):
        self.pdbFileSelector.lineEdit.set_validator(PdbValidator())
        self.outputSelector.set_directory_mode(True)

    def setup_radio_buttons(self):
        if WITH_PYMOL:
            self.pdbFileRadio.setChecked(False)
            self.pymolObjectRadio.setChecked(True)
            self.on_radio_changed(False)
        else:
            self.pdbFileRadio.setChecked(True)
            self.pymolObjectRadio.setChecked(False)
            self.on_radio_changed(True)
        self.pdbFileRadio.toggled.connect(self.on_radio_changed)

    def setup_objects_list(self):
        if WITH_PYMOL:
            import pymol
            objects = pymol.cmd.get_names('objects')
            self.pymolObjectCombo.addItems(objects)
            self.pymolObjectCombo.setCurrentIndex(len(objects) - 1)
        else:
            self.pymolObjectRadio.setEnabled(False)

    def on_radio_changed(self, value):
        self.toggle_group(self.PDB_FILE_WIDGETS, value)
        self.toggle_group(self.PYMOL_OBJECT_WIDGETS, not value)

    def bind(self, controller):
        controller.bind_radio_button('prep.use_pdb', self.pdbFileRadio)
        controller.bind_radio_button('prep.use_object', self.pymolObjectRadio)

        controller.bind_combo_box('prep.object', self.pymolObjectCombo)
        controller.update('prep.object', self.pymolObjectCombo.currentText())

        controller.bind_file_selector('prep.pdb', self.pdbFileSelector)
        controller.bind_file_selector('prep.output_location', self.outputSelector)

        controller.bind_lineEdit('prep.ligand_name', self.ligandNameEdit)
        controller.bind_lineEdit('prep.ligand_charge', self.ligandChargeEdit)
        controller.bind_checkBox('prep.use_struct', self.structCheckBox)

        prep_advanced = self.window_manager['prep_advanced']
        self.advancedOptionsButton.clicked.connect(prep_advanced.show)
        self.websiteButton.clicked.connect(controller.open_enlighten_website)

        # TODO: uncomment fields in production
        object_form_widgets = [
            self.outputSelector.lineEdit,
            self.ligandNameEdit, self.ligandChargeEdit,
            # prep_advanced.enlightenSelector.lineEdit, prep_advanced.amberSelector.lineEdit,
        ]
        object_form = Form(fields=object_form_widgets,
                           button=self.runPrepButton,
                           submit_callback=controller.run_prep)
        object_form.set_active(False)
        controller.listen('prep.use_object', object_form.set_active)

        pdb_form_widgets = [self.pdbFileSelector.lineEdit, ] + object_form_widgets
        pdb_form = Form(fields=pdb_form_widgets,
                        button=self.runPrepButton,
                        submit_callback=controller.run_prep)
        controller.listen('prep.use_pdb', pdb_form.set_active)



