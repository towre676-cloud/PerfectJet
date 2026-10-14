# Architecture

The current code is a small exact nucleus underneath a much larger documented program. New adapters must state their input domain, preserved question, operation conventions, evidence, and limits.

| Module | Responsibility | Failure information |
|---|---|---|
| `exact.py` | Rational rank, nullspaces, observable closure | Hidden target vector |
| `polynomial.py` | Sparse algebra and feature pullback | Unclosed polynomial |
| `transvectants.py` | Odd gates, kernel/active dimensions | Gate obstruction and finite rank |
| `rings.py` | Quotient ring arithmetic and explicit field maps | Nonunit denominator |
| `collision.py` | Valuation geometry and cyclotomic recurrence | Input-domain rejection |
| `populations.py` | Feasible completions, rank/unrank, ties | Infeasible prefix/rank rejection |
| `semantics.py` | Partial all-future equivalence | Distinguishing word |
| `dynamics.py` | Energy, defects, bounds, decision margins | Zero dial or unresolved decision |
| `jets.py` | Finite composition and Riccati rejection | First nonzero residual |
| `psg.py` | Corrected scalar flip reduction | Numerical bracket rejection |

The common structure is a representation q, evolution F, output O, and possibly weights. Exact dynamics requires qF=Fbar q. Exact weighted aggregation requires RA=Abar R. Approximate closure supplies residuals rather than an exact identity. Evidence status is external metadata; it must not be inferred from a class name.

## Boundaries

Lean source mentioned in the historical atlas remains upstream. General interval proving, Smith normal form, word-Hankel realization, unlimited nonlinear closure, global elliptic completeness, chemical simulation, empirical forecasting, and site/mobile synchronization are not implemented in0.1.0. Their integration requirements are retained explicitly.

## Add a result

Add the mathematics to a canonical chapter, add a registry row with correct status/assumptions, add or update topic coverage, implement replay only if the claim is executable here, and add tests that compare a genuinely independent route or attack a meaningful boundary. Regenerate monograph and coverage, run the checks, retain the receipt, and publish a complete package. A failed proposed identity should be retained as a correction or witness.
