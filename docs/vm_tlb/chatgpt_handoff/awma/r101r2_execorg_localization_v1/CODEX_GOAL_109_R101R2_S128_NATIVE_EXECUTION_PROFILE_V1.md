# CODEX GOAL — node109 R101R2 S128 Native Execution Profile V1

Run on **node109 / RTX4080 / SM89** in Lane F.

Suggested execution branch:

`hrl/awma-r101r2-s128-native-profile-109-v1`

Coordination branch:

`hrl/awma-r101r2-execorg-localization-v1-handoff`

Read first:

`docs/vm_tlb/chatgpt_handoff/awma/r101r2_execorg_localization_v1/START_HERE.md`

Stage:

`AWMA_R101R2_S128_NATIVE_EXECUTION_PROFILE_V1`

## 1. Question

The accepted Native same-map result is already frozen:

- F128 graph median ~0.493408 ms;
- K128 graph median ~0.623488 ms;
- F128 improvement 20.86%;
- independent holdout 20.09%.

Do **not** rerun this Goal to obtain a new performance headline.

Instead answer:

> What execution work and memory-path activity does F128 remove or reorganize relative to K128 on the exact accepted S128 scientific payload?

This is a diagnostic profile, not a mechanism.

## 2. Accepted authorities

R101:

`cfbe6503585fa1b10d979db5d26fb9be3a80e563`

Durable root:

`/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/r101_fixed_ns_intermediate_lifecycle_20260927/`

Accepted discovery S128 payload SHA256:

`09358f3f21265a9c3a8cdd9681efdaa93a06db7c8d1e1afdbb017e60f0e85544`

Pinned HiMuon:

`tang0389/himuon@af89eda9a0176effed99e1fe19cc1f8a1a2c9588`

Accepted coefficients:

`3.4445, -4.7750, 2.0315`

NS steps:

`5`

Accepted discovery outputs/reference from R101 review pack remain authority. Do not regenerate gradients.

If the accepted S128 scientific payload cannot be recovered or deterministically reconstructed to the exact SHA:

`R101R2_NATIVE_INPUT_NOT_RECOVERABLE`

and STOP.

## 3. Arms

Use exactly the accepted same-map pair.

### F128

Author `ns5_smem` fused single-CTA path on the full accepted 581-tile S128 batch.

### K128

Author compiled three-kernel path:

`XXT -> ba_plus_cAA -> fused_bmm_add`

for five iterations on the same 581 tiles.

No:
- tile change;
- coefficient change;
- Gram NS;
- Flash-Muon;
- fused-muon substitution;
- step-count change.

## 4. Correctness/path gate

Before profiling:

- exact accepted input SHA;
- exact source commit;
- output finite;
- accepted numerical contract `rtol=atol=1e-2`;
- F128/K128 same-map pair closes;
- actual intended F128 and K128 kernel paths close;
- JIT/autotune stabilized before formal profiling.

Record exact:
- kernel names;
- grid/block;
- cubin/module hashes where available;
- register/shared launch metadata.

Do not choose an alternate autotune result based on profiler performance.

If profiler replay changes the kernel configuration between compared captures, repair/freeze source-equivalent configuration before interpreting counters.

## 5. Reuse accepted timing/NSYS when possible

The R101 pack already establishes:
- graph timing;
- eager timing;
- F128 one fused NS kernel versus K128 fifteen NS-family kernels;
- path correctness.

Read/reuse that evidence.

Do not rerun NSYS unless a specific profile identity field needed by this Goal is absent.

If one NSYS canary is needed, it is diagnostic only and not new timing authority.

## 6. Static SASS/cubin analysis

For each unique kernel in the F128 and K128 paths, collect static disassembly when available.

Classify at minimum:

- global-memory load/store instructions;
- shared-memory load/store instructions;
- tensor/MMA instructions;
- integer/address/control instructions;
- synchronization/barrier instructions.

Static counts are per kernel binary, not dynamic execution counts.

Weighting static counts by launch geometry is allowed only as a clearly labeled derived estimate, never as measured dynamic instruction count.

## 7. Compact NCU profiling

All CUDA work must hold:

`/data/c16/locks/c16_gpu_campaign.lock`

Resolve metric names against the actual installed NCU first.

Create:

`NCU_METRIC_PREREGISTRATION.md`

The metric set must be compact and cover supported equivalents for:

### Execution work
- total executed instructions;
- active cycles;
- issued/active warp activity;
- tensor/math-pipe activity.

### Global-memory instruction work
- executed global load instruction count if supported;
- executed global store instruction count if supported;
- otherwise the closest source/SASS-level dynamic memory-instruction counters available on SM89.

### Memory hierarchy
- L1/TEX sectors or bytes;
- L2 requested/read/write bytes or sectors;
- DRAM read/write bytes.

### Resource metadata
- registers/thread;
- shared memory/block;
- achieved occupancy or active warps.

Do not silently replace an unavailable metric with a different semantic quantity. Record `UNSUPPORTED` and the selected nearest supported metric separately.

Maximum formal NCU collection:

- one F128 profile bundle;
- one K128 profile bundle.

A bounded retry is allowed only for selector/replay/metric engineering failure, not to search for favorable counters.

Do not use NCU replay duration as primary timing.

## 8. Accounting

Produce a family-level table that separates:

- F128 fused kernel;
- K128 normalization;
- K128 XXT;
- K128 BA;
- K128 BMM-add.

For K128 sum the five iterations only where the metric is additive.

Do not average percentages by simple summation.

Required derived comparisons include:

- total dynamic executed instructions ratio;
- global load/store instruction ratio where qualified;
- L2 traffic ratio;
- DRAM traffic ratio;
- tensor/math activity comparison;
- active-cycle comparison;
- launch/kernel-count difference.

## 9. Interpretation boundary

This Goal alone does not decide the final R101R2 classification.

Prepare facts for joint review with the 174 O2 result.

Useful classifications for the Native side only:

### `NATIVE_PROFILE_EXECUTION_WORK_REDUCTION_CLEAR`

Allowed when F128 materially reduces dynamic instruction/global-memory instruction/kernel work relative to K128 and the evidence is counter-consistent.

### `NATIVE_PROFILE_MEMORY_ACTIVITY_REDUCTION_CLEAR`

Allowed when memory-hierarchy activity is the strongest measured difference.

### `NATIVE_PROFILE_MIXED`

Use when both are substantial or counter limitations prevent a clean decomposition.

Do not claim causality from profiler counters alone.

## 10. Publication

Durable root:

`/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/r101r2_s128_native_profile_20260929/`

Review pack:

`docs/vm_tlb/review_packs/AWMA_R101R2_S128_NATIVE_EXECUTION_PROFILE_109_V1/`

Minimum:

- README.md
- R101_INHERITANCE.md
- INPUT_AND_PATH_RECEIPT.json
- NCU_METRIC_PREREGISTRATION.md
- KERNEL_IDENTITY.tsv
- STATIC_SASS_SUMMARY.tsv
- NCU_RAW_METRIC_BINDING.tsv
- NCU_FAMILY_SUMMARY.tsv
- NATIVE_PROFILE_INTERPRETATION.md
- RAW_DATA_INDEX.tsv
- SHA256SUMS

Final states:

- `R101R2_NATIVE_PROFILE_PASS`
- `R101R2_NATIVE_INPUT_NOT_RECOVERABLE`
- `R101R2_NATIVE_PROFILE_NOT_QUALIFIED`

On closure:
node164 -> review pack -> hashes -> commit -> push -> fetch-back -> exact remote SHA/tree -> clean -> GPU release -> STOP.

Do not wait for Lane E before publication.
