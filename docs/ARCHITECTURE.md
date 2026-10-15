# Architecture

The current code is a small exact nucleus underneath a much larger documented program. New adapters must state their input domain, preserved question, operation conventions, evidence, and limits.

| Module | Responsibility | Failure information |
|---|---|---|
| `exact.py` | Rational rank, nullspaces, observable closure | Hidden target vector |
| `polynomial.py` | Sparse algebra and feature pullback | Unclosed polynomial |
| `transvectants.py` | Odd gates, kernel/active dimensions | Gate obstruction and finite rank |
| `rings.py` | Quotient ring arithmetic and explicit field maps | Nonunit denominator |
| `collision.py` | Valuation geometry and cyclotomic recurrence | Input-domain rejection |
| `populations.py` | Feasible completions, rank/unrank, ties, constraint attribution, inclusion profiles | Infeasible prefix/rank rejection |
| `semantics.py` | Partial all-future equivalence | Distinguishing word |
| `dynamics.py` | Energy, defects, bounds, decision margins | Zero dial or unresolved decision |
| `jets.py` | Finite composition and Riccati rejection | First nonzero residual |
| `psg.py` | Corrected scalar flip reduction | Numerical bracket rejection |
| `lattice.py` | Smith and Hermite forms, integer solvability, integer kernels, saturation | Certificate row; unsaturated witness |
| `realization.py` | Single- and multi-output word-Hankel realization, coarsest exact lumping | Held-out witness word; split block |
| `loci.py` | Exact one-parameter rank loci; partner-family exceptional parameters | Locus factor with its rank |
| `parametric.py` | Groebner bases, saturation, comprehensive rank cells in several parameters | Cell equations, inequations, rational points |
| `sieve.py` | Adaptive local power-residue sieve | Excluding modulus and residue |
| `strata.py` | Active partner strata, sextic discriminant, replayed partners at rational points | Stratum equations; commuting versus active split |
| `deformation.py` | Stationary response, relation breaking directions, symmetry protection | Breaking direction with its dR |
| `modular.py` | Groebner bases over GF(p), minors by modular Bareiss, Rabinowitsch emptiness | Unit-ideal verdict modulo a stated prime |
| `incidence.py` | Partner incidence in the full sextic space: line probes, covariants over quotient rings, slice classification, degenerate forms | Hypersurface invariant; orbit certificate; open degrees |
| `quadratic.py` | Solution-carrying compiler for k y^2 = a n^2 + b n + c: transport, Nagell seeds, orbit admissibility, remote indices | Branch and completeness status; failed reconstruction congruence |
| `invariants.py` | Clebsch invariants, weighted orbit test, Cayley-Sylvester counts, invariant relations on cells, slice certificates, degree-12 covariant partner | Unequal weighted point; relation weight |
| `readout.py` | Readout identifiability, demand readouts, minimal repair, Gaussian value of information | Two-fit witness vector; repeat versus new direction |
| `decisions.py` | Certified choice, targeted refinement, evolution-defect split | Overlapping contenders; separated defects |
| `applications/nfl_scouting` | Combine turn events, identifiability gate, pooled readouts, leakage-checked targets, grouped temporal validation, cards | Unidentified readout witness; leakage check; per-fold G |
| `engine.py` | Adaptive closure loop and the unified representation-and-obstruction report | Classified obstruction and next calculation |

The common structure is a representation q, evolution F, output O, and possibly weights. Exact dynamics requires qF=Fbar q. Exact weighted aggregation requires RA=Abar R. Approximate closure supplies residuals rather than an exact identity. Evidence status is external metadata; it must not be inferred from a class name.

## Boundaries

Lean source mentioned in the historical atlas remains upstream. General interval proving, the full seven-coefficient sextic incidence variety, numerical Hankel realization, unlimited nonlinear closure, global elliptic completeness, chemical simulation, empirical forecasting, and site/mobile synchronization are not implemented in 0.10.0. Smith form, exact single-output word realization, and coarsest exact lumping were added in 0.2.0; Hermite form, multi-output realization, one-parameter rank loci, and the local sieve in 0.3.0; multi-parameter rank cells in 0.4.0; active strata, readout identifiability, certified decisions, and the adaptive engine in 0.5.0; the Combine scouting adapter in 0.6.0, which reports no real-data result; invariant-theoretic partner results in 0.7.0; the quadratic solution compiler in 0.8.0. Their integration requirements are retained explicitly.

## Add a result

Add the mathematics to a canonical chapter, add a registry row with correct status/assumptions, add or update topic coverage, implement replay only if the claim is executable here, and add tests that compare a genuinely independent route or attack a meaningful boundary. Regenerate monograph and coverage, run the checks, retain the receipt, and publish a complete package. A failed proposed identity should be retained as a correction or witness.
