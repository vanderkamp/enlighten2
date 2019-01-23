import os
import pymol


def __init_plugin__(app=None):
    from pymol.plugins import addmenuitemqt
    addmenuitemqt('Enlighten', run_plugin_gui)


def run_plugin_gui():

    dialog = pymol.Qt.QtWidgets.QDialog()
    ui_file = os.path.join(os.path.dirname(__file__), 'ui_form.ui')
    form = pymol.Qt.utils.loadUi(ui_file, dialog)

    form.pymolObjectRadio.toggled.connect(lambda: update_view(form))
    bind_file_dialog(form.pdbFileEdit, form.pdbFileBrowseButton)
    bind_directory_dialog(form.enlightenEdit, form.enlightenBrowseButton)
    bind_directory_dialog(form.amberEdit, form.amberBrowseButton)

    form.runPrepButton.clicked.connect(lambda: run_prep(form))
    form.websiteButton.clicked.connect(open_enlighten_website)

    initialize_view(form)
    dialog.show()


def initialize_view(form):
    form.pymolObjectRadio.setChecked(True)
    objects = pymol.cmd.get_names('objects')
    form.pymolObjectCombo.addItems(objects)
    form.pymolObjectCombo.setCurrentIndex(len(objects)-1)

    enlighten_dir = os.getenv('ENLIGHTEN',
                              "Please specify ENLIGHTEN home directory")
    form.enlightenEdit.setText(enlighten_dir)

    amber_dir = os.getenv('AMBERHOME', "Please specify AMBER home directory")
    form.amberEdit.setText(amber_dir)

    form.outputEdit.setText(os.getcwd())
    form.ligandChargeEdit.setValidator(pymol.Qt.QtGui.QIntValidator())
    form.ligandChargeEdit.setText("0")


def update_view(form):
    PDB_FILE_WIDGETS = ('pdbFileLabel', 'pdbFileEdit', 'pdbFileBrowseButton')
    PYMOL_OBJECT_WIDGETS = ('pymolObjectLabel', 'pymolObjectCombo')
    if form.pdbFileRadio.isChecked():
        show_widgets(form, PDB_FILE_WIDGETS)
        hide_widgets(form, PYMOL_OBJECT_WIDGETS)
    else:
        show_widgets(form, PYMOL_OBJECT_WIDGETS)
        hide_widgets(form, PDB_FILE_WIDGETS)


def run_prep(form):
    import subprocess
    import sys
    import threads

    if validate_fields(form):
        return

    if form.pdbFileRadio.isChecked():
        pdb_file = form.pdbFileEdit.text()
    else:
        pdb_file = write_object_to_pdb(form.pymolObjectCombo.currentText())

    ligand_name = form.ligandNameEdit.text()
    ligand_charge = form.ligandChargeEdit.text()
    enlighten = form.enlightenEdit.text()
    amberhome = form.amberEdit.text()
    os.chdir(form.outputEdit.text())
    os.environ.update({'AMBERHOME': amberhome})
    prepThread = threads.SubprocessThread("{}/prep.py {} {} {}"
                                          .format(enlighten, pdb_file,
                                                  ligand_name, ligand_charge))

    def prep_done():
        form.runPrepButton.setText("Run PREP")
        form.runPrepButton.setEnabled(True)
        if prepThread.error:
            error_message(form,
                          "The following errors were encountered:\n" +
                          prepThread.error)
        else:
            info_message(form, prepThread.output)
    prepThread.finished.connect(prep_done)

    form.runPrepButton.setText("Running...")
    form.runPrepButton.setEnabled(False)
    prepThread.start()


def write_object_to_pdb(object_name):
    filename = os.path.join(os.getcwd(), object_name + '.pdb')
    pymol.cmd.save(filename, '({})'.format(object_name))
    return filename


def open_enlighten_website():
    import webbrowser
    webbrowser.open_new("https://github.com/marcvanderkamp/enlighten/")


def validate_fields(form):
    VALIDATORS = [pdb_validator, enlighten_validator,
                  amber_validator, output_validator]
    results = [validator(form) for validator in VALIDATORS]
    errors = [result for result in results if result is not None]
    if errors:
        error_message(form,
                      "The following errors were encountered:\n"
                      "{}".format("\n".join(errors)))
    return errors


def pdb_validator(form):
    if not form.pdbFileRadio.isChecked():
        return None
    if not os.path.isfile(form.pdbFileEdit.text()):
        return "PDB file not found"
    return None


def enlighten_validator(form):
    enlighten_path = form.enlightenEdit.text()
    if not os.path.isfile(os.path.join(enlighten_path, 'prep.py')):
        return "prep.py not found in {}".format(enlighten_path)
    return None


def amber_validator(form):
    amber_bin_path = os.path.join(form.amberEdit.text(), 'bin')
    for filename in ('antechamber', 'pdb4amber', 'reduce'):
        if not os.path.isfile(os.path.join(amber_bin_path, filename)):
            return "{} not found in {}".format(filename, amber_bin_path)
    return None


def output_validator(form):
    output_path = form.outputEdit.text()
    if not os.path.isdir(output_path):
        return "directory {} does not exist".format(output_path)
    return None


def info_message(form, text):
    pymol.Qt.QtWidgets.QMessageBox.information(form, "Enlighten", text)


def error_message(form, text):
    pymol.Qt.QtWidgets.QMessageBox.critical(form, "Enlighten", text)


def show_widgets(form, widgets):
    for widget in widgets:
        getattr(form, widget).show()


def hide_widgets(form, widgets):
    for widget in widgets:
        getattr(form, widget).hide()


def bind_file_dialog(lineEdit, browseButton):
    browseButton.clicked.connect(lambda: assign_filename(lineEdit))


def bind_directory_dialog(lineEdit, browseButton):
    browseButton.clicked.connect(lambda: assign_directory(lineEdit))


def assign_filename(lineEdit):
    lineEdit.setText(pymol.Qt.QtWidgets.QFileDialog.getOpenFileName()[0])


def assign_directory(lineEdit):
    lineEdit.setText(pymol.Qt.QtWidgets.QFileDialog.getExistingDirectory())
