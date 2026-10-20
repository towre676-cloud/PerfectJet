"""Higher E8 arc-kernel translation towers and exact finite characters.

The all-weight statement is a proved lower bound, not a full differential
presentation.  On divided jets D*x[r]=(r+1)*x[r+1] and E*x[r]=x[r-1], one
has [E,D]=N, the ordinary polynomial-degree operator.  The weight-four
generator F has N-degree3 and E*F=0, so E^r D^r F=3^r*r!*F at every order.

Finite E8 characters are computed independently by Weyl-chamber-folded
Freudenthal recursion and the lattice-VOA weight multiplicities.  No Sage or
floating arithmetic is used.  Numerical character requests are bounded;
the translation identity itself has no truncation hypothesis.
"""
from __future__ import annotations

from fractions import Fraction as Q
from functools import lru_cache
from itertools import product
from math import comb, factorial, isqrt

from .asterion_e8 import E8LieAlgebra
from .asterion_relations import (
    AffinePBW, _add, _casimir_quadratic, _primitive,
    highest_weight_dimension, jet_derivative,
)
from .asterion_currents import CurrentPopulations, colored_partitions
from .exact import nullspace, rref


def _integer(value, name, low=0, high=12):
    if isinstance(value, bool) or not isinstance(value, int) or not low <= value <= high:
        raise ValueError(f"{name} must be an integer in {low}..{high}")
    return value


def _labels(value, *, dominant=True):
    if (not isinstance(value, (tuple, list)) or len(value) != 8
            or any(isinstance(x, bool) or not isinstance(x, int) for x in value)
            or (dominant and any(x < 0 for x in value))):
        raise ValueError("eight integer labels are required, nonnegative for a highest weight")
    return tuple(value)


def _jet_polynomial(value):
    if not isinstance(value, dict):
        raise ValueError("a jet polynomial must be a sparse monomial dictionary")
    out = {}
    for monomial, coefficient in value.items():
        if not isinstance(monomial, tuple):
            raise ValueError("jet monomials must be tuples of(index,derivative order)")
        for item in monomial:
            if (not isinstance(item, tuple) or len(item) != 2
                    or any(isinstance(x, bool) or not isinstance(x, int) for x in item)
                    or not 0 <= item[0] < 248 or item[1] < 0):
                raise ValueError("invalid divided-jet variable")
        if isinstance(coefficient, bool) or not isinstance(coefficient, (int, Q)):
            raise ValueError('jet coefficients must be exact integers or Fractions')
        z = Q(coefficient)
        if z:
            _add(out, {tuple(sorted(monomial)): z})
    return out


def lower_jets(polynomial):
    """E is the locally nilpotent lowering derivation E*x[r]=x[r-1]."""
    polynomial = _jet_polynomial(polynomial)
    out = {}
    for monomial, z in polynomial.items():
        for position, (i, order) in enumerate(monomial):
            if order:
                changed = list(monomial)
                changed[position] = i, order-1
                _add(out, {tuple(sorted(changed)): z})
    return out


def differentiate_jets(polynomial):
    return jet_derivative(_jet_polynomial(polynomial))


def multiply_jet_variable(polynomial, index, order=0):
    _integer(index, 'current index', 0, 247)
    _integer(order, 'derivative order', 0, 100)
    out = {}
    for monomial, z in _jet_polynomial(polynomial).items():
        _add(out, {tuple(sorted(monomial+((index, order),))): z})
    return out


def translation_tower_receipt(max_derivative=2):
    """Replay finite orders and retain the algebraic all-order left inverse."""
    _integer(max_derivative, 'maximum derivative', 0, 8)
    module = AffinePBW()
    q = module.highest_quadratic_3875()
    generator = module.quadratic_jet_tensor(q)
    lowest = not lower_jets(generator)
    tower, current = [], generator
    for order in range(max_derivative+1):
        lowered = current
        for _ in range(order):
            lowered = lower_jets(lowered)
        scalar = 3**order*factorial(order)
        expected = {key: z*scalar for key, z in generator.items()}
        tower.append({'conformal_weight': order+4, 'Li_degree': order+1,
                      'ordinary_polynomial_degree': 3,
                      'derivative_order': order, 'nonzero_monomials': len(current),
                      'left_inverse_scalar': scalar,
                      'left_inverse_checked': lowered == expected,
                      'nonzero': bool(current)})
        if order != max_derivative:
            current = differentiate_jets(current)
    all_checks = lowest and all(row['left_inverse_checked'] and row['nonzero'] for row in tower)
    return {'passed': all_checks, 'finite_checks': tower,
            'generator_lowering_zero': lowest,
            'all_order_identity': 'E^r D^r F_Q=3^r*r!*F_Q for every integer r>=0',
            'proof': '[E,D]=N; N(F_Q)=3F_Q; E(F_Q)=0; induction gives the displayed identity. '
                     'E preserves the arc ideal since E(D^s q)=s*deg(q)*D^(s-1)q for homogeneous ordinary relations q.',
            'imported_prior_theorems': [
                'The783-term F_Q has nonzero arc class and is the weight-four3875 kernel module.',
                'The ordinary cubic component is zero: I27000*g=Sym^3(g).'],
            'translation_injective_on_every_positive_ordinary_degree': True,
            'general_injectivity_proof':
                'On degree p>0 the operators satisfy [E,D]=p. If Dv=0, then '
                'D^r E^r v=(-p)^r*r!*v. Local nilpotence of E forces v=0. '
                'Both operators descend to the arc quotient; only D is asserted to preserve its arc-map kernel.',
            'all_weight_kernel_dimension_lower_bound': 3875,
            'all_weight_lower_bound_starts_at': 4,
            'all_weight_Jordan_grade_lower_bound': 31,
            'Jordan_grade_count': 125,
            'full_higher_kernel_claim': False}


def differential_annihilator_receipt(index=247, max_derivative=2):
    """Exact Leibniz syzygies descending from x[0]*F_Q=0 in the arc algebra."""
    _integer(index, 'current index', 0, 247)
    _integer(max_derivative, 'maximum derivative', 0, 6)
    module = AffinePBW()
    generator = module.quadratic_jet_tensor(module.highest_quadratic_3875())
    ordinary_zero_count = min(sum(order == 0 for _, order in monomial)
                              for monomial in generator)
    source = multiply_jet_variable(generator, index)
    source_in_cubic_ideal = all(sum(r == 0 for _, r in monomial) >= 3 for monomial in source)
    derivatives = [generator]
    for _ in range(max_derivative):
        derivatives.append(differentiate_jets(derivatives[-1]))
    rows, left = [], source
    for order in range(max_derivative+1):
        leibniz = {}
        for j in range(order+1):
            term = multiply_jet_variable(derivatives[order-j], index, j)
            _add(leibniz, term, comb(order, j)*factorial(j))
        rows.append({'derivative_order': order, 'identity_checked': leibniz == left,
                     'nonzero_monomials_before_arc_quotient': len(left),
                     'arc_class_zero_reason': 'D^r of a known ordinary cubic-ideal element'})
        if order != max_derivative:
            left = differentiate_jets(left)
    return {'passed': source_in_cubic_ideal and all(row['identity_checked'] for row in rows),
            'current_index': index, 'generator_zero_jet_degree': ordinary_zero_count,
            'all248_ordinary_currents_annihilate_K4': ordinary_zero_count == 2,
            'source_in_ordinary_cubic_ideal': source_in_cubic_ideal,
            'syzygies': rows,
            'all_order_syzygy': 'sum_(j=0)^r binom(r,j)*j!*x^[j]*D^(r-j)F_Q=0 in the arc algebra',
            'weight5_generated_component': 'only D(K4), dimension3875; g[0]*K4=0',
            'complete_syzygy_presentation_claim': False}


class E8Freudenthal:
    """Small dominant-weight exact character engine, bounded by conformal degree.

    Freudenthal recursion is folded by Weyl symmetry after each upward root
    step.  From a dominant weight mu, ||mu+k*alpha||² strictly increases for
    every positive root and k>0.  The recursion is therefore acyclic in norm.
    """
    def __init__(self, max_degree=6):
        self.max_degree = _integer(max_degree, 'maximum conformal degree', 0, 12)
        self.max_norm = 2*self.max_degree
        self.algebra = E8LieAlgebra()
        module = AffinePBW(algebra=self.algebra)
        self.inverse = tuple(tuple(int(z) for z in row) for row in module.cartan_inverse)
        self.positive_roots = tuple(root for root in self.algebra.roots if sum(root) > 0)
        self._dominant = lru_cache(maxsize=50000)(self._dominant_uncached)
        self._multiplicity = lru_cache(maxsize=50000)(self._multiplicity_uncached)
        self.recursion_trace = {}

    def root_coordinates(self, dynkin_labels):
        labels = _labels(dynkin_labels)
        return tuple(sum(self.inverse[i][j]*labels[j] for j in range(8)) for i in range(8))

    def dynkin_labels(self, root_coordinates):
        root = _labels(root_coordinates, dominant=False)
        return tuple(sum(self.algebra.cartan_matrix[i][j]*root[j] for j in range(8))
                     for i in range(8))

    def norm(self, root_coordinates):
        root = _labels(root_coordinates, dominant=False)
        labels = self.dynkin_labels(root)
        return sum(a*b for a, b in zip(root, labels))

    def casimir(self, root_coordinates):
        root = _labels(root_coordinates, dominant=False)
        return self.norm(root)+2*sum(root)

    def dominant(self, root_coordinates):
        root = _labels(root_coordinates, dominant=False)
        if self.norm(root) > self.max_norm:
            raise ValueError('weight norm exceeds the configured character bound')
        return self._dominant(root)

    def _dominant_uncached(self, root):
        root = list(root)
        for _ in range(10000):
            labels = self.dynkin_labels(root)
            negative = next((i for i, z in enumerate(labels) if z < 0), None)
            if negative is None:
                return tuple(root)
            root[negative] -= labels[negative]
        raise ArithmeticError('Weyl chamber reflection did not terminate')

    def dominant_weights(self, max_norm=None):
        maximum = self.max_norm if max_norm is None else _integer(max_norm, 'maximum squared norm', 0, self.max_norm)
        bounds = [isqrt(maximum//self.inverse[i][i]) for i in range(8)]
        weights = []
        for labels in product(*(range(bound+1) for bound in bounds)):
            root = self.root_coordinates(labels)
            norm = sum(a*b for a, b in zip(root, labels))
            if norm <= maximum:
                weights.append((labels, root, norm))
        if len(weights) > 2048:
            raise ValueError('dominant-weight enumeration exceeds2048 states')
        return tuple(sorted(weights, key=lambda row: (row[2], sum(row[1]), row[0]), reverse=True))

    def multiplicity(self, highest_dynkin_labels, weight_root_coordinates):
        highest = self.root_coordinates(highest_dynkin_labels)
        if self.norm(highest) > self.max_norm:
            raise ValueError('highest weight exceeds the configured norm bound')
        weight = _labels(weight_root_coordinates, dominant=False)
        if self.norm(weight) > self.norm(highest):
            return 0
        return self._multiplicity(highest, self._dominant(weight))

    def _multiplicity_uncached(self, highest, weight):
        if highest == weight:
            return 1
        if (self.norm(weight) >= self.norm(highest)
                or any(a < b for a, b in zip(highest, weight))):
            return 0
        denominator = self.casimir(highest)-self.casimir(weight)
        if denominator <= 0:
            raise ArithmeticError('nonpositive dominant Freudenthal denominator')
        labels = self.dynkin_labels(weight)
        numerator, terms = 0, []
        for alpha in self.positive_roots:
            pairing = sum(a*b for a, b in zip(labels, alpha))
            for k in range(1, isqrt(self.norm(highest)//2)+1):
                squared_norm = self.norm(weight)+2*k*pairing+2*k*k
                if squared_norm > self.norm(highest):
                    break
                upper = tuple(a+k*b for a, b in zip(weight, alpha))
                dominant_upper = self._dominant(upper)
                multiplicity = self._multiplicity(highest, dominant_upper)
                if multiplicity:
                    coefficient = 2*(pairing+2*k)
                    numerator += coefficient*multiplicity
                    terms.append((alpha, k, dominant_upper, coefficient, multiplicity))
        value = Q(numerator, denominator)
        if value.denominator != 1 or value < 0:
            raise ArithmeticError('Freudenthal multiplicity was not a nonnegative integer')
        self.recursion_trace[highest, weight] = {
            'denominator': denominator, 'numerator': numerator,
            'multiplicity': value.numerator, 'nonzero_root_terms': terms}
        return value.numerator

    def voa_character(self, degree):
        degree = _integer(degree, 'conformal degree', 0, self.max_degree)
        weights = self.dominant_weights(2*degree)
        partitions = colored_partitions(8, degree)
        decomposition, rows = [], []
        for labels, root, norm in weights:
            actual = partitions[degree-norm//2]
            previous = sum(copies*self.multiplicity(highest, root)
                           for highest, copies in decomposition)
            copies = actual-previous
            if copies < 0:
                raise ArithmeticError('negative VOA irreducible multiplicity')
            if copies:
                decomposition.append((labels, copies))
            rows.append({'dynkin_labels': labels, 'root_coordinates': root,
                         'squared_norm': norm, 'lattice_weight_multiplicity': actual,
                         'higher_irrep_contribution': previous,
                         'highest_irrep_multiplicity': copies})
        irreps = [{'dynkin_labels': labels, 'multiplicity': copies,
                   'dimension': highest_weight_dimension(labels, self.algebra)}
                  for labels, copies in decomposition]
        reconstructed = sum(row['multiplicity']*row['dimension'] for row in irreps)
        scalar = CurrentPopulations(degree).simple[degree]
        return {'conformal_degree': degree, 'irreducibles': irreps,
                'dominant_weight_rows': rows, 'reconstructed_dimension': reconstructed,
                'independent_E4_eta_dimension': scalar,
                'passed': reconstructed == scalar,
                'weight_formula': 'm_n(mu)=p8(n-||mu||²/2), from the E8 lattice-VOA realization',
                'method': 'Weyl-chamber-folded exact Freudenthal recursion',
                'complete_dominant_weight_bound': 2*degree}


def _highest_antisymmetric_pair(module, labels):
    """Solve a bounded exterior-square highest-weight sector, not a full tensor cube."""
    target = tuple(sum(module.cartan_inverse[i][j]*labels[j] for j in range(8))
                   for i in range(8))
    columns = [(i, j) for i in range(248) for j in range(i+1, 248)
               if tuple(a+b for a, b in zip(module.weights[i], module.weights[j])) == target]
    if len(columns) > 128:
        raise ValueError('exterior-square highest sector exceeds128 columns')
    rows = {}
    for column, pair in enumerate(columns):
        for node in range(8):
            e = next(iter(module.algebra.simple_e(node)))
            for position, x in enumerate(pair):
                for y, z in module.algebra.basis_bracket(e, x).items():
                    changed = list(pair)
                    changed[position] = y
                    a, b = changed
                    if a == b:
                        continue
                    key = node, tuple(sorted(changed))
                    rows.setdefault(key, [Q(0)]*len(columns))[column] += z*(1 if a < b else -1)
    kernel = nullspace(list(rows.values()), len(columns))
    if len(kernel) != 1:
        raise ArithmeticError('exterior-square highest multiplicity must be one')
    return _primitive({pair: z for pair, z in zip(columns, kernel[0]) if z}), len(columns)


def _two_current_lift(module, pair_polynomial, first_mode, second_mode, antisymmetric=False):
    out = {}
    sign = -1 if antisymmetric else 1
    for (i, j), z in pair_polynomial.items():
        _add(out, module.symmetrize(((first_mode, i), (second_mode, j))), z/2)
        _add(out, module.symmetrize(((first_mode, j), (second_mode, i))), sign*z/2)
    return out


def short_current_injectivity_receipt(degree=6):
    """Certify the entire at-most-two-current arc piece at weights5 or6.

    Five highest-weight blocks exhaust g tensor g.  Their exact affine
    Gram ranks agree with the differential quadratic presentation.  A
    nondegenerate restricted Gram form gives injection into the simple
    quotient without having to enumerate any complete weight6 PBW sector.
    """
    _integer(degree, 'short-current conformal degree', 5, 6)
    module = AffinePBW(maximum_weight=degree)
    theta = module.algebra.root_index[module.algebra.roots[-1]]
    adjoint, adjoint_columns = _highest_antisymmetric_pair(module, (0,0,0,0,0,0,1,0))
    exterior30380, exterior_columns = _highest_antisymmetric_pair(module, (0,0,0,0,0,1,0,0))
    cases = [((0,)*8, _casimir_quadratic(module), False, None),
             ((1,0,0,0,0,0,0,0), module.highest_quadratic_3875(), False, None),
             ((0,0,0,0,0,0,2,0), {(theta, theta): Q(1)}, False, None),
             ((0,0,0,0,0,0,1,0), adjoint, True, adjoint_columns),
             ((0,0,0,0,0,1,0,0), exterior30380, True, exterior_columns)]
    records = []
    for labels, polynomial, antisymmetric, search_columns in cases:
        states = []
        for second in range(1, degree//2+1):
            first = degree-second
            if first == second and antisymmetric:
                continue
            states.append(_two_current_lift(module, polynomial, first, second, antisymmetric))
        if labels == (0,0,0,0,0,0,1,0):
            states.append({((degree, theta),): Q(1)})
        gram = [[module.pairing(a, b) for b in states] for a in states]
        _, pivots = rref(gram)
        dimension = highest_weight_dimension(labels, module.algebra)
        expected = len(states)-(dimension == 27000)
        highest_checked = all(all(module.finite_highest_checks(state)) for state in states)
        records.append({'dynkin_labels': labels, 'dimension': dimension,
                        'antisymmetric_pair': antisymmetric,
                        'highest_search_columns': search_columns,
                        'highest_vector_nonzero_terms': len(polynomial),
                        'finite_highest_checked': highest_checked,
                        'states': len(states),
                        'Gram_matrix': [[str(z) for z in row] for row in gram],
                        'exact_Gram_rank': len(pivots), 'expected_arc_multiplicity': expected,
                        'passed': len(pivots) == expected and highest_checked})
    tensor_square_dimension = sum(row['dimension'] for row in records)
    # Symmetric and antisymmetric decompositions each separately exhaust their ambient square.
    symmetric_sum = sum(row['dimension'] for row in records if not row['antisymmetric_pair'])
    exterior_sum = sum(row['dimension'] for row in records if row['antisymmetric_pair'])
    injection_dimension = sum(row['dimension']*row['exact_Gram_rank'] for row in records)
    expected_dimension = ((degree-1)//2)*248**2 + (30876 if degree % 2 == 0 else 0)-27000+248
    checks = {'symmetric_square_exhausted': symmetric_sum == 248*249//2,
              'exterior_square_exhausted': exterior_sum == 248*247//2,
              'tensor_square_exhausted': tensor_square_dimension == 248**2,
              'all_exact_Gram_ranks': all(row['passed'] for row in records),
              'dimension_matches_arc_presentation': injection_dimension == expected_dimension}
    return {'passed': all(checks.values()), 'checks': checks, 'conformal_degree': degree,
            'blocks': records, 'injective_short_current_dimension': injection_dimension,
            'quadratic_ideal_module_dimension': 27000,
            'only_relations': 'the single D^(n-2)(I27000) copy; all other at-most-two-current classes inject',
            'Gram_argument': 'The affine contravariant form descends to the simple quotient. '
                            'Full rank on the known arc quotient forces injectivity there.',
            'dense_full_PBW_sector_allocated': False}


def tensor_cube_character_receipt():
    """Independently reconstruct all three Schur pieces of g tensor-cubed.

    Only241 distinct adjoint weights are convolved.  Highest weights are
    bounded by norm18, and exact Freudenthal subtraction certifies each
    finite character.  This avoids importing any large tensor-product table.
    """
    engine = E8Freudenthal(9)
    adjoint = {(0,)*8: 8, **{root: 1 for root in engine.algebra.roots}}
    square = {}
    for a, m in adjoint.items():
        for b, n in adjoint.items():
            root = tuple(x+y for x, y in zip(a, b))
            square[root] = square.get(root, 0)+m*n
    weights = engine.dominant_weights(18)
    inputs = {'symmetric_cube': {}, 'mixed_S21': {}, 'exterior_cube': {}}
    for _, root, _ in weights:
        cube = sum(m*square.get(tuple(x-y for x, y in zip(root, a)), 0)
                   for a, m in adjoint.items())
        two_one = 0
        for a, m in adjoint.items():
            rest = tuple(x-y for x, y in zip(root, a))
            if all(x % 2 == 0 for x in rest):
                two_one += m*adjoint.get(tuple(x//2 for x in rest), 0)
        three = adjoint.get(tuple(x//3 for x in root), 0) if all(x % 3 == 0 for x in root) else 0
        values = {'symmetric_cube': Q(cube+3*two_one+2*three, 6),
                  'mixed_S21': Q(cube-three, 3),
                  'exterior_cube': Q(cube-3*two_one+2*three, 6)}
        for name, value in values.items():
            if value.denominator != 1 or value < 0:
                raise ArithmeticError('Schur character multiplicity must be a nonnegative integer')
            inputs[name][root] = value.numerator
    expected = {'symmetric_cube': 248*249*250//6,
                'mixed_S21': (248**3-248)//3,
                'exterior_cube': 248*247*246//6}
    results = {}
    for name, multiplicities in inputs.items():
        decomposition, rows = [], []
        for labels, root, norm in weights:
            prior = sum(copies*engine.multiplicity(highest, root)
                        for highest, copies in decomposition)
            copies = multiplicities[root]-prior
            if copies < 0:
                raise ArithmeticError('Schur irreducible multiplicity was negative')
            if copies:
                decomposition.append((labels, copies))
            rows.append({'dynkin_labels': labels, 'squared_norm': norm,
                         'Schur_weight_multiplicity': multiplicities[root],
                         'higher_irrep_contribution': prior, 'highest_irrep_multiplicity': copies})
        irreps = [{'dynkin_labels': labels, 'multiplicity': copies,
                   'dimension': highest_weight_dimension(labels, engine.algebra)}
                  for labels, copies in decomposition]
        dimension = sum(row['multiplicity']*row['dimension'] for row in irreps)
        results[name] = {'irreducibles': irreps, 'dominant_weight_rows': rows,
                         'reconstructed_dimension': dimension,
                         'ambient_Schur_dimension': expected[name],
                         'passed': dimension == expected[name]}
    # Recover g tensor I27000 without a tensor table.  The degree2 lattice
    # character already proves V3875=V2-g-1, including all its finite weights.
    p8 = colored_partitions(8, 2)
    product_decomposition, product_rows = [], []
    for labels, root, norm in weights:
        actual = 0
        for a, m in adjoint.items():
            rest = tuple(x-y for x, y in zip(root, a))
            squared_norm = engine.norm(rest)
            if squared_norm <= 4:
                finite3875 = p8[2-squared_norm//2]-adjoint.get(rest, 0)-(rest == (0,)*8)
                actual += m*finite3875
        prior = sum(copies*engine.multiplicity(highest, root)
                    for highest, copies in product_decomposition)
        copies = actual-prior
        if copies < 0:
            raise ArithmeticError('g tensor3875 irreducible multiplicity was negative')
        if copies:
            product_decomposition.append((labels, copies))
        product_rows.append({'dynkin_labels': labels, 'tensor_weight_multiplicity': actual,
                             'higher_irrep_contribution': prior, 'highest_irrep_multiplicity': copies})
    product_irreps = [{'dynkin_labels': labels, 'multiplicity': copies,
                       'dimension': highest_weight_dimension(labels, engine.algebra)}
                      for labels, copies in product_decomposition]
    product_dimension = sum(row['dimension']*row['multiplicity'] for row in product_irreps)
    null_character = {}
    dimension_by_labels = {}
    for name in ('symmetric_cube', 'mixed_S21'):
        for row in results[name]['irreducibles']:
            labels = row['dynkin_labels']
            null_character[labels] = null_character.get(labels, 0)+row['multiplicity']
            dimension_by_labels[labels] = row['dimension']
    adjoint_labels = (0,0,0,0,0,0,1,0)
    null_character[adjoint_labels] -= 1
    for row in product_irreps:
        labels = row['dynkin_labels']
        null_character[labels] = null_character.get(labels, 0)-row['multiplicity']
    if any(z < 0 for z in null_character.values()):
        raise ArithmeticError('g tensor I27000 character was negative')
    null_irreps = [{'dynkin_labels': labels, 'multiplicity': copies,
                    'dimension': dimension_by_labels[labels]}
                   for labels, copies in sorted(null_character.items()) if copies]
    null_dimension = sum(row['dimension']*row['multiplicity'] for row in null_irreps)
    product_checks = {'g_tensor_3875_dimension': product_dimension == 248*3875,
                      'g_tensor_I27000_dimension': null_dimension == 248*27000}
    return {'passed': all(row['passed'] for row in results.values()) and all(product_checks.values()),
            'Schur_components': results, 'distinct_adjoint_weights': len(adjoint),
            'dominant_weight_norm_bound': 18,
            'Freudenthal_recursion_states': len(engine.recursion_trace),
            'character_formulas': [
                'Sym^3 chi=(chi^3+3 chi psi2(chi)+2 psi3(chi))/6',
                'S21 chi=(chi^3-psi3(chi))/3',
                'exterior^3 chi=(chi^3-3 chi psi2(chi)+2 psi3(chi))/6'],
            'quadratic_tensor_checks': product_checks,
            'g_tensor_3875': {'irreducibles': product_irreps,
                              'dominant_weight_rows': product_rows,
                              'reconstructed_dimension': product_dimension},
            'g_tensor_I27000': {'irreducibles': null_irreps,
                                'reconstructed_dimension': null_dimension,
                                'identity': 'g tensor I=Sym^3(g)+S21(g)-g-g tensor3875'},
            'large_tensor_product_tables_imported': False}


def verify_voa_character_certificate(record):
    """Replay a JSON finite-character certificate against every dominant lattice weight."""
    if not isinstance(record, dict):
        raise ValueError('a finite-character certificate must be an object')
    degree = _integer(record.get('conformal_degree'), 'conformal degree', 0, 12)
    irreps = record.get('irreducibles')
    if not isinstance(irreps, list) or len(irreps) > 256:
        raise ValueError('irreducibles must be a bounded list')
    engine, parsed, seen = E8Freudenthal(degree), [], set()
    dimensions_match = True
    for row in irreps:
        if not isinstance(row, dict):
            raise ValueError('each irreducible must be an object')
        labels = _labels(row.get('dynkin_labels'))
        if labels in seen:
            raise ValueError('duplicate highest weights are not allowed')
        seen.add(labels)
        copies = _integer(row.get('multiplicity'), 'irreducible multiplicity', 1, 10**12)
        dimension = _integer(row.get('dimension'), 'irreducible dimension', 1, 10**15)
        highest = engine.root_coordinates(labels)
        if engine.norm(highest) > 2*degree:
            raise ValueError('irreducible highest weight exceeds the conformal norm bound')
        dimensions_match &= dimension == highest_weight_dimension(labels, engine.algebra)
        parsed.append((labels, copies, dimension))
    partitions = colored_partitions(8, degree)
    rows = []
    for labels, root, norm in engine.dominant_weights():
        reconstructed = sum(copies*engine.multiplicity(highest, root)
                            for highest, copies, _ in parsed)
        target = partitions[degree-norm//2]
        rows.append({'dynkin_labels': labels, 'reconstructed_weight_multiplicity': reconstructed,
                     'lattice_weight_multiplicity': target, 'equal': reconstructed == target})
    dimension = sum(copies*dim for _, copies, dim in parsed)
    expected = CurrentPopulations(degree).simple[degree]
    checks = {'Weyl_dimensions': bool(dimensions_match),
              'every_dominant_weight': all(row['equal'] for row in rows),
              'independent_scalar_dimension': dimension == expected}
    return {'passed': all(checks.values()), 'checks': checks,
            'conformal_degree': degree, 'dominant_weight_checks': rows,
            'reconstructed_dimension': dimension, 'independent_E4_eta_dimension': expected}


def _dimension_character(record):
    return {row['dimension']: row['multiplicity'] for row in record['irreducibles']}


def _finite_kernel_closure(arc_proof, characters, schur, short5, short6):
    from .asterion_kernel_characters import length_three_character, weight_five_arc_character
    arc5 = weight_five_arc_character()
    simple5 = _dimension_character(characters[5])
    kernel5 = {dimension: arc5.get(dimension, 0)-simple5.get(dimension, 0)
               for dimension in set(arc5) | set(simple5)}
    kernel5 = {d: m for d, m in sorted(kernel5.items()) if m}
    primitive5 = dict(kernel5)
    primitive5[3875] = primitive5.get(3875, 0)-1
    primitive5 = {d: m for d, m in primitive5.items() if m}
    arc6_three = length_three_character(3)
    simple6 = _dimension_character(characters[6])
    short6_character = {row['dimension']: row['exact_Gram_rank'] for row in short6['blocks']}
    remaining_target = {dimension: simple6.get(dimension, 0)-short6_character.get(dimension, 0)
                        for dimension in set(simple6) | set(short6_character)}
    forced6 = {dimension: max(0, copies-remaining_target.get(dimension, 0))
               for dimension, copies in arc6_three.items()}
    forced6 = {d: m for d, m in sorted(forced6.items()) if m}
    primitive6 = {dimension: max(0, copies-kernel5.get(dimension, 0))
                  for dimension, copies in forced6.items()}
    primitive6 = {d: m for d, m in primitive6.items() if m}
    dimension = lambda character: sum(d*m for d, m in character.items())
    populations = CurrentPopulations(6)
    traces = {1: 1, 248: -2}
    traces[3875] = populations.simple_twine[2]-traces[1]-traces[248]
    symmetric_trace = (traces[248]**2+traces[248])//2
    exterior_trace = (traces[248]**2-traces[248])//2
    traces[27000] = symmetric_trace-traces[1]-traces[3875]
    traces[30380] = exterior_trace-traces[248]
    traces[147250] = (populations.simple_twine[4]-2*traces[1]-3*traces[248]
                     -2*traces[3875]-traces[27000]-traces[30380])
    def graded(character):
        total = dimension(character)
        trace = sum(traces[d]*copies for d, copies in character.items())
        neutral, other = Q(total+124*trace, 125), Q(total-trace, 125)
        if neutral.denominator != 1 or other.denominator != 1 or min(neutral, other) < 0:
            raise ArithmeticError('Jordan Fourier projection did not give nonnegative integer dimensions')
        return {'total_dimension': total, 'each_nonidentity_automorphism_trace': trace,
                'neutral_grade_dimension': int(neutral),
                'each_of124_nonzero_grades_dimension': int(other)}
    checks = {'arc_polarization_character_proof': arc_proof['passed'],
              'independent_Schur_and_tensor_character_proof': schur['passed'],
              'simple_finite_characters': all(r['passed'] for r in characters),
              'short_current_weight5_injective': short5['passed'],
              'short_current_weight6_injective': short6['passed'],
              'weight5_character_difference_nonnegative': all(z > 0 for z in kernel5.values()),
              'weight5_entire_kernel_Li2': short5['injective_short_current_dimension'] == 96256,
              'weight5_kernel_character': kernel5 == {248:1,3875:1,147250:1},
              'weight5_primitive_character': primitive5 == {248:1,147250:1},
              'weight6_remaining_target_character_nonnegative': all(z >= 0 for z in remaining_target.values()),
              'weight6_length3_forced_kernel_character': forced6 == {248:1,3875:1,30380:1,147250:1},
              'weight6_forced_new_primitive_character': primitive6 == {30380:1},
              'Jordan_trace_derivation': traces == {1:1,248:-2,3875:0,27000:0,30380:5,147250:0}}
    return {'passed': all(checks.values()), 'checks': checks,
            'weight_five': {
                'arc_dimension': dimension(arc5), 'simple_dimension': dimension(simple5),
                'arc_finite_character': arc5, 'simple_finite_character': simple5,
                'kernel_finite_character': kernel5, 'kernel_dimension': dimension(kernel5),
                'entire_kernel_Li_degree': 2, 'ordinary_polynomial_degree': 3,
                'lower_weight_generated_character': {3875:1},
                'lower_weight_generated_dimension': 3875,
                'primitive_quotient_character': primitive5,
                'primitive_quotient_dimension': dimension(primitive5),
                'primitive_definition': 'K5/(D K4+g[0]K4), for the graded commutative differential ideal',
                'ordinary_current_products_zero': True,
                'Jordan_kernel_distribution': graded(kernel5),
                'Jordan_primitive_distribution': graded(primitive5)},
            'weight_six': {
                'length_three_arc_character': arc6_three,
                'length_three_arc_dimension': dimension(arc6_three),
                'Li_degree_of_length_three_piece': 3,
                'injective_short_current_character': short6_character,
                'injective_short_current_dimension': dimension(short6_character),
                'simple_dimension': dimension(simple6),
                'maximum_target_character_after_short_currents': remaining_target,
                'forced_length_three_kernel_submodule': forced6,
                'length_three_kernel_dimension_lower_bound': dimension(forced6),
                'known_translated_kernel_character': kernel5,
                'known_translated_kernel_dimension': dimension(kernel5),
                'forced_new_primitive_submodule': primitive6,
                'new_primitive_dimension_lower_bound': dimension(primitive6),
                'Jordan_forced_kernel_lower_bound': graded(forced6),
                'Jordan_forced_primitive_lower_bound': graded(primitive6),
                'full_kernel_or_primitive_character_claim': False,
                'proof': 'The entire short-current arc piece injects. Subtract its finite character '
                        'from the total simple character to bound every remaining target multiplicity. '
                        'The length-three arc character exceeds that bound by the displayed submodule. '
                        'Translations of K5 inject. Products of earlier kernel classes have ordinary '
                        'degree at least4 and cannot fill this ordinary-degree3 component.'},
            'all_weight_kernel_dimension_lower_bound_from_weight5': dimension(kernel5),
            'all_weight_kernel_lower_bound_starts_at': 5,
            'all_weight_Jordan_kernel_lower_bound_from_weight5': graded(kernel5),
            'all_weight_proof': 'D is injective on every positive ordinary-degree arc component '
                               'and commutes with the finite E8 and Jordan actions.',
            'Jordan_trace_derivation': {'finite_irrep_traces': traces,
                'simple_twining_weight2': populations.simple_twine[2],
                'simple_twining_weight4': populations.simple_twine[4],
                'identities': ['V2=1+g+3875', 'Sym^2(g)=1+3875+27000',
                               'exterior^2(g)=g+30380',
                               'V4=2+3g+2*3875+27000+30380+147250'],
                'conjugacy_input': 'All124 nonidentity F5^3 automorphisms are conjugate, as in the currents receipt.'},
            'full_infinite_differential_kernel_presentation_claim': False}


def kernel_tower_receipt(*, exhaustive=False):
    if not isinstance(exhaustive, bool):
        raise ValueError('exhaustive must be a Boolean')
    tower = translation_tower_receipt(4 if exhaustive else 2)
    syzygies = differential_annihilator_receipt(max_derivative=3 if exhaustive else 2)
    engine = E8Freudenthal(6)
    characters = [engine.voa_character(n) for n in range(7)]
    from .asterion_kernel_characters import kernel_characters_receipt
    arc_proof = kernel_characters_receipt(exhaustive=exhaustive)
    schur = tensor_cube_character_receipt()
    short5, short6 = short_current_injectivity_receipt(5), short_current_injectivity_receipt(6)
    closure = _finite_kernel_closure(arc_proof, characters, schur, short5, short6)
    return {'schema': 'perfectjet/asterion-kernel-tower/1',
            'translation_tower': tower, 'differential_annihilators': syzygies,
            'simple_finite_characters': characters,
            'tensor_cube_character_certificate': schur,
            'short_current_injection_certificates': {'5': short5, '6': short6},
            'arc_character_certificate': arc_proof,
            'finite_kernel_closure': closure,
            'Freudenthal_recursion_states': len(engine.recursion_trace),
            'passed': tower['passed'] and syzygies['passed'] and closure['passed'],
            'all_world_novelty_claim': False,
            'full_infinite_kernel_presentation_claim': False,
            'higher_arc_dimension_status': 'complete throughweight5; forced additionalV30380 primitive atweight6; fullweight6open'}
