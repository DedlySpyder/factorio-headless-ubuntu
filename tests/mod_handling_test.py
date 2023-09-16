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
    
    def test__strip_source__example_use_case(self):
        file = '/opt/headless_factorio/mods/source/mod_1/info.json'
        src = '/opt/headless_factorio/mods'
        expected = 'mod_1/info.json'
        
        actual = mod_handling.strip_source(file, src)
        self.assertEqual(actual, expected)
    
    def test__strip_source__correct_mod_info(self):
        file = '/root/should_be_removed/mod_1/info.json'
        src = '/root'
        expected = 'mod_1/info.json'
        
        actual = mod_handling.strip_source(file, src)
        self.assertEqual(actual, expected)
    
    def test__strip_source__correct_mod_zip(self):
        file = '/root/should_be_removed/mod_1.zip'
        src = '/root'
        expected = 'mod_1.zip'
        
        actual = mod_handling.strip_source(file, src)
        self.assertEqual(actual, expected)
    
    def test__strip_source__correct_mod_data(self):
        file = '/root/should_be_removed/mod_1/data.lua'
        src = '/root'
        expected = 'mod_1/data.lua'
        
        actual = mod_handling.strip_source(file, src)
        self.assertEqual(actual, expected)
    
    def test__strip_source__correct_mod_deep_file(self):
        file = '/root/should_be_removed/mod_1/foo/bar/baz/buz.lua'
        src = '/root'
        expected = 'mod_1/foo/bar/baz/buz.lua'
        
        actual = mod_handling.strip_source(file, src)
        self.assertEqual(actual, expected)
    
    def test__strip_source__src_endswith_slash(self):
        file = '/root/should_be_removed/file'
        src = '/root/'
        expected = 'file'
        
        actual = mod_handling.strip_source(file, src)
        self.assertEqual(actual, expected)
    
    def test__list_source_mod_files__found_only_files_for_func(self):
        files = mod_handling.list_source_mod_files(self.res.mods_root, '.')
        for f in files:
            self.assertTrue(pathlib.Path(f[0]).is_file(), f'Leaf is not a file: {f}')
            
    def test__list_source_mod_files__file_counts_total(self):
        files = mod_handling.list_source_mod_files(self.res.mods_root, '.')
        self.assertEqual(len(files), 4, "Unexpected count of leaf files")
            
    def test__list_source_mod_files__file_counts_by_type(self):
        files = mod_handling.list_source_mod_files(self.res.mods_root, '.')
        zips, infos = 0, 0
        for f in files:
            if f[0].endswith('.zip'):
                zips += 1
            elif f[0].endswith('info.json'):
                infos += 1
            else:
                raise AssertionError(f'Unexpected file type: {f[0]}')
        self.assertEqual(zips, 2, "Unexpected count of leaf files")
        self.assertEqual(infos, 2, "Unexpected count of leaf files")
        

if __name__ == '__main__':
    unittest.main()