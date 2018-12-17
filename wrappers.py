import os
import shutil
import pdb_utils


def check_amberhome():
    if 'AMBERHOME' not in os.environ:
        raise AssertionError("$AMBERHOME not set")


def check_file(name, message=None):
    if not os.path.isfile(name):
        raise FileNotFoundError(message or "File " + name + " not found.")


def set_working_directory(working_directory):
    if os.path.exists(working_directory):
        shutil.rmtree(working_directory)
    os.makedirs(working_directory)
    os.chdir(working_directory)


class AntechamberWrapper(object):

    def __init__(self, pdb, name, charge=0,
                 working_directory=".antechamber", frcmod=None):

        check_amberhome()
        set_working_directory(working_directory)
        pdb.tofile('ligand.pdb')

        os.system(
            "$AMBERHOME/bin/antechamber "
            "-i ligand.pdb -fi pdb -o {name}.prepc -fo prepc "
            "-rn {name} -c bcc -nc {charge}"
            .format(name=name, charge=charge)
        )

        check_file(name + '.prepc',
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

        pdb.tofile('input.pdb')
        check_amberhome()
        set_working_directory(working_directory)

        os.system(
            "$AMBERHOME/bin/pdb4amber -i input.pdb -o pdb4amber.pdb "
            "--nohyd --dry &> pdb4amber.log"
        )
        os.system(
            "$AMBERHOME/bin/reduce -build -nuclear pdb4amber.pdb &> reduce.pdb"
        )

        with open('reduce.pdb') as f:
            self.renamed_histidines = get_renamed_histidines(pdb_utils.Pdb(f))

        os.chdir('..')


def get_renamed_histidines(pdb):
    rename_dict = {'no HE2': 'HID',
                   'no HD1': 'HIE',
                   'bothHN': 'HIP'}
    renamed_histidines = {}  # dict of residue_hash: new_name pairs
    for line in pdb.other:
        if line[:9] != 'USER  MOD' or line[25:28] != 'HIS':
            continue
        his_name = rename_dict.get(line[39:45])
        if his_name is None:
            continue
        his_hash = pdb_utils.residue_hash({'chainID': line[19],
                                           'resSeq': int(line[20:24]),
                                           'resName': "HIS"})
        renamed_histidines[his_hash] = his_name

    return renamed_histidines
