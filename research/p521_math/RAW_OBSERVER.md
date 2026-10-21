# A sharp raw-state observer and its error-correction frontier

This account concerns the fixed historical recurrence

\[
x_{i+1}=Ax_i\pmod M,\qquad M=2^{107}-1,\quad
A=3^{121}\pmod M,\qquad y_i=x_i\pmod B,\quad B=2^{26}.
\]

The target is the current raw emitting state, and every observation is one raw step after the preceding observation. Rejection sampling, unknown warmup, arbitrary skipped observations and P-521 base-point identification are separate problems. The method uses classical lattice reconstruction and coding bounds; worldwide priority of this exact specialization is unverified.

**Theorem.** Every five observation positions among times zero through eight determine the raw state uniquely. Five symbols are necessary. Within windows of five through nine consecutive raw outputs, a decoder uniquely recovers the state under any `t` arbitrary output-symbol errors and any `e` known erasures whenever

\[
n\ge 5+2t+e.
\]

This length threshold is optimal for the stated worst-case guarantee. In particular, five uncorrupted observations, seven observations with one arbitrary error, and nine with two arbitrary errors suffice, and the respective lengths cannot be reduced. These are 26-bit symbol errors, not only individual flipped bits.

## Global injectivity proof

Suppose two trajectories agree at five positions `t0<...<t4`. Dividing their state differences by `B` gives integers `z_i` with

\[
z_i\equiv A^{t_i-t_0}z_0\pmod M,\qquad
|z_i|\le U=\lfloor(M-1)/B\rfloor.
\]

The corresponding collision lattice has row generators `(1,A^d1,...,A^d4)` and `M e_i` for `i=1,...,4`. It has determinant magnitude `M^4`. For each normalized five-position pattern, the receipt gives an integer basis `R`. The checker verifies that every row satisfies the lattice congruences and that `|det R|=M^4`; therefore it is a basis of exactly this lattice, without trusting LLL or accepting a proper sublattice.

Write the collision vector as `z=cR`, with integer coefficients `c`. Exact inversion yields

\[
|c_j|=|(zR^{-1})_j|\le U\sum_i|(R^{-1})_{ij}|<1.
\]

Every coefficient is thus zero and the trajectories coincide. Seventy normalized certificates cover all 126 five-subsets of the nine-position window; time translation accounts for repeated normalized patterns. The largest verified bound is

\[
\frac{59762387137465627635627395045544}
{162259276829213363391578010288127}<0.369.
\]

The consecutive five-position pattern has largest bound below 0.086. Four observations can take at most `B^4=2^104` values, fewer than the `M=2^107-1` states. Consequently five is the exact global minimum.

## Constructive sharpness

Two concrete states are

```
122758394145529637777561808240313
50140205173557533948874584981177
```

Their six-output words are

```
26181305 18229658 376945 60485310 45393764 25145104
26181305 18229658 376945 60485310 13251489 13561652
```

The first four symbols agree. The six-symbol words differ in exactly two positions. Replacing the first word's fifth symbol with `13251489` produces a received word one error away from both states. Thus six observations really can be ambiguous under one error; this is an explicit collision, not merely an information count. The receipt retains and directly replays these states.

The same states extend with symbols `48496897 38292906` and `44436642 6693766`, respectively. Their eight-symbol words differ at exactly four positions. Taking the first word and replacing its fifth and sixth symbols with those of the second word gives a received word exactly two errors from both states. Thus eight observations can be ambiguous under two errors as well. Direct recurrence replay checks this witness in the tests and independent audit.

## Error and erasure proof

Any two distinct state words can agree at at most four observed positions, because agreement at five positions contradicts global injectivity. A length-`n` observation word therefore has minimum Hamming distance at least `n-4`. After `e` known erasures it has distance at least `n-e-4`. Unique correction of `t` errors follows from `n-e-4>=2t+1`.

Conversely, any code correcting `t` errors after `e` erasures requires distance at least `2t+1` on the unerased positions. Puncturing an additional `2t` positions must leave distinct codewords. The output alphabet has size `B`, so the `M` states would then need `M<=B^(n-e-2t)`. Since `M>B^4`, this requires `n-e-2t>=5`. The claimed length threshold follows. This is the standard Singleton/information argument, specialized here; it is not a new general coding theorem.

The constructive decoder selects five unerased positions, solves the resulting exact affine lattice box, then replays the candidate against every available observation. It accepts only a state within the declared error budget. The global distance theorem ensures that two accepted states cannot exist. Under the stated corruption bound, some five selected positions are clean, so the decoder finds the actual state.

## Reproduce

From the repository root, verify the mathematical receipt offline with

```bash
python research/p521_math/raw_observer.py --verify research/p521_math/results/raw-observer.json
python -m unittest discover -s research/p521_math/tests -p 'test_raw_observer.py' -v
```

No third-party package is needed for verification or inverse decoding. Discovery can be rerun with `python research/p521_math/raw_observer.py --generate`; it uses the earlier project's exact rational LLL fallback or optional fpylll. The checker independently implements rational inversion, determinant checks, exact box bounds, full pattern coverage and the sharpness replay. Altering the basis, determinant index, bounds, recurrence, pattern coverage or sharpness data causes rejection.

The tests cover every five-subset of nine for boundary and synthetic states, every single-error location in seven, every pair of error locations in nine, every four-erasure pattern in nine, mixed errors and erasures, explicit ambiguous six- and eight-symbol data, and corrupted certificates. Passing these tests supports the implementation; the finite lattice certificate supplies the global proof beyond the chosen synthetic states.
