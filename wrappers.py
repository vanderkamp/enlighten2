import os
import shutil
import pdb_utils
import utils


def check_amberhome():
    if 'AMBERHOME' not in os.environ:
        raise AssertionError("$AMBERHOME not set")


class AntechamberWrapper(object):

    def __init__(self, pdb, name, charge=0,
                 working_directory=".antechamber", frcmod=None):

        check_amberhome()
        utils.set_working_directory(working_directory)
        pdb.tofile('ligand.pdb')

        os.system(
            "$AMBERHOME/bin/antechamber "
            "-i ligand.pdb -fi pdb -o {name}.prepc -fo prepc "
            "-rn {name} -c bcc -nc {charge}"
            .format(name=name, charge=charge)
        )

        utils.check_file(name + '.prepc',
                         "Antechamber failed to generate {name}.prepc file"
                         .format(name=name))

        if frcmod is None:
            os.system("$AMBERHOME/bin/parmchk2 "
                      "-i {name}.prepc -f prepc -o {name}.frcmod"
                      .format(name=name))
            # TODO: check for ATTN warnings
            self.frcmod = os.path.join(os.getcwd(), name + '.frcmod')
        else:
            self.frcmod = frcmod

        os.chdir('..')


class Pdb4AmberReduceWrapper(object):

    def __init__(self, pdb, working_directory=".pdb4amber_reduce"):

        check_amberhome()
        utils.set_working_directory(working_directory)
        pdb.tofile('input.pdb')

        os.system(
            "$AMBERHOME/bin/pdb4amber -i input.pdb -o pdb4amber.pdb "
            "--nohyd --dry &> pdb4amber.log"
        )
        os.system(
            "$AMBERHOME/bin/reduce -build -nuclear pdb4amber.pdb &> reduce.pdb"
        )
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
            nonprot_pdb = pdb_utils.Pdb(f)
        self.nonprot_residues = set(atom['resName']
                                    for atom in nonprot_pdb.atoms)
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
                 working_directory=".propka"):

        utils.set_working_directory(working_directory)
        with open('input.pdb', 'w') as f:
            pdb.to_file(f)
        os.system("propka31 input.pdb &> propka31.log")
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
