from PyQt5 import QtWidgets, uic
import os
from validators import FileValidator, DirectoryValidator


class FileSelector(QtWidgets.QWidget):

    def __init__(self, *args):
        super().__init__(*args)

        ui_file = os.path.join(os.path.dirname(__file__), 'file_selector.ui')
        uic.loadUi(ui_file, self)

        self.text = self.lineEdit.text
        self.textChanged = self.lineEdit.textChanged
        self.setText = self.lineEdit.setText
        self.set_validator = self.lineEdit.set_validator

        self.pristine = True
        self.directory_mode = False
        self.browseButton.clicked.connect(self.browse)
        self.textChanged.connect(self.lineEdit.on_change)

    def set_directory_mode(self, value):
        self.directory_mode = value
        if value:
            self.set_validator(DirectoryValidator())
        else:
            self.set_validator(FileValidator())
        self.lineEdit.validate()

    def browse(self):
        if self.directory_mode:
            result = QtWidgets.QFileDialog.getExistingDirectory()
        else:
            result = QtWidgets.QFileDialog.getOpenFileName()[0]
        if result:
            self.setText(result)
