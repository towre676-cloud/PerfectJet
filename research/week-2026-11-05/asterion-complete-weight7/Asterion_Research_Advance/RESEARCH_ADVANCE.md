**Complete classification now available:** see [COMPLETE_WEIGHT7_THEOREM.md](COMPLETE_WEIGHT7_THEOREM.md). The following document retains its earlier proof stage; its open-sector list is superseded.

**Update:** [QUARTIC_SMALL_SECTOR_THEOREM.md](QUARTIC_SMALL_SECTOR_THEOREM.md) now resolves the singlet, adjoint and3875 quartic components. Their kernel is1+2*248+2*3875, with no new primitives. There are28 focused passing tests. The source-decomposition and monodromy sections below remain applicable; the open-rank discussion now applies to the other quartic types.

# Asterion: exact quartic source and a pure-braid infinite-order witness

4 November 2026. This checkpoint applies methods identified in the literature review. It contains new finite calculations and an evaluator extension, together with a fresh replay of an existing monodromy theorem. It does not close the weight-seven quartic kernel or the all-weight generator problem. No historical priority is claimed.

## Results at a glance

| Item | Result | Evidence and limitation |
| --- | --- | --- |
| Level-four pure braid | UV^-1 has infinite ordinary and projective order | Exact cyclotomic trace and integer 36406>400; no finite-group classification or unitarity needed for this exclusion |
| Existing monodromy closure | Fresh exhaustive replay passed; compact identity component SU(5), projective closure PU(5) | Retains the source's conformal-block unitarity and connected-subgroup theorem dependencies |
| Four-adjoint Schur characters | All five Schur functors decomposed exactly | Root weights, S4 Frobenius formula, Freudenthal subtraction, hook dimensions |
| Weight-seven quartic polynomial source | 19 irreducible types, dimension 3,175,205,504 | This is before the quadratic differential ideal and before VOA evaluation |
| Four-current projected lattice evaluator | Implemented and checked against original full mode calculation | Output projection only; its rank bounds full image rank from below |
| Focused validation | 20 tests passed, plus character/trace/monodromy replays | This is not a full PerfectJet regression run |

## 1. An explicit infinite-order element

Let A and B be the exact five-dimensional half-braid matrices in the pinned PerfectJet Tuba--Wenzl model over Q(zeta), zeta=exp(2pi i/17). They obey ABA=BAB, A^34=B^34=I and det A=det B=zeta^9. Their pure squares correspond to U and V. Set

    W = A^2 B^-2 = U V^-1.

Exact matrix multiplication gives tr(W)=sum_(j=0)^15 c_j zeta^j, where

    c = (33,0,22,-6,19,-2,13,7,18,18,7,13,-2,19,-6,22).

This retained trace is recomputed from the matrices, not accepted from a stored success flag. A second multiplication computes t times its complex conjugate in Q[zeta]/Phi17 and checks its field trace independently.

If W had finite order, every eigenvalue of every field-conjugate matrix sigma_k(W) would be a root of unity. Thus |sigma_k(tr W)|<=5 for all 16 embeddings. Summing squared moduli would give at most 16*25=400.

But the exact identity sum_(k=1)^16 zeta^(km)=16 when17 divides m and -1 otherwise gives

    sum_(k=1)^16 |sigma_k(tr W)|^2
      = 17 sum_j c_j^2 - (sum_j c_j)^2
      = 17*3943 - 175^2 = 36,406 > 400.

Therefore W has infinite order. Its determinant is one. If its projective order were finite, some W^m=cI would have c^5=1, so W^(5m)=I, a contradiction. Its projective order is infinite as well.

This proof is entirely integral once the exact matrix model and its trace are constructed. For additional localization, rigorous rational root enclosures show

    125 < Re sigma_8(tr W) < 126,
    sigma_8(zeta)=zeta^8.

The large trace occurs in a Galois-conjugate realization, not the unitary physical embedding; it does not contradict unitarity of the latter. It does not imply that W's powers alone are dense in SU(5), nor supply a presentation of the braid image.

The application to actual KZ holonomies uses the repository's flat equivariant descent, exact half spectra and central scalar, specialized irreducibility, and Tuba--Wenzl uniqueness up to simultaneous conjugacy. The fresh exhaustive monodromy replay supplies the specialized irreducibility gate. Its receipt separately records all proof dependencies. The explicit infinite-order witness adds a classification-free finiteness obstruction; density was already an existing repository theorem and is not claimed as a new theorem of this checkpoint.

## 2. Complete Schur decomposition of four adjoint factors

Let g=e8, of dimension 248, with 241 distinct weights: 240 roots of multiplicity one and zero of multiplicity eight. The five S4 conjugacy types are 1^4, 2 1^2, 2^2, 3 1, 4, with class sizes 1,6,3,8,6. The S4 character rows used are:

| Partition | Character row | Schur dimension |
| --- | --- | ---: |
|4|1,1,1,1,1|161,455,750|
|31|3,1,-1,0,-1|476,648,250|
|22|2,0,2,-1,0|315,223,376|
|211|3,-1,-1,0,1|469,021,878|
|1111|1,-1,1,1,-1|153,829,130|

For each row, the Frobenius character formula applies these coefficients and class sizes to chi^4, chi^2 psi2(chi), psi2(chi)^2, chi psi3(chi), psi4(chi), and divides by24. Every relevant dominant weight through squared norm 32 is included. Cauchy--Schwarz makes 32 an exhaustive highest-weight bound for four adjoint weights. Exact Freudenthal subtraction reconstructs the E8 irreducibles. Hook-content dimensions independently check all five totals. The tensor-power identity sum_lambda f^lambda dim S_lambda(g)=248^4 also passes.

The complete tables, highest weights in the repository's Dynkin numbering, power-sum weight coefficients and highest-weight subtraction rows are retained in quartic_schur_receipt.json. Dimension labels below are unambiguous among these nineteen types; the receipt retains the full highest weights.

## 3. The weight-seven, length-four polynomial source

The three jet shapes are (3,0,0,0), (2,1,0,0), and (1,1,1,0). Before quotienting, the corresponding E8 module is

    P_(7,4) = 2(g tensor Sym^3 g) + (g tensor g tensor Sym^2 g)
            = 3 S4(g) + 4 S31(g) + S22(g) + S211(g).

Its dimension is3,175,205,504. The table appended below gives all nineteen multiplicities and the five individual Schur decompositions. In particular the source contains 5 singlets, 11 adjoints, 15 copies of 3875, and 17 copies of 30380. These are polynomial-source multiplicities, not surviving arc multiplicities or kernel multiplicities.

This avoids a dense248^4 tensor. It creates a checkable inventory against which highest-vector searches can be certified complete. The auxiliary character S31+S22+S211 is also serialized, but this checkpoint does not claim it bounds the arc quotient: that requires a separate proof of the triple-diagonal and ideal constraints.

## 4. Four-current lattice evaluation

The previously retained projected evaluator covered at most three currents. The new ProjectedLatticeE8VOA4 extends root-only tails to four and inherits exact Cartan commutation, cocycles, divided-jet symmetrization and lower-length terms.

For roots a_i and creation indices n_i, expand the exact lattice product in |z1|>|z2|>|z3|>|z4|. Write k_ij=(a_i,a_j), and expand each (zi-zj)^k_ij with nonnegative h_ij. The Schur degree in the i-th exponential is

    d_i = n_i-1 - sum_(j>i) k_ij
                      + sum_(j>i) h_ij - sum_(j<i) h_ji.

Choose incoming h values starting with the last column. Nonnegativity of d_j supplies a finite bound after all outgoing h_jk have been chosen. This enumerates exactly the coefficient terms. Full root charges and pair inner products are retained, while oscillator output coordinates are restricted only after the exact generating formula. Mixed Cartan/root words commute Cartan modes to the left with all bracket corrections. No intermediate state is truncated.

Tests compare the output with projection of the original unprojected mode evaluator. They cover all three weight-seven mode shapes, repeated and distinct roots, mixed Cartan/root words, nonzero total charge, cache reuse, multiple oscillator supports and PBW-symmetrized rational inputs. A projected rank remains only a full-rank lower bound; proving an exact kernel still needs matching full null lifts or another upper bound.

## 5. Literature applications and boundaries

| Primary source | Verified scope in the preceding search | Application here |
| --- | --- | --- |
|[Westbury, exceptional series through fifth tensor power](https://arxiv.org/abs/2607.16353)|2026 primary abstract; full tables not audited|Motivates comparison; this checkpoint reconstructs its own four-factor characters and does not depend on those tables|
|[Song--Zeng, Zhu and C2 algebras](https://arxiv.org/abs/2606.14407)|2026 primary abstract: classical freeness obstruction including level-one E8|Conceptual compatibility with a nonzero jet-to-Li kernel; not a weight-seven rank theorem|
|[Dahiya--Mukhin, intertwiners](https://arxiv.org/abs/2503.09845)|Published2025; inspected E8 multiplicity blocks and pole-conjecture discussion|Supports multiplicity-space strategy;249-dimensional quantum-affine module is not this jet source|
|[Kanade, type-A classical freeness](https://arxiv.org/abs/2606.19234)|2026 primary abstract and submitted status|Normal forms and character comparisons remain a future finite-generation route; no E8 freeness transfer|
|[Negami, finite images and KZ-type equations](https://arxiv.org/abs/2609.25805)|2026 primary abstract; Katz--Long--Moody hypotheses not audited|No such realization of Asterion constructed; its finiteness theorem is not used|
|[Jin, maximal ideals](https://arxiv.org/abs/2607.25249), [formal report](https://arxiv.org/abs/2609.27952)|2026 primary abstracts; negative-level theorem and conditional Lean interfaces|Not used as a theorem about this positive-level arc kernel|
|[Tuba--Wenzl, B3 and SL2Z](https://msp.org/pjm/2001/197-2/pjm-v197-n2-p11-s.pdf)|Classical primary paper; uniqueness and simplicity framework|Inherited exact cyclotomic model and its KZ identification|
|[Rowell--Tuba, finite low-dimensional images](https://arxiv.org/pdf/0806.0168)|Primary full text, degree-five projective-order criterion|Existing closure argument; new trace proof avoids its finite-group classification for infinitude|

## 6. Remaining mathematical work

1. Compute exact ranks of the quadratic differential-ideal maps on the relevant weight-seven quartic multiplicity spaces. The nineteen source multiplicities alone do not give these ranks.
2. Build complete highest columns for the surviving arc spaces and evaluate them together with all necessary lower-length corrections through the four-current evaluator.
3. Match projected image-rank lower bounds with full affine null lifts, then quotient by derivatives and products of established kernel generators. Only that last step determines new primitives.
4. Reconcile any later-session quartic claims using their actual certificates. This checkpoint does not promote remembered claims about sixteen resolved sectors or longer-length vanishing without their source evidence.
5. All-weight finite generation, an explicit unitarizing matrix, the endpoint associator and a complete discrete braid-image presentation remain outside these calculations.

The currently inspected PR13 is still open; its cubic result and its integration state are separate from this research checkpoint. No main-branch files or external repository state were changed.

## 7. Replay and provenance

Run Python3 with standard-library dependencies:

```sh
python replay.py
python replay.py --tests --monodromy
```

The first command recomputes the Schur receipt and the exact trace witness. The second also runs the 20 focused tests and reconstructs the actual-loop monodromy closure certificate. Running the latter is a bounded analytic calculation; the new trace exclusion itself does not require numerical transport or root enclosures.

SOURCE_PROVENANCE.json pins the main snapshot to9b69eab9beff3011bc6216b30a460c2c6d0e97be. The inherited three-current projection and its tests come from PR13 head081ee6d76726ead700eb87fb423835afa5ac8ba4. The archive contains a focused executable source subset, not a complete PerfectJet checkout. SHA256SUMS.json covers the retained checkpoint files.

## Complete four-factor decomposition table

| E8 dimension | S4 | S31 | S22 | S211 | Lambda4 | P(7,4) |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 1 | 0 | 2 | 0 | 0 | 5 |
| 248 | 0 | 2 | 0 | 3 | 1 | 11 |
| 3875 | 1 | 2 | 3 | 1 | 1 | 15 |
| 27000 | 2 | 2 | 3 | 1 | 1 | 18 |
| 30380 | 0 | 3 | 1 | 4 | 0 | 17 |
| 147250 | 1 | 1 | 1 | 2 | 1 | 10 |
| 779247 | 0 | 3 | 1 | 3 | 1 | 16 |
| 1763125 | 0 | 1 | 0 | 1 | 0 | 5 |
| 2450240 | 1 | 1 | 2 | 1 | 1 | 10 |
| 4096000 | 1 | 2 | 1 | 2 | 1 | 14 |
| 4881384 | 1 | 0 | 1 | 0 | 0 | 4 |
| 6696000 | 0 | 1 | 0 | 1 | 0 | 5 |
| 26411008 | 0 | 1 | 1 | 1 | 0 | 6 |
| 70680000 | 1 | 1 | 1 | 0 | 0 | 8 |
| 76271625 | 0 | 1 | 0 | 1 | 0 | 5 |
| 79143000 | 1 | 0 | 0 | 0 | 0 | 3 |
| 203205000 | 0 | 0 | 1 | 0 | 0 | 1 |
| 281545875 | 0 | 1 | 0 | 0 | 0 | 4 |
| 344452500 | 0 | 0 | 0 | 1 | 0 | 1 |
