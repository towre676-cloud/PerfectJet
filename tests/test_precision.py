"""Exact independent replays for the cancellation/precision guard."""
from fractions import Fraction as Q
import json
import random
import unittest

from perfectjet.precision import analyze_sum, compare_sums, receipt, repair_sum, round_binary


class PrecisionTests(unittest.TestCase):
    def test_binary_rounding_matches_hardware_in_ordinary_range(self):
        rng = random.Random(811)
        for _ in range(250):
            value = Q(rng.randint(-10**20, 10**20), rng.randint(1, 10**10))
            self.assertEqual(round_binary(value), Q.from_float(float(value)))
        self.assertEqual(round_binary(2**53 + 1), 2**53)
        self.assertEqual(round_binary(2**53 + 3), 2**53 + 4)
        self.assertEqual(round_binary(-2**53 - 1), -2**53)
        self.assertEqual(round_binary(Q(9, 8), 3), 1)  # midpoint, even significand
        self.assertEqual(round_binary(Q(11, 8), 3), Q(3, 2))

    def test_ordered_recursive_model_matches_hardware(self):
        rng = random.Random(616)
        for _ in range(60):
            terms = [Q(rng.randint(-10**12, 10**12), rng.randint(1, 100)) for _ in range(20)]
            floats = [float(t) for t in terms]
            subtotal = floats[0]
            for value in floats[1:]:
                subtotal += value
            result = analyze_sum(terms)
            self.assertEqual(result.approximation, Q.from_float(subtotal))
            self.assertLessEqual(result.actual_arithmetic_error, result.forward_error_bound)
            lo, hi = result.interval
            self.assertLessEqual(lo, sum(terms))
            self.assertGreaterEqual(hi, sum(terms))

    def test_rounding_relative_model_at_many_precisions(self):
        rng = random.Random(92)
        for bits in (2, 3, 7, 17, 53, 100):
            u = Q(1, 2**bits)
            for _ in range(50):
                value = Q(rng.randint(1, 10**8), rng.randint(1, 10**8))
                self.assertLessEqual(abs(round_binary(value, bits) - value), u * abs(value))

    def test_cancellation_and_repair(self):
        terms = [10**16, 1, -10**16]
        initial = analyze_sum(terms)
        self.assertEqual(initial.exact_sum, 1)
        self.assertEqual(initial.approximation, 0)
        self.assertEqual(initial.condition, 2 * 10**16 + 1)
        self.assertEqual(initial.conversion_error_bound, 0)
        self.assertGreater(initial.cancellation_bits, 54)
        result = repair_sum(terms, absolute_tolerance=0)
        self.assertEqual(result.attempted_bits, (53, 106))
        self.assertEqual(result.final.approximation, 1)
        self.assertTrue(result.satisfied)
        self.assertTrue(result.total_budget_satisfied)
        self.assertEqual(analyze_sum([10**16, -10**16, 1]).approximation, 1)

    def test_input_conversion_is_separate_from_summation(self):
        result = analyze_sum([Q(1, 3)], bits=3)
        self.assertEqual(result.approximation, Q(5, 16))
        self.assertEqual(result.recursive_error_bound, 0)
        self.assertEqual(result.conversion_error_bound, Q(1, 48))
        self.assertEqual(result.actual_arithmetic_error, Q(1, 48))

    def test_external_errors_survive_precision_repair(self):
        result = repair_sum([10**16, 1, -10**16], absolute_tolerance=0,
                            evaluation_error=Q(1, 1000), input_error=Q(1, 10), model_error=2)
        self.assertTrue(result.satisfied)
        self.assertFalse(result.total_budget_satisfied)
        self.assertEqual(result.final.evaluation_error, Q(1, 1000))
        self.assertEqual(result.final.input_error, Q(1, 10))
        self.assertEqual(result.final.model_error, 2)
        self.assertEqual(result.final.total_error_bound, Q(2101, 1000))

    def test_zero_cases_and_gamma_premise(self):
        self.assertEqual(analyze_sum([]).condition_status, "all_zero")
        self.assertEqual(analyze_sum([1, -1]).condition_status, "infinite_zero_sum")
        large = analyze_sum([1] * 10, bits=2)
        self.assertIsNone(large.gamma)
        self.assertIsNone(large.forward_error_bound)
        self.assertGreaterEqual(large.certified_arithmetic_error, 0)
        self.assertEqual(large.exact_sum, 10)

    def test_precision_limit_and_resource_guards(self):
        result = repair_sum([Q(1, 3)], absolute_tolerance=0, initial_bits=3, max_bits=7)
        self.assertFalse(result.satisfied)
        self.assertEqual(result.attempted_bits, (3, 6, 7))
        for terms in ([float("nan")], [float("inf")], ["1e100000000"], [1] * 10001):
            with self.assertRaises(ValueError):
                analyze_sum(terms)
        with self.assertRaises(ValueError):
            analyze_sum([1], input_error=-1)
        with self.assertRaises(ValueError):
            round_binary(1, 1)
        with self.assertRaises(ValueError):
            repair_sum([1], initial_bits=53, max_bits=3)

    def test_certified_near_tie_and_unresolved_external_uncertainty(self):
        candidates = {"A": [10**16, 1, -10**16], "B": [Q(3, 4)]}
        decision = compare_sums(candidates)
        self.assertEqual(decision.winner, "A")
        self.assertEqual(decision.status, "certified_winner")
        self.assertEqual(decision.candidates["A"].final.bits, 106)
        uncertain = compare_sums(candidates, error_budgets={"A": {"model_error": 1}})
        self.assertIsNone(uncertain.winner)
        self.assertEqual(uncertain.status, "unresolved_uncertainty")
        self.assertEqual(compare_sums({"A": [1], "B": [1]}).status, "exact_tie")
        self.assertEqual(compare_sums({"A": [2], "B": [1]}, maximize=False).winner, "B")
        with self.assertRaises(ValueError):
            compare_sums(candidates, error_budgets={"C": {"model_error": 1}})
        with self.assertRaises(ValueError):
            compare_sums(candidates, error_budgets={"A": {"mystery_error": 1}})

    def test_receipt_is_serializable_and_all_checks_pass(self):
        result = receipt()
        json.dumps(result)
        self.assertTrue(all(result["checks"].values()))


if __name__ == "__main__":
    unittest.main()
