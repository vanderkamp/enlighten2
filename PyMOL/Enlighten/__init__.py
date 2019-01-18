def __init_plugin__(app=None):
    from pymol.plugins import addmenuitemqt
    addmenuitemqt('Enlighten', run_plugin_gui)


def run_plugin_gui():
    import os
    from pymol.Qt import QtWidgets
    from pymol.Qt.utils import loadUi

    dialog = QtWidgets.QDialog()
    ui_file = os.path.join(os.path.dirname(__file__), 'ui_form.ui')
    form = loadUi(ui_file, dialog)

    form.pymolObjectRadio.toggled.connect(lambda: updateView(form))
    form.pymolObjectRadio.setChecked(True)
    dialog.show()


def updateView(form):
    PDB_FILE_WIDGETS = ('pdbFileLabel', 'pdbFileEdit', 'pdbFileBrowseButton')
    PYMOL_OBJECT_WIDGETS = ('pymolObjectLabel', 'pymolObjectCombo')
    if form.pdbFileRadio.isChecked():
        showWidgets(form, PDB_FILE_WIDGETS)
        hideWidgets(form, PYMOL_OBJECT_WIDGETS)
    else:
        showWidgets(form, PYMOL_OBJECT_WIDGETS)
        hideWidgets(form, PDB_FILE_WIDGETS)


def showWidgets(form, widgets):
    for widget in widgets:
        getattr(form, widget).show()


def hideWidgets(form, widgets):
    for widget in widgets:
        getattr(form, widget).hide()
