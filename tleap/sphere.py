import os


def run(params, template):
    params['center'] = '{resSeq}.{name}'.format(**params['ligand'][0])
    return template.format(**params)


def check(params):
    top_file = "{name}.sp{solvent_radius:.0f}.top".format(**params)
    rst_file = "{name}.sp{solvent_radius:.0f}.rst".format(**params)
    if os.path.isfile(top_file) and os.path.isfile(rst_file):
        print("Generated topology (prmtop) file {}".format(top_file))
        print("Generated coordinate (inpcrd) file {}".format(rst_file))
    else:
        print("Something went wrong, check {}/tleap.log."
              .format(params['name']))
