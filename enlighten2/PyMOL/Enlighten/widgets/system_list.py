from qt_wrapper import QtWidgets, QtGui, QtCore
import os


class SystemList(QtWidgets.QListWidget):
    selected = QtCore.pyqtSignal(QtWidgets.QListWidgetItem)
    unselected = QtCore.pyqtSignal()

    def __init__(self, *args):
        super().__init__(*args)
        self.directory = None
        self.itemSelectionChanged.connect(self._on_select)

    def update(self):
        if self.directory:
            self.set_directory(self.directory)

    def set_directory(self, directory):
        self.directory = directory
        self.clear()
        for system in _find_systems(directory):
            self.addItem(SystemItem(system))

    def _on_select(self):
        selected_system = self.selected_system()
        if not selected_system:
            return self.unselected.emit()
        self.selected.emit(selected_system)

    def selected_system(self):
        try:
            return self.selectedItems()[0]
        except IndexError:
            return None


class SystemItem(QtWidgets.QListWidgetItem):

    BACKGROUND_DICT = {'PREP': QtGui.QColor('#ffffff'),
                       'RELAX': QtGui.QColor('#ffff70'),
                       'DYNAM': QtGui.QColor('#70ff70')}

    def __init__(self, path):
        self.name = os.path.basename(path)
        super().__init__(self.name)
        self.tag = _system_tag(path)
        self.setBackground(self.BACKGROUND_DICT[self.tag])


def _system_tag(path):
    if _step_done(path, 'dynam'):
        return 'DYNAM'
    if _step_done(path, 'relax'):
        return 'RELAX'
    return 'PREP'


def _step_done(path, step):
    step_path = os.path.join(path, step)
    name = os.path.basename(path)
    return all((_has_subdir(path, step),
                _has_file(step_path, '{}_{}.{}'.format(name, step, 'rst'))))


def _find_systems(path):
    try:
        return [os.path.join(path, name) for name in os.listdir(path)
                if _is_a_system(path, name)]
    except FileNotFoundError:
        return []


def _is_a_system(path, name):
    system_path = os.path.join(path, name)
    return all((_has_file(system_path, '{}.{}'.format(name, 'rst')),
                _has_file(system_path, '{}.{}'.format(name, 'top'))))


def _has_file(path, filename):
    return os.path.isfile(os.path.join(path, filename))


def _has_subdir(path, subdir):
    return os.path.isdir(os.path.join(path, subdir))
