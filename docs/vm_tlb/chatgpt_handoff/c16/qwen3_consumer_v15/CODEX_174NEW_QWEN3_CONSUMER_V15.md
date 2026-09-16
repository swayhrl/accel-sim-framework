# CODEX GOAL — C16 Qwen3-8B Independent Consumer + Cross-Lineage Analysis V15 (174-new)

## Mission

Independently consume the accepted Qwen3 S2 formal run from node164/catalog/raw, without trusting node109's summary, and determine what scientific evidence is actually closed. In the same Goal, compare the validated Qwen3 semantic anchor against the already accepted Qwen2.5-7B raw semantic anchor at the same semantic role.

Producer HEAD to audit:
`c4c67b5759c9be110349116c295a1f5411ad8129`

Qwen3 formal run expected:
`C16R_qwen3-8b_s2-text_decode_nvbit-warp-mref-shard_v14-layer0-downproj_20260916T020000Z_dd14dd14dd14`

Qwen2.5 raw comparison authority remains the accepted V10 pair/174 V11 consumer evidence.

CPU-only. Do not run GPU/model execution. Do not mutate accepted raw/catalog. No Qwen3-30B/DeepSeek.

Expected pack:
`docs/vm_tlb/review_packs/C16_QWEN3_CONSUMER_174NEW_V15/`

## P0 — Audit producer claim vs durable evidence

Treat node109's `PASS_WITH_SCOPED_EVIDENCE` as a claim to audit, not an authority.

Explicitly note producer review-pack gaps visible at HEAD:
- `S2_STATE_CAPTURE.json` is zero bytes;
- no durable replay-equivalence/signature-gate artifact in the producer pack;
- formal ACK index is only a thin index;
- NCU index has no numeric export;
- producer's `REAL_EXECUTOR_INTEGRATION.tsv` is not sufficient proof of all executor guarantees.

These do not automatically invalidate accepted formal raw evidence. Separate:
1. formal-data validity;
2. semantic/replay evidence completeness;
3. producer engineering evidence completeness;
4. NCU numeric availability.

## P1 — Independently verify the Qwen3 formal run

Using node164 accepted catalog/raw as authority, locate the exact run_id.

Verify independently:
- catalog entry and immutable manifest;
- model/revision/scenario/phase/semantic target descriptors;
- exact static-set identity;
- expected static instructions;
- `EXECUTED` vs `ZERO_EXECUTION_PROVEN` partition;
- expected/present/closed shard counts;
- every raw C16WARP1 shard fingerprint;
- terminal closure;
- drop=0 / overflow=0;
- static-PC membership and path class;
- same-process context receipt if available;
- verify/admission/ACK receipts;
- no duplicate/concurrent admission evidence.

Recompute counts from durable artifacts. Do not copy `243` from producer prose.

Produce:
- `QWEN3_FORMAL_INDEPENDENT_AUDIT.json`
- `QWEN3_STATIC_EXEC_ZERO.tsv`
- `QWEN3_SHARD_FINGERPRINTS.tsv`
- `QWEN3_PIPELINE_RECEIPT_AUDIT.json`

If accepted raw is not independently self-consistent, fail closed.

## P2 — Qwen3 replay-local memory fingerprint

For every executed direct-global shard, decode only the information supported by the shard format.

Compute replay-local/per-shard and safely aggregatable statistics under the established C16 rules:
- active-lane dynamic memory events;
- load/store event counts;
- supported unique 4K/64K/2M page footprints;
- supported unique 128B line footprints;
- static-PC-level event distributions;
- same-process object composition only where ADDRESS_CONTEXT permits direct attribution; otherwise `UNKNOWN_RUNTIME`.

Do NOT invent:
- global cross-shard chronology;
- cross-path/direct+LDGSTS ordering;
- reuse distance across independent shards;
- cross-process absolute-VA comparison.

If aggregation across shards is not mathematically lossless for a metric, report per-shard distribution/summary rather than a false union.

Produce:
- `QWEN3_MEMORY_FINGERPRINT.tsv/json`
- `QWEN3_STATIC_PC_DYNAMIC_SUMMARY.tsv`
- object-attribution table with explicit evidence class.

## P3 — Independently establish semantic scope from available durable evidence

Audit what can be proven about:
- model: Qwen/Qwen3-8B exact revision;
- S2_TEXT authority;
- first decode;
- layer0 `mlp.down_proj`;
- exact streamed execution vs full-resident distinction;
- replay identity/equivalence;
- in-context vs replay signature equivalence.

If semantic/replay/signature evidence is not durable on node164/Git, do not promote it merely because formal raw exists. Mark the formal data as `FORMAL_CAPTURE_VALID_SEMANTIC_BINDING_PENDING_PRODUCER_EVIDENCE` if needed.

The node109 V15 evidence-closure task may later resolve this. Your task should be independently useful even before that result arrives.

## P4 — Cross-lineage matched-semantic comparison: Qwen2.5 raw vs Qwen3

Compare only supported, typed quantities for:
- Qwen2.5-7B raw S2 first-decode layer0 `mlp.down_proj`;
- Qwen3-8B S2 first-decode layer0 `mlp.down_proj`.

This is a `CROSS_LINEAGE_MATCHED_SEMANTIC_OPERATOR_COMPARISON`, NOT a same-model causal experiment and NOT same numeric input.

Compare where evidence allows:
- model static dimensions and target weight shape/bytes;
- qualified kernel implementation family/signature if proven;
- static direct-global set size;
- LDGSTS/special-path presence;
- executed/zero partition;
- active-lane dynamic event count;
- page/line footprint summaries;
- object-attribution composition;
- NCU only if both sides have durable numeric values with explicit comparable units.

Do not compare absolute VAs across the two deployments/processes.

An especially important question to test, not assume:
- do both lineages select the same BF16 GEMV implementation/static instruction family at first-decode `down_proj`, despite different MLP dimensions?
- if static implementation is the same, are dynamic launch/event/page footprints nevertheless different due to shape/model state?

Produce:
- `QWEN25_RAW_VS_QWEN3_DOWNPROJ_COMPARISON.tsv`
- `CROSS_LINEAGE_INTERPRETATION.md`

Every row must state `evidence_status` = PROVEN / PENDING / NOT_COMPARABLE.

## P5 — Decide next scientific target, but do not run it

Based on the actual comparison, identify what next Qwen3 evidence would add the most information.

Do not automatically choose another MLP linear if the current anchor already shows the same implementation family. Consider whether an attention/KV target or S3 long-context census would provide more orthogonal information.

This is a planning output only. Produce `NEXT_QWEN3_TARGET_RECOMMENDATION.json` with rationale categories and required evidence, not a GPU authorization.

## P6 — Final status

Create:
`docs/vm_tlb/review_packs/C16_QWEN3_CONSUMER_174NEW_V15/`

Include at least:
- `FINAL_DECISION.json`
- formal independent audit artifacts;
- memory fingerprint artifacts;
- cross-lineage comparison table;
- semantic-evidence status;
- next-target recommendation;
- `OPEN_ISSUES.md`;
- `SHA256SUMS`.

Allowed decisions:
- `C16_QWEN3_CONSUMER_174NEW_V15_PASS`
- `..._PASS_FORMAL_WITH_SEMANTIC_EVIDENCE_PENDING`
- `..._BLOCKED_FORMAL_INTEGRITY`

Do not hide missing semantic/signature/NCU evidence in prose. Keep those gaps typed and explicit.

Commit/push and STOP.