# The complete weight-seven E8 arc kernel

4 November 2026. Exact finite characters, polynomial ranks, lattice evaluation and generator-spanning proof.

The weight-seven classification is complete for the level-one E8 arc-to-Li map. The kernel is

\[
\boxed{K_7=\mathbf1\oplus3V_{248}\oplus3V_{3875}
 \oplus2V_{30380}\oplus2V_{147250}\oplus V_{779247},
 \qquad\dim K_7=1,146,877.}
\]

Every class is a derivative or product of previously established weight-four, five and six kernel classes. The new differential-generator quotient at weight seven is zero. Consequently the known minimal generator list through weight six remains sufficient through weight seven:

\[
V_{3875}\text{ at weight }4;\qquad
V_{248},V_{147250}\text{ at weight }5;\qquad
V_{30380}\text{ at weight }6.
\]

This is a finite-weight theorem. It does not prove that these generators suffice in all weights, and it does not classify weight eight. No historical-priority claim is made.

## 1. Setup and the length decomposition

Let g=e8, normalize long roots to squared length two, and put I=V27000 in Sym²g. Let A=J_infinity(Sym(g)/(I)). The canonical differential-algebra surjection to the Li associated graded of the simple affine VOA L1(E8) has kernel K. A variable x_i^[r] represents the divided jet D^r x_i/r!, with D x_i^[r]=(r+1)x_i^[r+1]. At conformal weight n and current length L, the Li degree is n-L.

The length-graded weight-seven kernel is:

| Current length | Li degree | Kernel character | Kernel dimension |
| ---: | ---: | --- | ---: |
|1|6|0|0|
|2|5|0|0|
|3|4|248+3875+30380+147250|181,753|
|4|3|1+2·248+2·3875+30380+147250+779247|965,124|
|5,6,7|2,1,0|0|0|

Lengths five through seven have zero arc space, not merely zero kernel. Indeed the existing exact cubic-surjectivity theorem gives I*g=Sym³g. At length L and weight n, at least 2L-n factors have zero jet. If 2L-n>=3, every monomial contains a zero-jet cubic and belongs to the differential ideal. At n=7 this eliminates L>=5. This argument also gives the general vanishing criterion A_(n,L)=0 whenever 2L-n>=3.

At lengths one and two, all possible E8 types are covered by g and g tensor g=1+248+3875+27000+30380. At weight seven the three unequal mode pairs give three copies of each tensor-square type, and D^5 I removes one27000. Complete highest columns, exact output images and the one quadratic ideal direction are retained. Their ranks prove that no extra kernel occurs at these lengths.

## 2. The complete quartic answer

The weight-seven quartic arc space, VOA image and kernel are

\[
\begin{aligned}
A_{7,4}={}&\mathbf1\oplus2V_{248}\oplus2V_{3875}
 \oplus2V_{30380}\oplus V_{147250}\oplus V_{779247}\oplus V_{6696000},\\
\operatorname{im}(A_{7,4}\to\operatorname{gr}V)={}&V_{30380}\oplus V_{6696000},\\
K_{7,4}={}&\mathbf1\oplus2V_{248}\oplus2V_{3875}
 \oplus V_{30380}\oplus V_{147250}\oplus V_{779247}.
\end{aligned}
\]

Their dimensions are respectively 7,691,504, 6,726,380 and 965,124. The complete nineteen-type source and rank table is appended below.

The earlier small-sector calculation closed the singlet, adjoint and3875 components by complete covariant bases and old-generator product spans. This checkpoint resolves30380 and all remaining types. It also supplies a bulk Casimir exclusion and direct highest-polynomial certificates.

## 3. The30380 component: distinguish a kernel class from a surviving image

The polynomial source contains seventeen30380 copies. The complete middle-shape covariance space has dimension eleven; the two repeated-three-variable shapes each have dimension three. Wedges built from B and brackets, supplemented by antisymmetric degree-four adjoint-operator words, give bases. Commuting output probes u,v satisfy [u,v]=0, so u wedge v lies in ker[Lambda²g->g]=V30380. They evaluate the desired output projection without a dense30380-dimensional representation.

The quadratic-pair projector and all six differentiated ideal sources give ideal rank fifteen. Thus two arc copies remain. Products of old kernel classes supply one nonzero class, but not both. Several other tested couplings, including the verified147250 source, land in that same line. These partial product spans are retained as arithmetic evidence; they are not treated as a completed kernel theorem by themselves.

The complementary arc class can be represented by

\[
F=\tfrac12\big(u^{[0]}v^{[1]}-v^{[0]}u^{[1]}\big)B(x^{[0]},x^{[2]}),
\]

where u=e_theta and v=e_(theta-alpha_6) in the repository's Chevalley convention. It is highest of type30380. The evaluator includes every lower-length highest column of that type: three at length two and ten at length three. Their projected image rank is seven; adjoining F increases it to eight. Projection is used only as a lower bound on full image rank. Therefore F has nonzero associated-graded VOA image even after every possible lower-length correction.

One known kernel copy and one certified image copy exhaust the two-dimensional arc multiplicity space. Hence the30380 quartic kernel and image multiplicities are exactly one each, with no new primitive. Integer Bareiss elimination independently checks both ranks and the ideal/product coordinate identities.

## 4. A universal quartic Casimir cutoff

This is a structural proof, supported by a small exact S4 certificate.

A dual quartic arc tensor can be regarded as an S4-invariant element of g^(tensor4) tensored with degree-three jet-label polynomials in z1,z2,z3,z4. The pair-ideal condition says that P_I(ij) applied to its restriction at zi=zj is zero. On a triple diagonal the tensor is symmetric in the three coincident slots. Since I*g=Sym³g, the three pair conditions force that triple-diagonal restriction to vanish.

Let U be the degree-three polynomial space vanishing on all four triple diagonals. Exact restriction equations in the twenty monomials have rank twelve, so dim U=8. Its S4 decomposition is S31+S22+S211. Within the subspace even under(12), the kernel of the pair restriction z1=z2 is the single line

\[
r_{12}=(z_1-z_2)^2(z_3-z_4).
\]

Its S31 and S211 components are both nonzero. Choose the positive S4-invariant metric weighting these irreducibles by13/11 and1, and S22 by1. Then the squared norms of the two components of r12 have ratio13:1. The sum of the six orthogonal rank-one projections onto the lines r_ij has eigenvalues13/7,0,1/7 on S31,S22,S211. The six-transposition class sum has eigenvalues2,0,-2. All these are exact identities on the retained eight-dimensional space.

For every pair of adjoint slots, the five known split-Casimir eigenvalues give the positive-form inequality

\[
\Omega_{ij}\le -6(1+\tau_{ij})+14P_I(ij).
\]

On a tensor satisfying the arc constraints, P_I(ij)T lies in the jet-label line r_ij. Thus its squared norm is bounded by the corresponding jet-label rank-one projection. Summing the pair inequality, using the adjoint Casimir60 and the exact frame eigenvalues, gives

\[
C_{\rm total}\le168-12\sum_{i<j}\tau_{ij}+28\sum_{i<j}E_{ij}
\le196.
\]

The three individual bounds are196 on S31,168 on S22 and196 on S211. Any quartic arc type with Casimir greater than196 is therefore absent. This eliminates eight source types at once. The proof uses the positive compact-form Hermitian structure on finite E8 representations; it does not apply an order inequality to an indefinite rational bilinear form.

## 5. The remaining direct finite computations

The polynomial source character was reconstructed independently from the241 distinct adjoint weights using Frobenius/Newton identities and exact Freudenthal subtraction. At weight seven it is3S4(g)+4S31(g)+S22(g)+S211(g), with dimension3,175,205,504 and nineteen irreducible types.

For the remaining types, a meet-in-the-middle weight join enumerates all quartic monomials. Exact highest vectors are checked under all eight raising operators and matched to the independent character multiplicity. Projecting the repeated quadratic pair to I and substituting all six jet distributions spans the complete ideal highest space.

The27000,1763125,2450240 and4096000 sources are entirely exhausted by the ideal. The6696000 sector has source multiplicity five and ideal rank four. Its remaining copy has nonzero full lattice image and no lower-length highest column, so it has zero kernel.

The147250 and779247 sectors each leave one arc copy. Actual highest polynomials obtained from products of the old3875 relation span those copies modulo the ideal. The products use free jets of order two, one and zero with F_Q, D F_Q and D² F_Q respectively. Complete sparse recombinations and invertible rational minors are retained. Thus both whole arc copies belong to K and neither is a new primitive.

The four-current evaluator supports all eight Cartan coordinates. When that full support is selected, its final output is the entire lattice image, rather than a projection. Its generating-function calculation never truncates intermediate states. A nonzero full-support6696000 image is independently reproduced by the original unprojected mode evaluator. The common full-mode source-null checks and the prior four-current comparison suite remain in the package.

## 6. Independent full-character closure and the cubic part

The length-three arc character is recomputed from the existing all-degree S3 covariance/diagonal-restriction proof, with its finite E8 tensor branchings independently reconstructed. Its weight-seven value is

\[
\mathbf1+9V_{248}+6V_{3875}+2V_{27000}+5V_{30380}
 +5V_{147250}+4V_{779247}+V_{2450240}+V_{4096000}.
\]

Combining it with the newly complete quartic character, the complete short-current characters and the long-current vanishing gives dim A7=18,480,125. Independently, the E8 lattice formula m7(mu)=p8(7-||mu||²/2) and Freudenthal subtraction reconstruct the entire VOA character with dimension17,333,248. The independent E4/eta^8 coefficient agrees.

Subtracting the two complete E8 characters gives the boxed kernel character, not just its dimension. Subtracting the quartic answer and the zero short/long pieces rederives the cubic kernel as248+3875+30380+147250. It agrees with the previous PR13 theorem without requiring its original projected matrices as an input to this character argument.

There is no new cubic primitive. On divided jets define E x^[r]=x^[r-1] for r>0 and E x^[0]=0. Then[E,D]=N, the ordinary current-length operator. The quadratic ideal is E-stable because E D^k I=2k D^(k-1) I. E is locally nilpotent, and at every positive length D is injective: if Dv=0 and E^m v is the last nonzero lowering, E^(m+1)Dv=(m+1)N E^m v is a contradiction.

The four known cubic source classes F_Q, P248, P147250 and P30380 therefore have nonzero appropriate derivatives at weight seven. Their distinct E8 types exactly exhaust the computed cubic kernel. The quartic kernel is exhausted by the explicit old-generator product spans. All other lengths have zero kernel. Thus no new differential generator occurs anywhere at weight seven.

## 7. Verification and reproducibility

The archive contains retained highest polynomials, ideal images, full or explicitly projected lattice matrices, finite character rows, positive-frame identities and independent rank certificates. Large sparse spans are verified by exact recombination into selected basis columns and invertible minors checked with integer Bareiss elimination. Small covariant coordinate matrices and corrected30380 image ranks are separately replayed with integer elimination.

The source null identities use the original full mode evaluator. The classification is an exact finite computation together with the stated representation-theoretic and filtration arguments. It is not a proof-assistant formalization.

The combined regression suite passed all 40 tests. The complete-weight entry point is:

```sh
python replay.py --weight7 --tests
```

The ordinary literature/braid replay and the separate exhaustive monodromy closure replay remain available. An all-weight presentation, finite generation beyond weight seven, weight-eight classification and the discrete braid-image presentation remain open. No external repository state was changed by this checkpoint.

## Complete quartic rank table

| E8 dimension | Source | Ideal rank | Arc | VOA image | Kernel |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 5 | 4 | 1 | 0 | 1 |
| 248 | 11 | 9 | 2 | 0 | 2 |
| 3875 | 15 | 13 | 2 | 0 | 2 |
| 27000 | 18 | 18 | 0 | 0 | 0 |
| 30380 | 17 | 15 | 2 | 1 | 1 |
| 147250 | 10 | 9 | 1 | 0 | 1 |
| 779247 | 16 | 15 | 1 | 0 | 1 |
| 1763125 | 5 | 5 | 0 | 0 | 0 |
| 2450240 | 10 | 10 | 0 | 0 | 0 |
| 4096000 | 14 | 14 | 0 | 0 | 0 |
| 4881384 | 4 | 4 | 0 | 0 | 0 |
| 6696000 | 5 | 4 | 1 | 1 | 0 |
| 26411008 | 6 | 6 | 0 | 0 | 0 |
| 70680000 | 8 | 8 | 0 | 0 | 0 |
| 76271625 | 5 | 5 | 0 | 0 | 0 |
| 79143000 | 3 | 3 | 0 | 0 | 0 |
| 203205000 | 1 | 1 | 0 | 0 | 0 |
| 281545875 | 4 | 4 | 0 | 0 | 0 |
| 344452500 | 1 | 1 | 0 | 0 | 0 |
