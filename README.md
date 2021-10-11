Enlighten2
============

**IMPORTANT: This repository contains the source code of the enlighten2 python package 
and the docker image, NOT the PyMOL plugin. The source code for the enlighten2 
PyMOL plugin can be found [here](https://github.com/vanderkamp/enlighten2-pymol).**

**For the installation instructions for PyMOL plugin and usage tutorials, please, visit the 
[project webpage](https://enlighten2.github.io).**

**The development version of the package with the latest bugfixes can be found on 
[dev branch](https://github.com/vanderkamp/enlighten2/tree/dev).**

Protocols and tools to run (automated) atomistic simulations of enzyme-ligand systems.

Aimed at:
 
- Experimental biochemists/enzymologists interested in gaining detailed insight into protein-ligand / enzyme-substrate complexes.
- Biomolecular researchers that would like to perform simulations in a high(er)-throughput fashion, e.g. for testing and hypothesis generation

Minimal software requirements:

- [AmberTools18 or later](https://ambermd.org/AmberTools.php) (the manual - Amber18.pdf or later - has instructions for installation)

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
   This typically means you will also need to add your public ssh key for the cluster (~/.ssh/id_rsa.pub) to your github 
   account here: https://github.com/settings/ssh

   Once the public ssh key is added, you can run:

   git clone git@github.com:vanderkamp/enlighten2.git

3) Prior to running Enlighten through the command line, make sure your environment is set up for the external programs

   For AmberTools, do the following:
   ```bash
   source <full path to amber directory, e.g. /users/me/amber18/>amber.sh
   ```

   For PropKa, ensure that propka31 is in your $PATH (i.e. it is recognised as command from the command-line), e.g. in bash:
   ```bash
   export PATH=$PATH:<path to propka>/propka31
   ```
   
## Using as a python package
Enlighten2 package is based on a set of wrapper classes for various AmberTools programs. When an instance of a wrapper 
class is initialized, it passes a protein(-substrate complex) structure to a corresponding program and stores the results 
of the execution.

### Pdb class
A molecular structure is represented in Enlighten2 as an instance of `Pdb` class in `pdb_utils` module. It can be created
either from a PDB file:
```python
    with open('XXXX.pdb') as f:
        pdb = pdb_utils.Pdb(f)
```
or from a set of atoms obtained from another `Pdb` instance:
```python
    ligand_atoms = pdb.get_residues_by_name('LIG')[0]
    ligand = pdb_utils.Pdb(ligand_atoms)
```
All the wrappers (except `SanderWrapper`) require a pdb object to be initialized. 

### `wrappers.AntechamberWrapper`
takes a ligand pdb object and along with the desired ligand residue name and the charge,
run parameterization with antechamber using bcc charges and write out the frcmod file using parmchk2. Full path to the 
directory containing prepc and frcmod files is stored in `working_directory` field.
```python
    antechamber_wrapper = wrappers.AntechanberWrapper(ligand_pdb, name='LIG', charge=0)
```

### `wrappers.Pdb4AmberReduceWrapper`
takes a pdb object of a protein(-substrate complex), runs pdb preparation with pdb4amber
and then adds hydrogen atoms with reduce. It also assigns proper names to histidines depending on their protonation state 
and removes the hydrogen atoms added to all non-protein residues. The resulting pdb is stored as a Pdb object in 
`pdb` field.
```python
    pbd4amber_reduce_wrapper = wrappers.Pdb4AmberReduceWrapper(pdb)
    result = pbd4amber_reduce_wrapper.pdb    
```

### `wrappers.PropkaWrapper`
Runs `propka31` on the provided pdb, renames the protonated/deprotonated residues according to the results and removes
hydrogens when needed. The resulting pdb is stored as a Pdb object in `pdb` field. Requires `propka31` to be available 
in the $PATH. Accepts target pH (default 7.0) and pH_offset (default 0.7) as arguments.
```python
    propka_wrapper = wrappers.PropkaWrapper(pdb, ph=9.0, ph_offset=0.5)
    result = propka_wrapper.pdb
```

### `wrappers.TleapWrapper`
runs system preparation using `tleap` based on a template input and a dictionary of parameters. Accepts a list of 
non-protein residues and a list of directories to look for corresponding prepc/frcmod files.
directories. At the moment only "sphere" template is available. Additional templates must are stored in enlighten2/tleap/ 
directory named `<template name>.in`. For each template, a correspoding python module `<template name>.py` with functions 
`run` and `check` must be provided. `run` is responsible for converting the dictionary of parameters and the template to 
a valid tleap input. `check` is executed after tleap to validate the output and do any necessary postprocessing. See 
tleap/sphere.py for an example. 

### Typical usage
The most common use case for enlighten2 package is to parse the pdb file with pdb4amber, reduce and propka as following:
```python
    with open('XXXX.pdb') as f:
        pdb = pdb_utils.Pdb(f)
    pdb4amber_pdb = wrappers.Pdb4AmberReduceWrapper(pdb).pdb
    propka_pdb = wrappers.PropkaWrapper(pdb4amber_pdb, ph=9.0).pdb
    propka_pdb.to_filename('result.pdb')
```
`AntechamberWrapper` is only responsible for running antechamber/parmchk2 with predefined arguments and therefore gives
little advantage over simply running the corresponding tools from a shell. The tleap usage is usually system specific, 
so the `TleapWrapper` is also not expected to be used manually. These two wrapper classes are mainly responsible for 
system preparation when using enlighten2 from a PyMOL plugin.

## Available protocols
The following predefined protocols are designed to be used through a PyMOL plugin, but can also be used from a command 
line. 
### PREP: prep.py

prep.py takes enzyme-ligand pdb file and generates ligand parameters, adds hydrogens, adds solvent (sphere), generates 
Amber topology/coordinate files.

  Usage:
  ```bash
  prep.py <system name> <pdb file> <ligand name> <net ligand charge> [<additional parameters file>]
  ```
- The pdb file should contain at least 1 (non-protein) ligand, WITH all hydrogens added!
- Uses the following AmberTools programs: antechamber (& sqm), prmchk2, pdb4amber, reduce, tleap 
- Ideally requires installation of propka31 (and put in $PATH)
- additional parameters are provided as a json file with the following fields:
  ```
  {
    "antechamber": {
        "ligand": <Ligand name>,
        "charge": <Ligand charge>,
        "ligand_chainID": <Ligand chain id> (default:  "L"),
        "ligand_index": <Index of the ligand in the pdb> (default: 1)
    },
    "propka": {
        "with_propka": <Whether to use propka> (default: True),
        "ph": <pH of simulation> (default: 7.0),
        "ph_offset": <allowed pKa-pH difference> (default:  0.7)
    },
    "tleap": {
        "template": <tleap input template> (default: "sphere"),        
        "solvent_radius": <Solvent sphere size> (default: 20.0),
        "solvent_closeness": <Minimum solute-solvent distance> (default: 0.75),
        "include": <Directories to look for frcmod/prepc files> (default: [])
    }
  }  
  ```

### DYNAM: dynam.py
dynam.py runs a predefined relaxation/production MD protocol for a system created with PREP.

  Usage:
  ```bash
  dynam.py <system name> [-relax] [<additional parameters file>]
  ```

- Uses sander program from AmberTools
- runs short relaxation protocol when used with -relax argument, 
else runs a longer production MD
- additional parameters are provided as a json file with the following fields:
  ```
  {
    "steps": <Number of MD steps> (default: 25000),
    "solvent_radius": <radius of the flexible sphere of atoms>,
    "central_atom": <center of the flexible sphere of atoms>
  }  
  ```
 
 Note that the parameters solvent_radius and central_atom are usually provided by PREP 
 output and therefore are not required.
