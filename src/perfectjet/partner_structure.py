"""All-degree local obstructions and complete boundary strata for sextic partners.

Polynomial identities are recomputed over Q[N,s] and exact Sylvester
determinants, without an external CAS. They do not classify all squarefree
sextics in unbounded degree. See docs/PARTNER_STRUCTURE.md for proofs.
"""
from fractions import Fraction as Q
from functools import lru_cache
from math import comb

from .polynomial import Poly


def falling(value, count):
    if type(count) is not int or count < 0:
        raise ValueError('nonnegative falling-factorial order required')
    result = 1
    for j in range(count):
        result = result*(value-j)
    return result


def indicial(order, multiplicity, degree, valuation):
    """The coefficient multiplying the leading local product a*b."""
    if order not in (3, 5) or type(multiplicity) is not int or not 0 <= multiplicity <= 6:
        raise ValueError('third/fifth gate and sextic multiplicity 0..6 required')
    return sum((-1)**i*comb(order, i)*falling(6-order+i, i)
               *falling(degree-i, order-i)*falling(multiplicity, order-i)
               *falling(valuation, i) for i in range(order+1))


def reduced_factors(multiplicity):
    """Return H,J3,J5,c3,c5 with I_r=c_r*H*J_r over Q[N,s]."""
    n, s = Poly.variable(0), Poly.variable(1)
    one = Poly.constant(1)
    if multiplicity == 0:
        return s*(s-1)*(s-2), one, (s-3)*(s-4), -120, -720
    if multiplicity == 1:
        return s*(s-1), 2*s-n-2, (s-2)*(s-3)*(6*s-5*n-4), -60, -120
    if multiplicity == 2:
        return s, n*n-5*n*s+2*n+5*s*s-5*s+2, (s-n)*(s-2)*(s-1)*(3*s-2*n-1), -24, -240
    if multiplicity == 3:
        return 2*s-n, n*n-10*n*s-3*n+10*s*s+2, s*(s-n)*(s-1)*(s-n+1), -6, -360
    if multiplicity == 4:
        return s-n, n*n-5*n*s-3*n+5*s*s+5*s+2, s*(s-n+1)*(s-n+2)*(3*s-n+1), -24, -240
    if multiplicity == 5:
        return (s-n)*(s-n+1), 2*s-n+2, (s-n+2)*(s-n+3)*(6*s-n+4), -60, -120
    if multiplicity == 6:
        return (s-n)*(s-n+1)*(s-n+2), one, (s-n+3)*(s-n+4), -120, -720
    raise ValueError('multiplicity 0..6 required')


def _determinant_polynomial(matrix):
    """Division-free subset determinant over Q[N,s]; no point sampling."""
    size = len(matrix)
    if any(len(row) != size for row in matrix):
        raise ValueError('square polynomial matrix required')
    @lru_cache(None)
    def visit(mask):
        row = mask.bit_count()
        if row == size:
            return Poly.constant(1)
        result = Poly.constant(0)
        for col in range(size):
            if mask >> col & 1:
                continue
            sign = (-1)**(col-(mask & ((1 << col)-1)).bit_count())
            result += sign*matrix[row][col]*visit(mask | (1 << col))
        return result
    return visit(0)


def resultant_in_valuation(left, right):
    """Sylvester determinant, descending s coefficients, left rows first."""
    def coefficients(poly):
        degree = max((e[1] for e in poly.terms), default=0)
        return [Poly({(e[0], 0): c for e, c in poly.terms.items() if e[1] == k})
                for k in range(degree, -1, -1)]
    a, b = coefficients(left), coefficients(right)
    m, n = len(a)-1, len(b)-1
    zero = Poly.constant(0)
    rows = [[zero]*i+a+[zero]*(n-i-1) for i in range(n)]
    rows += [[zero]*i+b+[zero]*(m-i-1) for i in range(m)]
    return _determinant_polynomial(rows)


def expected_resultant(multiplicity):
    n = Poly.variable(0)
    if multiplicity in (0, 6):
        return Poly.constant(1)
    if multiplicity == 1:
        return -4*(n-4)*(n-2)*(n-1)
    if multiplicity in (2, 4):
        return -(n-6)*(n-2)**3*(n-1)**3*(n+8)
    if multiplicity == 3:
        return (n-12)**2*(n-2)**2*(n-1)**4
    if multiplicity == 5:
        return 4*(n-4)*(n-2)*(n-1)
    raise ValueError('multiplicity 0..6 required')


def polynomial_certificate():
    n, s = Poly.variable(0), Poly.variable(1)
    rows = []
    for k in range(7):
        h, j3, j5, c3, c5 = reduced_factors(k)
        checks = (indicial(3, k, n, s) == c3*h*j3,
                  indicial(5, k, n, s) == c5*h*j5)
        resultant = resultant_in_valuation(j3, j5)
        if not all(checks) or resultant != expected_resultant(k):
            raise ArithmeticError('symbolic indicial/resultant identity failed at multiplicity '+str(k))
        rows.append(dict(root_multiplicity=k, common_factor=h.record(),
                         third_factorization=checks[0], fifth_factorization=checks[1],
                         resultant=resultant.record(), resultant_identity=True))
    return rows


def _degree(degree):
    if type(degree) is not int or degree < 3:
        raise ValueError('integer partner degree at least three required')
    return degree


def possible_valuations(multiplicity, degree):
    _degree(degree)
    if type(multiplicity) is not int or not 0 <= multiplicity <= 6 or degree < 13:
        raise ValueError('multiplicity 0..6 and degree at least thirteen required')
    if multiplicity == 0:
        return (0, 1, 2)
    if multiplicity == 1:
        return (0, 1)
    if multiplicity == 2:
        return (0,)
    if multiplicity == 3:
        return (degree//2,) if degree % 2 == 0 else ()
    return tuple(range(degree-multiplicity+4, degree+1))


def monomial_partner_exponents(multiplicity, degree):
    """Complete x-exponent basis for f=x^k*y^(6-k), every degree N>=3."""
    _degree(degree)
    if type(multiplicity) is not int or not 0 <= multiplicity <= 6:
        raise ValueError('multiplicity 0..6 required')
    return tuple(s for s in range(degree+1)
                 if indicial(3, multiplicity, degree, s) == 0
                 and indicial(5, multiplicity, degree, s) == 0)


def monomial_dimension(multiplicity, degree):
    """Closed all-degree formula, independent of the indicial evaluation loop."""
    _degree(degree)
    if type(multiplicity) is not int or not 0 <= multiplicity <= 6:
        raise ValueError('multiplicity 0..6 required')
    k = min(multiplicity, 6-multiplicity)
    if k == 0:
        return 3
    if k == 1:
        return 2+int(degree == 4)
    if k == 2:
        return 1+int(degree == 6)
    if k == 3:
        return int(degree % 2 == 0)+2*int(degree == 12)
    raise ValueError('multiplicity 0..6 required')


def high_multiplicity_basis(linear, multiplicity, degree):
    """Complete basis when f has exactly the supplied root multiplicity."""
    _degree(degree)
    thresholds = {4: 7, 5: 5, 6: 3}
    if multiplicity not in thresholds or degree < thresholds[multiplicity]:
        raise ValueError('multiplicity four/five/six with degree at least seven/five/three required')
    if not isinstance(linear, Poly) or linear.variables != 2 or not linear.terms or any(sum(e) != 1 for e in linear.terms):
        raise ValueError('nonzero homogeneous binary linear form required')
    d = multiplicity-4
    return tuple(linear**(degree-d)*Poly({(j, d-j): 1}) for j in range(d+1))


def affine_gate(form, partner, degree, order):
    """Direct affine formula, separate from mixed homogeneous derivatives."""
    _degree(degree)
    if order not in (1, 3, 5) or form.variables != 2 or partner.variables != 2:
        raise ValueError('binary forms and first/third/fifth order required')
    if any(sum(e) != 6 for e in form.terms) or any(sum(e) != degree for e in partner.terms):
        raise ValueError('homogeneous sextic and declared partner degree required')
    f = Poly({(e[0],): c for e, c in form.terms.items()}, 1)
    g = Poly({(e[0],): c for e, c in partner.terms.items()}, 1)
    result = Poly.constant(0, 1)
    for i in range(order+1):
        result += ((-1)**i*comb(order, i)*falling(6-order+i, i)
                   *falling(degree-i, order-i)
                   *f.derivative((order-i,))*g.derivative((i,)))
    return result


def receipt():
    return dict(schema='perfectjet/partner-structure/1',
                arithmetic='rational polynomial identities and division-free Sylvester determinants',
                proof_scope='characteristic zero; nonzero binary sextics; uniform degree N>=13',
                rows=polynomial_certificate(),
                monomial_dimension_series={'6': '3*t^3/(1-t)',
                    '5+1': '2*t^3/(1-t)+t^4', '4+2': 't^3/(1-t)+t^6',
                    '3+3': 't^4/(1-t^2)+2*t^12'},
                high_multiplicity_thresholds={'4': 7, '5': 5, '6': 3},
                formal_status='mathematical proofs and exact replay; no new Lean theorem',
                unresolved='global squarefree and mixed low-multiplicity classification for N>=21')
