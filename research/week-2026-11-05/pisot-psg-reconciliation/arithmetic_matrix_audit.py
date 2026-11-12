"""Exact checks of matrices printed in recovered Pisot manuscripts.

This checks the displayed finite matrices, not the alleged extraction from a
hat-tiling corpus, global tiling gap labels, or a physical flavor model.
Dependencies: sympy. Run directly to emit a JSON audit.
"""
import json
import sympy as s

x, z = s.symbols("x z")
A = s.Matrix([
    [0, 1, 1, 1, 0, 0],
    [1, 0, 0, 0, 0, 0],
    [1, 0, 0, 1, 0, 1],
    [1, 0, 1, 0, 1, 0],
    [0, 0, 0, 1, 0, 0],
    [0, 0, 1, 0, 0, 0],
])
permutation = [0, 2, 3, 1, 5, 4]
Ar = A.extract(permutation, permutation)
u = s.ones(3, 1) / s.sqrt(3)
v = s.Matrix([1, -1, 0]) / s.sqrt(2)
w = s.Matrix([1, 1, -2]) / s.sqrt(6)
zero = s.zeros(3, 1)
U = s.Matrix.hstack(*[
    c for r in [u, v, w]
    for c in [r.col_join(zero), zero.col_join(r)]
])
plus = s.Matrix([[2, 1], [1, 0]])
minus = s.Matrix([[-1, 1], [1, 0]])
decomposition = s.diag(plus, minus, minus)

edges = [(i, j) for i in range(6) for j in range(6) if A[i, j]]
B = s.Matrix([
    [int(v == v2 and w != u) for v2, w in edges]
    for u, v in edges
])

T = s.Matrix([
    [s.Rational("1.17"), s.Rational(".24"), s.Rational(".11")],
    [s.Rational(".64"), s.Rational("1.21"), s.Rational(".045")],
    [s.Rational(".018"), s.Rational(".015"), s.Rational(".96")],
])
eig_gram = s.nroots((T.T * T).charpoly(x).as_expr(), n=40)
b, b1, m = s.symbols("b b1 m", nonzero=True)
claimed_phi = 1 / (b*m) - b1 / b**2 * s.log(1 + b1*m/b)
claimed_derivative = s.factor(s.diff(claimed_phi, m) * (b*m**2 + b1*m**3))

checks = {
    "A_symmetric": A == A.T,
    "core_leaf_block_form": Ar == s.BlockMatrix([
        [s.ones(3)-s.eye(3), s.eye(3)],
        [s.eye(3), s.zeros(3)],
    ]).as_explicit(),
    "basis_orthogonal": s.simplify(U.T * U) == s.eye(6),
    "exact_2_plus_2_plus_2_decomposition": s.simplify(U.T * Ar * U) == decomposition,
    "A_characteristic_polynomial": s.expand(A.charpoly(x).as_expr() -
        (x**2-2*x-1)*(x**2+x-1)**2) == 0,
    "B_characteristic_polynomial": s.expand(B.charpoly(x).as_expr() -
        x**6*(x**3-1)**2) == 0,
    "B_L_factor": s.expand((s.eye(12)-z*B).det()-(1-z**3)**2) == 0,
    "B_eventual_period_three_from_power_two": B**5 == B**2,
    "B_path_counts_24_in_each_eventual_residue": all(sum(B**n) == 24 for n in (2, 3, 4)),
    "T_exact_full_rank": T.det() == s.Rational(24193617, 20000000),
}
result = {
    "status": "PASS" if all(checks.values()) else "FAIL",
    "scope": "Exact finite-matrix audit; no corpus provenance or global tiling certification.",
    "sources": [
        {"name": "triskelion_writeup.md", "library_file_id": "libfile_3117ef75ff4c8191baa3ca37ae0e609d",
         "file_id": "file_00000000e99071fd9b0c472b63811175", "lines": "123-198"},
        {"name": "# Pisot Embeddings, Delzant Polytop.txt", "library_file_id": "libfile_014e5b3db7648191afabba9bffaaaca4",
         "file_id": "file_0000000035fc722f87a815f281636f44", "lines": "101-132"},
    ],
    "checks": checks,
    "A_characteristic_polynomial": str(s.factor(A.charpoly(x).as_expr())),
    "B_characteristic_polynomial": str(s.factor(B.charpoly(x).as_expr())),
    "B_zero_algebraic_multiplicity": 6,
    "B_zero_geometric_multiplicity": 12-B.rank(),
    "B_trace_at_n": "6 if n is a positive multiple of 3; 0 otherwise",
    "T_determinant": str(T.det()),
    "T_rank": T.rank(),
    "T_singular_values_approx": [str(s.sqrt(y).evalf(30)) for y in eig_gram[::-1]],
    "claimed_two_loop_primitive_actual_time_derivative": str(claimed_derivative),
}
print(json.dumps(result, indent=2))
raise SystemExit(0 if all(checks.values()) else 1)
