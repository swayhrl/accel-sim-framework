# CODEX 174-new — V40 Independent Verify, Admit, ACK, and Third-Lineage Handoff V1

## Goal

Independently verify the OLMoE V40 producer bundle delivered from node109 into the node164-mounted C16 inbox, admit it to immutable node164 authority only if all frozen contracts reproduce, issue a positive ACK, and then prepare the third-lineage consumer handoff.

This is a CPU-side receiver/authority task. Do not rerun GPU capture.

## Mandatory first reads

1. `docs/vm_tlb/chatgpt_handoff/c16/olmoe_v40_formal_admission/CURRENT_STATE.md`
2. `docs/vm_tlb/chatgpt_handoff/c16/olmoe_v40_formal_admission/SELECTOR_AUTHORITY_REPAIR_V1.md`
3. this file
4. existing C16 data-plane implementation under `util/vm_tlb/c16/data_plane/`
4. the producer final review pack and transferred bundle manifest

## Node roles

- 109 = producer
- 174-new = independent receiver/verifier/coordinator
- node164 mount = durable raw/catalog authority

Expected node164 root:
`/root/share/mnt164/huangrulin/c16_ai_workload`

Do not copy model weights to 174-local storage.

Formal admission concurrency remains 1.

## Phase A — discover the transferred partial bundle

Locate the exact RUN_ID delivered by 109 in the Pipeline V1 inbox.

Require:
- one intended `<RUN_ID>.partial`;
- manifest present;
- producer local-close receipt present if required by the Pipeline V1 contract;
- no pre-existing raw destination or conflicting catalog entry.

Do not infer acceptance from rsync completion.

## Phase B — independent transport verification

Use the existing receiver verifier, not producer assertions.

Independently:
- validate manifest schema;
- enumerate actual regular artifacts;
- verify every declared size and SHA;
- verify manifest/run identity;
- reject symlinks/non-regular unexpected artifacts;
- generate a durable destination verification receipt.

If verification fails:
- quarantine according to existing data-plane policy;
- do not create ACK;
- diagnose ordinary transport/manifest engineering issues and continue only with a new valid partial bundle.

## Phase C — independent scientific recompute

From destination-side artifacts, independently rerun/recompute the accepted checks. Do not merely copy the producer summary.

Frozen target:
- OLMoE revision `b89a7c4bc24fb9e55ce2543c9458ce0ca5c4650e`
- S2 B1/T2048/D32
- layer1 natural expert58 down_proj
- actual-JIT variant A
- 1096 actual-A statics
- 243 selected static paths
- frozen all-static identity `089d264460999f54f9279ccced4b4bab72483d0572e1d08d6797338ef76a9aa3`
- frozen selector identity `9d2d414999e417200167664dc0b4c716f1dcfb72aaf505d89736e14dbedbcb33`

Important selector provenance rule:
- preserve the historical V38 `9d2d...` checksum as historical evidence;
- if producer recovered the exact historical serializer, independently reproduce it;
- otherwise, do not pretend to reproduce it. Verify the producer's `SELECTOR_AUTHORITY_REPAIR_V1` receipt, literal raw-TSV SHA, committed canonicalizer source/SHA, and independently recompute `C16_SELECTOR_CANONICAL_V1` from the destination bundle;
- require exact 243 selector membership equality with the formal shard set.
The new canonical V1 hash is a provenance-repair authority and must not be mislabeled as the historical V38 hash.

For all 243 shards independently require:
- exact static membership;
- function identity binding;
- occurrence gate;
- current C16WARP1 validator PASS;
- exact terminal/accounting;
- overflow=0;
- valid binary;
- clean lifecycle evidence;
- record_count classification.

A zero shard is accepted only when the selected static exists in the frozen selector and all lifecycle/terminal/accounting/identity gates pass with record_count=0.

Recompute:
- total selected
- executed
- proven zero
- failed/excluded
- dynamic_warp_records
- active_lane_events
- typed role anchors/fractions
- per-shard 128B / 4K / 64K / 2M locality
- `SUM_OF_PER_SHARD_UNIQUES`

Do not compute:
- cross-shard absolute VA union
- cross-shard chronology
- cross-shard reuse distance
- fresh-process absolute VA comparison

Expected producer-reported values are:
- 243 total
- 129 executed
- 114 proven zero
- 0 failed
- 132096 dynamic warp records
- 4196352 active-lane events
- typed anchors weight=101/input=103/output=1085

These are comparison expectations, not acceptance shortcuts. If independent recompute differs, fail closed and report the exact delta.

## Phase D — immutable authority admission

Only after transport verification PASS and scientific recompute PASS:
- use existing `admit_capture.py` / Pipeline V1 authority protocol;
- promote the verified partial bundle to immutable node164 raw storage;
- create immutable catalog entry;
- rebuild catalog snapshot deterministically;
- preserve all verification/admission receipts.

Do not overwrite an existing RUN_ID.

## Phase E — positive ACK

Generate the Pipeline V1 positive ACK bound to:
- exact run_id
- source manifest SHA
- destination verification/manifest SHA
- file count
- total bytes
- immutable destination raw path
- catalog entry SHA
- PASS verification status

The ACK must be machine-verifiable by the producer-side `validate_ack` contract.

No positive ACK exists before this step.

## Phase F — Git closure and third-lineage handoff

Create a small 174-side review/consumer pack containing:
- destination verification receipt;
- independent scientific recompute summary;
- admission receipt;
- catalog entry identity;
- positive ACK identity;
- explicit statement that OLMoE evidence is conditioned on actual-JIT variant A.

Commit/push/remote-verify on an appropriate 174 coordination/consumer branch with clean worktree.

After positive ACK, prepare the next C16 consumer stage for three independent MoE lineages:

1. Qwen3-30B natural expert21 down_proj
2. DeepSeek-V2-Lite natural expert4 down_proj
3. OLMoE natural expert58 down_proj / actual-JIT variant A

The next comparison is descriptive, not matched-input causal.

Allowed wording:
`three-independent-lineage MoE-family pattern`

Forbidden overclaim:
`universal MoE law`

Independent recompute should compare:
- executed/zero partition;
- dynamic warp/lane event quantities with units kept distinct;
- per-shard lines/pages;
- input/weight/output/other fractions.

Do not use cross-run absolute VA or cross-shard chronology/reuse.

## STOP boundary

STOP after:
- destination verify PASS;
- independent 243 scientific recompute PASS;
- immutable node164 raw admission;
- catalog entry/snapshot;
- positive ACK;
- Git review closure;
- third-lineage handoff prepared.

Do not start unrelated new GPU capture or new TLB/cache mechanism experiments.

Stop earlier only for:
- authority identity mismatch;
- independent recompute mismatch not explainable by engineering packaging;
- evidence contract/claim boundary change.
