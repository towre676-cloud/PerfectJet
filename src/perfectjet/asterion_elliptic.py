"""Rank-eight Felder classical dynamical elliptic r-matrix for exact E8.

We use additive coordinates z,x with multiplicative variables X=exp(z),
Y=exp(x), and nome p=exp(2*pi*i*tau).  The theta function is odd, normalized
by theta'(0)=1, with quasiperiods 2*pi*i and log(p).  Its product ratios have
rational p-series coefficients at rational X,Y, so every finite certificate
below uses exact arithmetic, including all dynamical derivatives.

The analytic CDYBE statement is the classical Felder theorem, reduced here to
the universal Fay identity and its rank-one derivative limit.  Finite p-series
checks are reported separately from that analytic argument.  This module does
not construct a quantum R-matrix or a quantization of the 248-vector bracket.
"""
from __future__ import annotations

from fractions import Fraction as Q
from functools import lru_cache
from math import factorial

from .asterion_e8 import E8LieAlgebra


SOURCES = ('https://arxiv.org/abs/hep-th/9407154',
           'https://arxiv.org/abs/math/0207008',
           'https://arxiv.org/abs/1707.06469')
DEFAULT_MULTIPLIERS = (2, 3, 5, 7, 11, 13, 17, 19)


def _q(value):
    if isinstance(value, (float, bool)):
        raise ValueError('exact rational coordinates required')
    try:
        return Q(value)
    except (TypeError, ValueError, ZeroDivisionError) as exc:
        raise ValueError('exact rational coordinates required') from exc


def _order(order, maximum=4):
    if isinstance(order, bool) or not isinstance(order, int) or not 0 <= order <= maximum:
        raise ValueError(f'order must be an integer in 0..{maximum}')
    return order


def _nonzero(value, *, nonunit=False):
    value = _q(value)
    if not value or (nonunit and value == 1):
        raise ValueError('multiplicative coordinate is zero or lies on the p=0 theta pole')
    return value


def _unit(value, order):
    return (Q(value),) + (Q(0),) * order


def _mul(a, b):
    n = len(a) - 1
    out = [Q(0)] * (n + 1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b[:n + 1 - i]):
                if y:
                    out[i + j] += x * y
    return tuple(out)


def _scale(a, scalar):
    return tuple(x * scalar for x in a)


def _plus(a, b, scale=1):
    return tuple(x + scale * y for x, y in zip(a, b))


def _inverse(a):
    if not a[0]:
        raise ValueError('a unit series is required')
    out = [1 / a[0]]
    for n in range(1, len(a)):
        out.append(-sum((a[k] * out[n - k] for k in range(1, n + 1)), Q(0)) / a[0])
    return tuple(out)


def _matrix_inverse(a):
    n = len(a)
    rows = [[Q(x) for x in row] + [Q(i == j) for j in range(n)] for i, row in enumerate(a)]
    for c in range(n):
        pivot = next((r for r in range(c, n) if rows[r][c]), None)
        if pivot is None:
            raise ValueError('singular invariant metric')
        rows[c], rows[pivot] = rows[pivot], rows[c]
        divisor = rows[c][c]
        rows[c] = [x / divisor for x in rows[c]]
        for r in range(n):
            if r != c and rows[r][c]:
                z = rows[r][c]
                rows[r] = [x - z * y for x, y in zip(rows[r], rows[c])]
    return tuple(tuple(row[n:]) for row in rows)


def _json(value):
    if isinstance(value, Q):
        return value.numerator if value.denominator == 1 else str(value)
    if isinstance(value, dict):
        return {str(k): _json(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json(v) for v in value]
    return value


class ThetaKernel:
    """Exact p-series of the normalized odd-theta Kronecker kernel."""
    def __init__(self, order=1):
        self.order = _order(order)

    @lru_cache(maxsize=8192, typed=True)
    def product_factor(self, x):
        """B(X)=product_(n>=1)(1-p^n X)(1-p^n/X)/(1-p^n)^2."""
        x = _nonzero(x)
        n = self.order
        out = _unit(1, n)
        for step in range(1, n + 1):
            factor = [Q(0)] * (n + 1)
            factor[0] = 1
            factor[step] = -(x + 1 / x)
            if 2 * step <= n:
                factor[2 * step] = 1
            denominator = [Q(0)] * (n + 1)
            for k in range(n // step + 1):
                denominator[k * step] = k + 1
            out = _mul(_mul(out, factor), denominator)
        return out

    @lru_cache(maxsize=8192, typed=True)
    def log_product_derivative(self, x):
        """X*d_X log B(X), regular also at X=1."""
        x = _nonzero(x)
        out = [Q(0)] * (self.order + 1)
        for degree in range(1, self.order + 1):
            out[degree] = sum((x ** (-k) - x ** k for k in range(1, degree + 1) if degree % k == 0), Q(0))
        return tuple(out)

    @lru_cache(maxsize=8192, typed=True)
    def rho(self, x):
        """rho(z)=theta'(z)/theta(z), X=exp(z)."""
        x = _nonzero(x, nonunit=True)
        out = list(self.log_product_derivative(x))
        out[0] = (x + 1) / (2 * (x - 1))
        return tuple(out)

    @lru_cache(maxsize=16384, typed=True)
    def _ratio(self, x, y):
        return _mul(self.product_factor(x * y), _inverse(_mul(self.product_factor(x), self.product_factor(y))))

    @lru_cache(maxsize=16384, typed=True)
    def phi(self, x, y):
        """Phi(z,a)=theta(z+a)/(theta(z)*theta(a)), theta'(0)=1."""
        x, y = _nonzero(x, nonunit=True), _nonzero(y, nonunit=True)
        return _scale(self._ratio(x, y), (x * y - 1) / ((x - 1) * (y - 1)))

    @lru_cache(maxsize=16384, typed=True)
    def dphi(self, x, y):
        """Additive derivative d_a Phi, equivalently Y*d_Y Phi.

        The product formula avoids the removable 0*infinity in
        Phi*(rho(z+a)-rho(a)) when X*Y=1.
        """
        x, y = _nonzero(x, nonunit=True), _nonzero(y, nonunit=True)
        prefactor = (x * y - 1) / ((x - 1) * (y - 1))
        derivative = -y / (y - 1) ** 2
        bracket = _plus(_unit(derivative, self.order),
            _scale(_plus(self.log_product_derivative(x * y), self.log_product_derivative(y), -1), prefactor))
        return _mul(self._ratio(x, y), bracket)

    def root_fay_residual(self, u, v, a, b):
        """Fay in the exact form multiplying an E8 three-root coefficient."""
        u, v, a, b = map(_nonzero, (u, v, a, b))
        first = _mul(self.phi(u, 1 / b), self.phi(u * v, a * b))
        second = _mul(self.phi(u, a), self.phi(v, a * b))
        third = _mul(self.phi(u * v, a), self.phi(v, b))
        return _plus(_plus(first, second, -1), third)

    def derivative_fay_residual(self, u, v, a):
        """The opposite-root limit of Fay, including the dynamical derivative."""
        u, v, a = map(_nonzero, (u, v, a))
        first = self.dphi(v, a)
        second = _mul(_plus(self.rho(u), self.rho(u * v), -1), self.phi(v, a))
        third = _mul(self.phi(u, 1 / a), self.phi(u * v, a))
        return _plus(_plus(first, second), third, -1)

    def opposite_root_residuals(self, u, v, a):
        """All three possible Cartan slots in an opposite-root coefficient."""
        u, v, a = map(_nonzero, (u, v, a))
        middle = _plus(_scale(self.dphi(u * v, a), -1),
                      _mul(_plus(self.rho(u), self.rho(v)), self.phi(u * v, a)))
        middle = _plus(middle, _mul(self.phi(u, a), self.phi(v, a)), -1)
        return (self.derivative_fay_residual(u, v, a), middle,
                self.derivative_fay_residual(v, u, a))


def _add_tensor(out, key, values, scale=1):
    if not scale or not any(values):
        return
    before = out.get(key)
    result = _scale(values, scale) if before is None else _plus(before, values, scale)
    if any(result):
        out[key] = result
    else:
        out.pop(key, None)


def _cdybe_tables(algebra, r12, r13, r23, derivatives, derivative_scale):
    """Contract the three actual bracket tensors and derivative families."""
    out = {}
    products = 0
    for left, right, slot in ((r12, r13, 0), (r12, r23, 1), (r13, r23, 2)):
        for (a, b), x in left.items():
            for (c, d), y in right.items():
                inputs = (a, c) if slot == 0 else (b, c) if slot == 1 else (b, d)
                bracket = algebra.basis_bracket(*inputs)
                if not bracket:
                    continue
                values = _mul(x, y)
                products += 1
                for k, coefficient in bracket.items():
                    key = (k, b, d) if slot == 0 else (a, k, d) if slot == 1 else (a, c, k)
                    _add_tensor(out, key, values, coefficient)
    ordinary_nonzero = len(out)
    ordinary_witness = next(iter(sorted(out.items())), None)
    derivative_terms = 0
    for slot, family in enumerate(derivatives):
        for i, table in enumerate(family):
            for (a, b), values in table.items():
                key = (i, a, b) if slot == 0 else (a, i, b) if slot == 1 else (a, b, i)
                _add_tensor(out, key, values, -derivative_scale if slot == 1 else derivative_scale)
                derivative_terms += 1
    return {'passed': not out, 'tensor_terms_per_r': (len(r12), len(r13), len(r23)),
            'nonzero_bracket_products': products,
            'ordinary_cybe_nonzero_components': ordinary_nonzero,
            'ordinary_cybe_witness': ordinary_witness,
            'dynamical_derivative_terms': derivative_terms, 'derivative_scale': derivative_scale,
            'residual_components': len(out), 'residual_witness': next(iter(sorted(out.items())), None)}


class EllipticE8R:
    """Felder classical elliptic dynamical r in the complete 248-vector E8.

    lambda_i=lambda(h_i), so x_alpha=sum_i alpha_i*lambda_i.  We specialize
    exp(lambda_i) to rational nonzero multipliers for exact formal p checks.
    Dynamical derivatives are alpha_i*d_x Phi; no metric factor is omitted.
    The inverse Cartan matrix belongs in the Cartan Casimir tensor.
    """
    def __init__(self, order=1, algebra=None):
        self.algebra = algebra or E8LieAlgebra()
        self.kernel = ThetaKernel(order)
        self.order = self.kernel.order
        self.inverse_cartan = _matrix_inverse(self.algebra.cartan_matrix)
        self.cartan_casimir = {(i, j): value for i, row in enumerate(self.inverse_cartan)
                               for j, value in enumerate(row) if value}
        self.root_pairs = tuple((root, self.algebra.root_index[root],
                                self.algebra.root_index[tuple(-x for x in root)])
                               for root in self.algebra.roots)

    def _parameters(self, multipliers):
        multipliers = tuple(map(_nonzero, multipliers))
        if len(multipliers) != 8:
            raise ValueError('eight multiplicative Cartan coordinates required')
        root_values = {}
        for root, _, _ in self.root_pairs:
            value = Q(1)
            for coordinate, power in zip(multipliers, root):
                value *= coordinate ** power
            if value == 1:
                raise ValueError(f'dynamical point lies on the theta pole for root {root}')
            root_values[root] = value
        return multipliers, root_values

    def tensor(self, spectral=23, multipliers=DEFAULT_MULTIPLIERS):
        spectral = _nonzero(spectral, nonunit=True)
        _, root_values = self._parameters(multipliers)
        out = {key: _scale(self.kernel.rho(spectral), value) for key, value in self.cartan_casimir.items()}
        for root, positive, negative in self.root_pairs:
            values = self.kernel.phi(spectral, root_values[root])
            if any(values):
                out[positive, negative] = values
        return out

    def derivatives(self, spectral=23, multipliers=DEFAULT_MULTIPLIERS):
        spectral = _nonzero(spectral, nonunit=True)
        _, root_values = self._parameters(multipliers)
        out = [dict() for _ in range(8)]
        for root, positive, negative in self.root_pairs:
            values = self.kernel.dphi(spectral, root_values[root])
            for i, coefficient in enumerate(root):
                if coefficient:
                    out[i][positive, negative] = _scale(values, coefficient)
        return tuple(out)

    def casimir(self):
        return self.cartan_casimir | {(a, b): Q(1) for _, a, b in self.root_pairs}

    def metric_certificate(self):
        g = self.algebra
        omega = self.casimir()
        checks = 0
        for generator in [g.simple_e(i) for i in range(8)] + [g.simple_f(i) for i in range(8)]:
            out = {}
            for (a, b), value in omega.items():
                for c, coefficient in g.bracket(generator, {a: Q(1)}).items():
                    out[c, b] = out.get((c, b), Q(0)) + value * coefficient
                for c, coefficient in g.bracket(generator, {b: Q(1)}).items():
                    out[a, c] = out.get((a, c), Q(0)) + value * coefficient
            if any(out.values()):
                raise ArithmeticError('E8 invariant Casimir failed simple-generator invariance')
            checks += 1
        gradient_checks = 0
        for root, _, _ in self.root_pairs:
            dual = tuple(sum(self.inverse_cartan[i][j] * sum(g.cartan_matrix[j][k] * root[k]
                         for k in range(8)) for j in range(8)) for i in range(8))
            if dual != root or g.inner_product(root, root) != 2:
                raise ArithmeticError('root/Cartan metric normalization failed')
            gradient_checks += 1
        if self.kernel.product_factor(1) != _unit(1, self.order):
            raise ArithmeticError('theta derivative-at-zero normalization failed')
        return {'rank': 8, 'root_count': 240, 'cartan_casimir_terms': len(self.cartan_casimir),
                'casimir_terms': len(omega), 'simple_generator_invariance_checks': checks,
                'root_metric_gradient_checks': gradient_checks,
                'spectral_residue': 'Res_(z=0) r(z,lambda)=Omega',
                'normalized_theta_product_at_zero': True,
                'root_pair_metric': 'B(e_alpha,e_minus_alpha)=1',
                'cartan_metric': 'B(h_i,h_j)=Cartan_ij; Omega_h=sum(Cartan^-1)_ij*h_i tensor h_j',
                'passed': True}

    def reduction_certificate(self, u=23, v=29, multipliers=DEFAULT_MULTIPLIERS):
        """All E8 root-triple signs and both universal Fay coefficient types."""
        u, v = _nonzero(u, nonunit=True), _nonzero(v, nonunit=True)
        _nonzero(u * v, nonunit=True)
        parameters, values = self._parameters(multipliers)
        g = self.algebra
        fay_checks = 0
        for alpha, ia, _ in self.root_pairs:
            for beta, ib, _ in self.root_pairs:
                total = tuple(a + b for a, b in zip(alpha, beta))
                if total not in g.root_index:
                    continue
                gamma = tuple(-x for x in total)
                minus = lambda root: g.root_index[tuple(-x for x in root)]
                n1 = g.basis_bracket(minus(beta), minus(gamma)).get(ia, Q(0))
                n2 = g.basis_bracket(minus(alpha), minus(gamma)).get(ib, Q(0))
                n3 = g.basis_bracket(minus(alpha), minus(beta)).get(g.root_index[gamma], Q(0))
                if not n1 or n1 != -n2 or n1 != n3:
                    raise ArithmeticError('root-triple invariant sign relation failed')
                residual = self.kernel.root_fay_residual(u, v, values[alpha], values[beta])
                if any(residual):
                    raise ArithmeticError('a complete E8 root-triple Fay coefficient failed')
                fay_checks += 1
        derivative_checks = 0
        unitarity_checks = 0
        for root, _, _ in self.root_pairs:
            a = values[root]
            if any(any(residual) for residual in self.kernel.opposite_root_residuals(u, v, a)):
                raise ArithmeticError('opposite-root derivative Fay coefficient failed')
            derivative_checks += 1
            if any(_plus(self.kernel.phi(u, a), self.kernel.phi(1 / u, 1 / a))):
                raise ArithmeticError('root kernel spectral unitarity failed')
            unitarity_checks += 1
        if any(_plus(self.kernel.rho(u), self.kernel.rho(1 / u))):
            raise ArithmeticError('Cartan kernel spectral unitarity failed')
        return {'p_order': self.order, 'spectral_multipliers': (u, v, u * v),
            'cartan_multipliers': parameters, 'dynamical_rank': 8,
            'ordered_three_root_fay_checks': fay_checks,
            'opposite_root_derivative_checks': derivative_checks,
            'opposite_root_tensor_arrangement_checks': 3 * derivative_checks,
            'root_spectral_unitarity_checks': unitarity_checks,
            'zero_weight_tensor_components': 8 ** 3 + 3 * 8 * 240 + fay_checks,
            'all_cartan_components_vanish_structurally': True,
            'passed': True,
            'scope': 'All E8 root coefficient types at the declared exact Cartan/spectral specialization through p^order; analytic universality uses the stated Fay proof.'}

    def cdybe(self, u=23, v=29, multipliers=DEFAULT_MULTIPLIERS, *, derivative_scale=1):
        """Direct full tensor CDYBE, retaining all eight derivative coordinates.

        derivative_scale is exposed for negative controls.  Only scale=1
        is the declared elliptic CDYBE; scale=0 demonstrates its necessity.
        """
        u, v = _nonzero(u, nonunit=True), _nonzero(v, nonunit=True)
        derivative_scale = _q(derivative_scale)
        r12, r13, r23 = self.tensor(u, multipliers), self.tensor(u * v, multipliers), self.tensor(v, multipliers)
        derivatives = (self.derivatives(v, multipliers), self.derivatives(u * v, multipliers), self.derivatives(u, multipliers))
        result = _cdybe_tables(self.algebra, r12, r13, r23, derivatives, derivative_scale)
        return result | {'p_order': self.order,
            'scope': 'Direct full E8 tensor arithmetic at the declared specialization; zero residual is exact at every retained p coefficient.'}


def _exponential(z, order):
    z = _q(z)
    return tuple(z ** n / factorial(n) for n in range(order + 1))


def trig_to_rational_series(z, x, order=6):
    """epsilon*rho_0(exp(epsilon*z)) and epsilon*Phi_0 for exact degeneration."""
    order = _order(order, 12)
    z, x = _q(z), _q(x)
    if not z or not x:
        raise ValueError('rational spectral and dynamical coordinates must be nonzero')
    def scaled_rho(value):
        exponential = _exponential(value, order + 1)
        unit_denominator = exponential[1:order + 2]
        numerator = tuple(exponential[n] + Q(n == 0) for n in range(order + 1))
        return _scale(_mul(numerator, _inverse(unit_denominator)), Q(1, 2))
    rho = scaled_rho(z)
    dynamic_rho = scaled_rho(x)
    return {'rho_series': rho, 'phi_series': _plus(rho, dynamic_rho),
            'rational_rho': 1 / z, 'rational_phi': 1 / z + 1 / x,
            'passed': rho[0] == 1 / z and rho[0] + dynamic_rho[0] == 1 / z + 1 / x,
            'scope': 'p->0 first, followed by additive scaling z,x -> epsilon*(z,x); exact formal epsilon coefficients.'}


def rational_e8_tensor(z=2, lambdas=(1, 2, 3, 4, 5, 6, 7, 8), algebra=None):
    """The actual rational degeneration Omega/z + sum_alpha e_alpha*e_-alpha/x_alpha."""
    z = _q(z)
    if not z:
        raise ValueError('spectral coordinate is a pole')
    lambdas = tuple(map(_q, lambdas))
    if len(lambdas) != 8:
        raise ValueError('eight additive Cartan coordinates required')
    model = EllipticE8R(0, algebra)
    out = {pair: value / z for pair, value in model.cartan_casimir.items()}
    for root, a, b in model.root_pairs:
        x = sum((coefficient * value for coefficient, value in zip(root, lambdas)), Q(0))
        if not x:
            raise ValueError('additive Cartan point lies on a rational root pole')
        coefficient = 1 / z + 1 / x
        if coefficient:
            out[a, b] = coefficient
    return out


def rational_cdybe(u=Q(2, 101), v=Q(3, 103), lambdas=(1, 2, 3, 4, 5, 6, 7, 8),
                   *, algebra=None, derivative_scale=1):
    """Full exact CDYBE for the actual rational degeneration, with additive u,v."""
    u, v = _q(u), _q(v)
    derivative_scale = _q(derivative_scale)
    if not u or not v or not u + v:
        raise ValueError('a rational spectral difference lies on a pole')
    lambdas = tuple(map(_q, lambdas))
    model = EllipticE8R(0, algebra)
    tables = tuple({key: (value,) for key, value in
                   rational_e8_tensor(z, lambdas, model.algebra).items()} for z in (u, u + v, v))
    derivatives = [dict() for _ in range(8)]
    for root, a, b in model.root_pairs:
        x = sum((coefficient * value for coefficient, value in zip(root, lambdas)), Q(0))
        for i, coefficient in enumerate(root):
            if coefficient:
                derivatives[i][a, b] = (-coefficient / x ** 2,)
    result = _cdybe_tables(model.algebra, *tables, (derivatives,) * 3, derivative_scale)
    return result | {'spectral_coordinates': (u, v, u + v), 'cartan_coordinates': lambdas,
                     'scope': 'Direct exact rational E8 tensor CDYBE after the sequential degeneration.'}


def degeneration_receipt(algebra=None):
    model = EllipticE8R(0, algebra)
    parameters, roots = model._parameters(DEFAULT_MULTIPLIERS)
    tensor = model.tensor(23, parameters)
    scalar_checks = 0
    for root, a, b in model.root_pairs:
        expected = model.kernel.rho(23)[0] + model.kernel.rho(roots[root])[0]
        if tensor[a, b][0] != expected:
            raise ArithmeticError('elliptic constant coefficient differs from the trigonometric degeneration')
        scalar_checks += 1
    additive = (1, 2, 3, 4, 5, 6, 7, 8)
    rational = rational_e8_tensor(2, additive, model.algebra)
    rational_checks = 0
    for root, a, b in model.root_pairs:
        x = sum(coefficient * value for coefficient, value in zip(root, additive))
        limit = trig_to_rational_series(2, x)
        if limit['phi_series'][0] != rational.get((a, b), Q(0)):
            raise ArithmeticError('root coefficient rational degeneration failed')
        rational_checks += 1
    rational_check = rational_cdybe(algebra=model.algebra)
    return {'elliptic_to_trigonometric_root_checks': scalar_checks,
            'trigonometric_to_rational_root_checks': rational_checks,
            'rational_tensor_terms': len(rational),
            'rational_cdybe': rational_check,
            'representative_formal_limit': trig_to_rational_series(2, 3),
            'rational_formula': 'r_rat(z,lambda)=Omega/z+sum_alpha (1/x_alpha)*e_alpha tensor e_minus_alpha',
            'passed': rational_check['passed'],
            'scope': 'Sequential p->0 and additive-scaling degeneration; no arbitrary simultaneous limiting path is claimed.'}


def elliptic_receipt(exhaustive=False, *, order=None, full_tensor=True):
    """JSON-safe actual E8 elliptic-r compatibility and degeneration evidence."""
    if not isinstance(exhaustive, bool) or not isinstance(full_tensor, bool):
        raise ValueError('exhaustive and full_tensor must be booleans')
    if order is None:
        order = 2 if exhaustive else 1
    model = EllipticE8R(order)
    metric = model.metric_certificate()
    reduction = model.reduction_certificate()
    direct = model.cdybe() if full_tensor else None
    degeneration = degeneration_receipt(model.algebra)
    return _json({'schema': 'perfectjet/asterion-elliptic-r/1', 'p_order': order,
        'exhaustive': exhaustive,
        'arithmetic': 'exact rational coefficients of formal p-series at rational multiplicative coordinates',
        'formula': 'r(z,lambda)=rho(z)*Omega_h+sum_alpha Phi(z,x_alpha)*e_alpha tensor e_minus_alpha',
        'coordinates': 'lambda_i=lambda(h_i), x_alpha=sum(alpha_i*lambda_i), X=exp(z), L_i=exp(lambda_i)',
        'domain': 'Im(tau)>0; p=exp(2*pi*i*tau); z and every x_alpha avoid 2*pi*i*Z+log(p)*Z; finite formal checks avoid X=1 and all root multipliers=1',
        'cdybe_convention': 'h_i^(1)*d_i r23(v)-h_i^(2)*d_i r13(u+v)+h_i^(3)*d_i r12(u)+[r12,r13]+[r12,r23]+[r13,r23]=0',
        'metric': metric, 'complete_root_fay_reduction': reduction,
        'direct_tensor_cdybe': direct, 'degenerations': degeneration,
        'analytic_proof': {'status': 'classical theorem with explicit coefficient reduction in ASTERION_ELLIPTIC.md',
            'ingredients': ['odd normalized Jacobi theta', 'Fay trisecant identity',
                           'opposite-root derivative limit of Fay', 'invariant E8 metric and root-triple signs'],
            'finite_series_is_not_analytic_proof': True},
        'passed': metric['passed'] and reduction['passed'] and degeneration['passed']
                  and degeneration['rational_cdybe']['passed'] and (direct is None or direct['passed']),
        'quantum_r_matrix_constructed': False, 'sources': SOURCES,
        'scope': 'An actual rank-eight classical dynamical elliptic E8 r-matrix with spectral parameter. No quantum R-matrix or new Lie bracket is asserted.'})
