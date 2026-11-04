# Independent collision/Pell replay

Run from the repository root using Python 3.10 or newer and the standard library:

```bash
python independent_checks/collision_pell/verify.py --output independent_checks/collision_pell/report.json
```

The script compares the public extension APIs with separately written oracles.
It enumerates actual ordered divisor pairs; iterates Pell solutions directly;
uses finite modular cycles for remote Pell indices; expands literal formal
logarithms; reconstructs Euler products with binomial coefficients; and recovers
every Galois norm coefficient for conductors 1 through 6 by exact interpolation
of multiplication determinants. Its cyclotomic polynomials use a separate
Möbius-product construction. It also checks positive residue populations,
every rank of bounded examples, prime-local projection semantics, rational
Euler-product interval endpoints, and invalid-input/allocation limits. The
conductor-four transport is checked on actual integer factor pairs with
products through 500, including coprimality, fourth-power size preservation,
inverse reconstruction, and the independent fourth-power divisor formula.
Every public JSON operation also receives a route-level replay.

The JSON report binds the replay to SHA-256 hashes of the examined source and
proof files. Regenerate it after source changes. It is an executable arithmetic
check, not a Lean certificate or a proof of Estermann's theorem. The universal
self-inversive and projection arguments are reviewed separately in the report;
finite interpolation ranges are explicitly bounded. A full Galois norm,
prime-local projection, global total-collision residue, and individual complex
phase product have different meanings throughout this replay.
