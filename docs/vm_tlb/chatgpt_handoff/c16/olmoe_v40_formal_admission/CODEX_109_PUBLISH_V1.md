# CODEX 109 — V40 Producer Closure and Publish V1

## Goal

Complete producer-side closure for the already captured OLMoE V40 formal dataset, publish the immutable bundle through the existing C16 data plane to `hrl174new`, and stop after durable producer publish evidence is available.

Do not attempt direct SSH to node164.

## Mandatory first reads

1. `docs/vm_tlb/chatgpt_handoff/c16/olmoe_v40_formal_admission/CURRENT_STATE.md`
2. this file
3. current V40 review pack
4. existing data-plane implementation under `util/vm_tlb/c16/data_plane/`

## Starting Git facts

Expected producer baseline:
`hrl/c16-olmoe-nvbit-runtime-compat-109-v40 @ 5901495b4b3b33b88b10b9b4e1a6a13c9a4e1310`

Verify remote/local facts before editing.

## Phase A — CPU-only producer re-audit

Do not rerun GPU formal shards by default.

Tighten `v40_formalize_243.py` fail-closed checks:
- actual selector identity must be verified against the frozen accepted selector contract;
- exactly one non-null tool SHA across all accepted shards;
- exactly one non-null replay SHA;
- exactly one non-null function-identity SHA;
- 243 unique selected statics;
- every shard independent validator PASS;
- every shard current-supervisor CLEAN_EXIT;
- zero FAILED_EXCLUDED;
- executed/zero partition exactly covers all 243.

Important: the historical frozen selector SHA may be a normalized selector identity rather than the literal TSV file byte SHA. Inspect V38 authority and reproduce the exact accepted hashing method. Do not compare unlike hash definitions and do not redefine the authority. Record both literal file SHA and frozen normalized identity if they are different.

Recompute from immutable attempts:
- formal shard table
- 243 summary
- per-shard analysis
- typed role anchors
- dynamic warp record count
- active-lane event count
- role fractions
- SUM_OF_PER_SHARD_UNIQUES

No cross-shard VA union/chronology/reuse.

If re-audit reproduces:
243 = 129 executed + 114 proven-zero + 0 failed,
132096 warp records,
4196352 active-lane events,
typed role anchors weight=101/input=103/output=1085,
record those as local producer-closed facts.

If it does not reproduce, fail closed and diagnose locally. Ordinary parser/hash/report bugs are solve-and-continue. Do not rerun GPU shards unless an immutable shard artifact is genuinely invalid/missing after audit.

## Phase B — close the Git review pack

The existing V40 status file is stale.

Commit a small final producer review pack. At minimum include:
- FINAL_LOCAL_PRODUCER_STATUS.md or equivalent;
- FORMAL_243_SUMMARY.json;
- FORMAL_243_ANALYSIS.json;
- typed-canary summary/receipt;
- P5 source/tool/build SHA closure;
- frozen all-static/selector identity closure;
- explicit transfer state = NOT_YET_ADMITTED;
- SHA256SUMS for the small review pack.

Do not put bulk raw shards into Git.

Use precise terminology:
- dynamic_warp_records
- active_lane_events
Do not collapse them into one ambiguous “dynamic events” field.

Push and canonical remote-verify the producer branch. Ensure clean worktree.

## Phase C — build one immutable C16 data-plane bundle

Use the existing C16 Pipeline V1 conventions rather than inventing a second transfer protocol.

Create one run/bundle representing the OLMoE V40 formal capture portfolio and its required evidence.

The bundle must be sufficient for 174-new to independently:
- verify manifest/artifact SHA;
- rerun C16WARP1 shard validators;
- recompute the 243 partition and per-shard analysis;
- inspect source/tool/replay/function identity receipts;
- build authority-side catalog entry.

Include the immutable raw artifacts actually needed for those checks. Do not include model weights in the capture bundle.

Bind manifest identity to:
- OLMoE model/revision authority;
- S2 B1/T2048/D32;
- natural expert58 down_proj;
- actual-JIT variant A;
- producer GPU/runtime;
- final producer Git commit;
- NVBit/P5 tool identity;
- input binding authority.

Run local finalize and require local closure receipt.

## Phase D — publish through the correct route

Hard network rule:

109 cannot directly access node164.

Do not retry:
`ssh 10.156.120.164`
or any direct node164 address.

Correct route:
`109 -> hrl174new -> /root/share/mnt164/huangrulin/c16_ai_workload`

Use/reuse `util/vm_tlb/c16/data_plane/publish_capture.py` / Pipeline V1 publish semantics.

First verify the `hrl174new` SSH alias and destination mount path are reachable without mutating authority data.

Publish only to:
`.../captures/inbox/<RUN_ID>.partial`
or the exact current Pipeline V1 inbox layout.

Never publish directly into raw/catalog.

Transport must remain resume-capable and copy-only. Preserve source until positive ACK.

After transfer completes, write producer-side publish receipt/log with:
- run_id
- source path
- source manifest SHA
- command/transport
- destination inbox path
- transfer completion state

Do **not** call this positive ACK.

## STOP boundary for 109

STOP after:
- local producer re-audit PASS;
- final producer review pack committed/pushed/remote-verified;
- immutable local bundle finalized;
- bundle copied completely to the hrl174new/node164-mounted inbox;
- no source deletion;
- authority status still explicitly PENDING.

Do not perform node164 raw promotion/catalog admission from 109 if that would collapse the independent receiver role.

The next step belongs to 174-new Codex using `CODEX_174_ADMIT_V1.md`.

Only stop earlier for:
- scientific identity/contract change;
- frozen selector/all-static authority truly fails;
- immutable raw evidence cannot close;
- hrl174new transport itself is unavailable after ordinary engineering repair.
