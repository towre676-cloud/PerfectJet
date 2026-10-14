# Mathematical proofs for the shared exact core

These arguments state the mathematical reasons behind the executable identities. They are conventional written proofs, not Lean kernel proofs. The independent finite checks attack implementation errors; they do not replace the arguments' hypotheses.

## Cyclotomic closure and affine-periodic coefficients

Let L be a positive integer and zeta a primitive Lth root of unity. Work in formal power series over Q(zeta). Every pair a,b>=0 has unique decompositions a=r+Li,b=s+Lj with0<=r,s<L. Since zeta^(ab)=zeta^(rs), summing i,j gives the denominator(1-x^L)^2 and numerator sum_{r,s<L}zeta^(rs)x^(r+s). Uniqueness of decomposition prevents any missing or duplicated summand.

The coefficient of x^n in the original series is a_n=sum_{j=0}^n zeta^(j(n-j)). Write n=dL+r. The summand is periodic in j modulo L because replacing j by j+L changes j(n-j) by a multiple of L. The n+1 indices comprise d complete blocks and the partial block0..r. Thus a_n=dG_r+B_r. Replacing n by n+L increases d by1 and leaves r fixed, proving a_{n+2L}-2a_{n+L}+a_n=0. The numerator at1 is sum_r sum_s zeta^(rs)=L: r0 contributes L, every other inner geometric sum is0. For L>=2 its highest coefficient is zeta^((L-1)^2)=zeta.

## Active partner dimension

Let L:V->W and P:V->Y be linear maps over a field. Put K=ker L and J=K intersect ker P. The active quotient is K/J. Rank-nullity gives dim K=dim V-rank L and dim J=dim V-rank([L;P]). Subtraction yields dim(K/J)=rank([L;P])-rank L. This counts independent nonzero P outputs available inside the correction-free kernel. It does not count every individual nonzero partner, which is an infinite set over an infinite field.

For a fixed sextic, the third/fifth transvectants are linear in the partner g, so this theorem applies to the supplied gate matrices. Odd self-transvectants vanish by antisymmetry, but their first transvectant also vanishes; self-pairs therefore contribute to K without contributing to the active quotient.

## Parametric molecular identity

The sextic f_lambda and eighth-degree g_lambda are affine in lambda. Every fixed-order transvectant is bilinear in its two inputs, so each resulting monomial coefficient has degree at most2 in lambda. Exact vanishing at three distinct rational parameters implies every coefficient polynomial is identically zero. The implementation retains four parameters and independently computes all polynomial coefficients. The first transvectant has x12 coefficient6, independent of lambda, so its nonvanishing is not merely a sampled observation.

The quintic h is independent of lambda. Its third transvectant is affine in lambda; exact coefficient calculation yields72(7lambda-40)(x4y+xy4). Fifth transvectant vanishes. This proves exactness of this partner at40/7 and failure for other lambda. It does not prove absence of other quintic partners elsewhere.

## Target recovery

For finite-dimensional vector spaces, ker O subset ker G iff every row functional of G vanishes on ker O. The annihilator of ker O is the row space of O, so this is equivalent to G=LO for a linear map L. Equivalently, choose a basis N for ker O: recovery holds iff GN=0. A nonzero column response supplies a witness with unchanged observations and changed target. Rational row reduction computes this exactly for rational input matrices.

For T(x)=g^Tx+1/2 x^TQx with symmetric Q, substitute x=x0+Nz. The difference T(x0+Nz)-T(x0) equals z^T N^T(g+Qx0)+1/2 z^T N^TQN z. A polynomial of degree at most2 vanishes for every z over Q or R iff its linear and symmetric quadratic coefficients vanish. Hence the two fibre-constancy conditions. On a restricted/nonlinear feasible fibre they are sufficient but may not be necessary; the chapter's equivalence is for the full affine fibre.

## Weighted quotient series

Assume RA=Abar R. Induction gives RA^t=Abar^tR. If H=Hbar R, then HA^ts=Hbar Abar^t Rs. Apply the same multiplication argument coefficientwise to A(z)=sum_c z^c A_c. Positive costs imply A(0)=0 and ensure the formal inverse exists as a geometric series, yielding H(I-A(z))^-1s=Hbar(I-Abar(z))^-1Rs. Matching state labels alone is insufficient: aggregation must preserve total outgoing weights and the output must factor through R.

## Exact feature closure

Assume p(F(x))=Gp(x) as a polynomial identity. Base time0 is immediate. If p(F^t(x))=G^tp(x), substitution gives p(F^(t+1)(x))=G p(F^t(x))=G^(t+1)p(x). If O=Hp, then all outputs O(F^t(x))=HG^tp(x) follow. Exact span solving and coefficient replay establish the one-step identity; no regression residual is silently discarded. Existence of a finite closed feature span is not asserted for arbitrary polynomial F.

## Completion-count navigation

A feasible population in original binary order partitions disjointly by the next bit. Therefore C(q)=C(q0)+C(q1). In lexicographic order, every zero-branch completion precedes every one-branch completion. A word with bit1 skips exactly C(q0) predecessors at that level. Summing the skipped populations gives rank. Conversely, an address r either lies in the zero branch or in the one branch after subtracting C(q0). Induction on remaining length proves rank/unrank are inverse bijections. Drawing r uniformly thus samples original objects uniformly. Prefix count zero means no feasible completions and must not be sampled.

## Energy balance and defect propagation

For constant symmetric M, differentiating E=1/2 u^TMu gives E'=u^TM(Au+f). The scalar u^TMAu equals u^T(A^TM+MA)u/2. Divide by E to obtain the declared lambda/zeta identity and rho=1-zeta/lambda. M positive definite and u nonzero ensure E>0; lambda0 makes the ratio undefined.

Subtract V times reduced dynamics from full dynamics to get e_next=Ae+(AV-VG)z+(B-VH)u. Iterating yields the exact finite convolution. If norm(Ax)<=gamma norm(x), gamma<1, apply the triangle inequality at each step. A uniform defect bound delta yields the geometric series. This assumes the same valid norm throughout; eigenvalue bounds alone do not establish that norm contraction.

## Reflection coordinate and flip obstruction

If an injective local Psi satisfies Psi composed f=-Psi, applying it twice gives Psi composed f2=Psi and hence f2=id. Conversely, for a centered analytic involution f with f'(0)=-1, Psi=(x-f(x))/2 has derivative1 at0, so the analytic inverse function theorem makes it locally invertible. Direct substitution gives Psi composed f=-Psi. This proves the local equivalence.

For f(x)=-x+ax2+bx3+O(x4), expand -f+a f2+b f3 to cubic order. Quadratic terms cancel and the cubic coefficient is-2(b+a2). This is an obstruction to involution at that order; its vanishing does not settle higher orders. The finite-jet implementation composes the polynomial series directly rather than inferring reflection from multiplier-1.

## Quotient-ring field identity

In the monic quotient Q[u]/(u3-4u2+5u-1), reduction produces unique degree<3 coordinates. A nonzero polynomial element is invertible when its multiplication matrix is nonsingular; solving for its inverse and replaying the product checks the denominator. Substituting alpha=u-1 reduces alpha3-alpha2+1 to0. Since alpha is invertible, beta=-1/alpha satisfies beta3-beta-1=0 after multiplication by alpha3. The Hessian and vertex identities are established by the same exact quotient operations. This proves algebraic identities of the displayed field elements, not the geometric interpretation of the original state integral.

## Decision margin

If abs(J(a)-Jhat(a))<=epsilon_a, then J(a)>=Jhat(a)-epsilon_a and J(a)<=Jhat(a)+epsilon_a. A candidate whose lower bound exceeds every competitor's upper bound is strictly best. A shared epsilon therefore needs estimated margin>2epsilon. Equality only provides a non-strict comparison; the implementation returns unresolved for overlapping intervals. Empirical uncertainty needs its own justified intervals.
