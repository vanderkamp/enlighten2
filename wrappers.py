import os
import shutil
import pdb_utils
import utils
import tleap
import json
import sys


def get_amberhome():
    if 'AMBERHOME' not in os.environ:
        raise AssertionError("$AMBERHOME not set")
    return os.environ['AMBERHOME']


class AntechamberWrapper(object):

    def __init__(self, pdb, name, charge=0,
                 working_directory="antechamber", create_frcmod=True):

        amberhome = get_amberhome()
        utils.set_working_directory(working_directory)
        pdb.to_filename('ligand.pdb')

        antechamber_command = (amberhome + "/bin/antechamber " +
                               "-i ligand.pdb -fi pdb -o {name}.prepc "
                               "-fo prepc -rn {name} -c bcc -nc {charge}"
                               .format(name=name, charge=charge))
        utils.run_in_shell(antechamber_command, 'antechamber.out')
        utils.check_file(name + '.prepc',
                         "Antechamber failed to generate {name}.prepc file"
                         .format(name=name))

        self.working_directory = os.getcwd()
        if create_frcmod:
            parmck_command = (amberhome + "/bin/parmchk2 " +
                              "-i {name}.prepc -f prepc -o {name}.frcmod"
                              .format(name=name))
            utils.run_in_shell(parmck_command, 'parmchk2.out')
            # TODO: check for ATTN warnings

        os.chdir('..')


class Pdb4AmberReduceWrapper(object):

    def __init__(self, pdb, working_directory="pdb4amber_reduce"):

        amberhome = get_amberhome()
        utils.set_working_directory(working_directory)
        pdb.to_filename('input.pdb')

        pdb4amber_command = (amberhome + "/bin/pdb4amber "
                             "-i input.pdb -o pdb4amber.pdb --nohyd")
        utils.run_in_shell(pdb4amber_command, 'pdb4amber.out')

        reduce_command = (amberhome + "/bin/reduce "
                          "-build -nuclear pdb4amber.pdb")
        utils.run_in_shell(reduce_command, 'reduce.pdb')

        with open('reduce.pdb') as f:
            self.pdb = pdb_utils.Pdb(f)

        renamed_histidines = get_renamed_histidines(self.pdb)
        residues = self.pdb.residues()

        for res_hash, res_name in renamed_histidines.items():
            pdb_utils.modify_atoms(residues.get(res_hash, []),
                                   'resName', res_name)

        # Remove hydrogens on HETATMs
        self.pdb.atoms = [atom for atom in self.pdb.atoms
                          if (atom['record'] != 'HETATM' or
                              'new' not in atom['extras'])]

        # Remove hydrogens added by reduce to non-protein residues
        with open('pdb4amber_nonprot.pdb') as f:
            self.nonprotPdb = pdb_utils.Pdb(f)
        self.nonprot_residues = set(atom['resName']
                                    for atom in self.nonprotPdb.atoms)
        self.pdb.atoms = [atom for atom in self.pdb.atoms
                          if (atom['resName'] not in self.nonprot_residues or
                              'new' not in atom['extras'])]

        os.chdir('..')


def get_renamed_histidines(pdb):

    RENAME_DICT = {'no HE2': 'HID',
                   'no HD1': 'HIE',
                   'bothHN': 'HIP'}
    renamed_histidines = {}  # dict of residue_hash: new_name pairs

    for line in pdb.other:
        if line[:9] != 'USER  MOD' or line[25:28] != 'HIS':
            continue

        his_name = RENAME_DICT.get(line[39:45])
        if his_name is None:
            continue

        his_hash = pdb_utils.residue_hash({'chainID': line[19],
                                           'resSeq': int(line[20:24]),
                                           'resName': "HIS"})
        renamed_histidines[his_hash] = his_name

    return renamed_histidines


PROT_DICT = {'ASP': 'ASH', 'GLU': 'GLH'}
DEPROT_DICT = {'CYS': 'CYM', 'LYS': 'LYN'}


class PropkaWrapper(object):

    def __init__(self, pdb, ph=7.0, ph_offset=0.7,
                 working_directory="propka"):

        utils.set_working_directory(working_directory)
        pdb.to_filename('input.pdb')

        utils.run_in_shell("propka31 input.pdb", "propka31.out")
        with open('input.pka') as f:
            propka_results = parse_propka_output(f)

        self.pdb = pdb.copy()
        residues = self.pdb.residues()

        self.prot_pka = ph + ph_offset
        self.deprot_pka = ph - ph_offset
        self.prot_list = []
        self.deprot_list = []

        for hash, pka_entry in propka_results.items():
            if hash not in residues:
                continue

            if prot_residue(pka_entry, self.prot_pka):
                pdb_utils.modify_atoms(residues[hash],
                                       'resName',
                                       PROT_DICT[pka_entry['resName']])
                self.prot_list.append(pka_entry)

            if deprot_residue(pka_entry, self.deprot_pka):
                pdb_utils.modify_atoms(residues[hash],
                                       'resName',
                                       DEPROT_DICT[pka_entry['resName']])
                self.deprot_list.append(pka_entry)

                # Need to remove hydrogens added by reduce on deprotonated
                # residues - else top-file creation will fail.
                self.pdb.remove_atom(pdb_utils.find_atom(
                    residues[hash],
                    lambda atom: 'new' in atom['extras']
                ))

                # Also remove HZ1 atoms from deprotonated LYS
                if pka_entry['resName'] == 'LYS':
                    self.pdb.remove_atom(pdb_utils.find_atom(
                        residues[hash],
                        lambda atom: atom['name'] == 'HZ1'
                    ))

        PRINT_PKA_FORMAT = "{resName:>6}{resSeq:>4}{chainID:>2}{pKa:>9.2f}"

        if len(self.prot_list) > 0:
            print("The following ASP/GLU residues have predicted pKa's above "
                  "{:4.2f} and will be protonated (on OD2/OE2):"
                  .format(self.prot_pka))
            print("                  pKa")

            for pka_entry in self.prot_list:
                print(PRINT_PKA_FORMAT.format(**pka_entry))

        if len(self.deprot_list) > 0:
            print("The following CYS/LYS residues have predicted pKa's below "
                  "{:4.2f} and will be deprotonated:"
                  .format(self.deprot_pka))
            print("                  pKa")

            for pka_entry in self.deprot_list:
                print(PRINT_PKA_FORMAT.format(**pka_entry))

        os.chdir('..')


def parse_propka_output(file):
    while next(file) != "SUMMARY OF THIS PREDICTION\n":
        pass
    next(file)
    return {pdb_utils.residue_hash(entry): entry
            for entry in map(line_to_pka_entry, file)
            if entry is not None}


def line_to_pka_entry(line):
    raw_entry = line.split()
    if len(raw_entry) != 5:
        return None
    return {'resName': raw_entry[0],
            'resSeq': int(raw_entry[1]),
            'chainID': raw_entry[2],
            'pKa': float(raw_entry[3]),
            'model-pKa': float(raw_entry[4])}


def prot_residue(pka_entry, prot_pka):
    return (pka_entry['resName'] in PROT_DICT.keys() and
            pka_entry['pKa'] >= prot_pka)


def deprot_residue(pka_entry, deprot_pka):
    return (pka_entry['resName'] in DEPROT_DICT.keys() and
            pka_entry['pKa'] <= deprot_pka)


class TleapWrapper(object):

    def __init__(self, template_name, include=[], nonprot_residues=[],
                 params={}, working_directory='tleap'):

        utils.set_working_directory(working_directory)

        enlighten_path = os.path.dirname(__import__(__name__).__file__)
        tleap_module_path = os.path.join(enlighten_path, 'tleap')
        template_path = os.path.join(tleap_module_path, template_name + '.in')
        template_contents = None
        if os.path.isfile(template_path):
            with open(template_path) as f:
                template_contents = f.read()

        params['include'] = get_tleap_includes(include, nonprot_residues)
        template_module = getattr(
            __import__('tleap', fromlist=[template_name]),
            template_name
        )

        params['pdb'].to_filename('input.pdb')
        with open('tleap.in', 'w') as f:
            f.write(template_module.run(params, template_contents))
        utils.run_in_shell('tleap -f tleap.in', 'tleap.log')

        try:
            check_result = template_module.check(params, self)
            if check_result:
                sys.exit(check_result)
        except AttributeError:
            pass

        if 'export' in params:
            with open('params', 'w') as f:
                json.dump(params['export'], f)
        os.chdir('..')


def get_tleap_includes(include, nonprot_residues):

    INCLUDE_COMMANDS = {'off': 'loadoff {}',
                        'prepc': 'loadamberprep {}',
                        'frcmod': 'loadamberparams {}'}

    # Find all the include files and check that frcmod and prepc files are
    # provided for all non-protein residues
    include_lists = {key: [] for key in INCLUDE_COMMANDS.keys()}
    for residue in nonprot_residues:
        residue_includes = {
            key: utils.file_in_paths('{}.{}'.format(residue, key), include)
            for key in INCLUDE_COMMANDS.keys()
        }

        if not residue_includes['prepc']:
            raise FileNotFoundError("Cannot find topology ({0}.prepc) for "
                                    "residue {0}. Exiting...".format(residue))
        if not residue_includes['frcmod']:
            raise FileNotFoundError("Cannot find parameters ({0}.frcmod) for "
                                    "residue {0}. Exiting...".format(residue))

        for key, value in residue_includes.items():
            if residue_includes[key] is not None:
                include_lists[key].append(value)

    return '\n'.join(INCLUDE_COMMANDS[key].format(name)
                     for key, include_list in include_lists.items()
                     for name in include_list)


class SanderWrapper(object):

    def __init__(self, prefix, template, crd, prmtop, params, working_directory):

        self.prefix = prefix

        os.mkdir(working_directory)
        self.working_directory = os.path.abspath(working_directory)

        template_file = self._full_path('{}.in'.format(prefix))
        utils.dump_to_file(template_file, self._get_template(template, params))

        command = ('{amberhome}/bin/sander -O -i {prefix}.in -p {prmtop} '
                   '-c {crd} -o {prefix}.log -r {prefix}.rst -ref {crd}')
        self.exit_code = utils.run_at_path(
            command.format(amberhome=get_amberhome(), prefix=prefix,
                           crd=crd, prmtop=prmtop),
            working_directory
        )

        self.output_crd = self._full_path('{}.rst'.format(prefix))

    def _full_path(self, filename):
        return os.path.join(self.working_directory, filename)

    @staticmethod
    def _get_template(template, params):
        enlighten_path = os.path.dirname(__import__(__name__).__file__)
        template_path = os.path.join(enlighten_path, 'sander', template + '.in')
        return utils.parse_template(template_path, params)
