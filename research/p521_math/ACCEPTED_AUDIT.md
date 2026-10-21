# Independent audit of the accepted-output observer

The six-output theorem passes an independent standard-library verification. The audit implementation in `verify_accepted_observer.py` imports no other project module, reduction code, or external mathematics package. It reconstructs every lattice and every source guard from the public constants and checks the retained receipt directly. This is an independent implementation within this repository, not an external peer review.

The audited claim is precise: **six consecutive accepted 26-bit outputs uniquely identify the first accepted emitting state**, for the fixed recurrence `x <- A*x mod M`, with `M=2^107-1`, `A=3^121 mod M`, and rejection of raw states `x >= M-(M mod 2^26)`. Five accepted outputs do not suffice in the worst case. The claim does not identify an arbitrary state before the first call; some such states are observationally equivalent forever.

## Completeness of the case split

The rejection region consists of `M-u` for `1 <= u <= B-1`, with `B=2^26`. Two consecutive rejected states would give `v=A*u mod M` with both distances in that interval. For

```
q0 = 9944586160332543
q1 = 21699637613853658
```

the audit verifies `q0+A*q1 = 0 mod M` and `0 < q0*u+q1*v <= (B-1)*(q0+q1) < M`, which is impossible for a multiple of `M`. Thus every accepted-output gap is exactly one or two raw steps. Five gaps therefore give 32 possible six-output patterns.

All 32 equal-pattern collision problems are checked. For unequal patterns, the receipt checks all 961 ordered pairs whose left pattern contains a rejection. Any omitted ordered pair has an all-one left pattern and a rejecting right pattern; reversing it is among the checked pairs. The case split therefore covers every pair of valid trajectories, including cases with different rejection positions.

## Exact lattice and enumeration checks

For equal patterns, a collision gives a difference vector `z` with `|z_i| <= floor((M-1)/B)` and `z_i = A^t_i*z_0 mod M`. Each retained six-dimensional basis is checked for those congruences and determinant magnitude `M^5`. Membership together with the index proves it spans the full collision lattice. Exact rational inversion bounds all integer basis coefficients strictly below one in magnitude. The largest bound over all 32 patterns is

\[
\frac{2659994645194790114589299127948}
{162259276829213363391578010288127}<0.0164.
\]

For unequal patterns, the first rejected left raw state is `M-u`, with `1 <= u <= B-1`. The audit independently derives `s_i=alpha_i*u mod M` and

\[
z_i=beta_i z_0+c_i u\pmod M,
\qquad c_i=(alpha_i-beta_i alpha_0)B^{-1}\pmod M.
\]

The coordinates are `(2^55*u,z_0,...,z_5)`. Every retained basis row must have its first coordinate divisible by `2^55` and satisfy all five congruences. The determinant magnitude must equal `2^55*M^5`. This checks the scaling and full lattice index, so enumeration cannot silently omit a coset.

The inverse basis gives exact enclosing integer coefficient intervals. The audit recalculates every interval and enumerates every combination, then checks the original coordinate bounds. Across all 961 cross-pattern pairs this is 1,556 coefficient combinations and 304 lattice vectors in the coordinate boxes. Every potential distinct accepted-state pair is replayed through the actual rejection loop. The observed gap patterns and accepted outputs must match, including all emitting-state acceptance guards and all forced skipped-state rejection guards. No six-output collision survives. No heuristic search or numerical tolerance enters this check.

## Sharpness and state convention

The two distinct accepted states

```
126295752713511514371453877552714
81692446156502146450273842038346
```

are independently replayed. Their first five accepted outputs agree and their sixth outputs differ. This is an explicit counterexample to five-output global injectivity, not only a counting argument.

The first-call return map advances before emitting. Every accepted emitting state has its ordinary predecessor as a pre-call preimage. If that predecessor is rejected, its own predecessor is a second pre-call preimage. The no-consecutive-rejections lemma rules out any third preimage. Since multiplication by `A` is a permutation, exactly `B-1` emitting states have two preimages, and `M-2*(B-1)` have one. The receipt's concrete equivalence witness and these counts are replayed independently. A result claiming unique recovery of every pre-call state would therefore be false; the implementation correctly targets the first emitting state.

## Reproduce and limits

```bash
python research/p521_math/verify_accepted_observer.py
python -m unittest discover -s research/p521_math/tests -p 'test_verify_accepted_observer.py' -v
```

The audit tests reject proper sublattices, altered scaling, truncated coefficient intervals, missing cross-pattern coverage, duplicate patterns, and corrupted rejection data. The global proof comes from the exact lattice receipt, rather than from the finite test cases. The audit establishes the observer theorem under this fixed source model; it makes no historical-origin, elliptic-curve key recovery, or worldwide-priority claim.
