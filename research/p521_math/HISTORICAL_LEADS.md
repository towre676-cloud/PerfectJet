# Historical generator evidence

The subsequent [source-recovery audit](HISTORICAL_SEARCH.md) records the author/archive and distribution searches, the still missing NTL 2.x/3.x implementations, and a digest-gated execution harness for the authentic 1.5 source. No successor source distribution or P-521 origin was recovered. Existing source pins and mathematical certificates below retain their original scope.

The useful new artifact is **the author's NTL 1.5 distribution, preserved on 1 August 1997**. Its integer RNG matches the FreeLIP multiplicative generator already studied. Its public wrappers and machine configuration add concrete models that are easy to miss: `RandomLen` assembles limbs in the opposite order from `RandomBnd`, forces the highest requested bit, and the ordinary 64-bit-long configuration uses **50-bit limbs** with 53-bit doubles.

This is evidence about historically available software, not a recovered P-521 seed or an attribution of that software to the curve designers. Machine-readable source pins are in [results/historical-sources.json](results/historical-sources.json).

## Recovered primary artifact

- Original distribution: `http://www.cs.wisc.edu/~shoup/ntl/ntl-1.5.tar.Z`.
- Exact preserved response: <https://web.archive.org/web/19970801214429id_/http://www.cs.wisc.edu/~shoup/ntl/ntl-1.5.tar.Z>.
- Size: 446,513 bytes.
- SHA-256: `c2d80c5293c824b16f89ac7e5e0aeb29e3996f8560b877c44858f41c43717e1c`.
- SHA-1 in Archive CDX base32 notation: `PRGFKILF6MDDAQFNECN6RBRIB45DHDMS`; independently recomputed from the downloaded compressed bytes and equal to the CDX digest.
- HTTP capture: **1997-08-01 21:44:29 UTC**. Original HTTP `Last-Modified`: **1997-07-07 16:12:11 GMT**. These establish preserved metadata and availability, not an exact release date.
- Author's page, captured 1997-08-03: <https://web.archive.org/web/19970803064110id_/http://www.cs.wisc.edu/~shoup/ntl/>. It identifies NTL 1.5 and links this archive. Page SHA-256: `7b90940769232f73902161df48ee8f933d1ee8827c4a843934338b292ad2181a`.

The distribution says its software is for research and educational purposes only. No original archive or source file is included in this repository. The descriptions below are independently stated mathematical semantics and file identifiers.

| Archive member | Bytes | SHA-256 | Relevant locations |
| --- | ---: | --- | --- |
| `lip.c` | 81,764 | `3fe2f59879c2dbc57fa5e324676cf5d56dc21176030b93e4b11eeb808864cde2` | `zrstarts` 3156; `zrstart` 3180; `zrandom` 3192; `zrandomb` 4694; `zrandoml` 4716 |
| `lip.h` | 13,943 | `578173101d0469f0a36c97dee8b876e1f32766dcd7c809ee290a2ae306b8a14c` | `SINGLE_MUL` radix override 40–47 |
| `ZZ.h` | 25,549 | `1097310ae098a6f73187e0bafec4d68922a1fa862e4c057bda5a47e30dc3ccdf` | `SetSeed` 552; `RandomBnd` 557; `RandomLen` 566 |
| `ZZ.c` | 16,635 | `4a1f20a6801408acbde7f16649a6de473397003ead162a91f7a3622185420c7a` | single-precision `RandomLen` 766 |
| `MakeDesc.c` | 3,721 | `cf6fa9b7239373c26d8f04c1086ee1108ddf87a1a75e826c387f15fe57be06d4` | default `ZZ_NBITS` 138–145 |
| `README` | 26,367 | `dd130798b1b2e1090f3bda561bb6d3d365ba3a753daf09124f86fd98d1bdf933` | identifies changes from NTL 1.0 to 1.5 |

## Exact NTL 1.5 semantics

Let

\[
 M=2^{107}-1=162259276829213363391578010288127,
 \qquad A=3^{121}\bmod M=56455876562739436995171414077326.
\]

`SetSeed` passes the complete arbitrary-precision `ZZ` integer into `zrstart`: reduce it modulo `M` and replace residue zero by one. The lazy default seed is `7157891`. No byte-array seeding API or truncation to a machine word was found in this version. The public seed API takes a `ZZ`, rather than a `long`. This matters when a candidate seed exceeds a signed machine word.

For a positive bound `b`, one `zrandom(b)` call computes `T = M - (M mod b)`, advances `S = A*S mod M` until `S < T`, and returns `S mod b`. The emitted word is the **low residue**. There is no high-word extraction in this recovered function.

For radix `R=2^w`, the two big-integer wrappers differ:

1. **`RandomBnd(x,bound)`**, calling `zrandomb`: when `bound>1`, take `ceil(bitlength(bound)/w)+1` accepted `zrandom(R)` outputs, concatenate **first output most significant**, then reduce modulo `bound`. Return zero when `bound<=1`.
2. **`RandomLen(x,L)`**, calling `zrandoml`: for `L>1`, take `ceil(L/w)` accepted `zrandom(R)` outputs and assign them **first output least significant**. Keep only the requested number of bits in the last limb, and force bit `L-1` to one. For `L<=0`, return zero; for `L=1`, return one. Those edge cases consume no output.

`RandomBits` is absent from the recovered NTL 1.5 distribution. Its implementation must not be guessed from the names or from a later release.

Independent executable outline (accepted radix outputs include the preceding rejection loop):

```python
def seed(s):
    return s % M or 1

def draw(S, b):
    T = M - M % b
    while True:
        S = A * S % M
        if S < T:
            return S, S % b

def random_bnd(S, bound, w):
    if bound <= 1:
        return S, 0
    R = 1 << w
    n = (bound.bit_length() + w - 1) // w + 1
    x = 0
    for _ in range(n):
        S, u = draw(S, R)
        x = x * R + u
    return S, x % bound

def random_len(S, L, w):
    if L <= 0:
        return S, 0
    if L == 1:
        return S, 1
    n = (L + w - 1) // w
    x = 0
    for j in range(n):
        S, u = draw(S, 1 << w)
        x += u << (j * w)
    return S, (x & ((1 << (L - 1)) - 1)) | (1 << (L - 1))
```

The last expression discards the random value of the forced bit, just as the source does. It does not discard an RNG call.

## Historically justified radix widths

The recovered `MakeDesc.c` computes the largest even integer at most

\[
\min(\text{bits per long}-2,\ \text{double precision}-3).
\]

For 53-bit floating-point precision this yields `w=30` with a 32-bit `long`, and **`w=50` with a 64-bit `long`**. A supported `SINGLE_MUL` option overrides it to `w=26`. The shipped makefile uses `-O2` and leaves `SINGLE_MUL` optional.

This is a source-backed reason to test 26, 30, and 50 in an NTL-1.5 model. FreeLIP's separate Alpha-specific 62-bit configuration should not be silently substituted for NTL's configuration algorithm.

For P-521, `RandomBnd(p)` consumes 22, 19, or 12 accepted words at widths 26, 30, or 50 respectively. `RandomLen(521)` consumes 21, 18, or 11, with opposite assembly order and a forced highest bit.

## Immediate implication for P-521

The published `GX` has **bitlength 520**, while every `RandomLen(521)` output has bit 520 set. Consequently `GX` cannot be the direct `RandomLen(521)` output. Reduction modulo `p=2^521-1` adds only the special possibility of zero and does not produce this `GX` either.

This statement does not cover Montgomery representation changes, scalar multiplication, or other later transformations. `RandomBnd`, other requested bit lengths, and source-backed alternative machine widths remain different models. The recovered archive justifies testing them; it does not assert that any was used.

## What chronology is actually established

- NTL 1.5 was publicly archived by **1 August 1997**, before the 8 August coefficient-seed timestamp associated with several later curves.
- An archived author Usenet announcement has header **29 December 1997 13:03:56 GMT**, announces NTL 2.0, and names 1.7 as its predecessor: <https://ns1.omnitech.net/data/Books/Math/97/NTL/>. This is an exact preserved announcement timestamp, not a proven first-release timestamp.
- The author's archived page on **3 February 1999** identifies 3.1b and says 3.0f is still available: <https://web.archive.org/web/19990203204956id_/http://www.cs.wisc.edu/%7Eshoup/ntl/>.
- The [author's current changelog](https://libntl.org/doc/tour-changes.html) says 3.0d→3.0e and 3.0e→3.0f fixed `RandomBits` bugs; 3.1b→3.5a replaced the PRNG. Those entries have no dates. The 5.0c→5.1a entry explicitly dates dropping the first 256 ARC4 bytes to **8 June 2001**.
- A separate contemporaneous observation, [Schneier's newsletter of 15 December 1998](https://www.schneier.com/crypto-gram/archives/1998/1215.html), says “Version 3.1b has just been released.” This is useful corroboration but is not an author release record or an exact release date.

No NTL 3.0/3.1/3.5 source archive was recovered here, and no exact release date for those versions is established. In particular, the undated 3.5 replacement entry is **not evidence of a PRNG switch during 1997**. Later MD5/ARC4 code must not be retroactively treated as a contemporary 1997 generator.

## Next source question

The highest-value missing artifact is an authentic NTL 2.0 or 3.0-era distribution. It could establish when `RandomBits` appeared, the exact pre-fix and post-fix bit assembly, and whether the old `RandomLen` semantics survived. The actual 1.5 archive already answers the low-word and width questions for one software version available during 1997.
