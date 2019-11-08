#!/bin/sh
../../prep.py 1btl_0rn.sp20.ph7 1btl_0rn.pdb 0RN -1
../../dynam.py 1btl_0rn.sp20.ph7 -relax
../../dynam.py 1btl_0rn.sp20.ph7
