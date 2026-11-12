# Exact polynomial kernel towers

PerfectJet now exposes a small generic engine for repeated exact constraints.
It is intentionally independent of Asterion and of any one Hamiltonian family.

For a finite rational state space with evolution matrix \(A\) and constraint
matrix \(C\), the depth-\(r\) observation matrix is

\[
\mathcal O_r=
\begin{bmatrix}
C\\
CA\\
\vdots\\
CA^r
\end{bmatrix}.
\]

The surviving space is \(\ker \mathcal O_r\). If the cumulative row rank does
not increase at the next depth, its row space is closed under right
multiplication by \(A\), so the kernel has stabilized for every later depth.

`perfectjet.kernel_tower.matrix_kernel_tower` computes this tower using
exact rational arithmetic, records the rank and kernel at every depth, and
returns a witness whenever a newly added block detects a direction that
survived all earlier blocks.

## Polynomial operators

`polynomial_kernel_tower` removes the requirement that evolution preserve a
finite polynomial degree. The input observable is restricted to a supplied
finite basis, but the evolved basis elements may move to arbitrary degrees.
At every depth the supplied polynomial constraints are evaluated in the
ambient sparse polynomial ring; every nonzero output coefficient becomes an
exact matrix row.

For a binary sextic Hamiltonian (H), take

[
D_HG=T_1(H,G),qquad
C_HG=(T_3(H,G),T_5(H,G)).
]

Then the engine builds

[
mathcal O_{H,N}^{(r)}
=
egin{bmatrix}
C_H\
C_HD_H\
dots\
C_HD_H^r
end{bmatrix}_{V_N}
]

without assuming that (D_H(V_N)subseteq V_N).

The regression suite includes the exceptional homogeneous sextic

[
H=q^4p^2+q^6.
]

On the quadratic domain ((q^2,qp,p^2)), the exact kernel dimensions are

[
3longrightarrow1longrightarrow0.
]

Thus all quadratics pass the static gates, only (qp) survives the first
Poisson iterate, and the second iterate kills that final direction. The same
engine checks (H=q^6), where the three-dimensional homogeneous degree-four
kernel stabilizes immediately.

## Why this belongs in PerfectJet

The API captures a common layer behind several existing workstreams:

- transvectant partner kernels and persistent Hamiltonian cores;
- Asterion relation spaces acted on by differentiation or raising operators;
- observability/reconstruction problems such as the height-series readers;
- any exact rational constraint system where repeated evolution exposes hidden
  directions.

The module does not claim that an arbitrary nonlinear callable is linear.
Linearity and applicability of the supplied evolution/constraint operators are
the caller's mathematical obligations. The certificate concerns the exact
matrix induced by those operators on the supplied finite input span.
