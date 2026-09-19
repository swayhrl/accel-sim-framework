> **MID-CAMPAIGN CHECKPOINT 1 REQUESTED:** At the next target-safe boundary, before launching another GPU target, execute `CODEX_SIDE_GOAL_109_V2_1_MIDCAMPAIGN_CHECKPOINT_1.md`, push/remote-verify the checkpoint, then automatically resume this same V2.1 queue. The checkpoint does not reset the active 10h timer and does not close the campaign.

# CODEX SIDE GOAL OVERRIDE — 109 Ten-Hour V2.1 Lock-Wait + Expanded High-Value Queue

Date: 2026-09-19

Status: ACTIVE OVERRIDE FOR `AWMA_109_TEN_HOUR_CAPTURE_AND_NATIVE_RECON_V2`.

This file supersedes the **lock/wallclock policy and queue order/depth** in:

`CODEX_SIDE_GOAL_109_TEN_HOUR_CAPTURE_NATIVE_RECON_V2.md`

All frozen workload identity, storage, fail-closed, publication, provenance and mainline-preemption rules from V2 remain in force.

## 0. Revised time semantics

The RTX4080 lock is expected to be occupied when this goal starts.

Do not consume the 10-hour active campaign budget while waiting for the lock.

Use two timers:

```text
LOCK_WAIT_BUDGET   = up to 6h00m
ACTIVE_GPU_BUDGET  = 10h00m after successful lock acquisition
FINALIZATION_RESERVE = final 30m of ACTIVE_GPU_BUDGET
absolute worst-case elapsed = ~16h
```

If the lock becomes available after 2h, the campaign still gets the full 10h active window.

If the lock never becomes available within 6h, finish CPU-only preparation, close as:

`BLOCKED_GPU_LOCK_TIMEOUT_AFTER_PREP`

then commit/push/clean/STOP.

## 1. W0 — GPU-lock wait with useful CPU-only work

Poll the normal 109 GPU lock every:

`5 min`

Rules:

- never bypass the lock;
- never kill the lock holder;
- never busy-loop;
- record lock owner PID/command/first-seen/last-seen where visible;
- if ownership changes, continue waiting normally.

While waiting, complete as much as possible without touching the GPU:

1. fetch/pull all accepted V1/V2 coordination anchors;
2. build a deterministic expanded target queue;
3. close exact Qwen target identities from accepted census for all planned targets;
4. pre-generate selector arguments and per-target receipts;
5. pre-create node164 destination namespaces;
6. compile/test the native TLB probe harness CPU/toolchain side;
7. audit V1 accepted 16 bundles and build combined offline coverage index;
8. derive per-family existing structural invariants from V1 footprint data;
9. audit model assets/109 replicas for optional cross-model work;
10. prepare all analysis scripts and unit tests;
11. produce `GPU_LOCK_WAIT_RECEIPT.tsv`.

As soon as the lock becomes free:

- acquire it through the normal mechanism;
- set `ACTIVE_START_UTC`;
- start the 10h active timer;
- begin Priority 1.

If a legitimate task takes the lock again after this campaign has begun, wait up to 45 minutes with 5-minute polling. If still unavailable, continue CPU-only analysis/finalization or mark the pending target `DEFERRED_LOCK_BUSY`; never preempt the owner.

# Expanded priority queue

The queue below is intentionally about twice the original V2 workload.

The rule is **value first, breadth later**.

# PRIORITY 1 — RTX4080 native TLB reconnaissance core

Run this first after GPU acquisition because it directly supports the active 174 lookup-model-validity mainline.

Retain the V2 claim boundary:

`RECONNAISSANCE_ONLY`

No simulator baseline rewrite is authorized.

## 1A — Core dependent-chain surface

Run the original V2 single-chain sweep first:

Address spacing:

```text
4 KiB
16 KiB
64 KiB
256 KiB
2 MiB
```

Touched locations:

```text
16,32,64,128,256,512,
1K,2K,4K,8K,16K,32K
```

Extend safely where useful.

At least 50 samples/point when practical.

## 1B — Warm-repeat versus translation-thrash pair

For each candidate knee region discovered in 1A, add two bounded states:

```text
WARM_REPEAT:
  rerun same dependent chain after immediate warmup

INTERVENING_THRASH:
  execute a separate large randomized address-space sweep before rerunning target chain
```

The intervening sweep must be recorded precisely.

Do not call it a TLB flush.

Purpose:

- see whether the candidate knee is sensitive to translation working-set disturbance;
- separate stable data-cache timing from translation-state sensitivity as much as practical.

## 1C — Two load-policy variants if toolchain/source semantics are clean

If CUDA/PTX documentation available locally/toolchain inspection closes semantics, compare:

```text
default global load
cache-global / L1-data-bypass-like global load
```

Only use a load policy whose semantics are source/toolchain-supported.

Do not claim either isolates TLB latency.

If semantics are not clean, skip with receipt.

## 1D — Concurrency surface

Add active dependent chains:

```text
1 warp
2 warps
4 warps
8 warps
16 warps
```

Use independent chains and keep each chain's dependency serial.

Collect the same candidate-knee points, not the entire exhaustive 1A surface if time is tight.

## 1E — Repeatability

For the 8–12 most informative points from 1A–1D:

- rerun in three separate benchmark process launches;
- compare median/p10/p90;
- report cross-process coefficient of variation.

This is required before calling any knee reproducible.

# PRIORITY 2 — Decode Flash temporal series

Complete the original V2 high-value temporal matrix.

## 2A — Flash Primary-1 splitkv

Fresh formal captures:

```text
STEP4
STEP8
STEP16
STEP24
STEP32
```

Existing step1 stays immutable.

## 2B — Flash Primary-2 combine

Fresh formal captures:

```text
STEP4
STEP8
STEP16
STEP24
STEP32
```

Existing step1 stays immutable.

All exact function/shape identity rules from V2 remain.

# PRIORITY 3 — Decode Flash 2D time × within-step depth matrix

This is the main workload expansion and should be done before lower-value Prefill oversampling.

Accepted census shows each Decode Flash family recurs many times per decode step.

Do not interpret within-step occurrence as transformer layer number.

Re-close every exact function+shape occurrence from the fresh listing.

## 3A — Primary-1 splitkv depth sampling

For decode steps:

```text
1
8
16
24
32
```

sample exact same-family/shape occurrences approximately spanning early/mid/late positions:

```text
occ0
occ8
occ17
occ23
```

Reuse accepted/formal assets when the exact cell is already covered:

- step1/occ17 existing Primary-1;
- step8/16/24/32 occ17 from Priority 2.

Fresh-capture only uncovered cells.

Expected maximum new cells: about 14–15, depending on overlap/identity.

If a requested occurrence does not exist under the exact same function+shape, record `CELL_NOT_PRESENT` rather than substituting.

## 3B — Primary-2 combine depth sampling

For decode steps:

```text
1
8
16
24
32
```

sample:

```text
occ0
occ8
occ16
occ23
```

Reuse step1/occ0 and Priority-2 temporal occ0 cells.

Fresh-capture only uncovered cells.

Again, occurrence is execution position within an exact function/shape family, not a proven model layer.

## 3C — 2D analysis

Produce:

`DECODE_FLASH_TIME_DEPTH_MATRIX.tsv`

For every accepted cell report:

- dynamic records;
- memory instructions;
- effective lane-addresses;
- 4KiB pages;
- 64KiB pages;
- opcode histogram digest;
- grid/block;
- exact function digest.

Answer only structural questions:

- does footprint grow with decode step?
- does footprint vary by within-step occurrence?
- are Primary-1/Primary-2 stable enough for representative sampling?

No simulator-performance equivalence claim.

# PRIORITY 4 — Decode GEMV secondary family

Close exact family identity first.

If the previously noted approximately `grid=18992, block=8x8` family closes unambiguously, capture:

```text
STEP1
STEP4
STEP8
STEP16
STEP24
STEP32
```

This adds one extra early step over V2.

Then, if at least 4h remain, sample within-step occurrence variation at:

```text
STEP1:  early / middle / late exact-family occurrences
STEP16: early / middle / late
STEP32: early / middle / late
```

Use actual occurrence indices from the fresh census, not invented numeric positions.

If the family has only one matching occurrence per step, record that and skip depth sampling.

# PRIORITY 5 — Complete Prefill Flash family

Existing accepted:

```text
occ0
occ2
occ4
occ6
occ9
```

Capture remaining exact-family occurrences:

```text
occ1
occ3
occ5
occ7
occ8
```

If all ten exact-family occurrences are now present, compute:

- count invariance;
- opcode-histogram invariance;
- 4KiB/64KiB page-count variation;
- Jaccard overlap of actual page sets between occurrence pairs if addresses are same-run comparable;
- otherwise explicitly say page-set identity is not comparable across independent runs and limit analysis to counts.

Do not force cross-run address identity.

# PRIORITY 6 — Denser Prefill GEMM family

Existing:

```text
occ0 / 4 / 8 / 12 / 16 / 19
```

Capture:

```text
occ2 / 6 / 10 / 14 / 18
```

If >=2h30m remain after these, add:

```text
occ1 / 5 / 9 / 13 / 17
```

only if exact same CUTLASS function+shape remains closed.

This yields a dense but still bounded depth sample.

# PRIORITY 7 — Qwen native timing stability

Run up to:

`12 fresh NSYS runs`

for the frozen S2 workload.

Report stability for:

- Prefill total;
- Decode total;
- Q05;
- Prefill GEMM Primary;
- Decode GEMV Primary;
- Decode Flash Primary-1;
- Decode Flash Primary-2.

Also report whether target ordering/function-shape identities remain stable across repeats.

No NCU.

# PRIORITY 8 — Cross-model reconnaissance

Run only after all higher-value Qwen/native-TLB work is closed or quarantined and >=75 minutes remain.

## 8A — Asset audit

Audit exact node164 authority + 109 replicas for:

```text
Llama-3.2-1B
DeepSeek-V2-Lite
gpt-oss-20b
Gemma-3-12B
Qwen3.5-35B-A3B
Qwen3.5-27B
```

No network download.

## 8B — NSYS census

For any model with:

- complete exact asset;
- existing proven 109 runtime recipe;
- no new quantization/offload contract;
- natural fit on RTX4080 under that recipe;

run a bounded native launch census.

Priority:

1. Llama-3.2-1B;
2. DeepSeek-V2-Lite;
3. others only if exact runnable recipe already exists.

## 8C — Representative capture, only if deterministic

If a fresh census plus an already frozen selection rule can identify a representative target without user/scientific choice, capture at most:

`2 targets per additional model`

Selection rule must be explicit and mechanical, e.g. the dominant exact family by native GPU time within a predeclared phase/category.

Label:

`RECONNAISSANCE_PRODUCER_ASSET`

Do not promote it to a frozen workload baseline.

# PRIORITY 9 — Offline combined analysis

Combine V1 + V2.1 accepted assets.

Produce at minimum:

- `QWEN_FAMILY_TEMPORAL_DEPTH_MATRIX_V2.tsv`
- `DECODE_FLASH_TIME_DEPTH_MATRIX.tsv`
- `FAMILY_REPRESENTATIVENESS_SUMMARY.md`
- `NATIVE_TLB_RECON_SUMMARY.tsv`
- `NATIVE_TLB_RECON_KNEE_CANDIDATES.md`
- `NATIVE_TLB_RECON_REPEATABILITY.tsv`
- `MODEL_ASSET_AND_REPLICA_MATRIX.tsv`
- `CROSS_MODEL_CENSUS_STATUS.tsv`

Key analysis questions:

1. Which Qwen kernel families are structurally invariant across execution depth?
2. Which Decode families change with token step?
3. Is Decode Flash materially more step-sensitive than Decode GEMV?
4. Which family has the largest translation-relevant page footprint?
5. Which native TLB/reach knees are reproducible across process launches?
6. Which observed knees are strongly load-policy/cache-state dependent?
7. What exact experiments should be promoted into a future formal RTX4080 calibration contract?

# Updated resource guards

Keep per-target simulator-native guards from V2.

Increase aggregate new formal trace allowance to:

`160 GiB`

because the queue is approximately doubled.

Native microbenchmark logs remain separate and small.

Do not let aggregate growth threaten node164 safety; if available capacity unexpectedly drops below a comfortable margin, stop new large captures and continue analysis/finalization.

# Updated final deliverables

Use the same report/review-pack names as V2, but add:

```text
GPU_LOCK_WAIT_RECEIPT.tsv
ACTIVE_WINDOW_RECEIPT.json
DECODE_FLASH_TIME_DEPTH_MATRIX.tsv
NATIVE_TLB_RECON_REPEATABILITY.tsv
FAMILY_REPRESENTATIVENESS_SUMMARY.md
```

Campaign status remains:

`AWMA_109_TEN_HOUR_CAPTURE_AND_NATIVE_RECON_V2_COMPLETE_WITH_SCOPE`

even if low-priority cells are skipped by time guard.

# Finalization

The 30-minute reserve begins relative to `ACTIVE_START_UTC + 9h30m`, not Codex launch time.

At reserve entry:

- do not start another GPU target;
- finalize/ACK already complete captures;
- release GPU as soon as no capture needs it;
- finish review pack/git CPU-only;
- remote verify;
- clean;
- STOP.

Do not automatically start another campaign.
