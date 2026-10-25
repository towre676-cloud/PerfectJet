# Asterion 493: the e = 0 affine-linear Jacobi system is inconsistent — dimension 493 is excluded

First stage of closing the Asterion 493–496 gap (programme item AST-P036),
following the reduction in PerfectJet PR #7
(`independent_checks/asterion_completion/INTERVAL_493_496.md`, §5).
Committed here on the branch `muse/asterion-493-excluded`, as new files
under `independent_checks/asterion_completion/`, for review by pull
request against main; no existing repository file is changed.
Everything below is over **Q**, in exact rational arithmetic.

## Result (computed, and independently re-verified)

The affine-linear system that any quadratic completion of
$\mathfrak{g}_0 = \mathfrak{sl}_2 \ltimes \mathfrak{n}$ in dimension
$493$ would have to satisfy — the $(\mathfrak{g}_0, \mathfrak{g}_0, W)$
Jacobi components paired against $W$, in the 169 unknowns
$(\omega_2, S)$ of the $\mathfrak{sl}_2$-equivariant normal form — is
**inconsistent**. It has 22,688 channel equations, coefficient rank
160, and no solution. Consequently, given the normal-form reduction of
PR #7 (§§3 and 5: at $e = 0$ any completion has $c \ne 0$, restricted
radical exactly $\mathfrak{n}$, and $W \cong \mathfrak{n}$ as
$\mathfrak{s}$-modules, so its data occur in the family parametrised
here, and Jacobi is invariant under the identifications used),
**there is no quadratic completion of $\mathfrak{g}_0$ in dimension
493**. The completion interval narrows from $[493, 496]$ to
$\{494, 495, 496\}$, with 496 attained by the cotangent double.

The inconsistency is not a near-miss depending on delicate
cancellation across the whole system. **434 of the 22,688 channel
equations are nonzero constants with every parameter coefficient equal
to zero**; each one is on its own a complete Farkas-style certificate
(an equation $0 = \text{const} \ne 0$ that no choice of
$(\omega_2, S)$ can satisfy). The headline certificate, the one the
exact solver isolated, is the intermediate-spin $J = 1$ component in
the sector $(a, b, c, d) = (7, 7, 7, 7)$ (that is,
$x, y \in V_7 \subset \mathfrak{n}$, $w, w' \in W_7$):

$$f^{(7,7,7,7)}_{J=1}(\omega_2, S) \;=\;
\frac{1}{750140620033193209655193330568396800000000} \;\ne\; 0,$$

identically in all 169 unknowns; the Farkas functional is the single
row itself, with $\lambda =
750140620033193209655193330568396800000000$ giving constant sum exactly
$1$. The most arithmetically striking certificate is in sector
$(7, 11, 7, 11)$, whose $J = 18$ component is the constant $-154$
exactly. The full list of the 434 obstructing rows, with their
sectors, spins and constants, is recoverable from
`asterion_linear_system.json` (rows with empty `coeffs` and nonzero
`const`).

## How the system was assembled

The assembly works in the binomial polynomial basis of the repository's
principal $\mathfrak{sl}_2$ basis, where every Clebsch–Gordan coefficient
is rational. The $\mathfrak{g}_0$ bracket at $t = 0$ is a single
transvectant channel, $[e_i^a, e_j^b] = \kappa_{ab}^{a+b-1}\,
T_1(e_i^a, e_j^b)$, with $\kappa$ the repository's own coupling table
(`PrincipalE8Basis.couplings()`, all 170 entries) and $T_1$ the
repository's `monomial_transvectant`; this was checked against
`PrincipalReesFamily.basis_bracket(t = 0)` on 3,744 sampled basis pairs
with zero mismatches. The invariant form on each block is
$\beta_m(e_p, e_q) = (-1)^p \binom{2m}{p}\,\delta_{p+q,\,2m}$, verified
to be invariant under the $\mathfrak{sl}_2$ action; the gauge of PR #7
§5 is $c = 1$, $A = \beta$ (i.e. $a_m = 1$), $S|_{W_m} = s_m \beta_m$.
The unknowns are the 162 $\mathfrak{sl}_2$-singlet channels of
$\omega_2$ (transvectant channels $(a; b, d)$, antisymmetrised in the
$W$ slots) and the 7 scalars $s_m$ — the counts 162, 7, 169 and the
target dimension 22,688 all reproduce PR #7's Part B character
arithmetic exactly. Brackets $[x, w]$ ($x \in \mathfrak{g}_0$,
$w \in W$) are computed from $\omega$ by the block inverse of $B$
($\mathfrak{s}$-block via $\beta_1^{-1}$; $u_W = A^{-1} v_{\mathfrak{n}}$;
$u_{\mathfrak{n}} = A^{-T}(v_W - S u_W)$ with $(Su_W)(p) = s_m v_{\mathfrak{n}}(p)$
on block $m$), which makes the $(\mathfrak{g}_0, \mathfrak{g}_0, W)$
Jacobiator paired against $W$ affine in $(\omega_2, S)$ by construction,
as PR #7 §5 predicts. The 22,688 scalar equations are extracted sector
by sector: for each pair of $\mathfrak{g}_0$ blocks $(a, b)$ and $W$
blocks $(c, d)$, the Jacobi tensor restricted to the sector is expanded
in its singlet channels $T_J$ (intermediate-spin coupling of the
$(x, y)$ and $(w, w')$ transvectants, contracted by $\beta_J$), by
evaluating at greedily selected weight tuples and inverting the exact
evaluation matrix. The assembled system is very sparse: every equation
involves at most 5 unknowns, 12,495 equations are parameter-free (12,061
of them identically zero, 434 the nonzero obstructions above), and the
rest have support 1–5.

The rank was computed modulo two primes (1000003 and 999983, both
giving rank 160 and inconsistency) and then exactly over **Q**: an
exact RREF with transformation tracking on a 161-row subsystem (160
pivot rows plus the obstructing row) has coefficient rank exactly 160
and produces the Farkas functional, which was checked by direct dot
products against the stored rows.

## Verification (independent checks, all passing)

The implementation and the certificate were verified through routes
that do not reuse the extraction path. The $\mathfrak{g}_0$ bracket
formula agrees with the repository's Rees-family bracket on 3,744
sampled pairs and satisfies the Jacobi identity on 1,500 random
triples; $\beta_m$ is exactly invariant under the
$\mathfrak{sl}_2$ action; every $\omega_2$ channel tensor is annihilated
by the raising operator (308 tests); the components of the Jacobiator
paired against $\mathfrak{g}_0$ vanish identically on 1,200 random
tuples, confirming PR #7 §5's claim inside this implementation; and the
Jacobi values $F$ were recomputed numerically at random rational
parameters by a second implementation in which every bracket
$[x, w]$ is checked against its defining pairings
$B([x, w], z) = \omega(x, w, z)$ for all 493 basis vectors $z$
(24 tuples, no failures). The stored equations reproduce $F$ on fresh
tuples: residual identities $F(t) = \sum_J f_J T_J(t)$ hold on 40 fresh
tuples of sector $(7,7,7,7)$ and on 300 random (sector, tuple) pairs
across the whole system. Finally, the two sectors $(7,7,7,7)$ and
$(7,11,7,11)$ were re-derived by a completely different method —
contraction against the channel tensors under the
$\mathfrak{sl}_2$-invariant pairing summed over **all** weight tuples
of the sector (2,255 and 4,055 tuples respectively), with the channel
Gram matrix checked to be exactly diagonal, as Schur orthogonality
requires — and all 22 channel components of the two sectors, including
every obstructing constant, agree with the stored system exactly.
`verify_certificate.py` reruns all of these certificate checks in
about 15 seconds (see `verify_log.txt`).

## What is proved, what is computed, what is open

What this stage establishes is a finite exact computation, dependent
on one proved input from PR #7: the equivariant normal form (any
dimension-493 completion has $c \neq 0$ and data in the
$(\omega_2, \omega_3, S)$ family, with the linear subsystem above as a
necessary condition). The assembly, the rank, and the inconsistency
certificate are computed here in exact rational arithmetic from the
repository's own coupling data and are independently re-verified as
described; the nonvanishing of the obstructing components is
independent of the normalisation conventions for $\beta$ and the
channel tensors (rescaling changes the constants by nonzero factors,
never to zero). Within those terms, dimension 493 is **closed**:
no quadratic completion exists there.

Dimensions 494 and 495 remain **open**. The same programme applies to
them — at $e = 1$ and $e = 2$ the linear stage has 177 and 186 unknowns
($\omega_2$ has 169 and 176 channels, $S$ has 8 and 10 parameters, by
PR #7's counts) — but the $e = 0$ computation says nothing about them
directly, and even a consistent linear stage there would leave the
quadratic system in $(\omega_2, \omega_3, S)$ (including the 68
$\omega_3$ channels at $e = 0$, more at higher $e$) untouched. Also
untouched, as in PR #7: completions are considered over **Q** (the
obstruction is rational, so it excludes completions over any field of
characteristic zero, and over any extension, since it is an identity
$0 = \text{const} \neq 0$ in the parameters).

## Files

- `asterion_linear.py` — the assembly and exact solve (portable;
  `--repo` defaults to `../../PerfectJet` relative to the script;
  the repository is only read). Runtime ≈ 500 s, of which ≈ 487 s is
  the sector extraction.
- `asterion_linear_results.json` — checks, modular ranks, the Farkas
  certificate, sector metadata (channels and selected tuples for all
  1,640 nonempty sectors), and the channel/parameter index conventions.
- `asterion_linear_system.json` — all 22,688 affine equations
  (sector, $J$, sparse coefficients, constant), one JSON object per line.
- `asterion_linear_run.log` — the main run's stage log.
- `verify_certificate.py` — independent verification of the
  certificate (Farkas dot products, contraction re-derivation of two
  full sectors, residual and spot checks); `--repo` as above.
- `verify_log.txt` — captured output of a passing verification run.
