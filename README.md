Enlighten2
============

**IMPORTANT: This repository contains the source code of the enlighten2 python package 
and the docker image, NOT the PyMOL plugin. The source code for the enlighten2 
PyMOL plugin can be found [here](https://github.com/vanderkamp/enlighten2-pymol).** 

Protocols and tools to run (automated) atomistic simulations of enzyme-ligand systems.

Aimed at:
 
- Experimental biochemists/enzymologists interested in gaining detailed insight into protein-ligand / enzyme-substrate complexes.
- Biomolecular researchers that would like to perform simulations in a high(er)-throughput fashion, e.g. for testing and hypothesis generation

Minimal software requirements:

- [AmberTools18 or later](http://www.ambermd.org) (the manual - Amber18.pdf or later - has instructions for installation)

Several utitilies/programs from AmberTools18 (or later) are used for the majority of tasks.

Additional recommended software requirements:

- propka31 (see the [github site](https://github.com/jensengroup/propka-3.1) or here: www.propka.ki.ku.dk; Required for p*K*a estimation titratable residues, in presence of ligand)


###Download the repository on Linux/UNIX/Mac :   

First ensure that git is installed. Instructions are [here](http://git-scm.com/downloads). 

Command-line:

1) In the right-hand corner of this page, there is a title "HTTPS clone URL" with a URL in a field below it.
   Copy this link 

2) Go to the command line on your Linux/Mac and cd to a suitable location to create the Repository
   Then type:

   git clone https://github.com/vanderkamp/enlighten2.git

   On some UNIX clusters, you may need to use SSH rather than HTTPS to clone the repository.
   This typically means you will also need to add your public ssh key for the cluster (~/.ssh/id_rsa.pub) to your github account here: https://github.com/settings/ssh

   Once the public ssh key is added, you can run:

   git clone git@github.com:vanderkamp/enlighten2.git

3) Prior to running Enlighten through the command line, make sure your environment is set up for the external programs

   For AmberTools, do the following:
   ```bash
   source <full path to amber directory, e.g. /users/me/amber14/>amber.sh
   ```

   For PropKa, ensure that propka31 is in your $PATH (i.e. it is recognised as command from the command-line), e.g. in bash:
   ```bash
   export PATH=$PATH:<path to propka>/propka31
   ```


## Available protocols
### PREP: prep.py
prep.py takes enzyme-ligand pdb file and generates ligand parameters, adds hydrogens, adds solvent (sphere), generates Amber topology/coordinate files.

  Usage:
  ```bash
  prep.py <pdb file> <ligand name> <net ligand charge> [<additional parameters file>]
  ```
- The pdb file should contain at least 1 (non-protein) ligand, WITH all hydrogens added!
- Uses the following AmberTools14 programs: antechamber (& sqm), prmchk2, pdb4amber, reduce, tleap 
- Ideally requires installation of propka31 (and put in $PATH)
