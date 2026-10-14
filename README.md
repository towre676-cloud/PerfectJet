# PerfectJet

**Exact arithmetic, predictive state, and navigable populations in one research atlas.**

PerfectJet brings together the PerfectPower, DynaComp, PSG, SOE, WIND, IMP, Morphonic, conductor, Shadow–Core, and Weyl-exactness programs. Its central question is: what smaller representation preserves the answer we need, and what witness tells us when it fails?

The repository contains a [master monograph](docs/MONOGRAPH.md), a [complete topic map](docs/COVERAGE_MAP.md), a [309-equation atlas](docs/EQUATION_ATLAS.md), preserved [archival sources](archive/README.md), and a dependency-free Python core. Historical reports and open proposals remain labeled. No new Lean proof or complete imported upstream solver is claimed.

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
perfectjet sieve
perfectjet nfl --synthetic --seed 1 --out results/nfl-synthetic
python -m unittest discover -s tests -v
```

Without installation, set `PYTHONPATH=src` and use `python -m perfectjet.cli report`. [Windows instructions](docs/QUICKSTART.md) include PowerShell commands.

The runnable core covers rational observability and hidden witnesses, finite partial-machine equivalence, polynomial feature closure, weighted quotient replay, exact selection counts/rank/unrank/ties, corrected energy balances, finite jets, transvectant partner dimensions, exact cubic-field identities, cyclotomic collision coefficients at very large indices, integer lattices (Smith and Hermite forms, integer solvability with infeasibility certificates, integer kernels, saturation index), minimal single- and multi-output word-Hankel realizations with held-out witnesses, coarsest exact weighted lumping, exact rank loci in one or several parameters (comprehensive Gaussian elimination with an exact Groebner engine), an adaptive local sieve for perfect-power hits, active partner strata with replayed partners, exact readout identifiability with repair and value of information, certified decisions, and an adaptive representation engine whose adapters all return one representation-and-obstruction report. Clebsch invariants explain the partner strata: every binary sextic has det L_3=(A^2-B/6)/16 and the correction-free quartic partner (f,f)_4. The PSG root calculation is explicitly numerical.

## Combine scouting

`perfectjet nfl` runs the Combine scouting pipeline in `src/perfectjet/applications/nfl_scouting`: turn events with full lineage, an exact identifiability gate for each athlete's readout, leakage-checked NFL targets, athlete-grouped temporal validation against a conventional baseline, a frozen shortlist rule, and scouting cards. Point it at real data with `--data DIR --mapping mapping.json` ([data contract](docs/nfl/DATA_CONTRACT.md)); the [protocol](docs/nfl/PROTOCOL.md) fixes every analysis choice in advance. The `--synthetic` mode plants or withholds a signal to test the pipeline itself and is never evidence about football. No real-data scouting advantage is claimed.

## Read and explore

[Quick start](docs/QUICKSTART.md) explains the commands. [Architecture](docs/ARCHITECTURE.md) shows how the modules connect. [Corrections and limits](docs/chapters/23_status_corrections_and_frontiers.md) separates current checks from historical claims and missing sources. [Examples](examples/walkthrough.py) connect arithmetic populations, observations, and closure defects.

PerfectJet complements [PerfectPower](https://github.com/towre676-cloud/perfectpower) and [DynaComp](https://github.com/towre676-cloud/DynaComp). Their inspected revisions are recorded in [upstream references](integrations/upstreams.json). This repository does not automatically change their code, sites, or applications.

## Download

The complete [v0.7.0 package](releases/PerfectJet-v0.7.0.zip) contains source, tests, documentation, registry, retained results, and extracted archives. GitHub's [source archive](https://github.com/towre676-cloud/PerfectJet/archive/refs/heads/main.zip) always follows `main`. The [monograph](docs/MONOGRAPH.md) is readable directly on GitHub.

## Reproduce the retained release

```bash
python scripts/build_chapters.py
python scripts/build_corpus.py
python scripts/build_topics.py
python scripts/check_coverage.py
```

The release record states local test results separately from GitHub Actions status. The source provenance describes which documents are complete textual extractions and which are selected excerpts.
