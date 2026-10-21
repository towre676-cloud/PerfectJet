# Sharp FreeLIP recovery and the P-521 provenance search

The strongest result of this follow-up is a **sharp state-recovery theorem for the historical rejection sampler**. Six consecutive returned 26-bit words determine its first emitting state for every possible state. Five words do not: two explicit states produce the same first five returned words and different sixth words. An independent standard-library checker verifies the complete finite proof, and a constructive decoder recovers the state from six words.

The published P-521 base point's origin remains unknown. This directory also records a complete search of power-of-two field representations and source-supported integer-generation variants. Those searches supply exclusions, not a provenance reconstruction. They concern public parameter generation, not recovery of signing keys or a discrete-logarithm attack.

## Exact recovery results

All the recovery statements fix

\[
M=2^{107}-1,\qquad A=3^{121}\bmod M,\qquad B=2^{26},
\qquad F(s)=As\bmod M.
\]

A raw observation is `s mod B`, followed by one recurrence step. The historical accepted interface advances the recurrence until the state is below `T = M - (M mod B)` and returns that state's low word. These interfaces have different sharp observation thresholds.

| Target and observation contract | Proven guarantee | Sharpness |
|---|---|---|
| Current raw state, fixed consecutive steps | Five outputs determine every state | Two states agree in their first four outputs |
| Raw state with corrupt observations | For `5 <= n <= 9`, recover with `t` arbitrary symbol errors and `e` known erasures when `n >= 5 + 2t + e` | Five clean, seven with one error, nine with two errors are optimal worst-case lengths |
| First accepted emitting state, consecutive returned words | Six outputs determine every state; actual forced rejections are included | Two states agree in five accepted outputs |
| Raw state before the first accepted call | Six outputs determine its exact one- or two-element preimage set | Some pairs remain indistinguishable even with infinitely many future returned words |

For the accepted collision, the distinct emitting states

```
126295752713511514371453877552714
81692446156502146450273842038346
```

both return

```
53806666 63148225 39235656 43695102 27978396
```

Their sixth returned words are `37823841` and `63084375`. The first trajectory crosses a rejected state before its fifth return; the second does not. Thus a proof for a fixed raw observation schedule cannot establish the accepted-interface threshold by itself.

The six-output proof handles this directly. A positive integer relation proves that rejected states cannot be consecutive, so there are 32 five-gap patterns. Exact collision-lattice bases prove injectivity within each pattern. For different patterns, orient the pair so that the left trajectory has a rejection and anchor that rejected state as `M-u`, where `1 <= u < B`. This replaces an unrestricted 107-bit state parameter with a bounded 26-bit rejection distance. Complete exact coefficient intervals cover every possible collision. The retained proof covers all 961 required oriented cross-pattern pairs; its 1,556 coefficient tuples contain 304 vectors in the relaxed state-difference boxes, and full source guards eliminate every one. These are certificate enumeration counts, not sampled states.

The pre-call ambiguity is structural. For an accepted emitting state `e`, `F^-1(e)` is always a possible pre-call state. There is one additional pre-call state, `F^-2(e)`, exactly when `F^-1(e)` is rejected. There are precisely `B-1` double fibers and `M-2(B-1)` singleton fibers. Since the six-word theorem identifies `e`, these are exactly the full future-output equivalence classes of the pre-call states for this interface.

The raw error-correction theorem follows from a stronger observation result: every five positions among raw times zero through eight determine the state. It implies minimum Hamming distance at least `n-4` for windows through length nine. The standard Singleton counting argument proves the corresponding length lower bound, and explicit ambiguity witnesses realize the failures at four clean, six one-error, and eight two-error observations. These are errors in entire 26-bit symbols.

## Use the constructive decoders

Run this from the repository root:

```python
from research.p521_math.accepted_observer import (
    accepted_trace, first_call_preimages, recover_accepted,
)
from research.p521_math.raw_observer import decode, raw_outputs

emitting = 126295752713511514371453877552714
returned = accepted_trace(emitting, 6)["outputs"]
assert recover_accepted(returned) == emitting
possible_pre_call_states = first_call_preimages(emitting)

raw_state = 871002724
received = raw_outputs(raw_state, 9)
received[2] ^= 12345
received[7] ^= 67890
assert decode(received, errors=2)["state"] == raw_state
```

The decoders and retained-certificate verification need only the Python standard library. They reject impossible observations rather than selecting an unsupported state. Unknown arbitrary skipped draws, unknown recurrence constants, and other output functions are outside these contracts.

## Historical investigation and coordinate search

The [historical source account](HISTORICAL_LEADS.md) pins an NTL 1.5 author archive captured on August 1, 1997. Its actual recurrence and integer-generation wrappers give contemporaneous hypotheses to test. This is firmer evidence than projecting a later NTL generator backward in time. An archive capture establishes availability by that capture date; it does not establish which software a curve designer used.

The [field-chart search](ROTATIONS.md) checks whether the entire published `Gx` can be reproduced after decoding any power-of-two field representation. Since the field prime is `2^521-1`, the 521 possible factors act as cyclic rotations of the field word. Every phase is covered for the six specified low26 limb assemblies, with original source rejection, all internal states, and every necessary modular carry branch. There is no match. Blinded synthetic controls recover complete valid points, hidden phases and states, including forced rejection and prior rejected point candidates.

The [portable-source models](PORTABLE_MODELS.md) separately test the historically supported limb widths and recovered integer wrappers. Actual source configurations and analytic variants are labeled separately. Each retained exclusion is checked by an exact integer contradiction. Known-origin controls replay the full wrapper, including partial top limbs and rejection predicates.

An all-state exclusion can reject a specified generator/output/conversion family decisively. It does not measure how close a different historical recipe is to being found. The remaining positive target is a reproducible recipe that yields the entire published point, supported by historical evidence. No such recipe was recovered here.

## Verify the claims offline

From the repository root:

```bash
python research/p521_math/verify_all.py
python -m unittest discover -s research/p521_math/tests -v
```

The combined verifier binds the retained searches to the actual P-521 target and complete declared coverage. Raw and accepted recovery have additional independent checkers that do not import their discovery implementations. Lattice reduction is used to discover certificates; verification checks exact arithmetic, lattice membership, full determinant index, coefficient intervals, pattern coverage, rejection guards and ambiguity witnesses. Passing synthetic tests supports the code; the certificates establish the global finite statements.

Read the [raw proof](RAW_OBSERVER.md), [raw independent audit](RAW_AUDIT.md), [accepted proof](ACCEPTED_OBSERVER.md), and [accepted independent audit](ACCEPTED_AUDIT.md) for assumptions and proof details. The construction specializes classical truncated-congruential lattice reconstruction and coding arguments. Worldwide priority of these exact specializations has not been established.

A primary reference for recovering truncated variables from linear congruences is Frieze, Håstad, Kannan, Lagarias and Shamir, [*Reconstructing Truncated Integer Variables Satisfying Linear Congruences*](https://doi.org/10.1137/0217016), SIAM Journal on Computing 17(2), 262–280 (1988). The exact constants, global bounds, rejection-interface collision, complete six-return certificate and implementation here are specific specializations.

The earlier standalone release in `research/p521/` remains a separate, versioned checkpoint. This follow-up has its own source, receipts and automated offline replay.
