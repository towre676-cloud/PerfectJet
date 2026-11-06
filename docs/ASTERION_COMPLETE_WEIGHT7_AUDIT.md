# Complete weight-seven E8 audit and integration proposal

Audit date: 5 November 2026 (America/New_York). Research input: PR #16,
`92d9eed8f07ea0549a16acb06b974189a2622380`. Comparison main:
`8f38d6f2ee66c25a0618c45c36212e61905355c2`. Release-candidate PR #15 head
observed: `0876e9f1defc19b87ead8291a8458e71a899c55f`.

## Decision

The recovered complete theorem has substantially stronger support than a
preservation-only import: its mathematical regeneration reproduces the stated
quartic and complete characters. It is suitable for a dedicated research
verification contribution. Installed-package promotion remains a separate
integration task. Keep v0.22.0rc1 explicitly cubic-only and preserve all its
existing verification gates. A repaired publication job does not verify this
additional theorem.

The result concerns the level-one E8 arc-to-Li map over characteristic zero:

\[
K_7=1\oplus3V_{248}\oplus3V_{3875}\oplus2V_{30380}
\oplus2V_{147250}\oplus V_{779247},\qquad \dim K_7=1,146,877.
\]

It is an exact finite computation with structural mathematical arguments,
not a proof-assistant formalization, independent external peer review, or an
all-weight finite-generation theorem.

## Reproduced calculations

The complete `replay.py --weight7 --tests` regeneration passed with exit code
zero using Python 3.12.14 in the recovered package. Its final 40 tests passed
in 64.779 seconds after mathematical regeneration. The accompanying delivery
logs retain the full command output; intermediate printed `passed` flags
were not used as the outcome of the entire command.

Separate checks replayed all seven retained sparse spans using rational
recombinations and integer Bareiss minors; regenerated the S4 frame and cutoff;
reconstructed the length-three arc and full VOA characters; and checked the
small covariant matrices and corrected 30380 image ranks. The focused suite
has 40 tests (36 E8/quartic tests and four braid tests); those four braid tests
do not supply additional evidence for the quartic theorem.

All 40 focused tests also passed using main's existing mathematics modules
and certificate resource, with only the missing four-current evaluator loaded
through an audit-only import. This is a compatibility check, not an installed
wheel verification. The existing four cubic integration tests also passed.

| Quantity | Reproduced value |
| --- | ---: |
| Quartic polynomial source dimension | 3,175,205,504 |
| Quartic source irreducible types | 19 |
| Quartic arc dimension | 7,691,504 |
| Quartic image dimension | 6,726,380 |
| Quartic kernel dimension | 965,124 |
| Complete arc dimension at weight seven | 18,480,125 |
| Simple VOA dimension at weight seven | 17,333,248 |
| Complete kernel dimension | 1,146,877 |
| Cubic kernel dimension | 181,753 |
| New weight-seven differential-generator quotient dimension | 0 |

The quartic arc character is
`1 + 2·248 + 2·3875 + 2·30380 + 147250 + 779247 + 6696000`.
Its image is exactly `30380 + 6696000`. Subtraction gives
`1 + 2·248 + 2·3875 + 30380 + 147250 + 779247` for the quartic kernel.

## Rank accounting and surviving image multiplicities

| E8 dimension | Source multiplicity | Ideal rank | Arc | Image | Kernel |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 5 | 4 | 1 | 0 | 1 |
| 248 | 11 | 9 | 2 | 0 | 2 |
| 3,875 | 15 | 13 | 2 | 0 | 2 |
| 27,000 | 18 | 18 | 0 | 0 | 0 |
| 30,380 | 17 | 15 | 2 | 1 | 1 |
| 147,250 | 10 | 9 | 1 | 0 | 1 |
| 779,247 | 16 | 15 | 1 | 0 | 1 |
| 1,763,125 | 5 | 5 | 0 | 0 | 0 |
| 2,450,240 | 10 | 10 | 0 | 0 | 0 |
| 4,096,000 | 14 | 14 | 0 | 0 | 0 |
| 4,881,384 | 4 | 4 | 0 | 0 | 0 |
| 6,696,000 | 5 | 4 | 1 | 1 | 0 |
| 26,411,008 | 6 | 6 | 0 | 0 | 0 |
| 70,680,000 | 8 | 8 | 0 | 0 | 0 |
| 76,271,625 | 5 | 5 | 0 | 0 | 0 |
| 79,143,000 | 3 | 3 | 0 | 0 | 0 |
| 203,205,000 | 1 | 1 | 0 | 0 | 0 |
| 281,545,875 | 4 | 4 | 0 | 0 | 0 |
| 344,452,500 | 1 | 1 | 0 | 0 | 0 |

For the eight types above the Casimir cutoff, the table's ideal ranks follow
from structural vanishing of the arc quotient and the complete source
character. They are not eight separately regenerated large ideal matrices.

The 30380 evaluator includes all 13 lower-length highest columns (three at
length two and ten at length three). Their projected image rank is seven;
adding the quartic highest witness raises it to eight. Hence that witness
cannot belong to the full lower-length image. Projection establishes a lower
bound on image rank, not a null identity. One old-product kernel copy and one
surviving image copy exhaust the two arc copies. The ideal/product rank is
15/16 inside the 17-dimensional source multiplicity space.

For 6696000 the source has five copies, the ideal has rank four, and there
are no lower-length highest columns. Full eight-coordinate lattice evaluation
has rank one. The focused tests compare a nonzero representative with the
original unprojected mode evaluator. The remaining arc copy therefore has
zero kernel. The other direct sectors have ideal ranks 18, 5, 10, 14, 9 and
15 in dimensions 27000, 1763125, 2450240, 4096000, 147250 and 779247.

## Character reconstruction and proof assumptions

The polynomial source is reconstructed as `3S4(g)+4S31(g)+S22(g)+S211(g)`
from 241 distinct adjoint weights, S4 Frobenius characters and exact
Freudenthal subtraction. The whole tensor-four dimension is cross-checked.
This computation does not assume the claimed ideal or VOA ranks.

The length-three character follows the S3 covariance and diagonal-restriction
argument, including a fresh projected-polarization calculation and tensor
character reconstruction. The VOA character uses the E8 lattice multiplicity
`m7(mu)=p8(7-||mu||²/2)` and Freudenthal subtraction, with the independent
scalar `E4/eta^8` coefficient as a dimension check. Complete character
subtraction gives the full kernel, and removing the quartic answer recovers
exactly the merged cubic character `248+3875+30380+147250`.

The finite computations use the same E8 root/bracket and exact-arithmetic
infrastructure as PerfectJet. Their rerun is independent of historical
receipts; it is not a wholly independent implementation of E8 or Freudenthal.
Some regenerated receipts retain hard-coded historical `source_commit`
metadata. Those strings are not fresh-run provenance; the pinned input
commit, imported source hashes and execution logs identify this audit.
The identification of the level-one affine VOA with the E8 lattice VOA, the
filtered surjectivity of the arc-to-Li map, finite-dimensional complete
reducibility, and the representation-theoretic dual interpretation are
mathematical inputs. The audit reviewed their use and found the conventions
consistent; it did not reprove those general theorems from first principles.

## Casimir cutoff

Long roots have squared length two and the adjoint Casimir is 60. A separate
exact check recomputed pair split-Casimir eigenvalues from highest weights:
`-60,-30,-12,2,0` on `1,248,3875,27000,30380`. With symmetric/antisymmetric
pair parities these verify `Omega <= -6(1+tau)+14 P27000` on every pair type.

The degree-three jet-label space has 20 monomials. Regenerated triple-diagonal
constraints have rank 12 and leave dimension eight, of S4 type
`S31+S22+S211`. The even pair-restriction kernel is the line
`(z1-z2)^2(z3-z4)`. An explicitly positive invariant metric gives frame
eigenvalues `13/7,0,1/7` and transposition-sum eigenvalues `2,0,-2`.
Summation yields bounds `196,168,196` and the universal bound 196.

The crucial structural step is that the dual arc constraints force triple
diagonal vanishing, using `I27000*g=Sym³g`; the same dependency is recomputed
in the character replay. The pair projector then has its jet-label output
in the indicated line. The norm inequality is applied in a positive compact
Hermitian structure, not the indefinite rational Chevalley bilinear form.
The finite S4 identities are executable exact calculations. This transfer
from dual arc tensors to the operator inequality is a reviewed mathematical
argument, not a formalized proof.

## Why no new generator remains

The singlet, adjoint and 3875 old products increase ideal ranks respectively
`4->5`, `9->11`, `13->15`, exhausting their arc spaces. The 30380 product
increases rank `15->16`, accounting for its single kernel copy. Explicit
highest products of the weight-four 3875 relation and its derivatives
increase ranks `9->10` and `15->16` in 147250 and 779247. Every sparse
recombination is checked, not merely the determinant of a selected minor.
The full lower-weight null-source checks are part of the regeneration.

The cubic classes are derivatives of older classes. On divided jets,
`D x[r]=(r+1)x[r+1]` and `E x[r]=x[r-1]` give `[E,D]=N`, with N the current
length. The quadratic ideal is E-stable because `E D^k I=2k D^(k-1)I`.
Local nilpotence proves D injective at positive length; the four nonzero
translated classes exhaust the cubic kernel. This E is different from main's
Möbius operator `F x[r]=(r+1)x[r-1]`, which satisfies `[F,D]=2H`.
Both arguments are compatible. Their operators must not be conflated.

At lengths one and two the regenerated image ranks exhaust the arc spaces.
At lengths five through seven every weight-seven monomial has at least three
zero jets, so `I*g=Sym³g` makes the arc space zero. This proves the complete
length accounting at this weight; it says nothing about all-weight closure.

## Production integration obligations

1. Preserve the existing seven-sector primitive certificate resource. The
   recovered snapshot resource contains only `w5-248`; copying it over main
   would discard six existing sectors. That shared sector is identical.
2. Add the four-current evaluator without overwriting main's primitives
   module. All shared mathematics-module ASTs match except that the snapshot
   omits main's newer `mobius_lower` method. Most byte differences are trailing
   newlines; they still affect source hashes.
3. Treat the new module as a source-binding change: `source_digests()` globs
   `asterion*.py`. Regenerate the affected existing receipts and integration
   inventories through their mathematical replay commands. Do not merely
   replace hash strings or suppress stale-source checks.
4. Introduce a separately named complete-weight-seven report/resource with
   explicit length/Li degree, all 19 quartic rows, image multiplicities, old
   product dependencies, exact source/evidence hashes and verification mode.
   Preserve the cubic report's existing schema and meaning. A retained-evidence
   report must not present itself as a fresh lattice replay.
5. Bind the cutoff proof, character builders, source-null lifts and sparse
   reconstruction checks into dedicated CI. Add negative tests for removed
   sectors, changed minors/products, omitted lower-length columns, altered
   cutoff data and stale source/resource bindings.
6. Run the complete regeneration against the reconciled production modules,
   the existing cubic replay and full regression suite; build the wheel and
   source ZIP; verify installed resources and the report outside the checkout
   on Linux and Windows. The audit-only overlay is not a substitute.
7. Rebuild release inventories and reproducibility attestations for the
   eventual broader release. Keep rc1 cubic-only. Any Linux timeout repair
   must retain all substantive checks and is an independent workstream. No hosted
   workflow, release publication or installed full-theorem integration was
   completed by this audit.

## Concrete proposed patch for approval

This patch adds this audit document, `scripts/audit_complete_weight7.py`, and
`.github/workflows/complete-weight7-audit.yml`. The command verifies imported
source/evidence hashes, restores lossless evidence into a temporary copy,
runs the complete research replay and tests, and retains results with the
actual checkout commit. It rejects altered source inputs. Its summary keeps
`installed_package_verified=false` and `publication_authorized=false`.

The workflow is a separate read-only research job with a six-hour ceiling
and retained failure logs. It changes neither the release job's limits nor
its checks, and has no publication step. A hosted runtime measurement and
subsequent tuning of this research job remain pending. The local preparation
path and tamper rejection were tested; the underlying complete replay was
run directly, rather than rerunning the entire expensive command through
this newly written wrapper.

No production API or mathematical resource replacement is proposed for
immediate application. Promoting the full theorem is a later patch after the
obligations above. No changes have been pushed, merged or published.

## Sources

- https://github.com/towre676-cloud/PerfectJet/pull/16
- https://github.com/towre676-cloud/PerfectJet/pull/15
- https://github.com/towre676-cloud/PerfectJet/blob/92d9eed8f07ea0549a16acb06b974189a2622380/research/week-2026-11-05/asterion-complete-weight7/Asterion_Research_Advance/COMPLETE_WEIGHT7_THEOREM.md
- https://github.com/towre676-cloud/PerfectJet/blob/8f38d6f2ee66c25a0618c45c36212e61905355c2/docs/ASTERION_WEIGHT_SEVEN_LENGTH_THREE.md
