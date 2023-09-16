import pathlib
import unittest
from . import TestResources

from factorio_headless.lib import mod_handling


class TestModHandling(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.res = TestResources('TestModHandling')
    
    @classmethod
    def tearDownClass(self):
        self.res.cleanup()
    
    def test_apply_to_leaves__only_files_for_func(self):
        files: list[str] = []
        def func(s):
            files.append(s)
        mod_handling.apply_to_leaves(self.res.mods_root, func)
        for f in files:
            self.assertTrue(pathlib.Path(f).is_file(), f'Leaf is not a file: {f}')
            
    def test_apply_to_leaves__file_counts_total(self):
        files: list[str] = []
        def func(s):
            files.append(s)
        mod_handling.apply_to_leaves(self.res.mods_root, func)
        self.assertEqual(len(files), 4, "Unexpected count of leaf files")
            
    def test_apply_to_leaves__file_counts_by_type(self):
        files: list[str] = []
        def func(s):
            files.append(s)
        mod_handling.apply_to_leaves(self.res.mods_root, func)
        zips, infos = 0, 0
        for f in files:
            if f.endswith('.zip'):
                zips += 1
            elif f.endswith('info.json'):
                infos += 1
            else:
                raise AssertionError(f'Unexpected file type: {f}')
        self.assertEqual(zips, 2, "Unexpected count of leaf files")
        self.assertEqual(infos, 2, "Unexpected count of leaf files")
        

if __name__ == '__main__':
    unittest.main()