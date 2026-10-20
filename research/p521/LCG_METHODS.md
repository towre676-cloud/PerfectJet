# Exact LCG exclusions for P-521 public coordinates

This module studies the origin of the published P-521 base point. It does not recover private signing keys. Its input is the public coordinate pair, and its output is an exact exclusion of specified historical generator recipes. An exclusion is useful because it removes a complete model family, including every possible initial generator state, while preserving the hypotheses that were actually tested.

The POSIX generator has state modulus `2**48`, multiplier `0x5DEECE66D`, increment `11`, and recurrence `x_next = (a*x + 11) mod 2**48`. The module's output convention observes the current state first. For example, `outputs(state, 4, 31)` returns four consecutive top-31-bit observations, starting with `state >> 17`.

## Recovery API and its guarantees

`recover_top_bits_python(words, bits)` exhausts all `2**(48-bits)` states compatible with the first observation, then checks every later observation. It returns **all** compatible first-observed states for widths 28 through 48 and at least three observations. Empty means exact nonexistence within this model. To recover the state before that first observation, apply `previous(state)`. The C++ scanner implements the same finite enumeration in batches; every surviving state is replayed by the independent Python recurrence.

`recover_top_bytes_lattice(data)` constructs a lattice for a truncated affine recurrence and calls LLL followed by exact-CVP machinery from fpylll. It returns only recurrence-verified candidate states. This interface does **not** promise every state, and an empty result alone establishes no exclusion. It inversely reconstructs the already-published P-521 curve seed as a positive control: first-observed state `229179504894237`, timestamp `871002724`, candidate 1,136. The curve-seed provenance itself is credited to Anthropic's October 16, 2026 investigation.

`exclusion_certificate(data)` finds a short integer relation that contradicts all hidden states for a specified 20-byte top-eight-bit trace. `verify_exclusion(certificate)` checks that contradiction with ordinary Python integers and no lattice dependency. `verify_byte_assembly_exclusion(certificate)` additionally checks the Mersenne reduction argument described below. `verify_report(report)` checks all 188 exact trace proofs and the complete frozen assembly domain, including that the only uncovered lengths are the two 110-byte models. It does not rerun the separate native scanner.

## Why a small dual relation excludes all states

Write `x_i = a**i*x_0 + d_i mod M`, where `M = 2**48`, `d_0 = 0`, and `d_(i+1) = a*d_i + 11 mod M`. For an integer vector `v` satisfying `sum(v_i*a**i) = 0 mod M`, every compatible state must obey `sum(v_i*(x_i-d_i)) = 0 mod M`. The observed byte `y_i` puts `x_i` in the closed integer interval `[2**40*y_i, 2**40*(y_i+1)-1]`. Interval addition therefore bounds the entire relation. If that interval contains no multiple of `M`, no initial state can produce the trace.

LLL discovers short vectors `v`; verification only checks their modular relation and integer endpoints. The recorded calculations give such a contradiction for all 188 twenty-byte windows in the two 66-byte coordinates, in either byte order. The proof does not enumerate `2**48` states, and does not trust the LLL implementation to establish its conclusion.

## Complete direct-byte assembly exclusions

Let a raw integer `R` be assembled from consecutive top-eight-bit outputs, using either byte order, then reduced modulo `P = 2**521-1`. If the result equals a published coordinate `G`, necessarily `R = G + q*P = G-q+q*2**521`. The raw byte count bounds `q`. Choose a 160-bit byte-aligned window strictly below bit 521 whose lower discarded part of `G` is at least this maximum quotient. Subtracting `q` cannot borrow into that window, and adding `q*2**521` cannot reach it. Every admissible raw integer therefore has the same interior output trace. A dual contradiction for that trace excludes every raw integer and every initial state in the model.

The retained run excludes raw byte counts **65 through 109**, for each coordinate and either assembly order. The 65-byte `Gy` case is already impossible because the raw range is too small. These conclusions have 179 proof rows. The two 110-byte cases remain uncovered by this certificate construction. Output slices other than the top eight bits, intervening discarded outputs, hashing, other generators and scalar multiplication are outside this complete-model result.

## Reproduction

From the repository root, `python research/p521/lcg_forensics.py --verify research/p521/results/lcg_forensics.json` checks the retained exact certificates using the standard library alone. No compiler, fpylll installation, network connection or reference regeneration is required.

To regenerate the full deterministic receipt, install `research/p521/requirements-lcg.txt` in a virtual environment and run `python research/p521/lcg_forensics.py --with-lattice --output research/p521/results/lcg_forensics.json`. A C++17 compiler is needed for the native scanner. The canonical JSON excludes wall-clock values; `--timing` prints a separate runtime to standard error. Running without `--with-lattice` produces only the native finite-scan portion and the forward seed control. Optional dependency versions affect discovery machinery; retained certificates retain the same exact mathematical checker.

The native run covers 3,302 four-word traces across every bit offset, both coordinate byte orders, and top-31/top-32/padded-top-31 layouts. It enumerates 327,680,000 compatible first states and finds no matches. These are finite trace exclusions, distinct from the complete raw-byte assembly theorem. Synthetic inverse controls, known-seed controls, certificate corruption tests and an exhaustive check of the small 66-byte reduction quotients accompany the implementation.

The method's building blocks are classical truncated-LCG lattice analysis, elementary duality and a Mersenne carry identity. No worldwide novelty or general P-521 security weakness is asserted. The primary context is [Anthropic's curve-origin investigation](https://www.anthropic.com/research/ecdsa-curve-origins) and [Filippo Valsorda's independent seed verification](https://words.filippo.io/seeds-solved/).
