"""Exact Asterion response bases and certified integral basis moves.

``Asterion`` names the deterministic prescription implemented here, not a new
isomorphism class of Lie algebra.  Starting from ordered seeds and ordered
adjoint probes, breadth-first commutator words are retained at their first
independent occurrence.  A primitive rational normalization fixes their scale.
The resulting basis carries its word provenance, exact inverse, determinant,
and independently replayable bracket transport.

Sparse vectors are mappings ``ambient_index -> rational``; dense sequences are
also accepted.  No floating equality, numerical rank, or third-party dependency
is used.  A bounded optimization result describes its declared pair workload;
it never claims global optimality or preservation of an integer lattice unless
the relevant arithmetic is actually checked.
"""
from __future__ import annotations

from collections import deque
from fractions import Fraction as Q
from itertools import combinations
from math import comb, gcd, lcm


def _rational(value):
    if isinstance(value, bool) or isinstance(value, float):
        raise ValueError("exact rational coefficients required")
    try:
        return Q(value)
    except (TypeError, ValueError, ZeroDivisionError) as exc:
        raise ValueError("exact rational coefficients required") from exc


def _dimension(value):
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError("positive integer dimension required")
    return value


def sparse(vector, dimension):
    """Validate and copy a sparse or dense exact vector."""
    dimension = _dimension(dimension)
    if hasattr(vector, 'items'):
        items = vector.items()
    else:
        vector = list(vector)
        if len(vector) != dimension:
            raise ValueError("vector dimension differs")
        items = enumerate(vector)
    out = {}
    for index, value in items:
        if isinstance(index, bool) or not isinstance(index, int) or not 0 <= index < dimension:
            raise ValueError("vector index outside the ambient space")
        value = _rational(value)
        if value:
            out[index] = value
    return out


def _add(left, right, scale=Q(1)):
    out = dict(left)
    for index, value in right.items():
        out[index] = out.get(index, Q(0)) + scale * value
        if not out[index]:
            del out[index]
    return out


def _scale(vector, scalar):
    return {i: scalar * x for i, x in vector.items() if scalar * x}


def _linear_combination(columns, coordinates):
    out = {}
    for j, scalar in coordinates.items():
        out = _add(out, columns[j], scalar)
    return out


def primitive(vector):
    """Return (primitive integer vector, exact multiplying factor).

    The first nonzero ambient coordinate is positive.  This fixes a rational
    line, not its index in an independently specified integer lattice.
    """
    if not vector:
        return {}, Q(1)
    denominator = lcm(*(x.denominator for x in vector.values()))
    common = 0
    for value in vector.values():
        common = gcd(common, abs(value.numerator * (denominator // value.denominator)))
    scale = Q(denominator, common)
    if vector[min(vector)] < 0:
        scale = -scale
    return _scale(vector, scale), scale


def _wire_vector(vector):
    return [[i, str(value)] for i, value in sorted(vector.items())]


def _unwire_vector(vector, dimension):
    if not isinstance(vector, list):
        raise ValueError("serialized sparse vector must be a list")
    out = {}
    for item in vector:
        if not isinstance(item, (list, tuple)) or len(item) != 2:
            raise ValueError("serialized vector entry must be an index/coefficient pair")
        i, x = item
        if i in out:
            raise ValueError("duplicate serialized vector index")
        out[i] = _rational(x)
    return sparse(out, dimension)


class _Span:
    """Sparse column elimination with representations in original columns."""
    def __init__(self):
        self.rows = []
        self.pivots = []
        self.representations = []
        self.pivot_values = []

    def reduce(self, vector):
        residual = dict(vector)
        coordinates = {}
        eliminations = []
        for j, (pivot, row, representation) in enumerate(zip(
                self.pivots, self.rows, self.representations)):
            coefficient = residual.get(pivot, Q(0))
            if coefficient:
                residual = _add(residual, row, -coefficient)
                coordinates = _add(coordinates, representation, coefficient)
                eliminations.append([j, str(coefficient)])
        return residual, coordinates, eliminations

    def add(self, vector):
        residual, coordinates, eliminations = self.reduce(vector)
        if not residual:
            return None, Q(0), eliminations
        pivot = min(residual)
        value = residual[pivot]
        column = len(self.rows)
        self.pivots.append(pivot)
        self.rows.append(_scale(residual, 1 / value))
        self.representations.append(_scale(_add({column: Q(1)}, coordinates, -1), 1 / value))
        self.pivot_values.append(value)
        return pivot, value, eliminations


class BasisCompilationError(ValueError):
    """A failed span request, including an exact annihilator witness."""
    def __init__(self, record):
        self.record = record
        self.witness = record.get('annihilator')
        super().__init__(f"Asterion compilation reached rank {record['rank']} of {record['dimension']}")


class AsterionBasis:
    """An ordered exact basis and its bidirectional coordinate transform."""
    def __init__(self, dimension, bracket, columns, *, labels=None,
                 provenance=None, inverse_rows=None):
        self.dimension = _dimension(dimension)
        if not callable(bracket):
            raise ValueError("bracket must be callable")
        self.ambient_bracket = bracket
        self.columns = tuple(sparse(v, dimension) for v in columns)
        if len(self.columns) != dimension:
            raise ValueError("a full basis must have exactly dimension columns")
        self.labels = tuple(labels or [f'A({j})' for j in range(dimension)])
        if len(self.labels) != dimension or len(set(self.labels)) != dimension:
            raise ValueError("basis labels must be distinct and match the dimension")
        self.provenance = dict(provenance or {})
        span = _Span()
        for column in self.columns:
            if span.add(column)[0] is None:
                raise ValueError("singular basis matrix")
        inversions = sum(p > q for j, p in enumerate(span.pivots) for q in span.pivots[j + 1:])
        self.determinant = Q((-1) ** inversions)
        for value in span.pivot_values:
            self.determinant *= value
        if inverse_rows is None:
            inverse = [{} for _ in range(dimension)]
            for ambient_index in range(dimension):
                residual, coordinates, _ = span.reduce({ambient_index: Q(1)})
                if residual:
                    raise ValueError("basis elimination failed to span the ambient space")
                for basis_index, value in coordinates.items():
                    inverse[basis_index][ambient_index] = value
            self.inverse_rows = tuple(inverse)
        else:
            self.inverse_rows = tuple(sparse(v, dimension) for v in inverse_rows)
            if len(self.inverse_rows) != dimension:
                raise ValueError("inverse row count differs")
            if not self.verify_inverse()['valid']:
                raise ValueError("supplied inverse does not invert the basis matrix")
        self.optimization = None

    def ambient(self, coordinates):
        return _linear_combination(self.columns, sparse(coordinates, self.dimension))

    def coordinates(self, vector):
        vector = sparse(vector, self.dimension)
        out = {}
        for j, row in enumerate(self.inverse_rows):
            # Skip absent coordinates rather than performing rational
            # multiplication by zero in every ambient dimension.
            value = 0
            for i, coefficient in row.items():
                if i in vector:
                    value += coefficient * vector[i]
            if value:
                out[j] = value
        return out

    def bracket(self, left, right):
        return self.coordinates(self.ambient_bracket(self.ambient(left), self.ambient(right)))

    def basis_bracket(self, left, right):
        return self.coordinates(self.ambient_bracket(self.columns[left], self.columns[right]))

    def verify_inverse(self):
        """Check both products on all unit columns, returning a failure witness."""
        for j in range(self.dimension):
            expected = {j: Q(1)}
            got = self.coordinates(self.columns[j])
            if got != expected:
                return {'valid': False, 'side': 'inverse_times_basis', 'column': j,
                        'expected': _wire_vector(expected), 'actual': _wire_vector(got)}
            got = self.ambient(self.coordinates(expected))
            if got != expected:
                return {'valid': False, 'side': 'basis_times_inverse', 'column': j,
                        'expected': _wire_vector(expected), 'actual': _wire_vector(got)}
        return {'valid': True, 'unit_columns_each_side': self.dimension}

    @property
    def integral(self):
        return all(x.denominator == 1 for column in self.columns for x in column.values())

    @property
    def unimodular(self):
        return self.integral and abs(self.determinant) == 1

    def shear(self, source, target, multiple):
        """Replace b_target by b_target + multiple*b_source.

        The elementary change is unimodular in the current basis even when
        that basis itself is only rational in ambient coordinates.
        """
        if (isinstance(source, bool) or isinstance(target, bool)
                or not isinstance(source, int) or not isinstance(target, int)
                or not 0 <= source < self.dimension or not 0 <= target < self.dimension
                or source == target):
            raise ValueError("distinct in-range source and target indices required")
        if isinstance(multiple, bool) or not isinstance(multiple, int):
            raise ValueError("integer shear multiple required")
        columns = list(self.columns)
        columns[target] = _add(columns[target], columns[source], Q(multiple))
        inverse = list(self.inverse_rows)
        inverse[source] = _add(inverse[source], inverse[target], Q(-multiple))
        provenance = dict(self.provenance)
        provenance['unimodular_moves'] = list(provenance.get('unimodular_moves', [])) + [
            {'source': source, 'target': target, 'multiple': multiple}]
        return AsterionBasis(self.dimension, self.ambient_bracket, columns,
                             labels=self.labels, provenance=provenance, inverse_rows=inverse)

    def record(self, *, pairs=None):
        record = {'schema': 'perfectjet/asterion-basis/1', 'name': 'Asterion response basis',
                  'dimension': self.dimension, 'labels': list(self.labels),
                  'columns': [_wire_vector(v) for v in self.columns],
                  'inverse_rows': [_wire_vector(v) for v in self.inverse_rows],
                  'determinant': str(self.determinant), 'integral_columns': self.integral,
                  'same_integer_lattice': self.unimodular, 'provenance': self.provenance,
                  'scope': 'Exact rational coordinates; integer-lattice equality means an integral unimodular ambient matrix.'}
        if pairs is not None:
            pairs = _pairs(self.dimension, pairs)
            record['bracket_images'] = [{'left': i, 'right': j,
                'coordinates': _wire_vector(self.basis_bracket(i, j))} for i, j in pairs]
            record['bracket_coverage'] = {'pairs': len(pairs),
                'full_unordered_pairs': len(pairs) == comb(self.dimension, 2)
                    and set(pairs) == set(combinations(range(self.dimension), 2))}
        if self.optimization is not None:
            record['optimization'] = self.optimization
        return record

    @classmethod
    def from_record(cls, bracket, record):
        if not isinstance(record, dict) or record.get('schema') != 'perfectjet/asterion-basis/1':
            raise ValueError("unsupported Asterion basis schema")
        n = _dimension(record['dimension'])
        basis = cls(n, bracket, [_unwire_vector(v, n) for v in record['columns']],
                    labels=record['labels'], provenance=record.get('provenance'),
                    inverse_rows=[_unwire_vector(v, n) for v in record['inverse_rows']])
        if str(basis.determinant) != record.get('determinant'):
            raise ValueError("recorded determinant differs")
        if basis.integral != record.get('integral_columns') or basis.unimodular != record.get('same_integer_lattice'):
            raise ValueError("recorded lattice claim differs")
        return basis


def _pairs(dimension, pairs):
    out = []
    seen = set()
    for pair in pairs:
        if not isinstance(pair, (list, tuple)) or len(pair) != 2:
            raise ValueError("each workload pair must contain two indices")
        i, j = pair
        if (isinstance(i, bool) or isinstance(j, bool) or not isinstance(i, int)
                or not isinstance(j, int) or not 0 <= i < dimension or not 0 <= j < dimension
                or i >= j or (i, j) in seen):
            raise ValueError("workload pairs must be distinct and satisfy 0 <= i < j < dimension")
        seen.add((i, j))
        out.append((i, j))
    return out


def compile_basis(dimension, bracket, seeds, probes=None, *, seed_labels=None,
                  probe_labels=None, max_depth=64, max_candidates=100000):
    """Compile the first independent breadth-first adjoint response words.

    The probes are fixed ambient vectors, acting as ``v -> [probe, v]``.  If
    omitted, the ordered seeds themselves are used as probes.  Dependent words
    need not be expanded: linearity makes their children combinations of the
    children of previously accepted words.  Failure includes an annihilator
    and reports whether the final span is invariant under every probe.
    """
    n = _dimension(dimension)
    if (isinstance(max_depth, bool) or not isinstance(max_depth, int) or max_depth < 0
            or isinstance(max_candidates, bool) or not isinstance(max_candidates, int)
            or max_candidates < 1):
        raise ValueError("nonnegative depth and positive candidate limits required")
    seeds = [sparse(v, n) for v in seeds]
    probes = [sparse(v, n) for v in (seeds if probes is None else probes)]
    seed_labels = list(seed_labels or [f's{j}' for j in range(len(seeds))])
    probe_labels = list(probe_labels or [f'p{j}' for j in range(len(probes))])
    if len(seed_labels) != len(seeds) or len(probe_labels) != len(probes):
        raise ValueError("seed/probe label counts differ")
    span = _Span()
    queue = deque((j, (), seed) for j, seed in enumerate(seeds))
    columns, words, history = [], [], []
    while queue and len(columns) < n and len(history) < max_candidates:
        seed_index, word, candidate = queue.popleft()
        candidate = sparse(candidate, n)
        column, factor = primitive(candidate)
        pivot, value, eliminations = span.add(column)
        step = {'seed': seed_index, 'word': list(word), 'accepted': pivot is not None,
                'normalization_factor': str(factor), 'pivot': pivot,
                'pivot_value': str(value), 'eliminations': eliminations}
        history.append(step)
        if pivot is None:
            continue
        columns.append(column)
        words.append({'seed': seed_index, 'word': list(word), 'normalization_factor': str(factor)})
        if len(word) < max_depth:
            for probe_index, probe in enumerate(probes):
                queue.append((seed_index, word + (probe_index,), sparse(bracket(probe, candidate), n)))
    provenance = {'prescription': 'breadth-first independent adjoint words; primitive first-positive normalization',
                  'seed_labels': seed_labels, 'probe_labels': probe_labels,
                  'seeds': [_wire_vector(v) for v in seeds], 'probes': [_wire_vector(v) for v in probes],
                  'basis_words': words, 'elimination_history': history,
                  'max_depth': max_depth, 'max_candidates': max_candidates,
                  'unimodular_moves': []}
    if len(columns) != n:
        from .exact import nullspace
        annihilators = nullspace([[v.get(i, Q(0)) for i in range(n)] for v in columns], n)
        invariant = all(not span.reduce(sparse(bracket(p, v), n))[0] for p in probes for v in columns)
        outside_seeds = [j for j, seed in enumerate(seeds) if span.reduce(seed)[0]]
        raise BasisCompilationError({'schema': 'perfectjet/asterion-compilation-failure/1',
            'dimension': n, 'rank': len(columns), 'candidate_count': len(history),
            'annihilator': _wire_vector(sparse(annihilators[0], n)),
            'probe_invariant_span': invariant,
            'all_seeds_in_span': not outside_seeds,
            'seed_indices_outside_span': outside_seeds,
            'all_future_obstruction': invariant and not outside_seeds,
            'stop_reason': 'candidate_limit' if len(history) >= max_candidates else 'depth_or_closure',
            'scope': 'Annihilator vanishes on the compiled span; all-future claim requires probe invariance and inclusion of every original seed.',
            'provenance': provenance})
    labels = [f'A({seed_labels[w["seed"]]};' + ','.join(probe_labels[j] for j in w['word']) + ')'
              for w in words]
    return AsterionBasis(n, bracket, columns, labels=labels, provenance=provenance)


def verify_certificate(bracket, record):
    """Independently replay inverse, words, elementary moves and stored brackets."""
    try:
        basis = AsterionBasis.from_record(bracket, record)
        provenance = record.get('provenance', {})
        checked_words = 0
        if 'basis_words' in provenance:
            n = basis.dimension
            seeds = [_unwire_vector(v, n) for v in provenance['seeds']]
            probes = [_unwire_vector(v, n) for v in provenance['probes']]
            columns = []
            for word in provenance['basis_words']:
                seed_index = word['seed']
                if isinstance(seed_index, bool) or not isinstance(seed_index, int) or not 0 <= seed_index < len(seeds):
                    raise ValueError("invalid provenance seed index")
                vector = seeds[seed_index]
                for index in word['word']:
                    if isinstance(index, bool) or not isinstance(index, int) or not 0 <= index < len(probes):
                        raise ValueError("invalid provenance probe index")
                    vector = sparse(bracket(probes[index], vector), n)
                normalized, factor = primitive(vector)
                if factor != _rational(word['normalization_factor']):
                    raise ValueError("word normalization factor differs")
                columns.append(normalized)
                checked_words += 1
            if len(columns) != n:
                raise ValueError("provenance word count differs")
            # Replay the selection transcript, including the rejected words.
            # This checks that the retained words really are the first
            # independent responses under the declared breadth-first order.
            span = _Span()
            queue = deque((j, (), seed) for j, seed in enumerate(seeds))
            replay_words = []
            max_depth = provenance['max_depth']
            max_candidates = provenance['max_candidates']
            history = provenance['elimination_history']
            if (isinstance(max_depth, bool) or not isinstance(max_depth, int) or max_depth < 0
                    or isinstance(max_candidates, bool) or not isinstance(max_candidates, int)
                    or max_candidates < 1 or len(history) > max_candidates):
                raise ValueError("invalid provenance search limits")
            for recorded_step in history:
                if not queue or len(replay_words) == n:
                    raise ValueError("selection transcript continues after termination")
                seed_index, word, candidate = queue.popleft()
                column, factor = primitive(candidate)
                pivot, value, eliminations = span.add(column)
                step = {'seed': seed_index, 'word': list(word), 'accepted': pivot is not None,
                        'normalization_factor': str(factor), 'pivot': pivot,
                        'pivot_value': str(value), 'eliminations': eliminations}
                if step != recorded_step:
                    raise ValueError("sparse elimination transcript differs")
                if pivot is not None:
                    replay_words.append({'seed': seed_index, 'word': list(word),
                                         'normalization_factor': str(factor)})
                    if len(word) < max_depth:
                        for probe_index, probe in enumerate(probes):
                            queue.append((seed_index, word + (probe_index,),
                                          sparse(bracket(probe, candidate), n)))
            if replay_words != provenance['basis_words']:
                raise ValueError("selection transcript does not establish the recorded basis")
            replay = AsterionBasis(n, bracket, columns, labels=basis.labels)
            for move in provenance.get('unimodular_moves', []):
                replay = replay.shear(move['source'], move['target'], move['multiple'])
            if replay.columns != basis.columns:
                raise ValueError("word/move replay differs from basis columns")
        checked_pairs = 0
        pair_records = record.get('bracket_images', [])
        _pairs(basis.dimension, [(row['left'], row['right']) for row in pair_records])
        for row in pair_records:
            actual = basis.basis_bracket(row['left'], row['right'])
            if actual != _unwire_vector(row['coordinates'], basis.dimension):
                return {'valid': False, 'failure': 'bracket_transport',
                        'left': row['left'], 'right': row['right'], 'actual': _wire_vector(actual)}
            checked_pairs += 1
        if 'bracket_coverage' in record:
            pairs = [(row['left'], row['right']) for row in pair_records]
            expected_coverage = {'pairs': len(pairs),
                'full_unordered_pairs': len(pairs) == comb(basis.dimension, 2)
                    and set(pairs) == set(combinations(range(basis.dimension), 2))}
            if record['bracket_coverage'] != expected_coverage:
                raise ValueError("recorded bracket coverage differs")
        optimization_verified = None
        if 'optimization' in record:
            optimization = record['optimization']
            input_basis = AsterionBasis(basis.dimension, bracket,
                [_unwire_vector(v, basis.dimension) for v in optimization['input_columns']],
                labels=basis.labels)
            optimized = optimize_basis(input_basis,
                moves=optimization['declared_moves'], multiples=optimization['multiples'],
                rounds=optimization['requested_rounds'], max_trials=optimization['max_trials'],
                pairs=optimization['workload_pairs'], max_pairs=optimization['max_pairs'])
            if optimized.optimization != optimization or optimized.columns != basis.columns:
                raise ValueError("optimization search/cost replay differs")
            optimization_verified = True
        return {'valid': True, 'inverse_unit_columns_each_side': basis.dimension,
                'word_columns': checked_words, 'bracket_pairs': checked_pairs,
                'optimization_replayed': optimization_verified,
                'scope': 'Stored bracket pairs and any optimization report replayed exactly; inverse equality holds on the full ambient space.'}
    except (ValueError, TypeError, KeyError, IndexError) as exc:
        return {'valid': False, 'failure': 'invalid_certificate', 'reason': str(exc)}


def tensor_cost(basis, *, pairs=None, max_pairs=4096):
    """Actual output support and coefficient height on a declared pair workload."""
    n = basis.dimension
    if pairs is None:
        if comb(n, 2) > max_pairs:
            raise ValueError("declare a bounded pair workload or increase max_pairs for a full tensor")
        pairs = list(combinations(range(n), 2))
    else:
        pairs = _pairs(n, pairs)
        if len(pairs) > max_pairs:
            raise ValueError("pair workload exceeds max_pairs")
    support = total_bits = max_bits = nonzero_pairs = 0
    for i, j in pairs:
        values = basis.basis_bracket(i, j)
        support += len(values)
        nonzero_pairs += bool(values)
        for value in values.values():
            bits = abs(value.numerator).bit_length() + value.denominator.bit_length()
            total_bits += bits
            max_bits = max(max_bits, bits)
    full = len(pairs) == comb(n, 2) and set(pairs) == set(combinations(range(n), 2))
    return {'objective': [support, max_bits, total_bits], 'output_terms': support,
            'max_coefficient_height_bits': max_bits, 'total_coefficient_height_bits': total_bits,
            'nonzero_input_pairs': nonzero_pairs, 'pair_count': len(pairs),
            'full_unordered_tensor': full,
            'input_workload': 'Pairs of current basis indices, not fixed ambient input vectors.',
            'height_definition': 'bit_length(abs(numerator)) + bit_length(denominator)',
            'objective_order': 'lexicographic: output terms, maximum height, total height'}


def optimize_basis(basis, *, moves=None, multiples=(-1, 1), rounds=1,
                   max_trials=256, pairs=None, max_pairs=4096):
    """Deterministic strict-descent search over integer elementary shears.

    This searches only the supplied moves/multiples and declared workload.
    Each accepted move has determinant one and a recorded exact inverse move.
    """
    if (isinstance(rounds, bool) or not isinstance(rounds, int) or rounds < 0
            or isinstance(max_trials, bool) or not isinstance(max_trials, int) or max_trials < 1):
        raise ValueError("nonnegative rounds and positive trial limit required")
    n = basis.dimension
    workload = list(combinations(range(n), 2)) if pairs is None else _pairs(n, pairs)
    if len(workload) > max_pairs:
        raise ValueError("declare a bounded pair workload or increase max_pairs")
    if moves is None:
        moves = [(i, j) for i in range(n) for j in range(n) if i != j]
    moves = list(moves)
    for source, target in moves:
        if (isinstance(source, bool) or isinstance(target, bool)
                or not isinstance(source, int) or not isinstance(target, int)
                or not 0 <= source < n or not 0 <= target < n or source == target):
            raise ValueError("invalid elementary move")
    multiples = tuple(multiples)
    if any(isinstance(k, bool) or not isinstance(k, int) or not k for k in multiples):
        raise ValueError("nonzero integer shear multiples required")
    current = AsterionBasis(n, basis.ambient_bracket, basis.columns,
        labels=basis.labels, provenance=basis.provenance, inverse_rows=basis.inverse_rows)
    initial = tensor_cost(current, pairs=workload, max_pairs=max_pairs)
    cost = initial
    trials = 0
    accepted = []
    completed_rounds = 0
    exhausted = False
    for round_index in range(rounds):
        best = None
        for source, target in moves:
            for multiple in multiples:
                if trials >= max_trials:
                    exhausted = True
                    break
                candidate = current.shear(source, target, multiple)
                candidate_cost = tensor_cost(candidate, pairs=workload, max_pairs=max_pairs)
                trials += 1
                key = tuple(candidate_cost['objective'])
                if key < tuple(cost['objective']) and (best is None or key < best[0]):
                    best = (key, candidate, candidate_cost, source, target, multiple)
            if exhausted:
                break
        if best is None:
            break
        _, current, next_cost, source, target, multiple = best
        accepted.append({'source': source, 'target': target, 'multiple': multiple,
                         'inverse_multiple': -multiple,
                         'before': cost['objective'], 'after': next_cost['objective']})
        cost = next_cost
        completed_rounds = round_index + 1
        if exhausted:
            break
    current.optimization = {'schema': 'perfectjet/asterion-shear-search/1',
        'initial': initial, 'final': cost, 'trials': trials, 'accepted_moves': accepted,
        'completed_improving_rounds': completed_rounds, 'trial_limit_reached': exhausted,
        'declared_move_count': len(moves), 'declared_moves': [list(move) for move in moves],
        'multiples': list(multiples), 'requested_rounds': rounds,
        'max_trials': max_trials, 'max_pairs': max_pairs,
        'workload_pairs': [list(pair) for pair in workload],
        'input_columns': [_wire_vector(v) for v in basis.columns],
        'integer_lattice_preserved_relative_to_input': True,
        'global_optimality_claimed': False,
        'scope': 'Exact strict descent on the declared pair workload and finite elementary-move search.'}
    return current


def verify_jacobi(dimension, bracket, *, triples=None, max_triples=100000):
    """Check alternation, skew symmetry and Jacobi on all or declared triples.

    Skew symmetry is checked on every basis pair.  In characteristic zero,
    Jacobi with repeated indices follows from skew symmetry, so increasing
    triples suffice for a full basis certificate.
    """
    n = _dimension(dimension)
    units = [{i: Q(1)} for i in range(n)]
    table = {}
    for i in range(n):
        if sparse(bracket(units[i], units[i]), n):
            return {'valid': False, 'failure': 'alternation', 'indices': [i, i]}
        for j in range(i + 1, n):
            left = sparse(bracket(units[i], units[j]), n)
            right = sparse(bracket(units[j], units[i]), n)
            if _add(left, right):
                return {'valid': False, 'failure': 'skew_symmetry', 'indices': [i, j]}
            table[i, j] = left
    if triples is None:
        if comb(n, 3) > max_triples:
            raise ValueError("declare bounded triples or increase max_triples")
        triples = list(combinations(range(n), 3))
        full = True
    else:
        triples = list(triples)
        if len(triples) > max_triples or len(set(map(tuple, triples))) != len(triples):
            raise ValueError("triple workload exceeds limit or contains duplicates")
        if any(len(t) != 3 or any(isinstance(i, bool) or not isinstance(i, int) for i in t)
               or not 0 <= t[0] < t[1] < t[2] < n for t in triples):
            raise ValueError("triples must satisfy 0 <= i < j < k < dimension")
        full = len(triples) == comb(n, 3)
    for count, (i, j, k) in enumerate(triples, 1):
        result = sparse(bracket(units[i], table[j, k]), n)
        result = _add(result, sparse(bracket(units[j], _scale(table[i, k], -1)), n))
        result = _add(result, sparse(bracket(units[k], table[i, j]), n))
        if result:
            return {'valid': False, 'failure': 'jacobi', 'indices': [i, j, k],
                    'residual': _wire_vector(result), 'triples_checked': count}
    return {'valid': True, 'alternation_checks': n, 'skew_pair_checks': comb(n, 2),
            'jacobi_triples': len(triples), 'full_basis_jacobi': full,
            'scope': 'Exact characteristic-zero replay; repeated-index Jacobi follows from verified skew symmetry.'}


def _sl2_bracket(left, right):
    # Ambient order h,e,f.  This small model is also an independent test fixture.
    result = {}
    table = {(0, 1): {1: Q(2)}, (0, 2): {2: Q(-2)}, (1, 2): {0: Q(1)}}
    for i, a in left.items():
        for j, b in right.items():
            if i < j:
                result = _add(result, table[i, j], a * b)
            elif j < i:
                result = _add(result, table[j, i], -a * b)
    return result


def basis_receipt():
    """A full independent three-dimensional demonstration of the machinery."""
    compiled = compile_basis(3, _sl2_bracket, [{1: 1, 2: 1}], [{1: 1}, {2: 1}],
                             seed_labels=['e+f'], probe_labels=['e', 'f'])
    pairs = list(combinations(range(3), 2))
    certificate = compiled.record(pairs=pairs)
    canonical = AsterionBasis(3, _sl2_bracket, [{0: 1}, {1: 1}, {2: 1}])
    deliberately_sheared = canonical.shear(1, 0, 1)
    optimized = optimize_basis(deliberately_sheared, rounds=2, max_trials=48)
    return {'schema': 'perfectjet/asterion-response-receipt/1',
            'name': 'Asterion basis calculus', 'compiled': certificate,
            'certificate_replay': verify_certificate(_sl2_bracket, certificate),
            'jacobi': verify_jacobi(3, compiled.bracket),
            'optimization': optimized.optimization,
            'optimized_inverse': optimized.verify_inverse(),
            'scope': 'Full sl2 demonstration; generic compiler and shear search also accept the E8 sparse bracket.'}


def e8_response_basis(algebra=None):
    """Construct the prescribed mixed, integral Asterion basis for E8.

    The eight seeds are e_i+f_i.  The sixteen ordered probes are e_1,...,e_8,
    f_1,...,f_8.  Breadth-first independence and primitive normalization are
    fixed by :func:`compile_basis`; no random seed or numerical tolerance is
    involved.  The determinant is computed from the resulting actual vectors.
    """
    if algebra is None:
        from .asterion_e8 import E8LieAlgebra
        algebra = E8LieAlgebra()
    seeds = [_add(algebra.simple_e(i), algebra.simple_f(i)) for i in range(8)]
    probes = [algebra.simple_e(i) for i in range(8)] + [algebra.simple_f(i) for i in range(8)]
    return compile_basis(248, algebra.bracket, seeds, probes,
        seed_labels=[f'e{i + 1}+f{i + 1}' for i in range(8)],
        probe_labels=[f'e{i + 1}' for i in range(8)] + [f'f{i + 1}' for i in range(8)],
        max_depth=64)


def e8_response_receipt(*, exhaustive=False, include_basis=False, algebra=None):
    """Replay the actual 248-dimensional compiled basis with explicit scope.

    Default bracket coverage is a deterministic 92-pair panel. ``exhaustive``
    expands this to all 30,628 unordered basis pairs.  Full inverse equality
    and every selection/word step are verified in both modes.
    """
    import hashlib
    import json
    basis = e8_response_basis(algebra)
    pairs = (list(combinations(range(248), 2)) if exhaustive else
             [(i, j) for i in range(8) for j in range(i + 1, 16)])
    record = basis.record(pairs=pairs)
    replay = verify_certificate(basis.ambient_bracket, record)
    digest = lambda data: hashlib.sha256(json.dumps(data, sort_keys=True,
        separators=(',', ':')).encode()).hexdigest()
    out = {'schema': 'perfectjet/asterion-e8-response/1',
        'basis_name': 'Asterion response basis', 'dimension': 248,
        'seed_count': 8, 'probe_count': 16,
        'basis_vectors': len(basis.columns),
        'basis_matrix_nonzero_entries': sum(map(len, basis.columns)),
        'inverse_matrix_nonzero_entries': sum(map(len, basis.inverse_rows)),
        'candidate_words_examined': len(basis.provenance['elimination_history']),
        'maximum_selected_word_depth': max(len(w['word']) for w in basis.provenance['basis_words']),
        'determinant': str(basis.determinant),
        'integral_columns': basis.integral,
        'same_chevalley_integer_lattice': basis.unimodular,
        'basis_matrix_sha256': digest(record['columns']),
        'inverse_matrix_sha256': digest(record['inverse_rows']),
        'selection_transcript_sha256': digest(basis.provenance),
        'certificate_replay': replay,
        'tensor_cost': tensor_cost(basis, pairs=pairs, max_pairs=comb(248, 2)),
        'passed': replay['valid'] and basis.unimodular,
        'scope': 'A prescribed mixed basis of the supplied E8 algebra; classical algebra, exact implementation, no priority claim.'}
    if exhaustive:
        reference = AsterionBasis(248, basis.ambient_bracket,
                                 [{i: Q(1)} for i in range(248)])
        baseline = tensor_cost(reference, max_pairs=comb(248, 2))
        current = out['tensor_cost']
        difference = current['output_terms'] - baseline['output_terms']
        out['chevalley_comparison'] = {
            'baseline': 'supplied Chevalley Cartan/root basis',
            'baseline_tensor_cost': baseline,
            'output_term_ratio': str(Q(current['output_terms'], baseline['output_terms'])),
            'output_term_difference': difference,
            'nonzero_input_pair_difference': current['nonzero_input_pairs'] - baseline['nonzero_input_pairs'],
            'asterion_is_denser': difference > 0,
            'sparsity_advantage_established': difference < 0,
            'finding': ('The Asterion response basis is denser; no sparsity advantage is established.'
                if difference > 0 else 'The Asterion response basis has the same output support.'
                if difference == 0 else 'The Asterion response basis has fewer output terms on this full tensor.'),
            'scope': 'Exact full unordered bracket tensors in their respective basis coordinates; no runtime advantage follows from this comparison.'}
    if include_basis:
        out['certificate'] = record
    return out
