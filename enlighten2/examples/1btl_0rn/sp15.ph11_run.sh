#!/bin/sh
../../prep.py 1btl_0rn.sp15.ph11 1btl_0rn.pdb 0RN -1 sp15.ph11_params
../../dynam.py 1btl_0rn.sp15.ph11 -relax
../../dynam.py 1btl_0rn.sp15.ph11 
