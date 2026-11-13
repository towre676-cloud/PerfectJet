import copy
import json
import unittest
from importlib.resources import files
from unittest.mock import Mock, patch

from perfectjet import complete_weight_seven as complete
from perfectjet.asterion_primitives import JetAlgebra, load_certificates


class CompleteWeightSevenTests(unittest.TestCase):
    def test_complete_character_and_primitives(self):
        record = complete.report()
        theorem = record['theorem']
        self.assertEqual(theorem['total_weight7_kernel_character'],
                         {'1': 1, '248': 3, '3875': 3, '30380': 2, '147250': 2, '779247': 1})
        self.assertEqual(theorem['quartic_VOA_image_character'], {'30380': 1, '6696000': 1})
        self.assertEqual(theorem['total_weight7_kernel_dimension'], 1146877)
        self.assertEqual(theorem['quartic_kernel_dimension'], 965124)
        self.assertEqual(theorem['new_weight7_primitive_dimension'], 0)
        self.assertEqual(len(load_certificates()['sectors']), 7)
        self.assertEqual(JetAlgebra.mobius_lower({((0, 2),): 1}), {((0, 1),): 3})

    def test_stale_sources_and_resources_fail_closed(self):
        original = complete.report()
        for field in ('source_sha256', 'installed_resource_sha256'):
            changed = copy.deepcopy(original)
            changed[field][next(iter(changed[field]))] = '0' * 64
            with self.subTest(field=field):
                self.assert_rejects(changed, 'binding|resource')

    def test_missing_quartic_sector_is_rejected(self):
        changed = complete.report()
        changed['theorem']['quartic_sector_table'].pop()
        self.assert_rejects(changed, 'quartic source sectors')

    def test_mutated_primitive_resource_is_rejected(self):
        actual = files('perfectjet.resources')
        primitive_name = complete.INSTALLED_RESOURCES[0]

        def read_resource(name):
            if name != primitive_name:
                return actual.joinpath(name)
            resource = Mock()
            primitive = json.loads(actual.joinpath(name).read_bytes())
            primitive['sectors'].pop('w5-248')
            resource.read_bytes.return_value = json.dumps(primitive).encode()
            return resource

        resources = Mock()
        resources.joinpath.side_effect = read_resource
        with patch.object(complete, 'files', side_effect=lambda name: resources if name == 'perfectjet.resources' else files(name)):
            with self.assertRaisesRegex(ValueError, 'stale complete weight-seven resource'):
                complete.report()

    def assert_rejects(self, record, error):
        actual = files('perfectjet.resources')

        def read_resource(name):
            if name != complete.RESOURCE:
                return actual.joinpath(name)
            resource = Mock()
            resource.read_bytes.return_value = json.dumps(record).encode()
            return resource

        resources = Mock()
        resources.joinpath.side_effect = read_resource
        with patch.object(complete, 'files', side_effect=lambda name: resources if name == 'perfectjet.resources' else files(name)):
            with self.assertRaisesRegex(ValueError, error):
                complete.report()
