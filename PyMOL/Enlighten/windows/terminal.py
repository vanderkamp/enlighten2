from PyQt5 import QtWidgets, uic


class TerminalWindow(QtWidgets.QDialog):

    def __init__(self, process, title):
        super().__init__()
        uic.loadUi('windows/terminal.ui', self)
        self.setWindowTitle(title)
        self.process = process
        self.terminal.attach(process)

    def closeEvent(self, event):
        self.process.terminate()
        self.process.waitForFinished()
        event.accept()
