MIXED-MASS FLAVOR BENCHMARK
Exact GIM quotient and physically weighted approximation error

CONTENTS
psg_flavor_benchmark.py -- complete fixed-input computation
benchmark-80dps.json   -- its recorded 80-digit result

RUN
    python -m pip install mpmath==1.3.0
    python psg_flavor_benchmark.py --dps 80

The script also accepts --dps 100. It uses Python 3 and mpmath only.

PHYSICAL AND NUMERICAL SCOPE
The target is the reduced leading electroweak Delta-S=2 box coefficient
C = lambda^T S lambda, with lambda_i = conjugate(V_is) V_id.
The common electroweak prefactor, QCD corrections, hadronic matrix elements,
and long-distance contributions are not included. This is a fixed numerical
benchmark, not an experimental fit or an interval-arithmetic certificate.

The masses are specified as x_i=m_i^2/M_W^2:
    (x_u,x_c,x_t)=(0,1/4000,4).
The standard exactly unitary CKM parameterization uses
    s12=9/40, s23=1/25, s13=7/2000, delta=pi/3.
These are deliberately specified illustrative inputs.

PUBLISHED INPUT
The kernel is the mixed-mass Inami-Lim function, using Appendix B,
equations 69-70, of Botella et al., EPJC 82 (2022) 360:
    https://doi.org/10.1140/epjc/s10052-022-10299-9
For the CKM convention see the PDG CKM review, equation 12.3:
    https://pdg.lbl.gov/2025/reviews/rpp2024-rev-ckm-matrix.pdf
The importance of manifest unitarity in kaon calculations is discussed in
Brod, Gorbahn and Stamou, Phys. Rev. Lett.125 (2020)171803:
    https://arxiv.org/abs/1911.06822

AN INDEPENDENT POSITIVE INTEGRAL
Define a(x)=(1-2x+x^2/4)/(1-x)^2. The published formula is
    S(x,y)=xy[(a(x)log(x)-a(y)log(y))/(x-y)
              -3/(4(1-x)(1-y))].
Its continuous diagonal limit is used when x=y, including S(1,1)=3/4.
The same function has the representation
    S(x,y)=integral_0^infinity w(z) phi_x(z) phi_y(z) dz,
    w(z)=(z^2+8z+4)/(4(z+1)^2), phi_x(z)=x/(z+x).
For distinct x,y unequal to 1, the residues at -x and -y are
    Rx=xy a(x)/(y-x), Ry=xy a(y)/(x-y).
The simple-pole residue at -1 is -Rx-Ry and the double-pole coefficient
there is D=-3xy/(4(x-1)(y-1)). Integration gives
    -Rx log(x)-Ry log(y)+D,
which is the closed formula. Remaining finite cases follow by continuity.
The script compares the closed formula and independent real quadrature
for cc, ct, tt and (1,1).

EXACT QUOTIENT AND ERROR
Unitarity gives sum_i lambda_i=0. For Q=I-11^T/3,
    C=lambda^T QSQ lambda.
The script uses an orthonormal two-column basis R of this zero-sum plane,
so K=R^T S R, z=R^T lambda and C=z^T K z.
It retains the larger eigenvalue and its eigenvector to form the rank-one
coefficient. Because the coefficient is complex bilinear, use transpose,
not conjugate transpose, in its definition.

For any kernel approximation Stilde, an absolute bound is
    |lambda^T(S-Stilde)lambda| <= ||lambda||_2^2 ||S-Stilde||_2.
For the present rank-one approximation, the operator-norm error is the
smaller eigenvalue of K. The script checks the computed amplitude error
against this bound.

RESULT
The rank-one kernel retains 99.9999993226% of the Frobenius-squared weight,
yet its complete complex-coefficient relative error is 95.92296721%.
The error in the imaginary part is 2.53473207%; these are different targets.
Thus small discarded spectral weight alone does not control an amplitude
whose mass channels have strongly different mixing weights.

The script also checks CKM unitarity, the GIM sum and the quotient identity.
PASS means these stated numerical comparisons meet the displayed precision
test. It does not certify the completeness of a physical kaon prediction.
