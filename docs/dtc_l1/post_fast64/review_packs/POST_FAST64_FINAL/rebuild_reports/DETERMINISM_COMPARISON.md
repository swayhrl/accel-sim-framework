# Measured determinism and validator-read-only comparison

Both records are copied from executed QA-runner outputs, never generated as claimed build steps.

## Isolated core package

- Status: **PASS**
- Compared files: 98
- SHA-256/byte mismatches: 0
- Detail: two isolated core builds; build exit codes=0/0; validation exit codes=0/0; recursive SHA-256 plus byte-size comparison

## Complete formal final package

- Status: **PASS**
- Compared files: 113
- SHA-256/byte mismatches: 0
- Detail: two isolated complete final-package builds (record included); recursive SHA-256 plus byte-size comparison; both final validators executed

## Validator mutation regression

`qa/E_VALIDATOR_READONLY_EXECUTION.tsv` records separate before/after path/SHA-256/byte maps for `--validate-core` and `--validate`; both are mandatory closeout gates.
