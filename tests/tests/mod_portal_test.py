import datetime
import filecmp
import json
import os
import requests
import requests_mock
import unittest

from . import TestResources

from factorio_headless.lib import data_objects, mod_portal


OLD_DATETIME = datetime.datetime.fromisoformat('2000-01-01')
def generate_versions(data: list[list[str]], file_name: str = None, download_url: str = None) -> list[dict]:
    vers = []
    for i, d in enumerate(data):
        vers.append({
            "version": str(i),
            "released_at": f'{OLD_DATETIME + datetime.timedelta(days=i)}Z',
            "info_json": {
                "dependencies": d
            },
            "file_name": file_name,
            "download_url": download_url
        })
    return vers
    
def generate_mod_data(name: str, releases: list[list[str]], file_name: str = None, download_url: str = None) -> dict:
    data = {}
    data['title'] = name
    data['name'] = name
    data['releases'] = generate_versions(releases, file_name, download_url)
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


class TestModPortal__find_mod_dependencies(unittest.TestCase):
    def test__single_release_small(self):
        mod_data = generate_mod_data('mod_name', [["foo", "! bar", "? baz", "(?) qux", "~ quxx"]])
        expected = ["foo", "quxx"]
        actual = mod_portal.find_mod_dependencies(mod_data)
        self.assertEqual(actual, expected)
    
    def test__single_release_large(self):
        mod_data = generate_mod_data('mod_name', [[
            "foo", "foo1",
            "! bar", "! bar1",
            "? baz", "? baz1",
            "(?) qux", "(?) qux1",
            "~ quxx", "~ quxx1"
        ]])
        expected = ["foo", "foo1", "quxx", "quxx1"]
        actual = mod_portal.find_mod_dependencies(mod_data)
        self.assertEqual(actual, expected)
    
    def test__multiple_release_small(self):
        mod_data = generate_mod_data('mod_name', [
            ["0foo", "! 0bar", "? 0baz", "(?) 0qux", "~ 0quxx"],
            ["foo", "! bar", "? baz", "(?) qux", "~ quxx"]
        ])
        expected = ["foo", "quxx"]
        actual = mod_portal.find_mod_dependencies(mod_data)
        self.assertEqual(actual, expected)
    
    def test__multiple_release_large(self):
        mod_data = generate_mod_data('mod_name', [[
                "0foo", "0foo1",
                "! 0bar", "! 0bar1",
                "? 0baz", "? 0baz1",
                "(?) 0qux", "(?) 0qux1",
                "~ 0quxx", "~ 0quxx1"
            ],[
                "foo", "foo1",
                "! bar", "! bar1",
                "? baz", "? baz1",
                "(?) qux", "(?) qux1",
                "~ quxx", "~ quxx1"
            ]
        ])
        expected = ["foo", "foo1", "quxx", "quxx1"]
        actual = mod_portal.find_mod_dependencies(mod_data)
        self.assertEqual(actual, expected)


@requests_mock.Mocker()
class TestModPortal__get_download_list(unittest.TestCase):
    def mock_requests(self, mock: requests_mock.Mocker, mods: list[dict]):
        for m in mods:
            mock.get(f'https://mods.factorio.com/api/mods/{m["name"]}/full', text=json.dumps(m))
    
    def test__single_mod_single_release_small(self, m: requests_mock.Mocker):
        mod_data = generate_mod_data('mod_name', [["foo", "! bar", "? baz", "(?) qux", "~ quxx"]])
        expected = set(["mod_name", "foo", "quxx"])
        self.mock_requests(m, [mod_data])
        actual = mod_portal.get_download_list(['mod_name'])
        self.assertSetEqual(actual, expected)
    
    def test__single_mod_single_release_large(self, m: requests_mock.Mocker):
        mod_data = generate_mod_data('mod_name', [[
            "foo", "foo1",
            "! bar", "! bar1",
            "? baz", "? baz1",
            "(?) qux", "(?) qux1",
            "~ quxx", "~ quxx1"
        ]])
        expected = set(["mod_name", "foo", "foo1", "quxx", "quxx1"])
        self.mock_requests(m, [mod_data])
        actual = mod_portal.get_download_list(['mod_name'])
        self.assertEqual(actual, expected)
    
    def test__single_mod_multiple_release_small(self, m: requests_mock.Mocker):
        mod_data = generate_mod_data('mod_name', [
            ["0foo", "! 0bar", "? 0baz", "(?) 0qux", "~ 0quxx"],
            ["foo", "! bar", "? baz", "(?) qux", "~ quxx"]
        ])
        expected = set(["mod_name", "foo", "quxx"])
        self.mock_requests(m, [mod_data])
        actual = mod_portal.get_download_list(['mod_name'])
        self.assertEqual(actual, expected)
    
    def test__single_mod_multiple_release_large(self, m: requests_mock.Mocker):
        mod_data = generate_mod_data('mod_name', [[
                "0foo", "0foo1",
                "! 0bar", "! 0bar1",
                "? 0baz", "? 0baz1",
                "(?) 0qux", "(?) 0qux1",
                "~ 0quxx", "~ 0quxx1"
            ],[
                "foo", "foo1",
                "! bar", "! bar1",
                "? baz", "? baz1",
                "(?) qux", "(?) qux1",
                "~ quxx", "~ quxx1"
            ]
        ])
        expected = set(["mod_name", "foo", "foo1", "quxx", "quxx1"])
        self.mock_requests(m, [mod_data])
        actual = mod_portal.get_download_list(['mod_name'])
        self.assertEqual(actual, expected)
    
    def test__multiple_mods_single_release_small(self, m: requests_mock.Mocker):
        mod_data = generate_mod_data('mod_name', [["foo", "! bar", "? baz", "(?) qux", "~ quxx"]])
        mod_data1 = generate_mod_data('mod_name1', [["foo", "! bar", "? baz", "(?) qux", "~ quxx1"]])
        expected = set(["mod_name", "foo", "quxx", "quxx1", "mod_name1"])
        self.mock_requests(m, [mod_data, mod_data1])
        actual = mod_portal.get_download_list(['mod_name', 'mod_name1'])
        self.assertSetEqual(actual, expected)
    
    def test__multiple_mods_single_release_large(self, m: requests_mock.Mocker):
        mod_data = generate_mod_data('mod_name', [[
            "foo", "foo1",
            "! bar", "! bar1",
            "? baz", "? baz1",
            "(?) qux", "(?) qux1",
            "~ quxx", "~ quxx1"
        ]])
        mod_data1 = generate_mod_data('mod_name1', [[
            "foo", "foo1",
            "! bar", "! bar1",
            "? baz", "? baz1",
            "(?) qux", "(?) qux1",
            "~ 0quxx", "~ 0quxx1"
        ]])
        expected = set(["mod_name", "foo", "foo1", "quxx", "quxx1", "mod_name1", "0quxx", "0quxx1"])
        self.mock_requests(m, [mod_data, mod_data1])
        actual = mod_portal.get_download_list(['mod_name', 'mod_name1'])
        self.assertEqual(actual, expected)
    
    def test__multiple_mods_multiple_release_small(self, m: requests_mock.Mocker):
        mod_data = generate_mod_data('mod_name', [
            ["0foo", "! 0bar", "? 0baz", "(?) 0qux", "~ 0quxx"],
            ["foo", "! bar", "? baz", "(?) qux", "~ quxx"]
        ])
        mod_data1 = generate_mod_data('mod_name1', [
            ["0foo", "! 0bar", "? 0baz", "(?) 0qux", "~ 0quxx"],
            ["foo", "! bar", "? baz", "(?) qux", "~ quxx1"]
        ])
        expected = set(["mod_name", "foo", "quxx", "mod_name1", "quxx1"])
        self.mock_requests(m, [mod_data, mod_data1])
        actual = mod_portal.get_download_list(['mod_name', 'mod_name1'])
        self.assertEqual(actual, expected)
    
    def test__multiple_mods_multiple_release_large(self, m: requests_mock.Mocker):
        mod_data = generate_mod_data('mod_name', [[
                "0foo", "0foo1",
                "! 0bar", "! 0bar1",
                "? 0baz", "? 0baz1",
                "(?) 0qux", "(?) 0qux1",
                "~ 0quxx", "~ 0quxx1"
            ],[
                "foo", "foo1",
                "! bar", "! bar1",
                "? baz", "? baz1",
                "(?) qux", "(?) qux1",
                "~ quxx", "~ quxx1"
            ]
        ])
        mod_data1 = generate_mod_data('mod_name1', [[
                "0foo", "0foo1",
                "! 0bar", "! 0bar1",
                "? 0baz", "? 0baz1",
                "(?) 0qux", "(?) 0qux1",
                "~ 0quxx", "~ 0quxx1"
            ],[
                "foo", "foo1",
                "! bar", "! bar1",
                "? baz", "? baz1",
                "(?) qux", "(?) qux1",
                "~ 0quxx", "~ 0quxx1"
            ]
        ])
        expected = set(["mod_name", "foo", "foo1", "quxx", "quxx1", "mod_name1", "0quxx", "0quxx1"])
        self.mock_requests(m, [mod_data, mod_data1])
        actual = mod_portal.get_download_list(['mod_name', 'mod_name1'])
        self.assertEqual(actual, expected)


@requests_mock.Mocker()
class TestModPortal__download_single_mod(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.res = TestResources(self.__name__)
    
    @classmethod
    def tearDownClass(self):
        self.res.cleanup()
    
    def test__happy_path(self, m: requests_mock.Mocker):
        mod_name = 'mod'
        src_filename = os.path.join(self.res.resources_root, 'mod_1.0.zip')
        mod_data = generate_mod_data(mod_name, [["base"]], 'mod_1.0.zip', f'/download/{mod_name}/url_suffix')
        response_headers = {"Content-Type": "application/octet-stream"}
        m.get(f'https://mods.factorio.com/api/mods/{mod_name}/full', text=json.dumps(mod_data))
        with open(src_filename, 'rb') as f:
            m.get(
                f'https://mods.factorio.com/download/{mod_name}/url_suffix?username=username_value&token=token_value',
                content=f.read(),
                headers=response_headers
            )
        player_data = data_objects.PlayerData().set_values('username_value', 'token_value')
        dst_dir = self.res.build_test_dir()
        mod_portal.download_single_mod(mod_name, player_data, dst_dir)
        contents = os.listdir(dst_dir)
        self.assertEqual(len(contents), 1, f'Downloaded more than 1 file: {contents}')
        self.assertEqual(contents[0], 'mod_1.0.zip', f'Unexpected downloaded file')
        self.assertTrue(filecmp.cmp(os.path.join(dst_dir, contents[0]), src_filename), 'Downloaded file does not match source file')
    
    def test__happy_path_multiple_chunks(self, m: requests_mock.Mocker):
        mod_name = 'mod'
        src_filename = os.path.join(self.res.resources_root, 'mod_1.0.zip')
        mod_data = generate_mod_data(mod_name, [["base"]], 'mod_1.0.zip', f'/download/{mod_name}/url_suffix')
        response_headers = {"Content-Type": "application/octet-stream"}
        m.get(f'https://mods.factorio.com/api/mods/{mod_name}/full', text=json.dumps(mod_data))
        with open(src_filename, 'rb') as f:
            m.get(
                f'https://mods.factorio.com/download/{mod_name}/url_suffix?username=username_value&token=token_value',
                content=f.read(),
                headers=response_headers
            )
        player_data = data_objects.PlayerData().set_values('username_value', 'token_value')
        dst_dir = self.res.build_test_dir()
        mod_portal.download_single_mod(mod_name, player_data, dst_dir, 32)
        contents = os.listdir(dst_dir)
        self.assertEqual(len(contents), 1, f'Downloaded more than 1 file: {contents}')
        self.assertEqual(contents[0], 'mod_1.0.zip', f'Unexpected downloaded file')
        self.assertTrue(filecmp.cmp(os.path.join(dst_dir, contents[0]), src_filename), 'Downloaded file does not match source file')
    
    def test__no_content_type_fails(self, m: requests_mock.Mocker):
        mod_name = 'mod'
        src_filename = os.path.join(self.res.resources_root, 'mod_1.0.zip')
        mod_data = generate_mod_data(mod_name, [["base"]], 'mod_1.0.zip', f'/download/{mod_name}/url_suffix')
        response_headers = {}
        m.get(f'https://mods.factorio.com/api/mods/{mod_name}/full', text=json.dumps(mod_data))
        with open(src_filename, 'rb') as f:
            m.get(
                f'https://mods.factorio.com/download/{mod_name}/url_suffix?username=username_value&token=token_value',
                content=f.read(),
                headers=response_headers
            )
        player_data = data_objects.PlayerData().set_values('username_value', 'token_value')
        dst_dir = self.res.build_test_dir()
        self.assertRaises(RuntimeError, mod_portal.download_single_mod, mod_name, player_data, dst_dir)
    
    def test__bad_content_type_fails(self, m: requests_mock.Mocker):
        mod_name = 'mod'
        src_filename = os.path.join(self.res.resources_root, 'mod_1.0.zip')
        mod_data = generate_mod_data(mod_name, [["base"]], 'mod_1.0.zip', f'/download/{mod_name}/url_suffix')
        response_headers = {"Content-Type": "application/json"}
        m.get(f'https://mods.factorio.com/api/mods/{mod_name}/full', text=json.dumps(mod_data))
        with open(src_filename, 'rb') as f:
            m.get(
                f'https://mods.factorio.com/download/{mod_name}/url_suffix?username=username_value&token=token_value',
                content=f.read(),
                headers=response_headers
            )
        player_data = data_objects.PlayerData().set_values('username_value', 'token_value')
        dst_dir = self.res.build_test_dir()
        self.assertRaises(RuntimeError, mod_portal.download_single_mod, mod_name, player_data, dst_dir)
    
    def test__auth_failure_fails(self, m: requests_mock.Mocker):
        mod_name = 'mod'
        src_filename = os.path.join(self.res.resources_root, 'mod_1.0.zip')
        mod_data = generate_mod_data(mod_name, [["base"]], 'mod_1.0.zip', f'/download/{mod_name}/url_suffix')
        response_headers = {"Content-Type": "application/octet-stream"}
        m.get(f'https://mods.factorio.com/api/mods/{mod_name}/full', text=json.dumps(mod_data))
        with open(src_filename, 'rb') as f:
            m.get(
                f'https://mods.factorio.com/download/{mod_name}/url_suffix?username=username_value&token=token_value',
                content=f.read(),
                headers=response_headers,
                status_code=403
            )
        player_data = data_objects.PlayerData().set_values('username_value', 'token_value')
        dst_dir = self.res.build_test_dir()
        self.assertRaises(requests.exceptions.HTTPError, mod_portal.download_single_mod, mod_name, player_data, dst_dir)


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