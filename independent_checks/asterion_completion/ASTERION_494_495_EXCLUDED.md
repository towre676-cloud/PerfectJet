# Asterion 494 and 495 are EXCLUDED: the diagonal quadratic systems force σ = 0 and det S₁₁ = 0

Committed here on the branch `muse/asterion-494-495-excluded`, as new files under `independent_checks/asterion_completion/`, for review by pull request against main; no existing repository file is changed.

Third stage of closing the Asterion 493–496 gap (programme item
AST-P036), following stage one ($e = 0$: dimension 493 excluded,
`ASTERION_493_EXCLUDED.md`, in this directory) and stage two (the affine-linear
systems at $e = 1, 2$ are consistent, with explicit solution spaces of
dimensions 12 and 16; the 1,205 diagonal-sector
$(\mathfrak{g}_0,\mathfrak{g}_0,W)$-against-$W$ channel equations are
genuinely quadratic and were deferred,
`ASTERION_E12_LINEAR.md`, in this directory). This stage assembles those 1,205
deferred equations exactly as polynomials on the stage-two solution
spaces and solves them over **Q**. The outcome is a complete
refutation at both values of $e$, by an unexpectedly small exact
certificate — the same two channel equations, in sector
$(7,7,7,7)$, with the same two rational weights, at both $e = 1$ and
$e = 2$:

$$
\lambda_0\, G^{(J=1)} \;+\; \lambda_1\, G^{(J=3)} \;=\;
\begin{cases} \sigma & (e = 1),\\[2pt] \det S_{11} \;=\; z_{13}z_{15} - z_{14}^2 & (e = 2), \end{cases}
$$

with $\lambda_0 = 8251546820365125306207126636252364800000000$ and
$\lambda_1 = -535242276962023543213984862699520000000$, an exact
polynomial identity in the solution-space coordinates $z$ (verified
from the stored polynomial files by two independent scripts, and the
two equations themselves independently re-derived from the numeric
model; see Verification). Every common zero of the diagonal system
is a zero of $G^{(1)}$ and $G^{(3)}$, hence has $\sigma = 0$
(resp. $\det S_{11} = 0$). But the PR #7 normal form requires
$S_{11}$ nondegenerate — $B$ must be a nondegenerate form and the
bracket $[x,w]$ is recovered through $B^{-1}$, whose trivial block is
$S_{11}^{-1}$. Therefore **no quadratic completion exists in
dimension 494, and none in dimension 495**. Combined with stage one
and the cotangent-double construction at 496, the Asterion interval
$\{494, 495, 496\}$ collapses: **the minimum quadratic completion
dimension is 496**, attained by the cotangent double. (As in stages
one and two, "excluded" means: excluded within the
$\mathfrak{sl}_2$-equivariant normal form of PR #7 §5, in the gauge
$c = 1$, $a_m = 1$; that reduction is the standing hypothesis of the
whole program.)

## Assembly of the polynomial systems (exact)

Stage two carries brackets as BV objects whose $\Delta$ terms are
kept symbolic in $S_{11}^{-1}$: a $\Delta$ term is a pair
$(\mathrm{cov}, \mathrm{nd})$ representing the
$\mathfrak{n}$-supported vector $\sum_{t,u} (S_{11}^{-1})_{tu}\,
\mathrm{cov}_u \cdot \mathrm{nd}_t$, with $\mathrm{cov}$ affine in the
mixed $\omega_2$ channels and $\mathrm{nd}_t$ the
$\mathfrak{n}$-part of $[x, e_t]$. Pairing against $w'$ in an
$M$-block of spin $d$ pairs $\mathrm{nd}_t$ through $\beta$, giving
affine forms $s_t$; the full Jacobi component is
$F = A + \sum_{\text{terms}} \sum_{t,u} (S_{11}^{-1})_{tu}\,
\mathrm{cov}_u s_t$ with $A$ the affine part stage two computes.
`assemble_diagonal.py` implements this pairing (`pair_w_full`),
clears the denominator — $G := \sigma F$ at $e = 1$;
$G := \det(S_{11}) \cdot F$ at $e = 2$, using the adjugate
$\mathrm{adj}(S_{11})$ whose entries are linear in $S_{11}$ — and
extracts the channel components $G_J$ in each of the 49 diagonal
sectors by stage two's own evaluation-matrix method (transvectant
channel matrix, exact rational Gaussian elimination), now with
polynomial right-hand sides. Restriction to the stage-two solution
spaces (particular solution $0$; bases read from the stage-two
results JSONs) substitutes $\mathrm{params} = \sum_i z_i\,
\mathrm{basis}_i$.

The restricted systems are extremely sparse. At $e = 1$: all 1,205
equations are quadratic in the 12 coordinates, none identically
zero, at most 4 monomials each (3,972 monomials in total), and —
the decisive structural fact — **only the monomials $z_{11}$
($=\sigma$), $z_2^2$, $z_2 z_3$, $z_3^2$ occur, in any equation**.
At $e = 2$: all 1,205 equations are cubic in the 16 coordinates,
none identically zero, at most 12 monomials each (11,864 total), and
only 12 monomials occur: $z_{13}z_{15}$, $z_{14}^2$, and the ten
cubics $z_i z_j z_k$ with $\{i,j\}$ ranging over the mixed-coordinate
pairs and $k \in \{13, 14, 15\}$. (Coordinates $z_0, z_1$ — the two
never-occurring channels — and at $e = 1$ the $s_m$ directions
$z_4, \dots, z_{10}$ occur in no diagonal equation; $\sigma = z_{11}$
is itself a coordinate at $e = 1$, and at $e = 2$ the $S_{11}$
entries are the coordinates $z_{13}, z_{14}, z_{15}$, so
$\det S_{11} = z_{13}z_{15} - z_{14}^2$ exactly.) Both systems are
therefore **linear in their monomial vectors**, and exact rational
linear algebra — not Gröbner bases — settles them. No finite-field
step and no evidence-versus-proof gap arises anywhere in this stage:
every computation is over **Q**.

## Dimension 494 ($e = 1$): excluded

The $1205 \times 4$ coefficient matrix over the monomial vector
$(z_2^2,\ z_2 z_3,\ z_3^2,\ \sigma)$ has $\mathrm{rank}_{\mathbf{Q}}
= 4$ (exact, `solve_diagonal.py`). Hence at every common zero of the
1,205 equations the whole monomial vector vanishes; in particular
$\sigma = 0$. The economical certificate is two equations of sector
$(7,7,7,7)$:

$$
G^{(1)} = \tfrac{1}{K_a}(z_2 - z_3)^2 + \tfrac{1}{D_a}\,\sigma,
\qquad
G^{(3)} = \tfrac{1}{K_b}(z_2 - z_3)^2 + \tfrac{1}{D_b}\,\sigma,
$$

with $K_a = 82515468203651253062071266362523648000000000$,
$D_a = 750140620033193209655193330568396800000000$,
$K_b = 5352422769620235432139848626995200000000$,
$D_b = 53524227696202354321398486269952000000$. With
$\lambda_0 = K_a/10$ and $\lambda_1 = -K_b/10$ the quadratic parts
cancel ($\lambda_0/K_a + \lambda_1/K_b = \tfrac1{10} - \tfrac1{10}
= 0$) and the $\sigma$ parts give
$\lambda_0/D_a + \lambda_1/D_b = 11 - 10 = 1$: exactly
$\lambda_0 G^{(1)} + \lambda_1 G^{(3)} = \sigma$. A completion in
dimension 494 would restrict to a point of the stage-two solution
space with all $G_J = 0$ and $\sigma \ne 0$ — impossible. **494 is
excluded.** Consequently the $(\mathfrak{g}_0,W,W)$ and $(W,W,W)$
Jacobi types at $e = 1$ (ambient counts 45,623 and 14,834) never
need to be solved: there is no $(\omega_2, S)$ point left for them
to constrain.

## Dimension 495 ($e = 2$): excluded

Kept entirely separate from $e = 1$: the assembly, monomial matrix,
and certificate were computed independently for $e = 2$ (the
numerical coincidence of the weights is explained below). The
$1205 \times 12$ coefficient matrix over the monomial vector has
$\mathrm{rank}_{\mathbf{Q}} = 4$ (nullity 8), and the $\det$
direction $(1, -1, 0, \dots, 0)$ is orthogonal to the entire null
space, i.e. $\det S_{11}$ lies in the row space. The sparse
certificate is again the sector-$(7,7,7,7)$ equations $J = 1$ and
$J = 3$, which here read

$$
G^{(1)} = \tfrac{1}{K_a}\,\Phi + \tfrac{1}{D_a}\det S_{11},
\qquad
G^{(3)} = \tfrac{1}{K_b}\,\Phi + \tfrac{1}{D_b}\det S_{11},
\qquad
\Phi = [u\ v]\; \mathrm{adj}(S_{11})\; \begin{bmatrix} u \\ v \end{bmatrix},
$$

with $u = z_2 - z_4$, $v = z_3 - z_5$ (in these two equations the
mixed coordinates enter only through $u$ and $v$; the remaining
1,203 equations have the same 12-monomial support but general
coefficients, and are not needed), the same constants $K_a, D_a, K_b, D_b$ as
at $e = 1$, and $\det S_{11} = z_{13}z_{15} - z_{14}^2$ entering via
$\det \cdot A_J$, where $A_J$ is the same affine part as at $e = 1$
— which is why the same weights occur: with
$\lambda_0 = K_a/10$, $\lambda_1 = -K_b/10$ the $\Phi$ parts cancel
($\tfrac1{10} - \tfrac1{10}$) and the $\det$ parts give
$11 - 10 = 1$: $\lambda_0 G^{(1)} + \lambda_1 G^{(3)} = \det S_{11}$
exactly, as polynomials. Every common zero of the 1,205 equations
therefore has $\det S_{11} = 0$, contradicting nondegeneracy.
**495 is excluded.** The other Jacobi types at $e = 2$ (ambient
counts 46,378 and 15,233) are likewise moot.

## Verification (all exact, all passing)

`validate_diagonal.py` (`validate_diagonal.log`): for 4 random
rational points $z$ of each solution space (side condition
satisfied), with stage two's numeric model — every bracket
$[x, w]$ checked against its defining pairings
$B([x,w], z) = \omega(x, w, z)$ for all basis vectors $z$, $S_{11}$
inverted exactly — the channel identity
$\mathrm{denom}(z) \cdot F_{\mathrm{numeric}}(\mathrm{tuple})
= \sum_J G_J(z)\, T_J(\mathrm{tuple})$ holds at 3 sampled weight
tuples in **each of the 49 diagonal sectors**: 588 checks per $e$,
zero failures. As a parameter-level spot check, the un-restricted
assembled polynomials in sector $(7,7,7,7)$ reproduce stage two's
recorded quadratic-evidence values $F = 2732730, 2459457, 1639638$
at $p = 0, 1, 2$ exactly (both $e$).

`verify_certificates.py` (`verify_certificates.log`), which shares
no code with the symbolic $\Delta$ assembly: (i) the two certificate
identities are re-verified from the stored polynomial files with
plain `Fraction` arithmetic; (ii) the two certificate channels
$G^{(1)}(z)$, $G^{(3)}(z)$ are re-derived from the numeric model
alone, at 3 fresh random points $z$ per $e$, by evaluating
$\mathrm{denom} \cdot F_{\mathrm{numeric}}$ at enough tuples of
sector $(7,7,7,7)$ to invert the channel matrix and solving over
**Q** — agreement with the stored polynomials in all 12 values, and
$\lambda_0 G^{(1)}(z) + \lambda_1 G^{(3)}(z) = \mathrm{denom}(z)$ at
every point.

`solve_diagonal.py` (`solve_diagonal.log`, `solve_results.json`)
recomputes the ranks over **Q** and re-verifies both polynomial
identities from the files; rerunning the full pipeline
(assemble → validate → solve → verify) reproduces everything.

## What is proved, what is computed, what is open

**Dimension 494 ($e = 1$).** Proved (modulo the standing PR #7
normal-form reduction and stage two's verified linear solve): no
quadratic completion exists. The proof is the assembled diagonal
system (exact, validated as above) plus the identity
$\lambda_0 G^{(1)} + \lambda_1 G^{(3)} = \sigma$, which lies in the
ideal generated by two of the system's equations; equivalently the
saturated system ($+\ \sigma u = 1$) has Gröbner basis $\{1\}$ over
**Q** — obtained here directly, without a Gröbner computation,
because the system is linear in its monomial vector and
$\mathrm{rank}_{\mathbf{Q}} = 4$ forces $\sigma = 0$ on its own.
Dimension 494 is **closed (excluded)**.

**Dimension 495 ($e = 2$).** Proved (same standing hypotheses,
independent computation): no quadratic completion exists; $\det
S_{11}$ lies in the ideal generated by the same two sector's
equations ($\lambda_0 G^{(1)} + \lambda_1 G^{(3)} = \det S_{11}$),
so the saturated system ($+\ (\det) u = 1$) is the unit ideal over
**Q**. Dimension 495 is **closed (excluded)**.

**Open:** nothing remains in the Asterion 493–496 interval. With
493 excluded by stage one and the cotangent double attaining 496,
the minimum dimension of a quadratic completion of
$\mathfrak{g}_0 = \mathfrak{sl}_2 \ltimes \mathfrak{n}$ (in the PR #7
normal form) is **496**. No claim is made outside that normal form;
nor does anything here speak to completions not arising from the
Rees-boundary setup of AST-P036.

## Files

- `assemble_diagonal.py` — symbolic assembly of the diagonal
  systems (extends stage two's machinery; the repository is only
  read). Runtimes ≈ 43 s ($e = 1$), ≈ 40 s ($e = 2$).
- `diagonal_e1_polys.json`, `diagonal_e2_polys.json` — the 1,205
  restricted polynomial equations per $e$ (sector, $J$, monomials in
  $z$ → coefficients).
- `diagonal_e1_params.json`, `diagonal_e2_params.json` — the same
  equations before restriction (monomials in the full 177/186
  parameters).
- `assemble_e1.log`, `assemble_e2.log` — assembly logs.
- `validate_diagonal.py`, `validate_diagonal.log` — channel-identity
  validation against the pairing-verified numeric model (588 checks
  per $e$) plus the parameter-level evidence point.
- `solve_diagonal.py`, `solve_diagonal.log`, `solve_results.json` —
  the exact monomial linear algebra over **Q** (ranks 4 and 4), the
  two certificates with weights $\lambda_0, \lambda_1$, and the
  polynomial-identity verifications.
- `verify_certificates.py`, `verify_certificates.log` — independent
  certificate verification (plain-fraction identity check; numeric
  re-derivation of the two certificate channels at random points).
