# Exact monogenic quotient algebras

`perfectjet.quotient_algebra.MonogenicQuotient` provides a small
dependency-free arithmetic layer for

[
A=mathbf Q[x]/(f(x)),
]

with monic (f). Elements use the power basis (1,x,ldots,x^{n-1}).
The engine computes exact products, powers, left-multiplication matrices,
traces, norms, the trace pairing, and the power-basis discriminant.

The first regression target is the cubic used by the 389a1 Selmer project,

[
g(x)=x^3-x^2-9x+11.
]

The engine independently recovers

[
operatorname{Tr}(1,eta,eta^2)	ext{ pairing}=
egin{pmatrix}
3&1&19\
1&19&-5\
19&-5&155
end{pmatrix},
qquad
det=1556,
]

as well as

[
N(eta-3)=-2,qquad N(eta-2)=3.
]

These are quotient-algebra statements only. Irreducibility, identification with
a number field, integrality, maximality of the power order, field discriminant,
class group arguments, and Selmer/Kummer conclusions remain obligations of the
consumer project.
