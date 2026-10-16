"""Brute paths, symbolic polynomial identities, and scoped tail checks."""
from fractions import Fraction as Q
from itertools import product
import json
import math
import random
import unittest

from perfectjet.weighted_growth import (
    ColoredGraph, GrowthCertificate, TypeHistogram, assumed_geometric_tail, receipt,
)


def brute_paths(graph, length, *, start=0, accepting=None, self_avoiding=False):
    accepted = set(range(graph.node_count)) if accepting is None else set(accepting)
    result = []
    for word in product(range(len(graph.edges)), repeat=length):
        state, visited = start, {start}
        for index in word:
            edge = graph.edges[index]
            if edge.source != state or (self_avoiding and edge.target in visited):
                break
            state = edge.target
            visited.add(state)
        else:
            if state in accepted:
                result.append(word)
    return result


class WeightedGrowthTests(unittest.TestCase):
    def test_exact_partition_derivatives_and_covariance(self):
        # Z=2*x^2+3*x*y+4*y^2, checked from elementary formulas.
        histogram = TypeHistogram(("x", "y"), {(2, 0): 2, (1, 1): 3, (0, 2): 4})
        evaluation = histogram.evaluate({"x": 2, "y": 3})
        self.assertEqual(evaluation.partition, 62)
        self.assertEqual(evaluation.weight_derivatives, (17, 30))
        self.assertEqual(evaluation.mean_counts, (Q(17, 31), Q(45, 31)))
        expected_second_x = Q(4 * 8 + 18, 62)
        self.assertEqual(evaluation.covariance[0][0], expected_second_x - Q(17, 31)**2)
        self.assertEqual(evaluation.covariance[0][1], -evaluation.covariance[0][0])
        self.assertEqual(evaluation.covariance[1][1], evaluation.covariance[0][0])
        self.assertGreater(evaluation.covariance[0][0], 0)
        self.assertTrue(evaluation.to_dict()["log_sensitivity_valid"])

    def test_zero_weights_preserve_polynomial_derivatives(self):
        histogram = TypeHistogram(("x", "y"), {(1, 1): 3, (0, 2): 4})
        evaluation = histogram.evaluate([0, 2])
        self.assertEqual(evaluation.partition, 16)
        self.assertEqual(evaluation.weight_derivatives, (6, 16))
        self.assertFalse(evaluation.to_dict()["log_sensitivity_valid"])
        empty = TypeHistogram(("x",), {}).evaluate([0])
        self.assertEqual(empty.partition, 0)
        self.assertIsNone(empty.mean_counts)
        self.assertIsNone(empty.covariance)

    def test_compiled_histogram_is_owned_and_requires_exact_type_shapes(self):
        source = {(1,): 2}
        histogram = TypeHistogram(("x",), source)
        source[(1,)] = 100
        self.assertEqual(histogram.population, 2)
        with self.assertRaises(TypeError):
            histogram.counts[(1,)] = 3
        for names, counts in [(("x", "x"), {}), (("x",), {(1, 0): 1}),
                              (("x",), {(-1,): 1}), (("x",), {(1,): -1})]:
            with self.assertRaises(ValueError):
                TypeHistogram(names, counts)
        with self.assertRaises(ValueError):
            histogram.evaluate({"wrong": 1})
        with self.assertRaises(ValueError):
            histogram.evaluate([-1])

    def test_graph_histogram_against_independent_exhaustive_words(self):
        rng = random.Random(912)
        for _ in range(14):
            nodes = rng.randint(1, 4)
            edges = [(rng.randrange(nodes), rng.randrange(nodes), rng.choice(("A", "B"))) for _ in range(4)]
            graph = ColoredGraph(nodes, edges, ("A", "B"))
            for length in range(5):
                for avoiding in (False, True):
                    paths = brute_paths(graph, length, accepting={nodes - 1}, self_avoiding=avoiding)
                    expected = {}
                    for word in paths:
                        counts = tuple(sum(graph.edges[i].color == color for i in word) for color in graph.type_names)
                        expected[counts] = expected.get(counts, 0) + 1
                    actual = graph.histogram(length, accepting={nodes - 1}, self_avoiding=avoiding)
                    self.assertEqual(dict(actual.counts), expected)
                    weights = {"A": Q(1, 3), "B": Q(2, 5)}
                    brute_mass = sum((math.prod(weights[graph.edges[i].color] for i in word) for word in paths), Q(0))
                    self.assertEqual(actual.evaluate(weights).partition, brute_mass)
                    self.assertEqual(graph.weighted_paths(length, weights, accepting={nodes - 1},
                                                         self_avoiding=avoiding), brute_mass)

    def test_parallel_edges_and_invalid_path_order(self):
        graph = ColoredGraph(2, [(0, 1, "A"), (0, 1, "A"), (1, 0, "B")])
        self.assertEqual(graph.histogram(2).population, 2)
        self.assertEqual(graph.path_weight([0, 2], {"A": 2, "B": 3}), 6)
        with self.assertRaises(ValueError):
            graph.path_weight([2, 0], {"A": 2, "B": 3})

    def test_order_sensitive_prices_are_not_collapsed_to_counts(self):
        graph = ColoredGraph(1, [(0, 0, "A"), (0, 0, "B")])
        base = {"A": 1, "B": 1}
        chronology = [{"A": 10, "B": 1}, {"A": 1, "B": 10}]
        self.assertEqual(graph.path_weight([0, 1], base, position_weights=chronology), 100)
        self.assertEqual(graph.path_weight([1, 0], base, position_weights=chronology), 1)
        self.assertEqual(graph.weighted_paths(2, base, position_weights=chronology), 121)
        self.assertEqual(graph.histogram(2).evaluate(base).partition, 4)
        with self.assertRaises(ValueError):
            graph.weighted_paths(2, base, position_weights=chronology[:1])

    def test_stable_log_partition_is_explicitly_uncertified(self):
        histogram = TypeHistogram(("A", "B"), {(1, 0): 2, (0, 1): 3})
        result = histogram.log_partition([1000, 999])
        self.assertAlmostEqual(result["log_partition"], 1000 + math.log(2 + 3 / math.e))
        self.assertIsNone(result["partition"])
        self.assertIsNone(result["rigorous_exponential_error_bound"])
        exact = histogram.evaluate([2, 3])
        approximate = histogram.log_partition([math.log(2), math.log(3)])
        self.assertAlmostEqual(approximate["partition"], float(exact.partition))
        for x, y in zip(approximate["mean_counts"], exact.mean_counts):
            self.assertAlmostEqual(x, float(y))
        self.assertEqual(TypeHistogram(("A",), {}).log_partition([0])["status"], "empty_population")

    def test_row_sum_and_block_tail_dominate_every_checked_length(self):
        graph = ColoredGraph(2, [(0, 1, "heavy"), (1, 0, "light")])
        weights = {"heavy": 2, "light": Q(1, 10)}
        row = graph.row_sum_certificate(weights)
        self.assertFalse(row.subcritical)
        with self.assertRaises(ValueError):
            row.tail()
        block = graph.block_certificate(weights, 2)
        self.assertEqual(block.block_bound, Q(1, 5))
        self.assertEqual(block.remainder_bounds, (1, 2))
        self.assertTrue(block.subcritical)
        self.assertEqual(block.tail(0), Q(15, 4))
        for d in range(10):
            # Here the worst start is 0 for odd lengths; even totals are identical.
            partial = sum((graph.weighted_paths(n, weights, start=0) for n in range(d, 40)), Q(0))
            self.assertLessEqual(partial, block.tail(d))
        self.assertEqual(block.scope, "finite_graph_all_walks")
        self.assertFalse(block.to_dict()["external_infinite_graph_claim"])
        conditional = graph.block_certificate(weights, 2, external_domination="Every external length-n path maps injectively with no larger weight.")
        self.assertTrue(conditional.conditional)
        self.assertTrue(conditional.to_dict()["external_infinite_graph_claim"])
        self.assertIn("UNPROVED", conditional.assumptions[-1])

    def test_arbitrary_finite_census_cannot_supply_infinite_growth(self):
        # Terminal finite graph admits zero paths after one step.  Nothing here
        # asserts that a larger graph has no omitted outgoing edges.
        graph = ColoredGraph(2, [(0, 1, "x")])
        certificate = graph.block_certificate([100], 2)
        self.assertEqual(certificate.block_bound, 0)
        self.assertEqual(certificate.tail(2), 0)
        self.assertEqual(certificate.scope, "finite_graph_all_walks")
        with self.assertRaises(ValueError):
            graph.row_sum_certificate([Q(1, 2)], external_domination="")
        with self.assertRaises(ValueError):
            assumed_geometric_tail(Q(1, 2), 2, domination_assumption="")
        assumed = assumed_geometric_tail(Q(1, 2), 3, prefactor=4,
                                         domination_assumption="For every n, total target mass is <=4*(1/2)^n.")
        self.assertEqual(assumed["tail_bound"], "1")
        self.assertTrue(assumed["conditional"])
        self.assertIn("UNPROVED", assumed["assumptions"][0])

    def test_empty_graph_and_invalid_certificate_shapes(self):
        graph = ColoredGraph(2, [])
        self.assertEqual(graph.histogram(0).evaluate([]).partition, 1)
        self.assertEqual(graph.histogram(1).evaluate([]).partition, 0)
        self.assertEqual(graph.row_sum_certificate([]).tail(1), 0)
        self.assertEqual(graph.row_sum_certificate([]).tail(0), 1)
        for block, bound, remainders in ((0, Q(1, 2), (1,)),
                                         (2, Q(1, 2), (1,)),
                                         (1, -1, (1,)),
                                         (1, Q(1, 2), (-1,))):
            with self.assertRaises(ValueError):
                GrowthCertificate(block, bound, remainders, "test", ("assumption",))

    def test_resource_guards(self):
        graph = ColoredGraph(1, [(0, 0, "A"), (0, 0, "B")])
        with self.assertRaises(ValueError):
            graph.histogram(10, max_frontier=1)
        with self.assertRaises(ValueError):
            graph.histogram(10, max_expansions=1)
        with self.assertRaises(ValueError):
            graph.histogram(1000000)
        with self.assertRaises(ValueError):
            ColoredGraph(1, [(0, 1, "A")])
        with self.assertRaises(ValueError):
            TypeHistogram(("A",), {(513,): 1})
        with self.assertRaises(ValueError):
            graph.weighted_paths(512, [Q(1, 2**3000), Q(1, 2**3000)])
        with self.assertRaises(ValueError):
            assumed_geometric_tail(Q(1, 2**4000), 10000, domination_assumption="All-length bound supplied.")
        with self.assertRaises(ValueError):
            TypeHistogram(("A",), {(1,): 1}).evaluate(iter(range(1000000000)))

    def test_receipt_is_serializable_and_checks_pass(self):
        result = receipt()
        json.dumps(result)
        self.assertTrue(all(result["checks"].values()))


if __name__ == "__main__":
    unittest.main()
