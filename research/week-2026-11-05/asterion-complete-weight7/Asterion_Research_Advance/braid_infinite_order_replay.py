"""An infinite-order pure braid witness from a Galois-conjugate trace.

The finite-order trace bound is elementary: a finite-order 5x5 complex
matrix has five root-of-unity eigenvalues, so its trace has modulus <=5.
This remains true under every embedding of its matrix coefficient field.
"""
from fractions import Fraction as Q
from pathlib import Path
import json
from perfectjet.kz_half_braid import algebraic_model, power
from perfectjet.asterion_kz import matrix_multiply as mm
from perfectjet.asterion_monodromy import seventeenth_roots, root_certificate, ComplexBall
from perfectjet.rings import QuotientRing, cyclotomic

EXPECTED_TRACE=(33,0,22,-6,19,-2,13,7,18,18,7,13,-2,19,-6,22)

def run():
    model=algebraic_model(); assert model['passed']
    ring=QuotientRing(cyclotomic(17))
    def decode(matrix):
        return tuple(tuple(ring.element(row) for row in line) for line in matrix)
    a,b=[decode(model['matrices'][key]) for key in ('sigma1','sigma2')]
    # Both generators have order 34, hence b^-2=b^32.
    w=mm(power(a,2),power(b,32))
    trace=sum(w[i][i] for i in range(5))
    assert trace.coefficients==tuple(map(Q,EXPECTED_TRACE))
    # A purely integral proof, independent of the root-ball calculation:
    # Tr_Q(zeta17)/Q(zeta^m)=16 for m=0 mod17 and -1 otherwise.
    # Thus sum_(k=1)^16 |sigma_k(trace)|^2 = 17 sum c_j^2-(sum c_j)^2.
    squared_trace_sum=17*sum(c*c for c in trace.coefficients)-sum(trace.coefficients)**2
    conjugate=sum(c*ring.generator**((-j)%17) for j,c in enumerate(trace.coefficients))
    norm_element=trace*conjugate
    independent_field_trace=16*norm_element.coefficients[0]-sum(norm_element.coefficients[1:])
    assert squared_trace_sum==independent_field_trace==36406
    assert squared_trace_sum>16*5**2
    roots=seventeenth_roots(128); root_proof=root_certificate(128)
    assert root_proof['passed']
    conjugates=[]
    for k in range(1,17):
        value=sum((roots[(k*j)%17]*c for j,c in enumerate(trace.coefficients)),ComplexBall(0))
        low=value.center.real-value.radius
        high=value.center.real+value.radius
        conjugates.append({'embedding_exponent':k,'real_lower':str(low),
                           'real_upper':str(high),'ball':value.to_json()})
    witness=conjugates[7]
    assert Q(witness['real_lower'])>125 and Q(witness['real_upper'])<126
    record={'schema':'asterion/pure-braid-infinite-order/1','passed':True,
            'source_commit':'9b69eab9beff3011bc6216b30a460c2c6d0e97be',
            'word':'sigma1^2 sigma2^-2 = U V^-1',
            'word_determinant':1,'determinant_argument':'det(sigma1)=det(sigma2)=zeta17^9',
            'model_sha256':model['matrix_sha256'],
            'trace_coefficients_ascending':[str(c) for c in trace.coefficients],
            'field_modulus_ascending':[str(c) for c in cyclotomic(17)],
            'Galois_embedding':'zeta17 -> zeta17^8',
            'strict_rational_bound':'125 < Re(sigma8(trace(U V^-1))) < 126',
            'finite_order_trace_modulus_bound':5,
            'sum_squared_conjugate_traces':int(squared_trace_sum),
            'finite_order_upper_bound_on_sum_squared_conjugate_traces':400,
            'root_free_integer_proof':'17*sum(c_j^2)-(sum(c_j))^2 = 36406 > 16*25 = 400',
            'infinite_order_proved':True,'infinite_projective_order_proved':True,
            'proof':'Finite order survives field embeddings and forces |trace|<=5, '
                    'hence the sum of sixteen squared trace moduli is <=400, '
                    'contradicting the exact integer36406. The additional certified '
                    'real-part bound locates one offending embedding. A determinant-one matrix '
                    'with finite projective order has a scalar power cI with c^5=1, '
                    'hence finite ordinary order, also excluded.',
            'classification_of_finite_linear_groups_used':False,
            'unitarity_used':False,'density_proved_by_this_witness':False,
            'actual_KZ_identification_dependency':'pinned half-braid descent, specialized '
                    'irreducibility, and Tuba-Wenzl equivalence-class theorem; separately replayed',
            'root_proof':root_proof,'conjugate_trace_enclosures':conjugates}
    Path('braid_infinite_order_receipt.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({k:record[k] for k in ('passed','word','strict_rational_bound',
        'infinite_order_proved','infinite_projective_order_proved')},indent=2),flush=True)

if __name__=='__main__':run()
