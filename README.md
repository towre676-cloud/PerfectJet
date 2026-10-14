# PerfectJet

**Exact arithmetic, predictive state, and navigable populations in one research atlas.**

PerfectJet brings together the PerfectPower, DynaComp, PSG, SOE, WIND, IMP, Morphonic, conductor, Shadow–Core, and Weyl-exactness programs. Its central question is: what smaller representation preserves the answer we need, and what witness tells us when it fails?

The repository contains a [master monograph](docs/MONOGRAPH.md), a [complete topic map](docs/COVERAGE_MAP.md), a [295-equation atlas](docs/EQUATION_ATLAS.md), preserved [archival sources](archive/README.md), and a dependency-free Python core. Historical reports and open proposals remain labeled. No new Lean proof or complete imported upstream solver is claimed.

## Run the mathematics

Requires Python 3.10 or newer. From this directory:

```bash
python -m pip install -e .
perfectjet report --output results/replay.json
perfectjet partners
perfectjet collision --conductor 7 --index 100000000000000000000000000000000000000000000000000
perfectjet core-field
perfectjet psg
python -m unittest discover -s tests -v
```

Without installation, set `PYTHONPATH=src` and use `python -m perfectjet.cli report`. [Windows instructions](docs/QUICKSTART.md) include PowerShell commands.

The runnable core covers rational observability and hidden witnesses, finite partial-machine equivalence, polynomial feature closure, weighted quotient replay, exact selection counts/rank/unrank/ties, corrected energy balances, finite jets, transvectant partner dimensions, exact cubic-field identities, and cyclotomic collision coefficients at very large indices. The PSG root calculation is explicitly numerical.

## Read and explore

[Quick start](docs/QUICKSTART.md) explains the commands. [Architecture](docs/ARCHITECTURE.md) shows how the modules connect. [Corrections and limits](docs/chapters/23_status_corrections_and_frontiers.md) separates current checks from historical claims and missing sources. [Examples](examples/walkthrough.py) connect arithmetic populations, observations, and closure defects.

PerfectJet complements [PerfectPower](https://github.com/towre676-cloud/perfectpower) and [DynaComp](https://github.com/towre676-cloud/DynaComp). Their inspected revisions are recorded in [upstream references](integrations/upstreams.json). This repository does not automatically change their code, sites, or applications.

## Download

The complete [v0.1.0 package](releases/PerfectJet-v0.1.0.zip) contains source, tests, documentation, registry, retained results, and extracted archives. GitHub's [source archive](https://github.com/towre676-cloud/PerfectJet/archive/refs/heads/main.zip) always follows `main`. The [monograph](docs/MONOGRAPH.md) is readable directly on GitHub.

## Reproduce the retained release

```bash
python scripts/build_chapters.py
python scripts/build_corpus.py
python scripts/build_topics.py
python scripts/check_coverage.py
```

The release record states local test results separately from GitHub Actions status. The source provenance describes which documents are complete textual extractions and which are selected excerpts.
