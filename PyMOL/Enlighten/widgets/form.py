from PyQt5.QtWidgets import QMessageBox


class Form:

    def __init__(self, fields, button, active=True):
        """
        Not a widget itself, but adds a form-like behaviour to a set of
        ValidatedLineEdit widgets and a button: when the button is clicked for
        the first time, all the fields are (re)validated and if any of the
        fields is invalid an error message appears and the button becomes
        inactive until all the fields become valid.
        :param fields: List of widgets having a 'validator' field
        """
        self.fields = fields
        self.button = button
        self.pristine = True
        self.active = active
        button.clicked.connect(self.on_button_click)
        for field in fields:
            field.textChanged.connect(self.on_field_change)

    def set_active(self, value):
        self.active = value

    def on_button_click(self):
        if not self.active:
            return
        self.pristine = False
        errors = self.get_errors()
        print(errors)
        if len(errors):
            QMessageBox.critical(self.button.parent(), "Error",
                                 self.error_message(errors))
            self.button.setEnabled(False)

    def on_field_change(self, value):
        if not self.pristine and self.active:
            self.button.setEnabled(not len(self.get_errors()))

    def get_errors(self):
        self.validate_fields()
        return [field.validator.tooltip() for field in self.invalid_fields()]

    def validate_fields(self):
        for field in self.fields:
            field.on_change()

    def invalid_fields(self):
        return [field for field in self.fields if not field.is_valid()]

    @staticmethod
    def error_message(errors):
        return "The following errors were encountered:\n" \
               "{}".format('\n'.join(errors))
