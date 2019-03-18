# -*- coding: utf-8 -*-
import os
import pymol
import shutil
import json


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
            'output_location': os.getcwd(),
            'ENLIGHTEN': os.environ.get('ENLIGHTEN', None),
            'AMBERHOME': os.environ.get('AMBERHOME', None),
        }

    def closeEvent(self, event):
        if getattr(self, 'advanced_options_form', None):
            self.advanced_options_form.close()


def run_plugin_gui():
    dialog = EnlightenForm()
    ui_file = os.path.join(os.path.dirname(__file__), 'ui_form.ui')
    form = pymol.Qt.utils.loadUi(ui_file, dialog)

    if check_path_data_set(form):
        environ_popup_window(form)

    if check_path_data_set(form):
        return

    form.pymolObjectRadio.toggled.connect(lambda: update_view(form))
    bind_file_dialog(form.pdbFileEdit, form.pdbFileBrowseButton)
    bind_directory_dialog(form.outputEdit, form.outputBrowseButton)

    form.outputEdit.textChanged.connect(lambda: update_form_data(
        form))
    form.ligandChargeEdit.textChanged.connect(lambda: update_form_data(
        form))
    form.ligandNameEdit.textChanged.connect(lambda: update_form_data(
        form))

    form.runPrepButton.clicked.connect(lambda: run_prep(form))
    form.websiteButton.clicked.connect(open_enlighten_website)
    test_function(form)
    form.AdvancedOptionsButton.clicked.connect(
        lambda: advanced_popup_window(form))

    initialize_view(form)

    dialog.show()


def update_form_data(form):
    form.data['output_location'] = form.outputEdit.text()
    form.data['ligand_name'] = form.ligandNameEdit.text()
    form.data['ligand_charge'] = form.ligandChargeEdit.text()


def check_path_data_set(form):
    return not form.data['ENLIGHTEN'] or not form.data['AMBERHOME']


def initialize_view(form):
    form.pymolObjectRadio.setChecked(True)
    objects = pymol.cmd.get_names('objects')
    form.pymolObjectCombo.addItems(objects)
    form.pymolObjectCombo.setCurrentIndex(len(objects) - 1)

    form.outputEdit.setText(form.data['output_location'])
    form.ligandChargeEdit.setValidator(pymol.Qt.QtGui.QIntValidator())
    form.ligandChargeEdit.setText(form.data['ligand_charge'])


def display_home_directories(advanced_form, form):
    advanced_form.enlightenEdit.setText(form.data['ENLIGHTEN'] or
                                        "Set path to Enlighten")
    advanced_form.amberEdit.setText(form.data['AMBERHOME'] or
                                    "Set path to Amber")


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
    import threads

    if validate_main(form):
        return

    if form.pdbFileRadio.isChecked():
        pdb_file_path = form.pdbFileEdit.text()
        pdb_folder_name = os.path.splitext(os.path.basename(pdb_file_path))[0]
        pdb_directory_path = os.path.dirname(pdb_file_path)
        output_location = form.data['output_location']

        # pdb_file_path already validated to be a file in validate_main
        if pdb_directory_path != output_location:
            shutil.copy(pdb_file_path, output_location)

    else:
        pdb_file_path = write_object_to_pdb(form.data['output_location'],
                                       form.pymolObjectCombo.currentText())
        pdb_folder_name = form.pymolObjectCombo.currentText()
    pdb_file = os.path.basename(pdb_file_path)

    pdb_folder = os.path.join(form.data['output_location'], pdb_folder_name)

    if os.path.isdir(pdb_folder):
        if delete_pdb_pop_up(form, pdb_folder_name):
            delete_pdb_folder(pdb_folder)
        else:
            print("exiting prep")
            return

    ligand_name = form.data['ligand_name']
    ligand_charge = form.data['ligand_charge']
    enlighten = form.data['ENLIGHTEN']
    amberhome = form.data['AMBERHOME']
    os.chdir(form.data['output_location'])
    os.environ.update({'AMBERHOME': amberhome})
    params_filename = "params.json"
    dump_parameters(form.data, params_filename)
    prepThread = threads.SubprocessThread("{}/prep.py {} {} {} {}"
                                          .format(enlighten, pdb_file,
                                                  ligand_name, ligand_charge,
                                                  params_filename))


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


def test_function(form):
    print(form.data)


def dump_parameters(data, filename):
    with open(filename, "w") as f:
        json.dump(get_parameters_dictionary(data), f, indent=4)


def get_parameters_dictionary(data):
    return {
        'antechamber': {
            'ligand': data['ligand_name'],
            'charge': float(data['ligand_charge']),
        },
        'propka': {
            'ph': float(data['ph']),
        },
        'tleap': {
            'solvent_radius': float(data['sphere_size'])
        }
    }


def delete_pdb_pop_up(form, pdb_folder):
    QMessageBox = pymol.Qt.QtWidgets.QMessageBox
    delete_pdb_verification = QMessageBox.question(
        form,
        'Warning',
        "A folder named {0} already exists. "
        "Continuing will the delete folder, are you "
        "sure you want to continue?".format(pdb_folder),
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.No
    )
    return delete_pdb_verification == QMessageBox.Yes



def delete_pdb_folder(output_path):
    if os.path.isdir(output_path):
        shutil.rmtree(output_path)
        print('Deleting folder at: ' + output_path)
    else:
        print("Folder no longer exists")


def write_object_to_pdb(output_location, object_name):
    filename = os.path.join(output_location, object_name + '.pdb')
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
    result = pymol.Qt.QtWidgets.QFileDialog.getOpenFileName()[0]
    if result:
        lineEdit.setText(result)


def assign_directory(lineEdit):
    result = pymol.Qt.QtWidgets.QFileDialog.getExistingDirectory()
    if result:
        lineEdit.setText(result)


class ExtOptionsDialog(pymol.Qt.QtWidgets.QDialog):

    def __init__(self, main_form):
        super(ExtOptionsDialog, self).__init__()
        self.main_form = main_form

    def closeEvent(self, event):
        self.main_form.AdvancedOptionsButton.setEnabled(True)
        self.main_form.advanced_options_form = None


def advanced_popup_window(form):
    advanced_dialog = ExtOptionsDialog(form)
    adv_op_ui_file = os.path.join(os.path.dirname(__file__), 'ui_advoptions.ui')
    advanced_form = pymol.Qt.utils.loadUi(adv_op_ui_file, advanced_dialog)

    form.AdvancedOptionsButton.setEnabled(False)

    def on_slider_moved(value):
        advanced_form.SphereSizeValue.setText(str(value))

    advanced_form.SphereSizeSlider.sliderMoved.connect(on_slider_moved)

    def on_sphere_size_text_changed():
        advanced_form.SphereSizeSlider.setValue(int(
            advanced_form.SphereSizeValue.text()))

    advanced_form.SphereSizeValue.textChanged.connect(on_sphere_size_text_changed)

    bind_directory_dialog(advanced_form.enlightenEdit, advanced_form.enlightenBrowseButton)
    bind_directory_dialog(advanced_form.amberEdit, advanced_form.amberBrowseButton)

    advanced_form.SphereSizeSlider.setMinimum(10)
    advanced_form.SphereSizeSlider.setMaximum(60)
    #set variables only on okay
    advanced_form.SphereSizeSlider.setValue(int(form.data['sphere_size']))
    advanced_form.SphereSizeValue.setText(str(form.data['sphere_size']))

    advanced_form.phEdit.setText(form.data['ph'])
    ph_validator = pymol.Qt.QtGui.QDoubleValidator(5.0, 14.0, 1, advanced_form.phEdit)
    advanced_form.phEdit.setValidator(ph_validator)

    advanced_form.okButton.clicked.connect(lambda: adv_op_popup_ok_click(
                                                     form, advanced_form))

    display_home_directories(advanced_form, form)
    advanced_dialog.show()
    form.advanced_options_form = advanced_form


def set_advanced_option_variables(form, sphere_value, ph_value):
    form.data['sphere_size'] = str(sphere_value)
    form.data['ph'] = str(ph_value)


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

    env_window.okButton.clicked.connect(lambda: environ_popup_ok_click(
        form, env_window))

    set_environmental_variables.exec_()




def environ_popup_ok_click(form, popup):

    if not validate_paths(popup):
        set_installation_paths(form, popup)
        popup.close()


def adv_op_popup_ok_click(form, advanced_form):

    if not validate_paths(advanced_form):
        set_installation_paths(form, advanced_form)
        set_advanced_option_variables(form,
                                      advanced_form.SphereSizeValue.text(),
                                      advanced_form.phEdit.text())
        advanced_form.close()


def set_installation_paths(form, popup):

    form.data["AMBERHOME"] = popup.amberEdit.text()
    form.data["ENLIGHTEN"] = popup.enlightenEdit.text()


def validate_paths(form):
    return validate_fields(form, [amber_validator, enlighten_validator])




