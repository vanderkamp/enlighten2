import os
import sys
from enlighten2 import pdb_utils


def run(params, template):
    if not params.get('center'):
        center = pdb_utils.atoms_center(params['ligand'])
        params['center'] = ' '.join('{:.3f}'.format(x) for x in center)
    return template.format(**params)


def check(params, tleap_wrapper):
    top_file = "{name}.top".format(**params)
    rst_file = "{name}.rst".format(**params)
    if os.path.isfile(top_file) and os.path.isfile(rst_file):
        print("Generated topology (prmtop) file {}".format(top_file))
        print("Generated coordinate (inpcrd) file {}".format(rst_file))
    else:
        print("Something went wrong, check {}/tleap/tleap.log."
              .format(params['name']), file=sys.stderr)
        return 1
    tleap_wrapper.top = os.path.abspath(top_file)
    tleap_wrapper.rst = os.path.abspath(rst_file)

    central_atom = closest_atom("{name}.pdb".format(**params), params['center'])
    params['export'] = {'central_atom': '{resSeq}@{name}'.format(**central_atom),
                        'solvent_radius': params['solvent_radius']}
    return 0


def closest_atom(pdb_filename, center):
    with open(pdb_filename, 'r') as f:
        return pdb_utils.Pdb(f).closest_atom(center_to_xyz(center))


def center_to_xyz(center):
    return [float(x) for x in center.split()]
