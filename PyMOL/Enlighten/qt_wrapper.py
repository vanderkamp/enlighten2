try:
    from pymol.Qt import QtWidgets, QtCore, QtGui, uic
    WITH_PYMOL = True
except ImportError:
    from PyQt5 import QtWidgets, QtCore, QtGui, uic
    WITH_PYMOL = False
