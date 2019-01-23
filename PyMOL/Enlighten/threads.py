import threading
import subprocess
from pymol.Qt import QtCore


class SubprocessThread(QtCore.QThread):
        def __init__(self, command):
            QtCore.QThread.__init__(self)
            self.command = command

        def __del__(self):
            self.wait()

        def run(self):
            proc = subprocess.Popen(self.command,
                                    shell=True,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            proc.wait()
            self.output = proc.stdout.read().decode('string_escape')
            self.error = proc.stderr.read().decode('string_escape')
