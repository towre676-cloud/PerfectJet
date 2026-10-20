# P-521 provenance laboratory

**Research release 0.1.0 · 20 October 2026 · PerfectJet**

This study proves that the published P-521 base-point x-coordinate cannot arise from the historical FreeLIP generator under any of six specified limb assemblies, even with an arbitrary internal state, arbitrary warmup, arbitrary earlier rejected coordinates, and the original low-limb rejection loop. It also supplies independently checkable exclusions for specified lrand48 byte assemblies of the public x and y coordinates. The P-521 base-point origin remains unexplained. These are public-parameter provenance results; no private key, discrete logarithm or cryptographic security break is claimed.

The central advance over an unsuccessful seed search is a finite arithmetic impossibility certificate. Lattice reduction discovers a short integer relation. A separate program verifies the relation, derives bounds over the entire hidden-state domain, and checks that the resulting interval contains no permitted integer. Its conclusion covers every state in the declared model rather than the seeds a search happened to try. Worldwide priority for this analysis is unverified.

## Verify in one command

From the repository root, or the extracted research release root, run:

```bash
python research/p521/run_research.py --check
```

Python 3.10 or later is sufficient. Verification requires no downloaded datasets, compiler, lattice library or network access. The command checks the retained all-state certificates, replays six previously explained base points, verifies P-521 curve membership and the standard order relation, checks primality of the field modulus by Lucas–Lehmer, and reproduces the already published P-521 curve seed. The standard subgroup order is imported from NIST; this study does not supply a new primality certificate for that order.

Run the research tests with `python -m unittest discover -s research/p521/tests -v`. A C++17 compiler is needed for the native scanner test; that test skips when no compiler is available. Optional inverse-discovery tests skip without fpylll. Certificate verification never needs either. `requirements-discovery.txt` pins the optional discovery dependencies. The exact-rational fallback in the FreeLIP discovery module can regenerate its certificates without dependencies, with a longer runtime.

## Exact findings and scope

| Result | Complete declared scope | Evidence |
|---|---|---|
| Source-faithful FreeLIP exclusion | Every state modulo 2^107−1; low26 rejection sampling; 20, 21 or 22 limbs; either limb order; final reduction modulo 2^521−1; target Gx | Six layouts, 128 possible seven-gap patterns per layout, 768 integer exclusion certificates |
| Simplified FreeLIP exclusion | Same layouts with every raw draw emitted | Six integer exclusion certificates |
| lrand48 byte traces | All 2^48 states for each 20-byte window in both 66-byte coordinates and either byte order | 188 independently checked dual certificates |
| lrand48 complete byte assemblies | Direct top-eight-bit output; 65 through 109 raw bytes; either byte order; final reduction modulo the P-521 prime; target Gx or Gy | 179 proof records, covering 180 assembly choices because the Gy/65-byte range proof covers both orders |
| Unsigned 31-bit words in 32-bit slots | Seventeen words, either word order, final reduction modulo the P-521 prime; target Gx or Gy | Two bit obstructions, independent of which RNG produced the words |
| Native recurrence fingerprints | Four-output bit windows, contiguous top31/top32 or top31 padded to32, both coordinate byte orders | 3,302 traces, 327,680,000 compatible first states enumerated, no match |
| Positive controls | Six previously explained historical base points; synthetic inverse recovery; forced rare FreeLIP rejection; known P-521 seed inverse | Separate replay and tests; historical discoveries credited to their authors |

The native top32 mode is an explicit hypothetical output slice of the 48-bit state; lrand48 itself returns 31 bits. A negative fingerprint scan only covers its listed traces. The complete byte-assembly exclusions have their own stronger proofs. The 110-byte and larger byte assemblies are outside the certified range, as are hashing, generator changes, interleaved unrelated draws, other limb widths, scalar multiplication of an underlying random point, and unspecified historical algorithms.

## Why P-521 exposes the hidden outputs

Write p=2^521−1. Twenty-two 26-bit limbs form an integer U<2^572. If U mod p=Gx, then U=Gx+qp=(q·2^521)+(Gx−q), with q at most 2^51. The published Gx has low52 bits 0xe7e31c2e5bd66, exceeding 2^51. Subtracting q therefore never borrows into bit52. Every possible raw candidate has the same bits52 through519. Those are eighteen complete low26 outputs, in a known order. The 20- and21-limb variants have analogous exact windows. The checker derives those windows from the public coordinate instead of trusting the receipt.

For the 22-limb, high-first layout the forced output window begins with

```
52041272 7041088 20607847 37669734 9328337 2737736 5128527 62202360
```

For the simplified no-rejection model, let M=2^107−1, A=3^121 mod M, and let x_i be the eight emitting states. The small integer row

```
(-3960, 1708, -6946, 982, 9113, -4528, -453, 4265)
```

satisfies sum(q_i A^i)=0 mod M. Therefore sum(q_i x_i)=kM for an integer k. Because 0≤x_i<M, that integer must lie in [−15886,16067]. Because x_i mod2^26 is the observed output and M≡−1 mod2^26, it must also satisfy k≡58656340 mod2^26. No integer satisfies both requirements. This is an exact contradiction, independent of the starting state. It is a compact illustrative proof for the simplified model, not a substitute for the original implementation's rejection cases.

## The historical rejection step matters

The original FreeLIP zrandom code discards a state at or above M−(M mod2^26) before returning its low26 bits. Such events are exceptionally rare, but dropping them would invalidate an all-state claim. A short positive dual relation proves that two rejected states cannot be consecutive. Thus adjacent accepted observations are separated by either one or two raw generator steps. The source-faithful receipt includes every one of the 2^7 gap patterns for the eight observations, and each has a checked impossibility certificate. The patterns deliberately form a relaxation: a two-step gap need not satisfy the rejection predicate inside the lattice search. Excluding this larger set also excludes the real source loop. The checker requires complete pattern coverage.

The certificate method writes x_i=y_i+2^26 u_i and retains the complete integer bounds on u_i. Recurrence congruences define an affine lattice. A dual integer functional maps all candidate states to multiples of a recorded denominator, while the observation box confines its value to a recorded interval. If that interval contains no multiple, no hidden state exists. LLL selects useful functionals; verification uses only integer identities and endpoint bounds. Failure to discover a certificate is reported as unresolved, never as an impossibility result.

## Relationship to the existing research

PerfectJet asks when observations determine a target and preserves the integer structure of coordinate changes. Singularity asks which distinctions an observation language can reveal. Here those ideas become a concrete generator-identification problem: recoverable output chunks determine an affine integer feasibility problem, and an explicit obstruction eliminates every hidden state of a declared historical model. This study imports classical lattice reduction and public PRNG formulas with attribution. It establishes a scoped new analysis and implementation within this project; it does not rename those classical algorithms as discoveries.

## Reproduce discovery and inspect the evidence

```bash
python -m pip install -r research/p521/requirements-discovery.txt
python research/p521/freelip_recovery.py --source-rejection --output /tmp/freelip-source.json
python research/p521/verify_certificate.py /tmp/freelip-source.json
python research/p521/lcg_forensics.py --with-lattice --output /tmp/lcg.json
python research/p521/verify_lcg_certificate.py /tmp/lcg.json
python research/p521/build_release.py
```

Lattice packages may discover different valid witness rows. The independent verifiers establish the mathematical conclusion without depending on a particular reduced basis. The native scan is reproducible separately; the certificate-only path checks its query coverage metadata and replayable positive controls, and states explicitly that it has not rerun the enumerated search.

The original FreeLIP source is pinned in `sources.json`, including its commit, blob, SHA-256 and rejection-loop semantics. No original source is redistributed. `results/` retains the full mathematical receipts. `verify_certificate.py` and `verify_lcg_certificate.py` were implemented separately from their corresponding discovery modules and import neither. Review notes and corruption tests accompany both. `build_release.py` creates a deterministic source ZIP, an embedded per-file manifest and a SHA-256 checksum.

## Public research frontier

The next task is to identify a historically supported successor generator or a transformation that survives these exclusions, then test it against the public coordinates with the same standards. An actual provenance solution must reproduce the entire coordinate and the historical selection procedure, retain its parameters, and admit independent replay. These results narrow that investigation; they do not identify the original program or prove it used a particular alternative.

Primary references are [NIST SP800-186](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-186.pdf), [Anthropic's seed and base-point reconstruction](https://www.anthropic.com/research/ecdsa-curve-origins), [Filippo Valsorda's independent seed verification](https://words.filippo.io/seeds-solved/), and the pinned original FreeLIP source linked in `sources.json`. Anthropic's previously published reconstructions are positive controls, not findings credited to this study.
