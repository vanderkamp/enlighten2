import os
import shutil
import pdb


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

    def __init__(self,
                 ligand_name,
                 ligand_pdb=None,
                 ligand_charge=0,
                 working_directory=".antechamber",
                 frcmod=None):

        ligand_pdb = ligand_pdb or ligand_name + '.pdb'
        check_file(ligand_pdb)
        check_amberhome()
        set_working_directory(working_directory)

        os.system(
            "$AMBERHOME/bin/antechamber "
            "-i {ligand_pdb} -fi pdb -o {ligand_name}.prepc -fo prepc "
            "-rn {ligand_name} -c bcc -nc {ligand_charge}"
            .format(ligand_pdb=ligand_pdb,
                    ligand_name=ligand_name,
                    ligand_charge=ligand_charge)
        )

        check_file(ligand_name + '.prepc',
                   "Antechamber failed to generate {ligand_name}.prepc file"
                   .format(ligand_name=ligand_name))

        if frcmod is None:
            os.system("$AMBERHOME/bin/parmchk2 "
                      "-i {ligand_name}.prepc -f prepc -o {ligand_name}.frcmod"
                      .format(ligand_name=ligand_name))
            # TODO: check for ATTN warnings
            self.frcmod = os.path.join(os.getcwd(), ligand_name + '.frcmod')
        else:
            self.frcmod = frcmod

        os.chdir('..')


class Pdb4AmberReduceWrapper(object):

    def __init__(self, system_name, system_pdb=None,
                 working_directory=".pdb4amber_reduce"):

        system_pdb = system_pdb or system_name + '.pdb'
        check_file(system_pdb)
        check_amberhome()
        set_working_directory(working_directory)

        os.system(
            "$AMBERHOME/bin/pdb4amber "
            "-i {system_pdb} -o {system_name}_pdb4amber.pdb "
            "--nohyd --dry &> pdb4amber.log"
            .format(system_pdb=system_pdb, system_name=system_name)
        )
        os.system(
            "$AMBERHOME/bin/reduce -build -nuclear "
            "{system_name}_pdb4amber.pdb &> {system_name}_reduce.pdb"
            .format(system_name=system_name)
        )
        with open(system_name + '_reduce.pdb') as f:
            reducePdb = pdb.Pdb(f)
        self.renamed_histidines = get_renamed_histidines(reducePdb)

        os.chdir('..')


def get_renamed_histidines(reducePdb):
    rename_dict = {'no HE2': 'HID',
                   'no HD1': 'HIE',
                   'bothHN': 'HIP'}
    renamed_histidines = {}  # dict of residue_hash: new_name pairs
    for line in reducePdb.other:
        if line[:9] != 'USER  MOD' or line[25:28] != 'HIS':
            continue
        his_name = rename_dict.get(line[39:45])
        if his_name is None:
            continue
        his_hash = pdb.residue_hash({'chainID': line[19],
                                     'resSeq': int(line[20:24]),
                                     'resName': "HIS"})
        renamed_histidines[his_hash] = his_name

    return renamed_histidines
