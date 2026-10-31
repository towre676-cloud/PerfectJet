# Collision/Pell research laboratory

Open **explorer.html** directly for a self-contained interactive laboratory.
It runs offline, including on a mobile browser: exact BigInt residue counts,
signed cancellations, remote cyclotomic coefficients, divisor-pair histograms,
Pell powers and JSON evidence export. Complex-plane graphics are illustrative;
the mathematical outputs identify their exact arithmetic separately.

The integrated application is the **Explore arithmetic collisions** card in
PerfectJet's Math Lab (`python run_observatory.py`). No separate server or
third-party package is needed for the command-line research engines.

## What the research establishes

- The conductor-two collision numerator factors through the Pell unit
  `1+sqrt(2)`; its logarithmic derivative and formal zeta exponents are exact.
- For every conductor `L>1`, the primitive numerator has roots inside and
  outside the unit circle. Its full Galois norm Euler product has the imaginary
  axis as a natural boundary. Conductor one gives `zeta(s)^2`.
- The positive **prime-local** divisibility projection has a finite zeta
  factorization precisely at conductors **1 and 4**. At four it equals
  `zeta(s)^2*zeta(4s)/zeta(2s)`. Every other conductor has a natural boundary.
- Conductor four has an explicit reversible transport from admissible `(m,n)`
  to `(u,v,w)`, with `gcd(u,v)=1` and `m*n=u*v*w^4`.
- The conductor-two positive arithmetic function has an elementary two-term
  summatory asymptotic and certified rational constant/value enclosures.
- Actual factor pairs can be counted, ranked, selected, conditioned and sampled
  by their **total** collision residue. Supplied factorization and output-bit
  budgets remain explicit.

The norm, primitive trace, prime-local projection, and global total-residue
condition are distinct objects. The proofs keep them separate. In particular,
the norm theorem does not classify each individual complex-phase Euler product.
Estermann's theorem is classical; the displayed family classifications have
written proofs and independent checks here, with historical priority unassessed.
No Lean formalization is claimed.

## Commands

From Windows Git Bash, first run `python -m pip install -e .`, then:

```bash
python -m perfectjet collision-research report --limit 10000
python -m perfectjet collision-research projection --conductor 4 --order 12
python -m perfectjet collision-research norm --conductor 3 --order 12
python -m perfectjet collision-research classify --max-conductor 32
python -m perfectjet collision-research constants --prime-cutoff 10000 --s 2
python -m perfectjet collision-research population --conductor 6 --factorization '[[2,4],[3,3],[5,2]]' --rank 7
python -m perfectjet collision-research pell --index 100000000000000000000000000000000000000000000000000 --modulus 1000000007
python -m perfectjet collision-research extract --order 4
```

Every command accepts `--output answer.json`. For reproducible custom requests
use `--request request.json`; all unknown or operation-incompatible keys reject.
Exact integers beyond JavaScript's safe range are decimal strings in JSON.
The original `perfectjet collision --conductor ... --index ...` route remains.

## Python APIs

```python
from perfectjet.collision_population import FactorPairResiduePopulation
from perfectjet.collision_four import collision_four_forward_vectors

p = FactorPairResiduePopulation({2: 4, 3: 3, 5: 2}, conductor=6, residue=0)
assert p.histogram() == (16, 6, 8, 12, 8, 10)
assert p.count() == 16
exponents = p.unrank(7)
assert p.rank(exponents) == 7
print(p.pair(7))
print(p.count(prefix=exponents[:1]))
print(p.sample())  # exact uniform draw via an integer rank

# Aligned exponents of the same primes; no factoring hidden in transport.
u, v, w = collision_four_forward_vectors((4, 1), (2, 4))
```

`RationalEulerFactor.extract` returns a **finite** zeta extraction and its
complete residual. It does not evaluate an infinite formal zeta product in a
region where it may diverge. Norm construction, residue convolution, exact
outputs, prime verification and prime-product work have separate limits.
An exact remote exponent representation need not be affordable to materialize
as the corresponding original integer.

## Proofs and reproducibility

Start with [chapter 39](../../docs/chapters/39_collision_pell_and_analytic_boundaries.md),
then the [norm proof](../../docs/COLLISION_NORM_CLASSIFICATION.md),
[projection and bijection proof](../../docs/COLLISION_PROJECTION_CLASSIFICATION.md),
and [asymptotic proof](../../docs/COLLISION_ASYMPTOTICS.md).

```bash
python scripts/verify_collision_pell.py --check
python independent_checks/collision_pell/verify.py
node scripts/check_collision_explorer.cjs
python -m unittest discover -s tests -p 'test_collision*.py' -v
```

The main receipt is deterministic and source-bound. The independent verifier
uses original integer pairs, a separate Pell recurrence, literal formal
logarithms, and determinant/interpolation norms. The browser-core replay also
executes validation, UI handlers and export against a minimal DOM; this checks
behavior, not screenshot layout. The asymptotic does not provide a certified
finite-input error bar, and numerical observations do not prove analytic
continuation or historical originality.
