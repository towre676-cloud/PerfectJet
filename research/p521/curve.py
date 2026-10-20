"""Exact public P-521 arithmetic and independently replayable seed provenance.

Parameters: NIST SP 800-186, secp521r1. No secret keys are inputs.
"""
from datetime import datetime, timezone

P = (1 << 521) - 1
A = P - 3
B = int('0051953eb9618e1c9a1f929a21a0b68540eea2da725b99b315f3b8b489918ef109'
        'e156193951ec7e937b1652c0bd3bb1bf073573df883d2c34f1ef451fd46b503f00', 16)
GX = int('00c6858e06b70404e9cd9e3ecb662395b4429c648139053fb521f828af606b4d3d'
         'baa14b5e77efe75928fe1dc127a2ffa8de3348b3c1856a429bf97e7e31c2e5bd66', 16)
GY = int('011839296a789a3bc0045c8a5fb42c7d1bd998f54449579b446817afbd17273e662c'
         '97ee72995ef42640c550b9013fad0761353c7086a272c24088be94769fd16650', 16)
N = int('01ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'
        'fa51868783bf2f966b7fcc0148f709a5d03bb5c9b8899c47aebb6fb71e91386409', 16)
G = (GX, GY)
SEED = 'D09E8800291CB85396CC6717393284AAA0DA64BA'
TIMESTAMP = 871002724
SEED_CANDIDATE = 1136


def on_curve(point):
    if point is None:
        return True
    x, y = point
    return 0 <= x < P and 0 <= y < P and (y*y - x*x*x - A*x - B) % P == 0


def add(left, right):
    if left is None:
        return right
    if right is None:
        return left
    x, y = left
    u, v = right
    if x == u and (y + v) % P == 0:
        return None
    slope = ((3*x*x + A) * pow(2*y, -1, P) if left == right else
             (v-y) * pow(u-x, -1, P)) % P
    nx = (slope*slope - x - u) % P
    return nx, (slope*(x-nx)-y) % P


def multiply(scalar, point=G):
    if scalar < 0:
        return multiply(-scalar, (point[0], -point[1] % P))
    answer = None
    while scalar:
        if scalar & 1:
            answer = add(answer, point)
        point = add(point, point)
        scalar >>= 1
    return answer


def lucas_lehmer(exponent=521):
    """For prime exponent 521, this is the exact Lucas-Lehmer primality test."""
    if exponent != 521:
        raise ValueError('This research contract fixes the known prime exponent 521')
    state, modulus = 4, (1 << exponent)-1
    for _ in range(exponent-2):
        state = (state*state-2) % modulus
    return state == 0


def seed_provenance():
    state = (TIMESTAMP << 16) | 0x330E
    candidate = bytearray()
    for i in range(20*SEED_CANDIDATE):
        state = (0x5DEECE66D * state + 11) % (1 << 48)
        if i >= 20*(SEED_CANDIDATE-1):
            candidate.append(state >> 40)
    generated = candidate.hex().upper()
    return {'timestamp': TIMESTAMP,
            'datetime_utc': datetime.fromtimestamp(TIMESTAMP, timezone.utc).isoformat(),
            'candidate_index_1_based': SEED_CANDIDATE, 'seed': generated,
            'matches_standard': generated == SEED,
            'attribution': 'Anthropic, 2026-10-16; reproduced here, not a new discovery'}


def arithmetic_checks():
    return {'field_modulus_is_prime_lucas_lehmer': lucas_lehmer(),
            'base_point_on_curve': on_curve(G),
            'standard_order_annihilates_base_point': multiply(N) is None,
            'base_point_nonzero': G is not None,
            'seed_provenance': seed_provenance()}
