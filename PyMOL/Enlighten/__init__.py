# -*- coding: utf-8 -*-
import os
import pymol
import re
import ntpath
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox
import shutil
from os import environ


def __init_plugin__(app=None):
    from pymol.plugins import addmenuitemqt
    addmenuitemqt('Enlighten', run_plugin_gui)


class EnlightenForm(pymol.Qt.QtWidgets.QDialog):

    def __init__(self):
        super(EnlightenForm, self).__init__()
        self.data = {
            'ligand_name': 'NaN',
            'ligand_charge': '0',
            'ph': '7.0',
            'sphere_size': '20',
            'ENLIGHTEN': os.environ.get('ENLIGHTEN'),
            'AMBERHOME': os.environ.get('AMBERHOME'),
            'output_location': '',
            'pdb_folder': ''
        }


def run_plugin_gui():
    dialog = EnlightenForm()
    ui_file = os.path.join(os.path.dirname(__file__), 'ui_form.ui')
    form = pymol.Qt.utils.loadUi(ui_file, dialog)

    if not check_environ_variables():
        environ_popup_window(form)

    form.pymolObjectRadio.toggled.connect(lambda: update_view(form))
    bind_file_dialog(form.pdbFileEdit, form.pdbFileBrowseButton)
    bind_directory_dialog(form.outputEdit, form.outputBrowseButton)

    form.runPrepButton.clicked.connect(lambda: run_prep(form))
    form.websiteButton.clicked.connect(open_enlighten_website)

    form.AdvancedOptionsButton.clicked.connect(
        lambda: advanced_popup_window(form))

    initialize_view(form)

    dialog.show()


def initialize_view(form):
    form.pymolObjectRadio.setChecked(True)
    objects = pymol.cmd.get_names('objects')
    form.pymolObjectCombo.addItems(objects)
    form.pymolObjectCombo.setCurrentIndex(len(objects) - 1)

    form.outputEdit.setText(os.getcwd())
    form.ligandChargeEdit.setValidator(pymol.Qt.QtGui.QIntValidator())
    form.ligandChargeEdit.setText(form.data['ligand_charge'])


def initiate_home_directories(form):
    form.data['ENLIGHTEN'] = os.getenv('ENLIGHTEN',
                              "Please specify ENLIGHTEN home directory")
    print('ENLIGHTEN: ' + form.data['ENLIGHTEN'])

    form.data['AMBERHOME'] = os.getenv('AMBERHOME', "Please specify AMBER home "
                                           "directory")
    print('AMBERHOME: ' + form.data['AMBERHOME'])


def display_home_directories(advanced_form, form):
    advanced_form.enlightenEdit.setText(form.data['ENLIGHTEN'])
    advanced_form.amberEdit.setText(form.data['AMBERHOME'])

def change_sphere_text_edit_value(advanced_form, form, sphere_value):
    advanced_form.SphereSizeValue.setText(str(sphere_value))


def change_slider_position(advanced_form, form, sphere_value):
    advanced_form.SphereSizeSlider.setValue(int(sphere_value))


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

    if validate_main(form):
        return

    #TODO: send charge and name variables from main form to dictionary on
    # clicking run prep

    if form.pdbFileRadio.isChecked():
        pdb_file = form.pdbFileEdit.text()
        pdb_folder = os.path.splitext(os.path.basename(str(pdb_file)))[0]
    else:
        pdb_folder = write_object_to_pdb(form.pymolObjectCombo.currentText())

    output_path = os.path.join(form.outputEdit.text(), pdb_folder)

    if os.path.isdir(output_path):
        delete_pdb_pop_up(form, pdb_folder)

    if delete_pdb_pop_up(form, pdb_folder):
        delete_pdb_folder(output_path)

    else:
        print("exiting prep")
        return

    ligand_name = form.data['ligand_name']
    ligand_charge = form.data['ligand_charge']
    enlighten = form.data['ENLIGHTEN']
    amberhome = form.data['AMBERHOME']
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


def delete_pdb_pop_up(form, pdb_folder):
    delete_pdb_verification = QMessageBox.question(form, 'Warning',
                                        "A folder named {0} already exists. "
                                "Continuing will the delete folder, are you "
                        "sure you want to continue?".format(pdb_folder),
                                        QMessageBox.Yes | QMessageBox.No,
                                        QMessageBox.No)
    if delete_pdb_verification == QMessageBox.Yes:
        return True


def delete_pdb_folder(output_path):
    if os.path.isdir(output_path):
        shutil.rmtree(output_path)
        print('Deleting folder at: ' + output_path)
    else:
        print("Folder no longer exists")


def write_object_to_pdb(object_name):
    filename = os.path.join(os.getcwd(), object_name + '.pdb')
    pymol.cmd.save(filename, '({})'.format(object_name))
    return filename


def open_enlighten_website():
    import webbrowser
    webbrowser.open_new("https://github.com/vanderkamp/enlighten2/")


def validate_main(form):
    return validate_fields(form,
                           [pdb_validator, output_validator, ligand_validator])


def validate_fields(form, validators):
    results = [validator(form) for validator in validators]
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
    if not os.path.isdir(enlighten_path):
        return "Wrong Enlighten path"
    if not os.path.isfile(os.path.join(enlighten_path, 'prep.py')):
        return "prep.py not found in {}".format(enlighten_path)
    return None


def amber_validator(form):
    amber_bin_path = os.path.join(form.amberEdit.text(), 'bin')
    if not os.path.isdir(amber_bin_path):
        return "Wrong AMBER path"
    for filename in ('antechamber', 'pdb4amber', 'reduce'):
        if not os.path.isfile(os.path.join(amber_bin_path, filename)):
            return "{} not found in {}".format(filename, amber_bin_path)
    return None


def output_validator(form):
    output_path = form.outputEdit.text()
    if not os.path.isdir(output_path):
        return "directory {} does not exist".format(output_path)
    return None


def ligand_validator(form):
    if not form.ligandNameEdit.text():
        return "Ligand name not provided"
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


class ExtOptionsDialog(pymol.Qt.QtWidgets.QDialog):

    def __init__(self, main_form):
        super(ExtOptionsDialog, self).__init__()
        self.main_form = main_form

    def closeEvent(self, event):
        self.main_form.AdvancedOptionsButton.setEnabled(True)


def advanced_popup_window(form):
    advanced_dialog = ExtOptionsDialog(form)
    adv_op_ui_file = os.path.join(os.path.dirname(__file__), 'ui_advoptions.ui')
    advanced_form = pymol.Qt.utils.loadUi(adv_op_ui_file, advanced_dialog)

    form.AdvancedOptionsButton.setEnabled(False)

    advanced_form.SphereSizeSlider.sliderMoved.connect(lambda:
        change_sphere_text_edit_value (advanced_form, form,
                                       advanced_form.SphereSizeSlider.value()))

    advanced_form.SphereSizeValue.textChanged.connect(lambda: change_slider_position(
        advanced_form, form, advanced_form.SphereSizeValue.text()))

    bind_directory_dialog(advanced_form.enlightenEdit, advanced_form.enlightenBrowseButton)
    bind_directory_dialog(advanced_form.amberEdit, advanced_form.amberBrowseButton)

    advanced_form.SphereSizeSlider.setMinimum(9)
    advanced_form.SphereSizeSlider.setMaximum(61)
    #set variables only on okay
    advanced_form.SphereSizeSlider.setValue(int(form.data['sphere_size']))
    advanced_form.SphereSizeValue.setText(form.data['sphere_size'])

    advanced_form.phEdit.setText(form.data['ph'])
    ph_validator = pymol.Qt.QtGui.QDoubleValidator(5.0, 14.0, 1, advanced_form.phEdit)
    advanced_form.phEdit.setValidator(ph_validator)

    advanced_form.okButton.clicked.connect(lambda: popup_ok_click(
                                                     form, advanced_form))
    advanced_form.okButton.clicked.connect(lambda:
                                           set_advanced_option_variables(
                                  form, advanced_form.SphereSizeValue.text(),
                                           advanced_form.phEdit.text()))

    display_home_directories(advanced_form, form)
    advanced_dialog.show()
    form.advanced_options_form = advanced_form


def set_advanced_option_variables(form, sphere_value, ph_value):
    form.data['sphere_value'] = str(sphere_value)
    form.data['ph_value'] = str(ph_value)


def check_environ_variables():
    if not (os.environ.get('ENLIGHTEN') and os.environ.get('AMBERHOME')):
        return False
#TODO: need to change to validate the paths, not just check if the environmental
# variables exist


def environ_popup_window(form):
    set_environmental_variables = pymol.Qt.QtWidgets.QDialog()
    set_environ_ui_file = os.path.join(os.path.dirname(__file__),
                                   'ui_set_environ.ui')
    env_window = pymol.Qt.utils.loadUi(set_environ_ui_file,
                                                set_environmental_variables)

    bind_directory_dialog(env_window.enlightenEdit,
                          env_window.enlightenBrowseButton)
    bind_directory_dialog(env_window.amberEdit, env_window.amberBrowseButton)

    env_window.setEnvironLabel.setText("Environmental variables not found: "
                                       "Please set the location of your Amber and "
                                       "Enlighten installation directories")

    display_home_directories(env_window, form)

    env_window.okButton.clicked.connect(lambda: popup_ok_click(
        form, env_window))

    set_environmental_variables.exec_()


def popup_ok_click(form, popup):

    if not validate_paths(popup):
        set_installation_paths(form, popup)
        popup.close()


def set_installation_paths(form, popup):

    form.data["AMBERHOME"] = popup.amberEdit.text()
    form.data["ENLIGHTEN"] = popup.enlightenEdit.text()


def validate_paths(form):
    return validate_fields(form, [amber_validator, enlighten_validator])

