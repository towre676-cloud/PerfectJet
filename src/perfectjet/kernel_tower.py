"""Exact kernel towers for rational matrices and polynomial operators.

The finite-state matrix API certifies permanent stabilization.  The polynomial
API is deliberately more conservative: evolution may leave the supplied input
span, so a finite-depth rank plateau is reported only as an observed plateau,
not as an infinite-tail theorem.
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
    """Compute an exact finite-dimensional observability/kernel tower.

    For square evolution A and constraint C, the cumulative matrix is
    [C; CA; ...; CA^r].  Once adding CA^r fails to increase row rank, the
    cumulative row space is A-invariant and every later block is redundant.
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
                    lost = {"vector": _serialize_vector(vector),
                            "new_block_response": _serialize_vector(response)}
                    break

        entry = {"depth": depth, "rank": current_rank,
                 "kernel_dimension": n-current_rank,
                 "kernel_basis": [_serialize_vector(v) for v in kernel],
                 "lost_witness": lost}
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
        if not closure:
            raise ArithmeticError("claimed matrix-tower stabilization failed closure replay")

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
            "Exact rational finite-state tower. Permanent stabilization is "
            "certified by cumulative row-space closure under right multiplication "
            "by the supplied square evolution matrix."
        ),
    }


def _validate_polynomial_problem(domain_basis, evolution, constraints):
    if not isinstance(domain_basis, (list, tuple)) or not domain_basis:
        raise ValueError("domain_basis must be a nonempty sequence")
    if any(not isinstance(p, Poly) for p in domain_basis):
        raise ValueError("domain_basis entries must be Poly objects")
    variables = domain_basis[0].variables
    if any(p.variables != variables for p in domain_basis):
        raise ValueError("domain_basis variable counts differ")
    if not callable(evolution):
        raise ValueError("evolution must be callable")
    if (not isinstance(constraints, (list, tuple)) or not constraints
            or any(not callable(c) for c in constraints)):
        raise ValueError("constraints must be a nonempty callable sequence")
    return variables


def _operator_block(images_by_constraint, width):
    rows, channels = [], []
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


def polynomial_observation_records(domain_basis, evolution, constraints, depth):
    """Return keyed exact rows for all constraint/evolution iterates through depth.

    Keys are (iterate, constraint_index, exponent_tuple).  This representation
    is stable under parameter specialization because missing rows are understood
    as exact zero rows; it is used by the parametric incidence engine.
    """
    variables = _validate_polynomial_problem(domain_basis, evolution, constraints)
    if type(depth) is not int or depth < 0:
        raise ValueError("depth must be a nonnegative integer")
    evolved = list(domain_basis)
    records = {}
    for iterate in range(depth + 1):
        for channel, constraint in enumerate(constraints):
            images = [constraint(p) for p in evolved]
            if any(not isinstance(p, Poly) or p.variables != variables for p in images):
                raise ValueError("constraints must return Poly objects with unchanged variable count")
            monomials = sorted(set().union(*(p.terms.keys() for p in images)))
            for exponent in monomials:
                row = [p.terms.get(exponent, Q(0)) for p in images]
                if any(row):
                    records[(iterate, channel, exponent)] = row
        if iterate != depth:
            evolved = [evolution(p) for p in evolved]
            if any(not isinstance(p, Poly) or p.variables != variables for p in evolved):
                raise ValueError("evolution must return Poly objects with unchanged variable count")
    return records


def polynomial_kernel_tower(domain_basis, evolution, constraints, max_depth,
                            include_matrices=False):
    """Compute a bounded repeated polynomial-constraint tower.

    Unlike the finite-state matrix API, evolution may leave the supplied input
    span. Therefore an unchanged rank at one iterate is only an observed
    plateau. The routine never converts such a plateau into an infinite-tail
    claim. A zero surviving kernel *is* permanent and is reported as certified.
    """
    variables = _validate_polynomial_problem(domain_basis, evolution, constraints)
    if type(max_depth) is not int or max_depth < 0:
        raise ValueError("explicit max_depth must be a nonnegative integer")
    n = len(domain_basis)
    evolved = list(domain_basis)
    cumulative = []
    history = []
    previous_rank = None
    plateaus = []
    zero_kernel_depth = None

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
                    lost = {"vector": _serialize_vector(vector),
                            "new_block_response": _serialize_vector(response)}
                    break
        if previous_rank is not None and current_rank == previous_rank:
            plateaus.append(depth)

        entry = {"depth": depth, "rows_added": len(block), "channels": channels,
                 "rank": current_rank, "kernel_dimension": n-current_rank,
                 "kernel_basis": [_serialize_vector(v) for v in kernel],
                 "lost_witness": lost}
        if include_matrices:
            entry["block"] = _serialize_matrix(block)
            entry["cumulative"] = _serialize_matrix(cumulative)
        history.append(entry)

        if current_rank == n:
            zero_kernel_depth = depth
            break
        previous_rank = current_rank
        if depth != max_depth:
            evolved = [evolution(p) for p in evolved]
            if any(not isinstance(p, Poly) or p.variables != variables for p in evolved):
                raise ValueError("evolution must return Poly objects with unchanged variable count")

    final_rank = rank(cumulative, n)
    return {
        "schema": "perfectjet/kernel-tower/polynomial-v2",
        "domain_dimension": n,
        "constraint_count": len(constraints),
        "bounded_through_depth": history[-1]["depth"],
        "zero_kernel_certified": zero_kernel_depth is not None,
        "zero_kernel_depth": zero_kernel_depth,
        "observed_plateau_depths": plateaus,
        "surviving_kernel_dimension": n-final_rank,
        "surviving_kernel_basis": [_serialize_vector(v) for v in nullspace(cumulative, n)],
        "history": history,
        "scope": (
            "Exact coefficient-kernel tower on the supplied finite input span, "
            "checked only through the reported depth. Evolution may leave that "
            "span, so a finite-depth plateau is not an infinite stabilization "
            "certificate. Zero kernel is permanent."
        ),
    }
