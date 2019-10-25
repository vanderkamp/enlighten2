from qt_wrapper import QtWidgets, QtCore, uic


class WindowManager:

    def __init__(self):
        self.windows = {}

    def bind_all(self, controller):
        for window in self.windows.values():
            window.bind(controller)

    def close_all(self):
        for window in self.windows.values():
            window.close()

    def add(self, name, widget):
        self.windows[name] = widget

    def __getitem__(self, name):
        return self.windows[name]


class ManagedWindow(QtWidgets.QWidget):

    def __init__(self, name, ui, window_manager):
        super().__init__()
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        self.window_manager = window_manager
        window_manager.add(name, uic.loadUi(ui, self))

    def bind(self, controller):
        raise NotImplementedError

    def toggle_group(self, widget_names, state):
        for name in widget_names:
            widget = getattr(self, name)
            if state:
                widget.show()
            else:
                widget.hide()

