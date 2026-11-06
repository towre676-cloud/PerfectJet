**Complete classification now available:** see [COMPLETE_WEIGHT7_THEOREM.md](COMPLETE_WEIGHT7_THEOREM.md). The following document retains its earlier proof stage; its open-sector list is superseded.

# Weight-seven quartic singlet, adjoint and 3875 sectors

4 November 2026. Exact finite calculation and structural product proof.

## The theorem

Let g=e8 with roots of squared length 2, let I=V27000 in Sym²g, and let A=J_infinity(Sym(g)/(I)). Let K be the kernel of the canonical map A to the Li associated graded of the level-one affine E8 VOA. Write A_(7,4) and K_(7,4) for conformal weight 7 and current length 4, equivalently Li degree 3.

On the isotypic components of types 1,248 and 3875,

    A_(7,4) = K_(7,4) = 1 + 2 V248 + 2 V3875.

This denotes only the stated isotypic components, not the full quartic sector. Their total dimension is 8,247. Every class in them is a derivative or product of previously established weight-four/five kernel classes. The primitive quotient has multiplicity zero in all three types.

| E8 type | Polynomial source multiplicity | Ideal rank | Arc multiplicity | Kernel multiplicity | New primitive multiplicity |
| --- | ---: | ---: | ---: | ---: | ---: |
|1|5|4|1|1|0|
|248|11|9|2|2|0|
|3875|15|13|2|2|0|

The arc-ideal ranks are newly computed here. The full kernel conclusion is a product-spanning argument using fresh source null replays. It does not infer a kernel from a projected image-rank deficiency.

## 1. Why a small covariant calculation is complete

Put x=x^[0], y=x^[1], z=x^[2], w=x^[3], with D x=y, D y=2z and D z=3w. The three quartic jet shapes have representation spaces

    Sym³g tensor g,   Sym²g tensor g tensor g,   g tensor Sym³g.

The previous exact Schur reconstruction supplies multiplicities(1,3,1) for the singlet,(2,7,2) for the adjoint and(3,9,3) for3875. The three totals are5,11,15. For the middle shape the character is S4+2S31+S22+S211. These dimensions are reconstructed from E8 roots and exact Freudenthal subtraction in quartic_schur_receipt.json.

Instead of expanding millions of monomials, construct explicit equivariant polynomial covariants with these jet shapes. The invariant form identifies polynomials with their coefficient tensors. For type3875, project the output Sym²g tensor to its3875 summand. A covariant is a finite-type homomorphism into the chosen self-dual target.

Exact evaluation at finitely many retained rational E8 points gives ranks7 and9 on the repeated-pair bases, and11 and15 on the complete adjoint and 3875 bases. Because the independent character computation proves that these are the full dimensions, the displayed covariants are bases and the evaluation maps are injective on the complete spaces. This is the critical completeness step: a later coordinate equality verified at these points is then an equality of covariants, not an empirical polynomial identity inferred from samples.

The points are deterministic sparse combinations of the Chevalley basis; every point and evaluation column is serialized. The small-subalgebra choice used to obtain compact points does not restrict the theorem: injectivity on the full E8 covariant space follows from the complete rank and character dimension.

## 2. Pair projectors and the whole ideal source

On Sym²g the known split-Casimir spectrum is(-60,-12,2) on1,3875,27000. Write C=sum_a t_a sym t^a, so <C,C>=248. The spectral projectors are

    P_I = (Omega+12)(Omega+60)/868
        = (372 Id+31 Omega+6 |C><C|)/434,

    P_R = (2 Id-Omega-|C><C|/4)/14,   R=V3875.

The simplification uses Omega²=-10 Omega+24 Id+12|C><C|, which is verified on each of the three spectral summands. Both projectors are selfadjoint for the nondegenerate invariant tensor form.

At length 4 and jet degree 3, every ideal element is a linear combination of

    x^[a] x^[b] D^k q,  q in I,  k+a+b=3.

Up to interchanging the two free currents, the six source choices(k,a,b) are

    (0,0,3), (0,1,2), (1,0,2), (1,1,1), (2,0,1), (3,0,0).

The divided-jet convention gives D^k q(x,x)=k! sum_(r+s=k) q(x^[r],x^[s]). For a repeated-pair covariant F(x;y,z), apply P_I in its two x slots, polarize that quadratic variable, then substitute the six choices. This is precisely the degree-four differential-ideal image.

There are no missing ideal sources of this degree. Complete reducibility of finite E8 modules implies that all target-type components of I tensor g tensor g arise by restricting equivariant maps on Sym²g tensor g tensor g with P_I. Thus applying the pair projector to a complete7- or9-dimensional covariant basis spans all ideal maps, including the equal-free-jet restrictions.

The two induced pair projectors have rank 3. Their idempotence is checked exactly. The six jet substitutions yield complete ideal-coordinate matrices of sizes 42 by 11 and 54 by 15, with ranks9 and13 respectively. The redundant rows are retained deliberately.

## 3. Explicit adjoint basis and surviving products

The middle-shape adjoint basis consists of the seven covariants

    F0=Bxx[y,z],  F1=Bxy[x,z],  F2=Bxz[x,y],
    F3=x B(x,[y,z]),
    F4=[x,[x,[y,z]]],
    F5=[x,[y,[x,z]]],
    F6=[y,[x,[x,z]]].

Here F0 is a basis label, distinct from the scalar quartic F_0 below. Add Bxx[x,w] and [x,[x,[x,w]]] at shape0003, and Byy[y,x] and [y,[y,[y,x]]] at shape0111. This is the complete eleven-dimensional source basis.

The established weight-five adjoint kernel generator is the covariant

    P=20x Bxz-21x Byy-12y Bxy.

One surviving product is [y,P]. A second is the adjoint contraction of z with the established weight-four3875 class F_Q. That class, written as a3875-valued polynomial, is proportional to2P_R(x sym [x,y]). Multiplying by the free second jet and contracting one output slot gives, up to nonzero normalization,

    2x B([x,y],z)+2[x,y] Bxz
      +[x,[[x,y],z]]+[[x,y],[x,z]]
    =2F3+2F2+F4-F6.

The ideal alone has rank 9. Adding either product gives rank 10; adding both gives rank 11. Hence they are independent modulo the ideal and exhaust the two adjoint copies. Both belong to K, so the entire adjoint arc component lies in K and has no new primitive.

The actual stored highest-weight P formula and the F_Q formula are independently checked at dense rational E8 points with nonzero evaluations. The product coupling identity and its coordinate vector are also checked exactly.

## 4. The3875 basis and two P products

For shape0003 use the three P_R-projected symmetric tensors

    (x sym x) Bxw,   (x sym w) Bxx,   x sym [x,[x,w]].

For shape0012 use

    (x sym x) Byz, (x sym y) Bxz, (x sym z) Bxy, (y sym z) Bxx,
    [x,y] sym [x,z], x sym [x,[y,z]], x sym [y,[x,z]],
    y sym [x,[x,z]], z sym [x,[x,y]].

For shape0111 use the first three formulas with x replaced by y and w replaced by x. The output projection P_R is understood in every formula. Their exact evaluation rank is15, matching the full source multiplicity.

The ideal rank is13. The two kernel products

    P_R(y sym P),   P_R(x sym D P)

each increase the rank by one and together give rank 15. Their coordinate formulas use

    D P = -4y Bxz-33y Byy-64x Byz+60x Bxw-24z Bxy.

Thus the two surviving3875 copies both lie in the ideal generated by the already established P. Their VOA images are zero, and no new3875 primitive occurs.

## 5. The singlet calculation

The five invariant basis polynomials are

    A=Bxx Bxw, B=Bxx Byz, C=Bxy Bxz,
    E=B([x,y],[x,z]), F=Bxy Byy.

The invariant contraction of the I pair is

    J(x,x;y,z)=(6Bxx Byz+372Bxy Bxz+31B([x,y],[x,z]))/434.

Polarizing J and using the same six ideal sources gives rank 4 in this five-dimensional space. The functional(0,-62,31,-360,0) kills all six ideal images and takes value 2184 on

    D F_0=-8Bxx Byz+8Bxy Bxz-4B([x,y],[x,z]),

where F_0=2Bxy²-B([x,y],[x,y])-2Bxx Byy is the established weight-six quartic. Therefore D F_0 is nonzero and spans the unique arc singlet.

The fresh product replay gives F_0=(91/155) sum_a x_(t^a) P^(t_a) modulo the arc ideal. The weight-five P lift is null, so F_0 belongs to K, and D F_0 does too. This settles the singlet kernel and its primitive quotient.

## 6. Full null identities and independent verification

The source-null replays use the original unprojected lattice evaluator. They reconstruct the weight-four lift R_Q=Sym(F_Q)-8Q31+24Q22, whose lattice image is zero while Sym(F_Q) alone has 44 image terms. They also reconstruct the full stored weight-five adjoint lift, including its lower-length correction, and verify zero lattice image, highest-weight equations and nonmembership in the arc ideal. The quartic F_0 product decision and the weight-six quartic theorem are freshly replayed.

Multiplication, translation and the finite E8 action preserve the full affine null ideal and the Li kernel. Thus the products used above have full affine null lifts, even though this checkpoint does not expand every product lift into a large PBW coefficient list. Their leading symbols are nonzero because the independent quotient ranks prove it. These facts supply the matching null upper bounds; a projected evaluator rank is not substituted for them.

An independent verifier clears rational denominators and uses integer Bareiss elimination. It checks the complete source ranks, ideal ranks, every retained ideal-to-source coordinate identity, every pair-projector coordinate identity and the ranks after adjoining the product classes. Eight new focused tests additionally check the character dimensions, actual coordinate-free generator formulas, product formulas, source-null replay gates and rejection of a changed coefficient.

## 7. Exact boundary and replay

This proves only the three named weight-seven quartic isotypic components. It does not determine the 30380 component, the other quartic types, longer current lengths, the complete weight-seven kernel, or finite generation in all weights. No remembered later-session classification is imported without its certificate.

Run:

```sh
python replay.py --quartic --tests
```

All source points, coefficient matrices, output probes, rank checks and product coordinates are retained in the small-sector receipts. The 28 focused tests combine the previous 20 with eight new tests. This is not a full PerfectJet regression run or a proof-assistant formalization.
