import unittest

from factorio_headless.lib import data_objects

# Dependency
class TestDependecyObject__init(unittest.TestCase):
    def test__just_name(self):
        dep_str = 'MOD_NAME'
        dep = data_objects.Dependency(dep_str)
        self.assertEqual(dep.mod_name, 'MOD_NAME')
        pass
    
    def test__no_version_incompatible(self):
        dep_str = '! MOD_NAME'
        dep = data_objects.Dependency(dep_str)
        self.assertEqual(dep.mod_name, 'MOD_NAME')
        self.assertFalse(dep.compatible, 'Unexpected Depedency compatible flag')
        self.assertFalse(dep.required, 'Unexpected Depedency required flag')
        pass
    
    def test__no_version_optional(self):
        dep_str = '? MOD_NAME'
        dep = data_objects.Dependency(dep_str)
        self.assertEqual(dep.mod_name, 'MOD_NAME')
        self.assertTrue(dep.compatible, 'Unexpected Depedency compatible flag')
        self.assertFalse(dep.required, 'Unexpected Depedency required flag')
        pass
    
    def test__no_version_hidden_optional(self):
        dep_str = '(?) MOD_NAME'
        dep = data_objects.Dependency(dep_str)
        self.assertEqual(dep.mod_name, 'MOD_NAME')
        self.assertTrue(dep.compatible, 'Unexpected Depedency compatible flag')
        self.assertFalse(dep.required, 'Unexpected Depedency required flag')
        pass
    
    def test__no_version_required_no_load_order(self):
        dep_str = '~ MOD_NAME'
        dep = data_objects.Dependency(dep_str)
        self.assertEqual(dep.mod_name, 'MOD_NAME')
        self.assertTrue(dep.compatible, 'Unexpected Depedency compatible flag')
        self.assertTrue(dep.required, 'Unexpected Depedency required flag')
        pass
    
    def test__no_prefix_less_than(self):
        dep_str = 'MOD_NAME < 0.0.1'
        dep = data_objects.Dependency(dep_str)
        self.assertEqual(dep.mod_name, 'MOD_NAME')
        self.assertEqual(dep.equality, '<')
        self.assertEqual(dep.version, '0.0.1')
        pass
    
    def test__no_prefix_less_than_or_equal(self):
        dep_str = 'MOD_NAME <= 0.0.1'
        dep = data_objects.Dependency(dep_str)
        self.assertEqual(dep.mod_name, 'MOD_NAME')
        self.assertEqual(dep.equality, '<=')
        self.assertEqual(dep.version, '0.0.1')
        pass
    
    def test__no_prefix_equal(self):
        dep_str = 'MOD_NAME = 0.0.1'
        dep = data_objects.Dependency(dep_str)
        self.assertEqual(dep.mod_name, 'MOD_NAME')
        self.assertEqual(dep.equality, '=')
        self.assertEqual(dep.version, '0.0.1')
        pass
    
    def test__no_prefix_greater_than_or_equal(self):
        dep_str = 'MOD_NAME >= 0.0.1'
        dep = data_objects.Dependency(dep_str)
        self.assertEqual(dep.mod_name, 'MOD_NAME')
        self.assertEqual(dep.equality, '>=')
        self.assertEqual(dep.version, '0.0.1')
        pass
    
    def test__no_prefix_greater_than(self):
        dep_str = 'MOD_NAME > 0.0.1'
        dep = data_objects.Dependency(dep_str)
        self.assertEqual(dep.mod_name, 'MOD_NAME')
        self.assertEqual(dep.equality, '>')
        self.assertEqual(dep.version, '0.0.1')
        pass
    
    # Not sure if this is allowed by the Mod Portal, but easy to cover
    def test__full_incompatible_strange_spacing(self):
        dep_str = ' !    MOD_NAME\t> \t 0.0.1\n'
        dep = data_objects.Dependency(dep_str)
        self.assertEqual(dep.mod_name, 'MOD_NAME')
        self.assertEqual(dep.equality, '>')
        self.assertEqual(dep.version, '0.0.1')
        self.assertFalse(dep.compatible, 'Unexpected Depedency compatible flag')
        self.assertFalse(dep.required, 'Unexpected Depedency required flag')
        pass
    
    def test__full_incompatible(self):
        dep_str = '! MOD_NAME > 0.0.1'
        dep = data_objects.Dependency(dep_str)
        self.assertEqual(dep.mod_name, 'MOD_NAME')
        self.assertEqual(dep.equality, '>')
        self.assertEqual(dep.version, '0.0.1')
        self.assertFalse(dep.compatible, 'Unexpected Depedency compatible flag')
        self.assertFalse(dep.required, 'Unexpected Depedency required flag')
        pass
    
    def test__full_optional_dependency(self):
        dep_str = '? MOD_NAME = 0.0.1'
        dep = data_objects.Dependency(dep_str)
        self.assertEqual(dep.mod_name, 'MOD_NAME')
        self.assertEqual(dep.equality, '=')
        self.assertEqual(dep.version, '0.0.1')
        self.assertTrue(dep.compatible, 'Unexpected Depedency compatible flag')
        self.assertFalse(dep.required, 'Unexpected Depedency required flag')
        pass
    
    def test__full_hidden_optional_dependency(self):
        dep_str = '(?) MOD_NAME <= 0.0.1'
        dep = data_objects.Dependency(dep_str)
        self.assertEqual(dep.mod_name, 'MOD_NAME')
        self.assertEqual(dep.equality, '<=')
        self.assertEqual(dep.version, '0.0.1')
        self.assertTrue(dep.compatible, 'Unexpected Depedency compatible flag')
        self.assertFalse(dep.required, 'Unexpected Depedency required flag')
        pass
    
    def test__full_required_no_load_order(self):
        dep_str = '~ MOD_NAME < 0.0.1'
        dep = data_objects.Dependency(dep_str)
        self.assertEqual(dep.mod_name, 'MOD_NAME')
        self.assertEqual(dep.equality, '<')
        self.assertEqual(dep.version, '0.0.1')
        self.assertTrue(dep.compatible, 'Unexpected Depedency compatible flag')
        self.assertTrue(dep.required, 'Unexpected Depedency required flag')
        pass


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
