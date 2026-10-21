# Historically grounded word widths and packing models

The retained receipt excludes **92 explicitly declared models of the P-521 public x coordinate**, using **1,617 exact integer dual certificates**. Every model is complete, and none produces a candidate origin. **62 synthetic positive controls recover their known initial states** and retain all emitting states for independent replay. These results constrain particular public parameter-generation recipes; they do not recover a private key or weaken P-521.

The useful advance is that the word-width choices now follow historical source, rather than assuming that the already studied 26-bit build was universal. The search also treats a newly recovered, pre-August-1997 NTL exact-length generator separately from modular bounded generation.

## Which widths have primary-source support?

| Word bits | Source evidence | Interpretation |
|---|---|---|
| 26 | Archived FreeLIP `lip.h` lines 589–595; NTL 1.5 `SINGLE_MUL` | Floating-point multiplication configuration; the previous release already studied its modular models |
| 30 | FreeLIP default branch, lines 589–595; Shoup's factorization implementation paper, §8.2; NTL 1.5 `MakeDesc.c` lines 139–146 | A historically justified default, not an arbitrary alternative |
| 50 | NTL 1.5 `MakeDesc.c` lines 139–146, using 64-bit `long` and 53-bit double precision | A distinct historical NTL configuration; the FreeLIP macro named `ALPHA50` actually sets its radix width to 62 |
| 62 | FreeLIP `ALPHA` and `ALPHA50` branches, lines 533–577 | Explicit historical architecture configurations; this is not NTL 1.5's default 64-bit width |
| 31 | FreeLIP header rejects odd `NBITS`, lines 646–649 | Included as a mathematical output variant only; not a valid build of this header |
| 32 | Header permits even `NBITS` below the machine-long width | Custom 64-bit configuration only; not a documented default |

The [pinned FreeLIP header](https://github.com/oreparaz/crypto-archeology/blob/1de75d5681e620a49f2404c5760075f3e0664413/freelip_1.0/lip.h) has SHA-256 `6f71e7255155d2c9ee759cfd8c0de8c075e52fb14efba0ca99d4594370ea910f`. The [author-distributed NTL 1.5 archive captured on 1997-08-01](https://web.archive.org/web/19970801214429id_/http://www.cs.wisc.edu/~shoup/ntl/ntl-1.5.tar.Z) has SHA-256 `c2d80c5293c824b16f89ac7e5e0aeb29e3996f8560b877c44858f41c43717e1c`. Its `lip.c` contains bounded generation at line 4694 and exact-length generation at line 4716. Shoup's [implementation paper](https://www.shoup.net/papers/factorimpl.pdf), §8.2, independently identifies the 30-bit default and 26-bit alternative. Original historical source is not redistributed here.

These sources establish available implementations. They do not establish which machine or program generated P-521's base point.

## The finite model family

All models use the archived multiplicative generator

\[
M=2^{107}-1,\qquad A=3^{121}\bmod M,\qquad x_{i+1}=Ax_i\bmod M.
\]

The source sampler for a word width \(w\) rejects states at or above \(M-(M\bmod2^w)\), then returns the low \(w\) bits. The receipt covers:

* **54 low-word models:** widths 30, 50 and 62; counts \(\lceil521/w\rceil-1\), \(\lceil521/w\rceil\), and \(\lceil521/w\rceil+1\); both limb orders; reduction modulo \(p=2^{521}-1\), retention of the low 521 bits, or retention of the high 521 bits. The largest count with high limbs first and modular reduction is the original `zrandomb` recipe. The other layouts are declared wrappers.
* **18 high-word models:** the same three widths and largest count, both orders, and the three packing rules. They emit the high \(w\) bits of each raw state with no rejection. These are analytic variants, not the original source sampler.
* **12 width-31/32 models:** largest count, both orders, three packing rules, and the low-word rejection rule. Their limited historical status is recorded above and in every profile.
* **8 exact-length models:** NTL 1.5 `RandomLen(520)` and `RandomLen(521)` at widths 26, 30, 50 and 62. The source fills low limbs first, masks the final limb and forces the requested top bit to one. Width 62 is explicitly labeled as this wrapper at FreeLIP's Alpha width, rather than an NTL 1.5 default.

The published x coordinate has bit length 520. Consequently `RandomLen(521)` cannot equal it, regardless of state. For `RandomLen(520)` the altered last word is omitted from the observations; all untouched lower full words remain constrained. This distinction avoids treating an overwritten top bit as if the generator emitted it.

For modular packing, write \(W=L+2^{521}H\). Since \(2^{521}\equiv1\pmod p\), a target constrains \(L+H\) to one of two exact intervals before a possible subtraction of \(p\). Enumerating the interval prefixes gives every possible unaffected full-limb observation block. The bit-window models extract only limbs entirely inside the retained window. Edge-case tests include zero and all-one words.

## An exact rejection bound for the 62-bit source

For widths up to 52, a positive modular relation with two terms proves that two rejected states cannot occur consecutively. Width 62 needs a different bound: two consecutive rejections really are possible.

For three raw states, the positive vector

\[
q=(6610084184,\ 40481587063,\ 44879765762)
\]

satisfies

\[
q_0+Aq_1+A^2q_2\equiv0\pmod M,
\qquad (2^{62}-1)(q_0+q_1+q_2)<M.
\]

If three consecutive states were rejected, their distances \(t_i=M-x_i\) would lie in \([1,2^{62}-1]\), and \(\sum q_it_i\) would be a positive multiple of \(M\) strictly below \(M\). This is impossible. Accepted outputs therefore have raw gaps in \(\{1,2,3\}\), and the receipt covers every such gap pattern.

The bound is tight: \(t_0=3389828199694795\) and \(t_1=5924008525679449\) satisfy \(At_0\equiv t_1\pmod M\); both distances are small enough to make \(M-t_0\) and \(M-t_1\) rejected. The synthetic suite includes a seed forcing exactly those two consecutive rejections before an accepted output. This is a mathematical property of this specified generator and sampler; no novelty-priority claim is made.

## What each exclusion proves

For low observations \(y_i\), write \(x_i=2^wu_i+y_i\); for high observations, write \(x_i=2^{107-w}y_i+u_i\). Each case gives an explicit integer box for \(u\) and an affine lattice \(u=d+L\), with raw transition exponents determined by the declared gaps.

A retained dual certificate contains an integer vector \(q\) and positive denominator \(D\). Verification checks that every lattice generator has dot product divisible by \(D\), recomputes the exact minimum and maximum of \(q\cdot(u-d)\) over the box, and proves that this interval contains no multiple of \(D\). This excludes **every one of the \(2^{107}-1\) residue states**, including zero, for that observation branch. LLL only discovers certificates. It is not trusted by their verifier.

The complete receipt verifier additionally re-derives the fixed target, all 92 profiles, every forced-prefix observation block, and every raw-gap pattern. It rejects omitted or duplicated branches, certificates attached to a different target/output model, and altered positive replays. A search budget exhaustion would be reported as unresolved; none occurs in the retained target receipt.

The positive controls have a narrower offline guarantee. The executed generation run recovered their known initial states; the retained receipt lets the offline checker replay those origins and verify every emitted state, word and assembled target. It does **not** retain an independently checkable proof of completeness or uniqueness of each control's inverse enumeration. Their `complete` flags record the generation run's outcome. This limitation does not affect completeness of the 92 target exclusions, whose entire coverage and dual proofs are independently verified.

## Reproduce and verify

From the repository root, verify the retained receipt using only Python's standard library:

```bash
python -m research.p521_math.portable_models --verify research/p521_math/results/portable-models.json
```

Regenerate it with optional `fpylll` acceleration, or the existing exact rational LLL fallback:

```bash
python -m research.p521_math.portable_models
python -m unittest research.p521_math.tests.test_portable_models -v
```

Eight tests cover the complete retained receipt without LLL, missing models/branches, changed targets and rebound certificates, changed dual bounds, altered positive replays, width-62 rejection tightness, bit-window/carry boundaries, exact-length top-bit handling, high-word recovery, and budget reporting.

The remaining provenance question is still open. These results reject the listed FreeLIP/NTL recipes for the exact published x coordinate. Other multipliers, RNG families, output transformations, elliptic-curve transformations, and undocumented generators remain outside this receipt.
