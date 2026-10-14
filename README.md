# PerfectJet

**Exact arithmetic, predictive state, and navigable populations in one research atlas.**

PerfectJet brings together the PerfectPower, DynaComp, PSG, SOE, WIND, IMP, Morphonic, conductor, Shadow–Core, and Weyl-exactness programs. Its central question is: what smaller representation preserves the answer we need, and what witness tells us when it fails?

The repository contains a [master monograph](docs/MONOGRAPH.md), a [complete topic map](docs/COVERAGE_MAP.md), a [384-equation atlas](docs/EQUATION_ATLAS.md), preserved [archival sources](archive/README.md), and a dependency-free Python core. Historical reports and open proposals remain labeled. No new Lean proof or complete imported upstream solver is claimed.

## Run the mathematics

Requires Python 3.10 or newer. From this directory:

```bash
python -m pip install -e .
perfectjet report --output results/replay.json
perfectjet partners
perfectjet collision --conductor 7 --index 100000000000000000000000000000000000000000000000000
perfectjet core-field
perfectjet psg
perfectjet lattice
perfectjet realization
perfectjet loci
perfectjet surface
perfectjet strata
perfectjet readout
perfectjet decisions
perfectjet engine
perfectjet invariants
perfectjet quadratic
perfectjet deformation
perfectjet sieve
perfectjet nfl --synthetic --seed 1 --out results/nfl-synthetic
python -m unittest discover -s tests -v
```

Without installation, set `PYTHONPATH=src` and use `python -m perfectjet.cli report`. [Windows instructions](docs/QUICKSTART.md) include PowerShell commands.

The runnable core covers rational observability and hidden witnesses, finite partial-machine equivalence, polynomial feature closure, weighted quotient replay, exact selection counts/rank/unrank/ties, corrected energy balances, finite jets, transvectant partner dimensions, exact cubic-field identities, cyclotomic collision coefficients at very large indices, integer lattices (Smith and Hermite forms, integer solvability with infeasibility certificates, integer kernels, saturation index), minimal single- and multi-output word-Hankel realizations with held-out witnesses, coarsest exact weighted lumping, exact rank loci in one or several parameters (comprehensive Gaussian elimination with an exact Groebner engine), an adaptive local sieve for perfect-power hits, active partner strata with replayed partners, exact readout identifiability with repair and value of information, certified decisions, and an adaptive representation engine whose adapters all return one representation-and-obstruction report. A solution-carrying compiler turns k y^2 = a n^2 + b n + c into a complete Pell population with reconstruction maps and exact remote-index queries. Clebsch invariants explain the partner strata: every binary sextic has det L_3=(A^2-B/6)/16 and the correction-free quartic partner (f,f)_4, and on A^2=25B/96 an explicit covariant is a degree-12 partner. These identities are certified by exact grids on a slice with a dense GL2-orbit. The PSG root calculation is explicitly numerical.

## Combine scouting

The [0.12 math bridges](docs/nfl/MATH_BRIDGES.md) connect causal Combine histories to NFL movement readouts and a player-cross-fitted get-off decoder. Finite-horizon delay states transfer physical forecasts; the decoder trains on out-of-player movement predictions. Frozen fitted loadings feed exact joint measurement-package allocation, with correlated attempt noise, robust loading hypotheses and a rationalization regret bound. Run `perfectjet math-bridges --output results/bridge-receipt.json` for executed analytic/synthetic receipts and `perfectjet nfl-bridges --help` for the official experiment. The [source-complete bridge notebook](notebooks/PerfectJet_Math_Bridges.ipynb) embeds the current source; real-data execution receipts are recorded separately. The original nine-file input has now been recovered and verified. No incremental scouting advantage is established.

The [0.11 motor-transfer study](docs/nfl/MOTOR_TRANSFER.md) tests a post-onset half-second Combine readout against snap-to-LOS NFL get-off, with independent-attempt reliability, uncertainty-integrated prediction and complete nested player validation. Install `.[scouting]`, then run `perfectjet nfl-burst --data DIR --out PRIVATE_DIR --verify-known-hashes --refits 64`. Its [standalone Kaggle notebook](notebooks/PerfectJet_Motor_Transfer.ipynb) is explicitly unexecuted until official raw inputs are available. The complete [prior NFL research](research/nfl_bdb_2027/README.md), including failed models, nine notebooks and Git history, is preserved. No new real-data gain is claimed. Exact demand ranks, inner reconstruction, bootstrap grouping and chronology were corrected.

`perfectjet nfl` runs the Combine scouting pipeline in `src/perfectjet/applications/nfl_scouting`: turn events with full lineage, an exact identifiability gate for each athlete's readout, leakage-checked NFL targets, athlete-grouped temporal validation against a conventional baseline, a frozen shortlist rule, and scouting cards. Point it at real data with `--data DIR --mapping mapping.json` ([data contract](docs/nfl/DATA_CONTRACT.md)); the [protocol](docs/nfl/PROTOCOL.md) fixes every analysis choice in advance. The `--synthetic` mode plants or withholds a signal to test the pipeline itself and is never evidence about football. No real-data scouting advantage is claimed.

## Read and explore

[Quick start](docs/QUICKSTART.md) explains the commands. [Architecture](docs/ARCHITECTURE.md) shows how the modules connect. [Corrections and limits](docs/chapters/23_status_corrections_and_frontiers.md) separates current checks from historical claims and missing sources. [Examples](examples/walkthrough.py) connect arithmetic populations, observations, and closure defects.

PerfectJet complements [PerfectPower](https://github.com/towre676-cloud/perfectpower) and [DynaComp](https://github.com/towre676-cloud/DynaComp). Their inspected revisions are recorded in [upstream references](integrations/upstreams.json). This repository does not automatically change their code, sites, or applications.

## Download

The complete [v0.13.1 package parts](releases/PerfectJet-v0.13.1.parts.json) contains source, tests, documentation, registry, retained results, and extracted archives. GitHub's [source archive](https://github.com/towre676-cloud/PerfectJet/archive/refs/heads/main.zip) always follows `main`. The [monograph](docs/MONOGRAPH.md) is readable directly on GitHub.

## Reproduce the retained release

```bash
python scripts/build_chapters.py
python scripts/build_corpus.py
python scripts/build_topics.py
python scripts/check_coverage.py
```

The release record states local test results separately from GitHub Actions status. The source provenance describes which documents are complete textual extractions and which are selected excerpts.

The [real-data evidence chapter](docs/nfl/REAL_DATA.md) connects the recovered 2.3 GB official input, 51 temporally evaluated rookies, 5,310 public-cohort model fits, and 122 independent NFL tracking games. The [public benchmark](research/public_nfl/REPORT.md) and [external movement tests](docs/nfl/EXTERNAL_TRACKING.md) retain nulls, coverage failures and the stronger controls that erase weaker-comparator headlines. Restricted raw input and individual derived outputs remain private.

Rebuild the complete release ZIP with `python releases/assemble_release.py releases/PerfectJet-v0.13.1.parts.json --download`. Every part and the assembled archive are SHA256-checked. GitHub rejected the single large blob; the verified parts preserve the exact complete ZIP.
