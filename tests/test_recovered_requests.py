import json
import unittest
from fractions import Fraction as Q

from perfectjet.recovered_requests import evaluate, schemas


class RecoveredRequestTests(unittest.TestCase):
    def test_every_default_and_schema_example_computes_json(self):
        for lab, schema in schemas().items():
            with self.subTest(lab=lab, kind="default"):
                self.assertIsInstance(evaluate(lab, {}), dict)
                json.dumps(evaluate(lab, {}), allow_nan=False)
            for params in [schema["sample_params"]] + schema.get("additional_samples", []):
                with self.subTest(lab=lab, params=params):
                    json.dumps(evaluate(lab, params), allow_nan=False)

    def test_unknown_keys_never_silently_fall_back_to_demo(self):
        for lab in schemas():
            with self.subTest(lab=lab):
                with self.assertRaisesRegex(ValueError, "unsupported parameter"):
                    evaluate(lab, {"not_a_parameter": 7})
        for lab, params in (("analytic", {"mode": "visible_ray", "radius": "1/5"}),
                            ("conductor", {"mode": "crt", "vector": [1, 0]})):
            with self.assertRaisesRegex(ValueError, "unsupported parameter"):
                evaluate(lab, params)
        with self.assertRaises(ValueError):
            evaluate("unknown", {})
        with self.assertRaises(ValueError):
            evaluate("theta", [])

    def test_branch_custom_probability_cost_threshold_and_risk(self):
        params = {"exact": "3/4", "frame": 0, "repeat": "1/5", "silent": "1/20",
                  "cost": 2, "max_attempts": 4, "failure_threshold": "1/10", "risk": 9}
        result = evaluate("branches", params)
        self.assertEqual(result["silent_floor"], "1/16")
        self.assertEqual(result["schedule"]["risk_price"], "9")
        self.assertEqual(result["schedule"]["best"]["max_attempts"], 4)
        self.assertEqual(evaluate("branches", dict(params, risk=0))["schedule"]["best"]["max_attempts"], 3)
        self.assertEqual(result["at_max_attempts"]["expected_cost"], str(2 * sum(Q(1, 5)**k for k in range(4))))
        rejected = evaluate("branches", dict(params, failure_threshold="1/20"))
        self.assertIsNone(rejected["schedule"]["best"])
        with self.assertRaises(ValueError):
            evaluate("branches", dict(params, exact="1/2"))
        with self.assertRaises(ValueError):
            evaluate("branches", dict(params, risk_price=1))

    def test_analytic_circle_custom_geometry_and_visible_ray_coefficients(self):
        circle = evaluate("analytic", {"mode": "log_circle", "charge": -2, "radius": "3/10", "orientation": -1})
        self.assertEqual(circle["period"]["coefficient_of_two_pi_i"], "3/5")
        with self.assertRaises(ValueError):
            evaluate("analytic", {"mode": "log_circle", "radius": "1/5", "divisors": [
                {"name": "target", "point": [0, 0], "charge": 1},
                {"name": "near", "point": ["1/10", 0], "charge": -1}]})
        ray = evaluate("analytic", {"mode": "visible_ray", "n": 12, "modulus": 3, "residue": 2})
        self.assertEqual(len(ray["coefficients"]), 12)
        self.assertTrue(ray["ratio_coefficient_identity"])
        self.assertEqual(ray["progression_coefficients"], [0, 1, 0, 0, 4, 0, 0, 4, 0, 0, 10, 0])
        self.assertEqual(ray["progression_residue_factor_times_inverse_zeta2"], "3/8")

    def test_growth_custom_graph_horizon_weights_and_self_avoidance(self):
        params = {"node_count": 2, "edges": [[0, 1, "a"], [1, 0, "b"]],
                  "weights": {"a": 2, "b": "1/10"}, "horizon": 4, "block_length": 2, "tail_minimum": 3}
        result = evaluate("growth", params)
        self.assertEqual(result["direct_path_weight"], "1/25")
        self.assertEqual(result["growth_certificate"]["block_bound"], "1/5")
        self.assertTrue(result["direct_path_sum_agrees"])
        self.assertEqual(result["growth_certificate"]["tail_minimum_length"], 3)
        avoid = evaluate("growth", dict(params, self_avoiding=True))
        self.assertEqual(avoid["histogram"]["population"], 0)
        self.assertEqual(avoid["direct_path_weight"], "0")
        terminal = evaluate("growth", dict(params, accepting=[1]))
        self.assertEqual(terminal["direct_path_weight"], "0")

    def test_conductor_custom_maps_replay_and_crt(self):
        result = evaluate("conductor", {"L": 2, "M": 6, "vector": [2, 3], "replay": False})
        self.assertEqual(result["vector"], ["2", "3"])
        self.assertEqual(len(result["pullback"]), 6)
        self.assertEqual(len(result["support_embedding"]), 6)
        self.assertIsNone(result["replay"])
        verified = evaluate("conductor", {"L": 2, "M": 4, "replay": True})
        self.assertTrue(verified["replay"]["fourier_support_to_pullback"])
        crt = evaluate("conductor", {"mode": "crt", "L": 2, "M": 3, "replay": True})
        self.assertEqual(sorted(crt["permutation"]), list(range(6)))
        self.assertTrue(crt["replay"]["fourier_factorization"])
        with self.assertRaises(ValueError):
            evaluate("conductor", {"L": 3, "M": 5})
        with self.assertRaises(ValueError):
            evaluate("conductor", {"mode": "crt", "L": 2, "M": 4})

    def test_theta_custom_rank_conductor_and_remote_index(self):
        result = evaluate("theta", {"rank": 1, "conductor": 3, "index": 10, "direct_through": 5})
        self.assertEqual(result["matrix"], [[2]])
        self.assertEqual(result["rank"], 1)
        self.assertEqual(result["conductor"], 3)
        self.assertEqual(result["remote_index"], "10")
        self.assertTrue(result["direct_coefficients_match"])
        remote = evaluate("theta", {"rank": 2, "conductor": 2, "index": str(10**80), "direct_through": 0})
        self.assertEqual(remote["remote_index"], str(10**80))

    def test_reach_custom_vector_and_projector_change_connectivity(self):
        separate = evaluate("reach", {"block_sizes": [1, 1], "vector": [1, 0]})
        joined = evaluate("reach", {"block_sizes": [1, 1], "vector": [1, 1]})
        self.assertEqual(separate["generated_algebra_dimension"], 2)
        self.assertEqual(joined["generated_algebra_dimension"], 4)
        self.assertTrue(joined["algebra_dimension_matches"])
        supplied = evaluate("reach", {"block_sizes": [1, 1], "projector": [[1, 0], [0, 0]], "verify_algebra": False})
        self.assertEqual(supplied["components"], [[0], [1]])
        self.assertNotIn("algebra_dimension_matches", supplied)
        with self.assertRaises(ValueError):
            evaluate("reach", {"block_sizes": [1, 1], "vector": [1, 0], "projector": [[1, 0], [0, 0]]})
        with self.assertRaises(ValueError):
            evaluate("reach", {"block_sizes": [1, 1], "projector": [[1, 1], [1, 0]]})

    def test_resource_limits_and_nonexact_inputs_reject_before_large_work(self):
        cases = [("branches", {"max_attempts": 129}), ("branches", {"cost": 0.1}),
                 ("analytic", {"mode": "visible_ray", "n": 513}),
                 ("analytic", {"mode": "log_circle", "radius": "1e1000000"}),
                 ("growth", {"node_count": 33}), ("conductor", {"M": 33}),
                 ("theta", {"rank": 6, "conductor": 16}),
                 ("theta", {"index": str(10**301)}), ("reach", {"block_sizes": [5, 5]})]
        for lab, params in cases:
            with self.subTest(lab=lab, params=params):
                with self.assertRaises(ValueError):
                    evaluate(lab, params)


if __name__ == "__main__":
    unittest.main()
