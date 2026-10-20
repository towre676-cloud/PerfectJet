"""Exact E8 quartic characters and a multiplicity-forced kernel bound.

The finite character calculations use only the241 adjoint weights, exact
Newton identities, Weyl dimensions, and Freudenthal recursion.  In
particular no Sym^4(g) or Sym^2(3875) tensor-product table is imported.

For W=1+3875 inside Sym^2(g), multiplication Sym^2(W)->Sym^4(g)
has a kernel containing1+3875: both types have multiplicity2 in the source
and multiplicity1 in the target.  Identifying the weight6/factorlength4 arc
piece with the dual of that kernel is a separate theorem in the quartic
module.  Neither this character bound nor that identification proves all
the remaining multiplication blocks have maximal rank.
"""
from __future__ import annotations

from collections import Counter
from fractions import Fraction as Q

from .asterion_kernel_tower import E8Freudenthal
from .asterion_relations import highest_weight_dimension
from .asterion_currents import colored_partitions


class _QuarticFreudenthal(E8Freudenthal):
    """Fixed norm32 specialization for four adjoint factors, not a VOA cutoff.

    The base public VOA character API is deliberately left unchanged.  The
    recursion itself is norm-acyclic and works at this explicit fixed bound.
    Four vectors of squared norm at most2 have sum norm at most32.
    """
    def __init__(self):
        super().__init__(12)
        self.max_norm = 32


def _plus(a, b):
    return tuple(x+y for x, y in zip(a, b))


def _minus(a, b, scale=1):
    return tuple(x-scale*y for x, y in zip(a, b))


def _adams_coefficient(character, weight, power):
    if any(x % power for x in weight):
        return 0
    return character.get(tuple(x//power for x in weight), 0)


def _decompose(engine, weights, multiplicities, expected_dimension):
    decomposition, rows = [], []
    for labels, root, norm in weights:
        actual = multiplicities[root]
        prior = sum(copies*engine.multiplicity(highest, root)
                    for highest, copies in decomposition)
        copies = actual-prior
        if copies < 0:
            raise ArithmeticError('negative finite irreducible multiplicity')
        if copies:
            decomposition.append((labels, copies))
        rows.append({'dynkin_labels': labels, 'root_coordinates': root,
                     'squared_norm': norm, 'Schur_weight_multiplicity': actual,
                     'higher_irrep_contribution': prior,
                     'highest_irrep_multiplicity': copies})
    irreps = [{'dynkin_labels': labels, 'multiplicity': copies,
               'dimension': highest_weight_dimension(labels, engine.algebra)}
              for labels, copies in decomposition]
    total = sum(row['dimension']*row['multiplicity'] for row in irreps)
    return {'passed': total == expected_dimension, 'irreducibles': irreps,
            'dominant_weight_rows': rows, 'reconstructed_dimension': total,
            'independent_symmetric_power_dimension': expected_dimension}


def _integer(value, name, low, high):
    if isinstance(value, bool) or not isinstance(value, int) or not low <= value <= high:
        raise ValueError(f'{name} must be an integer in {low}..{high}')
    return value


def verify_quartic_character_certificate(record):
    """Check serialized irreducibles against all exact Newton weight rows.

    This deliberately recomputes the small complete character calculation;
    a stored ``passed`` field and stored dimensions cannot grant acceptance.
    """
    if not isinstance(record, dict):
        raise ValueError('a quartic character certificate must be an object')
    actual = quartic_characters_receipt()
    checks = {}
    for name in ('Sym2_3875', 'Sym2_W', 'Sym4_g'):
        candidate = record.get(name)
        if not isinstance(candidate, dict) or not isinstance(candidate.get('irreducibles'), list):
            raise ValueError(f'{name} must contain an irreducibles list')
        if len(candidate['irreducibles']) > 128:
            raise ValueError('irreducible list exceeds128 entries')
        parsed, seen = {}, set()
        for row in candidate['irreducibles']:
            if not isinstance(row, dict):
                raise ValueError('each irreducible must be an object')
            labels = row.get('dynkin_labels')
            if (not isinstance(labels, (list, tuple)) or len(labels) != 8
                    or any(isinstance(x, bool) or not isinstance(x, int) or x < 0 for x in labels)):
                raise ValueError('eight nonnegative integer highest-weight labels are required')
            labels = tuple(labels)
            if labels in seen:
                raise ValueError('duplicate highest weights are not allowed')
            seen.add(labels)
            copies = _integer(row.get('multiplicity'), 'multiplicity', 1, 10**12)
            dimension = _integer(row.get('dimension'), 'dimension', 1, 10**15)
            parsed[labels] = copies, dimension
        expected = {tuple(row['dynkin_labels']): (row['multiplicity'], row['dimension'])
                    for row in actual[name]['irreducibles']}
        checks[name] = parsed == expected
    return {'passed': actual['passed'] and all(checks.values()), 'checks': checks,
            'stored_passed_field_trusted': False}


def quartic_characters_receipt(*, exhaustive=False):
    """Replay exact complete finite characters; exhaustive adds recursion rows.

    The flag never asserts an exact multiplication kernel or an exact
    weight6 arc dimension.  Both requested modes prove the same characters.
    """
    if not isinstance(exhaustive, bool):
        raise ValueError('exhaustive must be a Boolean')
    engine = _QuarticFreudenthal()
    zero = (0,)*8
    adjoint = {zero: 8, **{root: 1 for root in engine.algebra.roots}}
    square = {}
    for a, m in adjoint.items():
        for b, n in adjoint.items():
            root = _plus(a, b)
            square[root] = square.get(root, 0)+m*n
    # V2=1+g+3875 and m_V2(mu)=p8(2-||mu||²/2).  The squared-root
    # support already contains all norm4 lattice weights:2160, the E4 shell.
    p8 = colored_partitions(8, 2)
    finite3875 = {}
    support_shell_counts = Counter()
    for root in square:
        norm = engine.norm(root)
        if norm <= 4:
            value = p8[2-norm//2]-adjoint.get(root, 0)-(root == zero)
            if value:
                finite3875[root] = value
                support_shell_counts[norm] += 1
    finite_character_dependency = E8Freudenthal(2).voa_character(2)
    weights16 = engine.dominant_weights(16)
    symmetric3875, symmetricW = {}, {}
    for _, root, _ in weights16:
        product_coefficient = sum(m*finite3875.get(_minus(root, a), 0)
                                  for a, m in finite3875.items())
        value = Q(product_coefficient+_adams_coefficient(finite3875, root, 2), 2)
        if value.denominator != 1 or value < 0:
            raise ArithmeticError('symmetric square weight coefficient must be a nonnegative integer')
        symmetric3875[root] = value.numerator
        symmetricW[root] = value.numerator+finite3875.get(root, 0)+(root == zero)
    result3875 = _decompose(engine, weights16, symmetric3875, 3875*3876//2)
    resultW = _decompose(engine, weights16, symmetricW, 3876*3877//2)
    weights32 = engine.dominant_weights(32)
    symmetric4, newton_rows = {}, []
    for labels, root, norm in weights32:
        chi4 = sum(m*square.get(_minus(root, a), 0) for a, m in square.items())
        chi2psi2 = sum(m*square.get(_minus(root, a, 2), 0) for a, m in adjoint.items())
        psi2square = _adams_coefficient(square, root, 2)
        chipsi3 = sum(m*adjoint.get(_minus(root, a, 3), 0) for a, m in adjoint.items())
        psi4 = _adams_coefficient(adjoint, root, 4)
        numerator = chi4+6*chi2psi2+3*psi2square+8*chipsi3+6*psi4
        value = Q(numerator, 24)
        if value.denominator != 1 or value < 0:
            raise ArithmeticError('symmetric fourth weight coefficient must be a nonnegative integer')
        symmetric4[root] = value.numerator
        newton_rows.append({'dynkin_labels': labels, 'squared_norm': norm,
                            'chi4': chi4, 'chi2_psi2': chi2psi2,
                            'psi2_squared': psi2square, 'chi_psi3': chipsi3,
                            'psi4': psi4, 'numerator': numerator,
                            'Sym4_weight_multiplicity': value.numerator})
    result4 = _decompose(engine, weights32, symmetric4, 248*249*250*251//24)
    by_dimension = lambda result: {row['dimension']: row['multiplicity']
                                   for row in result['irreducibles']}
    source, target = by_dimension(resultW), by_dimension(result4)
    forced = {dimension: max(0, copies-target.get(dimension, 0))
              for dimension, copies in source.items()}
    forced = {d: m for d, m in sorted(forced.items()) if m}
    forced_dimension = sum(d*m for d, m in forced.items())
    expected_source = {1:2,3875:2,27000:1,147250:1,2450240:1,4881384:1}
    expected_target = {1:1,3875:1,27000:2,147250:1,2450240:1,
                       4096000:1,4881384:1,70680000:1,79143000:1}
    checks = {'degree2_lattice_character_dependency': finite_character_dependency['passed'],
              'complete_3875_weight_support': dict(support_shell_counts) == {0:1,2:240,4:2160},
              '3875_weight_dimension': sum(finite3875.values()) == 3875,
              'adjoint_square_weight_dimension': sum(square.values()) == 248**2,
              'Sym2_3875_dimension': result3875['passed'],
              'Sym2_W_dimension': resultW['passed'],
              'Sym4_g_dimension': result4['passed'],
              'source_character': source == expected_source,
              'target_character': target == expected_target,
              'forced_kernel_character': forced == {1:1,3875:1},
              'forced_kernel_dimension': forced_dimension == 3876}
    result = {'schema': 'perfectjet/asterion-quartic-characters/1',
              'passed': all(checks.values()), 'checks': checks,
              'Sym2_3875': result3875, 'Sym2_W': resultW, 'Sym4_g': result4,
              'weight_input': {'distinct_adjoint_weights': len(adjoint),
                               'adjoint_zero_weight_multiplicity': adjoint[zero],
                               'distinct_adjoint_square_weights': len(square),
                               'distinct_3875_weights': len(finite3875),
                               '3875_support_shell_counts': dict(support_shell_counts),
                               '3875_multiplicity_by_squared_norm': {0:35,2:7,4:1},
                               'complete_norm4_shell_dimension_from_E4': 240*(1+2**3)},
              'norm_bounds': {'Sym2_3875': 16, 'Sym2_W': 16, 'Sym4_g': 32,
                              'proof': 'Cauchy-Schwarz: a sum of r weights of norm at most L has squared norm at most r²L.'},
              'Sym4_Newton_weight_rows': newton_rows,
              'Newton_formulas': [
                  'Sym2(chi)=(chi²+psi2(chi))/2',
                  'Sym4(chi)=(chi⁴+6chi²psi2(chi)+3psi2(chi)²+8chi psi3(chi)+6psi4(chi))/24'],
              'Freudenthal_recursion_states': len(engine.recursion_trace),
              'finite_character_dependency_weight2': finite_character_dependency,
              'multiplication_map': 'mu:Sym²(W)->Sym⁴(g), W=1+3875 inside Sym²(g)',
              'forced_multiplication_kernel_character': forced,
              'forced_multiplication_kernel_dimension_lower_bound': forced_dimension,
              'quartic_arc_dimension_lower_bound': forced_dimension,
              'quartic_arc_identification_dependency':
                  'The factorlength4, jetdegree2 arc component is dual to ker(mu); '
                  'this separate polarization/S4 theorem must be supplied by asterion_quartic.',
              'kernel_bound_proof': 'An E8-equivariant map has rank at most the target multiplicity '
                                    'on each irreducible isotypic component. Both1 and3875 have '
                                    'source multiplicity2 and target multiplicity1.',
              'exact_full_quartic_kernel_claim': False,
              'all_other_multiplication_blocks_maximal_rank_claim': False,
              'explicit_quartic_VOA_null_vector_claim': False,
              'complete_weight6_arc_kernel_claim': False,
              'complete_infinite_kernel_claim': False,
              'all_world_novelty_claim': False,
              'large_tensor_product_tables_imported': False}
    if exhaustive:
        result['Freudenthal_recursion_trace'] = [
            {'highest_root_coordinates': highest, 'weight_root_coordinates': weight,
             **record} for (highest, weight), record in sorted(engine.recursion_trace.items())]
    return result
