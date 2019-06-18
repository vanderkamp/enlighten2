from PyQt5 import QtWidgets, uic
import os


class FileSelector(QtWidgets.QWidget):

    def __init__(self, *args):
        super().__init__(*args)

        ui_file = os.path.join(os.path.dirname(__file__), 'file_selector.ui')
        uic.loadUi(ui_file, self)

        self.text = self.lineEdit.text
        self.textChanged = self.lineEdit.textChanged
        self.setText = self.lineEdit.setText

        self.pristine = True
        self.directory_mode = False
        self.validator = None
        self.browseButton.clicked.connect(self.browse)
        self.textChanged.connect(self.on_change)

    def set_directory_mode(self, value):
        self.directory_mode = value
        self.validate(self.text())

    def set_validator(self, value):
        self.validator = value
        self.validate(self.text())

    def on_change(self, value):
        self.pristine = False
        self.validate(value)

    def validate(self, value):
        if self.pristine:
            return
        if self.is_valid(value):
            self.setStyleSheet("QLineEdit {background-color: #FFFFFF;}")
        else:
            self.setStyleSheet("QLineEdit {background-color: #FFAFAF;}")

    def is_valid(self, value):
        if self.validator:
            return self.validator(value)
        if self.directory_mode:
            return os.path.isdir(value)
        else:
            return os.path.isfile(value)

    def browse(self):
        if self.directory_mode:
            result = QtWidgets.QFileDialog.getExistingDirectory()
        else:
            result = QtWidgets.QFileDialog.getOpenFileName()[0]
        if result:
            self.setText(result)
