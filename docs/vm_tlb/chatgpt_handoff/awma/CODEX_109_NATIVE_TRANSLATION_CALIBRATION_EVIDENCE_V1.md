# CODEX 109 GOAL — Native Translation Calibration Evidence V1

Date: 2026-09-22

Mode:

`GOAL MODE / candidate-neutral native evidence / solve-and-continue`

Node:

`109 / RTX4080`

Stage:

`AWMA_NATIVE_TRANSLATION_CALIBRATION_EVIDENCE_109_V1`

Coordination branch:

`hrl/awma-native-calibration-handoff-v1`

This lane runs in parallel with 174-new simulator semantic recalibration. It does not depend on V2 succeeding and must not modify the 174 execution.

## 0. Scientific purpose

Collect native evidence that can later constrain and calibrate simulator translation semantics.

This stage does NOT:

- promote V1/V2 simulator candidates;
- claim a real RTX4080 TLB latency;
- design a TLB/PTW/cache mechanism;
- equate NVBit/NCU/NSYS evidence with simulator cycles.

The native question is:

> Does real RTX4080 behavior support latency/throughput overlap and page-working-set sensitivity consistent with a pipelined translation frontend, and what native constraints should any future accepted simulator baseline satisfy?

## 1. Frozen workload / accepted identities

Main AI workload:

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

Reuse authorities:

- exact-target Native export:
  `hrl/awma-109-exact-target-native-crossview-v1 @ 2122eccc7aed61d05b114075e1c3126c4308e64b`
- accepted Route-B / unattended producer evidence:
  `8f49ba3b9228b5f8a9163e961225ffd415107734`
- Q05 prefix producer authority:
  `c6733012c13099c6a86f506fd8c61e351791159e`
- kernel target selection:
  `hrl/awma-kernel-target-selection-109-v1 @ e90fd76d3704df4a367bb04de09aee42d0cab803`

Frozen mainline targets:

```text
T0 = Q05_PREFILL_ATTN_FLASH
T1 = PREFILL_GEMM_PRIMARY_OCC0
T2 = DECODE_GEMV_PRIMARY_STEP16
```

Do not result-substitute targets.

## 2. Existing evidence — reuse before capture

First build:

`EXISTING_NATIVE_CALIBRATION_EVIDENCE.tsv`

At minimum bind the following already-accepted facts.

### NSYS census

Accepted Qwen2.5 S2 census:

- 34,677 total CUDA kernel activities;
- 408 Prefill launches in the explicit inference range;
- 33,664 Decode launches;
- Q05 occurrence 0 duration = 159,969 ns;
- same-shape Prefill Flash family median = 154,112.5 ns.

This is useful Native timing/context evidence, but one census run is not a timing-stability qualification.

### Existing NVBit / Route-B dynamic memory evidence

T1 `PREFILL_GEMM_PRIMARY_OCC0`:

```text
raw dynamic records       12,043,648
memory instruction records 2,298,240
effective lane addresses  70,352,896
unique 4 KiB pages             7,906
unique 64 KiB pages              495
```

Multiple accepted Prefill GEMM occurrences (0/4/8/16/19) have the same dynamic-count and page-footprint descriptors.

T2 `DECODE_GEMV_PRIMARY_STEP16`:

```text
raw dynamic records        1,515,136
memory instruction records   318,592
effective lane addresses   9,022,720
unique 4 KiB pages             2,132
unique 64 KiB pages              135
```

Accepted step 4/8/16/24/32 GEMV captures have the same dynamic-count descriptors and nearly identical page footprints.

Accepted same-family Prefill Flash captures (occ2/4/6/9):

```text
raw dynamic records       13,490,624
memory instruction records 1,100,848
effective lane addresses  33,693,184
unique 4 KiB pages             3,625
unique 64 KiB pages              228
```

These are valid Native dynamic-address / footprint evidence.

Do not interpret the ~16:1 4K-to-64K page-count ratio as proof that RTX4080 hardware TLB pages are 64 KiB. It only shows the observed address ranges are densely packed at that extent.

### Existing gaps

The accepted exact-target Native export explicitly leaves:

- T0/T1/T2 compact exact-target timing: unavailable;
- exact-target NCU resource evidence: unavailable;
- T0 exact comparable Native footprint: unavailable in that evidence class;
- Q05 predecessor-page/TLB-residency context: unavailable.

Do not silently upgrade these from simulator-native trace data.

## 3. Reuse-first timing recovery

Before rerunning the GPU, attempt a deterministic join between:

- accepted NSYS `ALL_KERNEL_LAUNCHES.tsv`;
- accepted exact target identity receipts;
- exact function + phase + decode-step + grid + block + occurrence/ordinal.

If an existing NSYS launch can be uniquely and provenance-safely bound to T0/T1/T2, export:

`REUSED_EXACT_TARGET_NATIVE_TIMING.tsv`

Label each row:

`REUSED_ACCEPTED_NSYS_CENSUS`

If any identity is ambiguous, comes from a non-equivalent run, or cannot be hash/provenance closed, leave it unavailable and proceed to fresh timing collection.

Do not force a join.

## 4. Tool-capability canary

Record exact:

- GPU model / UUID;
- driver;
- CUDA;
- Nsight Systems;
- Nsight Compute;
- NVBit/tool build authorities;
- clock/power state observables available without system modification.

Run:

`ncu --query-metrics`

Search the actual RTX4080 metric list for names/descriptions matching:

```text
tlb
mmu
gmmu
page
translation
```

Record:

`DIRECT_TRANSLATION_COUNTER_STATUS.tsv`

If no reliable direct translation metric is exposed, record:

`DIRECT_TRANSLATION_COUNTER_UNAVAILABLE`

and continue. Do not infer hidden counters.

Nsight Compute is diagnostic only; primary Native timing must come from uninstrumented/lightweight timing or NSYS, not NCU replay timing.

## 5. Fresh exact-target Native timing

For any T0/T1/T2 timing not safely recovered from accepted census, run fresh exact frozen workload repetitions.

Requirements:

- target identity must match accepted function/shape/phase/step/occurrence receipt;
- verify implementation stability on every measured run;
- use lightweight timing / NSYS without NVBit or NCU;
- preserve individual-run values, not only averages;
- minimum 2 warmup + 5 measured runs;
- if coefficient of variation is clearly nontrivial, extend to 10 measured runs;
- record GPU clocks/temperature/power observables if available.

Output:

`EXACT_TARGET_NATIVE_TIMING_STABILITY.tsv`

T0/T1/T2 primary timing is Native ns/us only. Never convert it directly to simulator cycles.

## 6. Exact-target NCU resource regime

After selector canary proves exact launch selection, collect a bounded NCU set for T0/T1/T2.

Preferred interpretation:

- data-cache / L2 / DRAM traffic;
- achieved occupancy / active-warps;
- selected memory-dependency / scoreboard stall indicators;
- instruction/memory-workload consistency.

Actual metric names must be selected from `ncu --query-metrics` on this RTX4080.

Do not assume any metric exists.

Prefer application-context-preserving replay/cache policy if it is supported and reproducible; record exact replay mode and cache-control policy.

NCU timing is not the primary Native timing.

If direct TLB/MMU metrics are unavailable, NCU is used to control data-cache/DRAM confounders, not to manufacture a TLB hit rate.

Output:

`EXACT_TARGET_NCU_RESOURCE_REGIME.tsv`

## 7. Exact T0 Native footprint closure

T1/T2 already have accepted Route-B Native footprints.

T0 exact Native footprint remains unavailable in the accepted cross-view evidence class.

First determine whether an already accepted Q05 Native payload can be formally reclassified without importing simulator-only semantics.

If not, perform one bounded fresh exact-Q05 Native memory observer capture using the already-qualified Route-B/NVBit lifecycle.

Require:

- exact Q05 occurrence 0 identity;
- natural workload execution;
- terminal capture;
- full static global-address-path qualification under the current accepted producer methodology;
- memory-instruction records;
- effective lane addresses;
- unique 4K/64K pages;
- node164 publish + hash + ACK.

Do not recapture T1/T2 solely for symmetry.

## 8. Purpose-built translation microbenchmarks

This is the core hardware-calibration evidence and is independent of AI target timing.

Build a small CUDA microbenchmark suite with deterministic source/provenance.

Do not try to read an undocumented TLB latency directly.

Use behavioral comparisons.

### M0 — data/cache control

Same number of dynamic global loads and similar line traffic, with a compact virtual-page footprint.

Purpose:

- establish data/cache baseline;
- provide a control for page-spread experiments.

### M1 — dependent page chain

A serialized pointer/address dependency chain spanning a controlled number of pages.

Sweep working-set/page count from clearly small to clearly large.

Purpose:

- expose address-translation + memory dependency latency when concurrency cannot hide it;
- find behavioral working-set knees.

### M2 — independent multi-warp page streams

Independent page accesses with increasing active warps / independent chains.

Keep per-access work as close as practical to M1/control.

Purpose:

- test whether the Native machine hides latency through concurrent/outstanding translation/memory requests;
- characterize throughput scaling rather than only latency.

### M3 — page-footprint/stride sweep

Sweep address spacing / unique-page working set while keeping dynamic load count fixed as far as practical.

Include at least 4 KiB and 64 KiB spacing cases as behavioral probes, but do not label either as the hardware TLB page size unless independently established.

If CUDA VMM allocation granularity is queryable, record it as a driver allocation fact, not as a TLB-page-size proof.

### Measurement discipline

For each configuration:

- deterministic seed;
- same binary/source;
- bounded warmup;
- repeated Native timing;
- preserve individual results;
- measure data traffic for a small representative subset with NCU;
- use NVBit only as an address-stream verification canary if needed, never for primary timing.

Primary outputs:

```text
NATIVE_MICROBENCH_TIMING.tsv
NATIVE_MICROBENCH_RESOURCE_CONTROL.tsv
NATIVE_MICROBENCH_CONFIG_AUTHORITY.json
```

## 9. Representative simulator-native microbench traces

Only after Native microbenchmark behavior is stable, select a minimal representative set.

Target 4–6 total traces, for example:

- one compact dependent control;
- one large-footprint dependent case;
- one low-concurrency independent case;
- one high-concurrency independent case;
- optionally one working-set-knee case.

Capture these using the already accepted simulator-native producer path and publish to node164.

These traces are for later 174 Legacy/V1/V2 comparison.

Do not run Accel-Sim on node109.

Do not capture every sweep point.

## 10. Native calibration interpretation boundary

This stage may support:

- Native timing scaling;
- latency-exposure vs concurrency trends;
- page-working-set knees;
- exact-target data/cache resource regimes;
- exact-target Native page footprints;
- candidate-neutral hardware constraints.

It may NOT claim:

- RTX4080 L1 TLB latency = X cycles;
- a specific hidden TLB capacity unless the experiment genuinely isolates and supports it;
- NCU cache-control == TLB flush;
- NVBit-instrumented timing == uninstrumented Native timing;
- simulator cycles == Native nanoseconds.

## 11. Resource / parallel execution

This 109 lane is independent of 174-new V2.

Before GPU work:

- verify no existing GPU campaign/lock;
- inspect VRAM/process state;
- use the existing GPU campaign lock;
- do CPU-only artifact reuse / parser work while waiting for GPU if needed.

Within 109:

- NSYS/lightweight timing runs that share mutable process/GPU state may be serialized;
- CPU parsing/hash/publication should overlap GPU execution;
- NCU and NVBit must not run concurrently with primary timing;
- use maximum safe parallelism for independent CPU analysis/publication steps.

## 12. Durable publication

node164 remains the durable evidence authority.

109 local copies are temporary producer replicas.

For every new accepted bundle:

```text
local closure
-> manifest/SHA
-> node164 publish
-> destination verify
-> ACK
```

Do not delete local data merely because rsync exits 0.

## 13. Deliverables

Execution branch suggestion:

`hrl/awma-109-native-translation-calibration-evidence-v1`

Report:

`docs/vm_tlb/codex_handoff/awma/NATIVE_TRANSLATION_CALIBRATION_EVIDENCE_109_V1_REPORT.md`

Review pack:

`docs/vm_tlb/review_packs/AWMA_NATIVE_TRANSLATION_CALIBRATION_EVIDENCE_109_V1/`

Required:

```text
README.md
SOURCE_ANCHORS.md
EXISTING_NATIVE_CALIBRATION_EVIDENCE.tsv
REUSED_EXACT_TARGET_NATIVE_TIMING.tsv
DIRECT_TRANSLATION_COUNTER_STATUS.tsv
EXACT_TARGET_NATIVE_TIMING_STABILITY.tsv
EXACT_TARGET_NCU_RESOURCE_REGIME.tsv
T0_NATIVE_FOOTPRINT_STATUS.md
NATIVE_MICROBENCH_CONFIG_AUTHORITY.json
NATIVE_MICROBENCH_TIMING.tsv
NATIVE_MICROBENCH_RESOURCE_CONTROL.tsv
MICROBENCH_TRACE_SELECTION.tsv
RUN_RECEIPTS.json
RAW_DATA_INDEX.tsv
SHA256SUMS
```

If a file has no admitted rows, explicitly record why; do not fabricate data.

## 14. Stop boundary

Ordinary engineering problems: solve-and-continue.

STOP only for:

- workload/target identity change;
- inability to preserve Native evidence class;
- a required tool behavior that would invalidate the measurement;
- destructive/shared-state action requiring approval;
- a new architecture mechanism proposal.

Do not wait for 174 V2 to finish before performing the candidate-neutral Native evidence above.

At completion:

- commit;
- push;
- fetch-back;
- remote HEAD verify;
- remote tree verify;
- clean worktree;
- STOP for ChatGPT review.
