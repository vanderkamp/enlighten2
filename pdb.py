from itertools import groupby


class Pdb(object):

    def __init__(self, file=None, atoms=None):

        if file is None and atoms is None:
            raise ValueError('Either file or atoms must be provided')

        if file is None:
            self.atoms = atoms
        # ignores everything that is not ATOM or HETATM
        self.atoms = [parse_atom(line) for line in file
                      if any(x in line[:6] for x in ['ATOM', 'HETATM'])]

    def residues(self):
        """list of atom lists from each residue"""
        return {k: list(v) for k, v in groupby(self.atoms, _residue_hash)}

    def get_residues_by_name(self, residue_name):
        return [residue for k, residue in self.residues().items()
                if residue[0]['resName'] == residue_name]

    def to_file(self, file):
        dump_atoms_to_file(file, self.atoms)


def _residue_hash(atom):
    """Uniquely identifies the residue atom belongs to"""
    return '_'.join([str(atom[key])
                     for key in ['chainID', 'resSeq', 'resName']])


def parse_atom(atom_line):
    """
    Based on official PDB format from
    http://www.wwpdb.org/documentation/file-format-content/format33/sect9.html
    """
    return {
        'record': atom_line[:6].strip(),
        'serial': int(atom_line[6:11].strip()),
        'name': atom_line[12:16].strip(),
        'altLoc': atom_line[16].strip(),
        'resName': atom_line[17:20].strip(),
        'chainID': atom_line[21].strip(),
        'resSeq': int(atom_line[22:26]),
        'iCode': atom_line[26].strip(),
        'x': float(atom_line[30:38]),
        'y': float(atom_line[38:46]),
        'z': float(atom_line[46:54]),
        'occupancy': float(atom_line[54:60]),
        'tempFactor': float(atom_line[60:66]),
        'element': atom_line[76:78].strip(),
        'charge': atom_line[78:80].strip(),
        'extras': atom_line[80:]
    }


def dump_atom(atom):
    name_format = "{name:>4}" if len(atom['name']) > 2 else " {name:<3}"
    return ("{record:6}{serial:5} " + name_format + "{altLoc:1}"
            "{resName:>3} {chainID:1}{resSeq:4}{iCode:1}"
            "   {x:8.3f}{y:8.3f}{z:8.3f}{occupancy:6.2f}"
            "{tempFactor:6.2f}          {element:>2}"
            "{charge:>2}{extras}").format(**atom)


def dump_atoms_to_file(file, atoms):
    for atom in atoms:
        file.write(dump_atom(atom))
