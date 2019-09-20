from qt_wrapper import QtWidgets, uic
import os
from validators import AtomValidator


class AtomSelector(QtWidgets.QWidget):

    def __init__(self, *args):
        super().__init__(*args)

        ui_file = os.path.join(os.path.dirname(__file__), 'atom_selector.ui')
        uic.loadUi(ui_file, self)

        self.lineEdit.set_validator(AtomValidator())

        try:
            import pymol
            self.get_model = pymol.cmd.get_model
            self.loadButton.clicked.connect(self.load)
        except ImportError:
            self.loadButton.setEnabled(False)

    def load(self):
        try:
            atom = self.get_model('pk1').atom[0]
            self.lineEdit.setText('{}.{}'.format(atom.resi_number, atom.name))
        except IndexError:
            return

