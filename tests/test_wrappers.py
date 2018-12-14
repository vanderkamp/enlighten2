import unittest
import unittest.mock as mock
import wrappers


class TestAntechamberWrapper(unittest.TestCase):

    @mock.patch('wrappers.os.path')
    @mock.patch('wrappers.os')
    def test_antechamber_simple_call(self, mock_os, mock_os_path):
        mock_os_path.exists.return_value = False
        mock_os_path.isfile.return_value = True
        mock_os.environ = {'AMBERHOME': ""}
        mock_os.getcwd.return_value = '.'
        antechamber = wrappers.AntechamberWrapper('XXX')
        mock_os.system.assert_called_with(
            "$AMBERHOME/bin/antechamber -i XXX.pdb -fi pdb "
            "-o XXX.prepc -fo prepc -rn XXX -c bcc -nc 0"
        )
        mock_os_path.join.assert_called_with('.', 'XXX.frcmod')
