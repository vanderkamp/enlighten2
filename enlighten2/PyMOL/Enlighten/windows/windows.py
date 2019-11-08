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
        self.setWindowFlag(QtCore.Qt.Tool)
        self.window_manager = window_manager
        window_manager.add(name, uic.loadUi(ui, self))
        move_to_center(self)

    def bind(self, controller):
        raise NotImplementedError

    def toggle_group(self, widget_names, state):
        for name in widget_names:
            widget = getattr(self, name)
            if state:
                widget.show()
            else:
                widget.hide()


def move_to_center(window):
    center = QtWidgets.QDesktopWidget().availableGeometry().center()
    window_size = window.size()
    print(center, window_size)
    print(center.x(), center.y(), window_size.width(), window_size.height())
    window.move(center.x() - window_size.width() / 2,
                center.y() - window_size.height() / 2)
