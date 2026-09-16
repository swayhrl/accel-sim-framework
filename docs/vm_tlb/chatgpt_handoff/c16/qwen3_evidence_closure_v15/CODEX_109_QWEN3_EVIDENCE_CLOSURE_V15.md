# CODEX GOAL — C16 Qwen3-8B Evidence Closure V15 (node109)

## Mission

Do NOT rerun the scientific campaign from scratch. Treat producer HEAD `c4c67b5759c9be110349116c295a1f5411ad8129` as a producer-execution success whose final review pack is incomplete/internally inconsistent.

Close the missing durable evidence for the already-qualified Qwen3 S2 first-decode `model.layers.0.mlp.down_proj` target, without creating a duplicate formal admission.

Base execution branch:
`hrl/c16-qwen3-8b-unattended-campaign-109-v12`

Expected output pack:
`docs/vm_tlb/review_packs/C16_QWEN3_8B_EVIDENCE_CLOSURE_109_V15/`

## Known audit findings to resolve

1. Existing `S2_STATE_CAPTURE.json` is zero bytes. This cannot support the claimed exact-state gate.
2. Existing review pack has no durable `REPLAY_EQUIVALENCE.json` or `IN_CONTEXT_SIGNATURE_GATE.json`.
3. Existing `S2_FORMAL_ACK_INDEX.tsv` contains only run_id/manifest SHA/PASS; durable manifest/local-close/static executed-zero/drop-overflow/context receipts are not in the pack.
4. Existing `S2_NCU_INDEX.tsv` records only `.ncu-rep` path/SHA and descriptors; numeric metrics + units are not durably exported.
5. Existing `REAL_EXECUTOR_INTEGRATION.tsv` is byte-identical to prior V13 integrity JSON and is not the output of `v14_executor_integration.py`. Do not claim full real-executor test coverage from it.
6. Current real `driver.py` is improved, but integration coverage is partial. This task is evidence closure, not another full executor redesign. Report exact supported guarantees and exact remaining executor engineering gaps.

## P0 — Preserve history and inventory existing evidence

Do not delete/overwrite prior BLOCKED or PASS review packs.

Inventory `/data/c16/qwen3_runtime_v14/`, local campaign state, profiler outputs, NVBit outputs, formal run staging, Pipeline receipts and any node164-visible ACK/material.

Produce `LOCAL_EVIDENCE_INVENTORY.tsv` with path, bytes, SHA256, provenance stage and whether durable export is required.

Do not infer that an artifact exists because a prior summary says so.

## P1 — State-capture receipt closure

Use the already-existing exact state file if present:
`/data/c16/qwen3_runtime_v14/layer0_first_decode_state.pt`

Do not regenerate model state if the existing file is hash-valid and internally consistent.

Generate a non-empty machine-readable `S2_STATE_CAPTURE_RECEIPT.json` recording at minimum:
- exact model/revision;
- scenario `S2_TEXT` and first-decode semantic point;
- semantic target `model.layers.0.mlp.down_proj`;
- state-file path/SHA/bytes;
- decode token;
- `input` shape/dtype/SHA;
- `output` shape/dtype/SHA;
- stored layer0 KV tensor shape/dtype/SHA where present;
- exact target weight SHA;
- source script SHA;
- runtime lock identity.

Cross-check hashes against a fresh read of the state file. Do not fill fields from memory.

If the state file is absent/corrupt, one bounded exact recapture is allowed using the existing V14 exact streamed path. Label it `EVIDENCE_RECOVERY_RECAPTURE`, not a new scientific target.

## P2 — Replay equivalence closure

Produce `S2_REPLAY_EQUIVALENCE.json` from executable validation of the exact stored state and exact target weights.

Required fields:
- input/output/weight identities;
- repeatability result;
- bitwise_equal;
- max_abs;
- output SHA;
- replay script SHA;
- exact runtime identity.

If a durable replay result already exists and can be hash-bound, consume it. Otherwise one bounded replay is allowed. No new formal capture/admission.

## P3 — In-context vs replay signature evidence

Find existing NSYS/NVTX evidence for:
- in-context first-decode layer0 `mlp.down_proj` invocation;
- dedicated replay invocation.

Export a durable `S2_SIGNATURE_GATE.json` containing for each side:
- profiler report path/SHA or durable export SHA;
- NVTX range identity;
- exact kernel name/mangled identity if available;
- grid/block dimensions;
- occurrence/correlation evidence;
- final equivalence decision.

Do not infer signature equivalence from both using `internal::gemvx` in source/SASS alone.

If existing profiler evidence is absent or insufficient, at most one bounded Method-A recapture is allowed, using the already accepted exact state/runtime/target. This is evidence recovery only. Do not change target or implementation.

If signature equivalence still cannot be proven, final status must be `BLOCKED_SIGNATURE_EVIDENCE`, and do not preserve the prior scientific PASS label as closed evidence.

## P4 — Static-path summary closure

Do not rebuild the scientific static set unless the implementation hash differs.

From the actual `S2_STATIC_PATH_AUDIT.tsv` and qualified replay implementation, produce a compact `S2_STATIC_PATH_SUMMARY.json` with:
- exact function/kernel identity;
- SASS/library hashes;
- total static instructions audited;
- direct GLOBAL address-bearing static set count;
- LDGSTS GLOBAL_SOURCE count;
- other address-bearing special path count;
- control-only count where relevant;
- qualified direct/static set SHA;
- instrumentation/tool SHA.

The claimed 243 direct MREF / 0 LDGSTS must be recomputed from the audit, not copied from the report.

## P5 — Formal capture/admission durable evidence

For existing accepted run:
`C16R_qwen3-8b_s2-text_decode_nvbit-warp-mref-shard_v14-layer0-downproj_20260916T020000Z_dd14dd14dd14`

Do NOT create a duplicate formal admission.

Export/record the actual existing:
- formal manifest + SHA;
- complete static-set identity;
- executed vs `ZERO_EXECUTION_PROVEN` partition;
- expected shard count / present shard count / closed shard count;
- per-shard hash index or a durable index to immutable raw artifacts;
- terminal closure;
- drop count;
- overflow count;
- same-process ADDRESS_CONTEXT receipt + SHA;
- Pipeline verify receipt;
- admission receipt;
- accepted ACK receipt/identity.

Produce:
- `S2_FORMAL_CAPTURE_SUMMARY.json`
- `S2_FORMAL_SHARD_INDEX.tsv`
- `S2_PIPELINE_ACK_RECEIPT.json`

If these cannot be recovered from existing accepted data, STOP and report the concrete missing evidence. Never duplicate admission to make evidence easier.

## P6 — NCU durable numeric export

Existing report:
`/data/c16/qwen3_runtime_v14/ncu.ncu-rep`

Verify its SHA matches the prior index.

Export numeric data from this exact report using NCU's own export/import tooling. Produce `S2_NCU_METRICS.tsv` with at least:
- metric name;
- raw numeric value;
- explicit unit exactly as reported;
- target kernel/signature identity;
- cache-control mode;
- replay mode;
- NCU version;
- report SHA;
- export SHA.

Required metric family where actually present:
- `l1tex__t_bytes`
- `lts__t_bytes`
- `dram__bytes`

Do not infer unit scaling. If a value/unit cannot be losslessly exported, mark that field unavailable rather than guessing.

Publish the `.ncu-rep` or a lossless unit-preserving export to the existing durable node164 evidence namespace if repository policy permits, using `.partial` + post-copy SHA. Record a durable receipt. Do not rely only on `/data/c16/...` local lifetime.

## P7 — Real executor evidence correction

Run the actual `v14_executor_integration.py` and store its real output under a correctly named artifact.

Also statically audit current `driver.py` and report truthfully which guarantees are implemented versus not yet fully implemented. At minimum distinguish:
- real handler dispatch;
- missing-handler fail-closed;
- contiguous semantic-digest chain;
- campaign process lock;
- terminal stage receipt overwrite semantics;
- immutable attempt directory behavior;
- global formal-admission lock support;
- shard-resume support;
- stage-specific scientific validators.

Do not call unsupported guarantees PASS.

This engineering audit does NOT invalidate already accepted scientific data by itself; it defines what future campaigns may safely reuse.

## P8 — Final review pack

Create:
`docs/vm_tlb/review_packs/C16_QWEN3_8B_EVIDENCE_CLOSURE_109_V15/`

Include at least:
- `FINAL_DECISION.json`
- `LOCAL_EVIDENCE_INVENTORY.tsv`
- `S2_STATE_CAPTURE_RECEIPT.json`
- `S2_REPLAY_EQUIVALENCE.json`
- `S2_SIGNATURE_GATE.json`
- `S2_STATIC_PATH_SUMMARY.json`
- `S2_FORMAL_CAPTURE_SUMMARY.json`
- `S2_FORMAL_SHARD_INDEX.tsv`
- `S2_PIPELINE_ACK_RECEIPT.json`
- `S2_NCU_METRICS.tsv`
- NCU durable-export receipt if successful;
- `REAL_EXECUTOR_INTEGRATION_RESULTS.json/tsv`
- `EXECUTOR_IMPLEMENTATION_AUDIT.json`
- `OPEN_ISSUES.md`
- `SHA256SUMS`

Allowed decisions:
- `C16_QWEN3_8B_EVIDENCE_CLOSURE_109_V15_PASS`
- `..._PASS_WITH_NCU_NUMERIC_GAP`
- `..._BLOCKED_<specific_missing_evidence>`

No new semantic target. No S3 capture. No duplicate formal admission. No Qwen3-30B/DeepSeek work.

Commit/push and STOP.