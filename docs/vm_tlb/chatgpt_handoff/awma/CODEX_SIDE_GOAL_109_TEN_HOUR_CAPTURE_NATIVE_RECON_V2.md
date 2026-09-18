> **V2.1 ACTIVE OVERRIDE (2026-09-19):** before executing this file, read and apply `CODEX_SIDE_GOAL_109_TEN_HOUR_V2_1_LOCK_WAIT_EXPANDED_OVERRIDE.md`. The override changes lock-wait semantics, starts the 10h active budget only after lock acquisition, reorders the queue by scientific value, and approximately doubles the target backlog. Where the two files differ, V2.1 wins.

# CODEX SIDE GOAL — 109 Ten-Hour Capture + Native TLB Recon Campaign V2

Date: 2026-09-19

Status: AUTHORIZED 10-HOUR GPU SIDE LANE WHILE 174 MAINLINE CONTINUES.

Stage:

`AWMA_109_TEN_HOUR_CAPTURE_AND_NATIVE_RECON_V2`

Node:

`109 / RTX4080 16GB`

## 0. Relationship to mainline

The active scientific mainline remains on node174-new:

`AWMA_Q05_LOOKUP_MODEL_VALIDITY_CLOSURE_174NEW_V1`

This 109 campaign is explicitly subordinate.

Rules:

- do not touch the active 174 worktree/runtime;
- do not modify accepted Q05 contextual inputs or simulator scientific baselines;
- do not start a new simulator TLB/PTW/cache mechanism experiment;
- do not delete accepted node164 data;
- if a new mainline GPU requirement is explicitly communicated, stop at the nearest target-safe boundary, finalize completed work, release the GPU, and STOP;
- node109 active-model replicas may remain after the campaign.

## 1. Coordination / execution parent

Read coordination branch:

`hrl/awma-109-ten-hour-sidelane-handoff-v2`

Primary execution parent:

```text
hrl/awma-109-unattended-capture-campaign-v1
8f49ba3b9228b5f8a9163e961225ffd415107734
```

Recommended execution branch:

`hrl/awma-109-ten-hour-capture-native-recon-v2`

The V1 campaign is immutable accepted history.

Do not rewrite or republish its 16 accepted bundles.

Accepted source base still includes the exact-LDC validator recovery from:

`c6733012c13099c6a86f506fd8c61e351791159e`

## 2. Frozen Qwen workload

For all Qwen capture tasks:

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

Accepted selection/census anchors:

```text
kernel selection = e90fd76d3704df4a367bb04de09aee42d0cab803
Qwen census      = 678d7b491d4788369ca0c22717453b20846ab195
```

Fresh identity closure remains mandatory. Global launch IDs are navigation only.

## 3. Already accepted V1 assets — do not duplicate

V1 accepted 16 node164-ACKed bundles:

- DECODE_FLASH_PRIMARY_1 step1;
- DECODE_FLASH_PRIMARY_2 step1;
- PREFILL_FLASH occ2/4/6/9;
- PREFILL_GEMM_PRIMARY occ0/4/8/16/19;
- DECODE_GEMV_PRIMARY step4/8/16/24/32.

Use these as existing coverage.

The prior early-close P2D Step4 canary had no terminal closure and was rejected.

Never promote that canary.

If P2D Step4 is run in V2, perform a new fresh formal capture.

## 4. Global unattended guards

Hard wallclock:

`10h00m`

Reserve final:

`30 min`

for transfer verification, review-pack hashes, git push, remote verification and cleanup.

Do not start a new GPU target inside the final 30-minute reserve.

Per simulator-native target:

```text
max wallclock = 25 min
max compressed bundle = 8 GiB
```

Aggregate new formal capture budget:

`96 GiB`

Native microbenchmark artifacts are small and do not count against the raw-trace 96 GiB guard, but still belong on node164 when accepted.

Before every GPU phase:

- use the normal GPU lock;
- do not bypass a legitimate owner;
- verify enough local scratch space;
- verify Qwen/model asset identity before model runs.

Release the lock between logically independent phases where practical.

## 5. Failure policy

### Target-local quarantine and continue

Quarantine one target and proceed when:

- selector identity does not close;
- one target hits a new grammar/opcode semantic gap;
- one target exceeds its guard;
- one target's capture/postprocess/transfer fails after bounded repair;
- one optional model lacks an exact runnable recipe;
- one native reconnaissance point fails independently.

Do not weaken scientific semantics just to keep the campaign moving.

### Global STOP

Stop the whole campaign only if:

- frozen Qwen workload identity changes;
- the shared accepted producer is shown systematically invalid;
- GPU/driver/runtime becomes unstable across independent targets;
- node164 verify/admit/ACK becomes untrustworthy;
- aggregate guard is reached;
- a continuing repair would change shared trace scientific semantics;
- mainline explicitly requests the 109 GPU.

Routine selector, build, postprocess, compression, transfer, index and receipt issues are solve-and-continue.

# PHASE A — Complete Decode Flash temporal coverage

This is highest capture priority.

## A1 — Decode Flash Primary-1 splitkv

Existing accepted step1:

`DECODE_FLASH_PRIMARY_1`

Exact family:

`pytorch_flash::flash_fwd_splitkv_kernel<...>`

Expected shape:

```text
grid  = 1,9,14
block = 128,1,1
```

Fresh-capture:

```text
DECODE_FLASH_PRIMARY_1_STEP4
DECODE_FLASH_PRIMARY_1_STEP8
DECODE_FLASH_PRIMARY_1_STEP16
DECODE_FLASH_PRIMARY_1_STEP24
DECODE_FLASH_PRIMARY_1_STEP32
```

Use V1 identity receipts only as navigation aids.

Re-close exact phase + step + full function + grid/block + within-step occurrence from a fresh exact workload listing.

The old Step4 pre-terminal canary is rejected history and must not be reused.

## A2 — Decode Flash Primary-2 combine

Existing accepted step1:

`DECODE_FLASH_PRIMARY_2`

Exact family:

`pytorch_flash::flash_fwd_splitkv_combine_kernel<...>`

Expected shape:

```text
grid  = 2,1,1
block = 128,1,1
```

Fresh-capture:

```text
DECODE_FLASH_PRIMARY_2_STEP4
DECODE_FLASH_PRIMARY_2_STEP8
DECODE_FLASH_PRIMARY_2_STEP16
DECODE_FLASH_PRIMARY_2_STEP24
DECODE_FLASH_PRIMARY_2_STEP32
```

Require exact same runtime function/shape at every step.

If a later step changes specialization/shape, record it as a new observed family rather than forcing it into Primary-2.

For A1/A2 each successful target requires:

- natural workload completion;
- terminal COMPLETE;
- device_reported = receiver_accepted = raw_records;
- drop=0;
- overflow=0;
- mode2=0;
- strict validator PASS;
- immutable node164 verify/admit/ACK.

# PHASE B — RTX4080 native TLB latency-surface reconnaissance

This phase is **RECONNAISSANCE_ONLY**.

It is not a calibration receipt and must not modify the accepted simulator's 10/80 values.

Purpose:

- collect an Ada/RTX4080 native latency surface;
- identify reproducible working-set/stride knees;
- validate a microbenchmark methodology before the future mainline calibration contract.

## B0 — Harness isolation

Create an isolated source directory, e.g.:

`util/vm_tlb/awma/native_tlb_probe_v1/`

Do not modify CUDA runtime, driver, model environment or simulator.

Record:

- GPU exact name;
- compute capability;
- driver;
- CUDA toolkit;
- SM count;
- reported L2 cache size;
- memory clock / graphics clock snapshots when queryable;
- persistence/power mode when queryable;
- compile flags;
- binary SHA.

## B1 — Dependent pointer-chain benchmark

Implement a single-thread or single-active-lane dependent pointer chase.

Required properties:

- each load address depends on the prior load result;
- use `clock64()` or equivalent device cycle timing;
- measure a batch of dependent loads, not only one load per timestamp;
- include a register-only / no-global-load control for loop/timing overhead;
- use deterministic seeded random permutation over touched locations;
- preserve the same number of dependent loads across points;
- no host timing as the primary latency metric.

Prefer a cache-controlled global-load form such as an explicit PTX load policy only if its semantics are documented by the toolchain and stable.

Do not claim that a chosen cache operator isolates TLB latency by itself.

## B2 — Address-spacing / working-set sweep

Treat these as **address strides**, not asserted hardware page sizes:

```text
4 KiB
16 KiB
64 KiB
256 KiB
2 MiB
```

For each stride, sweep number of touched locations geometrically from small to the largest safe footprint.

Minimum useful touched-location sequence where memory allows:

```text
16, 32, 64, 128, 256, 512,
1K, 2K, 4K, 8K, 16K, 32K
```

Extend further for smaller strides when useful.

Do not allocate more than 50% of device memory in one point.

At each point:

1. construct random dependent chain;
2. pre-touch allocation;
3. warm up;
4. collect >=50 timing samples when runtime permits;
5. report median / p10 / p90 / min / max;
6. record actual bytes spanned and touched cache lines.

## B3 — Data-cache confound controls

At minimum compare:

- one repeatedly touched address / tiny working set;
- many virtual locations whose touched line footprint remains comfortably below reported L2 capacity;
- a deliberately larger touched-line footprint that stresses L2.

The goal is to distinguish a translation-reach knee from an ordinary data-cache-capacity knee.

Do not claim perfect separation.

## B4 — Occupancy/concurrency control

Primary reconnaissance uses one CTA / one active dependent chain.

If at least 45 minutes remain in Phase B, add a small concurrency sweep:

```text
1, 2, 4, 8 active warps
```

with independent chains.

This is secondary; do not let it block the single-chain surface.

## B5 — Reconnaissance output

Create:

- `NATIVE_TLB_RECON_DEVICE_RECEIPT.json`
- `NATIVE_TLB_RECON_RAW.tsv`
- `NATIVE_TLB_RECON_SUMMARY.tsv`
- `NATIVE_TLB_RECON_KNEE_CANDIDATES.md`
- `NATIVE_TLB_RECON_LIMITATIONS.md`

Allowed language:

`candidate latency/reach knees`

Forbidden:

- "L1 TLB latency = X cycles";
- "L2 TLB latency = Y cycles";
- direct rewrite of simulator 10/80;
- treating an end-to-end memory plateau as a pure TLB lookup latency.

If the harness cannot produce stable/reproducible knees after bounded engineering repair, quarantine Phase B as `RECON_INCONCLUSIVE` and continue.

# PHASE C — Secondary Decode GEMV family

Run only if at least 5h00m remain before finalization after A/B.

The earlier census suggested a secondary Decode GEMV family around:

```text
grid  ~= 18992,1,1
block ~= 8,8,1
```

These are not sufficient identity.

First close exact:

- full function;
- grid/block;
- step-local occurrence;
- recurrence consistency.

If unambiguous, capture:

```text
DECODE_GEMV_SECONDARY_STEP1
DECODE_GEMV_SECONDARY_STEP8
DECODE_GEMV_SECONDARY_STEP16
DECODE_GEMV_SECONDARY_STEP24
DECODE_GEMV_SECONDARY_STEP32
```

Otherwise mark:

`SKIPPED_IDENTITY_NOT_CLOSED`

and continue.

# PHASE D — Complete Prefill Flash depth coverage

Run if at least 3h30m remain.

Already accepted:

```text
occ0 = Q05 historical/formal family anchor
occ2
occ4
occ6
occ9
```

Fresh-capture remaining:

```text
PREFILL_FLASH_OCC1
PREFILL_FLASH_OCC3
PREFILL_FLASH_OCC5
PREFILL_FLASH_OCC7
PREFILL_FLASH_OCC8
```

Require exact Q05 family:

```text
flash_fwd_kernel
grid  = 16,1,14
block = 128,1,1
```

If any occurrence differs in specialization or launch shape, classify separately rather than forcing family equivalence.

# PHASE E — Denser Prefill GEMM depth coverage

Run if at least 2h00m remain.

Already accepted:

```text
occ0 / 4 / 8 / 12(existing older durable) / 16 / 19
```

Fresh-capture:

```text
PREFILL_GEMM_PRIMARY_OCC2
PREFILL_GEMM_PRIMARY_OCC6
PREFILL_GEMM_PRIMARY_OCC10
PREFILL_GEMM_PRIMARY_OCC14
PREFILL_GEMM_PRIMARY_OCC18
```

Require exact same CUTLASS function and:

```text
grid  = 128,3,1
block = 256,1,1
```

# PHASE F — Native timing stability

Run if at least 55 minutes remain.

No NCU.

Run the frozen Qwen S2 workload up to 10 times.

Track:

- Prefill total GPU time;
- Decode total GPU time;
- Q05 Prefill Flash occurrence0;
- Prefill GEMM Primary occurrence12;
- Decode GEMV Primary step1;
- Decode Flash Primary-1 step1;
- Decode Flash Primary-2 step1.

Report:

- median;
- min/max;
- p10/p90 when sample count permits;
- coefficient of variation.

This is native runtime stability only.

# PHASE G — Cross-model asset/census reconnaissance

Run only if at least 60 minutes remain after higher-priority work.

## G0 asset inventory

Audit node164 authority and 109 replicas for:

- meta-llama/Llama-3.2-1B;
- DeepSeek-V2-Lite;
- gpt-oss-20b;
- Gemma-3-12B;
- Qwen3.5-35B-A3B;
- Qwen3.5-27B.

Use on-disk receipts/configs.

Do not infer a revision from directory names when not proven.

Do not network-download new weights.

## G1 optional census

A model may run only when:

- complete exact local/164 asset is proven;
- exact existing runnable recipe is already present;
- no new quantization/offload/dtype contract is invented;
- it naturally fits current 4080 recipe.

Priority:

1. Llama-3.2-1B;
2. DeepSeek-V2-Lite if exact runnable;
3. others only if an already-proven 4080 recipe exists.

Run NSYS launch census only.

No full simulator-native cross-model capture unless all higher priority work is complete, >=45 min remain, and an exact representative target can be selected from the fresh census without user/scientific choice.

Any such extra capture is `RECONNAISSANCE_PRODUCER_ASSET`, not a frozen new workload baseline.

# PHASE H — Offline comparative analysis

For every new formal Qwen capture, compute:

- dynamic record count;
- memory-instruction count;
- effective lane-address events;
- translation-relevant 4KiB/64KiB unique pages;
- opcode-family histogram;
- record compression modes;
- terminal/drop/overflow.

Combine with V1's accepted 16-target matrix without copying raw data.

Produce:

`QWEN_FAMILY_TEMPORAL_DEPTH_MATRIX_V2.tsv`

Explicit analyses:

1. Decode Flash Primary-1 footprint vs decode step;
2. Decode Flash Primary-2 footprint vs decode step;
3. Decode GEMV Primary vs Secondary;
4. Prefill Flash depth stability;
5. Prefill GEMM depth stability.

No simulator-performance equivalence claim from footprint alone.

# Publication policy

Every successful simulator-native capture is independently immutable and ACKed on node164 immediately after closure.

Do not defer transfers to end-of-campaign.

Native TLB reconnaissance outputs belong under a separate provenance root, for example:

`/root/share/mnt164/huangrulin/awma_native_tlb_recon_4080_v1/`

Do not mix them into simulator trace bundle identities.

Keep model replicas on109 if useful.

# End-of-campaign deliverables

Report:

`docs/vm_tlb/codex_handoff/awma/TEN_HOUR_SIDELANE_109_V2_REPORT.md`

Review pack:

`docs/vm_tlb/review_packs/AWMA_109_TEN_HOUR_SIDELANE_V2/`

At minimum:

```text
README.md
SOURCE_ANCHORS.md
CAMPAIGN_QUEUE.tsv
TARGET_STATUS.tsv
TARGET_IDENTITY_RECEIPTS/
TRANSFER_ACKS/
QWEN_FAMILY_TEMPORAL_DEPTH_MATRIX_V2.tsv
NATIVE_TLB_RECON_DEVICE_RECEIPT.json
NATIVE_TLB_RECON_SUMMARY.tsv
NATIVE_TLB_RECON_KNEE_CANDIDATES.md
NATIVE_TLB_RECON_LIMITATIONS.md
NATIVE_TIMING_STABILITY.tsv
MODEL_ASSET_AND_REPLICA_MATRIX.tsv
CROSS_MODEL_CENSUS_STATUS.tsv
QUARANTINED_TARGETS.tsv
RAW_DATA_INDEX.tsv
SHA256SUMS
```

If a phase does not run due time/identity, provide an explicit SKIPPED receipt rather than fabricating an empty success.

Campaign success marker:

`AWMA_109_TEN_HOUR_CAPTURE_AND_NATIVE_RECON_V2_COMPLETE_WITH_SCOPE`

Target-local quarantines are compatible with campaign success.

# Finalization

At queue exhaustion or hard wallclock:

1. enter final 30-minute reserve;
2. do not start another GPU workload;
3. finalize current safe target if already near completion;
4. verify every node164 ACK;
5. record all skipped/quarantined items;
6. ensure no campaign GPU process remains;
7. release GPU lock;
8. hash review pack;
9. commit;
10. push;
11. remote ref verify;
12. clean worktree;
13. STOP.

Do not automatically start another campaign.
