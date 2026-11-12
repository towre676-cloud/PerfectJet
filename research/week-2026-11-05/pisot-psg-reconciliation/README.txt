QUOTIENTS, CLOSURE, AND PHYSICAL OBSERVABLES
3 November 2026

READ

Open research-reconciliation.html in a modern browser. It is self-contained:
all mathematical typesetting is embedded MathML, with no remote scripts,
fonts or style dependencies. Its source references remain clickable.

CONTENT

The article reconciles current PerfectJet recovery, the Pisot scalar family,
PSG synthesis, a displayed finite graph, protected flavor and annular periods.
It contains complete analytic proofs of the integral and its endpoint
correction, a corrected multiplier-profile synthesis, and the proof structure
for an interval-certified unique subcritical flip. The physical comparison
keeps each model's own assumptions and observables.

REPRODUCE THE CHECKS

Use Python 3.11 or later. From this extracted directory:

  python -m pip install -r requirements.txt
  python pisot_scalar_check.py
  python arithmetic_matrix_audit.py > arithmetic_matrix_audit.json
  python recheck_integral_and_flavor.py --dps 80
  python recheck_integral_and_flavor.py --dps 100 --output integral-and-flavor-checks-100dps.json

The scalar checker uses Arb real-ball interval arithmetic at 384 bits. It
encloses a root and local coefficients and proves monotonicity on 1,130
covering rational intervals. Its separate mpmath calculations at 80 and 120
decimal digits are explicitly classified as floating-point cross-checks.

The finite-matrix checker uses exact symbolic arithmetic. It verifies the
matrices displayed in the historical manuscripts, not their claimed
extraction from a tiling archive or any global tiling interpretation.

The integral/flavor checker uses high-precision quadrature to corroborate
the analytic integral proof, and exact rational arithmetic to reproduce
the scalar-loop polynomial remainder and Bezout identity. Numerical
quadratures are not interval certificates. The script never treats them
as such.

REBUILD THE ARTICLE (OPTIONAL)

  python -m pip install latex2mathml==3.81.1
  python build_reconciliation.py

VERIFIED RESULTS

All three checkers were executed successfully for the supplied inputs.
The integral calculations agree in every one of their 55 printed digits
at 80 and 100 working decimal digits. The scalar cross-checks agree in
all 65 printed digits of the local flip data at 80 and 120 working digits.
The article was inspected in Chromium at desktop and mobile widths;
its internal references resolve and its MathML has no error nodes.

The current PerfectJet release and selected source chapters were read at
commit 9b69eab9beff3011bc6216b30a460c2c6d0e97be. Its full regression suite
was not rerun in this reconciliation. The later protected-flavor source
was examined selectively; only the displayed scalar-loop obstruction was
freshly recomputed here. References in the article identify the original
completed annulus publication and mixed-mass flavor benchmark.

This package has one level and contains no nested archives.
