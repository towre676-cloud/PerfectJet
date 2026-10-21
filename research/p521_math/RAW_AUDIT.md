# Independent audit of the raw observer and provenance exclusions

The retained raw-observer receipt passes an independent standard-library checker,
`verify_raw_observer.py`. The checker imports neither the discovery module nor
its lattice-reduction code. Its determinant calculation uses fraction-free
Bareiss elimination; its inverse uses integer cofactors and the adjugate
identity, independently of the discovery module's rational Gauss-Jordan code.

## Raw observer: verified conclusions

All 70 retained bases satisfy their exact row congruences and have determinant
magnitude `M^4`, where `M=2^107-1`. Row membership alone would permit a proper
sublattice; the determinant condition rules that out. The checker independently
enumerates all 126 five-subsets of positions zero through eight and confirms
that subtracting each subset's first position gives precisely the 70 retained
patterns, without omissions or duplicates.

For each basis, all five coefficient bounds are recomputed using exact integer
minors and rational arithmetic. Every bound is strictly less than one. The
largest is exactly

```
59762387137465627635627395045544 /
162259276829213363391578010288127
```

which is less than `369/1000`. These are global collision-exclusion bounds,
not tests on selected states. If two trajectories have the same five symbols,
their state differences divided by `B=2^26` lie in the stated lattice and in
the box `[-floor((M-1)/B), floor((M-1)/B)]^5`. Multiplying by the verified inverse
makes every integral basis coefficient have absolute value less than one.
Consequently all differences vanish.

The arithmetic conditions `gcd(A,M)=gcd(B,M)=1` are also checked. The latter is
needed when dividing collision congruences by the output radix. The former makes
time translation bijective: agreement at normalized positions determines the
emitting state there, and multiplication by `A^(-t0) mod M` determines the state
at the original time zero. A primality assumption on `M` is unnecessary for this
argument.

## State convention and decoder alignment

The theorem concerns `y_i=x_i mod B`, followed by `x_(i+1)=A*x_i mod M`.
The input state is the first raw emitting state, before the first advance.
It is not automatically the historical constructor seed, a state before
warmup, or a state before a rejected source draw. The rejection wrapper needs
its own theorem.

The independent checker also implements the affine inverse directly from
`x_i=y_i+B*h_i`. Its tests recover the original time-zero state for every one
of the 126 five-subsets and each of five boundary/synthetic states, including
subsets whose first position is four. A separate comparison confirms that the
public decoder returns this time-zero state when its first four observations
are erased. Tests cover every admissible `(n,t,e)` budget for `5<=n<=9`, with
early observations erased and errors inserted afterward. There was no
off-by-one or emitting-state/time-zero alias in these checks.

## Sharpness and error/erasure frontier

The independent replay confirms the retained distinct-state pair shares its
first four output symbols. Its six-symbol words have Hamming distance two, and
the retained midpoint has distance one from each. Extending the same pair gives
these eight-symbol words:

```
26181305 18229658 376945 60485310 45393764 25145104 48496897 38292906
26181305 18229658 376945 60485310 13251489 13561652 44436642  6693766
```

They have distance four. The independently derived received word

```
26181305 18229658 376945 60485310 13251489 13561652 48496897 38292906
```

has distance two from both. Thus failure at four uncorrupted observations,
six observations with one error, and eight observations with two errors has
explicit replayable witnesses, beyond the information lower bound.

Any five-position agreement is impossible for distinct states, so the length
`n` code has distance at least `n-4`. Removing `e` known erasures leaves distance
at least `n-e-4`; `n>=5+2t+e` therefore suffices. Conversely, a code that corrects
`t` errors after arbitrary `e` erasures remains injective after puncturing an
additional `2t` positions. This would require
`M<=B^(n-e-2t)`. Since `M>B^4`, the same length threshold is necessary. The
result is an optimal observation-length guarantee within the stated windows;
it does not assert that the code cardinality attains equality in the Singleton
bound.

## Independent reproduction

From the repository root, without third-party packages:

```bash
python research/p521_math/verify_raw_observer.py
python -m unittest research.p521_math.tests.test_verify_raw_observer -v
```

All seven tests pass. They distinguish failed row membership, a proper
sublattice index, and a valid but insufficiently short unimodularly transformed
basis. They also reject altered rational bounds, missing/duplicate patterns,
wrong recurrence parameters, nonintegral schema numbers, changed sharpness
states, changed trajectories, and changed ambiguity data. The finite exact
certificate establishes the theorem; these tests additionally check the
implementation and corruption handling.

This audit establishes the stated specialization and its implementation. It
does not establish worldwide novelty, identify a P-521 construction seed, or
claim a general-purpose elliptic-curve discrete-logarithm break.

## Provenance exclusions: independent findings

The final retained receipts also pass independent arithmetic review:

| Receipt | Declared profiles | Exact exclusion witnesses | Outcome |
|---|---:|---:|---|
| `rotations.json` | 3,126 | 461,824 | No compatible state in the declared low-26 family |
| `portable-models.json` | 92 | 1,617 | No compatible state in the declared portable/wrapper families |

The rotation receipt covers every phase `0..520`, all three limb counts
`20,21,22`, and both assembly orders. Each phase means multiplication of the
canonical coordinate by `2^k mod (2^521-1)`, which is an invertible cyclic
521-bit rotation. This is a declared field-chart hypothesis, rather than
evidence that a historical program used that chart. The portable receipt
contains widths `26,30,31,32,50,62`, with the source configurations distinguished
from analytic or custom wrappers by the receipt's support labels.

For field reduction, write the raw integer as `W=L+2^521*H`, with
`0<=L<=P`, `0<=H<=2^(width*count-521)-1`, and `P=2^521-1`. The supported raw
lengths are below 1,042 bits, so `L+H=target+c*P` needs only `c=0,1`. Each carry
gives the complete necessary interval

```
max(0,target+c*P-Hmax) <= L <= min(P,target+c*P).
```

Extracting full words from these intervals after omitting the low uncertain
bits covers every possible raw assembly. Partial top words are omitted, and
the order conversion maps the retained full words back to the correct
consecutive source draws. Direct bit-window wrappers use only fully retained
words. For `RandomLen`, the source alters the entire last generated word by
masking it and forcing its top bit; omitting that word is a valid relaxation,
including when the requested bit length is a multiple of the word width.
`RandomLen(521)` cannot equal the 520-bit public coordinate by bit length alone.

The rotation dual proof is sound independently of basis reduction. If
`sum(q_i*A^t_i)=0 mod M`, then `sum(q_i*x_i)=k*M`. Exact signed box bounds
restrict `k` to an integer interval. Since `M=-1 mod 2^26` and
`x_i=y_i mod 2^26`, necessarily `k=-sum(q_i*y_i) mod 2^26`. Every retained
witness shows this residue has no representative in the interval. Arbitrary
dual rows are sufficient; no unverified basis-index claim is needed.

The portable dual proof is also sound. For low words write
`x_i=y_i+2^width*u_i`; for high words write
`x_i=2^(107-width)*y_i+u_i`. Both give a bounded affine lattice problem.
The checker verifies that each retained rational dual row is integral on all
homogeneous lattice generators, then derives its exact minimum and maximum
over the shifted coordinate box. The resulting interval contains no integer.
This is an all-state exclusion, including states outside the historical seed
interface's image.

Source rejection coverage is finite and certified. A rejected state is
`M-u`, where `1<=u<=M mod 2^width`. A positive integer relation
`sum(q_i*A^i)=0 mod M` would make any run of `len(q)` rejections satisfy
`sum(q_i*u_i)=0 mod M`, but the retained coefficients give
`0<sum(q)<=sum(q_i*u_i)<=r*sum(q)<M`, a contradiction. Consequently accepted
draws have gaps at most two for the supported widths through 50, and at most
three for width 62. The receipts enumerate every such gap pattern. Relaxing
the intermediate acceptance/rejection guards enlarges the candidate set, so
excluding every relaxed branch safely excludes the actual source loop.

The independent review rederived all interior branches and replayed all
461,824 rotation and 1,617 portable contradictions using only integers and
the standard library, without importing project math helpers. The provided
aggregate verifiers also pass under `python -S` with the lattice-reduction
and state-recovery functions replaced by functions that raise if called:

```bash
python -S research/p521_math/rotations.py --verify research/p521_math/results/rotations.json
python -S -m research.p521_math.portable_models --verify research/p521_math/results/portable-models.json
```

The 62 retained portable controls replay their claimed origins exactly. Their
offline receipts establish valid positive examples; the `complete` flags for
control inverse searches are discovery assertions, because the controls do
not retain full inverse-enumeration certificates. This distinction does not
affect the public-target exclusion proofs above.

The local NTL 1.5 archive's SHA-256 is
`c2d80c5293c824b16f89ac7e5e0aeb29e3996f8560b877c44858f41c43717e1c`, matching
the source record. Direct inspection confirms `zrandom` advances before
emitting and rejects states at or above `M-M mod radix`; `zrandomb` writes
draws into descending limb indices (most significant first), whereas
`zrandoml` writes ascending indices (least significant first) and then forces
the top bit. `ZZ.h` binds `RandomLen` to `zrandoml`. `MakeDesc.c` chooses the
largest even width no greater than `min(long_bits-2,double_precision-3)`, giving
30 on 32-bit long and 50 on 64-bit long with 53-bit double precision. The
receipt explicitly labels width-62 `RandomLen` as a parameterized FreeLIP
wrapper rather than an NTL 1.5 default. This audit does not turn a declared
configuration or source-family exclusion into proof of historical provenance.

The pinned FreeLIP header was also inspected locally and its recorded SHA-256
`6f71e7255155d2c9ee759cfd8c0de8c075e52fb14efba0ca99d4594370ea910f` confirmed.
It defaults to `NBITS=30`, uses 26 under `SINGLE_MUL`, and uses 62 under either
`ALPHA` or `ALPHA50`. In particular, `ALPHA50NBITS=50` is an internal arithmetic
parameter; that macro does not change this header's output word width to 50.
The width-50 model is justified independently by NTL 1.5's generated machine
configuration. The header rejects odd, nonpositive, or long-sized `NBITS`,
consistent with the receipt's distinction between width-31 analytic models
and an even width-32 custom configuration on 64-bit long.
