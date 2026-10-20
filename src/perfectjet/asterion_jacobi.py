"""Exact rank-eight Jacobi refinement of the E8 level-one character.

Lattice coordinates are doubled Euclidean coordinates, never floating point.
The classical all-order conclusions use Poisson summation and harmonic theta
modularity; finite receipts independently replay the coefficient identities.
This module does not identify the five-channel KZ system with a KZB system.
"""
from __future__ import annotations

from fractions import Fraction as Q
from functools import lru_cache
from math import isqrt, prod


SOURCES = (
    "https://arxiv.org/abs/1706.04619",
    "https://www.unige.ch/math/folks/delaharpe/articles/10HaPaVe2006.pdf",
    "https://people.math.harvard.edu/~elkies/M272.19/oct23.pdf",
)
ZERO = (0,) * 8


def _degree(value):
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 8:
        raise ValueError("lattice enumeration degree must be an integer in 0..8")
    return value


def _vector(value):
    value = tuple(value)
    if len(value) != 8 or any(isinstance(x, bool) or not isinstance(x, int) for x in value):
        raise ValueError("eight exact integer doubled coordinates required")
    return value


def in_lattice(vector):
    """Whether vector/2 lies in D8 union (D8+(1/2,...,1/2))."""
    vector = _vector(vector)
    return len({x % 2 for x in vector}) == 1 and sum(vector) % 4 == 0


def inner(left, right):
    return Q(sum(x*y for x, y in zip(_vector(left), _vector(right))), 4)


def lattice_degree(vector):
    vector = _vector(vector)
    if not in_lattice(vector):
        raise ValueError("the doubled vector is outside E8")
    squared = sum(x*x for x in vector)
    if squared % 8:
        raise ArithmeticError("E8 evenness failed")
    return squared // 8


@lru_cache(maxsize=9)
def lattice_shells(max_degree=4):
    """Complete norm-bounded enumeration with parity and residue guards.

    Each coordinate satisfies v_i^2 <= 8*N. Recursing over this finite ball,
    then testing sum(v_i)=0 mod4, visits every E8 point exactly once.
    """
    maximum = _degree(max_degree)
    shells = [[] for _ in range(maximum + 1)]
    for parity in (0, 1):
        def visit(prefix, remaining, total):
            used = len(prefix)
            if used == 8:
                norm = 8*maximum - remaining
                if total % 4 == 0 and norm % 8 == 0:
                    shells[norm//8].append(prefix)
                return
            bound = isqrt(remaining)
            lower = -bound
            if lower % 2 != parity:
                lower += 1
            for coordinate in range(lower, bound + 1, 2):
                rest = remaining - coordinate*coordinate
                if rest < parity * (7-used):
                    continue
                visit(prefix + (coordinate,), rest, total + coordinate)
        visit((), 8*maximum, 0)
    return tuple(tuple(sorted(shell)) for shell in shells)


def charge_population(weight, charge):
    """Exact multiplicity of Cartan charge charge/2 in L_1(E8)_weight."""
    from .asterion_currents import colored_partitions
    weight = _degree(weight)
    charge = _vector(charge)
    if not in_lattice(charge):
        return 0
    oscillator = weight - lattice_degree(charge)
    return colored_partitions(8, weight)[oscillator] if oscillator >= 0 else 0


def weyl_reflect(vector, root):
    """Reflect an E8 lattice vector in a norm-two root, exactly."""
    vector, root = _vector(vector), _vector(root)
    if not in_lattice(vector) or not in_lattice(root) or lattice_degree(root) != 1:
        raise ValueError("an E8 vector and a norm-two E8 root are required")
    coefficient = inner(vector, root)
    if coefficient.denominator != 1:
        raise ArithmeticError("E8 integrality failed")
    return tuple(x-int(coefficient)*a for x, a in zip(vector, root))


def elliptic_reindex(charge, shift):
    """Coefficient bijection proving the elliptic translation law.

    Theta(tau,z+tau*lambda+mu) =
    q^(-|lambda|^2/2) exp(-2*pi*i*(lambda,z))*Theta(tau,z),
    for lambda,mu in E8. The integer lattice pairing removes mu's phase.
    """
    charge, shift = _vector(charge), _vector(shift)
    if not in_lattice(charge) or not in_lattice(shift):
        raise ValueError("both charge and shift must belong to E8")
    translated = tuple(a+b for a, b in zip(charge, shift))
    left_degree = Q(lattice_degree(charge)) + inner(charge, shift)
    right_degree = Q(lattice_degree(translated)-lattice_degree(shift))
    if left_degree != right_degree:
        raise ArithmeticError("elliptic exponent reindexing failed")
    return {"translated_charge": translated, "exponent": left_degree}


def _partitions(total, largest=None):
    if not total:
        yield ()
        return
    for head in range(min(total, largest or total), 0, -1):
        for tail in _partitions(total-head, head):
            yield (head,) + tail


def _double_factorial_odd(n):
    return prod(range(1, n+1, 2))


def spherical_moment(shell_size, degree, exponents):
    """Moment of an exponent pattern on the radius-sqrt(2*degree) sphere."""
    exponents = tuple(exponents)
    if any(x % 2 for x in exponents):
        return Q(0)
    k = sum(exponents)//2
    denominator = prod(8+2*j for j in range(k))
    return Q(shell_size*(2*degree)**k * prod(_double_factorial_odd(x-1)
                                             for x in exponents), denominator)


def shell_moment(shell, exponents):
    exponents = tuple(exponents)
    if len(exponents) > 8 or any(not isinstance(x, int) or x < 0 for x in exponents):
        raise ValueError("a nonnegative exponent pattern of length at most eight is required")
    return Q(sum(prod(v[i]**e for i, e in enumerate(exponents)) for v in shell),
             2**sum(exponents))


def harmonic_projection_coefficients(degree=8, dimension=8):
    """Harmonic projection of (x,u)^degree as powers of |x|²|u|².

    Returns a_j in sum a_j |x|^(2j)|u|^(2j)(x,u)^(degree-2j).
    The recurrence is obtained by taking the Euclidean Laplacian in x.
    """
    if (isinstance(degree, bool) or not isinstance(degree, int)
            or degree < 2 or degree > 30 or degree % 2 or dimension != 8):
        raise ValueError("even harmonic degree2..30 and dimension8 required")
    out = [Q(1)]
    for j in range(degree//2):
        remaining = degree-2*j
        denominator = 2*(j+1)*(dimension+2*degree-2*(j+1)-2)
        out.append(-out[-1]*remaining*(remaining-1)/denominator)
    return tuple(out)


def _convolution(left, right, maximum):
    return tuple(sum(left[j]*right[n-j] for j in range(n+1))
                 for n in range(maximum+1))


def _solve_coefficients(columns, target, rows):
    """Solve the full Sturm panel, retaining inconsistency and rank guards."""
    count = len(columns)
    panel = [[Q(column[n]) for column in columns]+[Q(target[n])]
             for n in range(1, rows+1)]
    pivot_row = 0
    for col in range(count):
        pivot = next((i for i in range(pivot_row,len(panel)) if panel[i][col]), None)
        if pivot is None:
            raise ArithmeticError("cusp-form Sturm panel lost column rank")
        panel[pivot_row], panel[pivot] = panel[pivot], panel[pivot_row]
        scale = panel[pivot_row][col]
        panel[pivot_row] = [x/scale for x in panel[pivot_row]]
        for i in range(len(panel)):
            if i != pivot_row and panel[i][col]:
                scale = panel[i][col]
                panel[i] = [x-scale*y for x,y in zip(panel[i],panel[pivot_row])]
        pivot_row += 1
    if any(all(not x for x in row[:-1]) and row[-1] for row in panel):
        raise ArithmeticError("harmonic theta violates its modular Sturm panel")
    return tuple(panel[j][-1] for j in range(count))


def harmonic_theta_receipt(max_degree=4):
    """Exact harmonic-density relation compiler through angular degree30.

    Theta_{L,P_d} is in S_(4+d)=Delta*M_(d-8). The polynomial ring
    Q[E4,E6] and the Sturm bound floor((4+d)/12) give a complete finite
    presentation of each angular sector. Displayed coefficients specialize
    the direction to e1; the modular theorem is valid polynomial-valued in u.
    """
    from .asterion_currents import e4_coefficients, euler_product_coefficients
    maximum = max(2, _degree(max_degree))
    shells = lattice_shells(maximum)
    e4 = e4_coefficients(maximum)
    e6 = [1]+[0]*maximum
    for divisor in range(1, maximum+1):
        for n in range(divisor, maximum+1, divisor):
            e6[n] -= 504*divisor**5
    delta = (0,)+euler_product_coefficients(((1,24),),maximum)[:maximum]
    # One-coordinate histograms compute every directional power exactly.
    moments = []
    for shell in shells:
        histogram = {}
        for v in shell:
            histogram[v[0]] = histogram.get(v[0],0)+1
        moments.append(tuple(Q(sum(count*x**power for x,count in histogram.items()),2**power)
                             for power in range(31)))
    reports = []
    passed = True
    for degree in range(2,31,2):
        a = harmonic_projection_coefficients(degree)
        weighted = tuple(sum(a[j]*(2*n)**j*moments[n][degree-2*j]
                             for j in range(degree//2+1))
                         for n in range(maximum+1))
        basis_exponents = [(x,y) for x in range(max(0,degree-8)//4+1)
                           for y in range(max(0,degree-8)//6+1)
                           if 4*x+6*y == degree-8]
        columns = []
        for x,y in basis_exponents:
            term = delta
            for _ in range(x):
                term = _convolution(term,e4,maximum)
            for _ in range(y):
                term = _convolution(term,e6,maximum)
            columns.append(term)
        bound = (degree+4)//12
        coefficients = _solve_coefficients(columns,weighted,bound)
        residual = tuple(weighted[n]-sum(c*column[n] for c,column in zip(coefficients,columns))
                         for n in range(maximum+1))
        passed = passed and not any(residual)
        reports.append({"harmonic_degree":degree,"modular_weight":degree+4,
                        "cusp_dimension":len(columns),"sturm_bound":bound,
                        "basis_Delta_E4_E6_exponents":basis_exponents,
                        "axis_specialized_coefficients":tuple(map(str,coefficients)),
                        "axis_weighted_theta":tuple(map(str,weighted)),
                        "residual":tuple(map(str,residual))})
    return {"passed":bool(passed),"maximum_q_degree":maximum,
            "angular_degrees":list(range(2,31,2)),"sectors":reports,
            "all_order_theorem":"Theta_(E8,P_d) in S_(4+d)=Delta*Q[E4,E6]_(d-8)",
            "coefficient_scope":"Exact e1 directional specialization; polynomial-valued identity follows from harmonic theta modularity and the same Sturm bound",
            "first_two_dimensional_angular_sector":20,
            "global_priority_claim":False}


def jacobi_receipt(max_degree=4, *, exhaustive=False):
    """Replay the refined character, heat identity, and first angular boundary.

    D8 permutations and even sign changes reduce all even moments through8
    to partitions of1..4 and the all-odd pattern(1,...,1). Thus the reported
    moment comparisons cover whole tensors, not sampled directions.
    """
    from .asterion_currents import (CurrentPopulations, colored_partitions,
                                    e4_coefficients, euler_product_coefficients)
    if not isinstance(exhaustive, bool):
        raise ValueError("exhaustive must be Boolean")
    maximum = _degree(max_degree)
    shells = lattice_shells(maximum)
    counts = tuple(map(len, shells))
    reference = e4_coefficients(maximum)
    oscillators = colored_partitions(8, maximum)
    populations = CurrentPopulations(maximum)
    reconstructed = tuple(sum(counts[j]*oscillators[n-j] for j in range(n+1))
                          for n in range(maximum+1))
    norm_trace = tuple(sum(2*j*counts[j]*oscillators[n-j] for j in range(n+1))
                       for n in range(maximum+1))
    sigma1 = [0]*(maximum+1)
    for d in range(1, maximum+1):
        for n in range(d, maximum+1, d):
            sigma1[n] += d
    heat_residual = tuple(2*n*reconstructed[n]-norm_trace[n]
                         -16*sum(sigma1[j]*reconstructed[n-j] for j in range(1, n+1))
                         for n in range(maximum+1))
    patterns = [tuple(2*x for x in partition)
                for k in range(1, 5) for partition in _partitions(k)] + [(1,)*8]
    delta = (0,) + euler_product_coefficients(((1, 24),), maximum)[:maximum]
    moment_rows = []
    passed = counts == reference and reconstructed == populations.simple and not any(heat_residual)
    root_defects = {}
    roots = lattice_shells(1)[1]
    for pattern in patterns:
        root_defects[pattern] = shell_moment(roots, pattern)-spherical_moment(240, 1, pattern)
    for n, shell in enumerate(shells):
        if not n:
            continue
        for pattern in patterns:
            actual = shell_moment(shell, pattern)
            spherical = spherical_moment(len(shell), n, pattern)
            expected = spherical + (delta[n]*root_defects[pattern] if sum(pattern) == 8 else 0)
            passed = passed and actual == expected
            moment_rows.append({"shell": n, "exponents": pattern, "moment": str(actual),
                                "spherical": str(spherical), "residual": str(actual-expected)})
    # Eight independent roots generate E8 (determinant of the undoubled
    # coordinate matrix has absolute value1). Reflection checks need not
    # sample all240 roots because these simple reflections generate W(E8).
    simple = ((1,-1,-1,-1,-1,-1,-1,1), (2,2,0,0,0,0,0,0),
              (-2,2,0,0,0,0,0,0), (0,-2,2,0,0,0,0,0),
              (0,0,-2,2,0,0,0,0), (0,0,0,-2,2,0,0,0),
              (0,0,0,0,-2,2,0,0), (0,0,0,0,0,-2,2,0))
    tested_vectors = tuple(v for shell in shells for v in shell) if exhaustive else tuple(roots)+(ZERO,)
    reflection_checks = 0
    shift_checks = 0
    for v in tested_vectors:
        for root in simple:
            reflected = weyl_reflect(v, root)
            passed = passed and in_lattice(reflected) and lattice_degree(reflected) == lattice_degree(v)
            elliptic_reindex(v, root)
            reflection_checks += 1
            shift_checks += 1
    # E8 root shell is not an8-design; the exact all-shell criterion is
    # tau(n)=0. Proving nonvanishing for every n would prove Lehmer's conjecture.
    root_axis_defect = root_defects[(8,)]
    passed = passed and root_axis_defect == Q(-3, 2)
    harmonic = harmonic_projection_coefficients()
    passed = passed and harmonic == (Q(1), Q(-7,5), Q(7,12), Q(-7,96), Q(1,768))
    higher_harmonics = harmonic_theta_receipt(maximum)
    passed = passed and higher_harmonics["passed"]
    return {
        "schema": "perfectjet/asterion-jacobi/1", "passed": bool(passed),
        "maximum_lattice_degree": maximum, "exhaustive_requested": exhaustive,
        "lattice_shell_counts": counts, "lattice_points_enumerated": sum(counts),
        "refined_character_totals": reconstructed, "heat_residual": heat_residual,
        "theta": "Theta_E8(tau,z)=sum_alpha q^(|alpha|^2/2)*exp(2*pi*i*(alpha,z))",
        "normalized_character": "H(tau,z)=Theta_E8(tau,z)/phi(q)^8",
        "charge_multiplicity": "dim V[n,alpha]=p8(n-|alpha|^2/2)",
        "heat_equations": ["(2*D_tau-sum_i D_zi^2)Theta=0",
                           "(2*D_tau-sum_i D_zi^2)H=(2/3)*(1-E2)*H",
                           "(2*D_tau-sum_i D_zi^2)chi=-(2/3)*E2*chi"],
        "derivative_convention": "D_tau=(2*pi*i)^(-1)*d_tau; D_zi=(2*pi*i)^(-1)*d_zi",
        "elliptic_shift_checks": shift_checks, "weyl_reflection_checks": reflection_checks,
        "all_order_transformations": {
            "elliptic": "Theta(tau,z+tau*lambda+mu)=q^(-|lambda|^2/2)*e^(-2*pi*i*(lambda,z))*Theta(tau,z)",
            "T": "Theta(tau+1,z)=Theta(tau,z)",
            "S": "Theta(-1/tau,z/tau)=tau^4*exp(pi*i*(z,z)/tau)*Theta(tau,z)",
            "physical_character_S": "chi(-1/tau,z/tau)=exp(pi*i*(z,z)/tau)*chi(tau,z)",
            "proof_inputs": "evenness, unimodularity, Poisson summation, eta transformations"},
        "moment_rows": moment_rows,
        "complete_tensor_coverage": "D8 permutations and even sign changes; partitions through4 plus all-odd degree8",
        "harmonic_projection_coefficients": tuple(map(str, harmonic)),
        "harmonic_modular_relation_compiler": higher_harmonics,
        "degree8_defect": {
            "root_axis_value": str(root_axis_defect),
            "all_order_identity": "sum_n [M8_n(u)-N_n*n^4*|u|^8/8]*q^n=H8_root(u)*Delta(q)",
            "H8_root": "sum_alpha_root (alpha,u)^8-30*|u|^8",
            "fock_identity": "angular_defect_H(q,u)=H8_root(u)*q*phi(q)^16",
            "ramanujan_tau_through_bound": delta,
            "all_shell_8design_criterion": "shell_n is an8-design iff tau(n)=0",
            "nonvanishing_for_all_shells_proved": False,
            "arithmetic_boundary": "Lehmer's conjecture remains open"},
        "analytic_scope": "Classical Jacobi/weighted-theta theorems; not a proof of an elliptic quantum R matrix or KZ-to-KZB monodromy identification",
        "sources": SOURCES,
    }
