#!/usr/bin/env python3
import argparse
import json
from enlighten2 import pdb_utils, wrappers, utils
import shutil
import sys
import os


def get_ligand_atoms(pdb, ligand_name, ligand_index):

    ligands = pdb.get_residues_by_name(ligand_name)
    if len(ligands) == 0:
        raise ValueError("No ligands found")

    if ligand_index > len(ligands):
        raise ValueError("ligand_index is larger than the number of ligands")

    ligand_atoms = ligands[ligand_index - 1]
    if len(ligands) > 1:
        print("More than one ligand detected. Using coordinates from the ligand"
              " with chainID={} and resSeq={}"
              .format(ligand_atoms[0]['chainID'], ligand_atoms[0]['resSeq']))

    return ligand_atoms


def run_propka(pdb, ph, ph_offset):
    if shutil.which('propka31'):
        return wrappers.PropkaWrapper(pdb, ph, ph_offset).pdb
    else:
        print("propka31 cannot be found in $PATH.\n"
              "WARNING: all ASP/GLU will be treated as unprotonated.")
        return pdb


def main():

    parser = argparse.ArgumentParser(
        description=""
                    "Prepares the simulation system by performing the following actions:\n"
                    " - ligand parameterisation (with antechamber/prmchk2)\n"
                    " - pdb protonation (apart from ligands, they need to "
                    "   be protonated already!)\n"
                    " - tleap to solvate and write starting parm7/rst7 (top/rst)\n\n",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("name", help="name of the job")
    parser.add_argument("pdb", help="protonated PDB file",
                        type=argparse.FileType())
    parser.add_argument("ligand",
                        help="name of the residue to be used as the ligand")
    parser.add_argument("charge", help="charge of the ligand", type=int)
    parser.add_argument("params", help="JSON file with advanced parameters",
                        type=argparse.FileType(), nargs='?')

    args = parser.parse_args()

    job_name = args.name
    ligand_name = args.ligand
    ligand_charge = args.charge

    params = {
        'antechamber': {
            'ligand': args.ligand,
            'charge': args.charge,
            'ligand_chainID': "L",
            'ligand_index': 1,
        },
        'propka': {
            'with_propka': True,
            'ph': 7.0,
            'ph_offset': 0.7,
        },
        'tleap': {
            'template': 'sphere',
            'solvent_radius': 20.0,
            'solvent_closeness': 0.75,
            'include': []
        }
    }

    if args.params is not None:
        params = utils.merge_dicts_of_dicts(params, json.load(args.params))
        args.params.close()
        params['tleap']['include'] = [os.path.abspath(path)
                                      for path in params['tleap']['include']]

    if os.path.exists(job_name):
        print("It appears you've already (attempted to) run prep.py with {0}. "
              "Delete folder {0} or rename pdb if you want to run it again."
              .format(job_name), file=sys.stderr)
        sys.exit(1)

    print("Starting PREP protocol in {}/".format(job_name))
    sys.stdout.flush()
    utils.set_working_directory(job_name)

    pdb = pdb_utils.Pdb(args.pdb)
    ligand_index = params['antechamber']['ligand_index']
    ligand_atoms = get_ligand_atoms(pdb, ligand_name, ligand_index)

    # Only generate ligand frcmod if it is not found in include paths
    ligand_frcmod = utils.file_in_paths(ligand_name + '.frcmod',
                                        params['tleap']['include'])
    antechamber = wrappers.AntechamberWrapper(
        pdb_utils.Pdb(atoms=ligand_atoms), ligand_name, ligand_charge,
        create_frcmod=ligand_frcmod is None
    )
    sys.stdout.flush()
    if ligand_frcmod is None:
        params['tleap']['include'].append(antechamber.working_directory)

    # Change ligand chain ID to ligand_chainID
    ligand_chainID = params['antechamber']['ligand_chainID']
    pdb_utils.modify_atoms(ligand_atoms, 'chainID', ligand_chainID)

    # Run pdb4amber and reduce
    reduceResults = wrappers.Pdb4AmberReduceWrapper(pdb)
    sys.stdout.flush()
    pdb = reduceResults.pdb

    # Run propka31 if requested and found
    if params['propka']['with_propka']:
        pdb = run_propka(pdb=pdb,
                         ph=params['propka']['ph'],
                         ph_offset=params['propka']['ph_offset'])
    sys.stdout.flush()

    ligand = pdb.get_residues_by_name(ligand_name)[ligand_index-1]
    params['tleap']['name'] = os.path.basename(job_name)
    params['tleap']['pdb'] = pdb
    params['tleap']['ligand'] = ligand
    tleap = wrappers.TleapWrapper(params['tleap']['template'],
                                  params['tleap']['include'],
                                  reduceResults.nonprot_residues,
                                  params['tleap'])
    sys.stdout.flush()
    os.system("cp {} .".format(tleap.top))
    os.system("cp {} .".format(tleap.rst))
    print("Finished PREP protocol.")


if __name__ == '__main__':
    main()
