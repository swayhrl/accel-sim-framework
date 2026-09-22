# CODEX 109 MICRO-CLOSURE — Exact M1/M2 Native Pair V1R2

Date: 2026-09-22

Mode:

`BOUNDED NATIVE MICRO-CLOSURE / solve-and-continue`

Node:

`109 / RTX4080`

Stage:

`AWMA_NATIVE_TRANSLATION_CALIBRATION_EXACT_PAIR_109_V1R2`

This is not a new calibration campaign. It closes one exact Native timing gap identified by ChatGPT review while 174-new V2 continues independently.

Read first:

1. `REVIEW_109_NATIVE_TRANSLATION_CALIBRATION_ANALYSIS_V1R1_2026-09-22.md`
2. `hrl/awma-native-calibration-analysis-109-v1r1 @ 589d0d579e8e9d30922d3842084c3c50f09833d7`
3. existing source `util/vm_tlb/awma/native_tlb_probe_v1/native_tlb_probe.cu`

## 0. Purpose

The accepted behavioral concurrency matrix uses 4 KiB stride × 1024 locations.

The selected simulator-native representative pair uses:

```text
M1 = 4 KiB stride × 4096 locations × 1 warp
M2 = 4 KiB stride × 4096 locations × 16 warps
```

M1 has existing Native timing; M2 does not have an exact uninstrumented Native timing point.

Close this exact pair now so later 174 cross-calibration does not compare mismatched working sets.

## 1. Hard scope

Do not run:

- NSYS
- NCU
- NVBit
- simulator-native recapture
- Accel-Sim
- Qwen model workloads

Use only the existing native microbenchmark binary/source path and lightweight CUDA-native `clock64()` timing.

No source-semantic change unless required for a clear engineering defect.

## 2. Exact configurations

Run only:

### M1 exact pair control

```text
stride_bytes = 4096
locations    = 4096
warps        = 1
steps        = 512
samples      = 50
policy       = default
warmup       = 2
seed         = existing accepted deterministic seed
```

### M2 exact pair

Same except:

`warps = 16`

Use the same binary, allocation policy, seed, steps, samples, cache policy, and warmup settings.

Run 3 independent process repetitions for each configuration.

If a repetition fails or is obviously malformed, solve-and-continue and document; do not silently discard valid high-variance measurements.

Do not add unrelated sweep points.

## 3. Analysis

For each repetition and each configuration record:

- sample count;
- mean cycles/load;
- median cycles/load;
- p10;
- p90;
- CV.

Then report across the 3 process repetitions:

- median-of-medians;
- range of medians;
- process-level stability;
- M1 -> M2 relative median change.

The classification is behavioral only.

Do not call the change a direct TLB throughput measurement.

## 4. Durable evidence

Publish the small raw timing output and analysis to node164 under the existing Native calibration provenance family.

No simulator trace recapture is needed.

Bind:

- source/binary authority;
- exact command;
- GPU UUID;
- raw output SHA256;
- durable path;
- destination SHA verification.

## 5. Deliverables

Execution branch suggestion:

`hrl/awma-109-native-calibration-exact-pair-v1r2`

Report:

`docs/vm_tlb/codex_handoff/awma/NATIVE_TRANSLATION_CALIBRATION_EXACT_PAIR_109_V1R2_REPORT.md`

Review pack:

`docs/vm_tlb/review_packs/AWMA_NATIVE_TRANSLATION_CALIBRATION_EXACT_PAIR_109_V1R2/`

Required:

```text
README.md
SOURCE_ANCHORS.md
M1_M2_EXACT_NATIVE_PAIR.tsv
RUN_RECEIPTS.json
RAW_DATA_INDEX.tsv
SHA256SUMS
```

## 6. Stop boundary

Ordinary path/build/runtime issues: solve-and-continue.

STOP after remote publication and clean worktree.

Do not modify or wait on 174-new.

Do not start simulator cross-calibration.
