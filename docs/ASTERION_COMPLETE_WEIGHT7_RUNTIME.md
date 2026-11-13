# Complete weight-seven Asterion runtime

The installed package exposes the level-one E8 arc-to-Li kernel over
characteristic zero through `python -m perfectjet.complete_weight_seven`.
The report includes all 19 quartic source sectors, the exact irreducible
multiplicities, the lower-weight null-lift dependencies and the hashes of
the replay inputs and outputs.

| Current length | Li degree | Kernel dimension |
| --- | --- | ---: |
| 3 | 4 | 181,753 |
| 4 | 3 | 965,124 |
| All lengths | | 1,146,877 |

The complete character is
`1 + 3·248 + 3·3875 + 2·30380 + 2·147250 + 779247`.
The quartic image is `30380 + 6696000`. The quotient by derivatives
and products of lower-weight kernel classes has dimension zero at weight
seven. The theorem concerns this weight over characteristic zero and relies
on the representation-theoretic and VOA inputs documented in the
[mathematical audit](ASTERION_COMPLETE_WEIGHT7_AUDIT.md).

`ProjectedLatticeE8VOA4` extends the existing exact output projection
with four root currents. It uses the inherited Heisenberg commutation,
cocycle conventions and scaling. For the 30380 sector the projection of
all thirteen lower-length highest columns has rank seven. Adding the
quartic witness increases the rank to eight and certifies an associated-graded
image copy. Old products account for the other arc copy.

Reading the installed report verifies source and resource digests and
checks the character arithmetic against the cubic report. The dedicated
replay restores the pinned research inputs, replaces its runtime snapshot
with a copy of the maintained package and regenerates the lattice outputs,
source null lifts, cutoff, sparse spans and characters. The historical
`source_commit` fields inside some research receipts describe their
original provenance. The runtime report binds the exact source bytes used
by the current replay.

```sh
PYTHONPATH=src python -m scripts.verify_complete_weight_seven --output /tmp/perfectjet-complete-replay
python scripts/check_installed_weight_seven.py
```

Use the replay command with `--write` after the cubic and Asterion
publication receipts have been regenerated and checked. It writes the
installed report after the full replay and focused tests exit successfully.
The installed cubic entry point remains `python -m perfectjet.weight_seven`.
The v0.22.0rc1 candidate refers to that cubic result.

The evaluator lives in `perfectjet.complete_weight_seven_projection`.
The complete report adds that module explicitly to its mathematical source
inventory. Existing cubic and publication reports still bind the full
`asterion*.py` set. The replay creates a temporary compatibility import
for the pinned research scripts, then checks the maintained source and
primitive resource bytes against the replay copy.
