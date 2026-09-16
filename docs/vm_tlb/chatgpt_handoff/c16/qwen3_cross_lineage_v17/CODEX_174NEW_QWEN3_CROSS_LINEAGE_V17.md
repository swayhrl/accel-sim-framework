# CODEX GOAL — C16 Qwen3 Cross-Lineage Consumer V17 (174-new)

## Mission

Correct and complete the under-scoped V16 consumer. V16's Qwen3-only shard parse may be reused only after validation, but its cross-lineage comparison, pipeline audit, semantic audit, final decision, and next-target recommendation are NOT authoritative.

CPU-only. Do not run GPU/model execution. Do not mutate accepted raw/catalog.

Base V16 HEAD:
`46d26e76a7b6e4fca272b22895cede867de438ad`

Qwen3 producer evidence-closure authority:
`ac4420f81dfafbe03b96e1bda63b4af31fe77f6a`

Qwen3 run:
`C16R_qwen3-8b_s2-text_decode_nvbit-warp-mref-shard_v14-layer0-downproj_20260916T020000Z_dd14dd14dd14`

Qwen2.5 RAW run:
`C16R_qwen25-7b-raw_s2-text_decode_nvbit-warp-mref-shard_v10-semantic-downproj-r2_20260916T005000Z_cc10cc10cc10`

Expected pack:
`docs/vm_tlb/review_packs/C16_QWEN3_CROSS_LINEAGE_174NEW_V17/`

## P0 — Explicitly audit V16 shortcomings

Read `util/vm_tlb/c16/analysis/v16.py` and record that V16:
- did not open/read the Qwen2.5 RAW formal run;
- hard-coded a three-row comparison table;
- left Pipeline receipt audit pending;
- left semantic evidence audit pending;
- nevertheless emitted PASS_WITH_NCU_GAP;
- emitted a next-target recommendation without a completed cross-lineage evidence table.

Produce `V16_GAP_AUDIT.json`.

## P1 — Validate the Qwen3 C16WARP1 parser before using its fingerprints

Use the repository WRec definition as authority:
`struct WRec { uint32_t static_index, active_mask, cta_x, cta_y, cta_z, warp; uint64_t addr[32]; };`

For every Qwen3 shard validate, not merely assume:
- magic == `C16WARP1`;
- header static index matches manifest entry;
- selected occurrence is recorded;
- keep/count/overflow are internally consistent;
- binary size equals header + keep * sizeof(WRec);
- active-lane events are recomputed from popcount(active_mask);
- addresses used for page/line calculations are only active-lane addresses;
- no active-lane address is silently dropped;
- zero-execution shards have zero records;
- executed/zero partition matches manifest classification.

For a deterministic sample of executed shards, independently recompute event/page/line counts with a second implementation or a separate verification pass and require exact equality.

Because V16 showed many shards with one unique page/line despite large event counts, explicitly report address min/max, unique address count, unique 128B line count, and whether the one-line behavior is real or a parser/data artifact.

Produce:
- `QWEN3_WARP_FORMAT_VALIDATION.json`
- `QWEN3_SHARD_FINGERPRINTS_V2.tsv`
- `QWEN3_ADDRESS_SANITY.tsv`

If parser validation fails, BLOCKED.

## P2 — Deep-audit Qwen3 semantic and Pipeline evidence

Use the hash-closed V15 producer pack at HEAD `ac4420f...`.

Verify and hash-bind at least:
- `S2_STATE_CAPTURE_RECEIPT.json`;
- `S2_REPLAY_EQUIVALENCE.json`;
- `S2_SIGNATURE_GATE.json`;
- `S2_STATIC_PATH_SUMMARY.json`;
- `S2_FORMAL_CAPTURE_SUMMARY.json`;
- `S2_FORMAL_SHARD_INDEX.tsv`;
- `S2_PIPELINE_ACK_RECEIPT.json`.

Do not leave semantic or ACK state as PENDING if these artifacts validate.

Produce:
- `QWEN3_SEMANTIC_EVIDENCE_AUDIT.json`
- `QWEN3_PIPELINE_RECEIPT_AUDIT.json`

## P3 — Independently consume Qwen2.5 RAW formal run

Read the exact Qwen2.5 RAW catalog/raw run directly from node164 using the run ID above.

Apply the same C16WARP1 validation and fingerprint implementation used for Qwen3.

Recompute from raw, not prose:
- static direct-global set size;
- executed/zero partition;
- expected/present/terminal-closed shard counts;
- drop/overflow;
- active-lane event counts;
- per-shard 4K/64K/2M page footprint;
- per-shard 128B line footprint;
- address-sanity summaries;
- object attribution only where same-process context gives a lossless join, else UNKNOWN_RUNTIME.

Produce:
- `QWEN25_RAW_FORMAL_INDEPENDENT_AUDIT.json`
- `QWEN25_RAW_SHARD_FINGERPRINTS.tsv`
- `QWEN25_RAW_MEMORY_FINGERPRINT.json`

## P4 — Real cross-lineage matched-semantic comparison

Build a nontrivial table comparing Qwen2.5 RAW vs Qwen3 for first-decode layer0 `mlp.down_proj`.

Label the comparison exactly:
`CROSS_LINEAGE_MATCHED_SEMANTIC_OPERATOR_COMPARISON`

It is NOT same numeric input and NOT a causal architecture experiment.

Required rows where supported:
- model/revision;
- scenario/input-authority class;
- semantic role;
- MLP input/output dimensions;
- target weight shape/bytes;
- runtime/execution mode;
- kernel implementation family;
- kernel grid/block signature;
- static direct-global set size;
- LDGSTS/special-path presence;
- executed static count;
- zero-proven static count;
- total active-lane dynamic events;
- per-executed-shard event distribution: min/median/max and selected quantiles;
- per-shard 4K page footprint distribution;
- per-shard 64K page footprint distribution;
- per-shard 2M page footprint distribution;
- per-shard 128B line footprint distribution;
- object-attribution evidence class;
- NCU status.

Every row must have `evidence_status = PROVEN | PENDING | NOT_COMPARABLE` and evidence source/path.

Do not compare absolute VA across processes. Do not form a cross-shard address union unless separately proven lossless. Do not invent chronology or reuse distance.

NCU remains NOT_COMPARABLE unless both sides have explicit numeric values and comparable explicit units.

Produce:
- `QWEN25_RAW_VS_QWEN3_DOWNPROJ_COMPARISON_V2.tsv`
- `CROSS_LINEAGE_INTERPRETATION_V2.md`

The interpretation must answer, from evidence rather than assumption:
1. Are the qualified kernel implementation/static-path families the same or different?
2. If static implementation is similar, how do dynamic event and footprint distributions differ?
3. Which differences are plausibly shape/lineage-associated observations, without causal overclaim?
4. What remains unknown because inputs/processes differ?

## P5 — Next-target recommendation only after P4

Generate `NEXT_QWEN3_TARGET_RECOMMENDATION_V2.json` only after the completed comparison.

Choose among at least:
- another MLP target;
- S2 attention/KV target;
- S3 long-context attention/KV census;
- no additional Qwen3 target yet.

State what observed evidence creates information gain. Do not simply repeat the V16 recommendation.

## P6 — Final decision

Allowed:
- `C16_QWEN3_CROSS_LINEAGE_174NEW_V17_PASS`
- `..._PASS_WITH_TYPED_GAPS`
- `..._BLOCKED_<specific_gate>`

PASS requires:
- validated parser;
- deep Qwen3 semantic/ACK audit;
- independently consumed Qwen2.5 RAW run;
- completed multi-row cross-lineage comparison;
- recommendation derived from comparison.

Hash-close the pack, commit/push, report branch/HEAD/decision, then STOP.