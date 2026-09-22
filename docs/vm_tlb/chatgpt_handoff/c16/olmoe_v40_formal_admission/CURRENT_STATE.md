# C16 OLMoE V40 — Formal Admission Handoff V1

## Scope

This handoff continues the already-accepted OLMoE V40 producer line. Do not redo V31–V38 identity work, do not change the scientific target, and do not reopen the NVBit version/driver investigation.

## Frozen scientific identity

- model: `allenai/OLMoE-1B-7B-0125-Instruct`
- revision: `b89a7c4bc24fb9e55ce2543c9458ce0ca5c4650e`
- scenario: S2_TEXT B1/T2048/D32
- semantic target: layer1 natural expert58 `down_proj`
- evidence condition: actual-JIT variant A
- actual-A complete static count: 1096
- selected GLOBAL/GLOBAL_TO_SHARED/LDGSTS static set: 243
- frozen all-static SHA: `089d264460999f54f9279ccced4b4bab72483d0572e1d08d6797338ef76a9aa3`
- frozen selector SHA: `9d2d414999e417200167664dc0b4c716f1dcfb72aaf505d89736e14dbedbcb33`

## P0 route decision

Official NVBit 1.7.7.1 mem_trace has been frozen as healthy:

`NVBIT1771_OFFICIAL_MEMTRACE_ACTUAL_A_CLEAN_DYNAMIC_PATH`

The frozen receipt records:
- M0–M6
- rc=0
- timed_out=false
- no target/GPU residual process
- actual-A
- nonzero memory-event evidence
- BF16 raw uint16 output hash
- tool and replay SHA

Therefore:
- do not run the 1.7.5/1.7.7.1 compatibility matrix;
- do not test 1.7.7.3/1.8 for this goal;
- do not start R575 migration or reboot.

## Current producer Git state

Producer branch:
`hrl/c16-olmoe-nvbit-runtime-compat-109-v40`

Reported/verified producer HEAD:
`5901495b4b3b33b88b10b9b4e1a6a13c9a4e1310`

At this commit the implementation contains:
- occurrence-aware C16WARP1 validation;
- P5 static-ID/occurrence fixes;
- formal 243-shard CPU closure code;
- per-shard-only locality analysis.

109 reports the local immutable dataset currently closes as:
- total selected: 243
- executed: 129
- proven zero: 114
- failed/excluded: 0
- dynamic C16WARP1 warp records: 132,096
- active-lane events: 4,196,352
- typed anchors: weight static 101, input static 103, output static 1085

These numeric results are **producer-reported until independently rehashed/recomputed after transfer**. Do not call them node164-accepted yet.

## Important review gap before publish

The Git review pack under:
`docs/vm_tlb/review_packs/C16_OLMOE_NVBIT_RUNTIME_COMPAT_109_V40/`
is still stale at the old “typed/formal not closed” status.

Before authority admission, producer must commit a small final closure pack containing at minimum:
- final local formal summary;
- typed-canary closure receipt;
- per-shard analysis summary;
- P5 tool/source/build identity;
- selector/all-static identity closure;
- artifact/bundle manifest identity and SHA list;
- explicit status: LOCAL_PRODUCER_CLOSED / NODE164_NOT_YET_ADMITTED.

Raw shards do not go into Git.

## Required CPU-only hardening before publish

Do not rerun 243 GPU shards unless hardening uncovers a genuine artifact failure.

The current formalizer must be fail-closed tightened so that it:
1. actually verifies the frozen selector identity, rather than merely copying the expected SHA into output;
2. rejects missing/multiple tool SHA values;
3. rejects missing/multiple replay SHA values;
4. rejects missing/multiple function-identity SHA values;
5. requires every accepted shard to have CLEAN_EXIT with the residual-process closure encoded by the current supervisor;
6. requires the independent C16WARP1 validator PASS for every shard;
7. requires exactly 243 unique selected statics and zero FAILED_EXCLUDED;
8. preserves the executed/zero rule: a valid zero is only a selected static that exists in the frozen selector and closes all lifecycle/terminal/accounting/overflow gates with record_count=0.

Recompute the summary and analysis from the immutable raw attempts after hardening.

## Evidence/analysis restrictions

Continue to prohibit:
- cross-shard absolute-VA union;
- cross-shard global chronology;
- cross-shard reuse distance;
- fresh-process absolute-VA comparison.

Per-shard line/page distributions are allowed.
Sums of per-shard uniques must be explicitly labeled `SUM_OF_PER_SHARD_UNIQUES`.

Keep distinct:
- `dynamic_warp_records` = C16WARP1 warp records;
- `active_lane_events` = sum of active lanes across those records.

Do not silently call both “dynamic events”.

## Node/network roles

Hard boundary:
- node109: GPU producer and local active replica
- 174-new: transfer receiver / verifier / analysis coordinator
- node164: durable model/raw/catalog authority

109 does **not** have direct node164 access.

Correct data path:
`109 -> SSH alias hrl174new -> /root/share/mnt164/huangrulin/c16_ai_workload`

Do not retry `10.156.120.164:22` from 109.

Existing data-plane implementation intentionally constrains producer publishing to SSH alias `hrl174new`.

## Admission contract

Formal admission remains serial:
`FORMAL_ADMISSION_CONCURRENCY=1`

Required chain:
producer local close
→ publish to 174-new node164-mounted inbox as `.partial`
→ independent destination rehash/verify
→ immutable raw promotion
→ catalog entry/snapshot
→ positive ACK
→ producer marks transfer complete

An rsync success alone is not an ACK.

Until positive ACK exists, the correct scientific status is:
`LOCAL_PRODUCER_CLOSED / AUTHORITY_ADMISSION_PENDING`

## After positive ACK

Once node164 admission and ACK are independently closed:
- OLMoE 109 producer line ends;
- do not capture another expert/layer/scenario;
- do not chase variant B;
- prepare the third-lineage handoff for 174-new.

The next consumer set is:
- Qwen3-30B natural expert21 down_proj
- DeepSeek-V2-Lite natural expert4 down_proj
- OLMoE natural expert58 down_proj, conditioned on actual-JIT variant A

Allowed cross-model wording:
`three-independent-lineage MoE-family pattern`

Not allowed:
`universal MoE law`
