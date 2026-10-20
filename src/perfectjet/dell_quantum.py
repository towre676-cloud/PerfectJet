"""Exact two-nome certificates for normally ordered quantum DELL currents.

This is an independent, standard-library compiler for the coordinate-trigonometric
expansion of the Koroteev--Shakirov current.  It evaluates *every* Laurent
shift coefficient of a requested finite two-nome commutator at exact rational
positions. These point certificates are not functional identities or
an all-order proof of the DELL commutativity conjecture.

The declared action is S^n f(X)=f(Q^n X) S^n.  The classical coefficient product
is therefore not a valid implementation of quantum multiplication.  The common
left theta denominator cancels from (D C_0)^-1(D C_a), so the ratio coefficients
used below give precisely the same left-normalized operators as the raw current.

Source: https://arxiv.org/abs/1906.10354, equations (1.10)--(1.12), (3.2)--(3.3).
Their p is a square-root nome; our coordinate nome is its square P=p^2.
"""
from __future__ import annotations

from fractions import Fraction as Q
from functools import lru_cache
from itertools import product


class _NomeSeries:
    """Truncated coordinate-nome ring used inside the shift-operator algebra."""
    __slots__ = ("coefficients",)

    def __init__(self, coefficients):
        self.coefficients = tuple(Q(x) for x in coefficients)

    def _coerce(self, other):
        if isinstance(other,_NomeSeries):
            if len(other.coefficients) != len(self.coefficients):
                raise ValueError("incompatible nome orders")
            return other
        return _NomeSeries((Q(other),)+(Q(0),)*(len(self.coefficients)-1))

    def __add__(self, other):
        other=self._coerce(other)
        return _NomeSeries(tuple(a+b for a,b in zip(self.coefficients,other.coefficients)))

    __radd__ = __add__

    def __neg__(self):
        return _NomeSeries(tuple(-x for x in self.coefficients))

    def __sub__(self, other):
        return self+-self._coerce(other)

    def __rsub__(self, other):
        return self._coerce(other)+-self

    def __mul__(self, other):
        other=self._coerce(other)
        a,b=self.coefficients,other.coefficients
        return _NomeSeries(tuple(sum((a[k]*b[n-k] for k in range(n+1)),Q(0))
                                 for n in range(len(a))))

    __rmul__ = __mul__

    def inverse(self):
        a=self.coefficients
        if not a[0]:
            raise ValueError("a theta denominator is not a formal unit")
        result=[1/a[0]]
        for n in range(1,len(a)):
            result.append(-sum((a[k]*result[n-k] for k in range(1,n+1)),Q(0))/a[0])
        return _NomeSeries(result)

    def __truediv__(self, other):
        return self*self._coerce(other).inverse()

    def __bool__(self):
        return any(self.coefficients)

    def __eq__(self, other):
        try:
            return self.coefficients==self._coerce(other).coefficients
        except (TypeError,ValueError):
            return False


def _exact(value):
    if isinstance(value, (bool, float)):
        raise ValueError("exact rational parameters required")
    try:
        return Q(value)
    except (TypeError, ValueError, ZeroDivisionError) as exc:
        raise ValueError("exact rational parameters required") from exc


def _integer(value, name, minimum, maximum):
    if isinstance(value, bool) or not isinstance(value, int) or not minimum <= value <= maximum:
        raise ValueError(f"{name} must be an integer in {minimum}..{maximum}")
    return value


def _add(left, right):
    return tuple(x+y for x, y in zip(left, right))


def _accumulate(out, key, value):
    if value:
        out[key] = out.get(key, Q(0)) + value
        if not out[key]:
            del out[key]


def _json_number(value):
    if isinstance(value,_NomeSeries):
        return [_json_number(x) for x in value.coefficients]
    return value.numerator if value.denominator == 1 else str(value)


class QuantumDellBoundary:
    """Finite P,W-adic operators at rational positions and arbitrary exact Q.

    The small defaults intentionally make complete exact coefficient checking
    practical.  Offset points are cached because inverse normalization recursively
    asks for coefficients at many translated positions.  Singular shifted
    diagonals raise an error instead of being silently regularized.
    """

    def __init__(self, positions=(2, 5, 11), coupling=3, quantum=7, order=2,
                 coordinate_order=0):
        positions = tuple(_exact(x) for x in positions)
        if not 2 <= len(positions) <= 4 or any(not x for x in positions):
            raise ValueError("two to four nonzero exact positions required")
        self.positions = positions
        self.coupling = _exact(coupling)
        self.quantum = _exact(quantum)
        if not self.coupling or not self.quantum:
            raise ValueError("coupling and quantum shift must be nonzero")
        self.order = _integer(order, "order", 0, 4)
        self.coordinate_order = _integer(coordinate_order,"coordinate_order",0,3)
        self.rank = len(positions)
        self.zero = (0,)*self.rank
        # e(n)=n(n-1)/2 is nonnegative; this larger-than-needed interval
        # contains every integer with e(n)<=order, including n=0,1.
        choices = tuple(n for n in range(-self.order-1, self.order+3)
                        if n*(n-1)//2 <= self.order)
        shells = {}
        for shift in product(choices, repeat=self.rank):
            degree = sum(n*(n-1)//2 for n in shift)
            if degree <= self.order:
                shells.setdefault((sum(shift), degree), []).append(shift)
        self.shells = {key:tuple(values) for key, values in shells.items()}

    def _offset(self, offset):
        offset = tuple(offset)
        if len(offset) != self.rank or any(isinstance(x, bool) or not isinstance(x, int)
                                           for x in offset):
            raise ValueError("one integer offset per position required")
        return offset

    @lru_cache(maxsize=None)
    def theta(self, z):
        """Theta(z;P) without the scalar Euler factor, which cancels in ratios."""
        z=Q(z)
        m=self.coordinate_order
        if not m:
            return 1-z
        result=_NomeSeries((1-z,)+(Q(0),)*m)
        for k in range(1,m+1):
            a=[Q(0)]*(m+1);a[0]=1;a[k]=-z
            b=[Q(0)]*(m+1);b[0]=1;b[k]=-1/z
            result=result*_NomeSeries(a)*_NomeSeries(b)
        return result

    @lru_cache(maxsize=None)
    def coefficient(self, shift, offset):
        """C_n(Q^offset X), as an exact rational or formal P-series."""
        shift, offset = self._offset(shift), self._offset(offset)
        point = tuple(x*self.quantum**d for x, d in zip(self.positions, offset))
        result = Q(1)
        for i in range(self.rank):
            for j in range(i+1, self.rank):
                ratio = point[i]/point[j]
                if ratio == 1:
                    raise ValueError("a shifted position lies on a theta denominator divisor")
                result *= self.theta(self.coupling**(shift[i]-shift[j])*ratio)/self.theta(ratio)
        return result

    @lru_cache(maxsize=None)
    def current(self, charge, degree, offset=None):
        """Every shift coefficient of C_charge at exactly W^degree."""
        if offset is None:
            offset = self.zero
        offset = self._offset(offset)
        _integer(degree, "degree", 0, self.order)
        if isinstance(charge, bool) or not isinstance(charge, int):
            raise ValueError("charge must be an integer")
        return {shift:value for shift in self.shells.get((charge, degree), ())
                if (value := self.coefficient(shift, offset))}

    @lru_cache(maxsize=None)
    def normalized(self, charge, degree, offset=None):
        """Coefficient of C_0^-1 C_charge from C_0 H_charge=C_charge."""
        if offset is None:
            offset = self.zero
        offset = self._offset(offset)
        _integer(degree, "degree", 0, self.order)
        out = dict(self.current(charge, degree, offset))
        for k in range(1, degree+1):
            for shift, value in self.current(0, k, offset).items():
                translated = _add(offset, shift)
                for following, coefficient in self.normalized(charge, degree-k, translated).items():
                    _accumulate(out, _add(shift, following), -value*coefficient)
        return out

    def multiply(self, left_charge, right_charge, *, normalized=True, frozen=False):
        """Return every coefficient by (W degree, total shift).

        frozen=True deliberately computes the incorrect scalar Laurent product,
        retained only to demonstrate that coefficient translation matters.
        """
        builder = self.normalized if normalized else self.current
        answer = {}
        for degree in range(self.order+1):
            out = {}
            for k in range(degree+1):
                for shift, value in builder(left_charge, k, self.zero).items():
                    offset = self.zero if frozen else shift
                    for following, coefficient in builder(right_charge, degree-k, offset).items():
                        _accumulate(out, _add(shift, following), value*coefficient)
            answer[degree] = out
        return answer

    def commutator(self, left_charge=1, right_charge=2, *, normalized=True):
        left = self.multiply(left_charge, right_charge, normalized=normalized)
        right = self.multiply(right_charge, left_charge, normalized=normalized)
        answer = {}
        for degree in range(self.order+1):
            out = dict(left[degree])
            for shift, value in right[degree].items():
                _accumulate(out, shift, -value)
            answer[degree] = out
        return answer

    def receipt(self, left_charge=1, right_charge=2):
        if self.rank < 3:
            raise ValueError("a two-Hamiltonian certificate requires at least three particles")
        _integer(left_charge,"left_charge",1,self.rank-1)
        _integer(right_charge,"right_charge",1,self.rank-1)
        if left_charge==right_charge:
            raise ValueError("two distinct Hamiltonian charges required")
        exact = self.commutator(left_charge,right_charge)
        raw = self.commutator(left_charge,right_charge,normalized=False)
        ordinary = self.multiply(left_charge,right_charge,frozen=True)
        ordered = self.multiply(left_charge,right_charge)
        witnesses = []
        for degree in range(self.order+1):
            for shift, value in sorted(raw[degree].items()):
                witnesses.append({"degree":degree,"shift":list(shift),
                                  "coefficient":_json_number(value)})
        frozen_witness = None
        for degree in range(self.order+1):
            for shift in sorted(set(ordinary[degree])|set(ordered[degree])):
                difference = ordered[degree].get(shift,Q(0))-ordinary[degree].get(shift,Q(0))
                if difference:
                    frozen_witness = {"degree":degree,"shift":list(shift),
                                      "ordered_minus_frozen":_json_number(difference)}
                    break
            if frozen_witness:
                break
        counts = [len(ordered[d]) for d in range(self.order+1)]
        return {"schema":"perfectjet/dell-quantum-boundary/1",
                "passed":all(not values for values in exact.values()),
                "particles":self.rank,"positions":[_json_number(x) for x in self.positions],
                "hamiltonian_pair":[left_charge,right_charge],
                "coupling":_json_number(self.coupling),"quantum_shift":_json_number(self.quantum),
                "coordinate_nome":0 if not self.coordinate_order else "formal P",
                "coordinate_nome_order":self.coordinate_order,"momentum_nome_order":self.order,
                "normal_order":"S^n f(X)=f(Q^n X) S^n; coefficients on the left",
                "normalization":"H_a=C_0^-1 C_a; common raw-current denominator cancels on the left",
                "ordered_product_nonzero_coefficients_by_degree":counts,
                "normalized_commutator_nonzero_coefficients_by_degree":[len(exact[d]) for d in exact],
                "numerator_commutator_nonzero_coefficients_by_degree":[len(raw[d]) for d in raw],
                "numerator_commutator_first_witness":witnesses[0] if witnesses else None,
                "frozen_product_difference_witness":frozen_witness,
                "all_output_shift_coefficients_checked":True,
                "scope":"Exact finite-W and finite-P coefficient certificate at rational positions; not a rational-function identity or all-order theorem.",
                "source":"https://arxiv.org/abs/1906.10354"}


def quantum_boundary_receipt(*, exhaustive=False):
    """Replay two independent rational points in the two-nome expansion."""
    if not isinstance(exhaustive, bool):
        raise ValueError("exhaustive must be Boolean")
    order = 4 if exhaustive else 2
    coordinate_order=3 if exhaustive else 1
    points = (((2,5,11),3,7), ((3,7,13),Q(5,2),Q(3,2)))
    receipts = [QuantumDellBoundary(x,t,q,order,coordinate_order).receipt() for x,t,q in points]
    if exhaustive:
        four=QuantumDellBoundary((2,5,11,17),3,7,2,1)
        receipts.extend(four.receipt(i,j) for i in range(1,4) for j in range(i+1,4))
    return {"passed":all(row["passed"] for row in receipts),
            "exhaustive_requested":exhaustive,"certificates":receipts,
            "all_order_commutativity_proved":False,
            "coordinate_elliptic_dependence_checked":True,
            "claim_scope":"All finite shift outputs at the declared exact parameter points and finite P,W orders only."}
