# Quick start

PerfectJet is a Python research library plus a large mathematical atlas. It does not require NumPy, SymPy, Sage, or a GPU for its canonical checks.

On Linux/macOS, run `python -m pip install -e .` and then `perfectjet report`. On Windows PowerShell:

```powershell
cd "$env:USERPROFILE\Downloads\PerfectJet"
py -m pip install -e .
perfectjet report --output results\my-replay.json
py -m unittest discover -s tests -v
```

If installing is inconvenient:

```powershell
$env:PYTHONPATH = "src"
py -m perfectjet.cli report --output results\my-replay.json
```

The report checks selected identities and populations. It includes the finite molecular partner census, cubic field coordinates, collision recurrence receipts, a floating PSG root, hidden-state detection and repair, exact feature closure/failure, a small selection population, and a partial-machine quotient. Its limitation field states what is not imported or formally proved.

`perfectjet collision --conductor 7 --index 100000000000000000000` returns the coefficient as rational coordinates in Q[zeta_7]. Coordinates are not decimal magnitudes. `perfectjet core-field` returns exact field elements and zero-identity flags. `perfectjet partners` gives kernel and active dimensions, making self-commuting partners visible rather than counting them as active interactions.

`perfectjet lattice` shows a system that is solvable over Q but not over Z, with its certificate row, and an unsaturated lattice with its index and witness. `perfectjet realization` recovers the two-state Fibonacci model and a three-state factor counter from Hankel blocks, confirms them on longer held-out words, and reports a coarsest exact lumping.

`perfectjet loci` prints the exact parameter loci of the C3 partner family for degrees 3 to 12, including the rediscovered 40/7. `perfectjet surface` divides the two-parameter sextic family into cells of constant rank for degrees 3 to 12. It lists rational exceptional points such as (16,-9), where the sextic is (x-y)^4(x^2+4xy+y^2). `perfectjet strata` refines those cells by active capacity: every stratum reports kernel, active and commuting dimensions, whether the sextic has a repeated root there, and a partner replayed with exact transvectants at a rational point. `perfectjet readout` shows a readout that a player's attempts cannot identify, the two-fit witness, the two conditions that would identify it, and the variance reduction of each candidate. `perfectjet decisions` stops refinement once a choice is settled and replays the evolution-defect split. `perfectjet invariants` computes the Clebsch invariants of the exceptional sextics, groups GL2-equivalent points, checks det L_3=(A^2-B/6)/16 and the quartic covariant partner on random sextics, and finds the invariant relation behind each drop curve. `perfectjet quadratic` compiles n^2+7=2y^2 and the square-triangular equation into Pell populations, lists their orbits and admissible positions, and computes a 766-digit hit at index 1000, replayed exactly. `perfectjet engine` runs every adapter of the unified report. `perfectjet sieve` runs the adaptive power-residue sieve on the Pell7 equation and on n^3+3, and checks both against brute force.

For source-checkout use, `perfectjet atlas` emits the equation registry. The registry is intentionally not treated as an executable theorem database: every entry has an evidence status and assumptions.

Read the monograph for cross-project mathematics. Read the coverage map to locate a named program. Use the source index to distinguish original extracted text from the canonical corrected interpretation.

## Real NFL research replay

Install the optional scouting environment with `python -m pip install -e '.[scouting]'`. The original nine-file input has already been recovered and verified for this research run. Its raw files and individual derived outputs remain private; `results/real-nfl/preparation.json` records the source and extraction audit. Reuse a locally available copy rather than attempting another sign-in.

Prepare a fresh owned checkpoint with `python scripts/prepare_official_bridge_data.py --data /absolute/private/nine-files --private-output /absolute/private/checkpoint --audit-output /absolute/private/preparation.json`. Evaluate it with `python scripts/run_recovered_official.py --checkpoint /absolute/private/checkpoint/official_bridge_data.pkl --receipt /absolute/private/preparation.json --private-output /absolute/private/results.json --output /absolute/aggregate.json`. Add `--without-ngs`, `--front-drills`, `--kind burst` or `--refits 16` for the recorded sensitivities. Checkpoint and extractor hashes must match. Pickle is only for this freshly generated, owned checkpoint.

Read [the real-data chapter](nfl/REAL_DATA.md) before interpreting metrics. The public cohort and external tracking replay commands are in [the public benchmark](../research/public_nfl/REPORT.md) and [external tracking report](nfl/EXTERNAL_TRACKING.md). Their exact source snapshots, coverage exclusions and comparator definitions are part of the result.

## Stopped-flow measurement and scouting

The 0.14 study separates an unseen launch from observed rolling acceleration. Read `docs/nfl/STOPPED_FLOW.md`, then open `notebooks/PerfectJet_Stopped_Flow.ipynb`. It replays exact identities and the retained aggregate results without restricted input. The source-complete notebook also reconstructs the runnable package; executing the official experiments requires the already-owned raw data or its provenance-checked private checkpoint. Full command lines are in the study chapter.
