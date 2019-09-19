import os
import sys


def run(params, template):
    params['center'] = '{resSeq}.{name}'.format(**params['ligand'][0])
    return template.format(**params)


def check(params):
    top_file = "{name}.top".format(**params)
    rst_file = "{name}.rst".format(**params)
    if os.path.isfile(top_file) and os.path.isfile(rst_file):
        print("Generated topology (prmtop) file {}".format(top_file))
        print("Generated coordinate (inpcrd) file {}".format(rst_file))
    else:
        print("Something went wrong, check {}/tleap/tleap.log."
              .format(params['name']), file=sys.stderr)
