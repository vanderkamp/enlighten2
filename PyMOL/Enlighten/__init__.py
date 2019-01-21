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


def show_widgets(form, widgets):
    for widget in widgets:
        getattr(form, widget).show()


def hide_widgets(form, widgets):
    for widget in widgets:
        getattr(form, widget).hide()
