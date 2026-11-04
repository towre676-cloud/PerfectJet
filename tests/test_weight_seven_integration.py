"""Installed theorem reports fail closed on stale or incomplete bindings."""
import copy
import unittest
from unittest.mock import patch
from perfectjet import weight_seven


class IntegrationTests(unittest.TestCase):
    def test_complete_installed_report_and_open_boundary(self):
        record=weight_seven.report()
        self.assertEqual(len(record['kernel_multiplicities']),9)
        self.assertEqual(record['kernel_dimension'],181753)
        self.assertEqual(record['new_cubic_primitive_multiplicity'],0)
        self.assertIn('remain open',record['scope'])

    def test_changed_source_is_rejected(self):
        changed=dict(weight_seven.source_digests(),**{'asterion_lattice_projection.py':'0'*64})
        with patch.object(weight_seven,'source_digests',return_value=changed):
            with self.assertRaisesRegex(ValueError,'source binding'):weight_seven.report()

    def test_missing_sector_or_changed_certificate_is_rejected(self):
        original=weight_seven.report()
        for field in ('kernel_multiplicities','installed_resource_sha256'):
            changed=copy.deepcopy(original)
            if field=='kernel_multiplicities':del changed[field]['3875']
            else:changed[field]['asterion_w7_certificates.json']='0'*64
            with patch.object(weight_seven.json,'loads',return_value=changed):
                with self.assertRaises(ValueError):weight_seven.report()

    def test_missing_certificate_binding_is_rejected(self):
        changed=copy.deepcopy(weight_seven.report())
        del changed['installed_resource_sha256']['asterion_primitive_certificates.json']
        with patch.object(weight_seven.json,'loads',return_value=changed):
            with self.assertRaisesRegex(ValueError,'incomplete installed'):weight_seven.report()


if __name__=='__main__':unittest.main()
