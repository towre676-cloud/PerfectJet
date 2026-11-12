# Shared exact-mathematics engine

PerfectJet now contains a small set of dependency-free and exact-algebra
components intended for reuse by the wider research program.  The design rule
is that a consumer project keeps ownership of its mathematical theorem and its
independent verifier; PerfectJet supplies reusable algebra and emits receipts
whose scope is narrower than the consuming theorem.

## Layers

### 1. Exact linear algebra

`perfectjet.exact` supplies rational RREF, rank, nullspace, row
spaces, matrix multiplication and target-recovery primitives.

### 2. Sparse polynomial algebra

`perfectjet.polynomial.Poly` supplies exact sparse multivariate
polynomials, differentiation, substitution and evaluation.  Odd binary
transvectants live in `perfectjet.transvectants`.

### 3. Kernel towers

For a finite state space,

[
mathcal O_r=[C;CA;ldots;CA^r],qquad K_r=kermathcal O_r.
]

`matrix_kernel_tower` certifies permanent stabilization by exact
row-space closure.  `polynomial_kernel_tower` permits degree-changing
evolution but is intentionally bounded: a finite plateau is not an infinite
theorem.

### 4. Parametric incidence

`parametric_kernel_tower` interpolates keyed observation matrices
over (mathbf Q[t_1,ldots,t_s]) and passes them to PerfectJet's existing
Gröbner/saturation rank-cell engine.  This produces exact constructible
constant-rank cells and rank-drop loci.  The interpolation degree bound is an
explicit caller obligation and is recorded in every report.

### 5. Observation design

`optimize_coefficient_panel` exhausts coefficient-evaluation panels
and minimizes the exact equal-error gain

[
|M^{-1}|_infty.
]

The theorem is only about the declared sensor class.  Arbitrary rational
linear functionals form a larger optimization problem.

### 6. Monogenic quotient algebras

`MonogenicQuotient` computes exact arithmetic in

[
mathbf Q[x]/(f)
]

for monic (f): multiplication matrices, powers, traces, norms, trace pairing
and power-basis discriminant.  It does not establish irreducibility, integral
maximality or identify a presented quotient with a number field.

## Current consumers

### nonlinearhamiltonian

The bridge keeps the defining-star-exponential implementation independent and
compares it with PerfectJet's direct transvectant tower over all eleven
homogeneous sextic root strata, degrees 0--10 and refinement depths 0--2.
The family

[
q^4p^2+delta q^6
]

is also sent through the parametric engine, where (delta=0) is recovered as
an algebraic rank-drop boundary.

Consumer PR: `towre676-cloud/nonlinearhamiltonian#20`.

### singularity

The graph project retains ownership of its height-series formulas,
realizability proof and reader certificates.  PerfectJet independently replays
the exhaustive coefficient-panel optimization, including the connected
six-measurement optimum.

Consumer PR: `towre676-cloud/singularity#14`.

### certified-selmer-pipeline

The Selmer project keeps its standard-library cubic arithmetic and Mathlib
number-field development.  PerfectJet independently replays arithmetic in the
presented cubic quotient, including multiplication, norms, traces, cover
identities and the power-basis discriminant.

Consumer PR: `towre676-cloud/certified-selmer-pipeline#6`.

## Proof-boundary policy

Cross-repository agreement is valuable redundancy, but it is not a substitute
for the theorem that interprets the computation.

In particular:

- a bounded kernel calculation is not an all-degree Hamiltonian theorem;
- a rank-drop computation needs its parameter-family and interpolation-degree
  hypotheses;
- a coefficient-panel optimum is relative to its declared sensor class;
- quotient-algebra discriminant (1556) is not by itself a proof that the
  associated power order is maximal or that the field discriminant is 1556;
- none of these Python modules becomes Lean-formalized merely because a
  consumer repository also contains Lean proofs.

Each consumer pins a concrete PerfectJet commit so changes in the shared
engine are reviewable and replayable rather than silently inherited.
