from qt_wrapper import QtWidgets, uic
import os
from validators import FileValidator, DirectoryValidator


class FileSelector(QtWidgets.QWidget):

    def __init__(self, *args):
        super().__init__(*args)

        ui_file = os.path.join(os.path.dirname(__file__), 'file_selector.ui')
        uic.loadUi(ui_file, self)

        self.directory_mode = False
        self.browseButton.clicked.connect(self.browse)

    def set_directory_mode(self, value):
        self.directory_mode = value
        if value:
            self.lineEdit.set_validator(DirectoryValidator())
        else:
            self.lineEdit.set_validator(FileValidator())
        self.lineEdit.validate()

    def browse(self):
        if self.directory_mode:
            result = QtWidgets.QFileDialog.getExistingDirectory()
        else:
            result = QtWidgets.QFileDialog.getOpenFileName()[0]
        if result:
            self.lineEdit.setText(result)
