from windows.terminal import TerminalWindow
from qt_wrapper import QtCore


class Controller:

    def __init__(self):
        self.state = {}
        self.listeners = {}

    def update(self, key, value):
        if self.state.get(key) == value:
            return
        self.state[key] = value
        print(self.state)
        for listener in self._get_listeners(key):
            listener(value)

    def updater(self, key):
        return lambda value: self.update(key, value)

    def listen(self, key, listener):
        self.listeners[key] = self._get_listeners(key) + [listener]

    def _get_listeners(self, key):
        return self.listeners.get(key, [])


class PyQtController(Controller):

    def bind_lineEdit(self, key, lineEdit):
        lineEdit.textChanged.connect(self.updater(key))
        self.listen(key, self.lineEdit_text_updater(lineEdit))

    def bind_checkBox(self, key, checkBox):
        checkBox.toggled.connect(self.updater(key))
        self.listen(key, checkBox.setChecked)

    def bind_slider(self, key, slider):
        slider.valueChanged.connect(self.updater(key))
        self.listen(key, slider.setValue)

    def bind_radio_button(self, key, radioButton):
        radioButton.toggled.connect(self.updater(key))
        self.listen(key, radioButton.setChecked)

    def bind_combo_box(self, key, comboBox):
        comboBox.currentTextChanged.connect(self.updater(key))
        self.listen(key, comboBox.setCurrentText)

    def bind_file_selector(self, key, fileSelector):
        self.bind_lineEdit(key, fileSelector.lineEdit)

    def bind_atom_selector(self, key, atomSelector):
        self.bind_lineEdit(key, atomSelector.lineEdit)

    @classmethod
    def lineEdit_text_updater(cls, lineEdit):
        return lambda value: cls._set_text_if_changed(lineEdit, value)

    @staticmethod
    def _set_text_if_changed(lineEdit, value):
        if lineEdit.text() != value:
            lineEdit.setText(value)


class EnlightenController(PyQtController):

    @staticmethod
    def open_enlighten_website():
        import webbrowser
        webbrowser.open_new("https://github.com/vanderkamp/enlighten2/")

    def run_prep(self):
        import os
        path = os.path.join(os.path.dirname(__file__), 'mock_prep.py')
        self.run_in_terminal('Prep', path)

    def run_dynam(self):
        pass

    def load_trajectory(self):
        pass

    @staticmethod
    def run_in_terminal(title, command):
        process = QtCore.QProcess()
        terminal = TerminalWindow(process, title)
        process.start(command)
        terminal.exec()
