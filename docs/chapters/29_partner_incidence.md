# Partner incidence over the full sextic space

The partner question asks, for a binary sextic f and a degree N, whether some nonzero form g of degree N satisfies the correction gates (f,g)_3 = (f,g)_5 = 0. The set P_N of sextics whose kernel ker L_N(f) exceeds its generic dimension is closed and GL2-invariant. Earlier releases studied P_N on two-parameter families. Release 0.14.0 studies it in the full seven-dimensional space of sextics, which is the formal frontier this atlas has listed since 0.1.0.

## Two reductions that make the full space computable

**Lines find hypersurfaces.** A line f0 + t f1 meets every hypersurface component of P_N whose defining invariant does not vanish at f1, and a generic line misses every component of codimension two or more. Along the line, the exact one-parameter locus (`loci.rank_locus`) is therefore the restriction of the hypersurface part of P_N. Its degree is the degree of that hypersurface. Dividing invariant monomials of the matching weight by it identifies the defining invariant exactly (`incidence.identify_hypersurface`). On two independent random lines, only two degrees between 3 and 19 have a hypersurface component:
- degree 3, the quartic hypersurface A^2 = B/6;
- degree 12, the quartic hypersurface A^2 = 25B/96.

In both cases the restriction of the invariant equals the locus exactly, so on these lines the hypersurface part of P_N is that invariant hypersurface and nothing else. Every other degree from 3 to 19 has no hypersurface component.

**The slice finds everything else.** Every sextic with at least three simple roots is GL2-equivalent to xy(x-y)(x^3+px^2y+qxy^2+ry^3), with three simple roots at 0, 1 and infinity. Rank conditions on L_N become polynomial ideals in (p,q,r). Saturating by r and by 1+p+q+r removes placements where 0 or 1 is a repeated root. Those sextics reappear at other placements. When the locus is zero-dimensional, `incidence.classify_zero_dimensional` works in the finite algebra Q[p,q,r]/I:
- it computes the Clebsch invariants of the slice form with coefficients in that algebra (`clebsch_over`);
- it inverts A when A is a unit;
- it returns the exact minimal polynomials of the absolute invariants B/A^2, C/A^3 and D/A^5.

If each minimal polynomial is linear, every point of the locus has the same Clebsch point. When that point belongs to a squarefree sextic, the GIT fibre over it is a single orbit, so the locus is exactly one GL2-orbit. Sextics with fewer than three simple roots are, up to GL2, seven fixed forms and the family x^2y^2(x-y)(x-sy). They are checked directly (`degenerate_profile`).

## Classification in small degrees

**Degree 3.** For every sextic, det L_3 = (A^2-B/6)/16, certified in 0.9.0. On the slice, dim ker L_3 >= 2 is a zero-dimensional locus of ten points. Each point has absolute invariants (6,-36,0), which are those of x^6+y^6. Ten is 120 ordered placements divided by the order-12 dihedral stabilizer of the six roots. Among the degenerate forms, only those with a root of multiplicity at least five have a two-dimensional cubic kernel.

**Degree 4.** Every sextic has the quartic partner (f,f)_4, certified in 0.9.0. On the slice, dim ker L_4 >= 2 is zero-dimensional with all absolute invariants 0, which is the octahedral sextic xy(x^4-y^4). Among degenerate forms, only x^6 and x^5y have a larger quartic kernel. Hence dim ker L_4 >= 2 exactly when f is octahedral or has a root of multiplicity at least five.

**Degree 5.** The ideal of 6-by-6 minors of the 8-by-6 matrix L_5 on the slice is zero-dimensional of length 20. In Q[p,q,r]/I, B-486A^2, C+26244A^3 and D+419904A^5 reduce to zero and A is a unit. These are the absolute invariants of x^6+(40/7)x^3y^3+y^6, the C3 sextic at the 40/7 obstruction. Twenty is 120 placements divided by its order-6 stabilizer, so every point is a reduced point of that single orbit. The degenerate forms with a quintic partner are exactly those with a root of multiplicity at least four. These include x^4y(x-y), which is the GL2 class of (x-y)^4(x^2+4xy+y^2) at (+/-16,-9). Therefore:

> A binary sextic has a nonzero quintic g with (f,g)_3 = (f,g)_5 = 0 if and only if it has a root of multiplicity at least four, or it is GL2-equivalent over the algebraic closure to x^6 + (40/7) x^3 y^3 + y^6.

The 7lambda-40 obstruction, found by an ansatz in the earliest archive and rediscovered in 0.3.0, is therefore the only squarefree source of quintic partners. On the slice no sextic has two independent quintic partners.

**Degree 6.** Exact rational Groebner bases of the 6-by-6 minors of L_6 on the slice do not finish. `modular.py` computes the same ideal over a prime field instead:
- it builds all 1005 nonzero minors by fraction-free Bareiss modulo P;
- it interreduces them linearly, since polynomials of this degree in three variables span few monomials;
- it decides emptiness away from repeated roots at 0 and 1 with one Rabinowitsch variable.

Modulo 2147483629 and 1000000007 the locus is empty. A global numerical search on the slice agrees: about 1500 Gauss-Newton starts converge only to repeated-root forms. Among degenerate forms, a two-dimensional sextic kernel occurs exactly when there is a root of multiplicity at least four. With evidence modulo two primes rather than a rational proof:

> dim ker L_6(f) >= 2 if and only if f has a root of multiplicity at least four.

The engine is calibrated on degree 5. Modulo P it reports the quintic locus nonempty and the two-dimensional quintic locus empty, which matches the exact rational results above.

**Degree 7.** The 8-by-8 minors of the 12-by-8 matrix L_7 on the slice give 493 nonzero polynomials. Modulo 2147483629 and 1000000007, the locus is empty away from repeated roots at 0 and 1. A numerical search with 3000 starts converges only to repeated-root forms. Among degenerate forms, the septic kernel is nonzero exactly when there is a root of multiplicity at least four. With the same evidential status as degree 6:

> ker L_7(f) != 0 if and only if f has a root of multiplicity at least four.

Across degrees 5 to 7, then, a root of multiplicity at least four is the uniform source of extra partners. The C3 class at 40/7 in degree 5 is the only exception.

**Degree 8.** No line meets a hypersurface component, so P_8 has codimension at least two. The C3 family x^6+lambda x^3y^3+y^6 has the partner g_8 = xy(x^6+y^6-(7/20)lambda x^3y^3) for every lambda. Its gate coefficients are polynomials of degree at most two in lambda, and they vanish at five values (`c3_degree8_certificate`). On that family, the invariants satisfy exactly two relations of lowest weight (`c3_curve_relations`):

R5 = AB^2 + BC/6 - 9D/2 = 0 and C^2 = 6B^3.

These relations hold everywhere the degree-8 kernel is nonzero. On the slice, random projections det(R L_8) cut out a set containing the true locus. Modulo 2147483629 and 1000000007, the full three-variable radical test shows that R5 and C^2-6B^3 vanish on every point of it with no repeated root at 0 or 1. As a control, A does not vanish there. Plane sections meet the curve in 16 points, and on them both relations lie in the ideal itself. A global Gauss-Newton search gives the same answer: 557 squarefree degree-8 points on the slice all satisfy both relations to about 1e-14. The 26 points from three non-symmetric families satisfy them too.

The solutions of the two relations in weighted projective space form a single rational curve, parametrized by (A, B=6t^2, C=36t^3, D determined by R5). The C3 family maps onto it. Its special members are:
- (x^3-y^3)^2, the GL2 class of x^2y^2(x-y)^2;
- the octahedral sextic, at (lambda^2+50)^2 = 0;
- x^3y^3, at lambda = infinity.

Every sextic on that curve, apart from the boundary, is therefore GL2-equivalent to a member of the C3 family, which has an automorphism of order three. Among degenerate forms, the degree-8 kernel is nonzero exactly for those with a root of multiplicity at least four, and for x^3y^3 and x^2y^2(x-y)^2. Hence, with the forward direction resting on two primes:

> ker L_8(f) != 0 if and only if f has a root of multiplicity at least four or f has a projective automorphism of order three, that is, f is GL2-equivalent to x^6+lambda x^3y^3+y^6 for some lambda, or to x^3y^3.

This explains the earlier degree-8 observations. Order-three sextics are bielliptic, because D3 contains involutions, so the earlier bielliptic observation is a consequence. The lines b = 15 +/- 3a/2 satisfy R5 but not C^2 = 6B^3, which is why they carry no partner. The cubic drop curve on the symmetric surface satisfies both relations; it is a second parametrization of the same C3 curve. A sextic like x(x^5-y^5), whose B, C and D do not lie on the curve, has no degree-8 partner, as predicted.

**Degree 12.** The hypersurface part of P_12 is A^2 = 25B/96, where the covariant G of 0.9.0 is a partner. Lower-dimensional components of P_12 are not excluded by this method.

**Remaining components.** Lower-dimensional components of P_N for N >= 8, and of P_12 beyond its hypersurface, remain open. Degrees 9 to 11 have not been examined on the slice.

## Rational certificates and the classification through degree 19

Release 0.14.0 adds two external computer-algebra checks: `scripts/singular_partner_check.py` uses Singular over a prime field, and `scripts/msolve_partner_check.py` uses msolve over Q. They are optional verifiers; the dependency-free core does not need them.
- **The system.** For each degree N and kernel threshold k, a few random integer projections det(P L_N S) on the slice vanish wherever dim ker L_N >= k, so their common zero set contains the locus. A Rabinowitsch variable removes repeated roots at 0 and 1.
- **Emptiness.** msolve decides over Q whether that system has a complex solution. An empty superset means an empty locus.
- **Invariant relations.** Multiplying the Rabinowitsch polynomial by an invariant relation J tests whether J vanishes on every point of the locus.
- **Controls.** The control relation A fails wherever the locus is nonempty, as it must, and Singular modulo 2147483629 and 1000000007 agrees with every msolve verdict. The receipts are in `results/partner_incidence_solver_receipts.json`.

Points of the locus have three simple roots, so their invariants do not all vanish. In degrees 3, 4, 10 and 14 the relations give B = C = D = 0, or B = 6A^2 with C = -36A^3 and D = 0, and these force A to be nonzero. The Clebsch point is then that of the octahedral sextic or of x^6+y^6. Both are stable, so the GIT fibre over that point is a single GL2-orbit. Combined with the exact profiles of the degenerate root patterns (`degenerate_profile`) and the exact partners of the named sextics, this gives, over the algebraic closure, trusting the msolve computations:

| N | Extra correction-free partners occur exactly when f |
|---|---|
| 3 | satisfies B = 6A^2; dim ker >= 2 exactly for x^6+y^6 or a root of multiplicity >= 5 |
| 4 | (beyond (f,f)_4) is octahedral xy(x^4-y^4) or has a root of multiplicity >= 5 |
| 5 | has a root of multiplicity >= 4, or is equivalent to x^6+(40/7)x^3y^3+y^6 |
| 6 | (beyond f itself) has a root of multiplicity >= 4 |
| 7, 9, 11, 13, 15, 17, 19 | has a root of multiplicity >= 4 |
| 8 | has a root of multiplicity >= 4, or an automorphism of order three (x^6+lambda x^3y^3+y^6, or x^3y^3) |
| 10 | has a root of multiplicity >= 4, is x^3y^3, or is equivalent to x^6+y^6 |
| 12 | satisfies A^2 = 25B/96 (the hypersurface, which contains the degenerate cases) |
| 14 | has a root of multiplicity >= 4, is x^3y^3, or is octahedral |
| 16, 18, 20 | has a root of multiplicity >= 4, or is x^3y^3 |

Every exceptional class beyond a fourfold root is a sextic with extra symmetry:
- the dihedral sextic x^6+y^6, in degrees 3 and 10;
- the octahedral sextic, in degrees 4 and 14;
- the order-three family, in degree 8;
- its 40/7 member, in degree 5.

The only other exceptions are the two invariant hypersurfaces in degrees 3 and 12. This is a computer-assisted classification: its rational steps rest on msolve's correctness, and degrees 6 to 8 also have the independent dependency-free modular evidence above.

## Scope

The line method is exact on each line it uses. That the lines are generic is supported by agreement between independent random lines; the method does not prove genericity. The slice computations are exact, and the orbit identifications rest on the classical fact that Clebsch invariants separate orbits of squarefree sextics. Degrees 6 to 20 are settled over Q by msolve (an external solver) and modulo two primes by Singular and the dependency-free engine. Degrees 21 and above remain open.
