from windows.terminal import TerminalWindow
from qt_wrapper import QtWidgets, WITH_PYMOL
import os
import json
import shutil
from docker_process import DockerProcess


class Controller:

    def __init__(self):
        self.state = {}
        self.listeners = {}

    def update(self, key, value):
        if self.state.get(key) == value:
            return
        self.state[key] = value
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

        system_path = os.path.join(self.state['working_dir'],
                                   self.state['prep.system_name'])
        if os.path.isdir(system_path):
            message = "Folder {} exists. Remove?".format(system_path)
            if self.dialog(message):
                shutil.rmtree(system_path)
            else:
                return

        if self.state.get('prep.use_object'):
            pdb = self.state['prep.object'] + '.pdb'
            self.write_object_to_pdb(
                self.state['prep.object'],
                os.path.join(self.state['working_dir'], pdb)
            )
        else:
            pdb = os.path.basename(self.state['prep.pdb'])
            os.system("cp {} {}".format(self.state['prep.pdb'],
                                        self.state['working_dir']))

        self.dump_prep_params()
        prep_command = (
            "prep.py {system_name} {pdb} {ligand_name} {ligand_charge} params"
        ).format(
            system_name=self.state['prep.system_name'],
            pdb=pdb,
            ligand_name=self.state['prep.ligand_name'],
            ligand_charge=self.state['prep.ligand_charge']
        )
        self.run_in_terminal("Prep",
                             self.state['working_dir'],
                             prep_command,
                             self.after_prep)

    @staticmethod
    def dialog(message):
        dialog = QtWidgets.QMessageBox()
        dialog.setIcon(QtWidgets.QMessageBox.Question)
        dialog.setWindowTitle("Warning")
        dialog.setText(message)
        dialog.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        dialog.setDefaultButton(QtWidgets.QMessageBox.No)
        dialog.setEscapeButton(QtWidgets.QMessageBox.No)
        return dialog.exec_() == QtWidgets.QMessageBox.Yes

    def after_prep(self):
        if self.state.get('prep.relax'):
            self.update('dynam.system_name', self.state['prep.system_name'])
            self.update('dynam.tag', 'PREP')
            return self.run_dynam()
        self.load_system(self.state['working_dir'],
                         self.state['prep.system_name'],
                         'PREP')

    def dump_prep_params(self):
        params = {
            'propka': {
                'ph': float(self.state['prep.advanced.ph'])
            },
            'tleap': {
                'solvent_radius': self.state['prep.advanced.sphere_size'],
                'include': ['.']
            }
        }
        center = self.state['prep.advanced.center']
        if center != '':
            params['tleap']['center'] = center
        filename = os.path.join(self.state['working_dir'], 'params')
        with open(filename, 'w') as f:
            json.dump(params, f)

    def remove_system(self):
        if self.dialog("Are you sure?"):
            path = os.path.join(self.state['working_dir'],
                                self.state['dynam.system_name'])
            shutil.rmtree(path)

    def run_dynam(self):
        if self.state['dynam.tag'] == 'PREP':
            arg, title = '-relax', 'Relax'
        else:
            arg, title = '', 'Dynam'
        self.dump_dynam_params()
        dynam_command = "dynam.py {arg} {system_name} {params}".format(
            system_name=self.state['dynam.system_name'],
            arg=arg,
            params="dynam.params"
        )
        self.run_in_terminal(title,
                             self.state['working_dir'],
                             dynam_command,
                             self.after_dynam)

    def dump_dynam_params(self):
        params = {'steps': int(self.state['dynam.simulation_time']) * 500}
        filename = os.path.join(self.state['working_dir'], 'dynam.params')
        with open(filename, 'w') as f:
            json.dump(params, f)

    def after_dynam(self):
        tag = 'RELAX' if self.state['dynam.tag'] == 'PREP' else 'DYNAM'
        self.load_system(self.state['working_dir'],
                         self.state['dynam.system_name'],
                         tag)

    def load_dynam(self):
        self.load_system(self.state['working_dir'],
                         self.state['dynam.system_name'],
                         self.state['dynam.tag'])

    @classmethod
    def load_system(cls, working_dir, system_name, tag):
        system_dir = os.path.join(working_dir, system_name)
        step = tag.lower()
        if tag == 'PREP':
            rst_name = os.path.join('tleap', system_name + '.rst')
            format = 'rst'
        elif tag == 'RELAX':
            rst_name = os.path.join('relax', system_name + '_{}.rst'.format(step))
            format = 'rst'
        else:
            rst_name = os.path.join('dynam', 'md', 'mdcrd')
            format = 'trj'
        top_name = system_name + '.top'
        rst = os.path.join(system_dir, rst_name)
        top = os.path.join(system_dir, top_name)
        name = system_name + ' ({})'.format(step)
        cls.load_trajectory(rst, top, name, format)

    @staticmethod
    def load_trajectory(rst, top, name, format='rst'):
        if not WITH_PYMOL:
            return
        import pymol
        pymol.cmd.load(top, name)
        pymol.cmd.load(rst, name, format=format)

    @staticmethod
    def write_object_to_pdb(object_name, filename):
        import pymol
        # Keep original value to cause no side effects
        pdb_use_ter_records = pymol.cmd.get('pdb_use_ter_records')
        pymol.cmd.set('pdb_use_ter_records', 'off')
        pymol.cmd.save(filename, '({})'.format(object_name))
        pymol.cmd.set('pdb_use_ter_records', pdb_use_ter_records)

    @classmethod
    def run_in_terminal(cls, title, working_dir, command, on_finished):
        process = DockerProcess()
        terminal = TerminalWindow(process, title)
        process.start(working_dir, command)

        def finished_callback():
            if not process.exitCode():
                terminal.close()
                on_finished()

        process.finished.connect(finished_callback)
        terminal.exec()
