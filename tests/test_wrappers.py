import unittest
import unittest.mock as mock
from enlighten2 import pdb_utils, wrappers
from io import StringIO


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

    @mock.patch('enlighten2.wrappers.utils')
    @mock.patch('enlighten2.wrappers.os.path')
    @mock.patch('enlighten2.wrappers.os')
    def test_antechamber_simple_call(self, mock_os, mock_os_path, mock_utils):
        setup_mock(mock_os, mock_os_path)
        pdb = mock.MagicMock()
        pdb.to_filename = mock.MagicMock()
        antechamber = wrappers.AntechamberWrapper(pdb, 'XXX', 1)

        mock_utils.run_in_shell.assert_has_calls([
            mock.call("/bin/antechamber -i ligand.pdb -fi pdb "
                      "-o XXX.prepc -fo prepc -rn XXX -c bcc -nc 1",
                      'antechamber.out'),
            mock.call(("/bin/parmchk2 -i XXX.prepc -f prepc -o XXX.frcmod"),
                      'parmchk2.out')
        ])


class TestPdb4AmberReduceWrapper(unittest.TestCase):

    @mock.patch('enlighten2.wrappers.utils')
    @mock.patch('enlighten2.wrappers.os.path')
    @mock.patch('enlighten2.wrappers.os')
    def test_pdb4amber_reduce_call(self, mock_os, mock_os_path, mock_utils):
        setup_mock(mock_os, mock_os_path)
        pdb = mock.MagicMock()
        pdb.to_filename = mock.MagicMock()

        # Create a "list" of iterable_mock_open instances to mock properly
        # multiple open() calls in Pdb4AmberReduceWrapper.__init__
        mock_open_files = ['tests/test_files/reduce.pdb',
                           'tests/test_files/pdb4amber_nonprot.pdb',
                           'tests/test_files/pdb4amber_nonprot.pdb']
        mock_open = mock.MagicMock()
        side_effects = []
        for file in mock_open_files:
            with open(file) as f:
                side_effects.append(iterable_mock_open(read_data=f.read())())
        mock_open.side_effect = side_effects

        with mock.patch('enlighten2.wrappers.open', mock_open):
            result = wrappers.Pdb4AmberReduceWrapper(pdb)
        self.assertEqual(len(result.pdb.atoms), 4080)
        self.assertEqual(result.nonprot_residues, {'0RN'})

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

    @mock.patch('enlighten2.wrappers.utils')
    @mock.patch('enlighten2.wrappers.print')
    @mock.patch('enlighten2.wrappers.os.path')
    @mock.patch('enlighten2.wrappers.os')
    def test_propka_call(self, mock_os, mock_os_path, mock_print, mock_utils):
        setup_mock(mock_os, mock_os_path)

        with open('tests/test_files/reduce.pdb') as f:
            pdb = pdb_utils.Pdb(f)
        pdb.to_filename = mock.MagicMock()

        with open('tests/test_files/propka.pka') as f:
            mock_open = iterable_mock_open(read_data=f.read())

        with mock.patch('enlighten2.wrappers.open', mock_open):
            result = wrappers.PropkaWrapper(pdb)
        residues = result.pdb.residues()

        self.assertEqual(len(result.prot_list), 1)
        self.assertEqual(len(result.deprot_list), 0)
        self.assertNotIn('A_189_ASP', residues)
        self.assertIn('A_189_ASH', residues)
        self.assertEqual(len(residues['A_189_ASH']), 12)


class TestTleapWrapper(unittest.TestCase):

    @mock.patch('enlighten2.wrappers.os.path.isfile')
    def test_get_tleap_includes(self, mock_isfile):
        result = {'loadoff test1/res1.off',
                  'loadamberprep test1/res1.prepc',
                  'loadamberprep test2/res2.prepc',
                  'loadamberparams test1/res1.frcmod',
                  'loadamberparams test2/res2.frcmod'}

        FILES = {'test1': ['res1.off', 'res1.prepc', 'res1.frcmod'],
                 'test2': ['res2.prepc', 'res2.frcmod']}

        def side_effect(path):
            dir, name = path.split('/')
            return name in FILES[dir]
        mock_isfile.side_effect = side_effect

        self.assertEqual(
            set(wrappers.get_tleap_includes(['test1', 'test2'],
                                            ['res1', 'res2']).split('\n')),
            result
        )

        with self.assertRaises(FileNotFoundError) as context:
            wrappers.get_tleap_includes(['test1', 'test2'],
                                        ['res1', 'res3'])
        self.assertEqual(str(context.exception),
                         "Cannot find topology (res3.prepc) "
                         "for residue res3. Exiting...")


class TestSanderWrapper(unittest.TestCase):

    @mock.patch('enlighten2.wrappers.utils')
    @mock.patch('enlighten2.wrappers.os.path')
    @mock.patch('enlighten2.wrappers.os')
    def test_sander_call(self, mock_os, mock_os_path, mock_utils):
        setup_mock(mock_os, mock_os_path)
        params = {'bellymask': 'testmask'}

        def side_effect(*args):
            return 'sander/minh_ibelly.in'

        mock_os_path.join.side_effect = side_effect
        mock_os.environ = {'AMBERHOME': 'amberhome'}
        wrappers.SanderWrapper(prefix="test",
                               template="minh_ibelly",
                               crd="crd",
                               prmtop="prmtop",
                               params=params,
                               working_directory='test_dir')

        mock_utils.parse_template.assert_has_calls([
            mock.call('sander/minh_ibelly.in', params)
        ])
        mock_utils.run_at_path.assert_has_calls([
            mock.call("amberhome/bin/sander -O -i test.in -p prmtop -c crd "
                      "-o test.log -r test.rst -ref crd",
                      'test_dir')
        ])
