import unittest
import unittest.mock as mock
import wrappers
import pdb


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
        antechamber = wrappers.AntechamberWrapper('XXX')

        mock_os.system.assert_has_calls([
            mock.call("$AMBERHOME/bin/antechamber -i XXX.pdb -fi pdb "
                      "-o XXX.prepc -fo prepc -rn XXX -c bcc -nc 0"),
            mock.call("$AMBERHOME/bin/parmchk2 -i XXX.prepc "
                      "-f prepc -o XXX.frcmod")
        ])
        mock_os_path.join.assert_called_with('.', 'XXX.frcmod')


class TestPdb4AmberReduceWrapper(unittest.TestCase):

    @mock.patch('wrappers.open')
    @mock.patch('wrappers.os.path')
    @mock.patch('wrappers.os')
    def test_pdb4amber_reduce_call(self, mock_os, mock_os_path, mock_open):
        setup_mock(mock_os, mock_os_path)
        pdb4AmberReduce = wrappers.Pdb4AmberReduceWrapper(
            system_name='XXX',
            system_pdb='XXX_renamed_ligand.pdb'
        )
        mock_os.system.assert_has_calls([
            mock.call("$AMBERHOME/bin/pdb4amber -i XXX_renamed_ligand.pdb "
                      "-o XXX_pdb4amber.pdb --nohyd --dry &> pdb4amber.log"),
            mock.call("$AMBERHOME/bin/reduce -build -nuclear "
                      "XXX_pdb4amber.pdb &> XXX_reduce.pdb")
        ])

    def test_get_renamed_histidines(self):
        renamed_histidines = {'A_262_HIS': 'HIE',
                              'A_1_HIS': 'HIE',
                              'A_71_HIS': 'HIE',
                              'A_87_HIS': 'HID',
                              'A_128_HIS': 'HIE',
                              'A_133_HIS': 'HIE'}
        with open('tests/test_files/reduce.pdb') as f:
            reducePdb = pdb.Pdb(f)
        self.assertEqual(wrappers.get_renamed_histidines(reducePdb),
                         renamed_histidines)
