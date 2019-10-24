from qt_wrapper import QtWidgets, uic, WITH_PYMOL
import os
from validators import XYZValidator


class AtomSelector(QtWidgets.QWidget):

    def __init__(self, *args):
        super().__init__(*args)

        ui_file = os.path.join(os.path.dirname(__file__), 'atom_selector.ui')
        uic.loadUi(ui_file, self)

        self.lineEdit.set_validator(XYZValidator())
        if WITH_PYMOL:
            import pymol
            self.get_model = pymol.cmd.get_model
            self.loadButton.clicked.connect(self.load)
        else:
            self.loadButton.setEnabled(False)

    def load(self):
        try:
            atom = self.get_model('pk1').atom[0]
            self.lineEdit.setText(' '.join('{:.3f}'.format(x) for x in atom.coord))
        except IndexError:
            return

