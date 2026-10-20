"""Asterion basis calculus: exact arithmetic, queries and replay receipts.

The coined name describes this program and its prescribed coordinate charts.
It does not assert priority for the classical principal or Jordan gradings.
Run ``python -m perfectjet asterion --help`` for the numerical interface.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import statistics
import time


NOMENCLATURE = {
    "name": "Asterion basis calculus",
    "symbol": "A_(sigma,j)",
    "sector": "sigma identifies a polynomial module, finite grade, or compiled seed",
    "position": "j identifies a chain position or a direction inside a grade",
    "basis_contract": "ordered independent vectors, exact inverse, bracket transport, normalization and evidence",
    "priority_scope": "coined program nomenclature and explicit implementation; no worldwide naming or mathematical-priority claim",
}


def json_ready(value):
    """Lossless JSON encoding of rational/cyclotomic records and tuple keys."""
    if isinstance(value, Fraction):
        return value.numerator if value.denominator == 1 else str(value)
    if hasattr(value, "to_json"):
        return json_ready(value.to_json())
    if isinstance(value, dict):
        return {str(k): json_ready(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [json_ready(v) for v in value]
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("nonfinite numbers are not Asterion exact data")
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    raise TypeError(f"unsupported Asterion record type: {type(value).__name__}")


def vector_record(vector):
    return [{"label": json_ready(k), "coefficient": json_ready(v)}
            for k, v in sorted(vector.items()) if v]


def source_digests():
    folder = Path(__file__).parent
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(folder.glob("asterion*.py"))}


def report(*, exhaustive=False, include_tables=False):
    """Construct the actual algebras and replay the explicitly selected scope."""
    from .asterion_e8 import E8LieAlgebra, e8_receipt
    from .asterion_principal import PrincipalE8
    from .asterion_jordan import JordanE8, construction_receipt
    from .asterion_basis import basis_receipt, e8_response_receipt
    from .asterion_deformations import deformation_receipt
    from .asterion_transport import transport_receipt

    algebra = E8LieAlgebra()
    principal = PrincipalE8(algebra)
    out = {
        "schema": "perfectjet/asterion-replay/1",
        "nomenclature": NOMENCLATURE,
        "arithmetic": "exact rational and Q(zeta_5); no floating equality",
        "source_sha256": source_digests(),
        "exhaustive_requested": bool(exhaustive),
        "chevalley_coxeter": e8_receipt(exhaustive=exhaustive),
        "principal_polynomials": principal.receipt(exhaustive=exhaustive),
        "jordan_polynomials": construction_receipt(
            all_kernels=exhaustive, ambient_replay=exhaustive),
        "response_compiler": basis_receipt(),
        "asterion_e8_basis": e8_response_receipt(exhaustive=exhaustive,
                                                include_basis=include_tables, algebra=algebra),
        "deformations": deformation_receipt(),
        "chart_transport": transport_receipt(exhaustive=exhaustive),
        "limitations": [
            "Classical E8 and its gradings are identified by the cited constructions.",
            "No new complex simple Lie algebra or new Lean proof is asserted.",
            "Rational or cyclotomic coordinate charts do not establish the same integral lattice.",
            "Stored coefficient counts and table reductions are not runtime speedup claims.",
        ],
    }
    jordan = JordanE8()
    # A declared deterministic panel is separate from exhaustive Jacobi.
    triples = [(jordan.labels[i], jordan.labels[(i * 37 + 1) % 248],
                jordan.labels[(i * 73 + 5) % 248]) for i in range(248)]
    out["jordan_polynomials"]["jacobi"] = jordan.verify_jacobi(None if exhaustive else triples)
    if include_tables:
        kernels = jordan.all_grade_kernels(check=exhaustive)
        out["jordan_grade_kernels"] = [
            {"left_grade": a, "right_grade": b, "map": json_ready(kernel)}
            for (a, b), kernel in kernels.items()]
        out["jordan_cartan_certificates"] = jordan.verify_cartans(include_witnesses=True)
        from .asterion_transport import E8ChartTransport
        transport = E8ChartTransport(algebra, jordan)
        out["transport_columns"] = [vector_record(column) for column in transport.images]
    out["passed"] = (
        out["chevalley_coxeter"]["passed"]
        and out["principal_polynomials"]["verification"]["all_checks_passed"]
        and out["jordan_polynomials"]["jacobi"].get("passed", False)
        and out["jordan_polynomials"]["cartans"]["passed"]
        and (not exhaustive or (
            out["jordan_polynomials"].get("grade_pair_maps") == 7440
            and out["jordan_polynomials"].get("all_ambient_coefficients_replayed") is True))
        and out["response_compiler"]["certificate_replay"]["valid"]
        and out["response_compiler"]["jacobi"]["valid"]
        and out["asterion_e8_basis"]["certificate_replay"]["valid"]
        and out["deformations"]["sl2"]["H2_dimension"] == 0
        and out["chart_transport"]["passed"]
    )
    return json_ready(out)


def basis_bracket(chart, left, right):
    """Query an actual basis bracket; principal labels are (exponent,position)."""
    if chart == "e8":
        from .asterion_e8 import E8LieAlgebra
        algebra = E8LieAlgebra()
        if any(isinstance(i, bool) or not isinstance(i, int) or not 0 <= i < 248
               for i in (left, right)):
            raise ValueError("E8 basis indices must be integers in 0..247")
        result = algebra.bracket({left: 1}, {right: 1})
    elif chart == "principal":
        from .asterion_principal import PrincipalE8
        algebra = PrincipalE8()
        for label in (left, right):
            if (not isinstance(label, (tuple, list)) or len(label) != 2
                    or any(isinstance(x, bool) or not isinstance(x, int) for x in label)):
                raise ValueError("principal labels must be integer (exponent,position) pairs")
        left, right = tuple(left), tuple(right)
        if left not in algebra.keys or right not in algebra.keys:
            raise ValueError("principal labels must be valid (exponent,position) pairs")
        result = algebra.polynomial_basis_bracket(left, right)
    elif chart == "jordan":
        from .asterion_jordan import JordanE8
        algebra = JordanE8()
        for label in (left, right):
            if (not isinstance(label, (tuple, list)) or len(label) != 4
                    or any(isinstance(x, bool) or not isinstance(x, int) for x in label)):
                raise ValueError("Jordan labels must be integer (grade0,grade1,grade2,fiber) tuples")
        result = algebra.basis_bracket(tuple(left), tuple(right), check=True)
    else:
        raise ValueError("chart must be e8, principal, or jordan")
    return {"chart": chart, "left": left, "right": right,
            "bracket": vector_record(result), "arithmetic": "exact"}


def convert_principal(vector, *, inverse=False):
    """Convert sparse indexed coordinates between Chevalley and principal charts."""
    from .asterion_principal import PrincipalE8
    if not isinstance(vector, dict):
        raise ValueError("vector must be an object mapping basis indices to rational numbers")
    coordinates, seen = {}, set()
    for key, value in vector.items():
        if (isinstance(key, bool) or not isinstance(key, (str, int))
                or (isinstance(key, str) and (len(key) > 3 or not key.isascii() or not key.isdecimal()
                                             or str(int(key)) != key))):
            raise ValueError("coordinate keys must be canonical nonnegative integer indices")
        index = int(key)
        if not 0 <= index < 248:
            raise ValueError("basis indices must be in 0..247")
        if index in seen:
            raise ValueError("duplicate coordinate index")
        seen.add(index)
        if isinstance(value, (bool, float)):
            raise ValueError("coordinates must be exact integers or rational strings")
        coefficient = Fraction(value)
        if coefficient:
            coordinates[index] = coefficient
    algebra = PrincipalE8()
    converted = (algebra.to_chevalley(coordinates) if inverse
                 else algebra.from_chevalley(coordinates))
    replay = (algebra.from_chevalley(converted) if inverse
              else algebra.to_chevalley(converted))
    return {"from": "principal" if inverse else "chevalley",
            "to": "chevalley" if inverse else "principal",
            "vector": vector_record(converted), "roundtrip_passed": replay == coordinates}


def convert_coordinates(source, target, vector):
    """Lossless transport among all four bases, including cyclotomic inputs.

    Indexed charts accept a JSON object. The Jordan chart accepts records
    ``[{"label":[i,p,q,r],"coefficient":[a,b,c,d]},...]``. Coefficients are
    exact in the power basis 1,zeta5,zeta5²,zeta5³; rational scalars also work.
    """
    from .asterion_jordan import Cyclotomic5, JordanE8
    from .asterion_principal import PrincipalE8
    from .asterion_basis import e8_response_basis
    from .asterion_transport import E8ChartTransport
    charts = {"chevalley", "asterion", "principal", "jordan"}
    if not isinstance(source, str) or not isinstance(target, str) or source not in charts or target not in charts:
        raise ValueError("source and target must name chevalley, asterion, principal, or jordan")
    def coefficient(value):
        parts = value if isinstance(value, (tuple, list)) else (value,)
        if any(isinstance(part, (bool, float)) for part in parts):
            raise ValueError("coefficients must be exact integers or rational strings")
        return Cyclotomic5(value)
    coordinates = {}
    if source == "jordan":
        if not isinstance(vector, list):
            raise ValueError("Jordan vectors must be lists of label/coefficient records")
        for row in vector:
            if not isinstance(row, dict) or set(row) != {"label", "coefficient"}:
                raise ValueError("each Jordan record needs exactly label and coefficient")
            label = JordanE8._label(row["label"])
            if label in coordinates:
                raise ValueError("duplicate Jordan coordinate")
            coordinates[label] = coefficient(row["coefficient"])
    else:
        if not isinstance(vector, dict):
            raise ValueError("indexed vectors must be objects mapping indices to exact coefficients")
        for key, value in vector.items():
            if (isinstance(key, bool) or not isinstance(key, (str, int))
                    or (isinstance(key, str) and (len(key) > 3 or not key.isascii()
                                                 or not key.isdecimal() or str(int(key)) != key))):
                raise ValueError("coordinate keys must be canonical integer indices")
            index = int(key)
            if not 0 <= index < 248 or index in coordinates:
                raise ValueError("invalid or duplicate coordinate index")
            coordinates[index] = coefficient(value)
    coordinates = {k: c for k, c in coordinates.items() if c}
    transport, principal, response = E8ChartTransport(), None, None

    def lift(transform, values):
        out = {}
        for component in range(4):
            part = {k: c.coefficients[component] for k, c in values.items()
                    if c.coefficients[component]}
            if not part:
                continue
            for key, value in transform(part).items():
                coefficient = [Fraction(0)]*4
                coefficient[component] = value
                out[key] = out.get(key, Cyclotomic5(0)) + Cyclotomic5(coefficient)
        return {k: c for k, c in out.items() if c}

    def to_chevalley(chart, values):
        nonlocal principal, response
        if chart == "chevalley": return values
        if chart == "jordan": return transport.jordan_to_chevalley(values)
        if chart == "principal":
            principal = principal or PrincipalE8(transport.chevalley)
            return lift(principal.to_chevalley, values)
        response = response or e8_response_basis(transport.chevalley)
        return lift(response.ambient, values)

    def from_chevalley(chart, values):
        nonlocal principal, response
        values = {k: Cyclotomic5(c) for k, c in values.items() if c}
        if chart == "chevalley": return values
        if chart == "jordan": return transport.chevalley_to_jordan(values)
        if chart == "principal":
            principal = principal or PrincipalE8(transport.chevalley)
            return lift(principal.from_chevalley, values)
        response = response or e8_response_basis(transport.chevalley)
        return lift(response.coordinates, values)

    converted = from_chevalley(target, to_chevalley(source, coordinates))
    replay = from_chevalley(source, to_chevalley(target, converted))
    return {"from": source, "to": target, "coefficient_field": "Q(zeta_5)",
            "vector": vector_record(converted), "roundtrip_passed": replay == coordinates}


def benchmark(repeats=3):
    """Measured local costs; this benchmark makes no cross-machine speed claim."""
    if isinstance(repeats, bool) or not isinstance(repeats, int) or not 1 <= repeats <= 20:
        raise ValueError("repeats must be an integer in 1..20")
    from .asterion_e8 import E8LieAlgebra
    from .asterion_principal import PrincipalE8
    from .asterion_jordan import JordanE8
    records = {}
    for name, action in (
        ("chevalley_construction", E8LieAlgebra),
        ("principal_construction_and_170_couplings", lambda: PrincipalE8().couplings()),
        ("jordan_248_fourier_vectors", JordanE8),
    ):
        samples = []
        for _ in range(repeats):
            start = time.perf_counter()
            action()
            samples.append(time.perf_counter() - start)
        records[name] = {"seconds": samples, "median_seconds": statistics.median(samples)}
    return {"scope": "measured in this Python process; fresh instances, shared interpreter caches",
            "repeats": repeats, "measurements": records}


def evaluate(params):
    if not isinstance(params, dict):
        raise ValueError("Asterion parameters must be an object")
    operation = params.get("operation", "overview")
    if not isinstance(operation, str):
        raise ValueError("operation must be a string")
    allowed = {
        "overview": {"operation"},
        "report": {"operation", "exhaustive", "include_tables"},
        "bracket": {"operation", "chart", "left", "right"},
        "convert": {"operation", "vector", "inverse", "source", "target"},
        "benchmark": {"operation", "repeats"},
        "deformations": {"operation"},
        "compile": {"operation", "exhaustive", "include_basis"},
        "extension": {"operation", "exhaustive", "max_degree"},
        "boundary": {"operation", "exhaustive"},
        "currents": {"operation", "max_degree"},
        "kz": {"operation", "exhaustive"},
        "relations": {"operation", "exhaustive"},
        "higher": {"operation", "exhaustive"},
        "rigidity": {"operation", "exhaustive"},
        "periods": {"operation"},
        "discoveries": {"operation"},
        "frontiers": {"operation", "exhaustive", "max_degree"},
        "kernel-characters": {"operation", "exhaustive"},
        "kernel-tower": {"operation", "exhaustive"},
        "quartic": {"operation", "exhaustive"},
        "elliptic": {"operation", "exhaustive"},
        "monodromy": {"operation", "exhaustive"},
        "monodromy-algebra": {"operation", "exhaustive"},
        "jacobi": {"operation", "exhaustive", "max_degree"},
    }
    if operation not in allowed or set(params) - allowed[operation]:
        raise ValueError("unknown Asterion operation or unsupported parameter")
    if operation in ("frontiers", "kernel-characters", "kernel-tower", "quartic", "elliptic",
                     "monodromy", "monodromy-algebra", "jacobi"):
        from .asterion_frontiers import frontier_component_report, frontiers_report
        options = {"exhaustive":params.get("exhaustive",False),
                   "max_degree":params.get("max_degree",4)}
        return (frontiers_report(**options) if operation == "frontiers"
                else frontier_component_report(operation,**options))
    if operation in ("extension", "boundary", "currents", "kz", "relations", "higher", "rigidity", "periods", "discoveries"):
        from .asterion_extension import component_report, extension_report, research_ledger
        exhaustive = params.get("exhaustive", False)
        if not isinstance(exhaustive, bool):
            raise ValueError("exhaustive must be a Boolean")
        if operation == "discoveries":
            return research_ledger()
        if operation == "extension":
            return extension_report(exhaustive=exhaustive,
                                    max_degree=params.get("max_degree", 12))
        return component_report(operation, exhaustive=exhaustive,
                                max_degree=params.get("max_degree", 12))
    if operation == "overview":
        from .asterion_e8 import E8LieAlgebra
        from .asterion_principal import PrincipalE8
        from .asterion_jordan import JordanE8, naive_permutation_no_go
        core, principal, jordan = E8LieAlgebra(), PrincipalE8(), JordanE8()
        couplings = principal.couplings()
        return {"nomenclature": NOMENCLATURE, "dimension": core.dimension,
                "root_count": len(core.roots), "principal_chain_dimensions": [2*m+1 for m in core.exponents],
                "computed_couplings": len(couplings),
                "nonzero_couplings": sum(bool(x) for x in couplings.values()),
                "jordan_basis_vectors": len(jordan.labels), "jordan_grades": len(jordan.grades),
                "cartan_lines": len(jordan.cartan_lines()), "no_go": naive_permutation_no_go(),
                "example_jordan_bracket": basis_bracket("jordan", (1,0,0,0), (0,1,0,0)),
                "scope": "actual exact constructions; overview does not run exhaustive Jacobi"}
    if operation == "deformations":
        from .asterion_deformations import deformation_receipt
        return deformation_receipt()
    if operation == "compile":
        from .asterion_basis import e8_response_receipt
        for key in ("exhaustive", "include_basis"):
            if key in params and not isinstance(params[key], bool):
                raise ValueError(f"{key} must be a Boolean")
        return e8_response_receipt(exhaustive=params.get("exhaustive", False),
                                   include_basis=params.get("include_basis", False))
    if operation == "report":
        for key in ("exhaustive", "include_tables"):
            if key in params and not isinstance(params[key], bool):
                raise ValueError(f"{key} must be a Boolean")
        return report(exhaustive=params.get("exhaustive", False),
                      include_tables=params.get("include_tables", False))
    if operation == "bracket":
        return json_ready(basis_bracket(params.get("chart", "e8"), params.get("left", 0), params.get("right", 1)))
    if operation == "convert":
        if "source" in params or "target" in params:
            if "source" not in params or "target" not in params or "inverse" in params:
                raise ValueError("supply source and target together, without inverse")
            return convert_coordinates(params["source"], params["target"], params.get("vector", {}))
        if not isinstance(params.get("inverse", False), bool):
            raise ValueError("inverse must be a Boolean")
        return convert_principal(params.get("vector", {"0": 1}), inverse=params.get("inverse", False))
    return benchmark(params.get("repeats", 3))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", nargs="?", default="overview",
                        choices=("overview", "report", "bracket", "convert", "benchmark", "compile", "deformations",
                                 "extension", "boundary", "currents", "kz", "relations", "higher", "rigidity", "periods", "discoveries",
                                 "frontiers", "kernel-characters", "kernel-tower", "quartic", "elliptic", "monodromy", "monodromy-algebra", "jacobi"))
    parser.add_argument("--chart", choices=("e8", "principal", "jordan"), default="e8")
    parser.add_argument("--left", help="JSON basis index or coordinate label")
    parser.add_argument("--right", help="JSON basis index or coordinate label")
    parser.add_argument("--vector", help="JSON object of sparse indexed rational coordinates")
    parser.add_argument("--source", choices=("chevalley", "asterion", "principal", "jordan"))
    parser.add_argument("--target", choices=("chevalley", "asterion", "principal", "jordan"))
    parser.add_argument("--inverse", action="store_true")
    parser.add_argument("--exhaustive", action="store_true")
    parser.add_argument("--include-tables", action="store_true")
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--max-degree", type=int)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    params = {"operation": args.operation}
    if args.operation == "report":
        params.update(exhaustive=args.exhaustive, include_tables=args.include_tables)
    elif args.operation == "compile":
        params.update(exhaustive=args.exhaustive, include_basis=args.include_tables)
    elif args.operation == "bracket":
        if args.left is None or args.right is None:
            parser.error("bracket requires --left and --right JSON labels")
        params.update(chart=args.chart, left=json.loads(args.left), right=json.loads(args.right))
    elif args.operation == "convert":
        params.update(vector=json.loads(args.vector or '{"0":1}'))
        if args.source is not None or args.target is not None:
            if args.source is None or args.target is None or args.inverse:
                parser.error("convert needs --source and --target together, without --inverse")
            params.update(source=args.source, target=args.target)
        else:
            params["inverse"] = args.inverse
    elif args.operation == "benchmark":
        params["repeats"] = args.repeats
    elif args.operation == "extension":
        params.update(exhaustive=args.exhaustive, max_degree=args.max_degree if args.max_degree is not None else 12)
    elif args.operation == "currents":
        params["max_degree"] = args.max_degree if args.max_degree is not None else 12
    elif args.operation in ("frontiers", "jacobi"):
        params.update(exhaustive=args.exhaustive,max_degree=args.max_degree if args.max_degree is not None else 4)
    elif args.operation in ("kernel-characters", "kernel-tower", "quartic", "elliptic", "monodromy", "monodromy-algebra"):
        params["exhaustive"] = args.exhaustive
    elif args.operation in ("boundary", "kz", "relations", "higher", "rigidity"):
        params["exhaustive"] = args.exhaustive
    result = evaluate(params)
    content = json.dumps(json_ready(result), indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(content, encoding="utf-8")
    else:
        print(content, end="")
    return 0 if result.get("passed", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
