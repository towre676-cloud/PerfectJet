# NTL source recovery audit and remaining hypotheses

This follow-up did not recover an authentic NTL 2.0 or 3.0-era distribution. It preserves the successful NTL 1.5 recovery and adds execution against those authenticated source bytes. The archive search and the C replay answer different questions: the first asks which historical program is available to inspect; the second tests whether a recovered program agrees with its mathematical model. Neither supplies a P-521 base-point origin.

The machine-readable search records are [author-search.json](results/author-search.json) and [distribution-search.json](results/distribution-search.json). Each distinguishes a retrieved listing, a failed request, a guessed endpoint and an actual source artifact. Response hashes identify received bytes; an HTTP Date or a current directory timestamp is not a historical release date. Search-tool references are session bookkeeping; the recorded public URLs are the independently revisitable references. No missing source archive is assigned an invented hash.

## What the bounded archive search established

The author's [current download index](https://libntl.org/download.html) reaches back to the linked `ntl-5.1a.tar.gz`, dated 8 June 2001. The [official repository's initial commit](https://github.com/libntl/ntl/commit/c96ef935be00aaab6b8017d08654c8a217c92692) imports NTL 11.4.3 in December 2020. Neither provides source for the requested versions. The preserved [NTL 2.0 announcement](https://ns1.omnitech.net/data/Books/Math/97/NTL/) still identifies the author, predecessor 1.7 and original Wisconsin directory, but its retrieved text is not the distribution.

The checked Debian snapshot version list starts at 5.4.2-1; the inspected hamm and slink math-source listings did not identify NTL. The inspected FreeBSD distfiles listing starts its NTL entries at 5.3.1. FreeBSD's [initial math/ntl port](https://cgit.freebsd.org/ports/commit/math/ntl?id=dd8dce73978efd7b52d35f7877d0b9232a8cd966), dated 10 July 2000, names 4.1a. These observations concern the exact queried lists and paths, not every historical copy in those projects.

Additional inspected listings include MacPorts, FUNET mathematical and cryptographic software, Netlib, and ibiblio. They yielded no authenticated target distribution. Several Internet Archive, NetBSD and mirror requests failed or were inaccessible. One CDX query returned an empty list; that answer only concerns that query and service response. A failed request or an empty query result cannot establish that an archive never existed. The ledger retains those leads as unresolved access, rather than declaring them exhausted.

## Version-specific boundary

The [author's changelog](https://libntl.org/doc/tour-changes.html) distinguishes the first public 3.0 release, 3.0d, from prereleases 3.0a–c. It records a `RandomBits` correction in 3.0e affecting `ZZ.c` and `lip.c`, another correction in 3.0f affecting `lip.c`, and a generator replacement plus byte conversions in 3.5a. The undated entries do not specify the old bugs, their exact fixes, or the replacement algorithm's earlier availability.

| Historical family | What is supported now | What remains unresolved |
| --- | --- | --- |
| 1.5 | Authenticated archive; exact integer sampler and big-integer wrappers; finite C conformance replay; existing all-state coordinate exclusions | Whether this software was used by the curve designers; other transformations and point-selection procedures |
| 1.7 and 2.0 | Author's transition records; dated 2.0 announcement | Actual random-related source, seed semantics, widths, overloads, integer assembly and presence or absence of `RandomBits` |
| 3.0a–c | Identified by author as prereleases | Source, dates, distribution status and random-generation semantics |
| 3.0d | Identified by author as the first 3.0 release | Pre-fix `RandomBits` implementation, other wrappers and state consumption |
| 3.0e | First documented `RandomBits` correction | Exact corrected behavior and remaining bug; source and machine configurations |
| 3.0f | Second documented `RandomBits` correction; historical author-page lead | Actual corrected source, seed handling, rejection and conversion semantics |
| 3.1a/b | Author change records and preserved 3.1b page lead | Actual RNG source and whether its output stream matches 3.0f |
| 3.5a | Author explicitly records generator replacement and new byte conversions | Authenticated source, release chronology, precise replacement and any relevance to base-point selection |

An existing arithmetic exclusion transports to a later release only after proving that the later implementation satisfies the same declared generator, output and conversion contract. Similar names, backward compatibility claims, or silence in a changelog do not establish stream equivalence. Conversely, the mathematical theorem remains valid for its explicit model even while attribution to another version is unresolved.

The August 1997 coefficient-seed timestamp does not establish the date on which the base point was selected. A later generator cannot be eliminated merely because it postdates that coefficient seed. Historical availability, bitstream equivalence and attribution to the actual parameter-generation program remain separate obligations.

## Source execution and mathematical coverage

The [source replay program](ntl15_replay.py) accepts only the already authenticated compressed NTL 1.5 archive, checks its size and SHA-256 before decompression, and verifies every selected source member before compilation. It builds an independent driver around unchanged historical integer code. Original source and the original archive are not redistributed. The retained [numeric receipt](results/ntl15-source-replay.json) records the compiler, flags, driver digest, source digests, machine descriptors and all fixed test cases.

The replay compares integer outputs and final internal states, so an extra or omitted draw is observable even when the integer result is unchanged. Cases include full signed arbitrary-precision seeds, zero-residue normalization, lazy default initialization, bounds around a radix power, zero and one boundaries, partial top limbs, 520/521-bit requests and states forced exactly onto the rejection threshold. In particular, scalar `RandomBnd(1)` delegates to `zrandom(1)` and consumes a draw, while big-integer `RandomBnd(ZZ(1))` returns zero without drawing. Overload identity is part of the model.

The original machine-description program generates the native 64-bit-long, 53-bit-double, 50-bit-radix configuration. Widths 26 and 30 are explicitly recorded as radix emulations on that host. They do not claim execution of an original 32-bit ABI or the `SINGLE_MUL` multiplication path. The signed-wrap compilation choice is recorded. Finite successful replay is conformance evidence for those builds and cases, not an all-state proof of arbitrary historical C behavior.

Offline receipt validation recomputes every expected value and state and rejects missing or altered cases. It does not re-execute C or authenticate that a past execution occurred. Supplying the authentic archive to `--archive` performs the source execution again. No network access or guessed download is part of this command.

```bash
python -m research.p521_math.ntl15_replay --verify research/p521_math/results/ntl15-source-replay.json
python -m research.p521_math.ntl15_replay --archive /path/to/ntl-1.5.tar.Z --output /tmp/ntl15-source-replay.json
```

For a declared generator model H, let X_H(s) and Y_H(s) be its complete coordinate-building and point-selection computations. A provenance reconstruction requires a historically supported H and a retained witness s with `(X_H(s),Y_H(s))=(GX,GY)`, including every rejected candidate and sign choice. The current certificates instead establish `X_H(s) != GX` for every s in specified domains. This already excludes the complete point under those contracts; a separate y-coordinate scan is unnecessary for that implication. It does not exclude unknown H.

The earlier six-layout FreeLIP release and the later 92-profile portable receipt retain their original scopes. Their independent arithmetic checks still supply the complete-domain exclusions. This follow-up adds no new all-state impossibility theorem for NTL 2.x or 3.x, and no recovered P-521 seed. The missing distributions are concrete open inputs, not an excuse to manufacture successor implementations.
