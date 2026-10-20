# The rank-eight Jacobi and density bridge

This component supplies an exact common object between the finite E8 basis,
the level-one affine character, and elliptic geometry. It is a classical
construction implemented with complete lattice enumeration and exact moment
certificates. It does not identify the programme's five-dimensional KZ local
system with a KZB local system, and does not claim a new elliptic quantum group.

## A precise extended carrier

Let L be the even unimodular E8 lattice, normalized so roots have squared
length2. With q=exp(2πiτ), define

\[
\Theta_L(\tau,z)=\sum_{\alpha\in L}q^{(\alpha,\alpha)/2}
 e^{2\pi i(\alpha,z)},\qquad
H(\tau,z)=\Theta_L(\tau,z)\prod_{n\ge1}(1-q^n)^{-8}.
\]

Here z has eight complex Cartan coordinates. This is richer than the scalar
specialization H(τ,0)=E4(τ)/φ(q)^8: it retains every charge. The lattice-VOA
Fock decomposition is

\[
L_1(E_8)\cong V_L=\bigoplus_{\alpha\in L}
 S\!\left(\bigoplus_{n>0}\mathbb C^8t^{-n}\right)e^\alpha,
\qquad
\dim V_L[N,\alpha]=p_8\left(N-\frac{|\alpha|^2}{2}\right).
\]

At weight1, eight neutral oscillators and240 root charges recover the248
dimensional finite Lie algebra. Higher weights contain additional charges
and oscillator products. Thus the finite Lie basis is literally the first
positive weight of a larger exact graded carrier. No arbitrary redefinition
of the Lie bracket is needed to make this inclusion meaningful.

The code represents α by v=2α, with either every coordinate even or every
coordinate odd, and sum(v)=0 modulo4. Norm degree is sum(v_i²)/8. The finite
ball recursion has coordinate bound |v_i|≤floor(sqrt(8N)); it is exhaustive.
The first shell populations are1,240,2160,6720,17520,30240,60480.

## Elliptic compatibility, including the derivative normalization

For λ,μ∈L, reindexing α→α+λ proves

\[
\Theta_L(\tau,z+\lambda\tau+\mu)
=q^{-|\lambda|^2/2}e^{-2\pi i(\lambda,z)}\Theta_L(\tau,z).
\]

Evenness gives Θ(τ+1,z)=Θ(τ,z). Unimodularity and Poisson summation give

\[
\Theta_L(-1/\tau,z/\tau)
=\tau^4e^{\pi i(z,z)/\tau}\Theta_L(\tau,z).
\]

These are the lattice Jacobi transformation laws of weight4 and index1.
Dividing by η^8 gives physical character χ=q^(-1/3)H with modular weight0
and the same elliptic index. The T multiplier of χ is exp(-2πi/3).

Write Dτ=(2πi)^(-1)∂τ and Di=(2πi)^(-1)∂zi. Coefficientwise differentiation
proves the exact heat equations

\[
(2D_\tau-\textstyle\sum_iD_i^2)\Theta_L=0,
\quad
(2D_\tau-\textstyle\sum_iD_i^2)H=\tfrac23(1-E_2)H,
\quad
(2D_\tau-\textstyle\sum_iD_i^2)\chi=-\tfrac23E_2\chi.
\]

The oscillator correction matters: omitting it already gives residual16 at
weight1. The receipt reconstructs every total population from charge shells
and p8, then checks the corrected equation independently in exact integers.

## The first angular density boundary is arithmetic

Let S_n={α∈L:|α|²=2n}, N_n=|S_n|=240σ3(n), and
M8_n(u)=Σ_(α∈S_n)(α,u)^8. Every shell is a spherical7-design. Its second,
fourth and sixth moments are the corresponding spherical moments in every
direction. The first possible angular defect occurs in degree8. Define

\[
H_{8,\mathrm{root}}(u)=\sum_{\alpha\in S_1}(\alpha,u)^8-30|u|^8.
\]

This polynomial is harmonic: applying the Laplacian gives
112·Σ_(α∈S1)(α,u)^6−3360|u|^6=0 by the sixth-moment identity. It is nonzero,
with value−3/2 at the first Euclidean coordinate vector. Weighted-theta
modularity, and dim S12(SL2Z)=1, imply the all-order identity

\[
\boxed{M8_n(u)-\frac{N_n n^4}{8}|u|^8
=\tau(n)H_{8,\mathrm{root}}(u).}
\]

Here τ(n) is the Ramanujan coefficient of Δ=q∏(1−q^n)^24, not the elliptic
modulus. A direct proof uses the degree8 zonal harmonic

\[
P_8(x,u)=(x,u)^8-\frac75|x|^2|u|^2(x,u)^6
+\frac7{12}|x|^4|u|^4(x,u)^4
-\frac7{96}|x|^6|u|^6(x,u)^2
+\frac1{768}|x|^8|u|^8.
\]

Its weighted theta is a weight12 cusp form. Summing the lower terms on each
shell using the7-design identities reduces it exactly to the boxed defect.
The q coefficient fixes the cusp form to H8_root(u)Δ. The program verifies
the harmonic recurrence and all degree≤8 moment tensors: D8 permutations and
even sign changes reduce them to partitions of1..4 and the all-odd pattern
(1,1,1,1,1,1,1,1). This covers coefficients that axis-only probes miss.

After oscillator convolution, the angular defect series becomes
H8_root(u)Δ/φ^8=H8_root(u)qφ^16. This gives a precise density observable
inside the full affine carrier and its elliptic chemical-potential character.
It is an angular charge moment, not a spatial packing-density improvement.

The boundary is exact: S_n is an8-design if and only if τ(n)=0. Asserting
that no shell is an8-design would require Lehmer's nonvanishing conjecture.
The programme retains that arithmetic question as open. A finite successful
enumeration cannot close it.

## A finite relation generator for higher angular sectors

For every even d between2 and30 the module also constructs the zonal harmonic
projection P_d(x,u) by the exact Laplacian recurrence

\[
a_{j+1}=-a_j\frac{(d-2j)(d-2j-1)}
 {2(j+1)(8+2d-2(j+1)-2)},\qquad a_0=1.
\]

Harmonic theta modularity and the modular-form polynomial ring give

\[
\Theta_{L,P_d}\in S_{4+d}(SL_2\mathbb Z)
=\Delta\,\mathbb Q[E_4,E_6]_{d-8}.
\]

Consequently the coefficients of the finite basis
ΔE4^aE6^b, 4a+6b=d−8, are determined by a Sturm panel of at most the first
two q coefficients for d≤30. This is an all-order relation compiler in each
declared angular degree. Degrees2,4,6,10 vanish because their cusp spaces
vanish. Degree8 is the Δ sector above; degrees12,14,16,18 have respectively
ΔE4,ΔE6,ΔE4²,ΔE4E6 as bases. Degree20 is the first two-dimensional cusp
sector, with basis ΔE4³ and ΔE6². Thus a single scalar angular correction
ceases to suffice there.

The program computes and verifies the directional specialization u=e1
through degree30, including exact full-rank Sturm panels and independent
later coefficients. The underlying modular theorem is polynomial-valued in
u, but the full multivariate coefficient arrays above degree8 are **not**
computed here. Whole-tensor finite replay is retained through degree8.

## Sources and executable scope

Sakai, *E_n Jacobi forms and Seiberg–Witten curves*, arXiv:1706.04619,
gives the E8 Weyl invariant Jacobi-form setting. De la Harpe, Pache and Venkov,
*Construction of spherical cubature formulas using lattices* (2006), supplies
the harmonic theta and shell-design framework. Elkies, *Math272y*, October23
2019 notes, gives explicit E8 shell moment formulas. The identities here are
classical; the new contribution to this programme is their exact integration
with the retained finite-basis, current, period and elliptic certificates.

`jacobi_receipt(N, exhaustive=True)` enumerates every charge through N≤8,
checks all moment coefficient patterns, and checks eight generating root
reflections and elliptic reindexings on every enumerated vector. The analytic
all-order statements use the stated theorems, not finite extrapolation.
