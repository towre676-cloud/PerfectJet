"""Level-four half-braids: exact KZ descent and a cyclotomic B3 model.

Analytic identities use flat, permutation-equivariant KZ descent, not a
small interval residual. Tuba--Wenzl uniqueness identifies the exact model
up to simultaneous conjugacy; no endpoint associator is computed.
"""
from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha256
import json

from .asterion_kz import (E8KZ, EIGENVALUES, identity, matrix_add,
    matrix_multiply as mm, matrix_scale as scale)
from .asterion_monodromy import (ComplexBall, MatrixBall, SPECTRUM_EXPONENTS,
    seventeenth_roots, irreducibility_receipt)
from .asterion_kz import _round_gaussian, _complex_matrix_norm
from .rings import QuotientRing, cyclotomic

PARITIES = (1, -1, 1, -1, 1)
# mu_i = sign_i*zeta**exponent_i, in the existing channel order.
HALF_PHASES = ((1, 2), (1, 1), (1, 14), (-1, 0), (-1, 9))
TW_SOURCE = 'https://msp.org/pjm/2001/197-2/pjm-v197-n2-p11-s.pdf'


def power(matrix, n):
    out = identity()
    while n:
        if n & 1:
            out = mm(out, matrix)
        matrix = mm(matrix, matrix)
        n //= 2
    return out


def encoded_matrix(matrix):
    return [[x.record() for x in row] for row in matrix]


def descent_certificate():
    """Exact finite hypotheses for flat S3-equivariant Conf_3 descent."""
    s = E8KZ()
    # These global tensor permutations follow from form symmetry and Jacobi;
    # five independent evaluations reconstruct their matrices exactly.
    evaluations = tuple(s.tensor_values(b, a, c, d) for a,b,c,d in s.samples)
    p = mm(s.evaluation_inverse, evaluations)
    x = s.crossing_tensor
    q = mm(s.evaluation_inverse,tuple(s.tensor_values(a,c,b,d) for a,b,c,d in s.samples))
    a,b,c = s.A_tensor,s.B_tensor,s.C_tensor
    checks = {
        'pair_sum_scalar': matrix_add(matrix_add(a,b),c) == scale(identity(),-60),
        'swap12_involution': mm(p,p) == identity(),
        'swap23_involution': mm(q,q) == identity(),
        'crossing_is_long_swap': mm(mm(p,q),p) == x,
        'crossing_conjugates_swaps': mm(mm(x,p),x) == q,
        'permutation_braid': mm(mm(p,q),p) == mm(mm(q,p),q),
        'swap12_fixes_A': mm(mm(p,a),p) == a,
        'swap12_transports_B_to_C': mm(mm(p,b),p) == c,
        'swap23_fixes_B': mm(mm(q,b),q) == b,
        'swap23_transports_A_to_C': mm(mm(q,a),q) == c,
        'crossing_transports_A_to_B': mm(mm(x,a),x) == b,
        'swap_channel_parities': mm(mm(s.channel_inverse,p),s.channel_transform)
            == tuple(tuple(Q(PARITIES[i] if i==j else 0) for j in range(5)) for i in range(5)),
    }
    for name,left,right in [('A_BplusC',a,matrix_add(b,c)),
                            ('B_AplusC',b,matrix_add(a,c)),
                            ('C_AplusB',c,matrix_add(a,b))]:
        checks['flatness_'+name] = mm(left,right)==mm(right,left)
    # No local exponent differences are integers at this specialization.
    checks['nonresonant_at_level4'] = all(((u-v)/34).denominator != 1
        for i,u in enumerate(EIGENVALUES) for v in EIGENVALUES[i+1:])
    return {'passed':all(checks.values()), 'checks':checks,
        'swap12':[[str(v) for v in row] for row in p],
        'swap23':[[str(v) for v in row] for row in q],
        'theorem_dependency':'flat equivariant connection descends to unordered configuration space; its holonomy is a linear representation of its fundamental group B3',
        'central_exponent_mod17':4, 'half_generator_order':34,
        'half_determinant_exponent_mod17':9,
        'orientation':'positive exchange: the colliding separation rotates counterclockwise by pi; matrices act on column vectors',
        'square_identification':'positive standard exchange squares are the positive meridians U,V based at (0,1/2,1)',
        'canonical_endpoint_associator_computed':False}


@lru_cache(maxsize=1)
def algebraic_model():
    """Prop.2.7 matrices, checked as identities in Q[t]/Phi_17(t)."""
    ring = QuotientRing(cyclotomic(17))
    z = ring.generator
    l = tuple(sign*z**e for sign,e in HALF_PHASES)
    g = z**12
    l1,l2,l3,l4,l5 = l
    # Use powers for divisions by known roots of unity only.
    inv = lambda v: v**33  # every signed phase has order dividing34
    a15 = g**3*inv(l1*l5)
    a34 = a15+l3
    a14 = (l2*l4*g**15+1)*(l3+g**3*inv(l2*l4)) # g^-2=g^15
    a24 = a15+l3+g
    a12 = l2*a14*inv(a15)
    a23 = g+l3+g**2*inv(l3)
    a13 = (g**2*inv(l3)+l3+g)*(1+l1*l5*g**15)
    a = tuple(tuple(row) for row in (
        (l1,a12,a13,a14,a15), (ring.zero,l2,a23,a24,a15),
        (ring.zero,ring.zero,l3,a34,a15),
        (ring.zero,ring.zero,ring.zero,l4,l4),
        (ring.zero,ring.zero,ring.zero,ring.zero,l5)))
    b = tuple(tuple((-1)**(i+j)*a[4-i][4-j] for j in range(5)) for i in range(5))
    checks = {
        'braid_relation_exact':mm(mm(a,b),a)==mm(mm(b,a),b),
        'central_character_exact':power(mm(a,b),3)==scale(identity(),z**4),
        'first_order_divides34':power(a,34)==identity(),
        'second_order_divides34':power(b,34)==identity(),
        'gamma_fifth_power_is_determinant':g**5==z**9,
        'gamma_sixth_power_is_central':g**6==z**4,
        'cyclotomic_integral_entries':all(c.denominator==1 for m in (a,b) for row in m for x in row for c in x.coefficients),
        'phase_squares_match_pure_spectrum':all(v*v==z**e for v,e in zip(l,SPECTRUM_EXPONENTS)),
    }
    # Tuba--Wenzl Prop.2.8: all20 simplicity polynomials, exactly.
    nonzero = []
    for r in range(5):
        for t in range(5):
            if r==t:
                continue
            value = g**9*(g**2+l[r]*g+l[r]**2)*(g**2+l[t]*g+l[t]**2)
            for k in range(5):
                if k not in (r,t):
                    value *= (g**2+l[r]*l[k])*(g**2+l[t]*l[k])
            nonzero.append({'r':r,'s':t,'nonzero':value!=0,'coefficients':value.record()})
    checks['all20_simplicity_polynomials_nonzero'] = all(v['nonzero'] for v in nonzero)
    # Common character twist kills the center and determinant simultaneously.
    ta,tb=scale(a,z**5),scale(b,z**5)
    checks['normalized_center_is_identity'] = power(mm(ta,tb),3)==identity()
    checks['normalized_Delta_square_identity'] = power(mm(mm(ta,tb),ta),2)==identity()
    checks['normalized_determinant_is_one'] = z**(5*5+9)==1
    matrices={'sigma1':encoded_matrix(a),'sigma2':encoded_matrix(b)}
    return {'passed':all(checks.values()),'checks':checks,
        'field':'Q[t]/(1+t+...+t^16), t=exp(2*pi*i/17)',
        'gamma_exponent':12,'central_exponent':4,'determinant_exponent':9,
        'half_phases':[list(v) for v in HALF_PHASES],
        'matrices':matrices,'matrix_sha256':sha256(json.dumps(matrices,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
        'simplicity_polynomials':nonzero,'source':TW_SOURCE,
        'identification':'Tuba--Wenzl Theorem2.9, eigenvalues and central character; simultaneous conjugacy to the analytic KZ extension',
        'same_chart_conjugating_matrix_computed':False,
        'discrete_image_presentation_claim':False,
        'normalized_triangle_quotient':'Delta(2,3,34); injectivity not established'}


def rounded_ball(ball):
    center=tuple(tuple(_round_gaussian(x,2**128) for x in row) for row in ball.center)
    delta=matrix_add(ball.center,center,-1)
    return MatrixBall(center,ball.radius+_complex_matrix_norm(delta))


def product_balls(*balls):
    out=balls[0]
    for ball in balls[1:]:
        out=rounded_ball(out*ball)
    return out


def add_balls(left,right):
    return rounded_ball(MatrixBall(matrix_add(left.center,right.center),left.radius+right.radius))


def residual(left,right):
    diff=MatrixBall(matrix_add(left.center,right.center,-1),left.radius+right.radius)
    return {'center_norm_lower_bound':str(diff.norm_lower()),
        'error_bound':str(diff.radius),'norm_upper_bound':str(diff.norm_upper()),
        'nonzero_certified':diff.norm_lower()>diff.radius,
        'scope':'consistency enclosure; containing zero is not a proof of exact equality'}


def analytic_replay(pair=None):
    """Fresh bounded loops plus polynomial reconstruction in the original chart."""
    if pair is None:
        pair=E8KZ().monodromy_pair_receipt(order=48, tolerance=Q(1,10**12))
    first=pair['first_loop']
    u=MatrixBall(tuple(tuple(v for v in row) for row in first['approximation_exact']),Q(first['infinity_norm_error_bound']))
    v=MatrixBall(tuple(tuple(w for w in row) for row in pair['second_loop_approximation_exact']),Q(pair['second_loop_error_bound']))
    roots=seventeenth_roots()
    eig=[roots[e] for e in SPECTRUM_EXPONENTS]
    projectors=[]
    for i,value in enumerate(eig):
        p=MatrixBall(identity())
        for j,other in enumerate(eig):
            if i!=j:
                p=product_balls(p,product_balls(u.subtract_scalar(other),(value-other).inverse().rounded()))
        projectors.append(p)
    half=MatrixBall(scale(identity(),0))
    wrong=MatrixBall(scale(identity(),0))
    for p,(sign,e),parity in zip(projectors,HALF_PHASES,PARITIES):
        term=product_balls(p,roots[e]*sign)
        half=add_balls(half,term)
        wrong=add_balls(wrong,product_balls(term,parity))
    x=MatrixBall(E8KZ().crossing_tensor)
    second=product_balls(x,half,x)
    wrong_second=product_balls(x,wrong,x)
    checks={'square1':residual(product_balls(half,half),u),
        'square2':residual(product_balls(second,second),v),
        'braid':residual(product_balls(half,second,half),product_balls(second,half,second)),
        'center':residual(product_balls(half,second,half,second,half,second),MatrixBall(identity())*roots[4])}
    negative=residual(product_balls(wrong,wrong_second,wrong),product_balls(wrong_second,wrong,wrong_second))
    irred=irreducibility_receipt(u,v)
    # Gate: rigorous upper bound below1/1000, plus a rigorous rejection of
    # the omitted-parity construction. Equality itself has an analytic proof.
    passed=pair['passed'] and irred['passed'] and negative['nonzero_certified'] and all(Q(r['norm_upper_bound'])<Q(1,1000) for r in checks.values())
    def record(ball):
        return {'center':[[w.to_json() for w in row] for row in ball.center],
                'infinity_norm_error_bound':str(ball.radius)}
    return {'passed':passed,'same_chart_half_braids':{'sigma1':record(half),'sigma2':record(second)},
        'consistency_enclosures':checks,'omitted_parity_negative_control':negative,
        'specialized_irreducibility':irred,'loop_enclosures':pair,
        'exact_equality_basis':'flat equivariant KZ descent and local nonresonant spectrum, separately from residuals'}


def braid_receipt(*, exhaustive=False):
    if type(exhaustive) is not bool:
        raise TypeError('exhaustive must be boolean')
    descent=descent_certificate()
    model=algebraic_model()
    replay=analytic_replay() if exhaustive else None
    return {'schema':'perfectjet/asterion-half-braid/1',
        'passed':descent['passed'] and model['passed'] and (replay is None or replay['passed']),
        'exact_descent':descent,'algebraic_model':model,'analytic_replay':replay,
        'analytic_loop_replayed_in_this_run':exhaustive,
        'linear_B3_representation':descent['passed'] and model['passed'],
        'scalar_correction_required_for_B3':False,
        'PSL2Z_linear_descent_after_common_twist':'sigma_i -> zeta17^5 sigma_i',
        'full_discrete_image_presentation':False,'canonical_endpoint_associator_computed':False,
        'proof_boundary':'the analytic identification uses KZ descent and Tuba--Wenzl classification; interval residuals alone do not prove equality'}
