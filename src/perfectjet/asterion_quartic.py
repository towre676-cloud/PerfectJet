"""An explicit invariant quartic class in the weight-six E8 arc algebra.

The invariant tensor 2*Id-Omega-2*C tensor C has eigenvalues -434,14,0
on 1+3875+27000 in Sym²(g). Its diagonal vanishes, and its squared tensor
norm is947856. The duality proof in ASTERION_QUARTIC.md identifies this
with a nonzero arc class of length4, Li degree2 and conformal weight6.
Its individual image in the simple VOA is deliberately left undetermined.
"""
from __future__ import annotations

from copy import deepcopy
from fractions import Fraction as Q
from functools import lru_cache
import hashlib
from itertools import combinations
import json

from .asterion_e8 import E8LieAlgebra
from .asterion_relations import (
    AffinePBW, _add, _casimir_quadratic, _primitive, _symmetric_raising,
    weight_four_completeness_receipt,
)
from .asterion_kernel_tower import E8Freudenthal, short_current_injectivity_receipt
from .exact import nullspace, rref


def _q(value):
    if isinstance(value, (bool, float)):
        raise ValueError('exact rational coefficients required')
    try:
        return Q(value)
    except (TypeError, ValueError, ZeroDivisionError) as exc:
        raise ValueError('exact rational coefficients required') from exc


def _vector(value):
    if not isinstance(value, dict):
        raise ValueError('a sparse E8 vector is required')
    result = {}
    for i, z in value.items():
        if type(i) is not int or not 0 <= i < 248:
            raise ValueError('basis indices must be integers in0..247')
        z = _q(z)
        if z:
            result[i] = z
    return result


def invariant_pairing(x, y, algebra=None):
    """The root-length-two E8 form, without a Killing-form factor60."""
    g = algebra or E8LieAlgebra()
    x, y = _vector(x), _vector(y)
    value = Q(0)
    for i, a in x.items():
        if i < 8:
            value += a * sum(g.cartan_matrix[i][j] * b for j, b in y.items() if j < 8)
        else:
            opposite = g.root_index[tuple(-v for v in g.index_root[i])]
            value += a * y.get(opposite, Q(0))
    return value


def quartic_value(x, y, algebra=None):
    """F0(x,y)=2Bxy²-B([x,y],[x,y])-2Bxx*Byy at exact E8 points."""
    g = algebra or E8LieAlgebra()
    x, y = _vector(x), _vector(y)
    bracket = g.bracket(x, y)
    return (2 * invariant_pairing(x, y, g) ** 2
            - invariant_pairing(bracket, bracket, g)
            - 2 * invariant_pairing(x, x, g) * invariant_pairing(y, y, g))


def quartic_operator(polynomial, module=None):
    """Apply the actual tensor operator2Id-Omega-2|C><C| on Sym²(g)."""
    module = module or AffinePBW()
    if not isinstance(polynomial, dict):
        raise ValueError('an exact sparse quadratic polynomial is required')
    q = {}
    for monomial, z in polynomial.items():
        if (not isinstance(monomial, tuple) or len(monomial) != 2
                or any(type(i) is not int or not 0 <= i < 248 for i in monomial)):
            raise ValueError('quadratic monomials require two E8 basis indices')
        _add(q, {tuple(sorted(monomial)): _q(z)})
    out = {key: 2*z for key, z in q.items()}
    trace = Q(0)
    for (i, j), z in q.items():
        _add(out, module.omega_pair(i, j), -z)
        trace += z * module.invariant_form(i, j)
    _add(out, _casimir_quadratic(module), -2 * trace)
    return out


def pair_slot_certificate():
    """The six-slot elementary proof of the S_(2,2) reduction."""
    triple = ((1,1,0,1,0,0), (1,0,1,0,1,0),
              (0,1,1,0,0,1), (0,0,0,1,1,1))
    bianchi = ((1,0,0,0,0,-1), (0,1,0,0,-1,0),
               (0,0,1,-1,0,0), (1,1,1,0,0,0))
    a, pivots = rref(triple)
    b, other = rref(bianchi)
    partitions = ((0,1,2,3),(0,2,1,3),(0,3,1,2),
                  (1,2,0,3),(1,3,0,2),(2,3,0,1))
    keys = [(tuple(sorted(p[:2])),tuple(sorted(p[2:]))) for p in partitions]
    class_sum = [[0]*6 for _ in range(6)]
    for i,j in combinations(range(4),2):
        for row, p in enumerate(partitions):
            changed = tuple(j if k == i else i if k == j else k for k in p)
            key = tuple(sorted(changed[:2])),tuple(sorted(changed[2:]))
            class_sum[row][keys.index(key)] += 1
    class_sum_zero = all(not any(sum(z*v for z,v in zip(row, vector)) for row in class_sum)
                         for vector in nullspace(triple,6))
    return {'passed': a == b and pivots == other and len(pivots) == 4 and class_sum_zero,
            'slots': ['ab|cd','ac|bd','ad|bc','bc|ad','bd|ac','cd|ab'],
            'triple_symmetrizer_rows': [list(row) for row in triple],
            'pair_swap_and_Bianchi_rows': [list(row) for row in bianchi],
            'exact_rowspace_rank': len(pivots),
            'sum_six_transpositions_zero_on_solution_space': class_sum_zero,
            'meaning': 'All four triple symmetrizers vanish iff pair interchange holds and total symmetrization vanishes.'}


def casimir_cutoff_certificate(character_rows, module=None):
    """Actual Casimirs and the compact-Hermitian bound C_total<=168."""
    module = module or AffinePBW()
    def casimir_value(labels):
        root = [sum(module.cartan_inverse[i][j]*labels[j] for j in range(8)) for i in range(8)]
        return sum(a*b for a,b in zip(root,labels))+2*sum(root)
    values = []
    for row in character_rows:
        labels = row['dynkin_labels']
        casimir = casimir_value(labels)
        if casimir.denominator != 1:
            raise ArithmeticError('nonintegral E8 Casimir in quartic source')
        values.append({'dimension':row['dimension'],'Casimir':int(casimir)})
    expected = {1:0,3875:96,27000:124,147250:144,2450240:180,4881384:200}
    actual = {row['dimension']:row['Casimir'] for row in values}
    exterior = {248:casimir_value((0,0,0,0,0,0,1,0)),
                30380:casimir_value((0,0,0,0,0,1,0,0))}
    return {'passed': actual == expected and exterior == {248:60,30380:120}
                     and pair_slot_certificate()['passed'],
            'actual_source_Casimirs': values, 'adjoint_Casimir':60,
            'actual_exterior_square_Casimirs':{str(d):int(z) for d,z in exterior.items()},
            'symmetric_allowed_pair_spectrum':[-60,-12],
            'antisymmetric_allowed_pair_spectrum':[-30,0],
            'pair_operator_inequality': 'Omega_ij <= -6*(1+swap_ij)',
            'sum_swap_on_S22':0,'total_Casimir_upper_bound':168,
            'excluded_kernel_modules':[row for row in values if row['Casimir'] > 168],
            'proof': 'Use the invariant positive Hermitian form from a compact real form. '
                     'Each pair Casimir is selfadjoint; its allowed symmetric spectrum is at most-12 '
                     'and its antisymmetric spectrum at most0. Sum the six pair inequalities; '
                     'the transposition class sum vanishes on the pair-slot solution space. '
                     'C_total=4*60+2*sum(Omega_ij)<=240-72=168.'}


def multiplication_27000_certificate(module=None):
    """A nonzero coefficient of (P_W tensor P_W)delta_22(C*e_theta²)."""
    module = module or AffinePBW()
    theta = module.algebra.root_index[module.algebra.roots[-1]]
    target = tuple(sorted((theta, 0)))
    coefficients = []
    for a in range(8):
        q = {tuple(sorted((theta, a))): Q(1)}
        first = {}
        for (i,j), z in q.items():
            _add(first, module.omega_pair(i,j), z)
        second = {}
        for (i,j), z in first.items():
            _add(second, module.omega_pair(i,j), z)
        projected = {key: Q(148,868)*z for key,z in q.items()}
        _add(projected, first, -Q(72,868))
        _add(projected, second, -Q(1,868))
        coefficients.append(projected.get(target, Q(0)))
    contraction = sum(coefficients[a]*module.cartan_inverse[a][b]*coefficients[b]
                      for a in range(8) for b in range(8))
    coefficient = 4*contraction
    expected = (Q(1,7),0,0,0,0,0,-Q(1,7),0)
    return {'passed': tuple(coefficients) == expected and coefficient == Q(8,49),
            'highest_target': 'C*e_theta^2, weight2theta, dimension27000',
            'projector': 'P_W=(148-72*Omega-Omega^2)/868',
            'Cartan_coefficients': [str(z) for z in coefficients],
            'inverse_Cartan_contraction': str(contraction),
            'nonzero_polarization_coefficient': str(coefficient),
            'coefficient_slot': '(e_theta*h_0) tensor (e_theta*h_0)',
            'root_inputs_excluded_by_weight': True,
            'conclusion': 'Multiplication is nonzero on the unique27000 summand of Sym²W.'}


def multiplication_147250_certificate(module=None, *, include_vector=False):
    """An actual highest quartic in the multiplication image, without a table."""
    module = module or AffinePBW()
    def project(pair):
        pair = tuple(sorted(pair))
        first = module.omega_pair(*pair)
        second = {}
        for ij,z in first.items():
            _add(second,module.omega_pair(*ij),z)
        _add(second,first,72)
        _add(second,{pair:Q(1)},720)
        out = {pair:Q(1)}
        _add(out,second,-Q(1,868))
        return out
    def casimir(polynomial):
        out = {key:240*z for key,z in polynomial.items()}
        for monomial,z in polynomial.items():
            for i,j in combinations(range(4),2):
                other = tuple(monomial[k] for k in range(4) if k != i and k != j)
                for pair,c in module.omega_pair(monomial[i],monomial[j]).items():
                    _add(out,{tuple(sorted(other+pair)):2*z*c})
        return out
    source_pairs = ((128,243),(211,247))
    first,second = (project(pair) for pair in source_pairs)
    polynomial = {}
    for ij,z in first.items():
        for kl,w in second.items():
            _add(polynomial,{tuple(sorted(ij+kl)):z*w})
    polynomial = _primitive(polynomial)
    sizes = [len(polynomial)]
    for eigenvalue in (200,180):
        image = casimir(polynomial)
        _add(image,polynomial,-eigenvalue)
        polynomial = _primitive(image)
        sizes.append(len(polynomial))
    labels = (0,0,0,0,0,0,0,1)
    target = tuple(sum(module.cartan_inverse[i][j]*labels[j] for j in range(8)) for i in range(8))
    weight_checked = all(tuple(sum(module.weights[i][r] for i in monomial)
                               for r in range(8)) == target for monomial in polynomial)
    highest = [not _symmetric_raising(module,polynomial,node) for node in range(8)]
    eigenvector = casimir(polynomial) == {key:144*z for key,z in polynomial.items()}
    encoded = [[list(key),str(z)] for key,z in sorted(polynomial.items())]
    result = {'passed':bool(polynomial) and weight_checked and all(highest) and eigenvector,
              'source_pairs':[list(pair) for pair in source_pairs],
              'source_product':'P_W(e128*e243)*P_W(e211*e247)',
              'Casimir_filter':'(C_total-200)*(C_total-180)',
              'primitive_term_counts':sizes,'target_dynkin_labels':list(labels),
              'target_root_coordinates':[int(z) for z in target],
              'all_monomials_have_target_weight':weight_checked,
              'all_eight_raising_checks':highest,'Casimir_144_eigenvector_checked':eigenvector,
              'final_vector_sha256':hashlib.sha256(json.dumps(encoded,separators=(',',':')).encode()).hexdigest(),
              'first_nonzero_term':encoded[0] if encoded else None,
              'conclusion':'Multiplication is nonzero on the unique147250 summand of Sym²W.'}
    if include_vector:
        result['highest_quartic_vector'] = encoded
    return result


@lru_cache(maxsize=1)
def _grounding():
    module = AffinePBW()
    earlier = weight_four_completeness_receipt(module)
    casimir = _casimir_quadratic(module)
    q = module.highest_quadratic_3875()
    theta = module.algebra.root_index[module.algebra.roots[-1]]
    records = []
    for dimension, omega, vector, eigenvalue in (
            (1, -60, casimir, -434), (3875, -12, q, 14),
            (27000, 2, {(theta, theta): Q(1)}, 0)):
        expected = {key: z*eigenvalue for key, z in vector.items() if z*eigenvalue}
        records.append({'dimension': dimension, 'Omega_eigenvalue': omega,
                        'quartic_operator_eigenvalue': eigenvalue,
                        'actual_highest_vector_identity_checked': quartic_operator(vector, module) == expected})
    short = short_current_injectivity_receipt(6)
    short_singlets = next(row['exact_Gram_rank'] for row in short['blocks'] if row['dimension'] == 1)
    voa = E8Freudenthal(6).voa_character(6)
    voa_singlets = next(row['multiplicity'] for row in voa['irreducibles'] if row['dimension'] == 1)
    return {'quadratic_highest_modules_exhausted': earlier['checks']['quadratic_highest_modules_exhaust_Sym2'],
            'actual_Omega_spectrum_checked': earlier['checks']['quadratic_projector_spectrum_checked'],
            'I_times_g_equals_Sym3': earlier['checks']['I_times_g_onto_Sym3'],
            'operator_records': records,
            'short_current_check': short['passed'], 'short_current_singlets': short_singlets,
            'simple_VOA_character_check': voa['passed'], 'simple_VOA_singlets': voa_singlets,
            'exterior_square_exhausted': short['checks']['exterior_square_exhausted'],
            'no_adjoint_in_Sym2': all(row['dimension'] != 248 for row in
                                     earlier['quadratic_highest_modules']),
            'grounding_scope': 'Actual E8 highest vectors, Weyl dimensions and split-Casimir eigenvectors; exact projected-polarization I*g surjectivity; affine Gram ranks and lattice/Freudenthal character.'}


def quartic_receipt(exhaustive=False):
    """JSON-safe proof receipt for a nonzero invariant quartic arc class."""
    if not isinstance(exhaustive, bool):
        raise ValueError('exhaustive must be a boolean')
    ground = deepcopy(_grounding())
    from .asterion_quartic_characters import quartic_characters_receipt
    characters = quartic_characters_receipt(exhaustive=exhaustive)
    cutoff = casimir_cutoff_certificate(characters['Sym2_W']['irreducibles'])
    multiplication27000 = multiplication_27000_certificate()
    multiplication147250 = multiplication_147250_certificate(include_vector=exhaustive)
    slots = pair_slot_certificate()
    norm = sum(row['dimension'] * row['quartic_operator_eigenvalue'] ** 2
               for row in ground['operator_records'])
    g = E8LieAlgebra()
    x, y = {0: Q(1)}, {2: Q(1)}
    actual_value = quartic_value(x, y, g)
    checks = {'quadratic_decomposition': ground['quadratic_highest_modules_exhausted'],
              'actual_Omega_spectrum': ground['actual_Omega_spectrum_checked'],
              'cubic_ideal_surjectivity': ground['I_times_g_equals_Sym3'],
              'actual_operator_eigenvectors': all(row['actual_highest_vector_identity_checked']
                                                for row in ground['operator_records']),
              'elementary_pair_slot_duality': slots['passed'],
              'norm_nonzero': norm == 947856,
              'actual_Cartan_polynomial_witness': actual_value == -8,
              'finite_character_and_Gram_sources': ground['short_current_check']
                    and ground['simple_VOA_character_check'] and ground['exterior_square_exhausted']
                    and ground['no_adjoint_in_Sym2'],
              'whole_weight6_invariant_kernel_lower_bound':
                    ground['short_current_singlets'] + 1 + 1 - ground['simple_VOA_singlets'] >= 1,
              'independent_quartic_characters': characters['passed'],
              'multiplication_27000_nonzero': multiplication27000['passed'],
              'multiplication_147250_nonzero': multiplication147250['passed'],
              'Casimir_cutoff':cutoff['passed']}
    return {'schema': 'perfectjet/asterion-quartic-boundary/1', 'passed': all(checks.values()),
            'checks': checks, 'exhaustive': exhaustive,
            'conformal_weight': 6, 'Li_degree': 2, 'ordinary_polynomial_length': 4,
            'formula': 'F0(x,y)=2*B(x,y)^2-B([x,y],[x,y])-2*B(x,x)*B(y,y)',
            'jet_coordinates': 'x is the zero jet; y is the divided first jet',
            'metric': 'B(h_i,h_j)=Cartan_ij; B(e_alpha,e_minus_alpha)=1; long roots have squared length2',
            'tensor_operator': '2*Id-Omega-2*C tensor C =14*(K_3875-31*K_1)',
            'tensor_norm_squared': norm,
            'Casimir_norm_squared': 248,
            'invariant_mu_relation': 'mu(K_3875)=31*mu(K_1)=C^2/8',
            'exact_quartic_arc_invariant_dimension': 1,
            'arc_sector_dual': 'ker[mu:Sym^2(1+3875)->Sym^4(g)]',
            'pair_slot_certificate': slots, 'grounding': ground,
            'actual_Cartan_witness': {'x': [[0,'1']], 'y': [[2,'1']], 'F0': int(actual_value)},
            'arc_dimension_lower_bound_increment': 1,
            'quartic_arc_dimension_lower_bound': characters['quartic_arc_dimension_lower_bound'],
            'explicit_invariant_already_included_in_character_bound': True,
            'quartic_characters': characters,
            'multiplication_27000_certificate': multiplication27000,
            'multiplication_147250_certificate': multiplication147250,
            'Casimir_cutoff_certificate':cutoff,
            'Casimir_kernel_upper_bound':cutoff['total_Casimir_upper_bound'],
            'Casimir_cutoff_excluded_kernel_modules':cutoff['excluded_kernel_modules'],
            'remaining_unresolved_extra_kernel_modules': [],
            'obvious_nonzero_multiplication_blocks':{'1':'C^2','3875':'C*Q','4881384':'Q^2'},
            'exact_quartic_multiplication_kernel_character':{'1':1,'3875':1},
            'exact_quartic_arc_dimension':3876,
            'exact_full_quartic_kernel_claim': True,
            'complete_weight6_arc_kernel_claim': False,
            'whole_weight6_invariant_counts': {'short_at_most_two_currents': ground['short_current_singlets'],
                 'three_current_arc_Cartan_3_form': 1, 'quartic_arc_invariant': 1,
                 'simple_VOA': ground['simple_VOA_singlets'], 'kernel_lower_bound': 1},
            'three_current_invariant_proof': 'Only mode partition(3,2,1) admits the unique bracket Cartan3-form. '
                'All length3 arc relations have source I27000 tensor g, with no invariant; the symmetric-square decomposition has no adjoint.',
            'voa_image_of_explicit_quartic_class_computed': False,
            'affine_null_lift_of_F0_computed': False,
            'proof_document': 'docs/ASTERION_QUARTIC.md',
            'scope': 'A nonzero explicit invariant arc class, included in the independent3876-dimensional quartic arc lower bound. '
                'Invariant counts force at least one weight6 kernel singlet, but do not locate it in Li degree2 or3. '
                'The finite quartic multiplication kernel is exactly1+3875, dimension3876. '
                'The full weight6 arc-map kernel is not classified.'}
