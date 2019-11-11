import unittest
import unittest.mock as mock
from enlighten2 import utils


class TestUtils(unittest.TestCase):

    @mock.patch('enlighten2.utils.os.path.isfile')
    def test_file_in_paths(self, mock_isfile):
        DIRS = ['empty_dir', 'dir1', 'dir2']
        VALUES = {'empty_dir/file1': False,
                  'empty_dir/file2': False,
                  'dir1/file1': True,
                  'dir1/file2': False,
                  'dir2/file1': True,
                  'dir2/file2': False}

        def side_effect(path):
            return VALUES[path]

        mock_isfile.side_effect = side_effect
        self.assertEqual(utils.file_in_paths('file1', DIRS), 'dir1/file1')
        self.assertEqual(utils.file_in_paths('file2', DIRS), None)

    def test_merge_dicts_of_dicts(self):
        dict1 = {'a': {'a': 1, 'c': 3},
                 'c': {'b': 2}}
        dict2 = {'a': {'b': 2, 'c': 4},
                 'b': {'a': 1}}
        result = {'a': {'a': 1, 'b': 2, 'c': 4},
                  'b': {'a': 1},
                  'c': {'b': 2}}
        self.assertEqual(utils.merge_dicts_of_dicts(dict1, dict2), result)
