#!/usr/bin/env python3
import os
from wrappers import SanderWrapper
from functools import reduce
from collections import namedtuple


SystemFiles = namedtuple('SystemFiles', ('prmtop', 'crd'))


def run_sander_step(system_files, params):

    if not isinstance(system_files, SystemFiles):
        return system_files
    sander_wrapper = SanderWrapper(prefix=params['name'],
                                   template=params['template'],
                                   crd=system_files.crd,
                                   prmtop=system_files.prmtop,
                                   params=params.get('params', {}),
                                   working_directory=params['name'])
    if sander_wrapper.exit_code:
        return sander_wrapper.prefix
    return sander_wrapper.exit_code or SystemFiles(system_files.prmtop,
                                                   sander_wrapper.output_crd)


def run(prmtop, crd, params):
    result = reduce(run_sander_step, params, SystemFiles(prmtop, crd))
    if isinstance(result, SystemFiles):
        print("sanderflow finished successfully. Final coordinates are in {}"
              .format(result.crd))
        return True, result
    else:
        err_file = os.path.join(os.getcwd(), result, '{}.log'.format(result))
        print("sander failed at step '{}'. Check {} for more information"
              .format(result, err_file))
        return False, result
