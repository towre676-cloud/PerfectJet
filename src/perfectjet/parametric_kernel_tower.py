"""Parametric rank loci for repeated polynomial constraint towers.

This module composes kernel_tower's keyed polynomial observations with the
comprehensive exact rank-cell machinery in parametric.py.  It does not infer a
degree bound: callers must state an interpolation bound and the result records
that bound as part of its proof boundary.
"""
from __future__ import annotations

from fractions import Fraction as Q
from itertools import product

from .exact import rank
from .kernel_tower import polynomial_observation_records
from .parametric import (classify, drop_locus, evaluate, fmt, polynomial_matrix,
                         rank_cells)


def _grid(bound, nvars):
    return list(product(range(bound + 1), repeat=nvars))


def _serialize_poly(p):
    return [{"exponents": list(e), "coefficient": str(c)}
            for e, c in sorted(p.items())]


def _serialize_cell(cell, names):
    return {
        "rank": cell["rank"],
        "kernel_dimension": None,
        "equations": [_serialize_poly(p) for p in cell["equations"]],
        "equations_pretty": [fmt(p, names) for p in cell["equations"]],
        "inequations": [_serialize_poly(p) for p in cell["inequations"]],
        "inequations_pretty": [fmt(p, names) for p in cell["inequations"]],
    }


def parametric_polynomial_observation_matrix(
        family, domain_basis, evolution_factory, constraints_factory, *,
        nvars, parameter_degree, depth):
    """Interpolate the full keyed observation matrix over Q[t1,...,tn].

    family(*point) returns the specialized object (usually a Hamiltonian).
    evolution_factory(object) returns the evolution callable and
    constraints_factory(object) returns the constraint callables.

    parameter_degree is a per-variable degree bound for every matrix entry.
    This is an applicability assertion, not something this routine proves.
    """
    if type(nvars) is not int or not 1 <= nvars <= 3:
        raise ValueError("nvars must be 1, 2 or 3")
    if type(parameter_degree) is not int or parameter_degree < 0:
        raise ValueError("parameter_degree must be a nonnegative integer")
    if type(depth) is not int or depth < 0:
        raise ValueError("depth must be a nonnegative integer")

    cache = {}
    union = set()
    for pt in _grid(parameter_degree, nvars):
        obj = family(*map(Q, pt))
        records = polynomial_observation_records(
            domain_basis, evolution_factory(obj), constraints_factory(obj), depth)
        cache[tuple(map(Q, pt))] = records
        union.update(records)
    keys = sorted(union)
    width = len(domain_basis)

    def numeric(*point):
        point = tuple(map(Q, point))
        records = cache.get(point)
        if records is None:
            obj = family(*point)
            records = polynomial_observation_records(
                domain_basis, evolution_factory(obj), constraints_factory(obj), depth)
        return [records.get(key, [Q(0)] * width) for key in keys]

    matrix = polynomial_matrix(numeric, nvars, parameter_degree)
    return {
        "matrix": matrix,
        "row_keys": [
            {"iterate": key[0], "constraint": key[1], "exponents": list(key[2])}
            for key in keys
        ],
        "parameter_degree": parameter_degree,
        "depth": depth,
        "nvars": nvars,
    }


def parametric_kernel_tower(
        family, domain_basis, evolution_factory, constraints_factory, *,
        nvars, parameter_degree, max_depth, names=None):
    """Compute exact constant-rank cells at every bounded refinement depth."""
    if names is None:
        names = [f"t{i+1}" for i in range(nvars)]
    if len(names) != nvars:
        raise ValueError("names must contain one parameter name per variable")
    if type(max_depth) is not int or max_depth < 0:
        raise ValueError("max_depth must be a nonnegative integer")

    depths = []
    for depth in range(max_depth + 1):
        recovered = parametric_polynomial_observation_matrix(
            family, domain_basis, evolution_factory, constraints_factory,
            nvars=nvars, parameter_degree=parameter_degree, depth=depth)
        matrix = recovered["matrix"]
        cells = rank_cells(matrix, nvars)
        generic_rank = max(c["rank"] for c in cells)
        serialized = []
        for cell in cells:
            row = _serialize_cell(cell, names)
            row["kernel_dimension"] = len(domain_basis) - cell["rank"]
            serialized.append(row)
        drops = drop_locus(matrix, nvars, names)
        depths.append({
            "depth": depth,
            "row_count": len(matrix),
            "row_keys": recovered["row_keys"],
            "generic_rank": generic_rank,
            "generic_kernel_dimension": len(domain_basis) - generic_rank,
            "cells": serialized,
            "drop_locus": {
                "generic_rank": drops["generic_rank"],
                "cell_count": drops["cells"],
                "drop_cells": drops["drop_cells"],
            },
        })

    return {
        "schema": "perfectjet/parametric-kernel-tower/1",
        "parameter_names": list(names),
        "parameter_count": nvars,
        "parameter_degree_bound_per_variable": parameter_degree,
        "domain_dimension": len(domain_basis),
        "bounded_through_depth": max_depth,
        "depths": depths,
        "scope": (
            "Exact comprehensive rank cells over the algebraic closure for the "
            "interpolated bounded observation matrices. The stated interpolation "
            "degree bound is a caller-supplied mathematical assumption and must "
            "be justified independently. No finite depth implies an infinite-tail theorem."
        ),
    }


def replay_point(report, point, family, domain_basis, evolution_factory,
                 constraints_factory):
    """Replay every reported depth at one rational parameter point."""
    point = tuple(Q(x) for x in point)
    if len(point) != report["parameter_count"]:
        raise ValueError("point has wrong parameter count")
    obj = family(*point)
    out = []
    for depth_report in report["depths"]:
        depth = depth_report["depth"]
        records = polynomial_observation_records(
            domain_basis, evolution_factory(obj), constraints_factory(obj), depth)
        keys = [(r["iterate"], r["constraint"], tuple(r["exponents"]))
                for r in depth_report["row_keys"]]
        numeric = [records.get(key, [Q(0)] * len(domain_basis)) for key in keys]
        direct = rank(numeric, len(domain_basis))
        out.append({
            "depth": depth,
            "direct_rank": direct,
            "direct_kernel_dimension": len(domain_basis) - direct,
        })
    return {"point": [str(x) for x in point], "depths": out}
