# Equation ID contract: extending coverage to all 710 catalogue equations

## The gap

`data/equation_id_contract.json` (schema `perfectjet/equation-id-contract/1`)
records a SHA-256 of the canonical record for each equation from PJ-E001
through PJ-E417, and the repository's own checks (`scripts/build_corpus.py`,
`scripts/verify_release.py`) use it to detect any change to an archived
equation's meaning. The catalogue in `data/equations.json` now holds 710
equations, in six series: PJ-E001..PJ-E487, PJ-A001..PJ-A040,
PJ-D001..PJ-D035, PJ-H001..PJ-H088, PJ-HB001..PJ-HB012 and
PJ-X001..PJ-X048. Every equation outside PJ-E001..PJ-E417 — **293 equations**
(70 in PJ-E418..PJ-E487, plus the complete PJ-A, PJ-D, PJ-H, PJ-HB and PJ-X
series) — has no canonical hash in the contract, so a change to any of those
records would pass the existing checks silently.

## What this adds

`data/equation_id_contract_extension.json` (schema
`perfectjet/equation-id-contract-extension/1`) records the canonical hash for
exactly those 293 equations, in catalogue order, using the repository's own
canonicalisation from `scripts/build_corpus.py`: SHA-256 of
`json.dumps(record, sort_keys=True, ensure_ascii=False, separators=(',', ':'))`
encoded as UTF-8.

`scripts/extend_equation_id_contract.py` generates the extension and, with
`--check`, verifies the pair of files. It is a new companion file rather than
an edit of the existing contract, deliberately: the base contract's hashes
and its `through: PJ-E417` statement remain untouched, so nothing that reads
the current contract changes behaviour. Merging the extension into the base
file (and updating `through`) is a maintainer decision left open by this
pull request.

## Verification performed

Before generating anything, all 417 hashes already in the base contract were
recomputed against the current catalogue: **all 417 match**, so the extension
is built on a verified base. After generation, `--check` confirms that the
two files together cover all 710 catalogue equations exactly once, with no
overlap and no extra IDs, and that every one of the 293 extension hashes
matches the current record. A tamper test confirmed the checker has teeth:
changing a single character in one covered record (PJ-A037's title) makes
`--check` fail with an extension hash mismatch for that ID, exit code 1.

The catalogue and base contract files used here are byte-identical to the
copies on `main` (their git blob hashes match the ones served by GitHub:
`c8d1066547935c0793115b13ba3c6755c2e64362` for `data/equations.json` and
`1dbddf9382ff8d099d2238a36b429592cf0acd2a` for
`data/equation_id_contract.json`).

## What this is not

This extends an integrity contract; it does not change any equation, any
equation's status, or any claim in the catalogue. In particular it says
nothing about the Asterion quadratic completion question, whose general
minimum remains unresolved in 493..496 as recorded in
`src/perfectjet/resources/asterion_discoveries.json`.
