"""Recompute inherited cubic rank bounds; preserve historical source bindings.

Only output images are projected. Quotient image ranks account for possible
lower-length null directions. Full source null lifts are replayed by the
exhaustive frontier verifier, not inferred from projected zeroes.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
from perfectjet.asterion import json_ready, source_digests
from perfectjet import asterion_primitives as p
from perfectjet.asterion_lattice_projection import ProjectedLatticeE8VOA
from perfectjet.asterion_kernel_characters import length_three_character
from verify_asterion_w7_rank_certificates import vector_rank

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT/'results/asterion-primitives'
TARGETS = list(p.WEIGHT_SEVEN_SECTORS)+[('w7-3875', p.LAMBDA_3875, 3875)]


def replay():
    jets = p.JetAlgebra()
    lattice = ProjectedLatticeE8VOA(jets)
    stored = p.load_certificates()['sectors']
    history = json.loads((FOLDER/'length-three-boundary.json').read_text())
    characters = length_three_character(4)
    rows = {}
    for label, target, dimension in TARGETS:
        print('Starting '+label, flush=True)
        top, count = jets.highest_vectors(p.jet_shapes(3, 4), target)
        lower = []
        for length in (2, 1):
            lower.extend(jets.highest_vectors(p.jet_shapes(length, 7-length), target)[0])
        columns = top+lower
        if not all(jets.is_highest(c) for c in columns) or vector_rank(columns) != len(columns):
            raise ArithmeticError('invalid highest basis: '+label)
        ideal = p.ideal_highest_images(jets, p.g_tensor_i_highest(jets, target), 7)
        ideal_rank = vector_rank(ideal)
        if len(top)-ideal_rank != characters[dimension]:
            raise ArithmeticError('highest basis/character mismatch: '+label)
        images = [lattice.symmetric_lift(c) for c in columns]
        rank = vector_rank(images)
        lower_rank = vector_rank(images[len(top):])
        old = history['sectors'][label]
        known = old['kernel_multiplicity']
        source_label = None
        if known:
            source_label = 'w6-'+str(dimension)
            source = stored[source_label]['representatives'][0]
            symbol = jets.derivative(p.decode_polynomial(source['symbol']))
            correction = jets.derivative(p.decode_polynomial(source['correction']))
            if vector_rank(ideal+[symbol]) != ideal_rank+1:
                raise ArithmeticError('derivative nonmembership failed: '+label)
            if lattice.symmetric_lift(symbol) != {k:-v for k,v in lattice.symmetric_lift(correction).items()}:
                raise ArithmeticError('projected translated null failed: '+label)
        if len(top)-rank+lower_rank-ideal_rank != known:
            raise ArithmeticError('projected bound not attained: '+label)
        if (old['arc_multiplicity'],old['ideal_highest_rank']) != (len(top)-ideal_rank,ideal_rank):
            raise ArithmeticError('historical sector differs: '+label)
        rows[label] = {'weyl_dimension':dimension, 'polynomial_highest_vectors':len(top),
            'top_monomial_columns':count, 'lower_length_highest_vectors':len(lower),
            'arc_multiplicity':len(top)-ideal_rank, 'ideal_highest_rank':ideal_rank,
            'projected_rank_Q':rank, 'projected_lower_rank_Q':lower_rank,
            'kernel_multiplicity':known, 'derivative_source':source_label,
            'columns':[p.encode_polynomial(c) for c in columns],
            'images':[[[list(k[0]),[list(x) for x in k[1]],str(z)] for k,z in sorted(im.items())] for im in images]}
        print(json.dumps({k:v for k,v in rows[label].items() if k not in ('columns','images')}),flush=True)
        lattice.clear_cache()
    return json_ready({'schema':'perfectjet/asterion-w7-prior-replay/1',
        'source_sha256':source_digests(), 'sectors':rows,
        'historical_receipt_sha256':hashlib.sha256((FOLDER/'length-three-boundary.json').read_bytes()).hexdigest(),
        'scope':'Seven inherited cubic sectors; exact projected quotient ranks and translated nonmembership. Full source nulls replayed separately; quartic and longer lengths remain open.'})


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    raw=gzip.compress((json.dumps(replay(),indent=2,sort_keys=True)+'\n').encode(),mtime=0)
    raw=raw[:9]+b'\xff'+raw[10:]
    path=FOLDER/'w7-prior-sectors-replay.json.gz'
    if args.check:
        if path.read_bytes()!=raw:raise ValueError('stale prior-sector replay')
    else:path.write_bytes(raw)


if __name__=='__main__':main()
