# Exact reduced principal E8 tangent rigidity

The calculation supplies actual rational diagonal-gauge matrices, invertible
minors, recovery maps and complete sparse tangent constraints at the
semisimple E8 point. There are two independent certificates: a proof using
Whitehead's lemmas and complete reducibility, and an actual selected-Jacobian
rank computation with matching global gauge bounds. The second certificate
does not need Whitehead's cohomology vanishing. Neither certificate claims
that the Jacobian of every spin quadruple was assembled.

## The 170-dimensional cochain space

Use the fixed principal decomposition g=direct-sum V_m with
M={1,7,11,13,17,19,23,29}, where V_m=Sym^(2m)(Q^2). Each irreducible occurs
once. Schur's lemma gives dim End_sl2(g)=8. The Clebsch-Gordan rule gives one
intertwiner per admissible triple a,b,c. For equal input spins a=b, the
flip on output V_c has sign (-1)^(2a-c). Every retained c is odd, so the
sign is -1 and the channel belongs to the alternating square. Counting
unordered inputs gives exactly 170 independent invariant alternating
two-cochains. The code uses all these slots, including their actual E8
coefficients, which in this normalization are all nonzero.

## Actual gauges and their nonzero minors

For an invariant endomorphism S|V_m=s_m I, the infinitesimal basis gauge is

    d1(S)(x,y)=[Sx,y]+[x,Sy]-S[x,y].
    delta kappa_ab^c=kappa_ab^c(s_a+s_b-s_c).

The module constructs the full 170 by 8 rational matrix G. Its rows
(1,1,1) followed by (m,m,1) for m=7,11,13,17,19,23,29 form a lower-triangular
8 by 8 minor. The first diagonal entry is 1/2; the others are the seven
actual nonzero values 2*kappa_mm^1. The matrix rank is computed exactly.
After fixing all principal-action coefficients, the 162 by 7 gauge matrix
has the diagonal minor on the seven rows (m,m,1), again with nonzero
diagonal 2*kappa_mm^1. Both minors and their exact determinants are saved.

The eight gauge scalars can be recovered directly:

    s_1=delta kappa_11^1 / kappa_11^1,
    s_m=(delta kappa_mm^1 / kappa_mm^1+s_1)/2.

When the principal action is fixed, s_1=0 and only the second formula's
first term remains. These are explicit sparse left inverses H with H G=I.
For each nonpivot coordinate j, the equation

    delta kappa_j-G_j H(delta kappa)=0

gives an independent sparse tangent constraint. Their nonpivot columns
form an identity matrix; the code checks this and L G=0 exactly. There are
162 constraints in the full 170-coordinate space and 155 in the fixed
162-coordinate space. These matrices have exactly ker L=image G without
any appeal to a numerical tolerance.

## Why these are all Jacobi tangent directions

Let C^r=Hom(wedge^r g,g) be the finite Chevalley-Eilenberg cochain modules,
with the principal sl2 action. The differentials are sl2-equivariant.
Whitehead's second lemma gives H^2(g,g)=0, so any two-cocycle phi=d1(S).
If phi is invariant, complete reducibility supplies projections to the
trivial isotypic components commuting with the differential:

    d1 P_1=P_2 d1,   P_2(phi)=phi.

Consequently phi=d1(P_1 S), with an invariant endomorphism. This is why
ordinary Whitehead rigidity applies to the reduced invariant cochain
problem; it is not enough merely to quote H^2=0 and ignore equivariance.

The restricted d1 is injective. Whitehead's first lemma says derivations
are inner. If ad(z) commutes with principal sl2, then ad([s,z])=0. The E8
center is zero, so [s,z]=0 for every s. The verified principal decomposition
contains no V_0 and hence the centralizer is zero. Thus z=0, and the only
invariant derivation is zero.

It follows that ker(d2|invariants)=image G has dimension eight, so the
linearized Jacobi differential on 170 variables has rank 162. Every one of
the eight principal-action rows (1,m,m) changes by s_1/2. Fixing these rows
therefore imposes precisely s_1=0 on the eight-dimensional cocycle space,
leaving seven gauge directions. On the remaining 162 cochain variables,
the Jacobi differential has rank 162-7=155.

These ranks are theorem-derived from computed gauge data and stated
external results. They are not described as measured ranks of an assembled
dense Jacobi matrix. The sparse L matrices are complete equivalent tangent
equations, because their kernel and the Jacobi tangent kernel have now been
proved to be the same space.

## Independent literal-Jacobian ranks 155 and 162

The exhaustive receipt also differentiates actual compiled quadratic Jacobi
equations at the actual E8 coefficients. It uses relative coordinates
kappa_v(epsilon)=kappa_v(1+epsilon eta_v), which are invertible tangent
coordinates because all 170 reference coefficients are nonzero. Every
admissible intermediate equation coordinate is included in each declared
panel, including spins outside M. Rows are normalized to primitive integers.

The deterministic anchor-seven scan reaches rank 155 after 161 panels,
compiling 1,947 equation coordinates, including 1,379 outside M. It retains
155 independent rows from 102 distinct panels; 117 of those selected rows
have intermediate spins outside M. These last counts describe this exact
certificate, not a claim that the same number of outside equations is
indispensable in every possible certificate. The selected rows have 1,858
nonzero coefficients. Their source panel, equation index, intermediate
spin, primitive coefficients and elimination pivot are recorded.

The actual 155-row rank gives a lower bound on the full fixed-action Jacobi
rank. Seven independent exact diagonal gauge directions are in the kernel
of every full Jacobi row because d2*d1=0, an immediate consequence of source
Jacobi and differentiation of exact basis changes. Thus the rank is at most
162-7=155, supplying a matching upper bound without Whitehead.

Seven additional actual panels (1,1,m,m), m>1, yield the principal-only
relative rows eta_111-eta_1mm. They have rank seven on the eight principal
action coordinates and zero entries on the 162 nonprincipal coordinates.
Combine their seven pivot columns with the 155 nonprincipal pivot columns
above. The corresponding 162-row minor has block form

    [[J_155, unknown principal columns],
     [    0, P_7                     ]].

Both diagonal blocks are nonsingular. This proves the full 170-coordinate
Jacobi rank is at least 162, irrespective of the unrecorded block. The eight
independent global gauge directions give rank at most 170-8=162. Hence both
Jacobian ranks are now independently certified by actual equations and
matching gauge bounds. It is unnecessary to manufacture or store the whole
dense Jacobian to establish this result.

`replay_jacobian_certificate` recompiles every retained source panel, checks
the literal rows and tags, replays integer elimination and verifies all
gauge annihilations. It also recompiles the seven principal-only rows.
The rank computation initially took about 61 seconds and source/rank replay
brought the complete check to about 89 seconds in the retained environment;
these timings are workload observations, not complexity bounds.

## Smooth local classification and exact orbit membership

The diagonal gauge stabilizer is actually trivial, not merely finite. The
self-channel (m,m,m) transforms by lambda_m, and every such reference
coefficient is nonzero. Therefore each scale is recovered globally on the
orbit by

    lambda_m=kappa_prime_mmm/kappa_mmm.

The entire orbit is the graph of the Laurent-monomial equations

    kappa_prime_abc/kappa_abc=lambda_a lambda_b/lambda_c.

It is consequently a closed embedded eight-dimensional torus inside the
open ambient torus where all 170 coefficients are nonzero. Fixing the
principal action is precisely lambda_1=1 and gives a seven-dimensional
torus. `finite_orbit_membership` recovers these unique scales and checks
every one of the 170 equations exactly. Rejection does not classify other
Jacobi components.

The orbit supplies local Krull dimension at least eight, or seven in the
fixed-action slice. The certified tangent dimensions give the same upper
bounds. Equality makes the local rings regular and therefore smooth over
the characteristic-zero field. Since the locally closed orbit has full
dimension through a smooth point, it is open near that point; gauge
translation gives openness along the entire orbit. Thus compatible formal
deformations specializing to this E8 point are uniquely diagonal gauge
with scales specializing to one. This is stronger than a bare tangent count.

Inside the full-support Jacobi locus, this orbit is both open and closed.
It is connected, so it is exactly the connected component containing the
reference E8 point. This identifies that component only: other full-support
components, zero-channel contraction boundaries and integral forms remain
unclassified. The regular-local and smoothness criteria are standard
algebraic geometry, for example Stacks Project tags
https://stacks.math.columbia.edu/tag/00KU and
https://stacks.math.columbia.edu/tag/00TS .

## Reusable certificates and limits

`PrincipalRigidity.tangent_membership(delta, fixed=...)` recovers the unique
gauge candidate and checks every sparse constraint. A failing row is an
exact functional annihilating all gauge directions but not the proposed
perturbation. Under the stated theorem hypotheses this proves that the
perturbation is not a Jacobi cocycle. `jacobi_derivative` separately evaluates
the actual six-term linearized Jacobi residual on any declared three
vectors; it makes no global rank claim. Finite diagonal gauges and the
two-cochain evaluator allow direct coordinate-transport replay.

This tangent theorem concerns the semisimple E8 point with a fixed
principal-sl2 action. It does not classify the global Jacobi scheme, its
singular contraction points, integral lattices, braided brackets or
quantum structures. In particular the nilpotent Rees boundary is not
semisimple, so the Whitehead hypothesis fails there. That boundary's
deformation and quadratic-completion problems remain substantive targets.

External theorem references: Fiallo's proof notes, including both Whitehead
lemmas, https://www.math.ubc.ca/~reichst/Lie-Algebra-Cohomology.pdf ; Etingof's
complete-reducibility notes,
https://ocw.mit.edu/courses/18-745-lie-groups-and-lie-algebras-i-fall-2020/mit18_745_f20_lec18.pdf ; and the principal/transvectant comparison,
https://arxiv.org/html/2309.08213v3 . These are dependencies, not new results
claimed by Asterion.
