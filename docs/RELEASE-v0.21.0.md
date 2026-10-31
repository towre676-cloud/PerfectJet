# PerfectJet v0.21.0 — Exact research, certified collision counts and complete Math Lab

PerfectJet v0.21.0 packages **744 equations across 27 families and 30 computed Math Lab tools**, together with the complete finite-system Observatory, mathematical monograph, research proofs, independent checkers and reproducible examples. Python 3.10+ runs the core without third-party runtime dependencies. The full numerical research regression suite uses Python 3.12 and the pinned `scouting` extras.

## What this release includes

The preceding stable download, v0.17.0, contains 464 equations, 24 families and 25 tools. This release adds the intervening main-branch work: the Asterion E8 basis and current-algebra environment, hypergeometric recoupling and KZ transport, exact arc-kernel primitives through weight six, half-braid and Coxeter calculations, sextic boundary strata, the double-elliptic laboratory, and collision/Pell arithmetic. These are the changes already present in source v0.20.0 at `1ea119b1a703f3341ee08897b2dc304fbc4db7af`; they had not been published as stable v0.18.0, v0.19.0 or v0.20.0 GitHub downloads.

PR #14 adds certified finite-input conductor-two collision counting. Its reviewed head is `014daa17972934f1edf49ab107a57e5cf4caa150`. The contribution preserves the preceding asymptotic and proves an explicit square-root/log-squared remainder, with outward rational enclosures for the constants and integer bounds for the cumulative count. A finite zeta-factor extraction sharpens the constant intervals. The existing collision Math Lab tool exposes the approximation alongside the CLI and Python API; this extends that tool without changing the catalogue count.

At X = 10^12 and prime cutoff 10,000, the certified interval is **[17,012,193,046,518, 17,021,178,157,571]**, containing the independently evaluated count **17,016,685,657,676**. The proofs and provenance are in `docs/COLLISION_FINITE_X.md`, `docs/COLLISION_SQRT_REMAINDER.md` and `docs/COLLISION_CONSTANT_EXTRACTION.md`. The exact-count command below reproduces the example:

```sh
python -m perfectjet collision-research approximate --x 1000000000000 --prime-cutoff 10000 --include-exact
```

Run it after installing the core, or set `PYTHONPATH=src` from the extracted source directory. Omit `--include-exact` for inputs beyond the exact replay budget.

## Download and start

Download `PerfectJet-v0.21.0.zip` and its matching `.sha256` file from this release. Extract the ZIP and open the `PerfectJet` folder. Windows users can double-click `Start_Math_Lab.bat`; Linux and macOS users can run `python3 run_observatory.py`. The [installation guide](INSTALL.md) covers virtual environments, checksums, ports and the installed CLI.

## Reproducibility and source identity

Version 0.21.0 identifies the finalized distribution including PR #14; it does not reuse the earlier v0.20.0 checksum. Historical releases and checksum files remain intact. `MANIFEST.json` binds every included source file, and the outer SHA-256 receipt binds the deterministic ZIP. The release's `SOURCE_COMMIT.txt` identifies the exact publication commit; the tag points to that same revision. Rebuild with `python scripts/build_release.py` and compare the checksum.

Publication requires Linux and Windows archive verification, isolated wheel installation, all 30 installed tools, all 30 tools over the supplied launcher's HTTP interface, full mathematical regressions and executable research replays. The archive is rebuilt twice and the Windows and Linux checksums must agree. A draft receives the tested assets before a fresh download is installed and checked. The stable public download is downloaded and verified again after publication. CI logs and release verification artifacts record the actual results. Desktop visual rendering is outside the automated HTTP checks.

The atlas retains definitions, open questions and historical records as well as proved and executable results; individual tools state their supported domains. The release preserves the mathematical authorship and source-bound receipts of its constituent research.
