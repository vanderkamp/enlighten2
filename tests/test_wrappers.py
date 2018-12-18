import unittest
import unittest.mock as mock
import wrappers
import pdb_utils


def iterable_mock_open(_mock=None, read_data=''):
    """
    Returns modified mock_open object that supports iteration
    (iter, next, etc.)
    """
    mock_open = mock.mock_open(mock=_mock, read_data=read_data)
    mock_open.return_value.__iter__ = lambda self: self
    mock_open.return_value.__next__ = (lambda self:
                                       next(iter(self.readline, '')))
    return mock_open


def setup_mock(mock_os, mock_os_path):
    mock_os_path.exists.return_value = False
    mock_os_path.isfile.return_value = True
    mock_os.environ = {'AMBERHOME': ""}
    mock_os.getcwd.return_value = '.'


class TestAntechamberWrapper(unittest.TestCase):

    @mock.patch('wrappers.os.path')
    @mock.patch('wrappers.os')
    def test_antechamber_simple_call(self, mock_os, mock_os_path):
        setup_mock(mock_os, mock_os_path)
        pdb = mock.MagicMock()
        pdb.tofile = mock.MagicMock()
        antechamber = wrappers.AntechamberWrapper(pdb, 'XXX', 1)

        mock_os.system.assert_has_calls([
            mock.call("$AMBERHOME/bin/antechamber -i ligand.pdb -fi pdb "
                      "-o XXX.prepc -fo prepc -rn XXX -c bcc -nc 1"),
            mock.call("$AMBERHOME/bin/parmchk2 -i XXX.prepc "
                      "-f prepc -o XXX.frcmod")
        ])
        mock_os_path.join.assert_called_with('.', 'XXX.frcmod')


class TestPdb4AmberReduceWrapper(unittest.TestCase):

    @mock.patch('wrappers.os.path')
    @mock.patch('wrappers.os')
    def test_pdb4amber_reduce_call(self, mock_os, mock_os_path):
        setup_mock(mock_os, mock_os_path)
        pdb = mock.MagicMock()
        pdb.tofile = mock.MagicMock()
        with open('tests/test_files/reduce.pdb') as f:
            mock_open = iterable_mock_open(read_data=f.read())
        with mock.patch('wrappers.open', mock_open):
            result = wrappers.Pdb4AmberReduceWrapper(pdb)
        self.assertEqual(len(result.pdb.atoms), 4080)

    def test_get_renamed_histidines(self):
        renamed_histidines = {'A_262_HIS': 'HIE',
                              'A_1_HIS': 'HIE',
                              'A_71_HIS': 'HIE',
                              'A_87_HIS': 'HID',
                              'A_128_HIS': 'HIE',
                              'A_133_HIS': 'HIE'}
        with open('tests/test_files/reduce.pdb') as f:
            reducePdb = pdb_utils.Pdb(f)
        self.assertEqual(wrappers.get_renamed_histidines(reducePdb),
                         renamed_histidines)


class TestPropkaWrapper(unittest.TestCase):

    def test_line_to_pka_entry(self):
        self.assertEqual(
            wrappers.line_to_pka_entry("   ARG 215 A    12.39      12.50    "),
            {'resName': 'ARG',
             'resSeq': 215,
             'chainID': 'A',
             'pKa': 12.39,
             'model-pKa': 12.50}
        )

    def test_parse_propka_output(self):
        with open('tests/test_files/propka.pka') as f:
            output = wrappers.parse_propka_output(f)
        self.assertEqual(len(output), 76)
        self.assertEqual(
            output['A_154_ASP'],
            {'resName': 'ASP',
             'resSeq': 154,
             'chainID': 'A',
             'pKa': 4.24,
             'model-pKa': 3.80}
        )

    @mock.patch('wrappers.print')
    @mock.patch('wrappers.os.path')
    @mock.patch('wrappers.os')
    def test_propka_call(self, mock_os, mock_os_path, mock_print):
        setup_mock(mock_os, mock_os_path)

        with open('tests/test_files/reduce.pdb') as f:
            pdb = pdb_utils.Pdb(f)
        pdb.to_file = mock.MagicMock()

        with open('tests/test_files/propka.pka') as f:
            mock_open = iterable_mock_open(read_data=f.read())

        with mock.patch('wrappers.open', mock_open):
            result = wrappers.PropkaWrapper(pdb)
        residues = result.pdb.residues()

        self.assertEqual(len(result.prot_list), 1)
        self.assertEqual(len(result.deprot_list), 0)
        self.assertNotIn('A_189_ASP', residues)
        self.assertIn('A_189_ASH', residues)
        self.assertEqual(len(residues['A_189_ASH']), 12)
