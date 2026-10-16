import itertools
import json
import random
import unittest
from fractions import Fraction as Q

from perfectjet.branch_channels import (
    Branch, BranchPartition, OutcomeKind, RetryModel, receipt,
)


def exhaustive_attempt_paths(model, depth):
    """Integrate over full iid paths, then stop each at its first nonrepeat."""
    total = {key: Q() for key in ("exact", "frame", "silent", "exhausted", "failure", "attempts", "cost")}
    for path in itertools.product(model.partition.branches, repeat=depth):
        probability = Q(1)
        for branch in path:
            probability *= branch.probability
        paid, attempts, kind = Q(), 0, None
        for branch in path:
            paid += model.attempt_cost + branch.cost
            attempts += 1
            if branch.kind is not OutcomeKind.REPEAT:
                kind = branch.kind.value
                break
        if kind is None:
            kind = "exhausted"
            paid += model.exhaustion_cost
        total[kind] += probability
        total["attempts"] += probability * attempts
        total["cost"] += probability * paid
        total["failure"] += probability * (1 if kind == "silent" else model.exhaustion_failure if kind == "exhausted" else 0)
    return total


class BranchChannelTests(unittest.TestCase):
    def test_exact_conservation_and_disjoint_event_validation(self):
        partition = BranchPartition((Branch("yes", "exact", "2/3"), Branch("again", "repeat", "1/3")))
        self.assertEqual(partition.probability("exact"), Q(2, 3))
        self.assertEqual(partition.probability("frame"), 0)
        for branches in ((), (Branch("bad total", "exact", "2/3"),),
                         (Branch("same", "exact", "1/2"), Branch("same", "silent", "1/2"))):
            with self.assertRaises(ValueError):
                BranchPartition(branches)
        for probability in ("-1/10", "11/10"):
            with self.assertRaises(ValueError):
                Branch("bad probability", "exact", probability)
        with self.assertRaises(TypeError):
            Branch("floating", "exact", 0.5)
        with self.assertRaises(ValueError):
            Branch("two kinds", "exact,frame", 1)
        with self.assertRaises(ValueError):
            Branch("incorrect correction", "repeat", 1, correction="X")

    def test_retry_formulas_against_full_independent_path_enumeration(self):
        rng = random.Random(624)
        for _ in range(20):
            weights = [rng.randrange(1, 12) for _ in range(4)]
            total = sum(weights)
            partition = BranchPartition(tuple(Branch(kind.value, kind, Q(weight, total), Q(rng.randrange(4), 3))
                                               for kind, weight in zip(OutcomeKind, weights)))
            model = RetryModel(partition, Q(5, 7), Q(2, 3), Q(4, 9))
            for depth in (1, 2, 4):
                observed = model.evaluate(depth)
                reference = exhaustive_attempt_paths(model, depth)
                self.assertEqual(observed.exact_probability, reference["exact"])
                self.assertEqual(observed.frame_probability, reference["frame"])
                self.assertEqual(observed.silent_probability, reference["silent"])
                self.assertEqual(observed.exhausted_probability, reference["exhausted"])
                self.assertEqual(observed.effective_failure, reference["failure"])
                self.assertEqual(observed.expected_attempts, reference["attempts"])
                self.assertEqual(observed.expected_cost, reference["cost"])
                self.assertEqual(observed.accepted_probability + observed.exhausted_probability, 1)

    def test_scheduler_matches_explicit_objective_and_strict_threshold(self):
        model = RetryModel(BranchPartition((Branch("done", "exact", "3/4"),
                                           Branch("repeat", "repeat", "6/25"),
                                           Branch("wrong", "silent", "1/100"))))
        scheduled = model.optimize(12, "1/30", "10", [1, 2, 4, 7, 12])
        candidates = [model.evaluate(d) for d in (1, 2, 4, 7, 12)]
        valid = [c for c in candidates if c.effective_failure < Q(1, 30)]
        chosen = min(valid, key=lambda r: (r.expected_cost + 10 * r.effective_failure, r.max_attempts))
        self.assertEqual(scheduled.best, chosen)
        constant = RetryModel(BranchPartition((Branch("safe", "exact", "99/100"), Branch("wrong", "silent", "1/100"))))
        self.assertIsNone(constant.optimize(100, "1/100").best)

    def test_silent_floor_cannot_be_removed_by_deeper_repetition(self):
        model = RetryModel(BranchPartition((Branch("safe", "exact", "7/10"),
                                           Branch("repeat", "repeat", "1/5"),
                                           Branch("silent", "silent", "1/10"))))
        self.assertEqual(model.silent_floor, Q(1, 8))
        result = model.optimize(100, "1/10")
        self.assertIsNone(result.best)
        self.assertIn("floor blocks every finite depth", result.reason)
        for depth in (1, 3, 10, 100):
            observed = model.evaluate(depth)
            self.assertGreater(observed.effective_failure, model.silent_floor)
            self.assertEqual(observed.silent_given_acceptance, model.silent_floor)
        # If exhaustion is a harmless rejection, silent mass increases with
        # retries; the limit is not a lower bound on finite unconditional risk.
        harmless = RetryModel(model.partition, exhaustion_failure=0)
        self.assertLess(harmless.evaluate(1).effective_failure, harmless.silent_floor)
        self.assertIsNotNone(harmless.optimize(10, "11/100").best)

    def test_degenerate_repeat_and_success_models(self):
        repeat = RetryModel(BranchPartition((Branch("always again", "repeat", 1),)), exhaustion_failure="1/3")
        r = repeat.evaluate(17)
        self.assertEqual(r.expected_attempts, 17)
        self.assertEqual(r.effective_failure, Q(1, 3))
        self.assertEqual(r.exhausted_probability, 1)
        self.assertIsNone(r.silent_given_acceptance)
        self.assertEqual(repeat.asymptotic_failure, Q(1, 3))
        success = RetryModel(BranchPartition((Branch("always yes", "exact", 1),)))
        self.assertEqual(success.optimize(6, 1).best.max_attempts, 1)
        self.assertEqual(success.evaluate(6).expected_attempts, 1)

    def test_model_and_schedule_validation_and_json_receipt(self):
        partition = BranchPartition((Branch("done", "exact", 1),))
        for kwargs in ({"attempt_cost": -1}, {"exhaustion_failure": 2}, {"exhaustion_cost": -2}):
            with self.assertRaises(ValueError):
                RetryModel(partition, **kwargs)
        model = RetryModel(partition)
        for depth in (-1, 0, True, "2"):
            with self.assertRaises(ValueError):
                model.evaluate(depth)
        for depths in ([], [0], [4], [True], [1, "2"]):
            with self.assertRaises(ValueError):
                model.optimize(3, 1, allowed_depths=depths)
        json.dumps(receipt())


if __name__ == "__main__":
    unittest.main()
