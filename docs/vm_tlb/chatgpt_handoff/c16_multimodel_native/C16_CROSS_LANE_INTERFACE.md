# C16 Cross-Lane Interface

## A → G

A publishes before rental:
- model/deployment matrix;
- model asset manifests + expected hashes;
- input/token receipts;
- scenario matrix;
- GPU package manifest and transfer plan.

G may start a Wave-1 deployment only when its asset/input identity is closed. Wave-2 gaps do not block Wave-1.

## G → C

G first publishes `NATIVE_CATALOG_V1` after Wave-1 census. Minimum consumable payload:
- KERNEL_CATALOG.tsv
- KERNEL_SEMANTIC_MAP.tsv
- SEMANTIC_COVERAGE.tsv
- NATIVE_BASELINE.tsv
- RUNTIME_IMPLEMENTATION_AUDIT.tsv
- HEAVY_TAIL_KERNELS.tsv or raw inputs sufficient for C to recompute them
- manifest + producer/tool identity

C must not consume G's raw live files or naked profiler DBs as scientific input.

## C → G/H

C publishes frozen, versioned:
- STRATA_DEFINITION.json
- CERTAINTY_UNITS.tsv
- SAMPLE_BUDGETS.tsv
- SELECTOR_R/M plan hashes
- candidate NCU/NVBit target plans with semantic identity and selection reason

Once G starts capture for a plan version, C must not mutate that plan. Changes require a new selector/plan version.

## G → H

Small files via Git fixed commit. Large captures via local exchange storage, bound by:
- producer run_id;
- trace/counter file path;
- size;
- SHA256;
- transfer receipt;
- target identity;
- capture terminal/partial status;
- tool version/config.

H refuses raw input with missing hash/identity or wrong target.

## H → C/A

H publishes:
- MEMORY_FINGERPRINTS.tsv
- FINGERPRINT_VALIDATION.tsv
- REUSE_AND_OVERLAP.tsv
- ORDER_MODEL_AUDIT.md
- object attribution coverage
- metric evidence tiers

C uses these only for metric-specific qualification. A uses them for cross-model synthesis after C qualification is available.

## A final integration

A consumes fixed commits from G/C/H. No copy/merge of producer results into mutable A interpretation tables without preserving producer commit and source hash.

A final report must include one row per C16 stage from `C16_STAGE_ACCEPTANCE.tsv`, with execution status, scientific status, producing lane, evidence commit, cost, and limitation.

## Nonblocking policy

- A/C/H offline prep does not wait for GPU rental.
- G0/G1 success lets native baseline/census proceed even if G2/G3 fail.
- C historical estimator work does not wait for G.
- H parser/object-map work does not wait for G.
- Wave-1 publish does not wait for Wave-2.
- Dynamic gaps limit conclusions but should not cause invented data or indefinite waiting.
