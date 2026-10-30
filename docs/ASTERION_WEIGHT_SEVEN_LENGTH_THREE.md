# The weight-seven length-three E8 arc kernel

30 October 2026 · exact finite computation and structural proof

## The result and its boundary

For the arc algebra and Li map of `ASTERION_PRIMITIVES.md`, the two missing
highest-weight sectors are now determined:

| E8 module | Polynomial highest multiplicity | Ideal highest rank | Arc multiplicity | Lower-length highest columns | Full affine nullity | Kernel multiplicity | Class |
|---|---:|---:|---:|---:|---:|---:|---|
| 1 | 1 | 0 | 1 | 3 | 0 | 0 | none |
| 248 | 14 | 5 | 9 | 4 | 6 | 1 | D²P₂₄₈ |

Combining these with the seven previously certified sectors gives

\[
K_7^{(\mathrm{length}\,3)}
 =V_{248}\oplus V_{3875}\oplus V_{30380}\oplus V_{147250}
 =D\bigl(K_6^{(\mathrm{length}\,3)}\bigr).
\]

The four highest classes are respectively D²P₂₄₈, D³F_Q, DP₃₀₃₈₀ and
D²P₁₄₇₂₅₀. Their total dimension is **181,753**. There is **no new primitive
relation at weight seven and length three**. The last seven-sector conclusion
reuses the earlier receipts; those longer searches were not repeated for this
completion.

This is not the full weight-seven classification. In particular, the
weight-seven length-four, Li-degree-three kernel is not computed here. The
remaining longer-length contributions must also be computed or ruled out, and
their products, syzygies and possible primitive quotients must be settled.
There is no conclusion about finite generation or all-weight stabilization.

## Independent reconstruction of the source dimensions

At total jet degree four the trivial, standard and alternating S₃
multiplicities in the jet-label polynomial representation are (4,5,1).
The exact Freudenthal reconstruction of the three Schur functors gives

\[
[\mathbf1](\operatorname{Sym}^3g,S_{21}g,\Lambda^3g)=(0,0,1),
\qquad
[V_{248}](\operatorname{Sym}^3g,S_{21}g,\Lambda^3g)=(1,2,0).
\]

Thus the ambient highest multiplicities are 1 and 4+5·2=14. This uses
`tensor_cube_character_receipt`, which reconstructs the Schur characters from
adjoint weights and exact Freudenthal subtraction, rather than importing the
two multiplicities being tested. The complete reconstruction is retained in
`results/asterion-primitives/w7-schur-reconstruction.json`.

Independently, the established highest solver enumerates the four jet shapes
(0,0,4), (0,1,3), (0,2,2), (1,1,2). It finds one singlet highest vector in
49,376 weight-zero monomials and fourteen adjoint highest vectors in 16,986
weight-θ monomials. Rational reconstruction is followed by exact annihilation
under all eight raising operators. Independence and the matching Schur
multiplicity certify completeness over Q; modular nullity alone is not used
as the answer.

There is no singlet in g⊗I. Its adjoint highest space has dimension one,
recomputed with the Ω=2 constraint on the quadratic pair. The five maps
z^[4−k]D^k(i), k=0,…,4, give five independent adjoint ideal highest vectors.
Their rational rank is five. It becomes six after adjoining D²P₂₄₈. Hence
the source arc multiplicities are exactly 1 and 14−5=9, and the known
translated adjoint is nonzero modulo the ideal. Both these ranks are checked
again by independent fraction-free elimination.

## Exact lattice ranks and why projection proves completeness

The highest columns include all lengths at most three: 1+3=4 columns for the
singlet, and 14+4=18 for the adjoint. The lower columns are explicitly retained;
they are essential because a leading symbol can acquire a lower-length
correction in an affine null lift.

The computation retains the coefficients of lattice oscillator monomials
whose Cartan indices belong to {0,1}. This is a linear map on the **output**
of the Frenkel–Kac evaluator. No intermediate state is truncated. For speed,
root-only words are evaluated by the exact vertex-product identity

\[
Y(e^a,z_1)Y(e^b,z_2)Y(e^c,z_3)|0\rangle
=\epsilon(b,c)\epsilon(a,b+c)
 \prod_{i<j}(z_i-z_j)^{(a_i,a_j)}
 \exp\!\left(\sum_{m>0}\frac{\sum_i a_i(-m)z_i^m}{m}\right)
 e^{a+b+c},
\]

expanded in |z₁|>|z₂|>|z₃|. The package basis signs are included. Negative
Heisenberg modes are commuted to the left, keeping their exact affine
commutator corrections, before output coordinates are taken. One-, two- and
three-root formulas use the existing cocycle, Schur coefficients and 8! integer
scale. Tests compare the result with projection of the original full mode
calculation, including weight-seven words, mixed Cartan/root words and cache
reuse across distinct full lattice weights.

The retained matrices have sizes **52×4** and **65×18**, with rational ranks
**4** and **12**. The independent verifier clears column denominators and
uses integer Bareiss elimination; it does not call the production rational
rank routine. It also checks the polynomial columns, their independence,
raising equations and Schur completeness. With `--lattice`, every retained
image is regenerated and compared exactly.

A projected rank is only a lower bound on full rank. Here the complementary
upper bounds are attained by independently known full null lifts:

* The singlet matrix already has full column rank four, so its full lattice
  map has no null vector.
* The five independent ideal symbols have affine null lifts: I is the
  quadratic affine singular module, and multiplication and translation
  preserve its affine null ideal. Finite E8 complete reducibility permits
  highest lifts with those highest symbols.
* D² of the existing weight-five adjoint null lift is a sixth full null
  vector. Its symbol is independent of the ideal's five symbols.

Consequently the adjoint full nullity is at least six, while projected rank
twelve bounds it by 18−12=6. Equality follows. Its six null symbols consist
of five ideal directions and one surviving kernel direction. This also rules
out a hidden lower-length null direction. The independently checked ranks of
the lower-column image matrices are three and four.

The conclusion is therefore over Q and uses exact null identities and rank
bounds; it is not a conjecture based on one or several modular primes.

## An explicit representative and affine lift

Write B_rs=B(x^[r],x^[s]), u=e_θ and use divided jets. A representative of the
sole surviving adjoint class is

\[
\begin{aligned}
D^2P_{248}={}&u^{[0]}(240B_{04}-132B_{13}-128B_{22})\\
 &+u^{[1]}(48B_{03}-200B_{12})\\
 &+u^{[2]}(-56B_{02}-90B_{11})-72u^{[3]}B_{01}.
\end{aligned}
\]

With K_rs=Σ_a [u,t_a]^[r](t^a)^[s], an explicit full affine null lift is

\[
\boxed{\operatorname{Sym}(D^2P_{248})
 +\operatorname{Sym}(-80K_{05}-1076K_{14}-530K_{23})
 +18420u^{[6]}.}
\]

These are exactly the double derivatives of the retained weight-five symbol
and correction. The identities are checked term by term, not merely modulo
the ideal. The serialized representative has **2,131 symbol terms and 217
correction terms**, in the existing symbol/correction/SHA256 format. The
original weight-five affine lift was independently replayed through the
original, unprojected lattice evaluator and has zero image; the replay is
retained as `w7-source-null-replay.json`. Translation commutes with PBW
symmetrization and preserves the affine null module, proving the displayed
lift null without requiring a large second full lattice expansion. There is
no new primitive for which an additional null lift is needed.

## A structural argument and the higher-weight implication

On divided-jet symbols define F(x^[r])=(r+1)x^[r−1] for r>0 and F(x^[0])=0.
Extend it by derivations. With D(x^[r])=(r+1)x^[r+1] and H the conformal-weight
operator, direct computation gives [F,D]=2H. For the weight-two quadratic
module I, FI=0 and

\[
F D^k I=k(k+3)D^{k-1}I.
\]

Thus F descends to the arc quotient. On the Li associated graded it is the
leading-length action of L₁; the affine Möbius relations induce the same
commutator, and the Li map is compatible with these actions.

In either algebra F is locally nilpotent. If a positive-weight vector v of
weight n had Dv=0, choose m maximal with F^m v≠0. Repeated commutation gives

\[
0=F^{m+1}Dv=(m+1)(2n-m)F^m v.
\]

Since F lowers weight and positive current length has positive minimum
weight, m<n, so the coefficient is nonzero: a contradiction. Translation is
therefore injective on both algebras in positive weight. In particular
D⁻¹K=K there. A nonzero kernel class cannot disappear under translation, nor
can a class outside K enter K merely by differentiation.

This proves the singlet conclusion independently of the new lattice rank:
its arc multiplicity is one at both weights six and seven, so translation is
an isomorphism between those singlet spaces. The earlier weight-six cubic
singlet has zero kernel, hence so does its weight-seven translate.

It also proves survival of the four existing cubic generator towers at all
higher weights. It does **not** prove that those towers exhaust future cubic
kernels. The length-three arc multiplicities grow, and additional independent
classes remain possible. At weight eight the 248, singlet, 3875 and 30380
sectors still require completion. A useful future strategy is to subtract
the certified translated subspace first and bound the remaining image ranks;
this separates genuine primitive growth from forced derivative growth.

## Replay

From the repository root:

```sh
# Regenerate exact ideal and nonmembership ranks.
PYTHONPATH=src python scripts/build_asterion_w7_ideal.py
# Rebuild both highest bases and every retained lattice image.
PYTHONPATH=src python scripts/build_asterion_w7_rank_certificates.py
# Independently verify ranks, highest bases, ideal spans and every lattice image.
PYTHONPATH=src python scripts/verify_asterion_w7_rank_certificates.py --lattice
# Regenerate the standard representative and completion summary.
PYTHONPATH=src python scripts/assemble_asterion_w7_completion.py
PYTHONPATH=src python -m unittest tests.test_asterion_w7_certificates tests.test_asterion_w7_translation tests.test_asterion_lattice_projection -v
```

The default independent verifier checks the stored matrices without
regenerating their lattice images and explicitly reports that distinction.
The compressed JSON matrices are ordinary gzip files, with deterministic
headers. They contain every highest polynomial column and exact projected
image, not just reported ranks. Source digests are retained. The older direct
full evaluator remains available through
`scripts/complete_asterion_w7_length_three.py`; it can perform an expensive
unprojected sector search independently of the new optimization.
