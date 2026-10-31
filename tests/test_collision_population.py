"""Positive collision populations checked against original ordered objects."""

from itertools import product
from math import prod
from random import Random
import json
import unittest

from perfectjet.collision_population import (
    ExponentSplitPopulation, FactorPairResiduePopulation, collision_population_receipt,
)
from perfectjet.collision import CyclotomicCollision


class CollisionPopulationTests(unittest.TestCase):
    def test_local_count_and_every_rank_against_original_splits(self):
        for L in range(1, 10):
            for exponent in range(25):
                histogram = []
                for residue in range(L):
                    population = ExponentSplitPopulation(L, exponent, residue)
                    direct = [(a, exponent - a) for a in range(exponent + 1)
                              if a * (exponent - a) % L == residue]
                    self.assertEqual(population.count(), len(direct))
                    self.assertEqual([population.unrank(i) for i in range(len(direct))], direct)
                    self.assertEqual([population.rank(pair) for pair in direct], list(range(len(direct))))
                    histogram.append(population.count())
                self.assertEqual(sum(histogram), exponent + 1)

    def test_huge_local_exponent_and_stride_recurrence(self):
        for L in (2, 4, 6, 15):
            n = 10**100 + 7
            for residue in range(L):
                population = ExponentSplitPopulation(L, n, residue)
                c1 = ExponentSplitPopulation(L, n + L, residue).count()
                c2 = ExponentSplitPopulation(L, n + 2 * L, residue).count()
                self.assertEqual(c2 - 2 * c1 + population.count(), 0)
                if population.count():
                    for rank in (0, population.count() // 2, population.count() - 1):
                        pair = population.unrank(rank)
                        self.assertTrue(population.contains(pair))
                        self.assertEqual(population.rank(pair), rank)

    def test_positive_histogram_recovers_existing_cyclotomic_coefficients(self):
        for L in range(2, 9):
            cyclotomic = CyclotomicCollision(L)
            for exponent in range(13):
                weighted = sum((ExponentSplitPopulation(L, exponent, c).count() * cyclotomic.zeta**c
                                for c in range(L)), cyclotomic.ring.zero)
                self.assertEqual(weighted, cyclotomic.direct(exponent))

    def test_factor_pairs_against_direct_divisor_enumeration(self):
        # The oracle enumerates actual m|N, independently of residue convolution.
        for factors in ((), ((2, 3),), ((2, 2), (3, 1)), ((2, 3), (3, 2), (5, 1))):
            N = prod(p**e for p, e in factors)
            for L in range(1, 8):
                direct = [[] for _ in range(L)]
                for m in range(1, N + 1):
                    if N % m:
                        continue
                    left, right, residue, exponents = m, N // m, 0, []
                    for p, _ in factors:
                        a = b = 0
                        while left % p == 0:
                            left //= p
                            a += 1
                        while right % p == 0:
                            right //= p
                            b += 1
                        exponents.append(a)
                        residue += a * b
                    direct[residue % L].append((tuple(exponents), (m, N // m)))
                for residue in range(L):
                    population = FactorPairResiduePopulation(factors, L, residue)
                    objects = sorted(direct[residue])
                    self.assertEqual(population.count(), len(objects))
                    self.assertEqual(population.histogram(), tuple(map(len, direct)))
                    for rank, (exponents, pair) in enumerate(objects):
                        self.assertEqual(population.unrank(rank), exponents)
                        self.assertEqual(population.rank(exponents), rank)
                        self.assertEqual(population.pair(rank), pair)

    def test_prefix_counts_match_independent_completion_enumeration(self):
        factors = ((2, 4), (3, 3), (5, 2))
        all_exponents = list(product(*(range(e + 1) for _, e in factors)))
        for L in (2, 4, 7):
            for residue in range(L):
                population = FactorPairResiduePopulation(factors, L, residue)
                accepted = [x for x in all_exponents if sum(a * (e - a) for a, (_, e) in zip(x, factors)) % L == residue]
                for x in all_exponents:
                    for length in range(4):
                        prefix = x[:length]
                        self.assertEqual(population.count(prefix), sum(y[:length] == prefix for y in accepted))

    def test_huge_factored_exponent_compressed_rank_and_output_guard(self):
        factors = ((2, 10**100), (3, 10**90 + 1), (5, 7))
        for residue in range(6):
            population = FactorPairResiduePopulation(factors, 6, residue)
            self.assertEqual(sum(population.histogram()), prod(e + 1 for _, e in factors))
            if population.count():
                for rank in (0, population.count() // 2, population.count() - 1):
                    exponents = population.unrank(rank)
                    self.assertTrue(population.contains(exponents))
                    self.assertEqual(population.rank(exponents), rank)
                with self.assertRaises(ValueError):
                    population.pair(0)

    def test_parity_cancellation_is_signed_not_a_population_count(self):
        for exponents in product(range(1, 6), repeat=3):
            factors = tuple(zip((2, 3, 5), exponents))
            population = FactorPairResiduePopulation(factors, 2, 0)
            expected = prod(e + 1 for e in exponents if e % 2)
            self.assertEqual(population.parity_signed_total(), expected)
            self.assertEqual(population.histogram()[0] - population.histogram()[1], expected)
        # One even exponent has a negative balanced term, though its total is +1.
        population = FactorPairResiduePopulation({2: 2}, 2, 0)
        self.assertEqual(population.histogram(), (2, 1))
        self.assertEqual(population.parity_signed_total(), 1)

    def test_sampling_is_rank_based_and_reproducible(self):
        for population in (ExponentSplitPopulation(6, 10**30, 0),
                           FactorPairResiduePopulation({2: 8, 3: 5}, 7, 0)):
            left, right = Random(721), Random(721)
            self.assertEqual([population.sample(left) for _ in range(20)],
                             [population.sample(right) for _ in range(20)])
            self.assertTrue(all(population.contains(population.sample(left)) for _ in range(20)))

    def test_strict_inputs_limits_empty_and_receipt(self):
        for bad in (True, 2.0, "2"):
            with self.assertRaises(TypeError):
                ExponentSplitPopulation(bad, 2)
            with self.assertRaises(TypeError):
                ExponentSplitPopulation(2, bad)
            with self.assertRaises(TypeError):
                FactorPairResiduePopulation({2: bad})
        for factors in ([(4, 2)], [(2, 1), (2, 2)], [(3, 0)]):
            with self.assertRaises(ValueError):
                FactorPairResiduePopulation(factors)
        with self.assertRaises(ValueError):
            ExponentSplitPopulation(100, 2, max_conductor=20)
        with self.assertRaises(ValueError):
            FactorPairResiduePopulation({2: 2, 3: 3}, 5, max_work=49)
        with self.assertRaises(ValueError):
            FactorPairResiduePopulation({101: 1}, max_trial_divisions=1)
        with self.assertRaises(ValueError):
            FactorPairResiduePopulation({2: 1}, max_factors=0)
        with self.assertRaises(ValueError):
            FactorPairResiduePopulation({2: 100}, max_input_bits=2)
        empty = ExponentSplitPopulation(2, 1, 1)
        self.assertEqual(empty.count(), 0)
        with self.assertRaises(IndexError):
            empty.unrank(0)
        with self.assertRaises(ValueError):
            empty.sample()
        empty_factor = FactorPairResiduePopulation([], 2, 1)
        self.assertEqual(empty_factor.count(), 0)
        with self.assertRaises(IndexError):
            empty_factor.unrank(0)
        with self.assertRaises(ValueError):
            empty_factor.sample()
        with self.assertRaises(ValueError):
            empty_factor.rank(())
        self.assertFalse(empty.contains((True, 0)))
        receipt = collision_population_receipt()
        json.dumps(receipt)
        self.assertTrue(receipt["local_rank_replayed"])
        self.assertTrue(receipt["factor_rank_replayed"])
        empty_receipt = collision_population_receipt(2, 1, 1)
        self.assertIsNone(empty_receipt["local_rank"])
        self.assertIsNone(empty_receipt["local_rank_replayed"])
        with self.assertRaises(IndexError):
            collision_population_receipt(2, 1, 1, 7)


if __name__ == "__main__":
    unittest.main()
