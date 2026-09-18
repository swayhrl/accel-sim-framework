# CODEX SIDE GOAL — 109 Unattended Capture Campaign V1

Date: 2026-09-18

Status: AUTHORIZED GPU SIDE LANE WHILE 174 MAINLINE RUNS.

Stage:

`AWMA_109_UNATTENDED_CAPTURE_CAMPAIGN_V1`

Node:

`109 / RTX4080 16GB`

## 0. Relationship to the mainline

The active scientific mainline is:

`AWMA_Q05_CONTEXTUAL_WARM_PREFIX_REPLAY_174NEW_V1`

on node174-new.

This 109 campaign is explicitly subordinate.

Rules:

- do not touch the active 174 worktree/branch/runtime;
- do not modify accepted Q05 contextual bundle or mainline simulator inputs;
- do not start any TLB/PTW/cache mechanism experiment;
- do not delete accepted data;
- if a new mainline GPU requirement is communicated, finish the current target at the nearest safe checkpoint, publish/receipt what is complete, release the GPU lock and stop the side lane;
- never make the mainline wait for a side task.

This goal is designed for several hours of unattended execution.

## 1. Execution parent and coordination authority

Read coordination branch:

`hrl/awma-109-unattended-sidelane-handoff-v1`

Primary execution parent:

```text
hrl/awma-q05-prefix-ldc-recovery-109-v1
c6733012c13099c6a86f506fd8c61e351791159e
```

Recommended execution branch:

`hrl/awma-109-unattended-capture-campaign-v1`

This parent contains the narrow, source-backed exact-LDC validator recovery.

Accepted producer authority remains:

`5143b4e10aaf2fc47bb60492155d2464b0b726fd`

For ordinary single-target Route-B captures, preserve the accepted single-target producer semantics. Do not replace the producer with the multi-kernel prefix tool unless a task explicitly requires it.

## 2. Frozen primary workload

For all Qwen tasks:

```text
model      = Qwen/Qwen2.5-0.5B-Instruct
revision   = 7ae557604adf67be50417f59c2c2f167def9a775
scenario   = S2_TEXT
batch      = 1
prefill    = 2048
decode     = 32
dtype      = FP16
backend    = SDPA
```

Accepted target-selection authority:

`hrl/awma-kernel-target-selection-109-v1 @ e90fd76d3704df4a367bb04de09aee42d0cab803`

Accepted census authority:

`hrl/awma-qwen25-s2-census-109-v1 @ 678d7b491d4788369ca0c22717453b20846ab195`

Global launch numbers are navigation aids only. Every capture must re-close identity by phase + decode step when applicable + exact function + grid/block + occurrence semantics.

## 3. Storage/model locality

node164 remains authoritative for model assets and all published captures.

109 may retain a local replica of the active Qwen model and any other model actively used during this campaign. Local model copies are convenience replicas only.

Do not copy model weights to 174-new.

Publish every successful capture independently to node164 as soon as it is closed; do not wait until the end of the entire campaign.

Use the already-qualified resumable partial -> verify -> admit -> ACK data plane.

## 4. Global unattended guards

Hard global wallclock:

`10h30m`

This expanded V1.1 queue is intentionally about twice the original campaign size.

Reserve the last 30 minutes for final receipts, hashes, push and cleanup. Do not start a new GPU capture after the finalization reserve begins.

Per-target guards:

```text
max wallclock per simulator-native capture = 25 min
max compressed target bundle              = 8 GiB
```

Campaign aggregate new capture guard:

`64 GiB`

Before each GPU target:

- acquire the normal 109 GPU lock;
- verify no unrelated compute process owns the GPU;
- verify sufficient local free space for the per-target guard;
- verify the active model replica or node164 authoritative model is readable;
- release the lock immediately after target capture/finalization.

Do not kill unrelated processes or bypass a valid lock.

## 4A. W0 — Initial GPU-lock wait and CPU-only preparation

The GPU lock is expected to be occupied when this goal starts.

Do **not** fail after 15 minutes.

Initial wait policy:

```text
poll interval          = 5 min
maximum initial wait   = 4 h
lock bypass            = forbidden
kill lock owner        = forbidden
busy-loop polling      = forbidden
```

While the lock is held, make useful progress without touching the GPU:

1. run P0 historical `DECODE_FLASH_PRIMARY_1` promotion/validation if its existing raw is intact;
2. build the full target queue from the accepted census;
3. close exact function/shape/step identities for every planned target;
4. pre-create target receipts/manifests and selector arguments;
5. perform P6 model-asset / 109-replica inventory;
6. prepare capture wrappers and node164 publication destinations;
7. run CPU-only validator/postprocess/unit tests;
8. record the observed lock holder PID/command/first-seen/last-seen in `GPU_LOCK_WAIT_RECEIPT.tsv`.

As soon as the lock becomes available, acquire it using the normal mechanism and begin the highest-priority pending GPU target.

If the lock is still unavailable after 4 h, finish all CPU-only preparation, close as `BLOCKED_GPU_LOCK_TIMEOUT_AFTER_PREP`, commit/push/clean, and STOP.

After GPU work has begun, if a later target finds the lock occupied by another legitimate task, wait up to 45 minutes using the same 5-minute polling rule before quarantining that target as `DEFERRED_LOCK_BUSY` and moving to CPU-only/finalization work. Never bypass or kill the owner.

## 5. Failure policy: target-local quarantine vs global stop

This is an unattended campaign. A failure in one independent target must not waste the rest of the queue.

### Quarantine target and continue

Examples:

- exact target is absent in a fresh run;
- target-specific grammar/validator failure;
- target exceeds its per-target time/size guard;
- one target's raw/postprocess artifact is corrupt;
- a new opcode semantic gap appears that is not already source-proven;
- target-specific selector ambiguity.

For these:

1. mark target `BLOCKED_* / QUARANTINED`;
2. retain diagnostic receipt;
3. do not publish it as formal;
4. continue to the next independent target.

Do not weaken semantics merely to keep the queue moving.

### Global STOP

Stop the entire campaign only if:

- frozen Qwen workload/model identity changes;
- the shared accepted producer is shown to be systematically wrong;
- two consecutive otherwise-valid targets fail the same producer lifecycle invariant;
- GPU/driver/runtime becomes unstable across targets;
- node164 data-plane verify/admit/ACK is no longer trustworthy;
- aggregate guard is reached;
- continuing requires a shared producer/parser/trace semantic change;
- a mainline GPU preemption request arrives.

Routine build, selector, postprocess, indexing, compression, rsync and catalog issues are solve-and-continue.

## 6. P0 — Recover DECODE_FLASH_PRIMARY_1 without recapture if possible

Historical target:

`DECODE_FLASH_PRIMARY_1`

Identity:

```text
phase       = DECODE
decode step = 1
function    = pytorch_flash::flash_fwd_splitkv_kernel<...>
grid        = 1,9,14
block       = 128,1,1
within-step/function/shape occurrence = 17
reference global launch = 1748
```

Historical raw:

`/data/c16/awma/storage_sidelane_v1/captures/DECODE_FLASH_PRIMARY_1_formal_20260917T212700Z/raw/kernel-1748-ctx_0x55c188f7ab60.trace.xz`

Historical lifecycle:

```text
device_reported   = 1,338,761
receiver_accepted = 1,338,761
raw_records       = 1,338,761
drop              = 0
overflow          = 0
driver exit       = 0
```

It was blocked only by the old LDC.U8 strict-validator mismatch.

Procedure:

1. verify historical raw still exists and SHA/integrity can be closed;
2. canonical postprocess without modifying raw;
3. validate with the exact-LDC repaired validator from the execution parent;
4. if all closure checks pass, publish this existing capture to node164 as `PROMOTED_WITHOUT_RECAPTURE`;
5. only recapture if the historical raw is missing/corrupt or provenance cannot be closed.

No GPU should be used for P0 when existing raw is valid.

## 7. P1 — Capture DECODE_FLASH_PRIMARY_2

Historical selected target:

`DECODE_FLASH_PRIMARY_2`

Identity:

```text
phase       = DECODE
decode step = 1
family      = splitkv-combine
grid        = 2,1,1
block       = 128,1,1
within-step/function/shape occurrence = 0
reference global launch = 1018
historical recurrence count = 768 across 32 decode steps
```

Before capture, recover the exact mangled/demangled function identity from the accepted census/selection pack.

Perform one fresh selector/listing closure, then whole-target simulator-native capture.

Require:

- terminal COMPLETE;
- device_reported = receiver_accepted = raw_records;
- drop=0;
- overflow=0;
- mode2=0;
- repaired strict validator PASS;
- durable node164 verify/admit/ACK.

## 8. P2 — Qwen same-family representativeness matrix

Purpose: build a compact side dataset for **within-family variation** across layer position and decode step. These are producer assets only; do not simulate them in this goal.

### P2A — Prefill FlashAttention depth

Q05 family has 10 Prefill occurrences with the same accepted Q05 shape.

Q05 occurrence 0 is already accepted.

Capture the following stratified depth points:

```text
PREFILL_FLASH_OCC2
PREFILL_FLASH_OCC4
PREFILL_FLASH_OCC6
PREFILL_FLASH_OCC9
```

Identity must match the exact Q05 flash_fwd function family and:

```text
grid  = 16,1,14
block = 128,1,1
phase = PREFILL
family occurrence = 2, 4, 6 or 9
```

These targets test within-family/layer-depth address-footprint variation.

### P2B — Prefill GEMM depth

Accepted `PREFILL_GEMM_PRIMARY_1` exact function/shape has 20 recurrences. Existing durable capture is occurrence 12.

Capture a stratified set spanning the 20 accepted recurrences:

```text
PREFILL_GEMM_PRIMARY_OCC0
PREFILL_GEMM_PRIMARY_OCC4
PREFILL_GEMM_PRIMARY_OCC8
PREFILL_GEMM_PRIMARY_OCC16
PREFILL_GEMM_PRIMARY_OCC19
```

Require exact same function + grid `128,3,1` + block `256,1,1`.

Do not substitute another GEMM family.

### P2C — Decode GEMV temporal evolution

Accepted primary Decode GEMV:

```text
exact internal::gemvx int6
grid  = 1216,1,1
block = 16,4,1
step1 within-step occurrence = 10
```

Existing durable asset covers step 1.

From the accepted full census, prove the same exact function/shape identity in later steps and capture:

```text
DECODE_GEMV_PRIMARY_STEP4
DECODE_GEMV_PRIMARY_STEP8
DECODE_GEMV_PRIMARY_STEP16
DECODE_GEMV_PRIMARY_STEP24
DECODE_GEMV_PRIMARY_STEP32
```

Use step-local semantic binding; do not infer global launch IDs arithmetically.

### P2D — Decode Flash splitkv temporal evolution

Existing historical Primary 1 is step 1.

Capture same exact function/shape at:

```text
DECODE_FLASH_PRIMARY_1_STEP4
DECODE_FLASH_PRIMARY_1_STEP8
DECODE_FLASH_PRIMARY_1_STEP16
DECODE_FLASH_PRIMARY_1_STEP24
DECODE_FLASH_PRIMARY_1_STEP32
```

Require exact splitkv function + grid `1,9,14` + block `128,1,1`.

### P2E — Decode Flash combine temporal evolution

After P1 closes step 1, capture same exact splitkv-combine function/shape at:

```text
DECODE_FLASH_PRIMARY_2_STEP4
DECODE_FLASH_PRIMARY_2_STEP8
DECODE_FLASH_PRIMARY_2_STEP16
DECODE_FLASH_PRIMARY_2_STEP24
DECODE_FLASH_PRIMARY_2_STEP32
```

Require exact function + grid `2,1,1` + block `128,1,1`.

## 9. P3 — Secondary Decode GEMV family

Run after all P0-P2 high-priority targets are either durable or quarantined and at least 100 minutes remain before the finalization reserve.

The previous selection review identified a secondary Decode GEMV shape approximately:

```text
grid  = 18992,1,1
block = 8,8,1
one major recurrence per decode step
~21.5% of Decode GEMV family time
```

Do not capture from this approximate description.

First use the accepted census to identify exactly:

- full function identity;
- grid/block;
- per-step occurrence;
- recurrence consistency across all 32 steps;
- time share.

If exact identity closes, create a five-point decode-step series:

```text
DECODE_GEMV_SECONDARY_STEP1
DECODE_GEMV_SECONDARY_STEP8
DECODE_GEMV_SECONDARY_STEP16
DECODE_GEMV_SECONDARY_STEP24
DECODE_GEMV_SECONDARY_STEP32
```

If identity does not close unambiguously, record `SKIPPED_IDENTITY_NOT_CLOSED` and continue.

### P3B — Complete Prefill Flash family, time permitting

After the stratified Prefill Flash targets in P2A are durable/quarantined, and if at least 80 minutes remain, complete the remaining same-family occurrences so the project has all ten Prefill Flash occurrences represented.

Existing/stratified coverage before P3B is expected to include occurrence 0 plus 2/4/6/9.

Capture remaining exact-family occurrences:

```text
PREFILL_FLASH_OCC1
PREFILL_FLASH_OCC3
PREFILL_FLASH_OCC5
PREFILL_FLASH_OCC7
PREFILL_FLASH_OCC8
```

Require exact same function family + grid `16,1,14` + block `128,1,1`.

If a supposedly same-family occurrence has different exact function semantics or shape, quarantine that occurrence rather than broadening the family definition.

### P3C — Extended Prefill GEMM depth, time permitting

If at least 70 minutes remain after P3B/secondary-GEMV work, add five more exact recurrences from the same accepted Primary GEMM function/shape:

```text
PREFILL_GEMM_PRIMARY_OCC2
PREFILL_GEMM_PRIMARY_OCC6
PREFILL_GEMM_PRIMARY_OCC10
PREFILL_GEMM_PRIMARY_OCC14
PREFILL_GEMM_PRIMARY_OCC18
```

Together with the existing occurrence12 asset and P2B, this gives a denser depth sample without attempting all 20 recurrences.

Do not substitute a neighboring GEMM family.

## 10. P4 — Offline per-capture footprint summaries

For every successful simulator-native target in this campaign, compute small offline summaries without simulator execution:

- raw dynamic-record count;
- warp-instruction count when derivable;
- memory-instruction count when derivable;
- effective lane-address count when derivable;
- translation-relevant 4KiB unique page count;
- translation-relevant 64KiB unique page count;
- opcode-family histogram;
- address compression mode counts;
- zero/drop/overflow closure.

Translation-relevant address scope must follow accepted simulator VM entry semantics, not all serialized address-looking fields.

Do not equate unique pages with TLB misses.

Output one normalized table:

`CAPTURE_FOOTPRINT_MATRIX.tsv`

## 11. P5 — Native timing stability pass

If at least 35 minutes remain, run a lightweight fresh native timing/census stability pass for the frozen Qwen S2 workload.

No NCU.

Perform 8 runs maximum.

Track at least:

- total Prefill GPU time;
- total Decode GPU time;
- Q05 occurrence-0 duration;
- Prefill GEMM Primary occurrence-12 duration;
- Decode GEMV Primary step1 target duration;
- Decode Flash Primary1 step1 duration;
- Decode Flash Primary2 step1 duration when available.

Report median/min/max and coefficient of variation where meaningful.

This is native timing stability only. Do not make simulator claims from it.

## 12. P6 — Model asset / runnable-campaign inventory

This is CPU/storage work and can run after GPU captures or while no GPU target is active.

Inventory authoritative node164 model assets and 109 local replicas for at least:

```text
Qwen/Qwen2.5-0.5B-Instruct
meta-llama/Llama-3.2-1B
deepseek-v2-lite
gpt-oss-20b
gemma-3-12b-it
Qwen3.5-35B-A3B
Qwen3.5-27B
```

Use exact on-disk metadata/receipts; do not invent missing revisions.

Create:

`MODEL_ASSET_AND_109_REPLICA_MATRIX.tsv`

Columns should include:

- model;
- exact revision/hash when proven;
- node164 authoritative path;
- 109 replica path if present;
- size;
- completeness status;
- known runnable recipe on 109 yes/no;
- expected 4080 feasibility from an **existing proven runtime recipe only**;
- recommended next capture action.

Do not network-download a new model in this goal.

Do not create a new quantization/offload policy merely to fit a large model.

### Optional lightweight cross-model census

Only if all of the following are true:

1. at least 60 minutes remain;
2. an exact model asset is complete;
3. an already-established local runtime recipe exists;
4. the model naturally fits the RTX4080 under that existing recipe;
5. no scientific identity needs user choice.

Then a short NSYS launch census may be run, in priority order:

1. Llama-3.2-1B;
2. DeepSeek-V2-Lite only if an exact existing runnable identity is already closed;
3. gpt-oss-20b only if a complete local/164 asset and an already-proven 4080 runtime recipe exist;
4. Gemma-3-12B only under the same already-proven-runtime rule.

At most two cross-model censuses may run in this goal.

This optional census is `RECONNAISSANCE_ONLY`.

Do not start full simulator-native multi-model traces from a newly improvised runtime contract.

## 13. Publication policy

Each successful target gets its own immutable producer bundle + node164 ACK.

Do not wait to publish all captures together.

After all tasks, generate a campaign-level index that references child run IDs/ACKs without repackaging or moving already admitted bundles.

Refresh a deterministic small storage-catalog snapshot if convenient, but do not move historical paths.

## 14. Required campaign deliverables

Report:

`docs/vm_tlb/codex_handoff/awma/UNATTENDED_CAPTURE_CAMPAIGN_109_V1_REPORT.md`

Review pack:

`docs/vm_tlb/review_packs/AWMA_UNATTENDED_CAPTURE_CAMPAIGN_109_V1/`

At minimum:

```text
README.md
SOURCE_ANCHORS.md
CAMPAIGN_QUEUE.tsv
GPU_LOCK_WAIT_RECEIPT.tsv
TARGET_STATUS.tsv
TARGET_IDENTITY_RECEIPTS/
TRANSFER_ACKS/
CAPTURE_FOOTPRINT_MATRIX.tsv
NATIVE_TIMING_STABILITY.tsv              # if P5 ran
MODEL_ASSET_AND_109_REPLICA_MATRIX.tsv
QUARANTINED_TARGETS.tsv
RAW_DATA_INDEX.tsv
SHA256SUMS
```

Campaign status may legitimately be:

```text
AWMA_109_UNATTENDED_CAPTURE_CAMPAIGN_V1_COMPLETE_WITH_SCOPE
```

even if some target-local items are quarantined/skipped, provided the campaign itself remains scientifically fail-closed.

## 15. End-of-goal behavior

At wallclock/queue completion, lock-timeout completion, or mainline preemption:

1. do not start another capture;
2. finalize every completed target receipt;
3. verify every published node164 ACK;
4. record every quarantined/skipped target with reason;
5. ensure no GPU compute process from this goal remains;
6. release GPU lock;
7. review-pack hashes;
8. commit;
9. push;
10. remote ref verify;
11. clean worktree;
12. STOP.

Do not automatically start another side lane or mechanism experiment.
