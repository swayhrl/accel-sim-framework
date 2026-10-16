# Lane 3 RO oracle and independent transactions r2

Status: ORACLE_INPUT_AND_INDEPENDENT_TRANSACTION_REVIEW_READY.
Full simulator RO status: DEPENDENCY_PENDING, not runtime/performance ready.

Frozen Core producer `5dd246028e3a3d997c1ad48aa85d8d77e98982ac`; Framework verifier/source `28a594c78bc7568ca038f63ef8122ff7337b7d2c`; retained complete-input producer `d2ba33bd92c68f176294c9b5d5a22d3d7b7f8489`. Shared ABI `4fb91f0a5c9eb3bf494a154ea1f24b9a56b34617`. Coordination `6c136e2a56a008695f8c8b815723bf8f1a760db9` is not a runtime source.

## Delivered

Five complete development inputs (30 kernel traces total), manifest hashes, line-level SQLite read/write/atomic sets, conservative exclusions, compact certified line ranges and independently checked input bindings. coverage.csv denominator is traced global-read lane references, not L2 misses or achieved performance. FWT has zero eligible lines under the full-commandlist epoch; no unsafe per-load fallback is used.

Nineteen Python tests, seven actual transaction-module/byte-reference scenario groups, C++ range grammar tests and five real certificate loads pass. Full Release Core build, native descriptor unit and native production-path regression pass. Those native regression results preserve the old static path; they do not qualify integrated RO. Exact commands, identities, leases and raw hashes are in validation/. No formal performance simulation has been launched.

Read RO_ORACLE_CONTRACT.md, RO_TRANSACTION_STATE.md, SOURCE_MAP.md, METADATA_COST.md, RO_READY_MANIFEST.json, coverage.csv and inputs/. patch/ applies to the published Lane-1 shared ABI; the check is recorded. Lane 1 remains final public-Core integrator.

## Dependency handoff

Latest consumed Lane-1 public Framework contract remains cb7d92e4edde97e81520cfdd00762dfe81ee9b20, BASELINE_CONTRACT.runtime_ready=false. Its published Core exposes shared identity; the executable RO role/pin/sector/Tag-return adapter is not yet qualified/published. No whole-cache RO runtime switch is enabled by this candidate. Lane-5 tooling publication 12c2eeac8f9e55351fa58c3807cce5234231ad0c, client de8fe21d9598660e40da8486e48f2d46acee4582, was consumed for shared leases. All owned preprocessing/build tasks and leases are finished. No polling daemon or unreported background simulator remains.

The r1 pack is immutable. This r2 adds real input coverage, runtime line membership, cycle-local read grants, partial resident-sector preservation, detached address-cap stress, metadata ledger and additional validation. No scientific speedup or independent review acceptance is asserted.
