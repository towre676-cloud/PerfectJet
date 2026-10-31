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
            "count_enclosure", "exact_count", "observed_error", "exact_count_enclosed")
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
    constants = asymptotic_constants(prime_cutoff=10000)
    return json_value({
        "schema": "perfectjet/collision-finite-x-replay/1",
        "coefficient_replay": {"every_n_through": limit, "coefficients_equal": True,
                               "methods": ["prime-power update sieve", "pre-existing least-prime recurrence"]},
        "cumulative_replay": {"sample_count": len(samples), "every_comparison_equal": True,
                              "integer_inputs": samples},
        "sieve_convolution_decade_replay": {"all_equal": True, "counts": {str(n): count for n, count in decade_counts.items()},
                                           "sieve_computed_through": 10_000_000},
        "constant_intervals": {key: constants[key].record() for key in ("C", "D", "gamma", "K")},
        "exact_comparisons": comparisons,
        "parameter_study": optimization,
        "all_exact_counts_enclosed": all(row["exact_count_enclosed"] for row in comparisons),
        "proof": "docs/COLLISION_FINITE_X.md",
        "interpretation": "Guaranteed intervals follow from the written theorem and rational interval algorithms. Observed errors are exact-count comparisons, not a replacement for the remainder theorem. Auto chooses the smallest certified radius on its stated finite grid; no global parameter optimality is asserted.",
    })


def sources():
    paths = ["scripts/verify_collision_finite_x.py", "independent_checks/collision_finite_x/verify.py",
             "src/perfectjet/collision_research.py", "src/perfectjet/mathlab.py", "src/perfectjet/cli.py",
             "docs/COLLISION_FINITE_X.md", "docs/COLLISION_ASYMPTOTICS.md"]
    paths += ["src/perfectjet/" + name for name in (
        "collision_asymptotic.py", "collision_counting.py", "collision_intervals.py", "collision_majorant.py",
        "collision_constants.py", "collision_zeta.py", "collision.py")]
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
                      "parameter_study_rows": len(report["parameter_study"])}))


if __name__ == "__main__":
    main()
