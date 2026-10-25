"""Asterion AST-P036, e = 1 and e = 2 stages: the affine-linear
(g0, g0, W) Jacobi system for quadratic completions of
g0 = sl2 ltimes n in dimensions 494 (e = 1) and 495 (e = 2).

Generalisation of ../asterion_linear/asterion_linear.py (the e = 0
stage, which excluded dimension 493).  The normal form is PR #7's
(improvements_next/perfectjet_interval/REPORT.md, section 5):
W = n (+) 1^e as an sl2-module, gauge c = 1, a_m = 1; unknowns are the
omega2 singlet channels on g0 (x) Lambda^2 W and the S parameters
(block scalars s_m plus a general symmetric matrix on the trivial
summands 1^e).  Counts: omega2 = 169 (e=1) / 176 (e=2), of which 7e
are "mixed" channels involving a trivial W slot; S = 8 / 10; total
unknowns 177 / 186; with omega3 (68) the PR #7 totals 245 / 254.

THE e >= 1 SUBTLETY (why this is not a verbatim rerun).  Write
B = [[c beta, 0, 0], [0, 0, A], [0, A^T, S]] on (s, n, W).  For
x in g0, w in W, the bracket [x, w] is recovered from the covector
v(z) = omega(x, w, z) via B^{-1}.  Its s- and W_M-components come from
the forced part of omega (constant), its n-component is affine in
(omega2, S_M) as at e = 0, but its component on the trivial summands
is u_{W,1} = S_11^{-1} v_{W,1}, where v_{W,1}(z_u) = omega2(x, w, z_u)
is affine in the mixed channels: the inverse of the trivial block of
S enters.  The Jacobiator J(x, y, w) therefore contains, beyond the
affine part, terms

    Delta = sum_t (S_11^{-1} v^{(y,w)})_t [x, e_t]
            - sum_t (S_11^{-1} v^{(x,w)})_t [y, e_t],

where e_t are the trivial lines and [x, e_t] is supported on the
single n-block V_{a_x} (it is affine in the mixed channels of x).
Pairing against w' in W_M of block d, Delta can be nonzero only if
(a_y = c and d = a_x) or (a_x = c and d = a_y), where c is the block
of w; i.e. only in sectors with {a, b} = {c, d} as multisets,
c, d in M.  Against trivial w', S_11 cancels S_11^{-1} exactly and F
is affine in omega2 alone.  Hence:

  * in all sectors EXCEPT the 49 "diagonal" sectors {a,b} = {c,d}
    (c, d in M), F = B(J, w') is affine in (omega2, S) -- in fact
    independent of S_11 -- and those channel equations form the
    affine system solved here;
  * the 49 diagonal sectors carry 1205 genuinely quadratic channel
    equations (affine part = the e = 0 row, plus Delta, quadratic in
    the 7e mixed channels with coefficients in Q(S_11)); they are
    deferred, and counted, not extracted.

Notably, all 434 constant-only obstructing rows of the e = 0 system
lie in diagonal sectors: the 493 obstruction does NOT transfer.

Implementation: brackets are carried as "BV" objects: an affine D
vector (g0 and W_M components), the covector wtc = v_{W,1} (the
trivial-W component of the bracket is S_11^{-1} . wtc), and a list of
Delta terms (cov, {t: n-vector}) kept symbolic in S_11^{-1}.  In
pair_w, a Delta term either pairs to zero identically (checked) or
raises NonAffine -- by the analysis above this happens exactly in
diagonal sectors, which the extraction skips.  pair_w against a
trivial w' returns wtc (the S_11 cancellation), so it is exact.

Outputs (per e, in --out):
  asterion_e{e}_results.json   checks, counts, ranks, solution/Farkas
  asterion_e{e}_system.json the affine channel equations
  asterion_e{e}_run.log        stage log

Usage: python3 asterion_linear_e12.py --e {0,1,2} [--repo PATH]
       [--out DIR] [--sectors-only]
--e 0 reproduces the e = 0 setup (regression mode; with
--sectors-only it only extracts and writes the system).
Default repo: ../../PerfectJet relative to this file.  The repo is
only read.  Standard library only, except numpy (if present) for the
modular rank pass.
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
# Repository data and the exact g0 bracket at t = 0 (as e = 0 stage)
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

    @staticmethod
    def beta(m, p, q):
        if p + q != 2 * m:
            return ZERO
        return Q((-1) ** p * comb(2 * m, p))

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
# Affine forms: (const, {param_index: coeff})
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


def aff_is_zero(x):
    return not x[0] and not x[1]


# ---------------------------------------------------------------------------
# Bracket vectors (BV): affine D-vector + trivial covector + Delta terms
#
# vec: {('g', m, i) or ('w', (m, 0), i): affine}   (g0 and W_M parts)
# wtc: {t: affine}  -- covector v_{W,1}; the trivial-W component of
#        the vector is S_11^{-1} . wtc.
# delta: [(cov, {t: {(m, i): affine}})] -- contribution
#        sum_{t,u} (S_11^{-1})_{tu} cov_u * nvec_t, supported on n.
# ---------------------------------------------------------------------------

class BV:
    __slots__ = ("vec", "wtc", "delta")

    def __init__(self, vec=None, wtc=None, delta=None):
        self.vec = vec if vec is not None else {}
        self.wtc = wtc if wtc is not None else {}
        self.delta = delta if delta is not None else []

    def pruned(self):
        self.vec = {k: v for k, v in self.vec.items() if not aff_is_zero(v)}
        self.wtc = {k: v for k, v in self.wtc.items() if not aff_is_zero(v)}
        return self


def bv_add(x, y):
    vec = dict(x.vec)
    for k, v in y.vec.items():
        vec[k] = aff_add(vec[k], v) if k in vec else v
    wtc = dict(x.wtc)
    for k, v in y.wtc.items():
        wtc[k] = aff_add(wtc[k], v) if k in wtc else v
    return BV(vec, wtc, x.delta + y.delta)


def bv_scale(x, s):
    s = Q(s)
    if not s:
        return BV()
    if s == 1:
        return x
    vec = {k: aff_scale(v, s) for k, v in x.vec.items()}
    wtc = {k: aff_scale(v, s) for k, v in x.wtc.items()}
    delta = [({u: aff_scale(v, s) for u, v in cov.items()}, nd)
             for cov, nd in x.delta]
    return BV(vec, wtc, delta)


class NonAffine(Exception):
    pass


# ---------------------------------------------------------------------------
# The completion model at given e
# ---------------------------------------------------------------------------

class Completion:
    def __init__(self, model: Model, e: int):
        self.md = model
        self.e = e
        self.E = model.EXPONENTS
        self.M = model.M
        # W blocks: (spin, copy); M-blocks first, then trivial lines.
        self.WB = [(m, 0) for m in self.M] + [(0, t) for t in range(e)]
        self.wb_index = {B: i for i, B in enumerate(self.WB)}
        # omega2 channels: (a; B1, B2), wb_index(B1) <= wb_index(B2).
        channels = []
        for a in self.E:
            for i1, B1 in enumerate(self.WB):
                for B2 in self.WB[i1:]:
                    r = B1[0] + B2[0] - a
                    if r < 0 or a < abs(B1[0] - B2[0]):
                        continue
                    if B1 == B2 and r % 2 == 0:
                        continue
                    channels.append((a, B1, B2))
        channels.sort(key=lambda ch: (ch[0], self.wb_index[ch[1]],
                                      self.wb_index[ch[2]]))
        self.channels = channels
        self.channel_index = {ch: i for i, ch in enumerate(channels)}
        self.n_omega2 = len(channels)
        self.mixed_index = [i for i, ch in enumerate(channels)
                            if ch[1][0] == 0 or ch[2][0] == 0]
        # S parameters: block scalars s_m, then symmetric S_11 entries.
        self.s_index = {m: self.n_omega2 + k for k, m in enumerate(self.M)}
        base = self.n_omega2 + len(self.M)
        self.stt_index = {}
        k = 0
        for t in range(e):
            for u in range(t, e):
                self.stt_index[(t, u)] = base + k
                k += 1
        self.n_s = len(self.M) + k
        self.n_params = self.n_omega2 + self.n_s
        # channels touching (a, W-block)
        self.ch_from = {}
        for idx, (a, B1, B2) in enumerate(channels):
            r = B1[0] + B2[0] - a
            self.ch_from.setdefault((a, B1), []).append((idx, B2, r, False))
            if B2 != B1:
                self.ch_from.setdefault((a, B2), []).append((idx, B1, r, True))
        self._bgw_cache = {}
        self._nt_cache = {}

    # omega2 value on (x=(a,i), w=(B1,j), w'=(B2,l)) as an affine form.
    def omega2(self, a, i, B1, j, B2, l):
        md = self.md
        if self.wb_index[B1] > self.wb_index[B2]:
            return aff_scale(self.omega2(a, i, B2, l, B1, j), -1)
        idx = self.channel_index.get((a, B1, B2))
        if idx is None:
            return AFF_ZERO
        r = B1[0] + B2[0] - a
        o = j + l - r
        if o + i != 2 * a:
            return AFF_ZERO
        val = md.transv(B1[0], j, B2[0], l, r) * Q((-1) ** o * comb(2 * a, o))
        return aff_param(idx, val) if val else AFF_ZERO

    # Bracket [x, w], x a g0 basis key (a, i), w = (Bkey, kw).
    # Returns a BV.  Uses the B^{-1} block formulas; the trivial-W
    # component is returned as the covector wtc (component itself is
    # S_11^{-1} . wtc).
    def bracket_g0_w(self, x, w):
        key = (x, w)
        hit = self._bgw_cache.get(key)
        if hit is not None:
            return hit
        md = self.md
        (a, i), (Bw, kw) = x, w
        mw = Bw[0]
        v_s = {}    # t -> Q (const)
        v_n = {}    # (b, l) -> Q (const)
        v_w = {}    # (Bd, l) -> affine, Bd an M-block of W
        wtc = {}    # trivial copy t -> affine
        if mw > 1:
            b = mw - a + 1
            if b in self.M:
                l = 2 * mw - kw - i + 1
                if 0 <= l <= 2 * b:
                    br = md.bracket_g0(a, i, b, l)
                    if br and br[0] == mw and br[1] == 2 * mw - kw:
                        val = -br[2] * md.beta(mw, br[1], kw)
                        if val:
                            v_n[(b, l)] = val
            if a == mw:
                t = 2 * mw - kw - i + 1
                if 0 <= t <= 2:
                    br = md.bracket_g0(a, i, 1, t)
                    if br and br[0] == mw and br[1] == 2 * mw - kw:
                        val = -br[2] * md.beta(mw, br[1], kw)
                        if val:
                            v_s[t] = val
        for idx, Bd, r, swapped in self.ch_from.get((a, Bw), ()):  # noqa: B007
            l = 2 * a - i - kw + r
            if not (0 <= l <= 2 * Bd[0]):
                continue
            val = self.omega2(a, i, Bw, kw, Bd, l)
            if aff_is_zero(val):
                continue
            if Bd[0] > 1:
                v_w[(Bd, l)] = val
            else:
                wtc[Bd[1]] = val
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
                u[('w', (bb, 0), q)] = aff_const(val * Q((-1) ** q,
                                                         comb(2 * bb, q)))
        blocks_w = {Bd for (Bd, _l) in v_w} | {(bb, 0) for bb in vn_by_block}
        for Bk in blocks_w:
            m = Bk[0]
            rhs = {}
            for (Bd, l), aval in v_w.items():
                if Bd == Bk:
                    rhs[l] = aval
            if m in vn_by_block:
                sp = self.s_index[m]
                for l, val in vn_by_block[m].items():
                    term = (ZERO, {sp: -val})
                    rhs[l] = aff_add(rhs[l], term) if l in rhs else term
            for l, aval in rhs.items():
                q = 2 * m - l
                k2 = ('g', m, q)
                u[k2] = aff_add(u.get(k2, AFF_ZERO),
                                aff_scale(aval, Q((-1) ** q, comb(2 * m, q))))
        res = BV(vec=u, wtc=wtc, delta=[]).pruned()
        self._bgw_cache[key] = res
        return res

    # n-components of [x, e_t] (x g0 key, t a trivial copy), as
    # {(m, i): affine}.  [x, e_t] is supported on n (checked).
    def n_part_triv(self, x, t):
        key = (x, t)
        hit = self._nt_cache.get(key)
        if hit is not None:
            return hit
        bv = self.bracket_g0_w(x, ((0, t), 0))
        assert not bv.wtc and not bv.delta
        nd = {}
        for k, v in bv.vec.items():
            assert k[0] == 'g' and k[1] in self.M, (x, t, k)
            nd[(k[1], k[2])] = v
        self._nt_cache[key] = nd
        return nd

    # Bracket [x, U] for x a g0 basis key and U a BV coming from a
    # single bracket_g0_w (so U.delta is empty).  The trivial-W part
    # of U (S_11^{-1} . U.wtc) contributes a Delta term.
    def bracket_g0_d(self, x, U):
        assert not U.delta
        md = self.md
        out = BV()
        for key, alpha in U.vec.items():
            if key[0] == 'g':
                br = md.bracket_g0(x[0], x[1], key[1], key[2])
                if br:
                    k2 = ('g', br[0], br[1])
                    out.vec[k2] = aff_add(out.vec.get(k2, AFF_ZERO),
                                          aff_scale(alpha, br[2]))
            else:
                if not aff_is_const(alpha):
                    raise ArithmeticError(
                        "non-constant W coefficient in bracket_g0_d")
                c0 = alpha[0]
                if c0:
                    bw = self.bracket_g0_w(x, (key[1], key[2]))
                    out = bv_add(out, bv_scale(bw, c0))
        if U.wtc:
            nd = {t: self.n_part_triv(x, t) for t in range(self.e)}
            out.delta.append((dict(U.wtc), nd))
        return out.pruned()

    # Jacobiator J(x, y, w) as a BV.
    def jacobi(self, x, y, w):
        t1 = self.bracket_g0_d(x, self.bracket_g0_w(y, w))
        t2 = self.bracket_g0_d(y, self.bracket_g0_w(x, w))
        out = bv_add(t1, bv_scale(t2, -1))
        br = self.md.bracket_g0(x[0], x[1], y[0], y[1])
        if br:
            t3 = self.bracket_g0_w((br[0], br[1]), w)
            out = bv_add(out, bv_scale(t3, -br[2]))
        return out.pruned()

    # F = B(J, w'), w' = (Bd, l).  Affine in the affine sectors;
    # raises NonAffine if a Delta term survives the pairing (this
    # happens exactly in the diagonal sectors {a,b} = {c,d}).
    def pair_w(self, J, wp):
        md = self.md
        Bd, l = wp
        if Bd[0] == 0:
            # S_11 . (S_11^{-1} . wtc) = wtc: exact cancellation.
            return J.wtc.get(Bd[1], AFF_ZERO)
        m = Bd[0]
        total = AFF_ZERO
        for key, val in J.vec.items():
            if key[0] == 'g' and key[1] == m:
                bv_ = md.beta(m, key[2], l)
                if bv_:
                    total = aff_add(total, aff_scale(val, bv_))
            elif key[0] == 'w' and key[1] == Bd:
                if not aff_is_const(val):
                    raise ArithmeticError("non-constant J_W in pair_w")
                bv_ = md.beta(m, key[2], l)
                if bv_ and val[0]:
                    total = aff_add(total,
                                    (ZERO, {self.s_index[m]: val[0] * bv_}))
        for cov, nd in J.delta:
            a_nonzero = False
            for ndvec in nd.values():
                s = AFF_ZERO
                for (mm, ii), aval in ndvec.items():
                    if mm == m:
                        bv_ = md.beta(m, ii, l)
                        if bv_:
                            s = aff_add(s, aff_scale(aval, bv_))
                if not aff_is_zero(s):
                    a_nonzero = True
                    break
            if not a_nonzero:
                continue
            if all(aff_is_zero(cov.get(u, AFF_ZERO)) for u in range(self.e)):
                continue
            raise NonAffine(
                f"Delta term survives pairing against {(Bd, l)}")
        return total

    # B(J, z) for z a g0 basis key (Delta is n-supported and wtc is
    # W_1-supported; both pair trivially with g0).
    def pair_g0(self, J, z):
        md = self.md
        m, l = z
        total = AFF_ZERO
        if m == 1:
            for key, val in J.vec.items():
                if key[0] == 'g' and key[1] == 1:
                    bv_ = md.beta(1, key[2], l)
                    if bv_:
                        total = aff_add(total, aff_scale(val, bv_))
        else:
            for key, val in J.vec.items():
                if key[0] == 'w' and key[1] == (m, 0):
                    bv_ = md.beta(m, key[2], l)
                    if bv_:
                        total = aff_add(total, aff_scale(val, bv_))
        return total


def is_diagonal_sector(cp: Completion, a, b, Bc, Bd):
    """Sectors in which F can be genuinely quadratic at e >= 1."""
    return (cp.e >= 1 and Bc[0] in cp.M and Bd[0] in cp.M
            and sorted([a, b]) == sorted([Bc[0], Bd[0]]))


# ---------------------------------------------------------------------------
# Sector extraction of the Jacobi channel components (as e = 0 stage)
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
    v = list(vec)
    for piv, row in basis:
        if v[piv]:
            f = v[piv]
            v = [x - f * y for x, y in zip(v, row)]
    return v


def solve_square_affine(mat, rhs):
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


def extract_sector(cp: Completion, a, b, Bc, Bd, rng):
    """Return (Js, tuples, f_affines) for one affine sector.
    Bc, Bd are W block keys; tuples are weight indices (i, j, k, l)."""
    md = cp.md
    c, d = Bc[0], Bd[0]
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
        raise ArithmeticError(f"sector {(a, b, Bc, Bd)}: evaluation rank "
                              f"{len(chosen)} < {nch} channels")
    fvals = []
    for (i, j, k, l) in chosen:
        J = cp.jacobi((a, i), (b, j), (Bc, k))
        fvals.append(cp.pair_w(J, (Bd, l)))
    f = solve_square_affine(chosen_vals, fvals)
    return Js, chosen, f


# ---------------------------------------------------------------------------
# Exact linear algebra over Q and modular rank (as e = 0 stage)
# ---------------------------------------------------------------------------

def solve_subsystem(rows_data, idxs, n_params):
    mat = []
    for i in idxs:
        coeffs, const = rows_data[i]
        row = [coeffs.get(j, ZERO) for j in range(n_params)] + [const]
        mat.append(row)
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
    for i in range(n):
        if all(not aug[i][col] for col in range(n_params)) and aug[i][n_params]:
            lam = aug[i][n_params + 1:]
            return {"consistent": False, "rank": coeff_rank, "farkas_lambda": lam,
                    "farkas_rows": list(idxs)}
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
# Checks (generalised from the e = 0 stage)
# ---------------------------------------------------------------------------

def run_checks(md: Model, cp: Completion, repo: Path):
    checks = {}
    checks["e"] = cp.e
    checks["omega2_channel_count"] = cp.n_omega2
    checks["mixed_channel_count"] = len(cp.mixed_index)
    checks["s_param_count"] = cp.n_s
    checks["total_unknowns"] = cp.n_params
    checks["pr7_total_with_omega3"] = cp.n_params + 68
    total_sector = 0
    affine_sector = 0
    diag_sector = 0
    n_aff_sec = 0
    n_diag_sec = 0
    for ai, a in enumerate(cp.E):
        for b in cp.E[ai:]:
            for Bc in cp.WB:
                for Bd in cp.WB:
                    nch = len(sector_channels(a, b, Bc[0], Bd[0]))
                    total_sector += nch
                    if is_diagonal_sector(cp, a, b, Bc, Bd):
                        diag_sector += nch
                        n_diag_sec += 1 if nch else 0
                    else:
                        affine_sector += nch
                        n_aff_sec += 1 if nch else 0
    checks["jacobi_channel_components_total"] = total_sector
    checks["jacobi_channel_components_affine"] = affine_sector
    checks["jacobi_channel_components_diagonal_quadratic"] = diag_sector
    checks["affine_sector_count"] = n_aff_sec
    checks["diagonal_sector_count"] = n_diag_sec

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

    from perfectjet.asterion_boundary import PrincipalReesFamily
    fam = PrincipalReesFamily(md.basis)
    idx = md.basis.label_index
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
        for term in (br_lin(x, br_vec(y, z)), br_lin(y, br_vec(z, x)),
                     br_lin(z, br_vec(x, y))):
            for k, v in term.items():
                tot[k] = tot.get(k, ZERO) + v
        if any(tot.values()):
            bad += 1
    checks["g0_jacobi_failures"] = bad

    def chan_eval(ch, i, j, l):
        a, B1, B2 = ch
        r = B1[0] + B2[0] - a
        o = j + l - r
        if o + i != 2 * a:
            return ZERO
        return md.transv(B1[0], j, B2[0], l, r) * Q((-1) ** o * comb(2 * a, o))

    def act(block_spin, key_idx):
        if block_spin == 0:
            return None
        return md.bracket_g0(1, 0, block_spin, key_idx)

    bad = 0
    tested = 0
    for ch in cp.channels:
        a, B1, B2 = ch
        for _ in range(6):
            i = rng.randrange(2 * a + 1)
            j = rng.randrange(2 * B1[0] + 1)
            l = rng.randrange(2 * B2[0] + 1)
            if chan_eval(ch, i, j, l) == 0 and rng.random() < 0.7:
                continue
            tested += 1
            tot = ZERO
            ra = act(a, i)
            if ra:
                tot += ra[2] * chan_eval(ch, ra[1], j, l)
            rb = act(B1[0], j)
            if rb:
                tot += rb[2] * chan_eval(ch, i, rb[1], l)
            rd = act(B2[0], l)
            if rd:
                tot += rd[2] * chan_eval(ch, i, j, rd[1])
            if tot:
                bad += 1
    checks["omega2_channel_invariance_failures"] = bad
    checks["omega2_channel_invariance_tests"] = tested

    bad = 0
    gkeys = [(m, j) for m in cp.E for j in range(2 * m + 1)]
    wkeys = [(B, j) for B in cp.WB for j in range(2 * B[0] + 1)]
    for _ in range(1200):
        x, y, w = rng.choice(gkeys), rng.choice(gkeys), rng.choice(wkeys)
        J = cp.jacobi(x, y, w)
        if not J.vec and not J.wtc and not J.delta:
            continue
        for z in gkeys:
            val = cp.pair_g0(J, z)
            if val[0] or val[1]:
                bad += 1
                break
    checks["paired_g0_nonzero_instances"] = bad

    # [x, e_t] is supported on n (used by the Delta analysis).
    bad = 0
    for t in range(cp.e):
        for x in gkeys:
            nd = cp.n_part_triv(x, t)
            bv = cp.bracket_g0_w(x, ((0, t), 0))
            if bv.wtc or bv.delta:
                bad += 1
            for k in bv.vec:
                if k[0] != 'g' or k[1] not in cp.M:
                    bad += 1
    checks["triv_bracket_support_failures"] = bad
    return checks


# ---------------------------------------------------------------------------
# Numeric model: exact rational evaluation at concrete parameters,
# with brackets verified against their defining pairings.
# ---------------------------------------------------------------------------

def mat_inv_q(A):
    n = len(A)
    rows = [list(A[i]) + [ONE if j == i else ZERO for j in range(n)]
            for i in range(n)]
    for col in range(n):
        piv = next((r for r in range(col, n) if rows[r][col]), None)
        if piv is None:
            raise ArithmeticError("singular matrix")
        rows[col], rows[piv] = rows[piv], rows[col]
        inv = ONE / rows[col][col]
        rows[col] = [x * inv for x in rows[col]]
        for r in range(n):
            if r != col and rows[r][col]:
                f = rows[r][col]
                rows[r] = [x - f * y for x, y in zip(rows[r], rows[col])]
    return [row[n:] for row in rows]


class NumericModel:
    def __init__(self, md: Model, cp: Completion, params):
        self.md = md
        self.cp = cp
        self.params = params
        e = cp.e
        if e:
            S = [[params[cp.stt_index[(min(t, u), max(t, u))]]
                  for u in range(e)] for t in range(e)]
            self.Sinv = mat_inv_q(S)
        else:
            self.Sinv = []

    def B_form(self, u, v):
        md = self.md
        cp = self.cp
        params = self.params
        tot = ZERO
        for k1, c1 in u.items():
            for k2, c2 in v.items():
                val = None
                if k1[0] == 'g' and k2[0] == 'g':
                    if k1[1] == 1 and k2[1] == 1:
                        val = md.beta(1, k1[2], k2[2])
                elif k1[0] == 'g' and k2[0] == 'w':
                    if k2[1][0] > 1 and k1[1] == k2[1][0]:
                        val = md.beta(k1[1], k1[2], k2[2])
                elif k1[0] == 'w' and k2[0] == 'g':
                    if k1[1][0] > 1 and k1[1][0] == k2[1]:
                        val = md.beta(k1[1][0], k2[2], k1[2])
                elif k1[0] == 'w' and k2[0] == 'w':
                    if k1[1] == k2[1] and k1[1][0] > 1:
                        m = k1[1][0]
                        val = (params[cp.s_index[m]]
                               * md.beta(m, k1[2], k2[2]))
                    elif k1[1][0] == 0 and k2[1][0] == 0:
                        t, uu = k1[1][1], k2[1][1]
                        val = self.params[cp.stt_index[(min(t, uu), max(t, uu))]]
                if val:
                    tot += c1 * c2 * val
        return tot

    def omega_val(self, x, y, z):
        md = self.md
        cp = self.cp
        args = [x, y, z]
        order = sorted(range(3), key=lambda t: (0 if args[t][0] == 'g' else 1))
        inv = sum(1 for s in range(3) for t in range(s + 1, 3)
                  if order[s] > order[t])
        sgn = -1 if inv % 2 else 1
        a1, a2, a3 = (args[order[0]], args[order[1]], args[order[2]])
        if a3[0] == 'g':
            br = md.bracket_g0(a1[1], a1[2], a2[1], a2[2])
            if not br or br[0] != 1 or a3[1] != 1:
                return ZERO
            return sgn * br[2] * md.beta(1, br[1], a3[2])
        if a2[0] == 'g' and a3[0] == 'w':
            if a3[1][0] == 0:
                return ZERO
            br = md.bracket_g0(a1[1], a1[2], a2[1], a2[2])
            if not br or br[0] != a3[1][0]:
                return ZERO
            return sgn * br[2] * md.beta(br[0], br[1], a3[2])
        if a2[0] == 'w':
            val = cp.omega2(a1[1], a1[2], a2[1], a2[2], a3[1], a3[2])
            return sgn * aff_eval(val, self.params)
        return ZERO

    def bgw(self, x, w, verify=True):
        cp = self.cp
        bv = cp.bracket_g0_w(x, w)
        vec = {k: aff_eval(v, self.params) for k, v in bv.vec.items()}
        if cp.e:
            wtc_eval = [aff_eval(bv.wtc.get(t, AFF_ZERO), self.params)
                        for t in range(cp.e)]
            for t in range(cp.e):
                val = sum(self.Sinv[t][u] * wtc_eval[u] for u in range(cp.e))
                if val:
                    vec[('w', (0, t), 0)] = val
        vec = {k: v for k, v in vec.items() if v}
        if verify:
            basis = [(('g', m, i)) for m in cp.E for i in range(2 * m + 1)] + \
                    [(('w', B, i)) for B in cp.WB for i in range(2 * B[0] + 1)]
            xk = ('g', x[0], x[1])
            wk = ('w', w[0], w[1])
            for zk in basis:
                lhs = self.B_form(vec, {zk: ONE})
                rhs = self.omega_val(xk, wk, zk)
                if lhs != rhs:
                    raise ArithmeticError(
                        f"pairing failure {x} {w} {zk}: {lhs} != {rhs}")
        return vec

    def bgd(self, x, vec, verify=True):
        md = self.md
        out = {}
        for key, c in vec.items():
            if key[0] == 'g':
                br = md.bracket_g0(x[0], x[1], key[1], key[2])
                if br:
                    k2 = ('g', br[0], br[1])
                    out[k2] = out.get(k2, ZERO) + c * br[2]
            else:
                bw = self.bgw(x, (key[1], key[2]), verify=verify)
                for k2, v in bw.items():
                    out[k2] = out.get(k2, ZERO) + c * v
        return {k: v for k, v in out.items() if v}

    def F(self, x, y, w, wp, verify=True):
        md = self.md
        t1 = self.bgd(x, self.bgw(y, w, verify=verify), verify=verify)
        t2 = self.bgd(y, self.bgw(x, w, verify=verify), verify=verify)
        J = dict(t1)
        for k, v in t2.items():
            J[k] = J.get(k, ZERO) - v
        br = md.bracket_g0(x[0], x[1], y[0], y[1])
        if br:
            t3 = self.bgw((br[0], br[1]), w, verify=verify)
            for k, v in t3.items():
                J[k] = J.get(k, ZERO) - br[2] * v
        J = {k: v for k, v in J.items() if v}
        return self.B_form(J, {('w', wp[0], wp[1]): ONE})


def numeric_cross_check(md: Model, cp: Completion):
    """Random rational parameters; numeric F (pairing-verified
    brackets, S_11 inverted exactly) vs the affine machinery, on
    tuples in affine (non-diagonal) sectors."""
    rng = random.Random(4242)
    params = [Q(rng.randrange(-5, 6), rng.choice((1, 1, 2, 3)))
              for _ in range(cp.n_params)]
    # the numeric model inverts S_11 exactly; resample its diagonal
    # until it is invertible (a random draw can be singular, e.g. 0).
    for _try in range(50):
        try:
            nm = NumericModel(md, cp, params)
            break
        except ArithmeticError:
            for t in range(cp.e):
                params[cp.stt_index[(t, t)]] += Q(3, 2)
    else:
        raise ArithmeticError("could not draw an invertible S_11")
    gkeys = [(m, j) for m in cp.E for j in range(2 * m + 1)]
    wkeys = [(B, j) for B in cp.WB for j in range(2 * B[0] + 1)]
    tested = 0
    failures = 0
    skipped_diag = 0
    attempts = 0
    while tested < 24 and attempts < 400:
        attempts += 1
        x, y, w, wp = (rng.choice(gkeys), rng.choice(gkeys),
                       rng.choice(wkeys), rng.choice(wkeys))
        if is_diagonal_sector(cp, x[0], y[0], w[0], wp[0]):
            skipped_diag += 1
            continue
        numeric = nm.F(x, y, w, wp, verify=True)
        aff = cp.pair_w(cp.jacobi(x, y, w), wp)
        mine = aff_eval(aff, params)
        tested += 1
        if numeric != mine:
            failures += 1
    return {"tuples": tested, "failures": failures,
            "diagonal_tuples_skipped": skipped_diag}


def quadratic_evidence(md: Model, cp: Completion):
    """Evidence that the diagonal sectors are genuinely quadratic at
    e >= 1: in sector (7,7,7,7), with all parameters zero except
    S_11 = I and one mixed channel p (7; V_7, trivial), the numeric F
    (full model, S_11 inverted exactly) has nonzero second difference
    in p for some weight tuple -- i.e. a p^2 term (Delta) is present.
    Returns a dict describing the search outcome."""
    if cp.e == 0:
        return {"applicable": False}
    base = [ZERO] * cp.n_params
    for t in range(cp.e):
        base[cp.stt_index[(t, t)]] = ONE
    cand_channels = [i for i in cp.mixed_index if cp.channels[i][0] == 7]
    rng = random.Random(31337)
    tuples = []
    for i in range(15):
        for j in range(15):
            for k in range(15):
                l = 28 - i - j - k
                if 0 <= l <= 14:
                    tuples.append((i, j, k, l))
    rng.shuffle(tuples)
    tried = 0
    for (i, j, k, l) in tuples[:40]:
        x, y, w, wp = (7, i), (7, j), ((7, 0), k), ((7, 0), l)
        for pidx in cand_channels:
            vals = []
            for pv in (0, 1, 2):
                params = list(base)
                params[pidx] = Q(pv)
                nm = NumericModel(md, cp, params)
                vals.append(nm.F(x, y, w, wp, verify=False))
            tried += 1
            second = vals[2] - 2 * vals[1] + vals[0]
            if second != 0:
                return {"applicable": True, "found": True,
                        "sector": [7, 7, 7, 7],
                        "tuple": [i, j, k, l],
                        "channel": [cp.channels[pidx][0],
                                    list(cp.channels[pidx][1]),
                                    list(cp.channels[pidx][2])],
                        "F_at_p0_p1_p2": [str(v) for v in vals],
                        "second_difference": str(second),
                        "trials": tried}
    return {"applicable": True, "found": False, "trials": tried}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

EXPECTED = {
    0: {"omega2": 162, "mixed": 0, "s": 7, "unknowns": 169,
        "total_channels": 22688},
    1: {"omega2": 169, "mixed": 7, "s": 8, "unknowns": 177,
        "total_channels": 23012},
    2: {"omega2": 176, "mixed": 14, "s": 10, "unknowns": 186,
        "total_channels": 23336},
}


def frac_str(x):
    return str(x)


def sector_key(a, b, Bc, Bd):
    return [a, b, list(Bc), list(Bd)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--e", type=int, required=True, choices=(0, 1, 2))
    ap.add_argument("--repo", type=Path,
                    default=Path(__file__).resolve().parents[1])  # repository root
    ap.add_argument("--out", type=Path, default=Path(__file__).resolve().parent)
    ap.add_argument("--sectors-only", action="store_true",
                    help="extract and write the system, skip the solve")
    args = ap.parse_args()
    e = args.e
    out_dir = args.out
    out_dir.mkdir(parents=True, exist_ok=True)
    prefix = f"asterion_e{e}"
    t_start = time.time()
    log(f"=== e = {e} (dimension {493 + e}) ===")
    log(f"repo: {args.repo}")
    md = Model(args.repo)
    cp = Completion(md, e)
    exp = EXPECTED[e]
    log(f"channels: omega2={cp.n_omega2} (mixed {len(cp.mixed_index)}), "
        f"S={cp.n_s}, unknowns={cp.n_params}")
    assert cp.n_omega2 == exp["omega2"], cp.n_omega2
    assert len(cp.mixed_index) == exp["mixed"]
    assert cp.n_s == exp["s"]
    assert cp.n_params == exp["unknowns"]

    log("stage: checks")
    checks = run_checks(md, cp, args.repo)
    for k, v in checks.items():
        log(f"  check {k}: {v}")
    assert checks["jacobi_channel_components_total"] == exp["total_channels"]
    assert checks["beta_invariance_failures"] == 0
    assert checks["repo_bracket_mismatches"] == 0
    assert checks["g0_jacobi_failures"] == 0
    assert checks["omega2_channel_invariance_failures"] == 0
    assert checks["paired_g0_nonzero_instances"] == 0
    assert checks["triv_bracket_support_failures"] == 0

    log("stage: numeric cross-check of F (pairing-verified brackets)")
    ncc = numeric_cross_check(md, cp)
    log(f"  numeric cross-check: {ncc}")
    assert ncc["failures"] == 0 and ncc["tuples"] == 24

    log("stage: quadratic evidence in diagonal sector (7,7,7,7)")
    qev = quadratic_evidence(md, cp)
    log(f"  quadratic evidence: {qev}")

    log("stage: sector extraction (affine sectors only)")
    t_asm = time.time()
    rng = random.Random(20261024 + e)
    rows = []
    sectors_meta = []
    bad_sectors = []
    E = cp.E
    nsec_total = 0
    for ai, a in enumerate(E):
        for b in E[ai:]:
            for Bc in cp.WB:
                for Bd in cp.WB:
                    Js = sector_channels(a, b, Bc[0], Bd[0])
                    if not Js:
                        continue
                    nsec_total += 1
                    if is_diagonal_sector(cp, a, b, Bc, Bd):
                        bad_sectors.append({
                            "sector": sector_key(a, b, Bc, Bd),
                            "channels_J": Js})
                        continue
                    Js2, chosen, f = extract_sector(cp, a, b, Bc, Bd, rng)
                    assert Js2 == Js
                    sid = len(sectors_meta)
                    sectors_meta.append({
                        "sector": sector_key(a, b, Bc, Bd),
                        "channels_J": Js,
                        "tuples": [list(t) for t in chosen]})
                    for J, aff in zip(Js, f):
                        rows.append((sid, J, aff[1], aff[0]))
                    if nsec_total % 250 == 0:
                        log(f"  ... {nsec_total} sectors, {len(rows)} rows, "
                            f"{time.time() - t_asm:.0f}s")
    log(f"  assembled {len(rows)} affine equations "
        f"({len(sectors_meta)} affine sectors; {len(bad_sectors)} diagonal "
        f"sectors deferred) in {time.time() - t_asm:.1f}s")
    rows_data = [(coeffs, const) for (_sid, _J, coeffs, const) in rows]
    n_const_nonzero = sum(1 for coeffs, const in rows_data
                          if not coeffs and const)
    n_zero_rows = sum(1 for coeffs, const in rows_data
                      if not coeffs and not const)
    log(f"  affine rows: {n_zero_rows} identically zero, "
        f"{n_const_nonzero} constant-only nonzero")

    sys_path = out_dir / f"{prefix}_system.json"
    with open(sys_path, "w", encoding="utf-8") as fh:
        for sid, J, coeffs, const in rows:
            fh.write(json.dumps({
                "sector": sid, "J": J,
                "coeffs": {str(k): frac_str(v) for k, v in sorted(coeffs.items())},
                "const": frac_str(const)}) + "\n")
    log(f"  system written to {sys_path.name}")

    result = None
    rank_mod = {}
    if not args.sectors_only:
        log("stage: modular rank pass")
        pivots_mod = {}
        for p in (1000003, 999983):
            r, cons, piv = modular_rank(rows_data, cp.n_params, p)
            rank_mod[p] = (r, cons)
            pivots_mod[p] = piv
            log(f"  mod {p}: rank={r}, consistent={cons}")
        subsystem = list(pivots_mod[1000003])

        log("stage: exact solve over Q (subsystem + verification loop)")
        for _attempt in range(40):
            sol = solve_subsystem(rows_data, subsystem, cp.n_params)
            if not sol["consistent"]:
                lam = sol["farkas_lambda"]
                sub_rows = sol["farkas_rows"]
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
                result = {"outcome": "inconsistent",
                          "rank_coefficients": sol["rank"],
                          "farkas": {"rows": sub_rows,
                                     "lambda": [frac_str(x) for x in lam],
                                     "constant_sum": frac_str(const_sum)}}
                log(f"  INCONSISTENT: Farkas certificate on {len(sub_rows)} "
                    f"rows, constant sum {const_sum}")
                break
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
                          "null_basis": [[frac_str(x) for x in vec]
                                         for vec in null_basis]}
                log(f"  CONSISTENT: rank={sol['rank']}, solution affine "
                    f"dimension {len(null_basis)} (verified against all "
                    f"{len(rows_data)} rows)")
                break
            subsystem.append(failing)
            log(f"  row {failing} not satisfied by subsystem solution; "
                f"adding it (subsystem size {len(subsystem)})")
        if result is None:
            raise ArithmeticError("solve loop did not terminate")

    results = {
        "schema": "asterion-linear-e12/1",
        "e": e,
        "dimension": 493 + e,
        "repo": str(args.repo),
        "checks": checks,
        "numeric_cross_check": ncc,
        "quadratic_evidence_diagonal_sector": qev,
        "counts": {
            "unknowns": cp.n_params,
            "omega2_channels": cp.n_omega2,
            "mixed_channels": len(cp.mixed_index),
            "s_params": cp.n_s,
            "omega3_channels": 68,
            "pr7_total": cp.n_params + 68,
            "channel_equations_total": checks[
                "jacobi_channel_components_total"],
            "channel_equations_affine": len(rows_data),
            "channel_equations_diagonal_quadratic":
                checks["jacobi_channel_components_diagonal_quadratic"],
            "affine_rows_zero": n_zero_rows,
            "affine_rows_constant_nonzero": n_const_nonzero,
        },
        "modular_ranks": {str(p): {"rank": r, "consistent": c}
                          for p, (r, c) in rank_mod.items()},
        "system": {"equations": len(rows_data), "unknowns": cp.n_params,
                   "omega2_channels": [[ch[0], list(ch[1]), list(ch[2])]
                                       for ch in cp.channels],
                   "s_params": {str(m): cp.s_index[m] for m in cp.M},
                   "stt_params": {f"{t},{u}": idx
                                  for (t, u), idx in cp.stt_index.items()},
                   "sectors": sectors_meta,
                   "diagonal_sectors": bad_sectors},
        "result": result,
        "timing_seconds": round(time.time() - t_start, 1),
    }
    if result is not None and result["outcome"] == "consistent":
        dim = result["solution_dimension"]
        results["reduced_remaining"] = {
            "free_in_omega2_S_after_linear_stage": dim,
            "omega3_parameters": 68,
            "total_free_for_quadratic_stage": dim + 68,
            "deferred_diagonal_channel_equations": checks[
                "jacobi_channel_components_diagonal_quadratic"],
            "note": "Remaining: the 49 diagonal-sector (g0,g0,W)-against-W "
                    "channel equations (quadratic in the mixed channels, "
                    "coefficients in Q(S_11)), plus the (g0,W,W) and "
                    "(W,W,W) Jacobi types involving omega3."}
    res_path = out_dir / f"{prefix}_results.json"
    res_path.write_text(json.dumps(results, indent=1), encoding="utf-8")
    log(f"results written to {res_path.name}; total {time.time() - t_start:.1f}s")
    (out_dir / f"{prefix}_run.log").write_text(
        "\n".join(LOG_LINES) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
