import os
import sys


def run(params, template):
    params['center'] = params.get('center', params['ligand'][0]['resSeq'])
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
    tleap_wrapper.top = os.path.abspath(top_file)
    tleap_wrapper.rst = os.path.abspath(rst_file)
