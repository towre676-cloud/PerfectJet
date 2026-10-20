# Explicit level-four Asterion half-braids

The specified level-four pure-loop representation extends to a genuine linear representation of B3. There is no scalar defect in its braid relation. The generators have actual and projective order 34, their squares are exactly the existing U,V, and their full twist is zeta^4 I, where zeta=exp(2 pi i/17). An independently replayable cyclotomic model identifies its simple Tuba–Wenzl equivalence class. These are applications of classical KZ descent and low-dimensional classification to the retained E8 data; no historical priority or presentation of the dense image is asserted.

## Conventions and exact descent

The fiber is the five-dimensional invariant four-adjoint tensor space, equivalently Hom_g(g,g tensor g tensor g) after using the invariant form to dualize the fourth slot. The first three slots move; the fourth is the output. Matrices act on columns, and matrix products compose with the rightmost operator acting first. A positive exchange means that the colliding separation rotates counterclockwise through pi. The ordered base configuration is (0,1/2,1).

Let A=Omega12, B=Omega23 and C=Omega13 in the existing tensor chart. Exact rational arithmetic verifies

\[
A+B+C=-60I,\qquad [A,B+C]=[B,A+C]=[C,A+B]=0.
\]

The corresponding flat connection on the ordered configuration space is

\[
dF=h\big(A\,d\log(z_2-z_1)+B\,d\log(z_3-z_2)
+C\,d\log(z_3-z_1)\big)F,\qquad h=1/34.
\]

The tensor permutations P12 and P23 are computed in the exact tensor chart. They square to I, satisfy the S3 braid relation, fix their corresponding residue and permute the other residues. For example P12 B P12=C. They are genuine permutations of the invariant tensors: form symmetry and the Jacobi identity give their global action; the retained invertible five-evaluation matrix extracts their coordinates. The exact channel action of P12 is diag(1,-1,1,-1,1), in the channel order (1,248,3875,30380,27000). These signs distinguish symmetric and alternating summands.

Flatness and this permutation equivariance descend the connection to unordered configurations. Holonomy therefore gives a linear B3 representation. This is the exact proof of the braid relation, rather than a claim that an interval residual containing zero proves equality. The standard positive adjacent exchanges square to the positive collision meridians. Under the section (z1,z2,z3)=(0,z,1), those meridians are homotopic to the existing counterclockwise rectangular loops about zero and one. Thus their squared matrices are U,V with no inverse or extra scalar.

For completeness, put L=z3-z1 and u=(z2-z1)/L. The connection becomes

\[
h\big(A\,d\log u+B\,d\log(u-1)-60I\,d\log L\big).
\]

This displays the scalar scale term that would be lost by retaining only the cross-ratio coordinate. Local collision coordinates can use fixed pair midpoint and a positive real incoming separation. Their nonresonant canonical local basis has leading identity, and the tensor exchange acts on a channel by its sign times exp(pi i h a). Transport along the real incoming path fixes the positive logarithm branch. A full counterclockwise turn doubles the exponent. The path to the collision can be contracted toward its tangential limit; flatness makes the transported exchange independent of this contraction. No numerical limit at a singular endpoint is taken in the certificate.

## Half-braids in the existing based chart

The pure spectrum is simple. If P_i(U) denotes its polynomial spectral projector, the local half-exchange spectrum and commutation with its square force

\[
R_1=\sum_{i=1}^5\mu_i P_i(U),\qquad
P_i(U)=\prod_{j\ne i}\frac{U-\lambda_jI}{\lambda_i-\lambda_j},
\qquad R_2=XR_1X.
\]

Here X is the existing rational crossing matrix. The map z to 1-z comes from an orientation-preserving affine rotation of the moving configurations followed by permutation of the first and third labels. It conjugates the two positive adjacent exchanges, as well as their meridians. The scalar scale contribution cancels in this conjugation. In the existing channel order the exact phases are

\[
(\lambda_i)=(\zeta^4,\zeta^2,\zeta^{11},1,\zeta),
\qquad
(\mu_i)=(\zeta^2,\zeta,\zeta^{14},-1,-\zeta^9).
\]

Equivalently the half phases are eta raised to (4,2,28,17,1), with eta=exp(pi i/17). Each squared phase is the correct pure phase. The phase differences force projective order 34; the final phase also forces actual order 34. The signs are fixed by permutation descent, rather than by choosing arbitrary square roots of U. Multiplying both half generators by -1 gives the separate sign-character twist and still preserves their squares; it changes the chosen lift. The tensor permutations select the displayed lift.

The fresh analytic replay encloses these polynomial expressions using the existing rational Gaussian loop bounds and rigorous seventeenth-root balls. Matrix multiplication and outward rounding propagate all errors. It reports upper bounds for square, braid and central residuals as consistency checks, separately from their exact proofs. Omitting both alternating-channel signs is a negative control whose braid residual is rigorously separated from zero. Neither the ball centers nor a floating eigendecomposition are treated as exact operators.

## Central character and linear normalization

Rotate all three points counterclockwise once. Every pair separation winds once, so the central full twist is exactly

\[
Z=(R_1R_2)^3=\exp(2\pi i h(A+B+C))=\zeta^4 I.
\]

In particular det R1=det R2=zeta^9 and Z has order 17. The determinant check is (zeta^4)^5=(zeta^9)^6=zeta^3. The representation is already linear on B3. It descends projectively to PSL2(Z), but its current linear lift does not kill the center.

A common character twist does kill the center and determinant simultaneously:

\[
T_i=\zeta^5R_i,\quad (T_1T_2)^3=I,\quad
(T_1T_2T_1)^2=I,\quad \det T_i=1.
\]

Thus T is a linear PSL2(Z) representation. This twist changes its squared generators to zeta^10 U,zeta^10 V; it must not be silently substituted for the original pure-loop normalization. Positive braids and the opposite orientation likewise must not be mixed.

## Exact algebraic classification and replay

Tuba–Wenzl Proposition 2.7 and Main Theorem 2.9 classify simple five-dimensional B3 representations using the generator eigenvalues and the fifth root gamma of their determinant. Equivalently one can specify the central scalar. In this case

\[
\gamma=\zeta^{12},\qquad \gamma^5=\zeta^9,\qquad
\gamma^6=\zeta^4.
\]

The implementation evaluates their ordered triangular formulas with these inputs in Q[t]/Phi17(t). It checks the braid relation, central scalar and orders by exact matrix products, and evaluates every one of the twenty nonvanishing simplicity polynomials of Proposition 2.8. The matrices are retained as sixteen rational coefficients per entry; no transcendental approximations enter these checks. Their coefficients are cyclotomic integers and their determinants are units, giving a realization in GL5(Z[zeta]). The actual analytic extension is simple because any invariant subspace is invariant under its already-certified pure squares. The classification therefore identifies the cyclotomic model with the KZ extension up to one simultaneous conjugation. This is an equivalence-class certificate, not an explicitly computed conjugating matrix in the existing chart.

Run `PYTHONPATH=src python scripts/verify_asterion_braid.py` to regenerate the source-bound certificate and ledger in `results/asterion-half-braid`. Run the same command with `--check` to reconstruct everything from source and reject a stale or corrupted result. The algebraic model is also checked independently of the analytic loop replay; fast receipts explicitly say that the loops were not rerun. Regression tests independently decode the retained field matrices, reject a changed coefficient, reject the omitted swap signs, and replay the bounded analytic reconstruction.

## What this says about the countable image

We have explicit matrices, exact relations and an arithmetic realization, not a complete abstract presentation of their image. Verified relations include the B3 braid relation, R1^34=R2^34=I, central Z of order 17, and the degree-five minimal polynomial fixed by the displayed simple spectrum. A matrix polynomial is a relation in the representation algebra; it must not be advertised as a relator in a group presentation.

After the common twist, set s=T1 T2 T1 and t=T1 T2. Then s^2=t^3=I and t^(-1)s=T1 has order 34. Consequently the normalized image is a quotient of the hyperbolic triangle group Delta(2,3,34). Its faithful or nonfaithful status is not determined here. A complete presentation requires the full normal kernel of that triangle-group map (and tracking the central character to reconstruct the original lift), or a proof that the exhibited kernel relations generate it. Word search can provide additional exact relators or prove that particular words are nontrivial in the exact field model; a finite search cannot certify completeness. The existing compact and Zariski closure theorem supplies neither this kernel nor a word-approximation rate.

The canonical endpoint associator, an explicit same-chart algebraic conjugator and the dense-image kernel remain open. The other higher-weight and double-elliptic programmes are unchanged.

## Primary references

Imre Tuba and Hans Wenzl, *Representations of the braid group B3 and of SL(2,Z)*, Pacific Journal of Mathematics 197 (2001), 491–510, [published paper](https://msp.org/pjm/2001/197-2/pjm-v197-n2-p11-s.pdf), Proposition 2.7, Proposition 2.8 and Theorem 2.9. The explicit normal form and classification used here are theirs.

John J. Millson and Valerio Toledano Laredo, *Casimir operators and monodromy representations of generalised braid groups*, [author manuscript](https://www.math.umd.edu/~millson/papers/mtlfinalversion.pdf), introduction and KZ discussion: the S_n-equivariant flat KZ connection gives ordinary braid representations on unordered configuration space. The finite E8 hypotheses and their specialization are replayed here.
