"""Collision/Pell research through the CLI, JSON API, and Math Lab."""
from __future__ import annotations

import argparse
from fractions import Fraction
import json
from pathlib import Path

from .collision_zeta import (
    CONDUCTOR_TWO, RationalEulerFactor, conductor_two_report, integer, pell_pair,
)


def json_value(value):
    # Chunked conversion preserves permitted exact outputs on Python 3.11+
    # without changing the process-wide integer/string security setting.
    remaining = [750000]
    def decimal(number):
        if number.bit_length() > 262144:
            raise ValueError('integer exceeds the JSON output-bit budget; use the Python API')
        remaining[0] -= max(1, number.bit_length())
        if remaining[0] < 0:
            raise ValueError('combined exact integers exceed the JSON output budget')
        if abs(number).bit_length() < 12000:
            return str(number)
        sign = '-' if number < 0 else ''
        number = abs(number)
        chunks = []
        base = 10**1000
        while number:
            number, remainder = divmod(number, base)
            chunks.append(remainder)
        return sign+str(chunks[-1])+''.join(f'{c:01000d}' for c in reversed(chunks[:-1]))
    def convert(item):
        if isinstance(item, Fraction):
            return decimal(item.numerator)+'/'+decimal(item.denominator)
        if isinstance(item, dict):
            return {k: convert(v) for k, v in item.items()}
        if isinstance(item, (tuple, list)):
            return [convert(v) for v in item]
        # Keep all exact arithmetic digits across JavaScript consumers.
        if isinstance(item, int) and not isinstance(item, bool) and abs(item) > 2**53-1:
            return decimal(item)
        return item
    return convert(value)


def _denominator(period, power):
    out = (1,)
    for _ in range(power):
        result = list(out)+( [0]*period)
        for i, v in enumerate(out):
            result[i+period] -= v
        out = tuple(result)
    return out


SHAPES = {
    'report': {'order', 'index', 'limit'},
    'pell': {'index', 'modulus', 'max_bits'},
    'extract': {'order', 'numerator', 'denominator', 'degree_budget'},
    'norm': {'conductor', 'order'},
    'projection': {'conductor', 'order'},
    'population': {'conductor', 'exponent', 'residue', 'rank', 'factorization'},
    'four': {'a', 'b', 'u', 'v', 'w'},
    'constants': {'prime_cutoff', 's'},
    'approximate': {'X', 'sigma', 'prime_cutoff', 'bits', 'include_exact'},
    'classify': {'max_conductor'},
}


def evaluate(request=None):
    request = {} if request is None else request
    if not isinstance(request, dict):
        raise ValueError('collision request must be an object')
    operation = request.get('operation', 'report')
    if not isinstance(operation,str) or operation not in SHAPES:
        raise ValueError('unknown collision operation')
    unknown = set(request)-SHAPES[operation]-{'operation'}
    if unknown:
        raise ValueError('unsupported collision fields: '+', '.join(sorted(unknown)))
    p = {k:v for k,v in request.items() if k != 'operation'}
    if operation == 'report':
        out = conductor_two_report(p.get('order', 24), p.get('index', 10**100), p.get('limit', 1000))
    elif operation == 'pell':
        n = integer(p.get('index', 100), 'index')
        modulus = p.get('modulus')
        if modulus is not None:
            modulus = integer(modulus, 'modulus', 2)
        u,v = pell_pair(n, modulus, p.get('max_bits', 32768))
        norm = u*u-2*v*v
        out = {'index': str(n), 'unit_power': {'rational': u, 'sqrt_two': v},
               'pell_lucas': (2*u)%modulus if modulus else 2*u,
               'modulus': modulus, 'norm_verified': (norm-(-1)**n)%modulus == 0 if modulus else norm == (-1)**n,
               'scope': 'Exact quadratic-unit arithmetic; modular values do not reconstruct the full integer.'}
    elif operation == 'extract':
        factor = RationalEulerFactor(p.get('numerator', CONDUCTOR_TWO.numerator), p.get('denominator', CONDUCTOR_TWO.denominator))
        out = factor.extract(p.get('order', 4), p.get('degree_budget', 20000))
    elif operation == 'norm':
        from .collision_norm import collision_norm
        norm = collision_norm(integer(p.get('conductor', 2), 'conductor', 1))
        out = norm.report()
        if 'order' in p:
            out['formal_zeta_exponents'] = RationalEulerFactor(norm.numerator, _denominator(norm.denominator_period, norm.denominator_power)).zeta_exponents(p['order'])[1:]
    elif operation == 'projection':
        from .collision_projection import collision_projection
        projection = collision_projection(integer(p.get('conductor', 4), 'conductor', 1))
        out = projection.report()
        if 'order' in p:
            out['formal_zeta_exponents'] = RationalEulerFactor(projection.numerator, _denominator(projection.conductor, 2)).zeta_exponents(p['order'])[1:]
    elif operation == 'population':
        from .collision_population import collision_population_receipt, FactorPairResiduePopulation
        conductor = integer(p.get('conductor', 2), 'conductor', 1)
        residue = integer(p.get('residue', 0), 'residue')
        rank = integer(p.get('rank', 0), 'rank')
        if 'factorization' not in p:
            out = collision_population_receipt(conductor, integer(p.get('exponent', 10**100), 'exponent'), residue, rank)
        else:
            if 'exponent' in p:
                raise ValueError('choose exponent splits or a supplied factorization')
            factors = p['factorization']
            if isinstance(factors, dict):
                factors = list(factors.items())
            if not isinstance(factors, list) or len(factors) > 64:
                raise ValueError('factorization must contain at most 64 prime/exponent pairs')
            factors = [(integer(a, 'prime', 2), integer(b, 'exponent', 1)) for a,b in factors]
            population = FactorPairResiduePopulation(factors, conductor, residue)
            total = population.count()
            selected = population.unrank(rank) if total else None
            if not total and rank:
                raise ValueError('empty population has no requested rank')
            out = {'conductor': conductor, 'residue': residue%conductor,
                   'factorization': population.factorization, 'residue_histogram': population.histogram(),
                   'count': total, 'rank': rank if total else None, 'left_exponents': selected,
                   'rank_replayed': population.rank(selected) == rank if total else None,
                   'scope': 'Actual ordered divisor pairs conditioned on total kappa modulo L; supplied primes are exactly verified within a trial budget.'}
            if total:
                try:
                    out['original_pair'] = population.pair(rank)
                except ValueError:
                    out['original_pair'] = None
                    out['original_pair_note'] = 'Exponent representation retained; integer materialization exceeds the output-bit budget.'
            if conductor == 2:
                out['signed_parity_total'] = population.parity_signed_total()
    elif operation == 'four':
        from .collision_four import collision_four_forward_vectors, collision_four_inverse_vectors, receipt
        def vector(value,name):
            raw = value if isinstance(value,list) else [value]
            if len(raw)>4096:
                raise ValueError('exponent vector exceeds the prime-coordinate budget')
            return tuple(integer(x,name) for x in raw)
        if {'a','b'} & p.keys():
            if set(p) != {'a','b'}:
                raise ValueError('forward transport requires exactly a and b')
            a,b = vector(p['a'],'a'),vector(p['b'],'b')
            u,v,w = collision_four_forward_vectors(a,b)
        elif p:
            if set(p) != {'u','v','w'}:
                raise ValueError('inverse transport requires exactly u, v and w')
            u,v,w = (vector(p[k],k) for k in ('u','v','w'))
            a,b = collision_four_inverse_vectors(u,v,w)
        else:
            a,b = (4,1),(2,4)
            u,v,w = collision_four_forward_vectors(a,b)
        out = dict(receipt(),a=a,b=b,u=u,v=v,w=w,
                   roundtrip_verified=collision_four_inverse_vectors(u,v,w)==(a,b),
                   size_verified=all(x+y==r+s+4*t for x,y,r,s,t in zip(a,b,u,v,w)))
    elif operation == 'approximate':
        from .collision_asymptotic import counting_certificate
        if 'X' not in p:
            raise ValueError('approximate requires X')
        out = counting_certificate(**p)
    elif operation == 'constants':
        from .collision_constants import constants_receipt
        out = constants_receipt(integer(p.get('prime_cutoff', 100), 'prime_cutoff', 2), integer(p.get('s', 2), 's', 2))
    else:
        from .collision_norm import norm_classification_theorem
        from .collision_projection import projection_classification_theorem
        from .collision_projection import collision_projection
        maximum = integer(p.get('max_conductor', 16), 'max_conductor', 1, 64)
        out = {'norm_theorem': norm_classification_theorem(), 'prime_local_projection_theorem': projection_classification_theorem(),
               'projection_checkpoints': [collision_projection(n).report() for n in range(1,maximum+1)],
               'scope': 'Symbolic all-conductor proofs; bounded exact checkpoints are separate from those proofs.'}
    return json_value(out)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', nargs='?', choices=SHAPES, default='report')
    parser.add_argument('--request', type=Path, help='JSON request; overrides operation and numeric flags')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--conductor', type=int)
    parser.add_argument('--index')
    parser.add_argument('--exponent')
    parser.add_argument('--residue', type=int)
    parser.add_argument('--rank')
    parser.add_argument('--order', type=int)
    parser.add_argument('--limit', type=int)
    parser.add_argument('--modulus')
    parser.add_argument('--prime-cutoff', type=int)
    parser.add_argument('--s', type=int)
    parser.add_argument('--x', dest='X', help='exact rational X for the finite-input counting certificate')
    parser.add_argument('--sigma', help='rational sigma in (1/2,1), or auto')
    parser.add_argument('--bits', type=int)
    parser.add_argument('--include-exact', action='store_true', default=None)
    parser.add_argument('--max-conductor', type=int)
    parser.add_argument('--factorization', type=json.loads)
    for field in ('a','b','u','v','w'):
        parser.add_argument('--'+field,type=json.loads)
    args = parser.parse_args(argv)
    if args.request:
        request = json.loads(args.request.read_text(encoding='utf-8'))
    else:
        request = {key: value for key,value in vars(args).items() if key not in ('request','output') and value is not None}
    try:
        content = json.dumps(evaluate(request), indent=2, allow_nan=False)+'\n'
    except (ValueError, TypeError, IndexError) as error:
        parser.error(str(error))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(content, encoding='utf-8')
    else:
        print(content, end='')


if __name__ == '__main__':
    main()
