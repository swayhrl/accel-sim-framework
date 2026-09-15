# CODEX 174-new Lane A Goal — C16 Raw7B/AWQ Pair Preparation V8

Accepted Lane A base: `11c8da9df6401f5d2458903ca6be38940739162b`.
Accepted AWQ producer V7: `2a05cadcbcc0e0b477b83d28aabe0c0aee270150`.
Accepted model-completion authority: `cd74256d698d9949d222703db8bb077a3581792a`.

Suggested branch: `hrl/c16-raw7b-awq-pair-prep-174new-laneA-v8`.

CPU-only. Do not run CUDA/GPU workloads and do not mutate node164 formal raw/catalog data.

## Objective

Prepare a fail-closed consumer/comparator for the first controlled Qwen2.5-7B BF16-vs-AWQ deployment pair while independently improving the AWQ-side semantic/object interpretation that can be proven from existing evidence.

## P0 — Preserve accepted boundaries

Keep `RAW7B_AWQ_FUTURE_PAIR_CONTRACT.json` authoritative. A causal/deployment-level pair requires matching model family, exact semantic operator/layer, input token sequence, shape, object-role semantics, replay-local page/line definitions, and documented backend differences.

No cross-deployment absolute VA comparison. No cross-shard VA union/order/reuse. No Qwen0.5-vs-Qwen7 causal language.

## P1 — AWQ object-attribution recovery audit

Using only accepted V6 same-process ADDRESS_CONTEXT and formal shard evidence:
- inventory every runtime range carried in the context;
- resolve aliases/storage identity where present;
- classify ranges as WEIGHT, QUANT_METADATA, ACTIVATION/TEMPORARY only when directly proven from recorded runtime names/storage identity;
- explain why existing formal MREF addresses fall outside or inside known ranges;
- if a formal address maps losslessly to a recorded range, promote only that row to the proven class;
- otherwise retain `UNKNOWN_RUNTIME`.

Do not infer object identity from address magnitude, proximity, kernel purpose, or expected AWQ behavior.

Produce a coverage diagnostic showing known-range bytes, mapped formal events, unmapped formal events, and exact reason each promotion is allowed.

## P2 — Pair semantic-shape inventory

From canonical raw7B and AWQ model metadata, build a table for all 28 decoder layers and linear roles:
- layer id;
- semantic role;
- input/output features;
- raw BF16 tensor shape/bytes;
- AWQ qweight/qzero/scale metadata shapes/bytes where statically available;
- whether the role exists one-to-one across deployments.

This is static semantic preparation only; do not bind the accepted V6 function occurrence to a layer unless direct evidence proves it.

## P3 — Fail-closed pair comparator

Implement a reusable CPU-side comparator that accepts future raw/AWQ review packs and refuses comparison unless a machine-readable pair contract closes at least:
- pair input canonical token-sequence SHA;
- model family and exact deployment revisions;
- semantic layer id/linear role;
- operator input/output shape;
- phase/decode-step scope;
- raw replay equivalence PASS;
- formal path-coverage qualification for both sides;
- NCU metric semantic/cache-control compatibility when NCU is compared.

Comparator outputs should separate:
- deployment-level comparable metrics;
- AWQ-only overhead such as dequantization;
- incomparable evidence;
- unresolved object attribution.

Do not assume that raw BF16 and AWQ kernel implementations are identical; record implementation difference as part of the pair identity.

## P4 — Consume AWQ V7 scenario result descriptively

Record that S1/S3/S4 retained the same implementation/address-path family and were not formally extended. This supports using S2 as the representative AWQ deployment anchor, but does not prove numerical scaling laws.

Do not invent NCU numeric values: V7 Git evidence currently exposes report hashes/metric availability but not compact numeric exports. Make the comparator ready to ingest those exports once producer V8 supplies them.

## P5 — Future raw target recommendation

Produce a ranked, bounded recommendation for ONE matched raw target once node109 proves the AWQ semantic binding. Prefer an ordinary decoder-layer MLP linear if it gives a clean one-to-one raw/AWQ semantic pair. Do not pre-freeze a layer/role before producer evidence identifies the accepted AWQ anchor.

## Tests

- pair comparator rejects mismatched token SHA;
- rejects mismatched layer/role/shape;
- rejects absent replay equivalence;
- rejects incompatible NCU cache-control semantics;
- preserves UNKNOWN_RUNTIME rather than guessing;
- deterministic outputs;
- existing RTX3090 Q2 regressions if shared parser code changes.

## Review pack

Create `docs/vm_tlb/review_packs/C16_RAW7B_AWQ_PAIR_PREP_174NEW_LANEA_V8/` containing at least:
- `FINAL_DECISION.json`
- `AWQ_OBJECT_ATTRIBUTION_DIAGNOSTIC.tsv`
- `PAIR_SEMANTIC_SHAPE_INVENTORY.tsv`
- `PAIR_COMPARATOR_CONTRACT.json`
- comparator test results
- `RAW_TARGET_RECOMMENDATION.md`
- `OPEN_ISSUES.md`
- `SHA256SUMS`

Commit/push and STOP.
