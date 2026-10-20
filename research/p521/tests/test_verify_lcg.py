import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('independent_lcg_verifier', ROOT/'verify_lcg_certificate.py')
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)


class IndependentLCGVerification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = json.loads((ROOT/'results/lcg_forensics.json').read_text())

    def test_receipt_and_complete_coverage(self):
        result = checker.verify_document(self.receipt)
        self.assertEqual(result['byte_trace_proofs'], 188)
        self.assertEqual(result['assembly_proof_rows'], 179)
        self.assertEqual(result['assembly_coordinate_order_cases'], 180)
        self.assertEqual(result['native']['first_states'], 327680000)

    def test_mutations_rejected(self):
        changed = copy.deepcopy(self.receipt)
        changed['byte_assembly']['certificates'].clear()
        with self.assertRaises(checker.ProofError):
            checker.verify_document(changed)
        changed = copy.deepcopy(self.receipt)
        changed['byte_assembly']['certificates'][0]['maximum_quotient'] += 1
        with self.assertRaises(checker.ProofError):
            checker.verify_document(changed)
        changed = copy.deepcopy(self.receipt)
        changed['top_bytes']['dual_exclusion_certificates'][0]['certificate']['coefficients'][0] += 1
        with self.assertRaises(checker.ProofError):
            checker.verify_document(changed)
        changed = copy.deepcopy(self.receipt)
        changed['top_bits']['states_enumerated'] += 1
        with self.assertRaises(checker.ProofError):
            checker.verify_document(changed)

    def test_valid_generator_output_cannot_be_excluded(self):
        row = self.receipt['top_bytes']['dual_exclusion_certificates'][0]['certificate']
        proof = copy.deepcopy(row)
        data = bytes.fromhex(checker.SEED)
        proof['observation_hex'] = data.hex()
        proof['interval_lower'], proof['interval_upper'] = checker.proof_interval(data, proof['coefficients'])
        with self.assertRaises(checker.ProofError):
            checker.verify_dual(proof, data)


if __name__ == '__main__':
    unittest.main()
