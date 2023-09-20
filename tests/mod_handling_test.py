import os
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
    
    # strip_source
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
    
    # list_source_mod_files
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
        for src, _ in files:
            if src.endswith('.zip'):
                zips += 1
            elif src.endswith('info.json'):
                infos += 1
            else:
                raise AssertionError(f'Unexpected file type: {src}')
        self.assertEqual(zips, 2, "Unexpected count of leaf files")
        self.assertEqual(infos, 2, "Unexpected count of leaf files")
    
    def test__list_source_mod_files__check_destination(self):
        files = mod_handling.list_source_mod_files(self.res.mods_root, '.')
        for src, dst in files:
            split_pt = 9999
            if src.endswith('.zip'):
                split_pt = -1
            elif src.endswith('info.json'):
                split_pt = -2
            else:
                raise AssertionError(f'Unexpected file type: {src}')
            expected_parts = src.split(os.sep)[split_pt:]
            expected_parts.insert(0, '.')
            expected = os.sep.join(expected_parts)
            self.assertEqual(dst, expected)
    
    # delete_directory_contents
    def test__delete_directory_contents__files(self):
        dir = self.res.build_test_dir()
        pathlib.Path(os.path.join(dir, 'loose_file.txt')).touch()
        pathlib.Path(os.path.join(dir, 'loose_file1.txt')).touch()
        pathlib.Path(os.path.join(dir, 'loose_file2.txt')).touch()
        mod_handling.delete_directory_contents(dir)
        
        contents = os.listdir(dir)
        self.assertEqual(contents, [], 'Files were not deleted')
    
    def test__delete_directory_contents__empty_dirs(self):
        dir = self.res.build_test_dir()
        pathlib.Path(os.path.join(dir, 'empty_dir')).mkdir()
        pathlib.Path(os.path.join(dir, 'empty_dir1')).mkdir()
        pathlib.Path(os.path.join(dir, 'empty_dir2')).mkdir()
        mod_handling.delete_directory_contents(dir)
        
        contents = os.listdir(dir)
        self.assertEqual(contents, [], 'Files were not deleted')
    
    def test__delete_directory_contents__non_empty_dirs(self):
        dir = self.res.build_test_dir()
        pathlib.Path(os.path.join(dir, 'non_empty_dir')).mkdir()
        pathlib.Path(os.path.join(dir, 'non_empty_dir', 'dir_file.txt')).touch()
        pathlib.Path(os.path.join(dir, 'non_empty_dir1')).mkdir()
        pathlib.Path(os.path.join(dir, 'non_empty_dir1', 'dir_file1.txt')).touch()
        mod_handling.delete_directory_contents(dir)
        
        contents = os.listdir(dir)
        self.assertEqual(contents, [], 'Files were not deleted')
    
    def test__delete_directory_contents__combined(self):
        dir = self.res.build_test_dir()
        pathlib.Path(os.path.join(dir, 'loose_file.txt')).touch()
        pathlib.Path(os.path.join(dir, 'empty_dir')).mkdir()
        pathlib.Path(os.path.join(dir, 'non_empty_dir')).mkdir()
        pathlib.Path(os.path.join(dir, 'non_empty_dir', 'dir_file.txt')).touch()
        mod_handling.delete_directory_contents(dir)
        
        contents = os.listdir(dir)
        self.assertEqual(contents, [], 'Files were not deleted')
    
    # merge_mods
    def test__merge_mods__found_only_symlinks(self):
        dir = self.res.build_test_dir()
        mod_handling.merge_mods(self.res.mods_root, dir)
        files = list(pathlib.Path(dir).rglob('*.json'))
        files.extend(list(pathlib.Path(dir).rglob('*.zip')))
        for f in files:
            self.assertTrue(pathlib.Path(f).is_symlink(), f'Leaf is not a symlink: {f}')
            
    def test__merge_mods__file_counts_total(self):
        dir = self.res.build_test_dir()
        mod_handling.merge_mods(self.res.mods_root, dir)
        files = list(pathlib.Path(dir).rglob('*.json'))
        files.extend(list(pathlib.Path(dir).rglob('*.zip')))
        self.assertEqual(len(files), 4, "Unexpected count of leaf files")
            
    def test__merge_mods__file_counts_by_type(self):
        dir = self.res.build_test_dir()
        mod_handling.merge_mods(self.res.mods_root, dir)
        files = list(pathlib.Path(dir).rglob('*.json'))
        files.extend(list(pathlib.Path(dir).rglob('*.zip')))
        zips, infos = 0, 0
        for f in files:
            fs = str(f)
            if fs.endswith('.zip'):
                zips += 1
            elif fs.endswith('info.json'):
                infos += 1
            else:
                raise AssertionError(f'Unexpected file type: {fs}')
        self.assertEqual(zips, 2, "Unexpected count of leaf files")
        self.assertEqual(infos, 2, "Unexpected count of leaf files")

    def test__merge_mods__prior_data_deleted(self):
        dir = self.res.build_test_dir()
        pathlib.Path(os.path.join(dir, 'old_file.zip')).touch()
        pathlib.Path(os.path.join(dir, 'old_file.json')).touch()
        pathlib.Path(os.path.join(dir, 'mod_dir')).mkdir()
        pathlib.Path(os.path.join(dir, 'mod_dir', 'old_file.json')).touch()
        
        mod_handling.merge_mods(self.res.mods_root, dir)
        files = list(pathlib.Path(dir).rglob('*.json'))
        files.extend(list(pathlib.Path(dir).rglob('*.zip')))
        for f in files:
            fs = str(f)
            if fs.endswith('old_file.zip') or fs.endswith('old_file.json'):
                raise AssertionError(f'Old file still found after merge: {fs}')


if __name__ == '__main__':
    unittest.main()