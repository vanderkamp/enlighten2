from itertools import groupby
from copy import deepcopy


class Pdb(object):

    def __init__(self, file=None, atoms=None, ter=[], conect=[], other=[]):

        if file is None and atoms is None:
            raise ValueError('Either file or atoms must be provided')

        self.atoms = []
        self.ter = []
        self.conect = []
        self.other = []

        if file is None:
            self.atoms = deepcopy(atoms)
            self.ter = ter
            self.conect = conect
            self.other = other
            return

        for line in file:
            getattr(self, pdb_line_key(line)).append(line)
        self.atoms = [parse_atom(atom) for atom in self.atoms]
        self.ter = [parse_ter(ter) for ter in self.ter]

    def residues(self):
        """dict of residue_hash: residue_atom_list"""
        return {k: list(v) for k, v in groupby(self.atoms, residue_hash)}

    def get_residues_by_name(self, residue_name):
        return [residue for k, residue in self.residues().items()
                if residue[0]['resName'] == residue_name]

    def to_file(self, file):
        """Writes atoms, TER and CONECT entries. Ignores all the rest."""
        DUMP_CALLBACK = {'ATOM': dump_atom,
                         'HETATM': dump_atom,
                         'TER': dump_ter}
        # Sort atoms with TER entries by resSeq. TER is always the last.
        # If some atoms have no index (extra Hs added by reduce) they go
        # after the "normal" ones.
        for entry in sorted(self.atoms+self.ter,
                            key=lambda x: (x['chainID'],
                                           x['resSeq'],
                                           x['record'],
                                           x['serial'] or 99999999)):
            file.write(DUMP_CALLBACK[entry['record']](entry))
        for entry in self.conect:
            file.write(entry)

    def to_filename(self, filename):
        with open(filename, 'w') as f:
            self.to_file(f)

    def copy(self):
        return Pdb(atoms=self.atoms, ter=self.ter,
                   conect=self.conect, other=self.other)

    def remove_atom(self, atom):
        try:
            self.atoms.remove(atom)
        except ValueError:
            pass

    def closest_atom(self, xyz):
        distances = [dist_sq(atom_xyz(atom), xyz) for atom in self.atoms]
        return self.atoms[distances.index(min(distances))]


def residue_hash(atom):
    """Uniquely identifies the residue atom belongs to"""
    return '_'.join([str(atom[key])
                     for key in ['chainID', 'resSeq', 'resName']])


def modify_atoms(atoms, key, value):
    for atom in atoms:
        atom[key] = value


def find_atom(atoms, condition):
    """Return first atom in atoms that fulfills condition"""
    return next(atom for atom in atoms if condition(atom))


def atoms_center(atoms):
    """Returns the geometric center of a group of atoms"""
    n = len(atoms)
    return [sum(x)/n for x in zip(*(atom_xyz(atom) for atom in atoms))]


def dist_sq(vec1, vec2):
    return sum((a-b)**2 for a, b in zip(vec1, vec2))


def atom_xyz(atom):
    return atom['x'], atom['y'], atom['z']


def pdb_line_key(line):
    KEY_DICT = {'ATOM  ': 'atoms',
                'HETATM': 'atoms',
                'TER   ': 'ter',
                'CONECT': 'conect'}
    return KEY_DICT.get(line[:6], 'other')


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
        'extras': atom_line[80:] or '\n'
    }


def parse_ter(ter_line):
    """
    Based on official PDB format from
    http://www.wwpdb.org/documentation/file-format-content/format33/sect9.html
    """
    return {
        'record': ter_line[:6].strip(),
        'serial': int(ter_line[6:11].strip()) if ter_line[6:11].strip() else '',
        'resName': ter_line[17:20].strip(),
        'chainID': ter_line[21].strip() if len(ter_line) > 21 else '',
        'resSeq': int(ter_line[22:26].strip()) if ter_line[22:26].strip() else '',
        'iCode': ter_line[26].strip() if len(ter_line) > 26 else '',
        'extras': ter_line[27:] or '\n'
    }


def dump_atom(atom):
    name_format = "{name:>4}" if len(atom['name']) > 2 else " {name:<3}"
    return ("{record:6}{serial:5} " + name_format + "{altLoc:1}"
            "{resName:>3} {chainID:1}{resSeq:4}{iCode:1}"
            "   {x:8.3f}{y:8.3f}{z:8.3f}{occupancy:6.2f}"
            "{tempFactor:6.2f}          {element:>2}"
            "{charge:>2}{extras}").format(**atom)


def dump_ter(ter):
    return ("{record:6}{serial:5} {resName:>8} "
            "{chainID:1}{resSeq:4}{iCode:1}{extras}"
            .format(**ter))
