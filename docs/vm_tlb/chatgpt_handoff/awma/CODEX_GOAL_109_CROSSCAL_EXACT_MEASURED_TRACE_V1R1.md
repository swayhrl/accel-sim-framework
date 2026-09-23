# CODEX 109 GOAL — Exact Native Measurement Trace Recapture for Cross-Calibration V1R1

Date: 2026-09-23

Mode:

`GOAL MODE / bounded Native calibration recapture / solve-and-continue`

Node:

`109 / RTX4080`

Stage:

`AWMA_NATIVE_CROSSCAL_EXACT_MEASURED_TRACE_109_V1R1`

Read first:

`docs/vm_tlb/chatgpt_handoff/awma/REVIEW_NATIVE_SIMULATOR_CROSS_CALIBRATION_V1_2026-09-23.md`

Frozen Native authorities:

- V1R1:
  `589d0d579e8e9d30922d3842084c3c50f09833d7`
- exact M1/M2 V1R2:
  `1d56c7ff12bd273f0f27c0de24d308a255b50b56`

Purpose:

Create exact Native timing + simulator-native trace authority for the **measured 50-sample chase kernel**, not the 2-sample warmup kernel.

This is calibration evidence collection only.

No TLB/PTW/cache mechanism is designed.

## 1. Program/source authority

Use the accepted:

`native_tlb_probe_v1`

source semantics.

Prefer the exact accepted V1R2 source/binary if the binary survives and identity can be proven.

Accepted V1R2 source SHA256:

`cec9492b3d6dfeedab3cfcc3659523eaa6afebb2c0158499ad8c423b20d70f07`

Accepted V1R2 binary SHA256:

`a9488afa190ba1e27e58f840b07f1db092177c5a097773ce6a8934262e37357f`

If the exact binary is unavailable, rebuild from accepted source and record the new binary SHA. Do not change program semantics.

## 2. Freeze exact command authority

Use all four configurations with explicit command-line values.

Common:

```text
steps = 512
samples = 50
warmup-batches = 2
policy = default
seed = 102
thrash = disabled
```

M0:

```text
stride = 4096
locations = 16
warps = 1
```

M1:

```text
stride = 4096
locations = 4096
warps = 1
```

M2:

```text
stride = 4096
locations = 4096
warps = 16
```

M3:

```text
stride = 65536
locations = 1024
warps = 1
```

Publish the literal argv for every run.

Do not rely on defaults.

## 3. Fresh uninstrumented Native timing

For M0–M3:

- execute 3 independent processes each;
- same explicit command;
- no NSYS/NCU/NVBit;
- record all 50 measured samples per warp from the host-visible output;
- preserve raw output;
- compute per-process mean/median/p10/p90/CV;
- compute median-of-medians;
- for M2 retain per-warp/sample information where output permits and pooled summary.

These new timings become the exact reference for the repaired cross-calibration.

Recompute exact M1→M2 relative change from these contemporaneous runs.

Do not force reproduction of the old -4.5840%.

If the new exact reference differs, report the new measurement honestly and retain V1R2 as historical accepted evidence.

## 4. Exact trace-capture identity

Using the same explicit program command, capture the chase sequence with the qualified Route-B/NVBit lifecycle.

The source launch order is:

1. `chase occurrence0`: warmup, samples=2;
2. `chase occurrence1`: measured, samples=50;
3. `overhead`: later and not part of the primary calibration observable.

Required trace authority for each M0–M3:

- capture and identify BOTH `chase_occurrence_0` and `chase_occurrence_1` from the same program process/context;
- preserve ordering;
- bind both payloads to the same process/run ID and command authority;
- zero drop;
- zero overflow;
- xz integrity PASS;
- format/grammar validation PASS;
- exact source/binary/GPU UUID authority.

Prefer one producer execution that records both selected chase occurrences.

If the existing selector infrastructure can only select one occurrence, make the minimum engineering extension required to capture the two exact occurrences in one process without changing the benchmark program.

Do not capture only occurrence1 if doing so loses the ability to reconstruct the warmup→measurement context.

## 5. Verify bracket count

For each payload:

### warmup occurrence0

Expected complete clock brackets:

`warps × 2`

### measured occurrence1

Expected complete clock brackets:

`warps × 50`

Explicit expected measured counts:

```text
M0 = 50
M1 = 50
M2 = 800
M3 = 50
```

Use trace/SASS inspection to verify.

If occurrence1 does not contain the expected count, STOP:

`MEASURED_TRACE_BRACKET_COUNT_MISMATCH`

## 6. Address/permutation authority

Because seed is explicit:

`seed=102`

record it in every durable receipt.

Where practical, derive a normalized address-sequence fingerprint for the dependent load stream, independent of allocation base address.

For example, hash:

- page/stride-relative index sequence;
- or another deterministic normalized sequence derived from the trace.

Use it to prove M1 timing and M1 trace use the same benchmark permutation contract, likewise M2.

Do not compare raw absolute VAs across independent processes as though allocation base must match.

## 7. Durable publication

Publish immutable bundles to node164.

Each configuration must contain:

- full CLI;
- source/binary hash;
- GPU UUID;
- Native raw timing;
- timing summary;
- warmup occurrence0 trace;
- measured occurrence1 trace;
- ordered pair receipt;
- payload SHA256;
- drop/overflow receipt;
- xz/grammar status;
- normalized sequence fingerprint if generated;
- manifest;
- destination verification ACK.

No trace timing is used as Native timing.

## 8. Evidence classes

Use:

`NATIVE_UNINSTRUMENTED_TIMING_EXACT_V1R1`

for timing.

Use:

`SIMULATOR_NATIVE_CONTEXT_PAIR_EXACT_V1R1`

for the ordered warmup+measurement trace pair.

Do not merge them into one timing class.

## 9. Deliverables

Suggested branch:

`hrl/awma-109-native-crosscal-exact-measured-trace-v1r1`

Report:

`docs/vm_tlb/codex_handoff/awma/NATIVE_CROSSCAL_EXACT_MEASURED_TRACE_109_V1R1_REPORT.md`

Review pack:

`docs/vm_tlb/review_packs/AWMA_NATIVE_CROSSCAL_EXACT_MEASURED_TRACE_109_V1R1/`

Required:

```text
README.md
SOURCE_ANCHORS.md
COMMAND_AUTHORITY.tsv
NATIVE_TIMING_RAW_INDEX.tsv
NATIVE_TIMING_SUMMARY.tsv
M1_M2_EXACT_CHANGE.tsv
TRACE_PAIR_AUTHORITY.tsv
TRACE_BRACKET_COUNTS.tsv
ADDRESS_SEQUENCE_FINGERPRINT.tsv
RUN_RECEIPTS.json
RAW_DATA_INDEX.tsv
DURABLE_PUBLICATION_ACK.md
SHA256SUMS
```

If a normalized fingerprint is not technically meaningful, explain and use a clearly named NOT_APPLICABLE row instead of fabricating one.

## 10. Stop boundary

Do not run Accel-Sim on 109.
Do not run NCU/NSYS unless required for a purely engineering selector identity issue; they are not needed for primary evidence.
Do not alter the benchmark semantics.
Do not design a new mechanism.

Ordinary capture/selector/publication engineering problems solve-and-continue.

STOP only for:

- source/binary authority cannot be established;
- the two chase occurrences cannot be captured from one process without changing benchmark semantics;
- measured occurrence1 bracket identity cannot be closed;
- scientific payload corrupt/missing after capture.

Complete Git publication/fetch-back/hash verification/clean worktree and STOP.
