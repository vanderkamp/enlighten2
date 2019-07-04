from qt_wrapper import QtWidgets, uic
import os


class TerminalWindow(QtWidgets.QDialog):

    def __init__(self, process, title):
        super().__init__()
        path = os.path.join(os.path.dirname(__file__), 'terminal.ui')
        uic.loadUi(path, self)
        self.setWindowTitle(title)
        self.process = process
        self.terminal.attach(process)

    def closeEvent(self, event):
        self.process.terminate()
        self.process.waitForFinished()
        event.accept()
