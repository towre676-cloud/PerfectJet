"""Exact kernel towers for rational matrices and polynomial operators.

This module isolates the common algebra behind observability, repeated
constraint refinement, and polynomial partner problems. It is deliberately
small: all arithmetic is exact, dependency-free, and built on PerfectJet's
existing exact and polynomial layers.

Conventions
-----------
States are coefficient column vectors. A matrix constraint C acts by C x and
an evolution matrix A acts by A x. The depth-r tower is

    [ C ; C A ; ... ; C A^r ].

For polynomial operators, domain_basis fixes the coefficient columns.
Each constraint is a linear callable returning a Poly. Evolution may change
polynomial degree; no finite codomain basis is required.
"""
from __future__ import annotations

from fractions import Fraction as Q

from .exact import matmul, nullspace, rank, row_basis
from .polynomial import Poly


def _matrix(value, name):
    try:
        rows = [[Q(x) for x in row] for row in value]
    except (TypeError, ValueError, ZeroDivisionError) as error:
        raise ValueError(f"{name} must be an exact rational matrix") from error
    if rows and any(len(row) != len(rows[0]) for row in rows):
        raise ValueError(f"{name} must be rectangular")
    return rows


def _response(rows, vector):
    return [sum((a*b for a, b in zip(row, vector)), Q(0)) for row in rows]


def _serialize_vector(vector):
    return [str(x) for x in vector]


def _serialize_matrix(rows):
    return [[str(x) for x in row] for row in rows]


def matrix_kernel_tower(constraint, evolution, max_depth=None, include_matrices=False):
    """Compute the exact finite-dimensional kernel/observability tower.

    constraint is an m-by-n exact rational matrix and evolution is an n-by-n
    matrix. The routine stops as soon as cumulative row rank is unchanged, or
    when the kernel is zero. If max_depth is omitted, depth n is sufficient to
    encounter one of those conditions.

    The returned lost_witness at a rank-increasing depth is a vector that
    survived the preceding cumulative constraints and is detected by the new
    block.
    """
    c = _matrix(constraint, "constraint")
    a = _matrix(evolution, "evolution")
    if not a or len(a) != len(a[0]):
        raise ValueError("evolution must be a nonempty square matrix")
    n = len(a)
    if not c or any(len(row) != n for row in c):
        raise ValueError("constraint must be nonempty with evolution-width columns")
    if max_depth is None:
        max_depth = n
    if type(max_depth) is not int or max_depth < 0:
        raise ValueError("max_depth must be a nonnegative integer")

    cumulative = []
    block = c
    history = []
    previous_rank = None
    stabilized = False
    stabilization_depth = None

    for depth in range(max_depth + 1):
        previous_rows = list(cumulative)
        cumulative.extend(block)
        current_rank = rank(cumulative, n)
        kernel = nullspace(cumulative, n)

        lost = None
        if current_rank and (previous_rank is None or current_rank > previous_rank):
            for vector in nullspace(previous_rows, n):
                response = _response(block, vector)
                if any(response):
                    lost = {
                        "vector": _serialize_vector(vector),
                        "new_block_response": _serialize_vector(response),
                    }
                    break

        entry = {
            "depth": depth,
            "rank": current_rank,
            "kernel_dimension": n-current_rank,
            "kernel_basis": [_serialize_vector(v) for v in kernel],
            "lost_witness": lost,
        }
        if include_matrices:
            entry["block"] = _serialize_matrix(block)
            entry["cumulative"] = _serialize_matrix(cumulative)
        history.append(entry)

        if current_rank == n:
            stabilized = True
            stabilization_depth = depth
            break
        if previous_rank is not None and current_rank == previous_rank:
            stabilized = True
            stabilization_depth = depth-1
            break

        previous_rank = current_rank
        block = matmul(block, a)

    basis = row_basis(cumulative, n)
    closure = False
    if stabilized:
        evolved_basis = matmul(basis, a) if basis else []
        closure = rank(basis + evolved_basis, n) == len(basis)

    final_rank = rank(cumulative, n)
    return {
        "schema": "perfectjet/kernel-tower/matrix-v1",
        "state_dimension": n,
        "constraint_rows": len(c),
        "stabilized": stabilized,
        "stabilization_depth": stabilization_depth,
        "observable_rank": final_rank,
        "persistent_kernel_dimension": n-final_rank,
        "persistent_kernel_basis": [_serialize_vector(v) for v in nullspace(cumulative, n)],
        "observable_row_space_closed": closure,
        "history": history,
        "scope": (
            "Exact rational finite-dimensional tower. Stabilization is certified "
            "by cumulative row-space closure under right multiplication by evolution."
        ),
    }


def _operator_block(images_by_constraint, width):
    """Turn polynomial images of basis columns into a coefficient matrix block."""
    rows = []
    channels = []
    for channel, images in enumerate(images_by_constraint):
        if len(images) != width:
            raise ValueError("constraint image count differs from domain width")
        if any(not isinstance(p, Poly) for p in images):
            raise ValueError("polynomial constraints must return Poly objects")
        variables = images[0].variables if images else None
        if any(p.variables != variables for p in images):
            raise ValueError("constraint outputs have inconsistent variable counts")
        monomials = sorted(set().union(*(p.terms.keys() for p in images)))
        for exponent in monomials:
            row = [p.terms.get(exponent, Q(0)) for p in images]
            if any(row):
                rows.append(row)
                channels.append({"constraint": channel, "exponents": list(exponent)})
    return rows, channels


def polynomial_kernel_tower(domain_basis, evolution, constraints, max_depth=None,
                            include_matrices=False):
    """Compute repeated polynomial constraint kernels on a fixed input space.

    domain_basis is the coefficient basis for the input observable. The
    evolution callable may change degree at every iterate. Each constraint is
    applied to every evolved basis element and all nonzero output coefficients
    become exact matrix rows. Constraint channels remain distinct even when
    they produce the same output monomial.

    Linearity of the supplied callables is an explicit applicability
    assumption; the returned witness replays only the resulting exact matrices.
    """
    if not isinstance(domain_basis, (list, tuple)) or not domain_basis:
        raise ValueError("domain_basis must be a nonempty sequence")
    if any(not isinstance(p, Poly) for p in domain_basis):
        raise ValueError("domain_basis entries must be Poly objects")
    variables = domain_basis[0].variables
    if any(p.variables != variables for p in domain_basis):
        raise ValueError("domain_basis variable counts differ")
    if not callable(evolution):
        raise ValueError("evolution must be callable")
    if not isinstance(constraints, (list, tuple)) or not constraints or any(not callable(c) for c in constraints):
        raise ValueError("constraints must be a nonempty callable sequence")
    n = len(domain_basis)
    if max_depth is None:
        max_depth = n
    if type(max_depth) is not int or max_depth < 0:
        raise ValueError("max_depth must be a nonnegative integer")

    evolved = list(domain_basis)
    cumulative = []
    history = []
    previous_rank = None
    stabilized = False
    stabilization_depth = None

    for depth in range(max_depth + 1):
        images = [[constraint(p) for p in evolved] for constraint in constraints]
        block, channels = _operator_block(images, n)
        previous_rows = list(cumulative)
        cumulative.extend(block)
        current_rank = rank(cumulative, n)
        kernel = nullspace(cumulative, n)

        lost = None
        if current_rank and (previous_rank is None or current_rank > previous_rank):
            for vector in nullspace(previous_rows, n):
                response = _response(block, vector)
                if any(response):
                    lost = {
                        "vector": _serialize_vector(vector),
                        "new_block_response": _serialize_vector(response),
                    }
                    break

        entry = {
            "depth": depth,
            "rows_added": len(block),
            "channels": channels,
            "rank": current_rank,
            "kernel_dimension": n-current_rank,
            "kernel_basis": [_serialize_vector(v) for v in kernel],
            "lost_witness": lost,
        }
        if include_matrices:
            entry["block"] = _serialize_matrix(block)
            entry["cumulative"] = _serialize_matrix(cumulative)
        history.append(entry)

        if current_rank == n:
            stabilized = True
            stabilization_depth = depth
            break
        if previous_rank is not None and current_rank == previous_rank:
            stabilized = True
            stabilization_depth = depth-1
            break

        previous_rank = current_rank
        next_evolved = [evolution(p) for p in evolved]
        if any(not isinstance(p, Poly) for p in next_evolved):
            raise ValueError("evolution must return Poly objects")
        if any(p.variables != variables for p in next_evolved):
            raise ValueError("evolution changed polynomial variable count")
        evolved = next_evolved

    final_rank = rank(cumulative, n)
    return {
        "schema": "perfectjet/kernel-tower/polynomial-v1",
        "domain_dimension": n,
        "constraint_count": len(constraints),
        "stabilized": stabilized,
        "stabilization_depth": stabilization_depth,
        "persistent_kernel_dimension": n-final_rank,
        "persistent_kernel_basis": [_serialize_vector(v) for v in nullspace(cumulative, n)],
        "history": history,
        "scope": (
            "Exact coefficient-kernel tower on the supplied finite input span. "
            "Evolution may leave that span because each iterate is constrained "
            "directly in the ambient sparse polynomial ring."
        ),
    }
