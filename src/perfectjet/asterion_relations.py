"""Sparse affine-vacuum PBW arithmetic and a weight-four E8 relation search.

Creation words are tuples ``((mode,index),...)`` representing the negative
currents ``x_index[-mode]`` acting on the vacuum.  The PBW order is decreasing
positive mode followed by increasing basis index.  All coefficients are exact
rationals.  The implementation is weight bounded and never constructs a dense
31,000-variable cochain matrix.

The relation ledger distinguishes an exact affine-form calculation from the
representation-theoretic interpretation of the arc map.  No full kernel or
unrestricted Groebner basis claim is made.
"""
from __future__ import annotations

from collections import defaultdict
from fractions import Fraction as Q
from functools import lru_cache
import hashlib
from itertools import permutations
import json
from math import factorial, gcd, lcm

from .asterion_e8 import E8LieAlgebra
from .exact import nullspace, rref


ZERO_WEIGHT = (0,)*8
OMEGA_3875 = (4, 7, 10, 8, 6, 4, 2, 5)
SONG_ZENG = "https://arxiv.org/pdf/2606.14407#page=24"


def _add(out, vector, scalar=1):
    for key, z in vector.items():
        value = out.get(key, Q(0))+scalar*z
        if value:
            out[key] = value
        else:
            out.pop(key, None)
    return out


def _primitive(vector):
    if not vector:
        return {}
    scale = lcm(*(Q(z).denominator for z in vector.values()))
    integers = {k: int(z*scale) for k, z in vector.items()}
    divisor = gcd(*(abs(z) for z in integers.values()))
    sign = 1 if integers[min(integers)] > 0 else -1
    return {k: Q(sign*z//divisor) for k, z in sorted(integers.items())}


def _json(value):
    if isinstance(value, Q):
        return value.numerator if value.denominator == 1 else str(value)
    if isinstance(value, dict):
        return {str(k): _json(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [_json(v) for v in value]
    return value


class AffinePBW:
    """Exact bounded induced affine vacuum module at a rational level.

    The mode relation is [x[m],y[n]]=[x,y][m+n]+m*k*B(x,y)*delta_(m+n,0).
    The invariant form has B(h_i,h_j)=A_ij and B(e_alpha,e_-alpha)=1.
    Words of conformal weight greater than ``maximum_weight`` are rejected.
    """
    def __init__(self, level=1, maximum_weight=4, algebra=None):
        if (isinstance(maximum_weight, bool) or not isinstance(maximum_weight, int)
                or not 1 <= maximum_weight <= 6):
            raise ValueError("maximum_weight must be an integer in 1..6")
        self.algebra = algebra or E8LieAlgebra()
        self.level = Q(level)
        self.maximum_weight = maximum_weight
        self.weights = {i: ZERO_WEIGHT if i < 8 else self.algebra.index_root[i]
                        for i in range(248)}
        augmented = [list(map(Q, row))+[Q(i == j) for j in range(8)]
                     for i, row in enumerate(self.algebra.cartan_matrix)]
        inverse, _ = rref(augmented)
        self.cartan_inverse = tuple(tuple(row[8:]) for row in inverse)
        self.opposite = {i: i if i < 8 else self.algebra.root_index[
            tuple(-a for a in self.weights[i])] for i in range(248)}
        self.tau_sign = self._opposition_signs()
        self._pair_casimir_cache = {}
        self._normal = lru_cache(maxsize=250000)(self._normal_uncached)
        self._action = lru_cache(maxsize=250000)(self._action_uncached)

    def _opposition_signs(self):
        signs = {i: Q(1) for i in range(8)}
        positives = [r for r in self.algebra.roots if sum(r) > 0]
        for alpha in positives:
            index = self.algebra.root_index[alpha]
            if sum(alpha) == 1:
                sign = Q(1)
            else:
                chosen = None
                for i, simple in enumerate(self.algebra.simple_roots):
                    beta = tuple(a-b for a, b in zip(alpha, simple))
                    if beta in self.algebra.root_index and sum(beta) > 0:
                        chosen = i, beta
                        break
                if chosen is None:
                    raise ArithmeticError("positive root has no simple predecessor")
                i, beta = chosen
                e = next(iter(self.algebra.simple_e(i)))
                b = self.algebra.root_index[beta]
                c = self.algebra.basis_bracket(e, b)[index]
                negative = self.algebra.basis_bracket(self.opposite[b], self.opposite[e])
                sign = signs[b]*negative[self.opposite[index]]/c
            signs[index] = signs[self.opposite[index]] = sign
        return signs

    def validate_word(self, word):
        if not isinstance(word, (tuple, list)):
            raise ValueError("a creation word must be a tuple or list")
        result = []
        for entry in word:
            if (not isinstance(entry, (tuple, list)) or len(entry) != 2
                    or any(isinstance(x, bool) or not isinstance(x, int) for x in entry)):
                raise ValueError("word entries must be integer (positive mode,basis index) pairs")
            mode, index = entry
            if mode < 1 or not 0 <= index < 248:
                raise ValueError("creation modes must be positive and indices in 0..247")
            result.append((mode, index))
        word = tuple(result)
        if sum(n for n, _ in word) > self.maximum_weight:
            raise ValueError("creation word exceeds the configured conformal weight")
        return word

    @staticmethod
    def _order(entry):
        return -entry[0], entry[1]

    def normalize(self, word):
        return dict(self._normal(self.validate_word(word)))

    def _normal_uncached(self, word):
        inversion = next((i for i in range(len(word)-1)
                          if self._order(word[i]) > self._order(word[i+1])), None)
        if inversion is None:
            return ((word, Q(1)),)
        i = inversion
        (m, a), (n, b) = word[i:i+2]
        swapped = word[:i]+(word[i+1], word[i])+word[i+2:]
        out = dict(self._normal(swapped))
        for c, value in self.algebra.basis_bracket(a, b).items():
            contracted = word[:i]+((m+n, c),)+word[i+2:]
            _add(out, dict(self._normal(contracted)), value)
        return tuple(sorted(out.items()))

    def invariant_form(self, i, j):
        if i < 8 and j < 8:
            return Q(self.algebra.cartan_matrix[i][j])
        return Q(1) if i >= 8 and self.opposite[i] == j else Q(0)

    def act(self, index, mode, state):
        if (isinstance(index, bool) or not isinstance(index, int) or not 0 <= index < 248
                or isinstance(mode, bool) or not isinstance(mode, int)):
            raise ValueError("current action requires an integer index and mode")
        out = {}
        for word, coefficient in state.items():
            word = self.validate_word(word)
            if mode < 0 and sum(n for n, _ in word)-mode > self.maximum_weight:
                raise ValueError("current action exceeds the configured conformal weight")
            _add(out, dict(self._action(index, mode, word)), Q(coefficient))
        return out

    def _prepend(self, entry, state):
        out = {}
        for word, z in state.items():
            _add(out, dict(self._normal((entry,)+word)), z)
        return out

    def _action_uncached(self, index, mode, word):
        if mode < 0:
            return self._normal(((-mode, index),)+word)
        if not word:
            return ()
        (n, b), tail = word[0], word[1:]
        out = self._prepend((n, b), dict(self._action(index, mode, tail)))
        for c, value in self.algebra.basis_bracket(index, b).items():
            _add(out, dict(self._action(c, mode-n, tail)), value)
        if mode == n:
            central = mode*self.level*self.invariant_form(index, b)
            if central:
                _add(out, {tail: Q(1)}, central)
        return tuple(sorted(out.items()))

    def pairing_word(self, left, state):
        """Contravariant affine vacuum pairing, normalized by <1,1>=1."""
        left = self.validate_word(left)
        current = state
        scalar = Q(1)
        for n, index in left:
            current = self.act(self.opposite[index], n, current)
            scalar *= self.tau_sign[index]
            if not current:
                return Q(0)
        return scalar*current.get((), Q(0))

    def pairing(self, left, right):
        return sum((Q(z)*self.pairing_word(word, right)
                    for word, z in left.items()), Q(0))

    def symmetrize(self, factors):
        factors = self.validate_word(factors)
        out = {}
        for word in permutations(factors):
            _add(out, self.normalize(word), Q(1, factorial(len(factors))))
        return out

    def root_weight(self, word):
        return tuple(sum(self.weights[i][j] for _, i in word) for j in range(8))

    def leading_li_symbol(self, state):
        if not state:
            return {"differential_degree": None, "polynomial": {}}
        weight_set = {sum(n for n, _ in word) for word, z in state.items() if z}
        if len(weight_set) != 1:
            raise ValueError("a Li symbol requires one homogeneous conformal weight")
        weight = next(iter(weight_set))
        length = max(len(word) for word, z in state.items() if z)
        polynomial = {}
        for word, z in state.items():
            if len(word) == length and z:
                monomial = tuple(sorted((i, n-1) for n, i in word))
                _add(polynomial, {monomial: Q(z)})
        return {"differential_degree": weight-length,
                "polynomial": polynomial}

    def derivative(self, state):
        out = {}
        for word, z in state.items():
            for j, (n, i) in enumerate(word):
                changed = word[:j]+((n+1, i),)+word[j+1:]
                _add(out, self.normalize(changed), n*Q(z))
        return out

    def highest_quadratic_3875(self):
        pairs = [(i, j) for i in range(248) for j in range(i, 248)
                 if tuple(a+b for a, b in zip(self.weights[i], self.weights[j])) == OMEGA_3875]
        rows = {}
        for column, (i, j) in enumerate(pairs):
            for node in range(8):
                e = next(iter(self.algebra.simple_e(node)))
                for x, y in ((i, j), (j, i)):
                    for a, z in self.algebra.basis_bracket(e, x).items():
                        key = node, tuple(sorted((a, y)))
                        rows.setdefault(key, [Q(0)]*len(pairs))[column] += z
        kernel = nullspace(list(rows.values()), len(pairs))
        if len(kernel) != 1:
            raise ArithmeticError("the requested highest quadratic must be unique")
        return _primitive({pair: z for pair, z in zip(pairs, kernel[0]) if z})

    def quadratic_jet_tensor(self, quadratic):
        """F_Q=sum_a ad(t_a)(Q) times the first jet of the dual t^a."""
        out = {}
        for (i, j), coefficient in quadratic.items():
            for a in range(248):
                dual = ({b: self.cartan_inverse[a][b] for b in range(8)
                         if self.cartan_inverse[a][b]} if a < 8
                        else {self.opposite[a]: Q(1)})
                for x, y in ((i, j), (j, i)):
                    for v, z in self.algebra.basis_bracket(a, x).items():
                        for d, w in dual.items():
                            monomial = tuple(sorted(((v, 0), (y, 0), (d, 1))))
                            _add(out, {monomial: coefficient*z*w})
        return out

    def lift_jet_polynomial(self, polynomial):
        out = {}
        for monomial, coefficient in polynomial.items():
            _add(out, self.symmetrize(tuple((r+1, i) for i, r in monomial)), coefficient)
        return out

    def weight_four_candidates(self):
        quadratic = self.highest_quadratic_3875()
        jet = self.quadratic_jet_tensor(quadratic)
        cubic = self.lift_jet_polynomial(jet)
        q31, q22 = {}, {}
        for (i, j), coefficient in quadratic.items():
            _add(q31, self.symmetrize(((3, i), (1, j))), coefficient)
            _add(q31, self.symmetrize(((3, j), (1, i))), coefficient)
            _add(q22, self.symmetrize(((2, i), (2, j))), coefficient)
        return quadratic, jet, (cubic, q31, q22)

    def finite_highest_checks(self, state):
        return [not self.act(next(iter(self.algebra.simple_e(i))), 0, state)
                for i in range(8)]

    def mode_commutator_check(self, a, m, b, n, state):
        left = self.act(a, m, self.act(b, n, state))
        _add(left, self.act(b, n, self.act(a, m, state)), -1)
        right = {}
        for c, z in self.algebra.basis_bracket(a, b).items():
            _add(right, self.act(c, m+n, state), z)
        if m+n == 0:
            _add(right, state, m*self.level*self.invariant_form(a, b))
        return left == right

    def singular_square(self):
        theta = self.algebra.root_index[self.algebra.roots[-1]]
        return {((1, theta), (1, theta)): Q(1)}

    def weight_four_sector(self, target=OMEGA_3875, limit=20000):
        """Enumerate a single root-weight PBW sector, with a strict size bound."""
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 100000:
            raise ValueError("sector limit must be an integer in 1..100000")
        pairs = defaultdict(list)
        for i in range(248):
            for j in range(i, 248):
                pairs[tuple(a+b for a, b in zip(self.weights[i], self.weights[j]))].append((i, j))
        out = []

        def emit(word):
            out.append(word)
            if len(out) > limit:
                raise ValueError("weight sector exceeds the declared monomial limit")

        for weight, left in pairs.items():
            right = pairs.get(tuple(a-b for a, b in zip(target, weight)), ())
            for i, j in left:
                for k, l in right:
                    if j <= k:
                        emit(((1, i), (1, j), (1, k), (1, l)))
        for d in range(248):
            rest = tuple(a-b for a, b in zip(target, self.weights[d]))
            for i, j in pairs.get(rest, ()):
                emit(((2, d), (1, i), (1, j)))
        for i, j in pairs.get(target, ()):
            emit(((2, i), (2, j)))
            emit(((3, i), (1, j)))
            if i != j:
                emit(((3, j), (1, i)))
        for i in range(248):
            if self.weights[i] == target:
                emit(((4, i),))
        return tuple(out)

    def _classical_target_sector(self, symmetric_three=False):
        pairs = defaultdict(list)
        for i in range(248):
            for j in range(i, 248):
                pairs[tuple(a+b for a, b in zip(self.weights[i], self.weights[j]))].append((i, j))
        columns = []
        for d in range(248):
            rest = tuple(a-b for a, b in zip(OMEGA_3875, self.weights[d]))
            for i, j in pairs.get(rest, ()):
                if not symmetric_three or j <= d:
                    columns.append((i, j, d))
        return columns

    def omega_pair(self, i, j):
        """The split Casimir Omega=sum ad(t_a) tensor ad(t^a) on Sym²g."""
        key = tuple(sorted((i, j)))
        if key in self._pair_casimir_cache:
            return self._pair_casimir_cache[key].copy()
        out = {}
        for a in range(248):
            dual = ({b: self.cartan_inverse[a][b] for b in range(8)
                     if self.cartan_inverse[a][b]} if a < 8
                    else {self.opposite[a]: Q(1)})
            first = self.algebra.basis_bracket(a, i)
            if not first:
                continue
            for b, coefficient in dual.items():
                second = self.algebra.basis_bracket(b, j)
                for x, z in first.items():
                    for y, w in second.items():
                        _add(out, {tuple(sorted((x, y))): coefficient*z*w})
        self._pair_casimir_cache[key] = out.copy()
        return out

    def classical_highest_constraints(self, symmetric_three=False):
        """Exact sparse rows excluding highest weight3875 from old sources.

        For Sym³g the rows are the eight simple raising operators.  For
        Sym²g tensor g they additionally impose (Omega_12-2)v=0.  The
        zero-mode module generated by e_theta² is inside that eigenspace,
        since Omega commutes with g and Omega(e_theta²)=2e_theta².
        """
        columns = self._classical_target_sector(symmetric_three)
        rows = {}
        cache = {}
        for column, (i, j, d) in enumerate(columns):
            for node in range(8):
                e = next(iter(self.algebra.simple_e(node)))
                for position, x in enumerate((i, j, d)):
                    for y, coefficient in self.algebra.basis_bracket(e, x).items():
                        changed = [i, j, d]
                        changed[position] = y
                        monomial = (tuple(sorted(changed)) if symmetric_three
                                    else (*sorted(changed[:2]), changed[2]))
                        row = rows.setdefault(("raising", node, monomial), {})
                        _add(row, {column: coefficient})
            if not symmetric_three:
                if (i, j) not in cache:
                    cache[i, j] = self.omega_pair(i, j)
                omega = dict(cache[i, j])
                _add(omega, {(i, j): Q(1)}, -2)
                for (a, b), coefficient in omega.items():
                    row = rows.setdefault(("casimir", (a, b, d)), {})
                    _add(row, {column: coefficient})
        ordered = [(key, row) for key, row in sorted(rows.items()) if row]
        return columns, ordered


def _modular_full_column_certificate(columns, tagged_rows, prime=1009):
    """One full-rank reduction modulo a prime certifies rational injectivity."""
    if prime != 1009:
        raise ValueError("the replay protocol fixes the proven prime1009")
    encoded = []
    for tag, row in tagged_rows:
        if any(Q(z).denominator != 1 for z in row.values()):
            raise ArithmeticError("the integral highest-weight matrix acquired denominators")
        encoded.append([tag, [[j, int(z)] for j, z in sorted(row.items())]])
    digest = hashlib.sha256(json.dumps(encoded, separators=(',', ':')).encode()).hexdigest()
    basis, selected, pivots, pivot_values = {}, [], [], []
    for number, (_, source) in enumerate(tagged_rows):
        row = {j: int(z) % prime for j, z in source.items() if int(z) % prime}
        while row:
            pivot = min(row)
            if pivot not in basis:
                value = row[pivot]
                inverse = pow(value, prime-2, prime)
                basis[pivot] = {j: z*inverse % prime for j, z in row.items()}
                selected.append(number)
                pivots.append(pivot)
                pivot_values.append(value)
                break
            coefficient = row[pivot]
            for j, z in basis[pivot].items():
                value = (row.get(j, 0)-coefficient*z) % prime
                if value:
                    row[j] = value
                else:
                    row.pop(j, None)
        if len(basis) == len(columns):
            break
    return {"field_prime": prime, "columns": len(columns),
            "rows": len(tagged_rows), "rank_mod_prime": len(basis),
            "full_column_rank": len(basis) == len(columns),
            "integral_matrix_sha256": digest,
            "selected_original_rows": selected, "pivot_columns": pivots,
            "nonzero_pivot_values": pivot_values,
            "rational_implication": "full column rank modulo1009 implies zero rational kernel; "
                                    "this is an exact rank certificate, not a probability estimate"}


def arc_nonmembership_certificate(module=None):
    """Certify that the3875 highest component cannot come from old arc relations."""
    module = module or AffinePBW()
    sym_columns, sym_rows = module.classical_highest_constraints(True)
    mixed_columns, mixed_rows = module.classical_highest_constraints(False)
    symmetric = _modular_full_column_certificate(sym_columns, sym_rows)
    old_quadratic = _modular_full_column_certificate(mixed_columns, mixed_rows)
    theta = module.algebra.root_index[module.algebra.roots[-1]]
    singular_omega = module.omega_pair(theta, theta) == {(theta, theta): Q(2)}
    return {"symmetric_cubic_source": symmetric,
            "quadratic_null_module_tensor_current_source": old_quadratic,
            "singular_square_omega_eigenvalue_two_checked": singular_omega,
            "passed": symmetric['full_column_rank'] and old_quadratic['full_column_rank']
                      and singular_omega,
            "argument": "Both old differential-relation source modules have no highest "
                        "vector of finite weight omega3875. Their equivariant images "
                        "g*dI, I*dg and dJ3 (J3 subset Sym3g) therefore contain no3875. "
                        "The nonzero highest tensor F_Q of that weight survives the arc quotient.",
            "scope": "One irreducible highest-weight component; no full arc-kernel classification."}


def jet_derivative(polynomial):
    """Differentiate divided jets x^[r]=D^r(x)/r!, with D x^[r]=(r+1)x^[r+1]."""
    out = {}
    for monomial, z in polynomial.items():
        for position, (i, r) in enumerate(monomial):
            changed = list(monomial)
            changed[position] = i, r+1
            _add(out, {tuple(sorted(changed)): Q(z)*(r+1)})
    return out


def _cubic_derivative_tensor(polynomial):
    """Polarize degree3 to Sym²g tensor g; multiplication sends delta(p) to3p."""
    out = {}
    for monomial, z in polynomial.items():
        for position, d in enumerate(monomial):
            i, j = monomial[:position]+monomial[position+1:]
            _add(out, {(i, j, d): Q(z)})
    return out


def _multiply_tensor(tensor):
    out = {}
    for (i, j, d), z in tensor.items():
        _add(out, {tuple(sorted((i, j, d))): Q(z)})
    return out


def _omega_tensor(module, tensor):
    out = {}
    for (i, j, d), z in tensor.items():
        for (a, b), coefficient in module.omega_pair(i, j).items():
            _add(out, {(a, b, d): z*coefficient})
    return out


def _project_null_pair(module, tensor):
    """Project the first Sym² factor to I27000 using its exact Casimir polynomial."""
    first = _omega_tensor(module, tensor)
    second = _omega_tensor(module, first)
    _add(second, first, 72)
    _add(second, tensor, 720)
    return {k: z/Q(868) for k, z in second.items() if z}


def _symmetric_raising(module, polynomial, node):
    e = next(iter(module.algebra.simple_e(node)))
    out = {}
    for monomial, z in polynomial.items():
        for position, x in enumerate(monomial):
            for y, coefficient in module.algebra.basis_bracket(e, x).items():
                changed = list(monomial)
                changed[position] = y
                _add(out, {tuple(sorted(changed)): z*coefficient})
    return out


def _highest_cubic(module, dynkin_labels):
    target = tuple(sum(module.cartan_inverse[i][j]*dynkin_labels[j]
                       for j in range(8)) for i in range(8))
    pairs = defaultdict(list)
    for i in range(248):
        for j in range(i, 248):
            pairs[tuple(a+b for a, b in zip(module.weights[i], module.weights[j]))].append((i, j))
    columns = []
    for d in range(248):
        rest = tuple(a-b for a, b in zip(target, module.weights[d]))
        for i, j in pairs.get(rest, ()):
            if j <= d:
                columns.append((i, j, d))
    if len(columns) > 1000:
        raise ValueError("highest-cubic search exceeds its1000-column bound")
    rows = {}
    for column, monomial in enumerate(columns):
        for node in range(8):
            for changed, z in _symmetric_raising(module, {monomial: Q(1)}, node).items():
                rows.setdefault((node, changed), [Q(0)]*len(columns))[column] += z
    kernel = nullspace(list(rows.values()), len(columns))
    if len(kernel) != 1:
        raise ArithmeticError("highest-cubic sector does not have a unique primitive vector")
    return _primitive({monomial: z for monomial, z in zip(columns, kernel[0]) if z}), len(columns)


def _casimir_quadratic(module):
    out = {}
    for a in range(248):
        dual = ({b: module.cartan_inverse[a][b] for b in range(8)
                 if module.cartan_inverse[a][b]} if a < 8 else {module.opposite[a]: Q(1)})
        for b, z in dual.items():
            _add(out, {tuple(sorted((a, b))): z})
    return out


def _casimir_value(module, dynkin_labels):
    root_coordinates = [sum(module.cartan_inverse[i][j]*dynkin_labels[j]
                            for j in range(8)) for i in range(8)]
    return sum(a*b for a, b in zip(root_coordinates, dynkin_labels))+2*sum(root_coordinates)


def _lattice_voa_prefix(order=4):
    """Recompute theta_E8=E4 divided by the eight-boson Euler product."""
    partitions = [1]+[0]*order
    for mode in range(1, order+1):
        for _ in range(8):
            for n in range(mode, order+1):
                partitions[n] += partitions[n-mode]
    theta = [1]+[240*sum(d**3 for d in range(1, n+1) if n % d == 0)
                 for n in range(1, order+1)]
    return [sum(theta[i]*partitions[n-i] for i in range(n+1)) for n in range(order+1)]


def weight_four_completeness_receipt(module=None):
    """Exact projected-polarization proof of the complete weight-four kernel.

    Four explicit highest cubics have Weyl dimensions summing to dim Sym³g.
    Their projected polarization scalars simultaneously prove I*g=Sym³g
    and identify the kernel of delta to (Sym²g/I) tensor g.  This closes
    conformal weight4 only; higher-weight differential generators remain open.
    """
    module = module or AffinePBW()
    if module.level != 1:
        raise ValueError("weight-four completeness is a level-one statement")
    theta = module.algebra.root_index[module.algebra.roots[-1]]
    quadratic = module.highest_quadratic_3875()
    casimir = _casimir_quadratic(module)
    cubic248 = {tuple(sorted((*pair, theta))): z for pair, z in casimir.items()}
    cubic30380, search_columns = _highest_cubic(module, (0,0,0,0,0,1,0,0))
    cubic779247 = {tuple(sorted((*pair, theta))): z for pair, z in quadratic.items()}
    cubic1763125 = {(theta, theta, theta): Q(1)}
    cases = [((0,0,0,0,0,0,1,0), cubic248),
             ((0,0,0,0,0,1,0,0), cubic30380),
             ((1,0,0,0,0,0,1,0), cubic779247),
             ((0,0,0,0,0,0,3,0), cubic1763125)]
    # Ground the quadratic projector by exhibiting all three highest modules.
    quadratic_cases = [((0,)*8, casimir, -60),
                       ((1,0,0,0,0,0,0,0), quadratic, -12),
                       ((0,0,0,0,0,0,2,0), {(theta, theta): Q(1)}, 2)]
    quadratic_records = []
    for labels, polynomial, eigenvalue in quadratic_cases:
        image = {}
        for (i, j), z in polynomial.items():
            _add(image, module.omega_pair(i, j), z)
        target = tuple(sum(module.cartan_inverse[i][j]*labels[j] for j in range(8)) for i in range(8))
        quadratic_records.append({
            'dynkin_labels': labels, 'dimension': highest_weight_dimension(labels, module.algebra),
            'omega_eigenvalue': eigenvalue,
            'omega_eigenvector_checked': image == {k: z*eigenvalue for k, z in polynomial.items()},
            'highest_checked': all(not _symmetric_raising(module, polynomial, node) for node in range(8)),
            'root_weight_checked': all(tuple(sum(module.weights[i][r] for i in monomial)
                                             for r in range(8)) == target for monomial in polynomial)})
    records = []
    for labels, polynomial in cases:
        delta = _cubic_derivative_tensor(polynomial)
        in_null_pair = _project_null_pair(module, delta)
        image = _multiply_tensor(in_null_pair)
        pivot = min(polynomial)
        scalar = image.get(pivot, Q(0))/polynomial[pivot]
        quotient_delta = dict(delta)
        _add(quotient_delta, in_null_pair, -1)
        quotient_image = _multiply_tensor(quotient_delta)
        target = tuple(sum(module.cartan_inverse[i][j]*labels[j] for j in range(8)) for i in range(8))
        records.append({
            'dynkin_labels': labels,
            'dimension': highest_weight_dimension(labels, module.algebra),
            'quadratic_casimir': _json(_casimir_value(module, labels)),
            'highest_vector_terms': len(polynomial),
            'highest_vector': [{'monomial': key, 'coefficient': _json(z)}
                               for key, z in sorted(polynomial.items())],
            'all_eight_raising_operators_zero': all(
                not _symmetric_raising(module, polynomial, node) for node in range(8)),
            'root_weight_checked': all(tuple(sum(module.weights[i][r] for i in monomial)
                                             for r in range(8)) == target for monomial in polynomial),
            'null_pair_projected_polarization_terms': len(in_null_pair),
            'mu_P_I_delta_scalar': _json(scalar),
            'mu_P_I_delta_identity_checked': image == {k: z*scalar for k, z in polynomial.items() if z*scalar},
            'mu_P_W_delta_scalar': _json(3-scalar),
            'mu_P_W_delta_identity_checked': quotient_image == {
                k: z*(3-scalar) for k, z in polynomial.items() if z*(3-scalar)},
            'P_W_delta_is_zero': not quotient_delta})
    n = 248
    sym2, sym3 = n*(n+1)//2, n*(n+1)*(n+2)//6
    null2 = quadratic_records[-1]['dimension']
    quotient2 = sym2-null2
    delta_kernel = records[-1]['dimension']
    delta_rank = sym3-delta_kernel
    mixed = quotient2*n-delta_rank
    li2 = n*n+sym2-null2
    arc4 = mixed+li2+n
    actual = _lattice_voa_prefix()
    # The grading of a finite irreducible E8 module is independent of its
    # realization.  Extract3875 from simple weight2 =1+3875+Dg, rather than
    # pretending that a Chevalley-to-Jordan transport of783 terms was run.
    from .asterion_currents import CurrentPopulations
    populations = CurrentPopulations(2)
    neutral = populations.graded_dimension(2, (0,0,0))
    nonzero = populations.graded_dimension(2, (1,0,0))
    current_neutral = populations.graded_dimension(1, (0,0,0))
    current_nonzero = populations.graded_dimension(1, (1,0,0))
    kernel_neutral = neutral-current_neutral-1
    kernel_nonzero = nonzero-current_nonzero
    checks = {
        'quadratic_highest_modules_exhaust_Sym2': sum(r['dimension'] for r in quadratic_records) == sym2,
        'quadratic_projector_spectrum_checked': all(r['highest_checked'] and r['root_weight_checked'] and r['omega_eigenvector_checked'] for r in quadratic_records),
        'cubic_highest_modules_exhaust_Sym3': sum(r['dimension'] for r in records) == sym3,
        'cubic_highest_vectors_checked': all(r['all_eight_raising_operators_zero'] and r['root_weight_checked'] for r in records),
        'I_times_g_onto_Sym3': all(Q(r['mu_P_I_delta_scalar']) and r['mu_P_I_delta_identity_checked'] for r in records),
        'projected_delta_injective_on_first_three_modules': all(
            Q(r['mu_P_W_delta_scalar']) and r['mu_P_W_delta_identity_checked'] for r in records[:3]),
        'projected_delta_zero_on_V3theta': records[-1]['P_W_delta_is_zero'],
        'weight2_affine_null_space_dimension_equals_I': sym2+n-actual[2] == null2,
        'arc_simple_weight4_difference_is_3875': arc4-actual[4] == 3875,
        'graded_3875_is_31_regular_Jordan_modules': kernel_neutral == kernel_nonzero == 31
                                                   and kernel_neutral+124*kernel_nonzero == 3875,
    }
    return _json({
        'schema': 'perfectjet/asterion-projected-polarization/1',
        'method': 'projected polarization certificate',
        'quadratic_projector': 'P_I=(Omega+12)(Omega+60)/868; P_W=1-P_I',
        'quadratic_highest_modules': quadratic_records,
        'cubic_highest_modules': records,
        '30380_highest_search_columns': search_columns,
        'Sym2_dimension': sym2, 'Sym3_dimension': sym3,
        'ordinary_C2_degree3_quotient_dimension': 0,
        'projected_delta_kernel_dimension': delta_kernel,
        'projected_delta_image_dimension': delta_rank,
        'mixed_weight4_arc_dimension': mixed,
        'Li_degree2_weight4_dimension': li2,
        'Li_degree3_weight4_dimension': n,
        'arc_character_through_weight4': [1,n,quotient2+n,n*n-null2+n,arc4],
        'simple_character_through_weight4': actual,
        'weight4_arc_kernel_dimension': arc4-actual[4],
        'weight4_arc_kernel_module': 'V_(1,0,0,0,0,0,0,0), dimension3875',
        'graded_kernel_per_sector': 31, 'graded_kernel_sector_count': 125,
        'graded_kernel_Li_differential_degree': 1,
        'graded_kernel_derivation': {
            'simple_weight2_neutral': neutral, 'simple_weight2_each_nonzero': nonzero,
            'Dg_neutral': current_neutral, 'Dg_each_nonzero': current_nonzero,
            'invariant_quadratic_neutral': 1, 'kernel_neutral': kernel_neutral,
            'kernel_each_nonzero': kernel_nonzero,
            'identity': 'V3875 restricted to F5^3 is31 copies of its125-dimensional regular representation',
            'proof_dependency': 'CurrentPopulations level-one twining/Fourier-projection theorem; '
                                'weight2=1+V3875+Dg and finite E8-module identification',
            'explicit_generator_transported_to_Jordan_coordinates': False,
        },
        'old_relation_redundancy': 'g*D(I) is contained in I*D(g)+D(Sym3g), by D(x*i)=Dx*i+x*Di',
        'checks': checks, 'passed': all(checks.values()),
        'proof_scope': 'Complete conformal-weight4 arc kernel once combined with the explicit nonzero F_Q generator and affine null lift; higher conformal weights are not classified.',
        'infinite_differential_kernel_claim': False,
    })


def highest_weight_dimension(dynkin_labels, algebra=None):
    """Exact Weyl dimension formula in this repository's E8 node ordering."""
    if (not isinstance(dynkin_labels, (tuple, list)) or len(dynkin_labels) != 8
            or any(isinstance(x, bool) or not isinstance(x, int) or x < 0
                   for x in dynkin_labels)):
        raise ValueError("eight nonnegative integer Dynkin labels are required")
    algebra = algebra or E8LieAlgebra()
    dimension = Q(1)
    for root in algebra.roots:
        height = sum(root)
        if height > 0:
            dimension *= Q(height+sum(x*y for x, y in zip(dynkin_labels, root)), height)
    if dimension.denominator != 1:
        raise ArithmeticError("Weyl dimension was not integral")
    return dimension.numerator


def _state_records(state):
    return [{"word": word, "coefficient": _json(z)} for word, z in sorted(state.items())]


def _jet_records(polynomial):
    return [{"divided_jet_monomial": monomial, "coefficient": _json(z)}
            for monomial, z in sorted(polynomial.items())]


def singular_square_receipt(module=None):
    """Replay the classical level-one singular vector and selected descendants."""
    module = module or AffinePBW()
    singular = module.singular_square()
    checks = []
    for mode in (1, 2):
        for index in range(248):
            value = module.act(index, mode, singular)
            if value:
                checks.append({"mode": mode, "index": index,
                               "residual_terms": len(value)})
    highest = module.finite_highest_checks(singular)
    original = module.leading_li_symbol(singular)['polynomial']
    derivative = module.derivative(singular)
    second = module.derivative(derivative)
    first_symbol = module.leading_li_symbol(derivative)['polynomial']
    second_symbol = module.leading_li_symbol(second)['polynomial']
    lowering = []
    for i in range(8):
        f = next(iter(module.algebra.simple_f(i)))
        state = module.act(f, 0, singular)
        lowering.append({"simple_root": i, "pbw_terms": len(state),
                         "squared_norm": _json(module.pairing(state, state))})
    return {"singular_vector": "e_theta[-1]^2|0>",
            "highest_root": list(module.algebra.roots[-1]),
            "positive_current_actions_checked": 496,
            "positive_current_witnesses": checks,
            "simple_positive_zero_modes_checked": highest,
            "finite_simple_lowering_descendants": lowering,
            "first_derivative": _state_records(derivative),
            "second_derivative": _state_records(second),
            "first_derivative_li_replay": first_symbol == jet_derivative(original),
            "second_derivative_li_replay": second_symbol == jet_derivative(jet_derivative(original)),
            "finite_null_module_dimension": highest_weight_dimension((0,0,0,0,0,0,2,0), module.algebra),
            "full_27000_descendant_basis_constructed": False,
            "passed": not checks and all(highest)
                      and first_symbol == jet_derivative(original)
                      and second_symbol == jet_derivative(jet_derivative(original))}


def verify_relation_certificate(certificate, *, exhaustive=False):
    """Replay a serialized lift, with full-sector pairings when requested."""
    if not isinstance(certificate, dict) or not isinstance(exhaustive, bool):
        raise ValueError("certificate must be an object and exhaustive a Boolean")
    module = AffinePBW()
    records = certificate.get('relation')
    if not isinstance(records, list) or len(records) > 20000:
        raise ValueError("a bounded serialized PBW relation is required")
    state = {}
    for record in records:
        if not isinstance(record, dict) or set(record) != {'word', 'coefficient'}:
            raise ValueError("PBW terms need word and coefficient fields")
        word = module.validate_word(record['word'])
        z = Q(record['coefficient'])
        if module.normalize(word) != {word: Q(1)} or word in state or not z:
            raise ValueError("relation terms must be distinct, nonzero canonical PBW words")
        if sum(n for n, _ in word) != 4 or module.root_weight(word) != OMEGA_3875:
            raise ValueError("relation has the wrong conformal or finite root weight")
        state[word] = z
    _, jet, candidates = module.weight_four_candidates()
    expected = {}
    for candidate, coefficient in zip(candidates, (1, -8, 24)):
        _add(expected, candidate, coefficient)
    high = module.finite_highest_checks(state)
    pairings = [module.pairing(candidate, state) for candidate in candidates]
    symbol = module.leading_li_symbol(state)
    checks = {'nonzero': bool(state), 'prescribed_lift': state == expected,
              'finite_highest': all(high), 'restricted_gram_radical': not any(pairings),
              'prescribed_li_symbol': symbol['polynomial'] == jet}
    witness = None
    count = 0
    if exhaustive:
        for word in module.weight_four_sector():
            value = module.pairing_word(word, state)
            count += 1
            if value:
                witness = {'word': word, 'pairing': _json(value)}
                break
        checks['complete_sector_radical'] = witness is None
    return {'passed': all(checks.values()), 'checks': checks,
            'exhaustive': exhaustive, 'complete_sector_pairings_checked': count,
            'witness': witness}


def relations_receipt(*, exhaustive=False):
    """Construct the bounded exact relation-search receipt (JSON safe)."""
    if not isinstance(exhaustive, bool):
        raise ValueError("exhaustive must be a Boolean")
    module = AffinePBW()
    quadratic, jet, candidates = module.weight_four_candidates()
    gram = [[module.pairing(x, y) for y in candidates] for x in candidates]
    kernel = nullspace(gram, 3)
    highest_checks = [module.finite_highest_checks(x) for x in candidates]
    singular = singular_square_receipt(module)
    nonmembership = arc_nonmembership_certificate(module)
    completeness = weight_four_completeness_receipt(module)
    out = {"schema": "perfectjet/asterion-affine-relations/1", "level": 1,
           "conformal_weight": 4, "target_finite_weight": list(OMEGA_3875),
           "highest_quadratic": [[list(pair), _json(z)] for pair, z in quadratic.items()],
           "jet_tensor_terms": len(jet),
           "candidate_pbw_terms": [len(x) for x in candidates],
           "finite_highest_checks": highest_checks,
           "affine_gram": _json(gram), "affine_gram_kernel": _json(kernel),
           "normalization": "F_Q=sum_a ad(t_a)(Q)*D(t^a); Sym denotes full PBW symmetrization; "
                            "Q31=sum Qij*(xi[-3]xj[-1]+xj[-3]xi[-1]); Q22=sum Qij*xi[-2]xj[-2]",
           "jet_convention": "variable(index,r)=D^r x_index/r! corresponds to x_index[-r-1]|0>",
           "jet_generator": _jet_records(jet),
           "singular_square": singular,
           "arc_nonmembership": nonmembership,
           "weight_four_completeness": completeness,
           "generated_kernel_component_weyl_dimension": highest_weight_dimension((1,0,0,0,0,0,0,0), module.algebra),
           "source": SONG_ZENG,
           "full_arc_kernel_claim": False,
           "ledger": [
               {"item": "level-one singular square and derivative consequences", "status": "known_exact_replayed"},
               {"item": "explicit783term F_Q and804term null lift", "status": "new_to_program_exact_construction", "priority_claim": False},
               {"item": "old-source highest-weight injectivity", "status": "exact_modular_rank_certificate_over_Q"},
               {"item": "complete weight-four kernel dimension3875", "status": "exact_projected_polarization_certificate"},
               {"item": "full differential arc-map kernel and its minimal generators", "status": "unresolved"}],
           "passed": all(all(row) for row in highest_checks)
                     and singular['passed'] and nonmembership['passed']
                     and completeness['passed'] and bool(jet) and len(kernel) == 1,
           "nonzero_arc_kernel_generator_certified_in_this_run": False,
           "weight4_kernel_complete_in_this_run": False}
    if kernel:
        coefficients = next((v for v in kernel if v[0]), None)
        if coefficients is not None:
            coefficients = [z/coefficients[0] for z in coefficients]
            relation = {}
            for state, z in zip(candidates, coefficients):
                _add(relation, state, z)
            symbol = module.leading_li_symbol(relation)
            sector = module.weight_four_sector()
            out["candidate_combination"] = _json(coefficients)
            out["relation_pbw_terms"] = len(relation)
            out["relation_squared_norm"] = _json(module.pairing(relation, relation))
            out["symbol_matches_jet_tensor"] = symbol["polynomial"] == jet
            out["li_differential_degree"] = symbol["differential_degree"]
            out["sector_dimension"] = len(sector)
            if exhaustive:
                checked = 0
                witness = None
                for word in sector:
                    z = module.pairing_word(word, relation)
                    checked += 1
                    if z:
                        witness = {"word": word, "pairing": z}
                        break
                out["complete_sector_pairing"] = {
                    "passed": witness is None, "rows_checked": checked,
                    "sector_dimension": len(sector), "witness": _json(witness)}
                out["passed"] = out['passed'] and witness is None
            out["relation"] = _state_records(relation)
            out["null_lift_certification"] = (
                "all14441 exact PBW sector pairings verified; affine radical membership"
                if exhaustive else "exact restricted3x3 Gram radical; request exhaustive for complete-sector certificate")
            out["passed"] = out['passed'] and symbol['polynomial'] == jet
            out["passed"] = out['passed'] and out['relation_squared_norm'] == 0
            out["nonzero_arc_kernel_generator_certified_in_this_run"] = exhaustive and out['passed']
            out["weight4_kernel_complete_in_this_run"] = exhaustive and out['passed']
        else:
            out['passed'] = False
    else:
        out['passed'] = False
    return _json(out)
