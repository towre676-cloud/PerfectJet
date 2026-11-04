"""Build/check deterministic finite-X certificates and exact comparison receipts."""
from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def _compact(certificate):
    keys = ("X", "floor_X", "sigma", "prime_cutoff", "bits", "prediction",
            "main_term", "remainder_upper", "prediction_error_upper",
            "count_enclosure", "exact_count", "observed_error", "exact_count_enclosed",
            "selected_remainder_method", "remainder_candidates")
    record = {key: certificate[key] for key in keys if key in certificate}
    record["parameter_candidates"] = [
        {key: row[key] for key in ("sigma", "B_upper", "remainder_upper")}
        for row in certificate["parameter_candidates"]
    ]
    return record


def build():
    from perfectjet.collision_asymptotic import counting_certificate
    from perfectjet.collision_counting import coefficient_sieve, exact_count, exact_counts
    from perfectjet.collision_intervals import asymptotic_constants
    from perfectjet.collision_intervals import Interval
    from perfectjet.collision_constant_extraction import extracted_asymptotic_constants
    from perfectjet.collision_research import json_value
    from perfectjet.collision_zeta import conductor_two_values

    # Independent coefficient construction: prime-power updates versus the
    # pre-existing least-prime recurrence.  Every input in this range is checked.
    limit = 100_000
    sieve = coefficient_sieve(limit)
    original = conductor_two_values(limit)
    if list(sieve) != original:
        raise ArithmeticError("independent coefficient sieves disagree")
    samples = sorted(set([0, 1, 2, 3, limit] + [1 + (i * 7919) % limit for i in range(200)]))
    prefix, total = {}, 0
    wanted = set(samples)
    for n, value in enumerate(original):
        total += value
        if n in wanted:
            prefix[n] = total
    for n in samples:
        if exact_count(n) != prefix[n]:
            raise ArithmeticError(f"independent cumulative replay failed at {n}")
    decade_counts = exact_counts([10**k for k in range(8)], method="sieve")
    for n, count in decade_counts.items():
        if exact_count(n) != count:
            raise ArithmeticError(f"sieve/convolution decade replay failed at {n}")

    # Include every decade through 10^12, perturbations at square and prime
    # powers, and nonintegral X at either side of count discontinuities.
    points = sorted(set([Fraction(10**k) for k in range(13)] + [
        Fraction(n) for n in (1023, 1024, 1025, 65535, 65536, 65537,
                             531440, 531441, 531442, 999999, 1000001)
    ] + [Fraction(3, 2), Fraction(1999999, 2), Fraction(2000001, 2)]))
    comparisons = [_compact(counting_certificate(point, include_exact=True)) for point in points]
    # Compare all eleven rational sigma candidates at each cutoff.  Selection
    # minimizes rigorous upper radii; it never fits the known exact answer.
    optimization = []
    for exponent in (2, 6, 8, 10, 12, 18, 24):
        for cutoff in (100, 1000, 10000):
            row = _compact(counting_certificate(10**exponent, prime_cutoff=cutoff))
            row["relative_prediction_error_upper"] = row["prediction_error_upper"] / max(Fraction(1), row["prediction"])
            optimization.append(row)
    # A matched comparison preserves cutoff, precision, and the sigma grid.
    # The baseline uses the direct constant intervals and the sigma theorem;
    # the new certificate may also select the independent sqrt/log theorem.
    constant_comparisons, improvements = [], []
    for cutoff in (1000, 10000):
        direct = asymptotic_constants(prime_cutoff=cutoff)
        extracted = extracted_asymptotic_constants(prime_cutoff=cutoff)
        constant_row = {"prime_cutoff": cutoff, "bits": 80, "constants": {}}
        sample = counting_certificate(1, prime_cutoff=cutoff)
        for name in ("C", "D", "K"):
            intersected = sample["constants"][name]
            old_width = direct[name].upper - direct[name].lower
            extracted_width = extracted[name].upper - extracted[name].lower
            new_width = Fraction(intersected["upper"]) - Fraction(intersected["lower"])
            constant_row["constants"][name] = {
                "direct": direct[name].record(), "extracted": extracted[name].record(),
                "intersection": intersected, "direct_width": old_width,
                "extracted_width": extracted_width, "intersection_width": new_width,
                "direct_to_extracted_width_ratio": old_width / extracted_width,
                "direct_to_intersection_width_ratio": old_width / new_width,
            }
        constant_comparisons.append(constant_row)
        for exponent in (6, 12, 24, 100):
            X = 10**exponent
            current = counting_certificate(X, prime_cutoff=cutoff)
            x = Interval(X)
            baseline_main = direct["C"] * x * x.log() + direct["K"] * x
            baseline_remainder = min(row["remainder_upper"] for row in current["parameter_candidates"])
            baseline_error = baseline_remainder + (baseline_main.upper - baseline_main.lower) / 2
            new_error = current["prediction_error_upper"]
            improvements.append({
                "X": X, "prime_cutoff": cutoff, "bits": 80,
                "baseline_method": "direct constants and minimum sigma-grid remainder",
                "baseline_prediction": (baseline_main.lower + baseline_main.upper) / 2,
                "baseline_main_term": baseline_main.record(),
                "baseline_remainder_upper": baseline_remainder,
                "baseline_prediction_error_upper": baseline_error,
                "current": _compact(current),
                "guaranteed_prediction_error_improvement_factor": baseline_error / new_error,
                "analytic_remainder_improvement_factor": baseline_remainder / current["remainder_upper"],
            })
    constants = counting_certificate(1, prime_cutoff=10000)["constants"]
    return json_value({
        "schema": "perfectjet/collision-finite-x-replay/2",
        "coefficient_replay": {"every_n_through": limit, "coefficients_equal": True,
                               "methods": ["prime-power update sieve", "pre-existing least-prime recurrence"]},
        "cumulative_replay": {"sample_count": len(samples), "every_comparison_equal": True,
                              "integer_inputs": samples},
        "sieve_convolution_decade_replay": {"all_equal": True, "counts": {str(n): count for n, count in decade_counts.items()},
                                           "sieve_computed_through": 10_000_000},
        "constant_intervals": constants,
        "constant_extraction_comparison": constant_comparisons,
        "certificate_improvement_study": improvements,
        "exact_comparisons": comparisons,
        "parameter_study": optimization,
        "all_exact_counts_enclosed": all(row["exact_count_enclosed"] for row in comparisons),
        "proof": "docs/COLLISION_FINITE_X.md",
        "interpretation": "Guaranteed intervals follow from the written theorems and rational interval algorithms. Observed errors are exact-count comparisons, not a replacement for the remainder theorems. Auto compares the finite sigma grid and the independently proved sqrt/log remainder. Improvement rows compare the old direct-constant, sigma-only certificate with the current certificate at the same cutoff, precision and sigma grid.",
    })


def sources():
    paths = ["scripts/verify_collision_finite_x.py", "independent_checks/collision_finite_x/verify.py",
             "src/perfectjet/collision_research.py", "src/perfectjet/mathlab.py", "src/perfectjet/cli.py",
             "docs/COLLISION_FINITE_X.md", "docs/COLLISION_ASYMPTOTICS.md"]
    paths += ["src/perfectjet/" + name for name in (
        "collision_asymptotic.py", "collision_counting.py", "collision_intervals.py", "collision_majorant.py",
        "collision_constants.py", "collision_zeta.py", "collision.py",
        "collision_zeta_intervals.py", "collision_constant_extraction.py", "collision_sqrt_remainder.py")]
    paths += [path.relative_to(ROOT).as_posix() for path in (ROOT / "docs").glob("COLLISION_*.md")]
    paths += [path.relative_to(ROOT).as_posix() for path in (ROOT / "tests").glob("test_collision*.py")]
    return {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in sorted(set(paths))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build()
    encoded = json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    manifest = {"schema": "perfectjet/collision-finite-x-source-manifest/1",
                "source_sha256": sources(),
                "validation_sha256": hashlib.sha256(encoded.encode()).hexdigest()}
    directory = ROOT / "results/collision-finite-x"
    directory.mkdir(parents=True, exist_ok=True)
    for name, content in {"validation.json": encoded,
                          "manifest.json": json.dumps(manifest, indent=2) + "\n"}.items():
        path = directory / name
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != content:
                raise ValueError("stale finite-X replay: " + name)
        else:
            path.write_text(content, encoding="utf-8")
    print(json.dumps({"status": "passed", "mode": "check" if args.check else "build",
                      "all_coefficients_through": report["coefficient_replay"]["every_n_through"],
                      "independent_cumulative_samples": report["cumulative_replay"]["sample_count"],
                      "exact_comparisons": len(report["exact_comparisons"]),
                      "parameter_study_rows": len(report["parameter_study"]),
                      "constant_comparison_cutoffs": len(report["constant_extraction_comparison"]),
                      "certificate_improvement_rows": len(report["certificate_improvement_study"])}))


if __name__ == "__main__":
    main()
