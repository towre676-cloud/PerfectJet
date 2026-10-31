"""Independent local identities and finite-product checks for extracted constants."""
from decimal import Decimal, localcontext
from fractions import Fraction as Q
from math import isqrt
import json
import unittest

from perfectjet.collision_constant_extraction import (
    extracted_asymptotic_constants, residual_derivative_weight,
    residual_factor, residual_tail_bounds,
)
from perfectjet.collision_intervals import asymptotic_constants, log_bounds
from perfectjet.collision_research import json_value


# Independent 100-digit reference evaluations, used only for regression.
# The production proof and endpoints never use these decimal constants.
ZETA2 = Decimal('1.644934066848226436472415166646025189218949901206798437735558229370007470403200873833628900619758705304004319')
ZETA2_PRIME = Decimal('-0.93754825431584375370257409456786497789786028861482992588543348036044381131270752279368941514115151749311382116')


def fraction(value):
    return Q(str(value))


class ExtractedConstantTests(unittest.TestCase):
    def test_rational_local_identity_and_independent_derivative(self):
        for p in range(2, 201):
            x = Q(1, p)
            numerator = 1 + 2*x - x*x
            denominator = (1-x)**2 * (1+x)**4
            r = numerator / denominator
            self.assertEqual(residual_factor(p), r)
            self.assertEqual((1-x*x)**2 * r, 1 - 2*x*x/(1+x)**2)
            # Literal quotient differentiation of N(x)/D(x), separate from
            # production's simplified derivative weight.
            numerator_prime = 2 - 2*x
            denominator_prime = -2*(1-x)*(1+x)**4 + 4*(1-x)**2*(1+x)**3
            g = x * (numerator_prime*denominator - numerator*denominator_prime) / (denominator*numerator)
            self.assertEqual(residual_derivative_weight(p), g)
            self.assertGreater(r, 1)
            self.assertGreater(g, 0)
            self.assertLessEqual(g, 12*x**3)
            # Differentiating the extracted zeta factor recovers the direct
            # H'(1)/H(1) local coefficient exactly, including its sign.
            self.assertEqual(Q(4, p*p-1) - g,
                             Q(4*p, (p+1)*(p*p+2*p-1)))

    def test_log_residual_bound_on_dense_rational_arguments(self):
        for p in range(2, 102):
            value = log_bounds(residual_factor(p))
            self.assertGreaterEqual(value.lower, 0)
            self.assertLessEqual(value.upper, Q(4, p**3))

    def test_prime_tails_dominate_independent_long_residual_sums(self):
        primes = [n for n in range(2, 20001)
                  if all(n % d for d in range(2, isqrt(n)+1))]
        with localcontext() as context:
            context.prec = 100
            rows = []
            for p in primes:
                v = Decimal(p)
                r = v**4*(v*v+2*v-1)/((v-1)**2*(v+1)**4)
                g = 4*(3*v-1)/((v*v-1)*(v*v+2*v-1))
                rows.append((p, r.ln(), v.ln()*g))
            for p in (2, 7, 100, 1000, 10000):
                tail = residual_tail_bounds(p)
                effective = tail['effective_prime_cutoff']
                direct_log = fraction(sum((a for prime,a,_ in rows if prime > effective), Decimal(0)))
                direct_derivative = fraction(sum((a for prime,_,a in rows if prime > effective), Decimal(0)))
                self.assertGreaterEqual(direct_log, tail['log_tail'].lower)
                self.assertLessEqual(direct_log, tail['log_tail'].upper)
                self.assertGreaterEqual(direct_derivative, tail['derivative_magnitude_tail'].lower)
                self.assertLessEqual(direct_derivative, tail['derivative_magnitude_tail'].upper)

    def test_long_independent_extracted_products_fit_short_certificates(self):
        primes = [n for n in range(2, 20001)
                  if all(n % d for d in range(2, isqrt(n)+1))]
        with localcontext() as context:
            context.prec = 100
            residual, derivative = Decimal(1), Decimal(0)
            for p in primes:
                v = Decimal(p)
                residual *= v**4*(v*v+2*v-1)/((v-1)**2*(v+1)**4)
                derivative += v.ln()*4*(3*v-1)/((v*v-1)*(v*v+2*v-1))
            c = fraction(residual/ZETA2**2)
            d = fraction(-4*ZETA2_PRIME/ZETA2 - derivative)
        for p in (2, 7, 100, 1000, 10000):
            row = extracted_asymptotic_constants(p)
            self.assertLessEqual(row['C'].lower, c)
            self.assertGreaterEqual(row['C'].upper, c)
            self.assertLessEqual(row['D'].lower, d)
            self.assertGreaterEqual(row['D'].upper, d)
            old = asymptotic_constants(p)
            for key in ('C','D','K'):
                self.assertLessEqual(row[key].lower, old[key].upper)
                self.assertGreaterEqual(row[key].upper, old[key].lower)
            self.assertGreater(row['K'].lower, 0)

    def test_practical_width_improvement_and_evidence_signs(self):
        new, old = extracted_asymptotic_constants(1000), asymptotic_constants(1000)
        self.assertLess(600*new['C'].width, old['C'].width)
        self.assertLess(400*new['D'].width, old['D'].width)
        self.assertLess(400*new['K'].width, old['K'].width)
        evidence = new['evidence']
        self.assertEqual(Q(evidence['residual_log_tail']['lower']), 0)
        self.assertEqual(Q(evidence['residual_derivative_tail']['upper']), 0)
        self.assertLess(Q(evidence['residual_derivative_tail']['lower']), 0)
        json.dumps(json_value(evidence), allow_nan=False)
        evidence['tail_method'] = 'mutated'
        self.assertNotEqual(extracted_asymptotic_constants(1000)['evidence']['tail_method'], 'mutated')
        for bits in (32, 128, 256):
            row = extracted_asymptotic_constants(100, bits=bits)
            self.assertLessEqual(row['C'].lower, new['C'].upper)
            self.assertGreaterEqual(row['C'].upper, new['C'].lower)

    def test_preflight_arguments_and_small_cutoff(self):
        for bad in (True, False, -1, 0, 1, '100', 100.0, None, 10001):
            with self.subTest(value=bad), self.assertRaises(ValueError):
                extracted_asymptotic_constants(bad)
        for bits in (True, 31, 257, 80.0):
            with self.assertRaises(ValueError):
                extracted_asymptotic_constants(100, bits=bits)
        for p in (True, 1, 1.0, '2', 1 << 65):
            for fn in (residual_factor, residual_derivative_weight):
                with self.assertRaises(ValueError):
                    fn(p)
        a, b = extracted_asymptotic_constants(2), extracted_asymptotic_constants(7)
        self.assertEqual(a['effective_prime_cutoff'], 7)
        self.assertEqual(a['prime_count'], 4)
        self.assertEqual(a['C'], b['C'])
        self.assertEqual(a['D'], b['D'])


if __name__ == '__main__':
    unittest.main()
