"""Finite-X guarantees checked against separately computed exact populations."""
from fractions import Fraction as Q
import json
from math import isqrt
import subprocess
import sys
import unittest

from perfectjet.collision_asymptotic import counting_certificate, certificate_receipt
from perfectjet.collision_intervals import Interval, euler_gamma_bounds
from perfectjet.collision_research import evaluate
from perfectjet.collision_zeta import conductor_two_values


class FiniteXTests(unittest.TestCase):
    def test_exact_populations_and_fractional_endpoints(self):
        values = conductor_two_values(20000)
        points = [1, 2, 3, 4, 8, 9, 15, 16, 24, 25, 31, 32,
                  100, 997, 1024, 9999, 10000, 20000]
        counts, total = {}, 0
        for n, value in enumerate(values):
            total += value
            if n in points:
                counts[n] = total
        for n in points:
            for x in (Q(n), Q(n) + Q(1, 3)):
                row = counting_certificate(x, sigma=Q(3, 4), prime_cutoff=100)
                bounds = row['count_enclosure']
                self.assertLessEqual(bounds['lower'], counts[n])
                self.assertGreaterEqual(bounds['upper'], counts[n])
                center = row['prediction']
                self.assertLessEqual(abs(counts[n] - center), row['prediction_error_upper'])

    def test_divisor_estimate_at_jumps_and_squares(self):
        # Between integer jumps Delta(y) is decreasing because
        # d(y log y+(2gamma-1)y)/dy=log y+2gamma>0.
        # Checking each side with 6/5*sqrt(y) is a regression, not the proof.
        limit = 10000
        divisor = [0] * (limit + 1)
        for d in range(1, limit + 1):
            for n in range(d, limit + 1, d):
                divisor[n] += 1
        gamma = euler_gamma_bounds()
        total = 0
        for n in list(range(1, 100)) + [k*k for k in range(10, 101)]:
            total = sum(divisor[:n+1])
            main = Interval(n) * (Interval(n).log() + 2 * gamma - 1)
            radius = Q(6, 5) * isqrt(n)
            # Radius below the theorem's radius for nonsquares; use a
            # certified root upper in those cases.
            radius = (Interval(n).pow(Q(1,2)) * Q(6,5)).upper
            self.assertLessEqual(total - main.lower, radius)
            self.assertLessEqual(main.upper - (total - divisor[n]), radius)

    def test_auto_selection_is_certified_and_replay_serializes(self):
        row = counting_certificate(10**6, prime_cutoff=100, include_exact=True)
        self.assertEqual(row['exact_count'], 8875548)
        self.assertTrue(row['exact_count_enclosed'])
        self.assertEqual(row['remainder_upper'], min(c['remainder_upper'] for c in row['parameter_candidates']))
        receipt = certificate_receipt(10**6, sigma='3/4', prime_cutoff=100)
        json.dumps(receipt, allow_nan=False)
        self.assertEqual(receipt['schema'], 'perfectjet/conductor-two-finite-x/1')
        result = evaluate({'operation':'approximate','X':'1000000','sigma':'3/4','prime_cutoff':100})
        self.assertEqual(result, receipt)

    def test_public_cli_and_strict_inputs(self):
        completed = subprocess.run([sys.executable, '-m', 'perfectjet',
            'collision-research', 'approximate', '--x', '1000', '--sigma', '3/4',
            '--prime-cutoff', '100', '--include-exact'], capture_output=True, text=True, check=True)
        row = json.loads(completed.stdout)
        self.assertTrue(row['exact_count_enclosed'])
        for kwargs in ({'X': True}, {'X': 1.0}, {'X': 'nan'}, {'X': 0},
                       {'X':'1e1000000000'}, {'X':'1e-1000000000'},
                       {'X':10,'sigma':'1e1000000000'},
                       {'X': 10, 'sigma':'1/2'}, {'X': 10, 'sigma':'1'},
                       {'X':10,'sigma':0.75}, {'X':10,'bits':True},
                       {'X':10,'bits':31}, {'X':10,'prime_cutoff':10001},
                       {'X':10,'include_exact':1}, {'X':1<<1025},
                       {'X':10**15,'include_exact':True}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                counting_certificate(**kwargs)


if __name__ == '__main__':
    unittest.main()
