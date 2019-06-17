import sys
from PyQt5 import QtWidgets
from windows.windows import WindowManager
from windows.main import MainWindow
from controller import EnlightenController


def main():
    app = QtWidgets.QApplication(sys.argv)
    window_manager = WindowManager()
    main_window = MainWindow(window_manager)
    controller = EnlightenController()
    window_manager.bind_all(controller)

    main_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
