# An explicit invariant quartic class at conformal weight six

The exact module `asterion_quartic.py` proves that the length-four, Li-degree-two component of the level-one E8 arc algebra contains exactly one invariant line. It supplies a coordinate-independent representative,

\[
 \boxed{F_0(x,y)=2B(x,y)^2-B([x,y],[x,y])-2B(x,x)B(y,y),}
\]

where \(x\) is the zero jet and \(y\) is the divided first jet. Thus every monomial has two zero jets and two first jets: its current length is four, Li degree two and conformal weight six. The squared tensor norm is **947,856**, proving that the displayed polynomial has a nonzero arc class. This adds one dimension to a lower bound which had counted only current lengths at most three.

In coordinates, if \(x_a^{[r]}\) is the current variable associated with \(t_a\), the universal elements in this formula are \(x=\sum_a t^a x_a^{[0]}\), \(y=\sum_a t^a x_a^{[1]}\). This uses \(B\) to identify polynomial functions and symmetric tensors and fixes the inverse-metric coefficients.

The individual image of \(F_0\) in the associated graded simple VOA is not computed here. Separate invariant counts force at least one weight-six kernel singlet, but do not determine whether it occurs in Li degree two or three. No affine null lift of this quartic is claimed.

## Grounded finite-dimensional input

Write \(V=\mathfrak e_8\), and normalize the invariant form by
\(B(h_i,h_j)=A_{ij}\), \(B(e_\alpha,e_{-\alpha})=1\). Long roots have squared length two; the Killing form is \(60B\), and is not substituted for \(B\) in this calculation. Let

\[
 C=\sum_a t_a\odot t^a\in\operatorname{Sym}^2V,
 \qquad \Omega=\sum_a\operatorname{ad}(t_a)\otimes\operatorname{ad}(t^a).
\]

Symmetric tensors are embedded by averaged symmetrization. Their bilinear form is the restriction of \(B^{\otimes n}\). In particular
\(\langle x\odot y,u\odot v\rangle=(B(x,u)B(y,v)+B(x,v)B(y,u))/2\),
\(\langle C,C\rangle=248\), and \(\langle C,x\odot x\rangle=B(x,x)\).

The earlier projected-polarization certificate establishes, from actual highest vectors, eight raising checks, Weyl dimensions and split-Casimir eigenvector equations,

\[
 \operatorname{Sym}^2V=\mathbf1\oplus R_{3875}\oplus I_{27000},
 \qquad \Omega=(-60,-12,2).
\]

It also proves \(I_{27000}\,V=\operatorname{Sym}^3V\) by actual nonzero projected-polarization scalars on every irreducible cubic summand. These are replayed dependencies, rather than an assumed external tensor-product table. Put \(I=I_{27000}\) and \(W=I^\perp=\mathbf1\oplus R_{3875}\). The exact projector is
\(P_I=(\Omega+12)(\Omega+60)/868\).

## The full dual identification

Use divided jets \(x=x^{[0]},y=x^{[1]},z=x^{[2]}\), with
\(Dx=y\), \(Dy=2z\). Before relations the length-four, derivative-degree-two sector is

\[
 (\operatorname{Sym}^3V)_x\otimes V_z
 \ \oplus\ (\operatorname{Sym}^2V)_x\otimes(\operatorname{Sym}^2V)_y.
\]

Its first summand is killed entirely by \(I(x,x)\,x\,z\), because \(IV=\operatorname{Sym}^3V\). In the remaining summand the quadratic differential ideal gives precisely:

- \(I(x,x)\,y\,y\), imposing the null-pair constraint in the two x slots;
- \(D I(x,x)\,x\,y\), imposing the null-pair constraint in a crossed x/y pair;
- \(D^2I(x,x)\,x\,x\). Since \(D^2q(x,x)=2q(y,y)+4q(x,z)\) and the x³z summand has died, this imposes the null-pair constraint in the two y slots.

There are no other generating possibilities at this length and derivative degree. A dual tensor \(T\) is therefore symmetric in slots 1,2 and in slots 3,4 and is annihilated by \(P_I\) on every unordered pair. Within-pair symmetries turn one crossed constraint into all four crossed constraints.

Every three-slot symmetrization of \(T\) vanishes. Indeed its pairing with the image of \(I\otimes V\to\operatorname{Sym}^3V\) is zero, by the three pair constraints. That image is the whole symmetric cube by the grounded surjectivity theorem, and the induced symmetric-tensor form is nondegenerate.

This implication can be completed without importing a Schur decomposition. For arbitrary indices write

\[
 (A,B,C',D,E,F)=
 (T_{ab;cd},T_{ac;bd},T_{ad;bc},T_{bc;ad},T_{bd;ac},T_{cd;ab}).
\]

The four triple-symmetrizer equations are

\[
 A+B+D=0,\quad A+C'+E=0,\quad B+C'+F=0,\quad D+E+F=0.
\]

In characteristic zero they are equivalent to

\[
 F=A,\qquad E=B,\qquad D=C',\qquad A+B+C'=0.
\]

The first three say that the two symmetric pairs can be interchanged; the last says that full symmetrization is zero. `pair_slot_certificate()` verifies this equivalence as an exact rank-four equality of rational row spaces on the six slots. Consequently every dual arc tensor lies in
\(\operatorname{Sym}^2W\cap\ker\mu\), where \(\mu\) is ordinary multiplication into \(\operatorname{Sym}^4V\).

Conversely suppose \(T\in\operatorname{Sym}^2W\) and \(\mu T=0\). The pair-interchange symmetry and zero total symmetrization give the Bianchi relation \(A+B+C'=0\). Apply \(P_I\) to slots 1,2. Its action on \(A\) vanishes because that pair belongs to \(W\). The other two images agree: the two crossed terms differ by interchanging slots 1,2, and the symmetric-pair projector satisfies \(P_I(12)=P_I\). Thus twice either crossed image is zero. This proves every crossed null-pair constraint. The dual identification is therefore exact:

\[
 \boxed{(\operatorname{Arc}R)_{\text{length }4,\,\text{Li }2}^{\!*}
 \cong\ker\!\left[\mu:\operatorname{Sym}^2W\longrightarrow\operatorname{Sym}^4V\right].}
\]

The use of a dual space matters: a nonzero dual vector alone proves a dimension bound, not automatically that the same written polynomial survives the quotient. The nonzero self-pairing below supplies the additional argument for this representative.

## The explicit tensor and its nonzero arc class

Identify \(\operatorname{Sym}^2V\otimes\operatorname{Sym}^2V\) with endomorphisms using its induced nondegenerate bilinear form. Consider

\[
 T_0=2\operatorname{Id}-\Omega-2\,|C\rangle\langle C|.
\]

Its eigenvalues on the three actual quadratic modules are

| Module | \(\Omega\) | \(|C\rangle\langle C|\) | \(T_0\) |
|---|---:|---:|---:|
| \(\mathbf1\) | −60 | 248 | −434 |
| \(R_{3875}\) | −12 | 0 | 14 |
| \(I_{27000}\) | 2 | 0 | 0 |

The implementation applies this actual sparse operator to the displayed highest vectors of all three modules and checks these equations again. Thus its tensor is in \(\operatorname{Sym}^2W\). If \(K_1,K_R\) denote the metric Casimir tensors of the two summands of \(W\), then

\[
 T_0=14(K_R-31K_1),\qquad K_1=C\otimes C/248.
\]

Under tensor evaluation on \((x,x;y,y)\), the identity operator gives \(B(x,y)^2\), the rank-one term gives \(B(x,x)B(y,y)\), and

\[
 \langle x\otimes x,\Omega(y\otimes y)\rangle
 =\sum_aB(x,[t_a,y])B(x,[t^a,y])=B([x,y],[x,y]).
\]

This fixes the commutator sign in the displayed formula for \(F_0\). Its evaluation on the full diagonal is identically zero: \([x,x]=0\) and the remaining two terms cancel. Polarization gives \(\mu T_0=0\). The duality theorem therefore puts \(T_0\) in the annihilator of the entire arc ideal in this sector, including all crossed relations.

The tensor is selfadjoint. Its squared norm is its operator-square trace:

\[
 \langle T_0,T_0\rangle
 =(-434)^2\cdot1+14^2\cdot3875+0^2\cdot27000
 =\boxed{947856}\ne0.
\]

Hence \(T_0\) cannot itself belong to the arc ideal, since it annihilates that ideal but has nonzero pairing with itself. The polynomial \(F_0\) represents a nonzero arc class. As an additional coordinate check, \(x=h_0,y=h_2\) gives \(B(x,y)=0\), \([x,y]=0\), \(B(x,x)=B(y,y)=2\), and \(F_0(x,y)=-8\). This evaluation confirms a nonzero polynomial; the annihilator and norm argument proves the stronger nonzero quotient statement.

There are exactly two invariant lines in \(\operatorname{Sym}^2W\), generated by \(K_1,K_R\). Their images obey

\[
 \mu(K_R)=31\mu(K_1)=C^2/8,
\]

by the tensor identity just proved. Since \(\mu(K_1)=C^2/248\ne0\), the invariant kernel is exactly one-dimensional. No assumption about the decomposition of \(\operatorname{Sym}^4V\), or about the absence of a quartic fundamental invariant, is needed.

## What the VOA counts do and do not establish

At weight six the at-most-two-current arc component has three invariant states, whose independent images are certified by its exact affine Gram block of rank three. The length-three arc component has one invariant: the Cartan three-form \(B([a,b],c)\), at the distinct creation modes \((3,2,1)\). No quadratic arc relation can kill this invariant, because all length-three relation sources are copies of \(I_{27000}\otimes V\), which has no invariant. Uniqueness follows from the grounded decompositions \(\operatorname{Sym}^2V=1+3875+27000\) and \(\Lambda^2V=248+30380\): the adjoint occurs exactly once in \(V\otimes V\). The other three-mode partitions have a symmetric equal-mode pair or a symmetric cube and contain no invariant.

Together with the quartic line, this gives at least five weight-six arc singlets. The independent lattice/Freudenthal character has exactly four weight-six VOA singlets. The arc map is surjective and E8-equivariant; taking invariants is exact in these finite-dimensional semisimple modules. There is therefore at least one invariant weight-six arc-map kernel state. This argument leaves open whether the cubic invariant, the explicit quartic invariant, or a relation with higher-filtration corrections supplies that kernel state. It does not declare \(F_0\) to be a null leading symbol.

`quartic_receipt(exhaustive=False)` replays the actual spectral and cubic-surjectivity dependencies, the pair-slot row-space proof, the three sparse operator identities, the nonzero norm and Cartan witness, and the independent Gram/VOA invariant counts. The `exhaustive` flag records orchestration mode; these bounded finite proofs already run in both modes. The module and its tests never build a dense \(248^4\) tensor or assume a retained quartic decomposition table. The contribution is this explicit exact derivation inside the program, without a historical-priority claim.

## A larger character bound and two proved multiplication exclusions

The separate exact engine `asterion_quartic_characters.py` reconstructs the complete characters by Newton identities and finite-weight Freudenthal subtraction:

\[
 \operatorname{Sym}^2W=2\cdot\mathbf1+2\cdot3875+27000+147250+2450240+4881384,
\]

\[
 \operatorname{Sym}^4V=\mathbf1+3875+2\cdot27000+147250+2450240
 +4096000+4881384+70680000+79143000.
\]

Consequently \(\ker\mu\) contains at least \(\mathbf1\oplus3875\), of total dimension **3,876**. The explicit invariant proved above is already the \(\mathbf1\) in this bound; it is not added again. The combined receipt nests the independent character certificate and exposes `quartic_arc_dimension_lower_bound=3876`. The earlier `arc_dimension_lower_bound_increment=1` refers only to the separately explicit invariant proof. Complete weight-six bounds must use the combined 3,876 once, rather than adding 3,876 and one.

There is also a useful upper restriction on the possible kernel modules. Choose the positive invariant Hermitian form coming from a compact real form. Every pair Casimir is selfadjoint. On a tensor annihilated by every \(P_I\), its allowed symmetric spectrum is \(-60,-12\), and its antisymmetric spectrum is \(-30,0\), coming from \(\Lambda^2V=248+30380\). Therefore

\[
 \Omega_{ij}\ \le\ -6(1+\tau_{ij})
\]

as a Hermitian quadratic-form inequality. The six-transposition class sum \(\sum_{i<j}\tau_{ij}\) is zero on the pair-slot solution space; the module checks this directly on the two-dimensional nullspace of its six-slot equations. Summing yields

\[
 C_{\mathrm{total}}=4\cdot60+2\sum_{i<j}\Omega_{ij}
 \le240-72=168.
\]

The actual source highest-weight Casimirs, computed from the inverse Cartan matrix, are \(0,96,124,144,180,200\) for dimensions \(1,3875,27000,147250,2450240,4881384\). Thus the last two modules cannot occur in the kernel. This is a positive-form inequality on the compact representation, not an inequality for the indefinite rational bilinear form used to write the coordinates.

The 27,000 block is also nonzero under multiplication. Take the actual highest quartic \(p=C e_\theta^2\) of weight \(2\theta\). The adjoint multiplication map is, up to a nonzero normalization, its two-plus-two polarization followed by \(P_W\) on both factors. The terms with \(e_\theta^2\) as one pair vanish, because that pair is in \(I\). The remaining part is

\[
 4\sum_a P_W(e_\theta\odot t_a)\otimes P_W(e_\theta\odot t^a).
\]

For its coefficient at \((e_\theta h_0)\otimes(e_\theta h_0)\), weight conservation permits only Cartan inputs. Eight exact projector calculations give

\[
 c=(1/7,0,0,0,0,0,-1/7,0),\qquad
 c^tA^{-1}c=2/49,
\]

so the coefficient is **8/49**, nonzero. This proves that multiplication is nonzero on the unique 27,000 source summand. The source's 1, 3,875 and 4,881,384 blocks have the immediate nonzero products \(C^2,CQ,Q^2\).

Finally the 147,250 block is also nonzero by an explicit highest-vector construction. Form the actual 49-term quartic

\[
 p=P_W(e_{128}e_{243})\,P_W(e_{211}e_{247})\in\operatorname{im}\mu,
\]

with indices in the repository's deterministic Chevalley basis. On quartics use the exact total Casimir
\(C_4=240+2\sum_{i<j}\Omega_{ij}\). Applying \((C_4-200)(C_4-180)\), with primitive rational rescaling after each factor, gives term counts **49 → 1,085 → 1,421**, ending in a nonzero polynomial. The implementation checks that every monomial has root weight \((5,10,15,12,9,6,3,8)\), corresponding to Dynkin weight \((0,0,0,0,0,0,0,1)\), and that all eight simple raising operators kill it. The exact Weyl dimension of this highest weight is 147,250. The independent consistency check \(C_4p'=144p'\) also passes. The module records the vector's SHA256 and includes all exact coefficients in exhaustive mode.

The multiplication image is E8-stable and hence preserved by the total Casimir. Therefore this nonzero highest vector remains constructively in the image and proves the required nonzero 147,250 block. Its highest-weight checks suffice; the proof does not assume that the Casimir filter has removed all other possible summands.

Every possible extra source summand has now been excluded from the kernel by either a nonzero multiplication witness or the positive-form Casimir bound. The multiplicity-two source blocks 1 and 3,875 each map nontrivially to their multiplicity-one targets. Consequently

\[
 \boxed{\ker\mu\cong\mathbf1\oplus3875,
 \qquad\dim(\operatorname{Arc}R)_{\mathrm{length}\,4,\mathrm{Li}\,2}=3876.}
\]

This is an exact finite quartic-sector theorem. It does not classify the complete weight-six arc-map kernel and does not determine the VOA image of the explicit invariant \(F_0\). The nested standalone character receipt deliberately retains its weaker multiplicity-bound scope; the exact result uses that character together with the multiplication and cutoff certificates in `asterion_quartic.py`.
