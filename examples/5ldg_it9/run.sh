#!/bin/sh
../../prep.py 5ldg_it9.sp20.ph7 5ldg.pdb IT9 0 params
../../dynam.py 5ldg_it9.sp20.ph7 -relax
../../dynam.py 5ldg_it9.sp20.ph7
