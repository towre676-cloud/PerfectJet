# The exact principal E8 boundary and its quadratic extension

This calculation starts from the 170 actual rational coefficients computed
by `asterion_principal.py`. The principal basis, transvectants, diagonal
contractions and cotangent doubles are classical constructions. Asterion is
the name of this exact implementation and its certificates. No new simple
Lie algebra or literature-priority claim is made.

## A polynomial family with a rigorous singular fibre

Write V_m=Sym^(2m)(Q^2) and M={1,7,11,13,17,19,23,29}. The underlying space is
the 248-dimensional direct sum of these eight modules. With the unnormalized
Cayley transvectants and the recorded principal normalization, define

    [P_a,Q_b]_t = sum_c kappa_ab^c t^(a+b-c-1) T_(a+b-c)(P_a,Q_b).

Only the actual existing E8 channels c in M are used. All 170 coefficients
are nonzero. Every transvection order is odd and at least one, so every
parameter exponent is a nonnegative even integer. This gives a bracket over
Q[t], not a limiting numerical approximation.

For nonzero t let S_t|V_m=t^(m-1). Then

    S_t [x,y]_t = [S_t x,S_t y]_E8.

Every input/output Jacobi coefficient is polynomial in t. For t nonzero it
vanishes by the displayed isomorphism and E8 Jacobi. It is consequently the
zero polynomial and vanishes at t=0 as well. Equivalently, in every nested
term with inputs a,b,c and output d, the power is
(a-1)+(b-1)+(c-1)-(d-1), independent of the intermediate module. This proves
Jacobi for all parameters; sampled tests are not the proof. The exhaustive
receipt independently checks the entire source E8 Jacobi table and every
principal-basis bracket before applying this argument.

The punctured family is isomorphic to E8. Its scaling weights are integers,
so this construction alone supplies no nontrivial monodromy. A connection,
its regularity, a compatible pairing and its gauge equivalence class are
additional data and must be studied separately.

## The sixteen surviving channels

At t=0 exactly sixteen first-transvectant channels survive. Eight are
[V_1,V_m]->V_m with coefficient 1/2. The remaining coefficients are:

| Inputs | Output | Coefficient |
| --- | --- | --- |
| 7,7 | 13 | -1/2 |
| 7,11 | 17 | 1/2 |
| 7,13 | 19 | 1/2 |
| 7,17 | 23 | -1/2 |
| 7,23 | 29 | 1/2 |
| 11,13 | 23 | 1/2 |
| 11,19 | 29 | 1/2 |
| 13,17 | 29 | 1/2 |

The 154 higher-transvectant channels vanish. The result is
sl2 semidirect n, where n has dimension 245. This is a projected,
channel-weighted first-transvectant algebra. The eight polynomial degrees
are not closed under the unrestricted ordinary Poisson bracket; omitted
degrees must not be silently reintroduced.

The lower-central ideals of n have dimensions 245,207,145,59,0. Their module
supports after the first are {13,17,19,23,29}, then {19,23,29}, then {29}.
The derived-series dimensions are 245,207,59,0. The center of n is V_29,
dimension 59. Its abelianization is V_7 direct sum V_11, dimension 38.
The full 248-dimensional boundary algebra is perfect and has zero center.

These are exact module-image certificates. Each block is irreducible for
the verified principal sl2 action. A nonzero equivariant channel therefore
maps onto its complete target block. The receipt supplies an actual
highest-vector bracket witnessing every nonprincipal surviving channel;
iterating the resulting supports gives the exact ideals, not merely upper
bounds. The chain (ad x^14)^3(y^22) is nonzero and passes successively through
V_17,V_23,V_29, proving nilpotency class four.

## All diagonal polynomial contractions and complete small cuts

For any integral weights w_m with w_1=0, the necessary and sufficient
condition for the corresponding diagonal scaling to extend polynomially
to zero is

    w_a+w_b-w_c >= 0 for every one of the 170 actual channels.

This gives an exact rational polyhedral cone in seven variables. It is
pointed: the slots (m,m,1) imply w_m>=0. It is full-dimensional: the all-one
point on the seven nonprincipal modules makes every nonprincipal channel
inequality strict. If any nonprincipal weight is zero, closure under the
nonzero channels forces all seven to be zero; the receipt checks each such
closure explicitly.

The complete binary box has only two admissible points: all-zero and
all-one. The all-one contraction has abelian 245-dimensional radical. In
the complete ternary box {0,1,2}^7, exactly 129 points are admissible: zero
and all 128 choices in {1,2}^7. For every nonzero ternary point the radical
is at most two-step nilpotent: any surviving nonprincipal bracket has two
weight-one inputs and a weight-two output, whose further radical brackets
vanish. These are complete bounded-box results; no global enumeration of
extremal rays or contraction isomorphism classes is claimed.

## The invariant-form obstruction and the 496-dimensional remedy

Pulling back the E8 Killing form by S_t gives block valuations
0,12,20,24,32,36,44,56. Its limit has rank three and radical n. More strongly,
every invariant symmetric form on the boundary has radical containing n.
The proof is short. Schur's lemma makes the eight pairwise nonisomorphic
sl2 modules mutually orthogonal. For m>1, [V_m,V_m] has no V_1 component in
the boundary. Therefore invariance gives

    B([s,x],y)=B(s,[x,y])=0  (s in sl2; x,y in V_m).

Since [sl2,V_m]=V_m, B vanishes on each such block. Only a scalar multiple
of the Killing form on sl2 remains. Thus the space of invariant symmetric
forms is one-dimensional and their maximum rank is three. A nondegenerate
invariant pairing cannot be restored inside these same 248 directions by
a rescaling trick.

The reusable cotangent construction enlarges any Lie algebra g to
g semidirect g*, with

    [(x,xi),(y,eta)]=([x,y],ad_x*eta-ad_y*xi),
    (ad_x*eta)(z)=-eta([x,z]),
    <(x,xi),(y,eta)>=xi(y)+eta(x).

For this boundary the dimension is 496. The Gram matrix is [[0,I],[I,0]],
so the pairing is nondegenerate with real signature (248,248). Both primal
and dual halves are isotropic, and the dual half is an abelian ideal.
Jacobi follows because the coadjoint action is a representation, which is
the transpose of base Jacobi. Invariance follows by expanding both sides
to zeta([x,y])-eta([x,z])+xi([y,z]). The implementation checks the entire
finite coadjoint transpose table. It does not assert Jacobi for an arbitrary
user-supplied base bracket without a separate base proof.

There is also a sharp dimension bound from the form obstruction. If this
248-dimensional boundary embeds in any Lie algebra D with a nondegenerate
invariant symmetric form, the restricted radical R contains n and hence
has dimension at least 245. The map R -> (D/g)* sending r to evaluation
B(r,-) is well-defined and injective: a vector in its kernel is orthogonal
to all of D and is zero. Therefore dim D is at least 248+245=493. The
canonical cotangent construction supplies dimension 496, leaving the
unrestricted minimum among 493,494,495,496 unresolved. If the embedded
248-dimensional algebra must be isotropic, the same argument gives the
lower bound 496, achieved by the cotangent double. The double is therefore
minimal for isotropic embeddings only. Quotienting by the three dual
principal directions does not make the canonical pairing descend and is
not a construction of a 493-dimensional quadratic completion.

## Hypergeometric continuation is a separate research problem

Classical recoupling coefficients are 6j symbols, expressible as terminating
balanced 4F3(1) series. Quantum and elliptic extensions are established
mathematics. Jacobi is a weighted quadratic cancellation involving the
actual E8 coefficients and recoupling matrices; universal recoupling
identities alone do not make arbitrary coefficients into E8. Intermediate
spins outside M must be included when comparing three bracket trees.

Replacing factorials by q-factorials is not a validated quantum E8 lift.
For the standard Drinfeld-Jimbo cobracket, delta(sum e_i) is proportional
to sum h_i wedge e_i, which does not lie in wedge^2 of the principal sl2.
The classical principal embedding is therefore not a Lie-bialgebra
embedding for that standard structure. A compatible twist, coideal or
quasi-Hopf formulation needs its own existence and coherence proof.

The precise next targets are the boundary's deformation/cohomology scheme,
global contraction support classification, and compatible connection or
metric extensions. Each can fail; certificates of obstruction are useful
outcomes. Neither new physics nor a new finite-dimensional simple type
follows from the Rees family alone.

Primary comparisons: Abdesselam and Thomas (2024),
https://arxiv.org/html/2309.08213v3 ; NIST 6j/4F3 formula,
https://dlmf.nist.gov/34.4#E3 ; Rosengren,
https://arxiv.org/html/math/0312310v1 ; Delius and Gould,
https://arxiv.org/html/q-alg/9605025v2 ; standard Lie-bialgebra formula,
https://link.springer.com/article/10.1007/s00220-021-04188-7 ; and the explicit
2025 E8 models and contraction discussion of Cabrera, Draper and Garvin,
https://link.springer.com/article/10.1007/s13398-025-01768-3 . These comparisons
do not establish priority for this particular computed principal boundary.
