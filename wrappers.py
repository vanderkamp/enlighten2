import os
import shutil


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
