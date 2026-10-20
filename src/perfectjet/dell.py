"""Exact two-nome classical Koroteev--Shakirov DELL laboratory.

P is the product nome of the coordinate theta function (the square of p in
KS eq. 3.3), W is the momentum nome, T is the coupling.  Coefficients are
evaluated exactly at rational nonsingular phase points; zero residuals at
these points are bounded certificates, not global commutativity proofs.
Independent global rational identities and no-go theorems live in the
normalization and obstructions modules.
"""
from __future__ import annotations

from fractions import Fraction as Q
from functools import lru_cache
from itertools import product
from math import isqrt


def rational(value):
    if isinstance(value, (float, bool)):
        raise ValueError("exact rational data required")
    return Q(value)


def _bound(value, maximum, name):
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= maximum:
        raise ValueError(f"{name} must be an integer in 0..{maximum}")
    return value


def _padd(a, b, scale=1):
    return tuple(x + scale*y for x, y in zip(a, b))


def _pmul(a, b):
    out = [Q(0)]*len(a)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b[:len(a)-i]):
                if y:
                    out[i+j] += x*y
    return tuple(out)


def _pinv(a):
    if not a[0]:
        raise ValueError("theta denominator has zero leading coefficient")
    out = [1/a[0]]
    for n in range(1, len(a)):
        out.append(-sum((a[j]*out[n-j] for j in range(1,n+1)),Q(0))/a[0])
    return tuple(out)


@lru_cache(maxsize=32768)
def theta_value_derivative(z, order):
    """Theta=(1-z) prod(1-P^m z)(1-P^m/z), and z*d_z Theta.

    The omitted z-independent product cancels from every ratio. Numerator
    zeros z=1 are allowed: the derivative is computed without dividing by it.
    """
    z = rational(z)
    if not z:
        raise ValueError("multiplicative theta argument must be nonzero")
    b = (Q(1),)+(Q(0),)*order
    derivative = (Q(0),)*(order+1)
    for m in range(1, order+1):
        f = [Q(0)]*(order+1)
        df = [Q(0)]*(order+1)
        f[0] = 1
        f[m] = -(z+1/z)
        df[m] = -z+1/z
        if 2*m <= order:
            f[2*m] = 1
        derivative = _padd(_pmul(derivative, f), _pmul(b, df))
        b = _pmul(b, f)
    return tuple((1-z)*v for v in b), _padd(tuple(-z*v for v in b),
                                                        tuple((1-z)*v for v in derivative))


@lru_cache(maxsize=65536)
def theta_ratio(z, multiplier, order):
    numerator, dn = theta_value_derivative(z*multiplier, order)
    denominator, dd = theta_value_derivative(z, order)
    inverse = _pinv(denominator)
    value = _pmul(numerator, inverse)
    derivative = _padd(_pmul(dn, inverse), _pmul(_pmul(value, dd), inverse), -1)
    return value, derivative


@lru_cache(maxsize=128)
def shift_shells(particles, momentum_order, charge):
    """Complete finite shell, proved by E(n)=sum n_i(n_i-1)/2>=0."""
    if isinstance(particles,bool) or not 2 <= particles <= 5:
        raise ValueError("particles must be in 2..5")
    _bound(momentum_order,8,"momentum order")
    if isinstance(charge,bool) or not isinstance(charge,int):
        raise ValueError("charge must be integral")
    radius = (1+isqrt(1+8*momentum_order))//2
    choices = [n for n in range(-radius,radius+2) if n*(n-1)//2 <= momentum_order]
    out = []
    for shift in product(choices, repeat=particles):
        if sum(shift) != charge:
            continue
        degree = sum(n*(n-1)//2 for n in shift)
        if degree <= momentum_order:
            out.append((degree,shift))
    return tuple(sorted(out))


class Series:
    """Rational P,W series in Q[P,W]/(P^(p+1),W^(w+1))."""
    __slots__ = ("p", "w", "terms")

    def __init__(self,p,w,terms=None):
        self.p,self.w = p,w
        self.terms = {k:rational(v) for k,v in (terms or {}).items()
                      if v and 0 <= k[0] <= w and 0 <= k[1] <= p}

    def _coerce(self, other):
        if isinstance(other,Series):
            if (self.p,self.w) != (other.p,other.w):
                raise ValueError("incompatible truncation rectangles")
            return other
        return Series(self.p,self.w,{(0,0):rational(other)})

    def __add__(self,other):
        other = self._coerce(other)
        out = self.terms.copy()
        for k,v in other.terms.items():
            out[k] = out.get(k,Q(0))+v
        return Series(self.p,self.w,out)

    __radd__ = __add__

    def __neg__(self):
        return Series(self.p,self.w,{k:-v for k,v in self.terms.items()})

    def __sub__(self,other):
        return self+-self._coerce(other)

    def __mul__(self,other):
        other = self._coerce(other)
        out = {}
        for (a,b),x in self.terms.items():
            for (c,d),y in other.terms.items():
                if a+c <= self.w and b+d <= self.p:
                    key = (a+c,b+d)
                    out[key] = out.get(key,Q(0))+x*y
        return Series(self.p,self.w,out)

    __rmul__ = __mul__

    def inverse(self):
        lead = self.terms.get((0,0),Q(0))
        if not lead:
            raise ValueError("unit series required")
        # Every nonconstant monomial has total degree >=1, so this geometric
        # sum terminates at w+p in the rectangular quotient ring.
        remainder = (self-Series(self.p,self.w,{(0,0):lead}))*(-1/lead)
        out = term = Series(self.p,self.w,{(0,0):1/lead})
        for _ in range(self.w+self.p):
            term = term*remainder
            out = out+term
        return out

    def as_json(self):
        return [{"W":a,"P":b,"value":str(v)} for (a,b),v in sorted(self.terms.items())]


class Jet:
    """Value and first log-coordinate derivatives; exact automatic differentiation."""
    __slots__ = ("value","derivatives")

    def __init__(self,value,derivatives):
        self.value,self.derivatives = value,tuple(derivatives)

    def __add__(self,other):
        return Jet(self.value+other.value,[a+b for a,b in zip(self.derivatives,other.derivatives)])

    def __mul__(self,other):
        return Jet(self.value*other.value,[a*other.value+self.value*b
                    for a,b in zip(self.derivatives,other.derivatives)])

    def inverse(self):
        inv = self.value.inverse()
        return Jet(inv,[-d*inv*inv for d in self.derivatives])


class ClassicalDELL:
    """Evaluate the current and normalized Hamiltonians with log-Poisson jets."""
    def __init__(self,x=(1,3,7),y=(2,5,11),coupling=2,*,coordinate_order=1,momentum_order=2):
        self.x,self.y = tuple(map(rational,x)),tuple(map(rational,y))
        self.n = len(self.x)
        if not 2 <= self.n <= 5 or len(self.y) != self.n:
            raise ValueError("matching position/momentum tuples of length2..5 required")
        self.t = rational(coupling)
        if not self.t or any(not a for a in self.x+self.y) or len(set(self.x)) != self.n:
            raise ValueError("nonzero coupling, nonzero coordinates and distinct positions required")
        self.p = _bound(coordinate_order,4,"coordinate order")
        self.w = _bound(momentum_order,8,"momentum order")
        self._currents = {}

    def zero(self):
        return Series(self.p,self.w)

    def unit_jet(self):
        return Jet(Series(self.p,self.w,{(0,0):1}),[self.zero() for _ in range(2*self.n)])

    def coefficient(self,shift):
        value = (Q(1),)+(Q(0),)*self.p
        dx = [(Q(0),)*(self.p+1) for _ in range(self.n)]
        for i in range(self.n):
            for j in range(i+1,self.n):
                ratio,dr = theta_ratio(self.x[i]/self.x[j],self.t**(shift[i]-shift[j]),self.p)
                dx = [_pmul(d,ratio) for d in dx]
                contribution = _pmul(value,dr)
                dx[i] = _padd(dx[i],contribution)
                dx[j] = _padd(dx[j],contribution,-1)
                value = _pmul(value,ratio)
        monomial = Q(1)
        for y,n in zip(self.y,shift):
            monomial *= y**n
        return tuple(v*monomial for v in value),[tuple(v*monomial for v in d) for d in dx]

    def current(self,charge):
        if charge in self._currents:
            return self._currents[charge]
        vals,derivatives = {},[{} for _ in range(2*self.n)]
        for degree,shift in shift_shells(self.n,self.w,charge):
            value,dx = self.coefficient(shift)
            for p,v in enumerate(value):
                key = (degree,p)
                vals[key] = vals.get(key,Q(0))+v
                for i in range(self.n):
                    derivatives[i][key] = derivatives[i].get(key,Q(0))+dx[i][p]
                    derivatives[self.n+i][key] = derivatives[self.n+i].get(key,Q(0))+shift[i]*v
        out = Jet(Series(self.p,self.w,vals),[Series(self.p,self.w,d) for d in derivatives])
        self._currents[charge] = out
        return out

    def hamiltonian(self,charge):
        return self.current(0).inverse()*self.current(charge)

    def poisson(self,left,right):
        out = self.zero()
        for i in range(self.n):
            out += left.derivatives[i]*right.derivatives[self.n+i]-left.derivatives[self.n+i]*right.derivatives[i]
        return out

    def replay(self):
        currents = [self.current(a) for a in range(self.n)]
        inverse = currents[0].inverse()
        h = [inverse*c for c in currents]
        pairs = []
        for a in range(1,self.n):
            for b in range(a+1,self.n):
                residual = self.poisson(h[a],h[b])
                raw = self.poisson(currents[a],currents[b])
                pairs.append({"charges":[a,b],"normalized_residual":residual.as_json(),
                              "raw_residual":raw.as_json(),"normalized_vanishes":not residual.terms,
                              "raw_nonzero":bool(raw.terms)})
        translation = []
        # In the literal sign-free current: C_(s+N)=W^s Y_all C_s.
        for charge in (0,1):
            lhs = self.current(charge+self.n).value
            yall = Q(1)
            for y in self.y:
                yall *= y
            rhs = self.current(charge).value*Series(self.p,self.w,{(charge,0):yall})
            translation.append({"charge":charge,"residual":(lhs-rhs).as_json(),"passed":not (lhs-rhs).terms})
        homogeneity = []
        for charge, state in enumerate(h):
            dx = sum(state.derivatives[:self.n],self.zero())
            dy = sum(state.derivatives[self.n:],self.zero())-charge*state.value
            homogeneity.append({"charge":charge,"position_residual":dx.as_json(),
                                "momentum_residual":dy.as_json(),"passed":not dx.terms and not dy.terms})
        yall = Q(1)
        for y in self.y:
            yall *= y
        matrix = [[v.derivatives[self.n+j].terms.get((0,0),Q(0)) for j in range(self.n)]
                  for v in h[1:]]+[[yall]*self.n]
        independence = determinant(matrix)
        return {"schema":"perfectjet/dell-classical/1","particles":self.n,
                "phase_point":{"x":list(map(str,self.x)),"y":list(map(str,self.y)),"T":str(self.t)},
                "truncation":{"P":self.p,"W":self.w},"poisson_convention":"{log Xi,log Yj}=delta_ij",
                "theta_convention":"Theta(z;P)=(1-z) product_m>=1 (1-P^m z)(1-P^m/z); scalar factor cancels",
                "current_convention":"sign-free C_a; physical (-1)^a factors do not change involutivity",
                "shell_counts":{str(a):[sum(degree==d for degree,_ in shift_shells(self.n,self.w,a))
                                          for d in range(self.w+1)] for a in range(self.n)},
                "hamiltonians":[v.value.as_json() for v in h[1:]],"pairs":pairs,
                "charge_translation":translation,
                "homogeneity":homogeneity,
                "leading_independence":{"log_momentum_jacobian":[[str(v) for v in row] for row in matrix],
                                        "determinant":str(independence),"nonzero":bool(independence)},
                "passed":all(p["normalized_vanishes"] for p in pairs) and all(t["passed"] for t in translation)
                         and all(t["passed"] for t in homogeneity) and bool(independence),
                "scope":"Exact finite bivariate series at this phase point; no global or all-order commutativity inference."}


def classical_receipt(*,exhaustive=False):
    settings = [((1,3,7),(2,5,11),2,2,3),((2,5,11),(3,7,13),Q(3,2),1,2)]
    if exhaustive:
        settings += [((1,3,7),(2,5,11),2,4,6),
                     ((1,3,7,13),(2,5,11,17),2,2,3),
                     ((1,3,7,13,23),(2,5,11,17,29),2,1,2)]
    reports = [ClassicalDELL(x,y,t,coordinate_order=p,momentum_order=w).replay()
               for x,y,t,p,w in settings]
    return {"passed":all(r["passed"] for r in reports),"cases":reports,
            "global_commutativity_proved":False,"self_duality_proved":False,
            "E8_double_elliptic_construction_claimed":False}


def determinant(matrix):
    rows = [list(map(Q,row)) for row in matrix]
    result = Q(1)
    for c in range(len(rows)):
        pivot = next((r for r in range(c,len(rows)) if rows[r][c]),None)
        if pivot is None:
            return Q(0)
        if pivot != c:
            rows[c],rows[pivot] = rows[pivot],rows[c]
            result = -result
        divisor = rows[c][c]
        result *= divisor
        for r in range(c+1,len(rows)):
            scale = rows[r][c]/divisor
            rows[r] = [x-scale*y for x,y in zip(rows[r],rows[c])]
    return result


def structural_receipt():
    """Replay the all-N generic independence proof at exact finite ranks.

    The proof is the elementary-symmetric Jacobian identity at P=W=0,T=1.
    A nonzero specialization proves that the rational leading determinant
    is not the zero function of parameters. Formal deformation preserves it.
    """
    from itertools import combinations
    cases = []
    for n in range(2,9):
        y = tuple(Q(2*j+1) for j in range(n))
        jacobian = []
        for a in range(1,n+1):
            row = []
            for j in range(n):
                others = [y[k] for k in range(n) if k != j]
                e = Q(0)
                for subset in combinations(others,a-1):
                    value = Q(1)
                    for v in subset:
                        value *= v
                    e += value
                row.append(y[j]*e)
            jacobian.append(row)
        expected = Q(1)
        for v in y:
            expected *= v
        for i in range(n):
            for j in range(i+1,n):
                expected *= y[i]-y[j]
        actual = determinant(jacobian)
        cases.append({"particles":n,"momenta":list(map(str,y)),"determinant":str(actual),
                      "Vandermonde_value":str(expected),"passed":actual==expected and bool(actual)})
    return {"passed":all(r["passed"] for r in cases),"finite_replays":cases,
            "all_rank_statement":"det d(e1,...,eN)/d(logY1,...,logYN)=(product Yi)*product_i<j(Yi-Yj)",
            "proof":"The ordinary Jacobian is alternating, has Vandermonde degree and leading coefficient1. Multiply column j byYj. At P=W=0,T=1 the literal current gives elementary symmetric polynomials.",
            "formal_consequence":"Generic functional independence of H1,...,H_(N-1),Y_all; H's descend and remain generically independent under the regular Y_all moment-map reduction by simultaneous X scaling.",
            "commutativity_consequence_claimed":False,"analytic_convergence_claimed":False}


def source_digests():
    import hashlib
    from pathlib import Path
    return {p.name:hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(Path(__file__).parent.glob('dell*.py'))}


def report(*,exhaustive=False,include_numerators=False):
    if type(exhaustive) is not bool or type(include_numerators) is not bool:
        raise ValueError('report flags must be Boolean')
    from .dell_normalization import (normalization_receipt,
                                      second_order_normalization_receipt,
                                      mixed_nome_normalization_receipt)
    from .dell_obstructions import obstruction_receipt
    from .dell_quantum import quantum_boundary_receipt
    from .dell_normalization_boundary import quadratic_boundary_receipt
    components = {'normalization':normalization_receipt(include_numerators=include_numerators),
                  'second-normalization':second_order_normalization_receipt(),
                  'normalization-boundary':quadratic_boundary_receipt(),
                  'mixed-normalization':mixed_nome_normalization_receipt(),
                  'obstructions':obstruction_receipt(),
                  'classical':classical_receipt(exhaustive=exhaustive),
                  'quantum':quantum_boundary_receipt(exhaustive=exhaustive),
                  'structure':structural_receipt()}
    return {'schema':'perfectjet/dell-research/1','passed':all(r['passed'] for r in components.values()),
            'source_sha256':source_digests(),'exhaustive_requested':exhaustive,'components':components,
            'scope':'Scoped symbolic and analytic theorems are separate from finite exact parameter-point replays. No worldwide priority, general self-dual DELL solution or E8 DELL model is claimed.',
            'open_gates':['Global two-nome quantum commutativity in the declared formulation',
                          'Complete deformation classification modulo canonical transformations',
                          'An explicit global position-momentum duality and comparison of distinct DELL formulations',
                          'Analytic convergence and global symplectic geometry of formal solutions',
                          'An exceptional-root E8 phase space and commuting Hamiltonian construction']}


def evaluate(params=None):
    if params is None:
        params = {}
    if not isinstance(params,dict):
        raise ValueError('DELL parameters must be an object')
    operation = params.get('operation','normalization')
    if set(params)-{'operation','exhaustive'}:
        raise ValueError('unsupported DELL request parameter')
    exhaustive = params.get('exhaustive',False)
    if type(exhaustive) is not bool:
        raise ValueError('exhaustive must be Boolean')
    if operation == 'report':
        return report(exhaustive=exhaustive)
    if operation == 'classical':
        return classical_receipt(exhaustive=exhaustive)
    if operation == 'quantum':
        from .dell_quantum import quantum_boundary_receipt
        return quantum_boundary_receipt(exhaustive=exhaustive)
    if 'exhaustive' in params:
        raise ValueError('exhaustive applies only to report, classical or quantum')
    if operation == 'normalization':
        from .dell_normalization import normalization_receipt
        return normalization_receipt()
    if operation == 'obstructions':
        from .dell_obstructions import obstruction_receipt
        return obstruction_receipt()
    if operation == 'structure':
        return structural_receipt()
    raise ValueError('unknown DELL operation')


def main(argv=None):
    import argparse,json
    from pathlib import Path
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exhaustive",action="store_true")
    parser.add_argument("--output",type=Path)
    args = parser.parse_args(argv)
    result = report(exhaustive=args.exhaustive)
    content = json.dumps(result,indent=2,sort_keys=True)+"\n"
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(content)
    else:
        print(content,end="")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
