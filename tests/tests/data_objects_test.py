import os
import unittest

from . import TestResources

from factorio_headless.lib import data_objects

# Dependency
class TestDependecyObject__init(unittest.TestCase):
    def test__just_name(self):
        dep_str = 'MOD_NAME'
        dep = data_objects.Dependency(dep_str)
        self.assertEqual(dep.mod_name, 'MOD_NAME')
    
    def test__no_version_incompatible(self):
        dep_str = '! MOD_NAME'
        dep = data_objects.Dependency(dep_str)
        self.assertEqual(dep.mod_name, 'MOD_NAME')
        self.assertFalse(dep.compatible, 'Unexpected Depedency compatible flag')
        self.assertFalse(dep.required, 'Unexpected Depedency required flag')
    
    def test__no_version_optional(self):
        dep_str = '? MOD_NAME'
        dep = data_objects.Dependency(dep_str)
        self.assertEqual(dep.mod_name, 'MOD_NAME')
        self.assertTrue(dep.compatible, 'Unexpected Depedency compatible flag')
        self.assertFalse(dep.required, 'Unexpected Depedency required flag')
    
    def test__no_version_hidden_optional(self):
        dep_str = '(?) MOD_NAME'
        dep = data_objects.Dependency(dep_str)
        self.assertEqual(dep.mod_name, 'MOD_NAME')
        self.assertTrue(dep.compatible, 'Unexpected Depedency compatible flag')
        self.assertFalse(dep.required, 'Unexpected Depedency required flag')
    
    def test__no_version_required_no_load_order(self):
        dep_str = '~ MOD_NAME'
        dep = data_objects.Dependency(dep_str)
        self.assertEqual(dep.mod_name, 'MOD_NAME')
        self.assertTrue(dep.compatible, 'Unexpected Depedency compatible flag')
        self.assertTrue(dep.required, 'Unexpected Depedency required flag')
    
    def test__no_prefix_less_than(self):
        dep_str = 'MOD_NAME < 0.0.1'
        dep = data_objects.Dependency(dep_str)
        self.assertEqual(dep.mod_name, 'MOD_NAME')
        self.assertEqual(dep.equality, '<')
        self.assertEqual(dep.version, '0.0.1')
    
    def test__no_prefix_less_than_or_equal(self):
        dep_str = 'MOD_NAME <= 0.0.1'
        dep = data_objects.Dependency(dep_str)
        self.assertEqual(dep.mod_name, 'MOD_NAME')
        self.assertEqual(dep.equality, '<=')
        self.assertEqual(dep.version, '0.0.1')
    
    def test__no_prefix_equal(self):
        dep_str = 'MOD_NAME = 0.0.1'
        dep = data_objects.Dependency(dep_str)
        self.assertEqual(dep.mod_name, 'MOD_NAME')
        self.assertEqual(dep.equality, '=')
        self.assertEqual(dep.version, '0.0.1')
    
    def test__no_prefix_greater_than_or_equal(self):
        dep_str = 'MOD_NAME >= 0.0.1'
        dep = data_objects.Dependency(dep_str)
        self.assertEqual(dep.mod_name, 'MOD_NAME')
        self.assertEqual(dep.equality, '>=')
        self.assertEqual(dep.version, '0.0.1')
    
    def test__no_prefix_greater_than(self):
        dep_str = 'MOD_NAME > 0.0.1'
        dep = data_objects.Dependency(dep_str)
        self.assertEqual(dep.mod_name, 'MOD_NAME')
        self.assertEqual(dep.equality, '>')
        self.assertEqual(dep.version, '0.0.1')
    
    # Not sure if this is allowed by the Mod Portal, but easy to cover
    def test__full_incompatible_strange_spacing(self):
        dep_str = ' !    MOD_NAME\t> \t 0.0.1\n'
        dep = data_objects.Dependency(dep_str)
        self.assertEqual(dep.mod_name, 'MOD_NAME')
        self.assertEqual(dep.equality, '>')
        self.assertEqual(dep.version, '0.0.1')
        self.assertFalse(dep.compatible, 'Unexpected Depedency compatible flag')
        self.assertFalse(dep.required, 'Unexpected Depedency required flag')
    
    def test__full_incompatible(self):
        dep_str = '! MOD_NAME > 0.0.1'
        dep = data_objects.Dependency(dep_str)
        self.assertEqual(dep.mod_name, 'MOD_NAME')
        self.assertEqual(dep.equality, '>')
        self.assertEqual(dep.version, '0.0.1')
        self.assertFalse(dep.compatible, 'Unexpected Depedency compatible flag')
        self.assertFalse(dep.required, 'Unexpected Depedency required flag')
    
    def test__full_optional_dependency(self):
        dep_str = '? MOD_NAME = 0.0.1'
        dep = data_objects.Dependency(dep_str)
        self.assertEqual(dep.mod_name, 'MOD_NAME')
        self.assertEqual(dep.equality, '=')
        self.assertEqual(dep.version, '0.0.1')
        self.assertTrue(dep.compatible, 'Unexpected Depedency compatible flag')
        self.assertFalse(dep.required, 'Unexpected Depedency required flag')
    
    def test__full_hidden_optional_dependency(self):
        dep_str = '(?) MOD_NAME <= 0.0.1'
        dep = data_objects.Dependency(dep_str)
        self.assertEqual(dep.mod_name, 'MOD_NAME')
        self.assertEqual(dep.equality, '<=')
        self.assertEqual(dep.version, '0.0.1')
        self.assertTrue(dep.compatible, 'Unexpected Depedency compatible flag')
        self.assertFalse(dep.required, 'Unexpected Depedency required flag')
    
    def test__full_required_no_load_order(self):
        dep_str = '~ MOD_NAME < 0.0.1'
        dep = data_objects.Dependency(dep_str)
        self.assertEqual(dep.mod_name, 'MOD_NAME')
        self.assertEqual(dep.equality, '<')
        self.assertEqual(dep.version, '0.0.1')
        self.assertTrue(dep.compatible, 'Unexpected Depedency compatible flag')
        self.assertTrue(dep.required, 'Unexpected Depedency required flag')


class TestDependecyObject__parse_compatibility_operator(unittest.TestCase):
    def test__incompatible(self):
        compatible, required = data_objects.Dependency._parse_compatibility_operator(None, '!')
        self.assertFalse(compatible, 'Unexpected Depedency compatible flag')
        self.assertFalse(required, 'Unexpected Depedency required flag')
    
    def test__optional_dependency(self):
        compatible, required = data_objects.Dependency._parse_compatibility_operator(None, '?')
        self.assertTrue(compatible, 'Unexpected Depedency compatible flag')
        self.assertFalse(required, 'Unexpected Depedency required flag')
    
    def test__hidden_optional_dependency(self):
        compatible, required = data_objects.Dependency._parse_compatibility_operator(None, '(?)')
        self.assertTrue(compatible, 'Unexpected Depedency compatible flag')
        self.assertFalse(required, 'Unexpected Depedency required flag')
    
    def test__required_no_load_order(self):
        compatible, required = data_objects.Dependency._parse_compatibility_operator(None, '~')
        self.assertTrue(compatible, 'Unexpected Depedency compatible flag')
        self.assertTrue(required, 'Unexpected Depedency required flag')


# PlayerData
class TestPlayerDataObject__set_values(unittest.TestCase):
    def test__set(self):
        pd = data_objects.PlayerData()
        pd.set_values('username', 'token')
        self.assertEqual(pd.username, 'username')
        self.assertEqual(pd.token, 'token')
    
    def test__returns_self(self):
        pd = data_objects.PlayerData()
        pd1 = pd.set_values('username', 'token')
        self.assertEqual(pd, pd1)


class TestPlayerDataObject__set_values_from_file(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.res = TestResources()
    
    def test__set(self):
        pd = data_objects.PlayerData()
        pd.set_values_from_file(os.path.join(self.res.resources_root, 'test_player_data.json'))
        self.assertEqual(pd.username, 'username_value')
        self.assertEqual(pd.token, 'token_value')
    
    def test__returns_self(self):
        pd = data_objects.PlayerData()
        pd1 = pd.set_values_from_file(os.path.join(self.res.resources_root, 'test_player_data.json'))
        self.assertEqual(pd, pd1)


class TestPlayerDataObject__as_params(unittest.TestCase):
    def test__is_dict(self):
        pd = data_objects.PlayerData()
        pd.set_values('username', 'token')
        params = pd.as_params()
        self.assertIsInstance(params, dict)
    
    def test__has_correct_values(self):
        pd = data_objects.PlayerData()
        pd.set_values('username', 'token')
        params = pd.as_params()
        self.assertEqual(params['username'], 'username')
        self.assertEqual(params['token'], 'token')
    
    def test__nothing_extra(self):
        pd = data_objects.PlayerData()
        pd.set_values('username', 'token')
        params = pd.as_params()
        for k, _ in params.items():
            self.assertIn(k , ['username', 'token'])
