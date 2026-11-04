"""Recompute the two previously missing weight-seven length-three sectors.

Writes existing-format explicit representatives, exact derivative-span identities
and a source-pinned receipt. No length-four or all-weight claim is made.
"""
import argparse
import json
from pathlib import Path
import time

from perfectjet.asterion import json_ready, source_digests
from perfectjet.asterion_kernel_characters import (
    SYM3, SCHUR21, EXTERIOR3, length_three_character,
    s3_polynomial_multiplicities,
)
from perfectjet.asterion_primitives import (
    ZERO, THETA, JetAlgebra, LatticeE8VOA, _sector_record,
    decode_polynomial, encode_polynomial, exact_rank, length_three_sector,
    load_certificates, solve_combination,
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'results/asterion-primitives'


def calculate(dimension, jets, lattice):
    target = ZERO if dimension == 1 else THETA
    result = length_three_sector(jets, lattice, target, 7)
    record = _sector_record(result, f'w7-{dimension}', dimension)
    schur_multiplicities = s3_polynomial_multiplicities(4)
    ambient = sum(m * c.get(dimension, 0) for m, c in zip(
        schur_multiplicities, (SYM3, SCHUR21, EXTERIOR3)))
    assert ambient == record['polynomial_highest_vectors']
    assert record['arc_multiplicity'] == length_three_character(4)[dimension]
    record['ambient_schur_reconstruction'] = {
        'S3_multiplicities': list(schur_multiplicities),
        'ambient_highest_multiplicity': ambient,
        'matches_direct_highest_elimination': True,
    }
    if dimension == 248:
        source = load_certificates()['sectors']['w5-248']['representatives'][0]
        derived = jets.derivative(jets.derivative(decode_polynomial(source['symbol'])))
        correction = jets.derivative(jets.derivative(decode_polynomial(source['correction'])))
        symbols = [r['symbol'] for r in result['representatives']]
        ideal = result['ideal_vectors']
        coords = solve_combination(derived, ideal + symbols)
        reverse = [solve_combination(s, ideal + [derived]) for s in symbols]
        record['derivative_identification'] = {
            'source': 'w5-248', 'derivative_order': 2,
            'derivative_in_ideal_plus_kernel': coords,
            'kernel_in_ideal_plus_derivative': reverse,
            'derivative_nonzero_modulo_ideal': exact_rank(ideal + [derived]) == exact_rank(ideal) + 1,
            'derivative_symbol': encode_polynomial(derived),
            'derivative_correction': encode_polynomial(correction),
        }
        assert coords is not None
        assert record['derivative_identification']['derivative_nonzero_modulo_ideal']
        # D commutes with PBW symmetrization and preserves the affine null module.
        record['equals_derivative_subspace'] = all(c is not None for c in reverse)
        record['new_primitive_multiplicity'] = record['kernel_multiplicity'] - 1
    else:
        record['new_primitive_multiplicity'] = record['kernel_multiplicity']
    record['source_sha256'] = source_digests()
    record['scope'] = 'Weight seven, length three, this highest-weight sector only.'
    return json_ready(record)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--only', nargs='+', type=int, choices=(1, 248), default=[1, 248])
    args = parser.parse_args()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    jets = JetAlgebra()
    lattice = LatticeE8VOA(jets)
    for dimension in args.only:
        start = time.monotonic()
        print(f'Starting w7-{dimension}', flush=True)
        record = calculate(dimension, jets, lattice)
        (OUTPUT / f'w7-{dimension}.json').write_text(
            json.dumps(record, indent=2, sort_keys=True) + '\n', encoding='utf-8')
        print(json.dumps({k: record[k] for k in (
            'label', 'polynomial_highest_vectors', 'ideal_highest_rank',
            'arc_multiplicity', 'lattice_null_dimension', 'kernel_multiplicity',
            'new_primitive_multiplicity')}), flush=True)
        print(f'Elapsed {time.monotonic()-start:.1f}s', flush=True)
        lattice.clear_cache()


if __name__ == '__main__':
    main()
