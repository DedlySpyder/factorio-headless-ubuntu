import datetime
import requests_mock
import unittest

from . import TestResources

from factorio_headless.lib import mod_portal


OLD_DATETIME = datetime.datetime.fromisoformat('2000-01-01')
def generate_versions(data: list[list[str]]) -> list[dict]:
    vers = []
    for i, d in enumerate(data):
        vers.append({
            "version": str(i),
            "released_at": f'{OLD_DATETIME + datetime.timedelta(days=i)}Z',
            "info_json": {
                "dependencies": d
            }
        })
    return vers
    
def generate_mod_data(name: str, releases: list[list[str]]) -> dict:
    data = {}
    data['title'] = name
    data['name'] = name
    data['releases'] = generate_versions(releases)
    return data


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


class TestModPortal__get_latest_version(unittest.TestCase):
    def test__single_version_no_deps(self):
        mod_data = generate_mod_data('mod_name', [[]])
        latest_version = mod_portal.get_latest_version(mod_data)
        self.assertEqual(latest_version['version'], '0', f'Unexpected latest version returned: {latest_version}')
    
    def test__single_version_single_dep(self):
        mod_data = generate_mod_data('mod_name', [["foo"]])
        latest_version = mod_portal.get_latest_version(mod_data)
        self.assertEqual(latest_version['version'], '0', f'Unexpected latest version returned: {latest_version}')
    
    def test__single_version_multiple_deps(self):
        mod_data = generate_mod_data('mod_name', [["foo", "bar", "baz"]])
        latest_version = mod_portal.get_latest_version(mod_data)
        self.assertEqual(latest_version['version'], '0', f'Unexpected latest version returned: {latest_version}')
    
    def test__multiple_versions_no_deps(self):
        mod_data = generate_mod_data('mod_name', [[], [], []])
        latest_version = mod_portal.get_latest_version(mod_data)
        self.assertEqual(latest_version['version'], '2', f'Unexpected latest version returned: {latest_version}')
    
    def test__multiple_versions_single_dep(self):
        mod_data = generate_mod_data('mod_name', [["foo"], ["bar"], ["baz"]])
        latest_version = mod_portal.get_latest_version(mod_data)
        self.assertEqual(latest_version['version'], '2', f'Unexpected latest version returned: {latest_version}')
    
    def test__multiple_versions_multiple_deps(self):
        mod_data = generate_mod_data('mod_name', [["foo", "bar", "baz"], ["qux", "quxx", "quxxx"], ["a", "b", "c"]])
        latest_version = mod_portal.get_latest_version(mod_data)
        self.assertEqual(latest_version['version'], '2', f'Unexpected latest version returned: {latest_version}')
    
    def test__multiple_versions_no_deps_reversed(self):
        mod_data = generate_mod_data('mod_name', [[], [], []])
        mod_data['releases'].reverse()
        latest_version = mod_portal.get_latest_version(mod_data)
        self.assertEqual(latest_version['version'], '2', f'Unexpected latest version returned: {latest_version}')
    
    def test__multiple_versions_single_dep_reversed(self):
        mod_data = generate_mod_data('mod_name', [["foo"], ["bar"], ["baz"]])
        mod_data['releases'].reverse()
        latest_version = mod_portal.get_latest_version(mod_data)
        self.assertEqual(latest_version['version'], '2', f'Unexpected latest version returned: {latest_version}')
    
    def test__multiple_versions_multiple_deps_reversed(self):
        mod_data = generate_mod_data('mod_name', [["foo", "bar", "baz"], ["qux", "quxx", "quxxx"], ["a", "b", "c"]])
        mod_data['releases'].reverse()
        latest_version = mod_portal.get_latest_version(mod_data)
        self.assertEqual(latest_version['version'], '2', f'Unexpected latest version returned: {latest_version}')
    
    def test__multiple_versions_no_deps_strange_order(self):
        mod_data = generate_mod_data('mod_name', [[], [], []])
        mod_data['releases'] = [mod_data['releases'][1], mod_data['releases'][2], mod_data['releases'][0]]
        latest_version = mod_portal.get_latest_version(mod_data)
        self.assertEqual(latest_version['version'], '2', f'Unexpected latest version returned: {latest_version}')
    
    def test__multiple_versions_single_dep_strange_order(self):
        mod_data = generate_mod_data('mod_name', [["foo"], ["bar"], ["baz"]])
        mod_data['releases'] = [mod_data['releases'][1], mod_data['releases'][2], mod_data['releases'][0]]
        mod_data['releases'].reverse()
        latest_version = mod_portal.get_latest_version(mod_data)
        self.assertEqual(latest_version['version'], '2', f'Unexpected latest version returned: {latest_version}')
    
    def test__multiple_versions_multiple_deps_strange_order(self):
        mod_data = generate_mod_data('mod_name', [["foo", "bar", "baz"], ["qux", "quxx", "quxxx"], ["a", "b", "c"]])
        mod_data['releases'] = [mod_data['releases'][1], mod_data['releases'][2], mod_data['releases'][0]]
        mod_data['releases'].reverse()
        latest_version = mod_portal.get_latest_version(mod_data)
        self.assertEqual(latest_version['version'], '2', f'Unexpected latest version returned: {latest_version}')


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