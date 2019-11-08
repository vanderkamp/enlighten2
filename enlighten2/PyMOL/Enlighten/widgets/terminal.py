from qt_wrapper import QtWidgets


class Terminal(QtWidgets.QTextEdit):

    def __init__(self, *args):
        super().__init__(*args)
        self.process = None
        self.setReadOnly(True)
        self.setStyleSheet("Terminal {background-color: #000000;}")

    def attach(self, process):
        self.clear()
        self.process = process
        process.readyReadStandardOutput.connect(self.output_ready)
        process.readyReadStandardError.connect(self.error_ready)
        process.finished.connect(self.detach)

    def detach(self):
        self.process = None

    def output_ready(self):
        text = self.process.readAllStandardOutput().data().decode('utf-8').strip()
        self.print_text(text, 'white')

    def error_ready(self):
        text = self.process.readAllStandardError().data().decode('utf-8')
        self.print_text(text, 'red')

    def print_text(self, text, color):
        cursor = self.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertHtml(
            '<font color="{}">{}</font><br>'.format(color,
                                                    text.replace('\n', '<br/>'))
        )
        self.ensureCursorVisible()
        print(text)
