from qt_wrapper import QtWidgets, QtGui
import os


class SystemList(QtWidgets.QListWidget):

    def __init__(self, *args):
        super().__init__(*args)
        self.directory = None

    def set_directory(self, directory):
        self.directory = directory
        self.clear()
        for system in _find_systems(directory):
            self.addItem(SystemItem(system))

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
        super().__init__(os.path.basename(path))
        self.path = path
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
