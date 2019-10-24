from windows.terminal import TerminalWindow
from qt_wrapper import QtCore, WITH_PYMOL
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
        command = self.docker_command(self.state['working_dir'],
                                      prep_command)
        self.run_in_terminal("Prep", command, self.after_prep)

    def after_prep(self):
        if self.state.get('prep.relax'):
            self.update('dynam.system_name', self.state['prep.system_name'])
            self.update('dynam.tag', 'PREP')
            return self.run_dynam()
        self.load_system(self.state['working_dir'],
                         self.state['prep.system_name'],
                         'prep')

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
        filename = os.path.join(self.state['working_dir'], 'params')
        with open(filename, 'w') as f:
            json.dump(params, f)

    def run_dynam(self):
        if self.state['dynam.tag'] == 'PREP':
            arg, title = '-relax', 'Relax'
        else:
            arg, title = '', 'Dynam'
        dynam_command = "dynam.py {system_name} {arg}".format(
            system_name=self.state['dynam.system_name'],
            arg=arg
        )
        command = self.docker_command(self.state['working_dir'],
                                      dynam_command)
        self.run_in_terminal(title, command, self.after_dynam)

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
        print(rst, top)
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
    def run_in_terminal(cls, title, command, on_finished):
        process = QtCore.QProcess()
        terminal = TerminalWindow(process, title)
        process.start(command)

        def finished_callback():
            if not process.exitCode():
                terminal.close()
                on_finished()

        process.finished.connect(finished_callback)
        terminal.exec()

    @classmethod
    def docker_command(cls, working_dir, command):
        if os.name == 'nt':
            if os.environ.get('DOCKER_TOOLBOX_INSTALL_PATH'):
                working_dir = cls.parse_win_path(working_dir)
            return "docker run -v {dir}:/tmp " \
                   "kzinovjev/enlighten2 " \
                   "/bin/bash -lc \"{command}\"".format(dir=working_dir,
                                                        command=command)
        return "docker run -v {dir}:/tmp -u {uid}:{gid} " \
               "kzinovjev/enlighten2 " \
               "/bin/bash -lc \"{command}\"".format(dir=working_dir,
                                                    uid=os.geteuid(),
                                                    gid=os.getegid(),
                                                    command=command)

    @staticmethod
    def parse_win_path(path):
        drive = path[0]
        return path.replace('{}:/'.format(drive),
                            '//{}/'.format(drive.lower()))
