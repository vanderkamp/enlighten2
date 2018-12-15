import unittest
from io import StringIO
import pdb


class TestPdb(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.atom_string = ("ATOM    278  HG2 ARG A  36      "
                           "17.074  -2.417  17.463  1.00 11.39"
                           "           H   new")
        cls.parsed_atom = {
            'record': "ATOM",
            'serial': 278,
            'name': "HG2",
            'altLoc': "",
            'resName': "ARG",
            'chainID': "A",
            'resSeq': 36,
            'iCode': "",
            'x': 17.074,
            'y': -2.417,
            'z': 17.463,
            'occupancy': 1.0,
            'tempFactor': 11.39,
            'element': "H",
            'charge': "",
            'extras': " new"
        }
        with open('tests/test_files/full.pdb') as f:
            cls.pdb = pdb.Pdb(f)

    def test_residue_hash(self):
        self.assertEqual(pdb.residue_hash(self.parsed_atom), "A_36_ARG")

    def test_parse_atom(self):
        self.assertEqual(pdb.parse_atom(self.atom_string), self.parsed_atom)

    def test_dump_atom(self):
        atom = pdb.parse_atom(self.atom_string)
        self.assertEqual(pdb.dump_atom(self.parsed_atom), self.atom_string)

    def test_create_pdb_from_file(self):
        self.assertEqual(len(self.pdb.atoms), 2236)
        self.assertEqual(len(self.pdb.residues()), 463)

    def test_dump_pdb_to_file(self):
        result_file = StringIO()
        self.pdb.to_file(result_file)
        result_file.seek(0)
        with open('tests/test_files/only_atoms.pdb', 'r') as pdb_file:
            self.assertEqual(pdb_file.read(), result_file.read())

    def test_get_residues_by_name(self):
        self.assertEqual(len(self.pdb.get_residues_by_name('TRP')), 4)

    def test_copy(self):
        pdb_copy = self.pdb.copy()
        self.assertIsNot(self.pdb, pdb_copy)
        self.assertIsNot(self.pdb.atoms, pdb_copy.atoms)
        self.assertEqual(self.pdb.atoms, pdb_copy.atoms)
