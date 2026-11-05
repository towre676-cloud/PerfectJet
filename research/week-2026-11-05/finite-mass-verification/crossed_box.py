"""Exact equal-mass nonplanar crossed-box dictionary and scalar integrand.

Conventions: D_j=q_j^2-m^2+i0, s=(p1+p2)^2, t=(p1+p3)^2,
u=-s-t, all external p_i^2=0, D=4-2*eps, loop measure
exp(2*EulerGamma*eps)*prod[d^D l/(i*pi^(D/2))].

The functions below do not choose a maximal-cut contour or its phase.
"""
from __future__ import annotations


def symanzik(alpha, s, t, m2=1):
    """Return (U,F), accepting scalars, SymPy expressions, or NumPy arrays.

    alpha is a sequence of seven entries.  For vectorized use pass
    samples.T rather than an array with its sample index first.
    No delta-function/projective Jacobian or overall Gamma factor is
    included.  F carries mass dimension two.
    """
    a1,a2,a3,a4,a5,a6,a7 = alpha
    left = a1+a2+a3+a6+a7
    right = a4+a5+a6+a7
    shared = a6+a7
    U = left*right-shared*shared
    Ps = a1*a3*(a4+a5+a6+a7)+a1*a5*a7+a3*a4*a6
    Pt = a2*a5*a6
    Pu = a2*a4*a7
    F = m2*sum(alpha)*U-s*Ps-t*Pt+(s+t)*Pu
    return U,F


def scalar_parameter_density(alpha, s, t, eps=0, m2=1, delta=0):
    """Projective scalar density, excluding prefactor and projective measure.

    The exact Feynman prescription is F-i*delta*U*sum(alpha).
    For NumPy data callers should pass samples.T and use complex dtype
    when a physical region requires contour continuation.
    """
    U,F = symanzik(alpha,s,t,m2)
    if delta:
        F = F-1j*delta*U*sum(alpha)
    return U**(1+3*eps)/F**(3+2*eps)


def scalar_prefactor(eps=0, mu2=1):
    """Overall factor for the original seven denominators (mpmath)."""
    import mpmath as mp
    return -mp.exp(2*mp.euler*eps)*mp.gamma(3+2*eps)*mu2**(2*eps)


def cut_polynomials(x, s, t, m2=1):
    """Return DPS quadratics (A,B,C) in x=l1.p4 on the maximal cut.

    y^2=A*B*C/(64*s) is monic.  With raw z=l1.p3, x=-s/2-z.
    The physical regulator is (B*C)^(-eps), up to the explicitly
    calculated kinematic factor and its continued logarithm.
    """
    A = 4*x*x+2*s*x+m2*s
    B = 4*x*x+2*s*x-3*m2*s
    C = s*(2*x+s+t)**2-4*m2*t*(s+t)
    return A,B,C


def cut_discriminant_factors(s,t):
    """Dimensionless m^2=1 finite-chart factors; s=0 is a chart boundary."""
    fAC = (s-4)*t*(s+t)-s*s
    fBC1 = s*s*t-9*s*s+s*t*t-12*s*t-4*t*t
    fBC2 = s*s*t-s*s+s*t*t+4*s*t-4*t*t
    return {'s':s,'t':t,'s_plus_t':s+t,'s_minus_4':s-4,
            's_plus_12':s+12,'AC':fAC,'BC1':fBC1,'BC2':fBC2}


def correlated_i0(s_physical,t_physical,m2=1,delta=0):
    """Dimensionless invariants induced by the common mass prescription."""
    continued_mass = m2-1j*delta
    return s_physical/continued_mass,t_physical/continued_mass


def threshold_box_density(beta,eps=0,m2=1):
    """Four-parameter one-loop box density at s=4m^2, l1=P/2.

    beta=(beta4,beta5,beta6,beta7); sum beta=1 in simplex coordinates.
    The one-loop prefactor is exp(EulerGamma*eps)*Gamma(2+eps).
    """
    b4,b5,b6,b7=beta
    Fb=m2*(sum(beta)**2-(b4-b5)*(b6-b7))
    return Fb**(-2-eps)


def cut13_box_polynomial(beta,s,x,m2=1):
    """Box polynomial on the physical cut D1=D3=0, with x=l1.p4.

    This is homogeneous in the four box Feynman parameters.  It is not
    the seven-line maximal-cut polynomial C.
    """
    b4,b5,b6,b7=beta
    return (m2*sum(beta)**2-m2*(b4*b6+b5*b7)
            -(m2+2*x)*b4*b7-(m2-s-2*x)*b5*b6)


def threshold_box_constant(eps=0):
    """Dimensionless threshold box B(eps), evaluated with mpmath.

    At eps=0 the result is elementary; for general eps the displayed
    hypergeometric function is the convergent exact power series at 1/16.
    """
    import mpmath as mp
    if eps == 0:
        return mp.sqrt(5)*mp.log((1+mp.sqrt(5))/2)-mp.pi/(2*mp.sqrt(3))
    return mp.hyper([1,mp.mpf('0.5'),1+eps/2,mp.mpf('1.5')+eps/2],
                    [mp.mpf('1.25'),mp.mpf('1.5'),mp.mpf('1.75')],
                    mp.mpf(1)/16)/6


def threshold_discontinuity_leading(beta,eps=0,m2=1,mu2=1):
    """Leading physical Disc_s I for positive real beta -> 0.

    Disc=I(s+i0)-I(s-i0), s=4*m2/(1-beta**2), -4*m2<t<0.
    The omitted term is O(beta**2) relative, locally uniformly for eps
    near zero and t away from the forward/backward endpoints.
    """
    import mpmath as mp
    coefficient=(-mp.pi*1j*m2**(-3)*mp.exp(2*mp.euler*eps)
                 *(mu2/m2)**(2*eps)*4**(-eps)
                 *mp.gamma(1-eps)*mp.gamma(2+eps)/mp.gamma(2-2*eps)
                 *threshold_box_constant(eps))
    return coefficient*beta**(1-2*eps)


def maximal_cut_gram_data(x,s,t,m2=1):
    """Return exact on-cut Gram factors in the fixed propagator dictionary."""
    A,B,C=cut_polynomials(x,s,t,m2)
    return {'external':-s*t*(s+t)/4, 'box_external':-s*A/4,
            'box':A*B/16, 'remaining':s*C/16}


def maximal_cut_density_from_logs(gram_logs,eps=0,mu2=1):
    """Coefficient of dx after seven normalized Baikov residues.

    gram_logs must contain the transported logarithms of, in order,
    (-E0,-E1,B_box,B_remaining).  No principal-branch defaults are used.
    The convention is the Wick-continued Euclidean angular contour with
    residues divided by (2*pi*i)**7 and the ordered residual coordinate
    x=l1.p4.  The one-dimensional contour and its sheet remain caller data.
    This function does not identify an arbitrary period with a physical
    Feynman discontinuity.
    """
    import mpmath as mp
    le0,le1,lb0,lb1=gram_logs
    return (mp.exp(2*mp.euler*eps)*mu2**(2*eps)
            /(32*mp.pi**3*mp.gamma(mp.mpf('0.5')-eps)**2)
            *mp.exp(eps*(le0+le1)-(mp.mpf('0.5')+eps)*(lb0+lb1)))
