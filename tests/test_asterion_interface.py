"""The public numerical interface must preserve exact values and evidence."""
from fractions import Fraction
import json
import math
import unittest

from perfectjet.asterion import basis_bracket, convert_coordinates, convert_principal, evaluate, json_ready


class AsterionInterfaceTests(unittest.TestCase):
    def test_all_three_actual_bracket_charts(self):
        for chart, left, right in (("e8", 0, 128),
                                   ("principal", [7, 3], [11, 6]),
                                   ("jordan", [1, 0, 0, 0], [0, 1, 0, 0])):
            value = json_ready(basis_bracket(chart, left, right))
            self.assertEqual(value["arithmetic"], "exact")
            json.dumps(value, allow_nan=False)
        out = basis_bracket("jordan", [1, 0, 0, 0], [0, 1, 0, 0])
        self.assertEqual(len(out["bracket"]), 1)
        self.assertEqual(out["bracket"][0]["label"], [1, 1, 0, 0])
        self.assertEqual(out["bracket"][0]["coefficient"], ["-1", "0", "0", "0"])

    def test_conversion_roundtrip_including_zero(self):
        for vector in ({"0": "1/3", "247": "-2/7"}, {"0": 0}, {}):
            self.assertTrue(convert_principal(vector)["roundtrip_passed"])
            self.assertTrue(convert_principal(vector, inverse=True)["roundtrip_passed"])

    def test_invalid_exact_coordinate_inputs_are_rejected(self):
        for vector in ({"01": 1}, {True: 1}, {1.5: 1}, {1: 0, "1": 2},
                       {"0": True}, {"0": 0.1}, {"248": 0}, {-1: 0}):
            with self.subTest(vector=vector), self.assertRaises(ValueError):
                convert_principal(vector)
        for chart, bad in (("e8", True), ("principal", [True, 0]),
                           ("principal", 7), ("jordan", [1, False, 0, 0])):
            with self.subTest(chart=chart), self.assertRaises(ValueError):
                basis_bracket(chart, bad, bad)

    def test_all_sixteen_directed_chart_transports_keep_cyclotomic_values(self):
        charts = ("chevalley", "asterion", "principal", "jordan")
        for source in charts:
            vector = ([{"label": [1,0,0,0], "coefficient": ["1/3", "-2/5", 0, 1]}]
                      if source == "jordan" else {"0": ["1/3", "-2/5", 0, 1], "247": 2})
            for target in charts:
                with self.subTest(source=source, target=target):
                    result = convert_coordinates(source, target, vector)
                    self.assertTrue(result["roundtrip_passed"])
                    json.dumps(result, allow_nan=False)
        for source, target, vector in (("bad", "jordan", {}),
                                       ("jordan", "principal", {}),
                                       ("chevalley", "principal", {"01": 1}),
                                       ("chevalley", "principal", {"0": True})):
            with self.assertRaises(ValueError):
                convert_coordinates(source, target, vector)

    def test_strict_operations_and_lossless_serialization(self):
        self.assertEqual(json_ready(Fraction(2, 3)), "2/3")
        for value in (math.inf, -math.inf, math.nan):
            with self.assertRaises(ValueError):
                json_ready(value)
        for params in ({"operation": []}, {"operation": "unknown"},
                       {"operation": "overview", "ignored": 1},
                       {"operation": "report", "exhaustive": 1}):
            with self.assertRaises(ValueError):
                evaluate(params)


if __name__ == "__main__":
    unittest.main()
