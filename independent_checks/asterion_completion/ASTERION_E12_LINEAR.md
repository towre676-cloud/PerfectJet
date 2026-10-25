# Asterion 494 and 495: the affine-linear stage at e = 1 and e = 2 is consistent — dimensions 494 and 495 are NOT excluded by the linear programme

Second stage of closing the Asterion 493–496 gap (programme item
AST-P036), following the $e = 0$ stage
(`ASTERION_493_EXCLUDED.md`, which excluded dimension 493) and
the normal-form reduction of PerfectJet PR #7
(`INTERVAL_493_496.md`, §5, in this same directory). Committed here on
the branch `muse/asterion-e12-linear`, as new files under
`independent_checks/asterion_completion/`, for review by pull request
against main; no existing repository file is changed. Everything
below is over **Q**, in exact rational arithmetic. The headline is
different from $e = 0$: at both $e = 1$ (dimension 494) and $e = 2$
(dimension 495) the affine-linear $(\mathfrak{g}_0, \mathfrak{g}_0, W)$
Jacobi system is **consistent**, so the linear stage excludes
nothing further. Combined with stage one, the completion interval
after the linear programme is exactly $\{494, 495, 496\}$, and what
remains for 494 and 495 is genuinely quadratic (described precisely
below). Getting this right requires one correction to PR #7 §5,
which asserted the system is affine in $(\omega_2, S)$ verbatim at
$e = 1, 2$: that is true outside 49 exceptional "diagonal" sectors
and false inside them, and — the decisive computed fact — **all 434
of the $e = 0$ constant-only obstructing rows lie in diagonal
sectors**, which is why 493 fell to the linear stage and 494/495 do
not.

## Results

At $e = 1$ ($W \cong \mathfrak{n} \oplus \mathbf{1}$, 177 unknowns:
$\omega_2$ has 169 singlet channels, 7 of them "mixed" channels
involving the trivial $W$ slot, and $S$ has 8 parameters, the 7 block
scalars $s_m$ plus the single entry $\sigma$ of $S$ on the trivial
line): the full $(\mathfrak{g}_0,\mathfrak{g}_0,W)$-against-$W$
channel space has dimension 23,012 (independently confirmed by
PR #7's Part B character count). Of these, 21,807 channel equations
in 1,915 sectors are affine in $(\omega_2, S)$; the remaining 1,205,
in the 49 diagonal sectors, are quadratic and are deferred (below).
The affine system is **consistent**: its coefficient rank is 165
(modulo both primes 1000003 and 999983, and exactly over **Q** by
RREF on the pivot subsystem), every one of the 21,807 equations is
homogeneous (constant term zero), and the solution set is the
12-dimensional linear subspace given explicitly in
`asterion_e1_results.json` (a basis of 12 null vectors, verified
against every stored row). At $e = 2$ ($W \cong \mathfrak{n} \oplus
\mathbf{1}^2$, 186 unknowns: $\omega_2$ has 176 channels, 14 mixed,
and $S$ has 10 parameters, 7 block scalars plus a general symmetric
$2 \times 2$ block $S_{11}$): the channel space has dimension 23,336
(again PR #7's count), of which 22,131 equations in 2,239 sectors are
affine and 1,205 in the same 49 diagonal sectors are deferred. The
affine system is again **consistent**, rank 170 (both primes, and
exactly over **Q**), all equations homogeneous, and the solution set
is an explicit 16-dimensional linear subspace. In both cases the
$S_{11}$ parameters occur in **no** affine equation at all — the
affine stage is entirely independent of $S_{11}$ — and the mixed
channels enter only through $16$ ($e=1$) resp. $32$ ($e=2$) nonzero
rows in trivial-involving sectors; the remaining 9,422 nonzero affine
rows (identical at $e = 1$ and $e = 2$) involve only the $e = 0$
parameters and are exactly the $e = 0$ system's non-diagonal rows.

## The $e \ge 1$ subtlety: where affinity fails, and why it matters

Write $B$ on $(\mathfrak{s}, \mathfrak{n}, W)$ in the normal form of
PR #7 §5. For $x \in \mathfrak{g}_0$, $w \in W$, the bracket $[x, w]$
is recovered from the covector $v(z) = \omega(x, w, z)$ through
$B^{-1}$. Its $\mathfrak{s}$- and $W_{\mathfrak{n}}$-components come
from the forced part of $\omega$ (constants), its
$\mathfrak{n}$-component is affine in $(\omega_2, S_{\mathfrak{n}})$
exactly as at $e = 0$, but its component on the trivial summands is
$u_{W,\mathbf{1}} = S_{11}^{-1}\, v_{W,\mathbf{1}}$, where
$v_{W,\mathbf{1}}(z_u) = \omega_2(x, w, z_u)$ is affine in the mixed
channels: **the inverse of the trivial block of $S$ enters**, and
with it, in the second bracket of the Jacobiator, products
$\Delta = \sum_t (S_{11}^{-1} v^{(y,w)})_t\, [x, e_t] - \sum_t
(S_{11}^{-1} v^{(x,w)})_t\, [y, e_t]$, where $e_t$ are the trivial
lines and $[x, e_t]$ is supported on the single
$\mathfrak{n}$-block $V_{a_x}$ and is affine in the mixed channels of
$x$ (both facts are checked in the code). Pairing against
$w' \in W_{\mathfrak{n}}$ of block $d$, $\Delta$ can survive only if
($a_y = c$ and $d = a_x$) or ($a_x = c$ and $d = a_y$), where $c$ is
the block of $w$ — i.e. only in sectors with
$\{a, b\} = \{c, d\}$ as multisets, $c, d \in M$: the 49 diagonal
sectors (7 with $c = d$ and $2 \times 21$ with $c \ne d$ in the two
orderings), carrying 1,205 channel equations at every $e$. Pairing
against a trivial $w'$ instead multiplies by $S_{11}$, which cancels
$S_{11}^{-1}$ exactly, so those components are affine in $\omega_2$
alone. In every non-diagonal sector $\Delta$ pairs to zero
identically; the implementation carries $\Delta$ symbolically and
its `pair_w` raises an error if a $\Delta$ term ever survives a
pairing outside a diagonal sector (in the diagonal sector
$(7,7,7,7)$ it does so on 435 of the 2,255 weight tuples, at both
$e = 1$ and $e = 2$). Inside the diagonal sectors the true equation
is $f_{\mathrm{aff}} + \Delta = 0$, where $f_{\mathrm{aff}}$ is
exactly the $e = 0$ row of that channel — constants and all — and
$\Delta$ is quadratic in the $7e$ mixed channels with coefficients
in $\mathbf{Q}(S_{11})$ (at $e = 1$, $\Delta = \sigma^{-1}$ times a
quadratic form in the 7 mixed channels; clearing $\sigma$ gives the
polynomial equation $\sigma f_{\mathrm{aff}} + \Delta_{\mathrm{num}}
= 0$).

That this is not a bookkeeping artefact is verified numerically in
the full model (exact $S_{11}^{-1}$, brackets checked against their
defining pairings): in sector $(7,7,7,7)$ at the weight tuple
$(12, 8, 6, 2)$, with all parameters zero except $S_{11} = I$ and the
single mixed channel $p = (7;\, V_7, \mathbf{1})$, the Jacobi
component is $F(p) = 2732730,\ 2459457,\ 1639638$ at
$p = 0, 1, 2$ — second difference $-546546 \ne 0$, so $F$ has a
genuine $p^2$ term, and the $p = 0$ value is the $e = 0$ constant
obstruction in that sector, now cancellable by the quadratic term.
(The same values occur at $e = 1$ and $e = 2$; recorded in both
results JSONs as `quadratic_evidence_diagonal_sector`.) Finally,
the reason stage one succeeded and this stage cannot: counting the
$e = 0$ system's 434 constant-only rows by sector (directly from
`../asterion_linear/asterion_linear_system.json.gz`) shows **every
one of them lies in a diagonal sector** — there are no constant-only
rows anywhere else — so no Farkas certificate of the $e = 0$ kind
exists at $e \ge 1$, and indeed every affine equation at
$e = 1, 2$ turns out homogeneous.

## The solution spaces

At $e = 1$ the 12 free directions of $(\omega_2, S)$ are: the two
channels $(7;\, V_{29}, V_{29})$ and $(11;\, V_{29}, V_{29})$, which
occur in no affine equation; two independent combinations supported
on the seven mixed channels $(a;\, V_a, \mathbf{1})$ (supports
$a \in \{7,11,13,17,19,23\}$ and $a \in \{7,11,13,17,19,29\}$); seven
directions, one for each $m \in M$, tying $s_m$ to a specific family
of unmixed channels (e.g. for $m = 7$: $s_7$ together with
$(1;7,7)$, $(7;7,13)$, $(11;7,17)$, $(13;7,19)$, $(17;7,23)$,
$(23;7,29)$); and $\sigma$ itself, which is unconstrained by the
affine system. At $e = 2$ the 16 directions are the analogous list:
the same two never-occurring channels, four mixed combinations (the
same two supports for each of the two trivial copies), the same
seven $s_m$ directions, and the three entries of $S_{11}$, all free.
The explicit bases (exact rational entries) are in the results
JSONs, and the verifier re-checks them against all 21,807 / 22,131
stored rows from disk.

## What remains: the reduced quadratic system

For dimension **494** ($e = 1$): after the linear stage,
$(\omega_2, S)$ ranges over the explicit 12-dimensional subspace
above; together with the 68 $\omega_3$ channels the quadratic stage
has **80 free parameters** (down from PR #7's 245). The remaining
$(\mathfrak{g}_0,\mathfrak{g}_0,W)$-against-$W$ conditions are the
**1,205 diagonal-sector channel equations**, quadratic in the mixed
channels (polynomial after clearing $\sigma$), restricted to that
subspace — heavily overdetermined, but genuinely quadratic, so no
rank or Farkas argument of the linear kind can settle them. Beyond
these, the $(\mathfrak{g}_0, W, W)$ and $(W, W, W)$ Jacobi types are
untouched; their ambient singlet-component counts at $e = 1$ are
45,623 and 14,834 (PR #7 Part B; upper bounds on the number of
independent scalar equations). A completion in dimension 494 exists
if and only if this combined quadratic system has a rational
solution with $S_{11}$ nondegenerate ($\sigma \ne 0$).

For dimension **495** ($e = 2$): the same statement with the
16-dimensional subspace, **84 free parameters** in the quadratic
stage (16 in $(\omega_2, S)$ plus 68 in $\omega_3$, down from 254),
the same 1,205 deferred diagonal equations (now quadratic in the 14
mixed channels, coefficients in $\mathbf{Q}(S_{11})$ with
$\det S_{11}$ as the clearing denominator), ambient counts 46,378
and 15,233 for the other two Jacobi types, and the side condition
$\det S_{11} \ne 0$.

## Verification (independent checks, all passing)

The generalised code was regression-tested against stage one before
the main runs: run at $e = 0$ it reproduces the stored
`asterion_linear_system.json.gz` **exactly** on 883 rows over 49
sectors (the 19 sectors containing the obstructing constants plus 30
random sectors), with the same parameter indexing. Inside each main
run: the $\mathfrak{g}_0$ bracket agrees with the repository's
`PrincipalReesFamily.basis_bracket(t = 0)` on 3,744 sampled pairs and
satisfies Jacobi on 1,500 random triples; $\beta_m$ is exactly
$\mathfrak{sl}_2$-invariant; every $\omega_2$ channel tensor is
annihilated by the raising operator (349 tests at $e = 1$, 338 at
$e = 2$); the $(\mathfrak{g}_0,\mathfrak{g}_0,W)$ Jacobi components
paired against $\mathfrak{g}_0$ vanish identically on 1,200 random
tuples; $[x, e_t]$ is verified to be supported on
$\mathfrak{n}$ for all $x$ and $t$; and the counts reproduce PR #7
Part B exactly (unknowns 177/186, totals with $\omega_3$ 245/254,
channel totals 23,012/23,336). The assembled $F$ values were
recomputed numerically at random rational parameters by the full
numeric model — every bracket $[x, w]$ checked against its defining
pairings $B([x,w], z) = \omega(x,w,z)$ for all $494$/$495$ basis
vectors $z$, with $S_{11}$ inverted exactly — on 24 tuples in
non-diagonal sectors, with zero failures at both $e$. Afterwards,
`verify_e12.py` (see `verify_e1_log.txt`, `verify_e2_log.txt`)
re-read the stored systems from disk and: re-verified the reported
solution spaces against **every** stored row; re-derived three
complete sectors by contraction under the
$\mathfrak{sl}_2$-invariant pairing summed over **all** weight
tuples of the sector — the 19-channel sector $(11,13,V_{11},V_{17})$
(12,003 tuples, channel Gram matrix exactly diagonal, all 19
components matching), a $d$-trivial sector $(1,7,V_7,\mathbf{1})$ and
a $c$-trivial sector $(1,13,\mathbf{1},V_{13})$; spot-checked the
residual identity $F = \sum_J f_J T_J$ on 285 ($e=1$) / 278 ($e=2$)
random (sector, tuple) pairs across the whole system; and confirmed
the bookkeeping (no stored sector is diagonal; exactly 49 diagonal
sectors with 1,205 equations deferred).

## What is proved, what is computed, what is open

**Dimension 494 ($e = 1$).** Computed, in exact rational arithmetic
and independently re-verified as above: the affine-linear
$(\mathfrak{g}_0,\mathfrak{g}_0,W)$-against-$W$ system (21,807 of the
23,012 channel equations; the other 1,205 are shown to be genuinely
quadratic, with the explicit $\Delta$ analysis and numerical
evidence) has rank 165 and is consistent, with the explicit
12-dimensional solution space recorded. Hence the linear stage does
not exclude 494, and no Farkas-style certificate exists for it.
**Open:** whether the reduced quadratic system — 1,205 diagonal
equations on the 12-dimensional $(\omega_2, S)$ solution space,
together with the $(\mathfrak{g}_0,W,W)$ and $(W,W,W)$ systems in the
80 total free parameters — has a rational solution with
$\sigma \ne 0$. Dimension 494 remains **open**.

**Dimension 495 ($e = 2$).** Computed and re-verified identically:
the affine system (22,131 of 23,336 channel equations) has rank 170
and is consistent, with the explicit 16-dimensional solution space
recorded; the linear stage does not exclude 495. **Open:** the
reduced quadratic system — the same 1,205 diagonal equations
(quadratic in 14 mixed channels) on the 16-dimensional solution
space, together with the other Jacobi types in 84 total free
parameters, with $\det S_{11} \ne 0$. Dimension 495 remains **open**.

Net effect of stages one and two: the affine-linear programme of
PR #7 §5 is now exhausted at all three values of $e$. It excludes
493 (stage one) and provably cannot exclude 494 or 495; any further
progress on the Asterion interval $\{494, 495, 496\}$ must engage
the quadratic systems above, starting with the 1,205 diagonal-sector
equations restricted to the explicit solution spaces delivered here.

## Files

- `asterion_linear_e12.py` — the generalised assembly and exact
  solve (portable; `--e {0,1,2}`; `--repo` defaults to
  `../../PerfectJet` relative to the script; the repository is only
  read). Runtimes ≈ 410 s ($e = 1$) and ≈ 414 s ($e = 2$), run in
  parallel, of which the sector extraction is the bulk.
- `asterion_e1_results.json`, `asterion_e2_results.json` — checks,
  counts, modular and exact ranks, quadratic-evidence record, the
  explicit solution bases, sector metadata, and the deferred
  diagonal-sector list.
- `asterion_e1_system.json.gz`, `asterion_e2_system.json.gz` — all
  affine channel equations (sector, $J$, sparse coefficients,
  constant), one JSON object per line.
- `asterion_e1_run.log`, `asterion_e2_run.log` — the main runs'
  stage logs.
- `verify_e12.py` — independent verification (solution re-check
  against all stored rows, contraction re-derivation of three
  sectors per $e$, global spot checks, bookkeeping); `--e {1,2}`,
  `--repo` as above.
- `verify_e1_log.txt`, `verify_e2_log.txt` — captured output of the
  passing verification runs.
