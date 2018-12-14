import os
import shutil


class AntechamberWrapper(object):

    def __init__(self,
                 ligand_name,
                 ligand_pdb=None,
                 ligand_charge=0,
                 working_directory=".antechamber",
                 frcmod=None):

        if ligand_pdb is None:
            ligand_pdb = ligand_name + '.pdb'
        if not os.path.isfile(ligand_pdb):
            raise ValueError("PDB file " + ligand_pdb + " not found.")

        if 'AMBERHOME' not in os.environ:
            raise AssertionError("$AMBERHOME not set")

        # Set current working directory to working_directory
        if os.path.exists(working_directory):
            shutil.rmtree(working_directory)
        os.makedirs(working_directory)
        os.chdir(working_directory)

        os.system(
            "$AMBERHOME/bin/antechamber "
            "-i {ligand_pdb} -fi pdb -o {ligand_name}.prepc -fo prepc "
            "-rn {ligand_name} -c bcc -nc {ligand_charge}"
            .format(ligand_pdb=ligand_pdb,
                    ligand_name=ligand_name,
                    ligand_charge=ligand_charge)
        )

        if not (os.path.isfile(ligand_name + '.prepc')):
            raise AssertionError(
                "Antechamber failed to generate {ligand_name}.prepc file"
                .format(ligand_name=ligand_name)
            )

        if frcmod is None:
            os.system("$AMBERHOME/bin/parmchk2 "
                      "-i {ligand_name}.prepc -f prepc -o {ligand_name}.frcmod"
                      .format(ligand_name=ligand_name))
            # TODO: check for ATTN warnings
            self.frcmod = os.path.join(os.getcwd(), ligand_name + '.frcmod')
        else:
            self.frcmod = frcmod

        os.chdir('..')
