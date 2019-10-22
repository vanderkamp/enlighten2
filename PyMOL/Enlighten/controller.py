from windows.terminal import TerminalWindow
from qt_wrapper import QtCore
import os
import json


class Controller:

    def __init__(self):
        self.state = {}
        self.listeners = {}

    def update(self, key, value):
        if self.state.get(key) == value:
            return
        self.state[key] = value
        print(self.state)
        for listener in self._get_listeners(key):
            listener(value)

    def updater(self, key):
        return lambda value: self.update(key, value)

    def listen(self, key, listener):
        self.listeners[key] = self._get_listeners(key) + [listener]

    def _get_listeners(self, key):
        return self.listeners.get(key, [])


class PyQtController(Controller):

    def bind_lineEdit(self, key, lineEdit):
        lineEdit.textChanged.connect(self.updater(key))
        self.listen(key, self.lineEdit_text_updater(lineEdit))

    def bind_checkBox(self, key, checkBox):
        checkBox.toggled.connect(self.updater(key))
        self.listen(key, checkBox.setChecked)

    def bind_slider(self, key, slider):
        slider.valueChanged.connect(self.updater(key))
        self.listen(key, slider.setValue)

    def bind_radio_button(self, key, radioButton):
        radioButton.toggled.connect(self.updater(key))
        self.listen(key, radioButton.setChecked)

    def bind_combo_box(self, key, comboBox):
        comboBox.currentTextChanged.connect(self.updater(key))
        self.listen(key, comboBox.setCurrentText)

    def bind_file_selector(self, key, fileSelector):
        self.bind_lineEdit(key, fileSelector.lineEdit)

    def bind_atom_selector(self, key, atomSelector):
        self.bind_lineEdit(key, atomSelector.lineEdit)

    @classmethod
    def lineEdit_text_updater(cls, lineEdit):
        return lambda value: cls._set_text_if_changed(lineEdit, value)

    @staticmethod
    def _set_text_if_changed(lineEdit, value):
        if lineEdit.text() != value:
            lineEdit.setText(value)


class EnlightenController(PyQtController):

    @staticmethod
    def open_enlighten_website():
        import webbrowser
        webbrowser.open_new("https://github.com/vanderkamp/enlighten2/")

    def run_prep(self):

        if self.state.get('prep.use_object'):
            pdb = self.state['prep.object'] + '.pdb'
            self.write_object_to_pdb(
                self.state['prep.object'],
                os.path.join(self.state['prep.working_dir'], pdb)
            )
        else:
            pdb = os.path.basename(self.state['prep.pdb'])
            os.system("cp {} {}".format(self.state['prep.pdb'],
                                        self.state['prep.working_dir']))

        self.dump_prep_params()
        prep_command = (
            "prep.py {system_name} {pdb} {ligand_name} {ligand_charge} params"
        ).format(
            system_name=self.state['prep.system_name'],
            pdb=pdb,
            ligand_name=self.state['prep.ligand_name'],
            ligand_charge=self.state['prep.ligand_charge']
        )

        command = self.docker_command(self.state['prep.working_dir'],
                                      prep_command)
        self.run_in_terminal("Prep", command)

    def dump_prep_params(self):
        params = {
            'propka': {
                'ph': float(self.state['prep.advanced.ph'])
            },
            'tleap': {
                'solvent_radius': self.state['prep.advanced.sphere_size']
            }
        }
        center = self.state['prep.advanced.center']
        if center != '':
            params['tleap']['center'] = center
        filename = os.path.join(self.state['prep.working_dir'], 'params')
        with open(filename, 'w') as f:
            json.dump(params, f)


    def run_dynam(self):
        pass

    def load_trajectory(self):
        pass

    @staticmethod
    def write_object_to_pdb(object_name, filename):
        import pymol
        pymol.cmd.save(filename, '({})'.format(object_name))

    @staticmethod
    def run_in_terminal(title, command):
        process = QtCore.QProcess()
        terminal = TerminalWindow(process, title)
        process.start(command)
        process.finished.connect(terminal.close)
        terminal.exec()

    @staticmethod
    def docker_command(working_dir, command):
        if os.name == 'nt':
            working_dir = working_dir.replace('C:/', '//c/')
            return "docker run -t -v {dir}:/tmp " \
                   "kzinovjev/enlighten2 " \
                   "/bin/bash -lc \"{command}\"".format(dir=working_dir,
                                                        command=command)
        return "docker run -t -v {dir}:/tmp -u {uid}:{gid} " \
               "kzinovjev/enlighten2 " \
               "/bin/bash -lc \"{command}\"".format(dir=working_dir,
                                                    uid=os.geteuid(),
                                                    gid=os.getegid(),
                                                    command=command)
