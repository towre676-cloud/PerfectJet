"""Forward positive controls from the six previously explained base points.

The historical reconstruction is credited to Anthropic, 16 October 2026.
This implementation includes FreeLIP's original rejection sampling.
"""
M = (1 << 107) - 1
A = pow(3, 121, M)
RADIX = 1 << 26
P192 = (1 << 192) - (1 << 64) - 1
P239 = (1 << 239) - (1 << 143) - (1 << 95) + (1 << 47) - 1

CASES = (
    ('P-192', 20000, P192,
     0x64210519e59c80e70fa7e9ab72243049feb8deecc146b9b1,
     0x188da80eb03090f67cbf20eb43a18800f4ff0afd82ff1012),
    ('prime239v1', 20420, P239,
     0x6b016c3bdcf18941d0d654921475ca71a9db2fb27d1d37796185c2942c0a,
     0xffa963cdca8816ccc33b8642bedf905c3d358573d3f27fbbd3b3cb9aaaf),
    ('prime239v2', 20507, P239,
     0x617fab6832576cbbfed50d99f0249c3fee58b94ba0038c7ae84c8c832f2c,
     0x38af09d98727705120c921bb5e9e26296a3cdcf2f35757a0eafd87b830e7),
    ('prime239v3', 20509, P239,
     0x255705fa2a306654b1f4cb03d6a750a30c250102d4988717d9ba15ab6d3e,
     0x6768ae8e18bb92cfcf005c949aa2c6d94853d0e660bbf854b1c9505fe95a),
    ('prime192v2', 20512, P192,
     0xcc22d6dfb95c6b25e49c0d6364a4e5980c393aa21668d953,
     0xeea2bae7e1497842f2de7769cfe9c989c072ad696f48034a),
    ('prime192v3', 20517, P192,
     0x22123dc2395a05caa7423daeccc94760a7d462256bd56916,
     0x7d29778100c65a1da1783716588dce2b8b4aee8e228f1896),
)


def reconstruct(seed, p, coefficient, max_candidates=1000):
    state, rejected = seed, 0
    threshold = M - M % RADIX

    def limb():
        nonlocal state, rejected
        while True:
            state = A * state % M
            if state < threshold:
                return state % RADIX
            rejected += 1

    for _ in range(7):
        limb()
    limbs_per_coordinate = (p.bit_length()+25)//26 + 1
    for candidate in range(1, max_candidates+1):
        raw = 0
        for _ in range(limbs_per_coordinate):
            raw = raw*RADIX + limb()
        x = raw % p
        rhs = (x*x*x-3*x+coefficient) % p
        if pow(rhs, (p-1)//2, p) in (0, 1):
            return {'x': x, 'candidate_index': candidate, 'rejected_draws': rejected}
    raise RuntimeError('Declared positive-control candidate budget exhausted')


def run_controls():
    results = []
    for name, seed, p, coefficient, expected in CASES:
        result = reconstruct(seed, p, coefficient)
        results.append({'curve': name, 'seed': seed, 'x': hex(result['x']),
                        'matches_published_x': result['x'] == expected,
                        'candidate_index': result['candidate_index'],
                        'rejected_draws': result['rejected_draws']})
    return {'attribution': 'Previously explained by Anthropic; independently implemented replay',
            'controls': results, 'all_pass': all(x['matches_published_x'] for x in results)}
