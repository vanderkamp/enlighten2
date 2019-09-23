from qt_wrapper import QtWidgets


class ValidatedLineEdit(QtWidgets.QLineEdit):

    def __init__(self, *args):
        super().__init__(*args)
        self.pristine = True
        self.validator = None
        self.textChanged.connect(self.on_change)

    def set_validator(self, validator):
        self.validator = validator
        self.validate()

    def get_invalid_tooltip(self):
        try:
            return self.validator.tooltip()
        except AttributeError:
            return ''

    def on_change(self, value=None):
        self.pristine = False
        self.validate(value)

    def validate(self, value=None):
        if self.pristine:
            return
        if self.is_valid(value):
            self.setToolTip('')
            self.setStyleSheet("QLineEdit {background-color: #FFFFFF;}")
        else:
            self.setToolTip(self.get_invalid_tooltip())
            self.setStyleSheet("QLineEdit {background-color: #FFAFAF;}")

    def is_valid(self, value=None):
        if not self.validator:
            return True
        return self.validator(value or self.text())
