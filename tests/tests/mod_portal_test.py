import requests_mock
import unittest
from . import TestResources

from factorio_headless.lib import mod_portal


class TestModPortal__parse_dependency_list(unittest.TestCase):
    def test__single_required(self):
        deps = ["foo"]
        expected = ["foo"]
        actual = mod_portal.parse_dependency_list(deps)
        self.assertEqual(actual, expected)
    
    def test__multiple_required(self):
        deps = ["base", "foo", "bar"]
        expected = ["base", "foo", "bar"]
        actual = mod_portal.parse_dependency_list(deps)
        self.assertEqual(actual, expected)
        
    def test__single_incompatible(self):
        deps = ["! foo"]
        expected = []
        actual = mod_portal.parse_dependency_list(deps)
        self.assertEqual(actual, expected)
        
    def test__single_incompatible_keep_optional(self):
        deps = ["! foo"]
        expected = []
        actual = mod_portal.parse_dependency_list(deps, keep_optional=True)
        self.assertEqual(actual, expected)
        
    def test__multiple_incompatible(self):
        deps = ["! foo", "! bar"]
        expected = []
        actual = mod_portal.parse_dependency_list(deps)
        self.assertEqual(actual, expected)
        
    def test__multiple_incompatible_keep_optional(self):
        deps = ["! foo", "! bar"]
        expected = []
        actual = mod_portal.parse_dependency_list(deps, keep_optional=True)
        self.assertEqual(actual, expected)
        
    def test__single_optional(self):
        deps = ["? foo"]
        expected = []
        actual = mod_portal.parse_dependency_list(deps)
        self.assertEqual(actual, expected)
        
    def test__single_optional_keep(self):
        deps = ["? foo"]
        expected = ["foo"]
        actual = mod_portal.parse_dependency_list(deps, keep_optional=True)
        self.assertEqual(actual, expected)
        
    def test__multiple_optional(self):
        deps = ["? foo", "(?) bar"]
        expected = []
        actual = mod_portal.parse_dependency_list(deps)
        self.assertEqual(actual, expected)
        
    def test__multiple_optional_keep(self):
        deps = ["? foo", "(?) bar"]
        expected = ["foo", "bar"]
        actual = mod_portal.parse_dependency_list(deps, keep_optional=True)
        self.assertEqual(actual, expected)
        
    def test__single_required_no_load_order(self):
        deps = ["~ foo"]
        expected = ["foo"]
        actual = mod_portal.parse_dependency_list(deps)
        self.assertEqual(actual, expected)
        
    def test__multiple_required_no_load_order(self):
        deps = ["~ foo", "~ bar"]
        expected = ["foo", "bar"]
        actual = mod_portal.parse_dependency_list(deps)
        self.assertEqual(actual, expected)
        
    def test__mixed_small(self):
        deps = ["foo", "! bar", "? baz", "(?) qux", "~ quxx"]
        expected = ["foo", "quxx"]
        actual = mod_portal.parse_dependency_list(deps)
        self.assertEqual(actual, expected)
        
    def test__mixed_small_keep_optional(self):
        deps = ["foo", "! bar", "? baz", "(?) qux", "~ quxx"]
        expected = ["foo", "baz", "qux", "quxx"]
        actual = mod_portal.parse_dependency_list(deps, keep_optional=True)
        self.assertEqual(actual, expected)
        
    def test__mixed_big(self):
        deps = [
            "foo", "foo1",
            "! bar", "! bar1",
            "? baz", "? baz1",
            "(?) qux", "(?) qux1",
            "~ quxx", "~ quxx1"
        ]
        expected = ["foo", "foo1", "quxx", "quxx1"]
        actual = mod_portal.parse_dependency_list(deps)
        self.assertEqual(actual, expected)
        
    def test__mixed_big_keep_optional(self):
        deps = [
            "foo", "foo1",
            "! bar", "! bar1",
            "? baz", "? baz1",
            "(?) qux", "(?) qux1",
            "~ quxx", "~ quxx1"
        ]
        expected = ["foo", "foo1", "baz", "baz1", "qux", "qux1", "quxx", "quxx1"]
        actual = mod_portal.parse_dependency_list(deps, keep_optional=True)
        self.assertEqual(actual, expected)


# POC for requests mocking, works well, have to supply all URLs that will get called
# @requests_mock.Mocker()
# class TestModPortal_download_mods(unittest.TestCase):
    # @classmethod
    # def setUpClass(self):
    #     self.res = TestResources(self.__name__)
    
#     @classmethod
#     def tearDownClass(self):
#         self.res.cleanup()
    
#     def test__foobar(self, m: requests_mock.Mocker):
#         mods = ['Avatars'] 
#         m.get(f'https://mods.factorio.com/api/mods/Avatars/full', text='{"releases":[{"released_at":"2023-01-01Z", "info_json": {"dependencies": ["foobar"]}}]}')
#         foo = mod_portal.download_mods(mods, dst_dir=self.res.build_test_dir())
#         self.assertEqual(set(), foo)


if __name__ == '__main__':
    unittest.main()