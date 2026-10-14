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

## Smith form and integer certificates

Row and column operations by integer elementary matrices keep U and V unimodular. Each pass either strictly lowers the absolute value of the pivot or clears its row and column. Positive integers cannot decrease forever, so the pass terminates. If the pivot fails to divide some later entry, adding that row to the pivot row and reducing again gives a smaller pivot. Thus the final diagonal satisfies $d_1|d_2|\cdots$. Unimodular transforms preserve the gcd $\Delta_k$ of all k-by-k minors, by Cauchy-Binet in both directions. For a divisibility-ordered diagonal, $\Delta_k=d_1\cdots d_k$. The tests compare these two routes.

Put y=V^{-1}x, so Bx=b becomes Dy=Ub. Because V is unimodular, x is integral exactly when y is integral. Coordinatewise, $d_iy_i=(Ub)_i$; rows past the rank require $(Ub)_i=0$. If coordinate i fails, the row $U_i/d_i$ times B equals row i of $V^{-1}$, which is integral, while its product with b is not an integer. Any integer solution x would make the same product an integer, a contradiction. The integer kernel is $\{Vy:Dy=0\}$, so it is spanned by the last n-r columns of V. Those columns extend to the unimodular basis V, so the kernel lattice is saturated.

For a generator matrix G, $UG=DV^{-1}$, and the rows of UG generate the same lattice as the rows of G. Hence the lattice is $\bigoplus_i d_i\mathbb Z w_i$, where $w_i$ are the rows of $V^{-1}$. Its rational span meets $\mathbb Z^n$ in $\bigoplus_{i\le r}\mathbb Z w_i$, because the $w_i$ form a basis of $\mathbb Z^n$. The quotient is $\bigoplus\mathbb Z/d_i$, with order $d_1\cdots d_r$. When $d_i>1$, $w_i$ is in the saturation and not in the lattice.

## Hankel realization from a finite block

Let M be the invertible Hankel block on prefixes $P_0$ and suffixes $S_0$, with r equal to the rank of the full finite block H on prefixes and suffixes of length at most k. Then every row $H[p,\cdot]$ is a combination $c_pH[P_0,\cdot]$, and restriction to $S_0$ gives $c_p=x_pM^{-1}$. Applied to the columns $as$ and to the empty suffix, $f(pas)=c_pH[P_0,as]$ and $f(p)=c_pH[P_0,\varepsilon]$. For prefixes p in the block, this gives $x_{pa}=x_pM^{-1}H_a[P_0,S_0]$ and $f(p)=x_pM^{-1}f(P_0)$. Induction on word length from $x_\varepsilon=f(S_0)$ shows the model agrees with f on the block. When f has a finite representation of dimension $n\le$ the block rank, the block rank equals the global Hankel rank, which is the minimal dimension. Without such a hypothesis the block cannot certify agreement on longer words. A held-out disagreement is then a witness that the block is too small.

## Coarsest exact lumping

Call a partition valid when every action matrix has constant block-column sums within each source block and the output is constant on blocks. The refinement step splits blocks by the vector of block-totals computed under the current partition. Suppose a valid partition $\pi$ refines the current partition. Two states in one $\pi$-block have equal totals into each $\pi$-block, so they also have equal totals into the unions that form current blocks. They are therefore never separated. The initial output partition is refined by every valid partition. By induction, every valid partition refines every iterate. The iteration stops only when the partition is valid, so its fixed point is the unique coarsest valid partition. With R the block indicator, the constant sums give $RA_c=\bar A_cR$ and $H=\bar HR$, which preserves the weighted cost series.

## Hermite form and lattice equality

Integer row operations keep U unimodular. In each column, Euclidean reduction among the remaining rows terminates with one nonzero entry, because the minimum absolute value strictly decreases. Rows above that pivot are then reduced modulo it. Uniqueness: let H and H' be Hermite forms of the same row lattice. Their pivot columns agree, because the pivot columns record the first nonzero coordinate across the lattice's echelon filtration. The first pivots are equal and positive, since each generates the projection of the lattice onto that coordinate. Inductively, row i of H minus row i of H' is a lattice vector whose first possible nonzero coordinate is pivot i, and that entry lies strictly between minus the pivot and the pivot. It must therefore vanish. The difference then has no nonzero pivot coordinate and is zero. Hence two row lattices are equal exactly when their nonzero Hermite rows agree.

## Multi-output realization

Replace columns indexed by suffixes with columns indexed by suffix-output pairs. The argument for single-output realization applies unchanged: each row $H[p,\cdot]$ is $x_pM^{-1}H[P_0,\cdot]$, so one state vector serves all outputs. A stacked rank can exceed every single-output rank, because the outputs may read independent parts of the state.

## One-parameter rank loci

Let r be the rank of A(t) over Q(t). Some r-minor is a nonzero polynomial of degree at most rd, where d bounds the entry degrees. It cannot vanish at all rd+1 evaluation nodes, so the maximum sampled rank is r. At any t, rank A(t)<r exactly when every r-minor vanishes there. Every drop point is therefore a root of the chosen nonzero minor $M_0$, and multiplicities do not matter, so the squarefree part s suffices. Over $R=Q[t]/(s)$, an element that is zero vanishes at every root of s. An element coprime to s vanishes at none of them, and an element sharing a factor g with s splits $R\cong Q[t]/(g)\times Q[t]/(s/g)$ by the Chinese remainder theorem. Elimination whose pivots are units of R is valid simultaneously at every root of the current modulus, so the rank is constant across those roots. Splitting at zero divisors terminates because degrees decrease. The drop locus is the product of the factors whose rank is less than r. Rational drop points come from the rational root theorem, and their ranks are replayed by direct evaluation.

## Local power exclusions

If $F(n)=m^d$, then $F(n)\equiv m^d \pmod q$ for every q. A residue that is not a d-th power modulo q therefore excludes n. Survivors for a set of moduli are residues modulo their least common multiple whose reductions survive each modulus. By the Chinese remainder theorem this set depends only on the set of moduli, not on their order. The greedy choice changes cost, never correctness. The sieved count equals the brute-force count, because integer roots are checked on every survivor.
