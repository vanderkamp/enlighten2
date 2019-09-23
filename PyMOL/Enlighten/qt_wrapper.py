try:
    from pymol.Qt import QtWidgets, QtCore, QtGui
    WITH_PYMOL = True
except ImportError:
    from PyQt5 import QtWidgets, QtCore, QtGui
    WITH_PYMOL = False

try:
    from PyQt5 import uic
except ImportError:
    from PyQt4 import uic