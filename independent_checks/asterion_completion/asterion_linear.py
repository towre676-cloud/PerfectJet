"""Asterion AST-P036, e = 0 stage: assemble and solve the affine-linear
Jacobi system for a quadratic completion of g0 in dimension 493.

Background (see REPORT.md and the prior interval report
../../improvements_next/perfectjet_interval/REPORT.md, section 5):
any quadratic completion of the boundary algebra g0 = sl2 ltimes n
(dim 248, n of dim 245) in dimension 493 has, after the sl2-equivariant
gauge fixing c = 1 and a_m = 1, free data

    omega2 : 162 sl2-singlet channels in g0 (x) Lambda^2 W,
    S      : 7 scalars s_m, one per W-block V_m (m = 7,11,13,17,19,23,29),
    omega3 : 68 channels in Lambda^3 W (do not enter this stage),

and the (g0, g0, W) Jacobi components paired against W form an affine
linear system in the 169 unknowns (omega2, S) whose target
Hom_sl2(Lambda^2 g0 (x) W, W) has dimension 22688.

This script assembles that system EXACTLY over Q and solves it:

  * g0 structure constants at t = 0 come from the repository's own
    principal-basis data (PrincipalE8Basis couplings + monomial
    transvectants), cross-checked against PrincipalReesFamily.
  * omega2 channels and the Jacobi channel components are parametrised
    by sl2 transvectant (Clebsch-Gordan) channels in the binomial
    polynomial basis, where every coefficient is rational.
  * The system is extracted sector by sector: for each pair of g0
    blocks (a, b) and W blocks (c, d), the Jacobi tensor restricted to
    the sector is a linear combination of the sector's singlet channels
    T_J; evaluating at greedily selected weight tuples and inverting
    the (square, exact) evaluation matrix gives the channel components
    f_J(omega2, S), one affine equation per channel (22688 in total).
  * The system is then solved exactly over Q (rank found modularly,
    solution/Farkas certificate computed and verified over Q).

Outputs (in the directory of this script, or --out):
  asterion_linear_results.json   summary, checks, solution or Farkas data
  asterion_linear_system.json the 22688 affine equations (row data)
  asterion_linear_run.log        stage log

Usage: python3 asterion_linear.py [--repo PATH] [--out DIR]
Default repo: ../../PerfectJet relative to this file.  The repo is only
read, never modified.  Standard library only, except numpy (if present)
for the modular rank pass; a pure-Python fallback is included.
"""
from __future__ import annotations

import argparse
import gzip
import json
import random
import sys
import time
from fractions import Fraction as Q
from functools import lru_cache
from math import comb
from pathlib import Path

ZERO = Q(0)
ONE = Q(1)


def log(msg):
    print(msg, flush=True)
    LOG_LINES.append(msg)


LOG_LINES = []


# ---------------------------------------------------------------------------
# Repository data and the exact g0 bracket at t = 0
# ---------------------------------------------------------------------------

class Model:
    def __init__(self, repo: Path):
        sys.path.insert(0, str(repo / "src"))
        from perfectjet.asterion_principal import (
            EXPONENTS, PrincipalE8Basis, monomial_transvectant)
        self.EXPONENTS = EXPONENTS
        self.M = tuple(m for m in EXPONENTS if m > 1)
        self.basis = PrincipalE8Basis()
        self.couplings = self.basis.couplings()
        self._transvectant = monomial_transvectant
        self._transv_cache = {}

    # -- transvectant coefficient on binomial-normalised monomials:
    # T_r(e_i^a, e_j^b) = transv(a,i,b,j,r) * e_{i+j-r}^{a+b-r}
    def transv(self, a, i, b, j, r):
        key = (a, i, b, j, r)
        v = self._transv_cache.get(key)
        if v is None:
            v = self._transv(a, i, b, j, r)
            self._transv_cache[key] = v
        return v

    def _transv(self, a, i, b, j, r):
        if r < 0 or r > min(2 * a, 2 * b):
            return ZERO
        if not (0 <= i <= 2 * a and 0 <= j <= 2 * b):
            return ZERO
        c = a + b - r
        o = i + j - r
        if o < 0 or o > 2 * c:
            return ZERO
        mt = self._transvectant(a, i, b, j, r)
        if not mt:
            return ZERO
        return Q(mt, comb(2 * c, o))

    # -- invariant symmetric form on V_m (binomial basis):
    # beta_m(e_p, e_q) = (-1)^p C(2m, p) if p + q == 2m else 0.
    @staticmethod
    def beta(m, p, q):
        if p + q != 2 * m:
            return ZERO
        return Q((-1) ** p * comb(2 * m, p))

    # -- g0 bracket at t = 0: [e_i^a, e_j^b] = coeff * e_o^{a+b-1} or None.
    @lru_cache(maxsize=None)
    def bracket_g0(self, a, i, b, j):
        if (a, i) == (b, j):
            return None
        sign = 1
        if (a, i) > (b, j):
            a, i, b, j = b, j, a, i
            sign = -1
        c = a + b - 1
        if c not in self.EXPONENTS:
            return None
        kappa = self.couplings.get((min(a, b), max(a, b), c), ZERO)
        if not kappa:
            return None
        o = i + j - 1
        if o < 0 or o > 2 * c:
            return None
        coeff = sign * kappa * self.transv(a, i, b, j, 1)
        if not coeff:
            return None
        return (c, o, coeff)


# ---------------------------------------------------------------------------
# Affine forms in the 169 unknowns: (const, {param_index: coeff})
# params 0..161: omega2 channels (a, b, d) sorted; 162..168: s_m
# ---------------------------------------------------------------------------

def aff_const(c):
    return (Q(c), {})


def aff_param(idx, coeff):
    return (ZERO, {idx: Q(coeff)})


AFF_ZERO = (ZERO, {})


def aff_add(x, y):
    if not x[1]:
        return (x[0] + y[0], y[1])
    if not y[1]:
        return (x[0] + y[0], x[1])
    d = dict(x[1])
    for k, v in y[1].items():
        nv = d.get(k, ZERO) + v
        if nv:
            d[k] = nv
        elif k in d:
            del d[k]
    return (x[0] + y[0], d)


def aff_scale(x, s):
    s = Q(s)
    if not s:
        return AFF_ZERO
    if s == 1:
        return x
    return (x[0] * s, {k: v * s for k, v in x[1].items()})


def aff_is_const(x):
    return not x[1]


def aff_eval(x, params):
    total = x[0]
    for k, v in x[1].items():
        total += v * params[k]
    return total


# ---------------------------------------------------------------------------
# The completion model: channels, brackets, Jacobiator
# ---------------------------------------------------------------------------

class Completion:
    def __init__(self, model: Model):
        self.md = model
        self.E = model.EXPONENTS
        self.M = model.M
        # omega2 channels: (a; b, d), b <= d in M, singlet via r = b+d-a,
        # triangle condition, and r odd when b == d (alternating slot).
        channels = []
        for a in self.E:
            for bi, b in enumerate(self.M):
                for d in self.M[bi:]:
                    r = b + d - a
                    if r < 0 or a < abs(b - d):
                        continue
                    if b == d and r % 2 == 0:
                        continue
                    channels.append((a, b, d))
        channels.sort()
        self.channels = channels
        self.channel_index = {ch: i for i, ch in enumerate(channels)}
        self.n_omega2 = len(channels)
        self.s_index = {m: self.n_omega2 + k for k, m in enumerate(self.M)}
        self.n_params = self.n_omega2 + len(self.M)
        # For the covector of [x, w]: channels touching (a, w-block).
        self.ch_from = {}
        for idx, (a, b, d) in enumerate(channels):
            r = b + d - a
            self.ch_from.setdefault((a, b), []).append((idx, d, r, False))
            if d != b:
                self.ch_from.setdefault((a, d), []).append((idx, b, r, True))
        self._bgw_cache = {}

    # omega2 value on (x=(a,i), w=(b,j), w'=(d,l)) as an affine form.
    def omega2(self, a, i, b, j, d, l):
        md = self.md
        if b < d:
            idx = self.channel_index.get((a, b, d))
            if idx is None:
                return AFF_ZERO
            r = b + d - a
            o = j + l - r
            if o + i != 2 * a:
                return AFF_ZERO
            val = md.transv(b, j, d, l, r) * Q((-1) ** o * comb(2 * a, o))
            return aff_param(idx, val) if val else AFF_ZERO
        if b > d:
            idx = self.channel_index.get((a, d, b))
            if idx is None:
                return AFF_ZERO
            r = b + d - a
            o = j + l - r
            if o + i != 2 * a:
                return AFF_ZERO
            val = -md.transv(d, l, b, j, r) * Q((-1) ** o * comb(2 * a, o))
            return aff_param(idx, val) if val else AFF_ZERO
        # b == d
        idx = self.channel_index.get((a, b, b))
        if idx is None:
            return AFF_ZERO
        r = 2 * b - a
        o = j + l - r
        if o + i != 2 * a:
            return AFF_ZERO
        val = md.transv(b, j, b, l, r) * Q((-1) ** o * comb(2 * a, o))
        return aff_param(idx, val) if val else AFF_ZERO

    # Bracket [x, w], x a g0 basis key (a, i), w a W basis key (mw, kw).
    # Returns dict over D keys: ('g', m, i) for g0, ('w', m, i) for W,
    # with affine values.  Uses B^{-1} block formulas:
    #   u_s(i)   = v_s(2-i)   * (-1)^i / C(2, i)
    #   u_W(q)   = v_n(2m-q)  * (-1)^q / C(2m, q)          (per block m)
    #   u_n(q)   = (v_W - S u_W)(2m-q) * (-1)^q / C(2m, q), and on block m
    #              (S u_W)(p) = s_m * v_n(p).
    def bracket_g0_w(self, x, w):
        key = (x, w)
        hit = self._bgw_cache.get(key)
        if hit is not None:
            return hit
        md = self.md
        (a, i), (mw, kw) = x, w
        v_s = {}    # index t -> Q (const)
        v_n = {}    # (b, l) -> Q (const)
        v_w = {}    # (d, l) -> affine
        # v_n: the single candidate z in n with [x, z] landing on block mw
        # at output index 2*mw - kw.  (b == 1 would put z in the sl2 block;
        # that is the v_s case below, which is the same condition a == mw.)
        b = mw - a + 1
        if b in self.M:
            l = 2 * mw - kw - i + 1
            if 0 <= l <= 2 * b:
                br = md.bracket_g0(a, i, b, l)
                if br and br[0] == mw and br[1] == 2 * mw - kw:
                    val = -br[2] * md.beta(mw, br[1], kw)
                    if val:
                        v_n[(b, l)] = val
        # v_s: z in the sl2 block; needs a == mw.
        if a == mw:
            t = 2 * mw - kw - i + 1
            if 0 <= t <= 2:
                br = md.bracket_g0(a, i, 1, t)
                if br and br[0] == mw and br[1] == 2 * mw - kw:
                    val = -br[2] * md.beta(mw, br[1], kw)
                    if val:
                        v_s[t] = val
        # v_W: omega2 channels touching (a, mw); partner index fixed by
        # the weight condition.
        for idx, d, r, swapped in self.ch_from.get((a, mw), ()):  # noqa: B007
            l = a + mw + d - i - kw
            if not (0 <= l <= 2 * d):
                continue
            ch = self.channels[idx]
            ca, cb, cd = ch
            if not swapped:
                val = md.transv(cb, kw, cd, l, r) * Q((-1) ** (kw + l - r)
                                                      * comb(2 * a, kw + l - r)) \
                    if kw + l - r + i == 2 * a else ZERO
            else:
                val = -md.transv(cb, l, cd, kw, r) * Q((-1) ** (kw + l - r)
                                                       * comb(2 * a, kw + l - r)) \
                    if kw + l - r + i == 2 * a else ZERO
            if val:
                v_w[(d, l)] = aff_param(idx, val)
        # apply B^{-1}
        u = {}
        for t, val in v_s.items():
            q = 2 - t
            u[('g', 1, q)] = aff_const(val * Q((-1) ** q, comb(2, q)))
        vn_by_block = {}
        for (bb, l), val in v_n.items():
            vn_by_block.setdefault(bb, {})[l] = val
        for bb, blk in vn_by_block.items():
            for l, val in blk.items():
                q = 2 * bb - l
                u[('w', bb, q)] = aff_const(val * Q((-1) ** q, comb(2 * bb, q)))
        blocks_w = {d for (d, _l) in v_w} | set(vn_by_block)
        for m in blocks_w:
            rhs = {}
            for (d, l), aval in v_w.items():
                if d == m:
                    rhs[l] = aval
            if m in vn_by_block:
                sp = self.s_index[m]
                for l, val in vn_by_block[m].items():
                    term = (ZERO, {sp: -val})
                    rhs[l] = aff_add(rhs[l], term) if l in rhs else term
            for l, aval in rhs.items():
                q = 2 * m - l
                u[('g', m, q)] = aff_add(u.get(('g', m, q), AFF_ZERO),
                                         aff_scale(aval, Q((-1) ** q, comb(2 * m, q))))
        u = {k: v for k, v in u.items() if v[0] or v[1]}
        self._bgw_cache[key] = u
        return u

    # Bracket [x, u] for x a g0 basis key and u a D vector (dict of affine).
    # W-components of u must be constant (true in the (g0,g0,W) Jacobi use).
    def bracket_g0_d(self, x, u):
        md = self.md
        out = {}
        for key, alpha in u.items():
            if key[0] == 'g':
                br = md.bracket_g0(x[0], x[1], key[1], key[2])
                if br:
                    k2 = ('g', br[0], br[1])
                    out[k2] = aff_add(out.get(k2, AFF_ZERO), aff_scale(alpha, br[2]))
            else:
                if not aff_is_const(alpha):
                    raise ArithmeticError("non-constant W coefficient in bracket_g0_d")
                bw = self.bracket_g0_w(x, (key[1], key[2]))
                c0 = alpha[0]
                if c0:
                    for k2, bv in bw.items():
                        out[k2] = aff_add(out.get(k2, AFF_ZERO), aff_scale(bv, c0))
        return {k: v for k, v in out.items() if v[0] or v[1]}

    # Jacobiator J(x, y, w) as a D vector of affine forms.
    def jacobi(self, x, y, w):
        t1 = self.bracket_g0_d(x, self.bracket_g0_w(y, w))
        t2 = self.bracket_g0_d(y, self.bracket_g0_w(x, w))
        out = dict(t1)
        for k, v in t2.items():
            out[k] = aff_add(out.get(k, AFF_ZERO), aff_scale(v, -1))
        br = self.md.bracket_g0(x[0], x[1], y[0], y[1])
        if br:
            t3 = self.bracket_g0_w((br[0], br[1]), w)
            for k, v in t3.items():
                out[k] = aff_add(out.get(k, AFF_ZERO), aff_scale(v, -br[2]))
        return {k: v for k, v in out.items() if v[0] or v[1]}

    # F = B(J, w') : the scalar (g0, g0, W) Jacobi component against W.
    def pair_w(self, J, wp):
        md = self.md
        d, l = wp
        total = AFF_ZERO
        for key, val in J.items():
            if key[0] == 'g' and key[1] == d:
                bv = md.beta(d, key[2], l)
                if bv:
                    total = aff_add(total, aff_scale(val, bv))
            elif key[0] == 'w' and key[1] == d:
                if not aff_is_const(val):
                    raise ArithmeticError("non-constant J_W in pair_w")
                bv = md.beta(d, key[2], l)
                if bv and val[0]:
                    total = aff_add(total, (ZERO, {self.s_index[d]: val[0] * bv}))
        return total

    # B(J, z) for z a g0 basis key: used to verify the identically-zero
    # components paired against g0.
    def pair_g0(self, J, z):
        md = self.md
        m, l = z
        total = AFF_ZERO
        if m == 1:
            for key, val in J.items():
                if key[0] == 'g' and key[1] == 1:
                    bv = md.beta(1, key[2], l)
                    if bv:
                        total = aff_add(total, aff_scale(val, bv))
        else:
            for key, val in J.items():
                if key[0] == 'w' and key[1] == m:
                    bv = md.beta(m, key[2], l)
                    if bv:
                        total = aff_add(total, aff_scale(val, bv))
        return total


# ---------------------------------------------------------------------------
# Sector extraction of the Jacobi channel components
# ---------------------------------------------------------------------------

def spins(x, y):
    return set(range(abs(x - y), x + y + 1))


def sector_channels(a, b, c, d):
    sab = spins(a, b)
    if a == b:
        sab = {J for J in sab if (a + b - J) % 2 == 1}
    return sorted(sab & spins(c, d))


def chan_val(md, a, b, c, d, J, i, j, k, l):
    r1 = a + b - J
    r2 = c + d - J
    o1 = i + j - r1
    o2 = k + l - r2
    if o1 < 0 or o1 > 2 * J or o2 < 0 or o2 > 2 * J or o1 + o2 != 2 * J:
        return ZERO
    t1 = md.transv(a, i, b, j, r1)
    if not t1:
        return ZERO
    t2 = md.transv(c, k, d, l, r2)
    if not t2:
        return ZERO
    return t1 * t2 * Q((-1) ** o1 * comb(2 * J, o1))


def reduce_vec(vec, basis):
    """basis: list of (pivot, row) in RREF. Returns reduced vec."""
    v = list(vec)
    for piv, row in basis:
        if v[piv]:
            f = v[piv]
            v = [x - f * y for x, y in zip(v, row)]
    return v


def solve_square_affine(mat, rhs):
    """Solve mat * f = rhs exactly; mat: n x n Fractions, rhs: affine list."""
    n = len(mat)
    rows = [list(mat[i]) + [rhs[i]] for i in range(n)]
    for col in range(n):
        piv = next((r for r in range(col, n) if rows[r][col]), None)
        if piv is None:
            raise ArithmeticError("singular evaluation matrix")
        rows[col], rows[piv] = rows[piv], rows[col]
        pv = rows[col][col]
        rows[col] = [x / pv for x in rows[col][:n]] + \
                    [aff_scale(rows[col][n], 1 / pv)]
        for r in range(n):
            if r != col and rows[r][col]:
                f = rows[r][col]
                rows[r] = [x - f * y for x, y in zip(rows[r][:n], rows[col][:n])] + \
                          [aff_add(rows[r][n], aff_scale(rows[col][n], -f))]
    return [rows[i][n] for i in range(n)]


def extract_sector(cp: Completion, a, b, c, d, rng):
    """Return (Js, tuples, f_affines) for one sector."""
    md = cp.md
    Js = sector_channels(a, b, c, d)
    nch = len(Js)
    if nch == 0:
        return Js, [], []
    total_wt = a + b + c + d
    cands = []
    for i in range(2 * a + 1):
        for j in range(2 * b + 1):
            for k in range(2 * c + 1):
                l = total_wt - i - j - k
                if 0 <= l <= 2 * d:
                    cands.append((i, j, k, l))
    rng.shuffle(cands)
    basis = []
    chosen = []
    chosen_vals = []
    for (i, j, k, l) in cands:
        vals = [chan_val(md, a, b, c, d, J, i, j, k, l) for J in Js]
        if not any(vals):
            continue
        red = reduce_vec(vals, basis)
        piv = next((t for t, x in enumerate(red) if x), None)
        if piv is None:
            continue
        inv = red[piv]
        newrow = [x / inv for x in red]
        new_basis = []
        for p, row in basis:
            if row[piv]:
                f = row[piv]
                row = [x - f * y for x, y in zip(row, newrow)]
            new_basis.append((p, row))
        new_basis.append((piv, newrow))
        new_basis.sort(key=lambda t: t[0])
        basis = new_basis
        chosen.append((i, j, k, l))
        chosen_vals.append(vals)
        if len(chosen) == nch:
            break
    if len(chosen) < nch:
        raise ArithmeticError(f"sector {(a, b, c, d)}: evaluation rank "
                              f"{len(chosen)} < {nch} channels")
    fvals = []
    for (i, j, k, l) in chosen:
        J = cp.jacobi((a, i), (b, j), (c, k))
        fvals.append(cp.pair_w(J, (d, l)))
    f = solve_square_affine(chosen_vals, fvals)
    return Js, chosen, f


# ---------------------------------------------------------------------------
# Exact linear algebra over Q (small systems) and modular rank (numpy)
# ---------------------------------------------------------------------------

def rref_q(mat, ncols):
    """RREF over Q of a list of lists of Fractions. Returns (rows, pivots)."""
    rows = [list(r) for r in mat]
    pivots = []
    r = 0
    for col in range(ncols):
        piv = next((i for i in range(r, len(rows)) if rows[i][col]), None)
        if piv is None:
            continue
        rows[r], rows[piv] = rows[piv], rows[r]
        inv = ONE / rows[r][col]
        rows[r] = [x * inv for x in rows[r]]
        for i in range(len(rows)):
            if i != r and rows[i][col]:
                f = rows[i][col]
                rows[i] = [x - f * y for x, y in zip(rows[i], rows[r])]
        pivots.append(col)
        r += 1
        if r == len(rows):
            break
    return rows, pivots


def solve_subsystem(rows_data, idxs, n_params):
    """Exact solve of subsystem rows_data[i], i in idxs.
    rows_data rows are (coeffs dict, const): sum coeff*x + const = 0.
    Returns dict with rank, consistent, and either particular+null basis
    or a Farkas certificate supported on idxs."""
    mat = []
    for i in idxs:
        coeffs, const = rows_data[i]
        row = [coeffs.get(j, ZERO) for j in range(n_params)] + [const]
        mat.append(row)
    # RREF with transformation tracking for Farkas extraction.
    n = len(mat)
    aug = [mat[i] + [ONE if j == i else ZERO for j in range(n)] for i in range(n)]
    pivots = []
    r = 0
    for col in range(n_params + 1):
        piv = next((i for i in range(r, n) if aug[i][col]), None)
        if piv is None:
            continue
        aug[r], aug[piv] = aug[piv], aug[r]
        inv = ONE / aug[r][col]
        aug[r] = [x * inv for x in aug[r]]
        for i in range(n):
            if i != r and aug[i][col]:
                f = aug[i][col]
                aug[i] = [x - f * y for x, y in zip(aug[i], aug[r])]
        pivots.append(col)
        r += 1
        if r == n:
            break
    coeff_rank = sum(1 for p in pivots if p < n_params)
    # inconsistency: a row that is zero on coefficients but nonzero on const
    for i in range(n):
        if all(not aug[i][col] for col in range(n_params)) and aug[i][n_params]:
            lam = aug[i][n_params + 1:]
            return {"consistent": False, "rank": coeff_rank, "farkas_lambda": lam,
                    "farkas_rows": list(idxs)}
    # particular solution and null basis from RREF (coeff pivots only)
    pivot_cols = [p for p in pivots if p < n_params]
    free_cols = [c for c in range(n_params) if c not in pivot_cols]
    particular = [ZERO] * n_params
    for row_i, pc in enumerate(pivot_cols):
        particular[pc] = -aug[row_i][n_params]
    null_basis = []
    for fc in free_cols:
        vec = [ZERO] * n_params
        vec[fc] = ONE
        for row_i, pc in enumerate(pivot_cols):
            vec[pc] = -aug[row_i][fc]
        null_basis.append(vec)
    return {"consistent": True, "rank": coeff_rank, "particular": particular,
            "null_basis": null_basis}


def egcd_inv(a, p):
    a %= p
    t, nt = 0, 1
    r, nr = p, a
    while nr:
        q = r // nr
        t, nt = nt, t - q * nt
        r, nr = nr, r - q * nr
    return t % p


def modular_rank(rows_data, n_params, p):
    """Forward elimination mod p on [A | -const]; returns
    (rank, consistent, pivot_row_indices)."""
    import numpy as np
    nrows = len(rows_data)
    M = np.zeros((nrows, n_params + 1), dtype=np.int64)
    inv_cache = {}
    for ri, (coeffs, const) in enumerate(rows_data):
        for cj, frac in coeffs.items():
            den = frac.denominator % p
            if den not in inv_cache:
                inv_cache[den] = egcd_inv(den, p)
            M[ri, cj] = (frac.numerator % p) * inv_cache[den] % p
        den = const.denominator % p
        if den not in inv_cache:
            inv_cache[den] = egcd_inv(den, p)
        M[ri, n_params] = (-const.numerator % p) * inv_cache[den] % p
    perm = list(range(nrows))
    piv_rows = []
    r = 0
    for col in range(n_params):
        if r >= nrows:
            break
        colvals = M[r:, col]
        nz = np.nonzero(colvals)[0]
        if len(nz) == 0:
            continue
        piv = r + int(nz[0])
        if piv != r:
            M[[r, piv]] = M[[piv, r]]
            perm[r], perm[piv] = perm[piv], perm[r]
        inv = egcd_inv(int(M[r, col]), p)
        if inv != 1:
            M[r] = (M[r] * inv) % p
        below = M[r + 1:]
        factors = below[:, col].copy()
        idxs = np.nonzero(factors)[0]
        if len(idxs):
            M[r + 1 + idxs] = (below[idxs] - factors[idxs][:, None] * M[r][None, :]) % p
        piv_rows.append(perm[r])
        r += 1
    consistent = True
    for i in range(r, nrows):
        if M[i, n_params] != 0:
            consistent = False
            break
    return r, consistent, piv_rows


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def run_checks(md: Model, cp: Completion, repo: Path):
    checks = {}
    checks["omega2_channel_count"] = cp.n_omega2
    checks["s_scalar_count"] = len(cp.M)
    checks["total_unknowns"] = cp.n_params
    total_sector = 0
    for ai, a in enumerate(cp.E):
        for b in cp.E[ai:]:
            for c in cp.M:
                for d in cp.M:
                    total_sector += len(sector_channels(a, b, c, d))
    checks["jacobi_channel_components"] = total_sector

    # beta invariance under the sl2 action (bracket with block 1).
    bad = 0
    for m in cp.M:
        for t in range(3):
            for i in range(2 * m + 1):
                for j in range(2 * m + 1):
                    s = ZERO
                    bi = md.bracket_g0(1, t, m, i)
                    if bi:
                        s += bi[2] * md.beta(m, bi[1], j)
                    bj = md.bracket_g0(1, t, m, j)
                    if bj:
                        s += bj[2] * md.beta(m, i, bj[1])
                    if s:
                        bad += 1
    checks["beta_invariance_failures"] = bad

    # bracket at t=0 against the repository's PrincipalReesFamily.
    from perfectjet.asterion_boundary import PrincipalReesFamily
    fam = PrincipalReesFamily(md.basis)
    idx = md.basis.label_index
    labels = md.basis.basis_labels
    rng = random.Random(777)
    pairs = [((a, i), (b, j)) for a in cp.E for i in range(2 * a + 1)
             for b in cp.E for j in range(2 * b + 1)]
    sample = rng.sample(pairs, 3000)
    sample += [((1, t), (m, j)) for t in range(3) for m in cp.E
               for j in range(2 * m + 1)]
    bad = 0
    for (a, i), (b, j) in sample:
        got = fam.basis_bracket(idx[(a, i)], idx[(b, j)], t=0)
        mine = md.bracket_g0(a, i, b, j)
        exp = {idx[(mine[0], mine[1])]: mine[2]} if mine else {}
        if got != exp:
            bad += 1
    checks["repo_bracket_mismatches"] = bad
    checks["repo_bracket_pairs_tested"] = len(sample)

    # g0 Jacobi on random triples (our bracket formula).
    bad = 0
    keys = [(m, j) for m in cp.E for j in range(2 * m + 1)]

    def br_vec(x, y):
        r = md.bracket_g0(x[0], x[1], y[0], y[1])
        return {(r[0], r[1]): r[2]} if r else {}

    def br_lin(x, vec):
        out = {}
        for y, c in vec.items():
            r = md.bracket_g0(x[0], x[1], y[0], y[1])
            if r:
                k = (r[0], r[1])
                out[k] = out.get(k, ZERO) + c * r[2]
        return {k: v for k, v in out.items() if v}

    for _ in range(1500):
        x, y, z = rng.choice(keys), rng.choice(keys), rng.choice(keys)
        tot = {}
        for term, sgn in ((br_lin(x, br_vec(y, z)), 1),
                          (br_lin(y, br_vec(z, x)), 1),
                          (br_lin(z, br_vec(x, y)), 1)):
            for k, v in term.items():
                tot[k] = tot.get(k, ZERO) + sgn * v
        if any(tot.values()):
            bad += 1
    checks["g0_jacobi_failures"] = bad

    # omega2 channel invariance: E-action (ad of (1,0)) annihilates each
    # channel tensor; tested on random index triples per channel.
    def chan_eval(ch, i, j, l):
        a, b, d = ch
        r = b + d - a
        o = j + l - r
        if o + i != 2 * a:
            return ZERO
        return md.transv(b, j, d, l, r) * Q((-1) ** o * comb(2 * a, o))

    def act(key_block, key_idx):
        r = md.bracket_g0(1, 0, key_block, key_idx)
        return r  # (block, idx, coeff) or None

    bad = 0
    tested = 0
    for ch in cp.channels:
        a, b, d = ch
        for _ in range(6):
            i = rng.randrange(2 * a + 1)
            j = rng.randrange(2 * b + 1)
            l = rng.randrange(2 * d + 1)
            if chan_eval(ch, i, j, l) == 0 and rng.random() < 0.7:
                continue
            tested += 1
            tot = ZERO
            ra = act(a, i)
            if ra:
                tot += ra[2] * chan_eval(ch, ra[1], j, l)
            rb = act(b, j)
            if rb:
                tot += rb[2] * chan_eval(ch, i, rb[1], l)
            rd = act(d, l)
            if rd:
                tot += rd[2] * chan_eval(ch, i, j, rd[1])
            if tot:
                bad += 1
    checks["omega2_channel_invariance_failures"] = bad
    checks["omega2_channel_invariance_tests"] = tested

    # (g0, g0, W) Jacobi paired against g0 vanishes identically:
    # random tuples, affine must be zero for every g0 basis pairing.
    bad = 0
    gkeys = [(m, j) for m in cp.E for j in range(2 * m + 1)]
    wkeys = [(m, j) for m in cp.M for j in range(2 * m + 1)]
    for _ in range(1200):
        x, y, w = rng.choice(gkeys), rng.choice(gkeys), rng.choice(wkeys)
        J = cp.jacobi(x, y, w)
        if not J:
            continue
        for z in gkeys:
            val = cp.pair_g0(J, z)
            if val[0] or val[1]:
                bad += 1
                break
    checks["paired_g0_nonzero_instances"] = bad
    return checks


# ---------------------------------------------------------------------------
# Independent numeric cross-check of F (pairing-verified brackets)
# ---------------------------------------------------------------------------

def numeric_cross_check(md: Model, cp: Completion):
    """For random rational parameters and random tuples, recompute
    F = B(J(x,y,w), w') numerically.  Every [x, w] bracket used is
    verified against its defining pairings B([x,w], z) = omega(x,w,z)
    for ALL basis z, with omega evaluated directly from the definitions
    (forced part from the g0 bracket, omega2 from channels, B from the
    beta forms and S).  Returns (tested, failures)."""
    rng = random.Random(4242)
    params = [Q(rng.randrange(-5, 6), rng.choice((1, 1, 2, 3))) for _ in range(cp.n_params)]

    def B_form(u, v):
        # u, v: D vectors as dicts with keys ('g'/'w', m, i), numeric.
        tot = ZERO
        for k1, c1 in u.items():
            for k2, c2 in v.items():
                if k1[0] == 'g' and k2[0] == 'g' and k1[1] == 1 and k2[1] == 1:
                    tot += c1 * c2 * md.beta(1, k1[2], k2[2])
                elif k1[0] == 'g' and k2[0] == 'w' and k1[1] == k2[1] and k1[1] > 1:
                    tot += c1 * c2 * md.beta(k1[1], k1[2], k2[2])
                elif k1[0] == 'w' and k2[0] == 'g' and k1[1] == k2[1] and k1[1] > 1:
                    tot += c1 * c2 * md.beta(k1[1], k2[2], k1[2])
                elif k1[0] == 'w' and k2[0] == 'w' and k1[1] == k2[1]:
                    tot += c1 * c2 * params[cp.s_index[k1[1]]] * md.beta(k1[1], k1[2], k2[2])
        return tot

    def omega_val(x, y, z):
        # omega on basis keys of D: keys ('g', m, i) / ('w', m, i).
        # Totally skew; reduce to sorted type order g,g,g / g,g,w / g,w,w.
        args = [x, y, z]
        # compute sign of permutation sorting by type rank g<w, stable
        order = sorted(range(3), key=lambda t: (0 if args[t][0] == 'g' else 1))
        perm = order
        inv = sum(1 for s in range(3) for t in range(s + 1, 3) if perm[s] > perm[t])
        sgn = -1 if inv % 2 else 1
        a1, a2, a3 = (args[perm[0]], args[perm[1]], args[perm[2]])
        if a3[0] == 'g':
            # omega(g,g,g) = B0([x,y], z): only sl2 block pairs, via beta1 of
            # the g0 bracket when it lands in block 1.
            br = md.bracket_g0(a1[1], a1[2], a2[1], a2[2])
            if not br or br[0] != 1 or a3[1] != 1:
                return ZERO
            return sgn * br[2] * md.beta(1, br[1], a3[2])
        if a2[0] == 'g' and a3[0] == 'w':
            br = md.bracket_g0(a1[1], a1[2], a2[1], a2[2])
            if not br or br[0] != a3[1]:
                return ZERO
            return sgn * br[2] * md.beta(br[0], br[1], a3[2])
        if a2[0] == 'w':
            val = cp.omega2(a1[1], a1[2], a2[1], a2[2], a3[1], a3[2])
            return sgn * aff_eval(val, params)
        return ZERO

    def bgw_checked(x, w):
        aff = cp.bracket_g0_w(x, w)
        vec = {k: aff_eval(v, params) for k, v in aff.items()}
        vec = {k: v for k, v in vec.items() if v}
        # verify defining pairings against every basis vector of D
        basis = [(('g', m, i)) for m in cp.E for i in range(2 * m + 1)] + \
                [(('w', m, i)) for m in cp.M for i in range(2 * m + 1)]
        xk = ('g', x[0], x[1])
        wk = ('w', w[0], w[1])
        for zk in basis:
            lhs = B_form(vec, {zk: ONE})
            rhs = omega_val(xk, wk, zk)
            if lhs != rhs:
                raise ArithmeticError(f"pairing failure {x} {w} {zk}: {lhs} != {rhs}")
        return vec

    def bgd_numeric(x, vec):
        out = {}
        for key, c in vec.items():
            if key[0] == 'g':
                br = md.bracket_g0(x[0], x[1], key[1], key[2])
                if br:
                    k2 = ('g', br[0], br[1])
                    out[k2] = out.get(k2, ZERO) + c * br[2]
            else:
                bw = bgw_checked(x, (key[1], key[2]))
                for k2, v in bw.items():
                    out[k2] = out.get(k2, ZERO) + c * v
        return {k: v for k, v in out.items() if v}

    gkeys = [(m, j) for m in cp.E for j in range(2 * m + 1)]
    wkeys = [(m, j) for m in cp.M for j in range(2 * m + 1)]
    tested = 0
    failures = 0
    for _ in range(24):
        x, y, w, wp = (rng.choice(gkeys), rng.choice(gkeys),
                       rng.choice(wkeys), rng.choice(wkeys))
        # numeric Jacobi via checked brackets
        t1 = bgd_numeric(x, bgw_checked(y, w))
        t2 = bgd_numeric(y, bgw_checked(x, w))
        J = dict(t1)
        for k, v in t2.items():
            J[k] = J.get(k, ZERO) - v
        br = md.bracket_g0(x[0], x[1], y[0], y[1])
        if br:
            t3 = bgw_checked((br[0], br[1]), w)
            for k, v in t3.items():
                J[k] = J.get(k, ZERO) - br[2] * v
        J = {k: v for k, v in J.items() if v}
        numeric = B_form(J, {('w', wp[0], wp[1]): ONE})
        aff = cp.pair_w(cp.jacobi(x, y, w), wp)
        mine = aff_eval(aff, params)
        tested += 1
        if numeric != mine:
            failures += 1
    return tested, failures


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def frac_str(x):
    return str(x)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path,
                    default=Path(__file__).resolve().parents[1])  # repository root
    ap.add_argument("--out", type=Path, default=Path(__file__).resolve().parent)
    args = ap.parse_args()
    out_dir = args.out
    out_dir.mkdir(parents=True, exist_ok=True)
    t_start = time.time()
    log(f"repo: {args.repo}")
    md = Model(args.repo)
    cp = Completion(md)
    log(f"channels: omega2={cp.n_omega2}, S={len(cp.M)}, unknowns={cp.n_params}")

    log("stage: checks")
    checks = run_checks(md, cp, args.repo)
    for k, v in checks.items():
        log(f"  check {k}: {v}")
    assert checks["omega2_channel_count"] == 162
    assert checks["total_unknowns"] == 169
    assert checks["jacobi_channel_components"] == 22688
    assert checks["beta_invariance_failures"] == 0
    assert checks["repo_bracket_mismatches"] == 0
    assert checks["g0_jacobi_failures"] == 0
    assert checks["omega2_channel_invariance_failures"] == 0
    assert checks["paired_g0_nonzero_instances"] == 0

    log("stage: numeric cross-check of F (pairing-verified brackets)")
    tested, failures = numeric_cross_check(md, cp)
    log(f"  numeric cross-check: {tested} tuples, {failures} failures")
    assert failures == 0

    log("stage: sector extraction (assembling 22688 equations)")
    t_asm = time.time()
    rng = random.Random(20261024)
    rows = []          # (sector_id, J, coeffs dict, const)
    sectors_meta = []
    E = cp.E
    for ai, a in enumerate(E):
        for b in E[ai:]:
            for c in cp.M:
                for d in cp.M:
                    Js = sector_channels(a, b, c, d)
                    if not Js:
                        continue
                    Js2, chosen, f = extract_sector(cp, a, b, c, d, rng)
                    assert Js2 == Js
                    sid = len(sectors_meta)
                    sectors_meta.append({
                        "sector": [a, b, c, d], "channels_J": Js,
                        "tuples": [list(t) for t in chosen]})
                    for J, aff in zip(Js, f):
                        rows.append((sid, J, aff[1], aff[0]))
    log(f"  assembled {len(rows)} equations in {time.time() - t_asm:.1f}s")
    assert len(rows) == 22688
    rows_data = [(coeffs, const) for (_sid, _J, coeffs, const) in rows]

    # save the system
    sys_path = out_dir / "asterion_linear_system.json"
    with open(sys_path, "w", encoding="utf-8") as fh:
        for sid, J, coeffs, const in rows:
            fh.write(json.dumps({
                "sector": sid, "J": J,
                "coeffs": {str(k): frac_str(v) for k, v in sorted(coeffs.items())},
                "const": frac_str(const)}) + "\n")
    log(f"  system written to {sys_path.name}")

    log("stage: modular rank pass")
    rank_mod = {}
    pivots_mod = {}
    for p in (1000003, 999983):
        r, cons, piv = modular_rank(rows_data, cp.n_params, p)
        rank_mod[p] = (r, cons)
        pivots_mod[p] = piv
        log(f"  mod {p}: rank={r}, consistent={cons}")
    p0 = 1000003
    subsystem = list(pivots_mod[p0])

    log("stage: exact solve over Q (subsystem + verification loop)")
    result = None
    for _attempt in range(12):
        sol = solve_subsystem(rows_data, subsystem, cp.n_params)
        if not sol["consistent"]:
            lam = sol["farkas_lambda"]
            sub_rows = sol["farkas_rows"]
            # verify Farkas against the subsystem rows exactly
            coeff_sum = [ZERO] * cp.n_params
            const_sum = ZERO
            for li, ri in zip(lam, sub_rows):
                if not li:
                    continue
                coeffs, const = rows_data[ri]
                for k, v in coeffs.items():
                    coeff_sum[k] += li * v
                const_sum += li * const
            assert all(not x for x in coeff_sum) and const_sum != 0
            result = {"outcome": "inconsistent", "rank_coefficients": sol["rank"],
                      "farkas": {"rows": sub_rows,
                                 "lambda": [frac_str(x) for x in lam],
                                 "constant_sum": frac_str(const_sum)}}
            log(f"  INCONSISTENT: Farkas certificate on {len(sub_rows)} rows, "
                f"constant sum {const_sum}")
            break
        # verify solution against ALL rows
        particular = sol["particular"]
        null_basis = sol["null_basis"]
        failing = None
        for ri, (coeffs, const) in enumerate(rows_data):
            val = const
            for k, v in coeffs.items():
                if particular[k]:
                    val += v * particular[k]
            if val:
                failing = ri
                break
            for vec in null_basis:
                s = ZERO
                for k, v in coeffs.items():
                    if vec[k]:
                        s += v * vec[k]
                if s:
                    failing = ri
                    break
            if failing is not None:
                break
        if failing is None:
            result = {"outcome": "consistent", "rank": sol["rank"],
                      "solution_dimension": len(null_basis),
                      "particular": [frac_str(x) for x in particular],
                      "null_basis": [[frac_str(x) for x in vec] for vec in null_basis]}
            log(f"  CONSISTENT: rank={sol['rank']}, solution affine dimension "
                f"{len(null_basis)} (verified against all {len(rows_data)} rows)")
            break
        subsystem.append(failing)
        log(f"  row {failing} not satisfied by subsystem solution; adding it "
            f"(subsystem size {len(subsystem)})")
    if result is None:
        raise ArithmeticError("solve loop did not terminate")

    results = {
        "schema": "asterion-linear-e0/1",
        "repo": str(args.repo),
        "checks": checks,
        "numeric_cross_check": {"tuples": tested, "failures": failures},
        "modular_ranks": {str(p): {"rank": r, "consistent": c}
                          for p, (r, c) in rank_mod.items()},
        "system": {"equations": len(rows_data), "unknowns": cp.n_params,
                   "omega2_channels": [list(ch) for ch in cp.channels],
                   "s_params": {str(m): cp.s_index[m] for m in cp.M},
                   "sectors": sectors_meta},
        "result": result,
        "timing_seconds": round(time.time() - t_start, 1),
    }
    if result["outcome"] == "consistent":
        dim = result["solution_dimension"]
        results["reduced_remaining"] = {
            "free_in_omega2_S_after_linear_stage": dim,
            "omega3_parameters": 68,
            "total_free_for_quadratic_stage": dim + 68}
    res_path = out_dir / "asterion_linear_results.json"
    res_path.write_text(json.dumps(results, indent=1), encoding="utf-8")
    log(f"results written to {res_path.name}; total {time.time() - t_start:.1f}s")
    (out_dir / "asterion_linear_run.log").write_text(
        "\n".join(LOG_LINES) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
