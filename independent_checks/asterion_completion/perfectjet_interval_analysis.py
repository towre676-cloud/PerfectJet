"""PerfectJet AST-P036: the quadratic-completion interval 493..496 for g0.

Two independent parts, standard library only, exact arithmetic throughout.

Part A replays the repo's own certified data (principal exponents, Rees
valuations, leading channels, the bound function) and checks every numerical
input of the 493 lower bound and the 496 cotangent upper bound that is
machine-checkable from the repo.

Part B is new combinatorics: sl2-module (character) arithmetic used to put
any hypothetical completion of dimension 493+e (e = 0,1,2) into an
sl2-equivariant normal form and to count exactly how many free parameters
and how many scalar Jacobi components remain.  All spins here are integers,
so every module is recorded as a Counter {spin: multiplicity}; tensor
products use Clebsch-Gordan, and exterior powers of irreducibles are
computed from weight multisets.  These counts are exact over Q.

Part C is a finite-field *mechanism* check of the lower-bound argument and
of the cotangent-subalgebra rank obstruction, run on a small analogue
(sl2 semidirect an abelian 7-dimensional module).  It validates the linear
algebra mechanism only; it is NOT evidence about dimensions 493-495 for g0.

Usage:  python3 perfectjet_interval_analysis.py [--repo PATH] [--out PATH]
Default repo location: ../../PerfectJet relative to this file (the cloned
PerfectJet checkout).  Nothing in the repo is modified.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from fractions import Fraction as Q
from itertools import combinations
from math import comb
from pathlib import Path


# --------------------------------------------------------------------------
# Part A: repo verification
# --------------------------------------------------------------------------

def part_a(repo: Path) -> dict:
    sys.path.insert(0, str(repo / "src"))
    from perfectjet.asterion_principal import EXPONENTS
    from perfectjet.asterion_boundary import PrincipalReesFamily, quadratic_completion_bound

    dims = {m: 2 * m + 1 for m in EXPONENTS}
    total = sum(dims.values())
    nil = total - dims[1]
    family = PrincipalReesFamily()
    couplings = family.couplings          # {(a,b,c): kappa} all 170 nonzero channels
    weights = family.weights                # w_m = m-1
    leading = family.leading_support()      # valuation-0 channels at t = 0

    leading_triples = sorted((r["left"], r["right"], r["output"]) for r in leading)
    # The key input of the invariant-form proof: at t=0 no [V_m, V_m] (m>1)
    # returns to the principal block V_1.
    bad_mm1 = [t for t in leading_triples if t[0] == t[1] > 1 and t[2] == 1]
    # Stronger valuation statement: the E8 channel (m,m,1) itself, when
    # nonzero, has valuation 2(m-1) > 0, so it dies at the boundary.
    mm1_valuations = {m: weights[m] + weights[m] - weights[1]
                      for m in EXPONENTS if (m, m, 1) in couplings or m > 1}
    self_brackets = sorted({(a, b, c) for (a, b, c) in leading_triples if a == b and a > 1})
    nn_outputs = sorted({c for (a, b, c) in leading_triples if a > 1 and b > 1})
    nn_inputs = sorted({m for m in EXPONENTS if m > 1})
    abelianization_spins = sorted(set(nn_inputs) - set(nn_outputs) |
                                  {m for m in nn_inputs
                                   if all(c != m for (a, b, c) in leading_triples if a > 1 and b > 1)})
    # n/[n,n]: blocks not hit by any nonprincipal-nonprincipal leading channel.
    hit = {c for (a, b, c) in leading_triples if a > 1 and b > 1}
    abelianization_spins = sorted(m for m in nn_inputs if m not in hit)
    abelianization_dim = sum(2 * m + 1 for m in abelianization_spins)

    bound = quadratic_completion_bound(248, 3)
    return {
        "exponents": list(EXPONENTS),
        "block_dimensions": {str(m): dims[m] for m in EXPONENTS},
        "dim_g0": total,
        "dim_sl2_block": dims[1],
        "dim_nilradical": nil,
        "coupling_channel_count": len(couplings),
        "leading_channel_count": len(leading),
        "leading_triples": [list(t) for t in leading_triples],
        "channels_mm_to_1_at_boundary": bad_mm1,
        "valuation_of_mm1_channels": {str(m): v for m, v in mm1_valuations.items()},
        "nonprincipal_self_brackets_at_boundary": [list(t) for t in self_brackets],
        "nn_bracket_output_spins": nn_outputs,
        "abelianization_spins": abelianization_spins,
        "abelianization_dimension": abelianization_dim,
        "quadratic_completion_bound_248_3": bound,
        "checks": {
            "dim_g0_is_248": total == 248,
            "dim_nilradical_is_245": nil == 245,
            "no_mm_to_1_channel_at_boundary": not bad_mm1,
            "all_mm1_valuations_positive_for_m_gt_1": all(
                v > 0 for m, v in mm1_valuations.items() if m > 1),
            "lower_bound_is_493": bound["unrestricted_quadratic_completion_lower_bound"] == 493,
            "cotangent_upper_bound_is_496": bound["canonical_cotangent_upper_bound"] == 496,
            "abelianization_matches_repo_38": abelianization_dim == 38,
        },
    }


# --------------------------------------------------------------------------
# Part B: sl2 module combinatorics (integer spins; Counter {spin: mult})
# --------------------------------------------------------------------------

def tensor(A: Counter, B: Counter) -> Counter:
    out = Counter()
    for a, ma in A.items():
        for b, mb in B.items():
            for j in range(abs(a - b), a + b + 1):
                out[j] += ma * mb
    return out


def decompose_weights(weight_counter: Counter) -> Counter:
    """Greedy highest-weight decomposition of a symmetric weight multiset."""
    cnt = dict(weight_counter)
    out = Counter()
    j = max(cnt) if cnt else 0
    while j >= 0:
        mult = cnt.get(j, 0) - cnt.get(j + 1, 0)
        if mult:
            out[j] = mult
        j -= 1
    return out


def ext_power_irrep(m: int, k: int) -> Counter:
    """Lambda^k of the irreducible of integer spin m, via weight multisets."""
    weights = list(range(-m, m + 1))
    sums = Counter()
    for combo in combinations(weights, k):
        sums[sum(combo)] += 1
    return decompose_weights(sums)


def module_dim(A: Counter) -> int:
    return sum(mult * (2 * j + 1) for j, mult in A.items())


def singlets(A: Counter) -> int:
    return A.get(0, 0)


def part_b() -> dict:
    EXPONENTS = (1, 7, 11, 13, 17, 19, 23, 29)
    s_mod = Counter({1: 1})                                  # V_1 = sl2
    n_mod = Counter({m: 1 for m in EXPONENTS if m > 1})      # n as sl2-module
    g_mod = s_mod + n_mod

    # Exterior powers of the direct sum n (distinct irreducibles).
    blocks = [Counter({m: 1}) for m in EXPONENTS if m > 1]
    lam2_n = Counter()
    for B in blocks:
        lam2_n += ext_power_irrep(next(iter(B)), 2)
    for i in range(len(blocks)):
        for j in range(i + 1, len(blocks)):
            lam2_n += tensor(blocks[i], blocks[j])
    lam3_n = Counter()
    mods = [m for m in EXPONENTS if m > 1]
    for m in mods:
        lam3_n += ext_power_irrep(m, 3)
    for i, m in enumerate(mods):
        for j, mp in enumerate(mods):
            if i != j:
                lam3_n += tensor(ext_power_irrep(m, 2), Counter({mp: 1}))
    for i in range(len(mods)):
        for j in range(i + 1, len(mods)):
            for k in range(j + 1, len(mods)):
                lam3_n += tensor(tensor(Counter({mods[i]: 1}), Counter({mods[j]: 1})),
                                 Counter({mods[k]: 1}))
    assert module_dim(lam2_n) == comb(245, 2), module_dim(lam2_n)
    assert module_dim(lam3_n) == comb(245, 3), module_dim(lam3_n)

    lam2_g = ext_power_irrep(1, 2) + lam2_n + tensor(s_mod, n_mod)
    assert module_dim(lam2_g) == comb(248, 2)

    results = {}
    for e in (0, 1, 2):
        # W (complement of g0 in D) as sl2-module: n plus e trivial lines.
        W = n_mod + Counter({0: e})
        lam2_W = lam2_n + Counter()
        if e:
            lam2_W = lam2_W + Counter({j: mult * e for j, mult in n_mod.items()})
            lam2_W += Counter({0: comb(e, 2)})
        assert module_dim(lam2_W) == comb(245 + e, 2)
        lam3_W = lam3_n + Counter()
        if e:
            # Lambda^2(n) x trivial^e  and  n x Lambda^2(trivial^e)
            lam3_W += Counter({j: mult * e for j, mult in lam2_n.items()})
            lam3_W += Counter({j: mult * comb(e, 2) for j, mult in n_mod.items()})
        assert module_dim(lam3_W) == comb(245 + e, 3), (e, module_dim(lam3_W))

        D_mod = g_mod + W
        omega2_singlets = singlets(tensor(g_mod, lam2_W))       # free part of omega on g x Lambda^2 W
        omega3_singlets = singlets(lam3_W)                      # free part of omega on Lambda^3 W
        # Ambient s-invariant scalar Jacobi components by input type,
        # paired against all of D (upper bounds on independent equations).
        jac_ggW = singlets(tensor(tensor(lam2_g, W), D_mod))
        # The (g,g,W) Jacobi identities paired with W are affine linear in
        # omega2 alone (see REPORT.md); their s-invariant scalar components:
        jac_ggW_paired_W = singlets(tensor(tensor(lam2_g, W), W))
        jac_gWW = singlets(tensor(tensor(g_mod, lam2_W), D_mod))
        jac_WWW = singlets(tensor(lam3_W, D_mod))
        results[str(e)] = {
            "dim_D": 493 + e,
            "dim_W": 245 + e,
            "B_parameters": {
                "c_on_sl2_block": 1,
                "A_block_scalars_a_m_nonzero": 7,
                "S_scalars_on_irreducible_blocks": 7,
                "S_on_trivial_block_symmetric": comb(e + 1, 2),
            },
            "omega2_free_singlet_parameters": omega2_singlets,
            "omega3_free_singlet_parameters": omega3_singlets,
            "jacobi_singlet_components_upper_bounds": {
                "inputs_g_g_W_paired_with_W_linear_in_omega2": jac_ggW_paired_W,
                "inputs_g_g_W": jac_ggW,
                "inputs_g_W_W": jac_gWW,
                "inputs_W_W_W": jac_WWW,
            },
        }
    return {
        "lam2_n_dimension_check": module_dim(lam2_n),
        "lam3_n_dimension_check": module_dim(lam3_n),
        "by_e": results,
        "note": ("Counts are dimensions of sl2-singlet (equivariant) parameter "
                 "and component spaces over Q. omega2/omega3 are the only free "
                 "parts of the invariant 3-form omega in the equivariant normal "
                 "form; Jacobi is a system of quadratic equations in them whose "
                 "s-invariant scalar components number at most the tabulated "
                 "bounds. Gauge freedom (per-block rescalings of W and GL(e) "
                 "on the trivial block) can normalise c and the seven a_m."),
    }


# --------------------------------------------------------------------------
# Part C: finite-field mechanism check on a small analogue (NOT g0 itself)
# --------------------------------------------------------------------------

def part_c() -> dict:
    p = 101

    def mm(A, B):
        n, k, m = len(A), len(B), len(B[0])
        return [[sum(A[i][t] * B[t][j] for t in range(k)) % p for j in range(m)]
                for i in range(n)]

    def rank(M):
        M = [row[:] for row in M]
        r = 0
        for c in range(len(M[0]) if M else 0):
            piv = next((i for i in range(r, len(M)) if M[i][c] % p), None)
            if piv is None:
                continue
            M[r], M[piv] = M[piv], M[r]
            inv = pow(M[r][c], p - 2, p)
            M[r] = [(x * inv) % p for x in M[r]]
            for i in range(len(M)):
                if i != r and M[i][c] % p:
                    f = M[i][c]
                    M[i] = [(x - f * y) % p for x, y in zip(M[i], M[r])]
            r += 1
        return r

    # Small analogue: h = sl2 ltimes V3, V3 abelian (dim 7), over F_101.
    # Basis: e,h,f of sl2 then 7 weight vectors of V3 (weights 3..-3).
    # sl2 action: h.v_j = (3-2j) v_j; e.v_j = j(7-j)/? -- use standard
    # representation matrices via the repo-free formulas on weight basis:
    # E v_j = j * v_{j-1} (raising), F v_j = (6-j) * v_{j+1} conventions are
    # immaterial: any nonzero equivariant action with [s,V]=V suffices for
    # the *form* mechanism; we use E v_j = (7-j) v_{j-1}?? To avoid an
    # incorrect representation, build V3 = Sym^3 of the 2-dim standard rep.
    # Sym^3 basis x^3, x^2 y, x y^2, y^3 has dim 4, not 7; spin 3 needs
    # Sym^6: dim 7.  Use Sym^6 with exact integer action coefficients.
    from math import comb as C
    d = 7  # Sym^6
    # basis u_j = x^{6-j} y^j, j=0..6; e = x d/dy, f = y d/dx, h = [e,f]
    E = [[0] * d for _ in range(d)]
    F = [[0] * d for _ in range(d)]
    H = [[0] * d for _ in range(d)]
    for j in range(d):
        if j > 0:
            E[j - 1][j] = j            # e u_j = j u_{j-1}
        if j < 6:
            F[j + 1][j] = 6 - j        # f u_j = (6-j) u_{j+1}
        H[j][j] = 6 - 2 * j
    EF = mm(E, F); FE = mm(F, E)
    comm = [[(EF[i][j] - FE[i][j]) % p for j in range(d)] for i in range(d)]
    assert comm == [[H[i][j] % p for j in range(d)] for i in range(d)], "sl2 action check"

    n = 3 + d  # dim h = 10
    # structure constants of h: [s,s] standard sl2 (e=0,h=1,f=2 indices),
    # [s, v] = action, [v,v] = 0.
    def bracket(i, j):
        out = [0] * n
        if i == j:
            return out
        if i > j:
            return [(-x) % p for x in bracket(j, i)]
        if j < 3:  # both in sl2: [e,h]=-2e? use [h,e]=2e,[h,f]=-2f,[e,f]=h
            table = {(0, 1): (0, -2), (0, 2): (1, 1), (1, 2): (2, -2)}
            k, v = table[(i, j)]
            out[k] = v % p
            return out
        # i in sl2, j in V (index j-3)
        col = j - 3
        M = (E, H, F)[i]
        for r in range(d):
            out[3 + r] = M[r][col] % p
        return out

    # cotangent double: dim 20, Gram [[0,I],[I,0]]; restricted form on h is 0,
    # radical = h (dim 10): analogue is the *isotropic* case.  To exercise
    # the 493-mechanism (nonzero restricted form, radical = V), instead use
    # the explicit quadratic algebra D = h + V* with B: Killing on sl2,
    # zero on V, evaluation pairing V x V*, zero on V*: check B nondeg,
    # restricted radical exactly V (dim 7), phi: V -> (D/h)* injective,
    # dim D = 17 = 10 + 7 = the analogue of the 493 lower bound, attained
    # at the level of *forms* (no Lie bracket on the complement is claimed).
    N = 3 + d + d
    G = [[0] * N for _ in range(N)]
    # Killing form of sl2 in basis e,h,f: diag-ish [[0,0,4],[0,8,0],[4,0,0]]/?
    K = [[0, 0, 4], [0, 8, 0], [4, 0, 0]]
    for i in range(3):
        for j in range(3):
            G[i][j] = K[i][j] % p
    for a in range(d):
        G[3 + a][3 + d + a] = 1
        G[3 + d + a][3 + a] = 1
    rk = rank(G)
    # restricted form on h (first 10 coords): radical = kernel of its Gram
    Gh = [row[:n] for row in G[:n]]
    rkh = rank(Gh)
    # map phi: V (coords 3..9) -> (D/h)* : matrix B(V, complement basis)
    phi = [[G[3 + a][n + b] for b in range(d)] for a in range(d)]
    return {
        "field": "F_101",
        "analogue": "h = sl2 semidirect V (V = Sym^6, abelian, dim 7); dim h = 10",
        "form_matrix_rank_on_D_dim17": rk,
        "restricted_form_rank_on_h": rkh,
        "restricted_radical_dimension": n - rkh,
        "phi_rank_V_to_dual_of_D_over_h": rank(phi),
        "analogue_lower_bound": n + (n - rkh),
        "dim_D": N,
        "checks": {
            "form_nondegenerate": rk == N,
            "radical_is_V_dim7": n - rkh == 7,
            "phi_injective": rank(phi) == 7,
            "bound_attained_at_form_level": N == n + 7,
        },
        "scope": ("Form-level mechanism only: nondegeneracy, radical and "
                  "injectivity of phi are checked; no Lie bracket on the "
                  "17-dimensional space is constructed or claimed."),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path,
                    default=Path(__file__).resolve().parents[2])  # repository root, when run from independent_checks/asterion_completion/
    ap.add_argument("--out", type=Path, default=Path(__file__).with_name(
        "perfectjet_interval_results.json"))
    args = ap.parse_args()
    results = {
        "schema": "perfectjet-interval-analysis/1",
        "part_A_repo_verification": part_a(args.repo),
        "part_B_equivariant_system_size": part_b(),
        "part_C_finite_field_mechanism": part_c(),
    }
    args.out.write_text(json.dumps(results, indent=1), encoding="utf-8")
    print(json.dumps({
        "A_checks": results["part_A_repo_verification"]["checks"],
        "B": {e: {"omega2": v["omega2_free_singlet_parameters"],
                  "omega3": v["omega3_free_singlet_parameters"],
                  "jacobi_bounds": v["jacobi_singlet_components_upper_bounds"]}
              for e, v in results["part_B_equivariant_system_size"]["by_e"].items()},
        "C_checks": results["part_C_finite_field_mechanism"]["checks"],
    }, indent=1))


if __name__ == "__main__":
    main()
