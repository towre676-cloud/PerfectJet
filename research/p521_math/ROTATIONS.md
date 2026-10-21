# P-521 field-chart search

The published P-521 base-point x-coordinate does not match the historical FreeLIP low26 sampler under any power-of-two field chart, for any internal state, in any of the six declared limb assemblies. The retained receipt covers all 521 chart phases, the original rejection loop, and every carry branch needed for reduction modulo the field prime. The actual base-point origin remains unknown.

This extends the direct-coordinate exclusions in `research/p521/` without changing that frozen release. It investigates a concrete representation hypothesis: perhaps a generated raw coordinate was stored in a Montgomery representation and decoded before publication. A positive match would have supplied a reproducible generator fingerprint; establishing historical origin would still require evidence that an implementation used the recovered recipe.

## Exact scope and result

Let `p = 2**521 - 1`, `M = 2**107 - 1`, and `A = 3**121 mod M`. The source sampler advances `state = A*state mod M`, discards states at or above `M - (M mod 2**26)`, and emits the low 26 bits of each accepted state. A raw integer is assembled from 20, 21, or 22 returned limbs, in either high-first or low-first order. For each `k` from 0 through 520, the search asks whether

```text
assemble(limbs) mod p = 2**k * published_Gx mod p.
```

Equivalently, decoding the assembled field element by multiplication by `2**(-k)` must reproduce the entire published x-coordinate. The source constants and rejection semantics are those pinned and reviewed in `research/p521/sources.json` and `research/p521/FREELIP_REVIEW.md`.

| Checked family | Exact retained count |
|---|---:|
| Power-of-two phases | 521 |
| Limb layouts per phase | 6 |
| Phase/layout profiles | 3,126 |
| Profiles excluded by the raw integer range | 534 |
| Remaining profiles | 2,592 |
| Carry-prefix branches in the remaining profiles | 3,608 |
| Rejection-gap patterns per branch | 128 |
| Verified modular contradictions | 461,824 |
| Shared short relation rows | 1,024 |
| Full-coordinate matches | 0 |
| Unresolved profiles or branches | 0 |

The first phases tried were 23, 55, and 25. They are the Montgomery exponents obtained by rounding a 521-bit modulus up to 17 32-bit limbs, nine 64-bit limbs, or 21 26-bit limbs: `544 mod 521 = 23`, `576 mod 521 = 55`, and `546 mod 521 = 25`. These are mathematically natural representation hypotheses, not evidence that a historical P-521 implementation used those representations. The search then covers every phase, so choosing other limb-aligned Montgomery radices that are powers of two cannot evade this particular exclusion.

## Why the check covers every state

Multiplication by `2**k` modulo `2**521-1` is a cyclic rotation of the canonical 521-bit field word. Moreover, `2**521 = 1 mod p`, and no smaller positive exponent gives one: `0 < 2**k-1 < p` for `0 < k < 521`. Thus the 521 phases cover the whole subgroup of power-of-two field factors.

For each rotated target `T`, the checker enumerates every possible interior-limb prefix of a raw assembled integer `W` satisfying `W mod p = T`. Write `W = H*2**521 + L`, with `0 <= L <= p`. For 21 and 22 limbs, `H` is at most `2**25-1` or `2**51-1`. Therefore `H+L` is either `T` or `T+p`. Projecting both resulting intervals for `L` onto complete limb boundaries yields all possible interior prefixes, including a possible subtraction borrow. Some targets have two branches; both are retained and checked. For 20 limbs, `W < 2**520`, so an out-of-range target is impossible directly.

The first eight forced interior outputs are enough for every exclusion in this receipt. The source's existing positive integer relation proves that two rejected raw states cannot be consecutive. Consequently the eight accepted states have one of exactly `2**7` raw recurrence-gap patterns, each gap being one or two. The search checks all patterns. For an exclusion it relaxes the rejection predicates, allowing even gaps that the real source would not take; excluding that larger set also excludes the source itself.

For one gap pattern, let `t_i` be its cumulative raw times, and let `y_i` be the eight forced low26 outputs. Each retained integer row `q` satisfies

```text
sum(q_i * A**t_i) = 0 mod M.
```

If corresponding emitting states `x_i` existed, their recurrence would give `sum(q_i*x_i) = K*M`. Because `0 <= x_i <= M-1`, the quotient `K` lies between

```text
ceil((M-1)*sum(min(q_i, 0))/M)
floor((M-1)*sum(max(q_i, 0))/M).
```

Also `M = -1 mod 2**26` and `x_i = y_i mod 2**26`, so `K = -sum(q_i*y_i) mod 2**26`. Each certificate selects a row for which this residue has no representative in the quotient interval. This is an exact integer contradiction, independent of the initial state. Lattice reduction discovers the rows; verification checks their recurrence relation and contradiction using integer arithmetic only.

Covering every state also covers arbitrary warmup and any number of earlier rejected whole-coordinate candidates under this same sampler. Taking either square root of a candidate point does not change its x-coordinate. These observations do not extend the result to a different generator, output slice, limb contract, nonlinear transformation, or arbitrary group operation.

## Positive controls and full replay

The tests generate valid synthetic P-521 points from hidden states and chart phases. Only the public x-coordinate is passed to the inverse search, which scans all 521 phases. It recovers the phase and the state immediately before the matching coordinate. Every recovered candidate must replay the actual rejection predicates, every assembled limb, field reduction, and inverse chart conversion. A surviving observation fingerprint without this full replay is not a match.

Three controls cover an ordinary state at phase 173, a constructed rare rejection inside the forced observation window at phase 91, and three rejected whole-coordinate candidates before the first finite point at phase 4. The point-selection replay verifies every earlier nonsquare candidate, the selected x-coordinate, and the chosen sign of its square root. The rare-rejection control recovers a genuine two-step source gap. These are satisfiable algorithm checks, not claims about the published point's history. For a real match the earlier whole-point selection history cannot generally be inferred from a coordinate alone; it would need separate evidence and replay.

## Reproduction

From the repository root, verify the retained receipt with the Python standard library:

```sh
python research/p521_math/rotations.py --verify research/p521_math/results/rotations.json
python -m unittest research.p521_math.tests.test_rotations -v
```

Regenerate the search:

```sh
python research/p521_math/rotations.py --output research/p521_math/results/rotations.json
```

Discovery uses the existing exact-rational lattice reduction fallback. Installing the optional dependencies pinned in `research/p521/requirements-discovery.txt` makes discovery faster. Verification of the retained public-target receipt uses no lattice library, external data, or network access. `--priority-only` produces a deliberately limited three-phase receipt; its verifier reports that it does not cover the whole orbit.

The module's checker validates the declared phase/layout coverage and reports whether the entire orbit and all six layouts are present. The frozen receipt fixes the public target and complete coverage; the tests enforce both. The search and checker share the existing interior-window implementation, so they are not separate independent implementations. Corruption tests reject changed targets, relations, prefixes, gap coverage, source-loop proofs, and match summaries.

The contribution is a complete, reproducible exclusion of this representation family. It supplies neither a P-521 origin reconstruction nor a private-key or discrete-logarithm result.
