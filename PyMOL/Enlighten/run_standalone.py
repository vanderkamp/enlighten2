import sys
from qt_wrapper import QtWidgets
from windows.windows import WindowManager
from windows.main import MainWindow
from controller import EnlightenController


def main():
    app = QtWidgets.QApplication(sys.argv)
    window_manager = WindowManager()
    main_window = MainWindow(window_manager)
    window_manager.bind_all(EnlightenController())

    main_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
