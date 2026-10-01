# Codex Goal — Lane F / node109
## R19F1 Ada FP8 numerical decomposition and readiness boundary V1

Date: 2026-10-01

Execution branch:
`hrl/awma-r19f1-fp8-readiness-109-v1`

Scientific parent:
`63de02aa82587680baca665d09101dc8c67222a2`

This is a bounded solve-and-continue follow-up. It does **not** relax or reinterpret the failed V1 allclose gate. It creates a new, representation-matched numerical contract so representation error and FP8 consumer-compute error are not conflated.

## 0. Fixed authority

Reuse exactly:
- TE v2.19.0 / source commit `5e52befd5262c06289106338c308079d6adb391f`
- RTX4080 / SM89
- accepted Qwen2.5-0.5B real input
- exact layer0 `mlp.up_proj` input/weight payload
- M/N/K = 256 / 4864 / 896
- Float8CurrentScaling(E4M3) recipe
- same isolated R19 environment unless a deterministic repair is required.

Parent real payload SHA:
`5ac9e6eb35ec2676926481d563628b80d528dac3dbdbe87bece26d21f4c54b48`

Do not change model, prompt, shape, recipe or precision family.

All CUDA/NSYS/NCU work uses:
`/data/c16/locks/c16_gpu_campaign.lock`

## 1. Why this follow-up exists

V1 compared the complete FP8 path against the original BF16 linear output using TE's E4M3 elementwise tolerance and stopped.

Source audit after V1 showed that TE's own quantized GEMM tests use a representation-matched reference:
- test values are quantized;
- the represented/dequantized values are copied into the reference tensors;
- quantized GEMM output is compared against computation on those representable values.

Therefore V1 mixed:
1. BF16 -> FP8 representation distortion;
2. FP8 GEMM / consumer execution error.

This Goal separates them.

The old V1 gate remains a valid historical STOP and is never relaxed.

## 2. F1A — construct three frozen numerical objects

From the exact real Qwen payload create:

### B0_ORIGINAL
`y_bf16 = linear(x_bf16_original, w_bf16_original)`

This is only the original-format reference.

### R0_REP_MATCHED
Use the exact TE current-scaling quantizers / representation path to create the same FP8 input and FP8 weight representation that the native consumer uses.

Dequantize those exact representations to BF16 or FP32:
- `x_rep`
- `w_rep`

Compute:
`y_rep_ref = linear(x_rep, w_rep)`

Use a reference dtype/path that does not itself invoke FP8.

### F0_TE_FP8
Run the TE native FP8 consumer on the same exact FP8 representations / equivalent current-scaling representation.

Record:
- quantized payload hashes where accessible;
- quantizer/scaling metadata;
- dequantized representation hashes;
- output hashes;
- all finite status.

Do not generate an unrelated second quantization of the tensors for the matched reference.

## 3. Numerical qualification

### 3.1 Consumer-compute gate

Primary correctness gate:
`F0_TE_FP8` versus `R0_REP_MATCHED`.

Use the source-backed TE v2.19 E4M3 quantized-compute tolerance:
- atol = 0.0675
- rtol = 0.125

Also report:
- max abs
- mean abs
- RMSE
- cosine
- percentile absolute error if convenient.

This is the only pass/fail numerical gate for allowing readiness timing.

If it fails:
`R19F1_FP8_REP_MATCHED_NUMERICS_NOT_QUALIFIED`
STOP.

### 3.2 Representation distortion

Separately compare:
`B0_ORIGINAL` versus `R0_REP_MATCHED`.

Report the same error statistics.

Do **not** reuse the failed V1 allclose as a new pass/fail gate.
Do not claim application-level model quality from one layer.

This comparison answers only:
"what numerical difference comes from choosing this FP8 representation for this real tensor pair?"

## 4. F1B — prove native consumer identity

Before formal timing prove, using source/runtime evidence plus at most one NSYS capture if needed, that the current-scaling TE path actually launches an FP8 GEMM/consumer path on SM89 rather than silently using BF16 GEMM.

A metadata flag alone is not sufficient if the runtime path is ambiguous.

Save exact kernel/timeline identity at the level that the available profiler reliably provides.
No SASS/NVBit is required.

If native FP8 compute identity cannot be established:
`R19F1_FP8_CONSUMER_IDENTITY_NOT_QUALIFIED`
STOP.

## 5. F1C — exact same-consumer readiness decomposition

The causal question is not BF16 versus FP8.

Construct two FP8-contract arms using the same frozen representation and same consumer.

### A1_ONLINE
Normal online current-scaling representation path:
`real BF16 input ready -> input FP8 representation ready -> same FP8 consumer -> output committed`

Weight behavior:
- use the normal steady-state frozen-weight cache/reuse contract;
- first-microbatch weight conversion/JIT is recorded separately;
- primary timing uses steady state after the official cached-weight path is established.

### D0_READY
The exact FP8 input representation is prepared before the measured interval, and the same FP8 consumer executes using:
- the same represented input bits/scales;
- the same cached FP8 weight representation;
- the same output dtype/math.

D0 is allowed only if pinned TE public/source-supported APIs can feed a prequantized input into the same underlying consumer path without changing its GEMM/math contract.

Preferred implementation is TE's own quantized/fusible operation path if it proves same consumer backend.

Do not use a different custom GEMM or an unrelated lower-level kernel and call it readiness.

If no exact same-consumer ready-representation path can be qualified:
`R19F1_READY_REP_DIAGNOSTIC_NOT_QUALIFIED`
STOP after publishing the source/API finding.

## 6. Timing

Only after Sections 3–5 pass.

For A1_ONLINE and D0_READY:
- 3 paired groups
- 2 warmups + 5 formal repeats per arm/group
- alternate arm order
- save every sample
- median/MAD.

Primary interval:
`input state at arm boundary -> FP8 consumer output committed`

A1 includes per-call input quantization/scale/layout work.
D0 excludes only the representation preparation moved before the boundary.
Both include the same consumer and output commitment.

Any small metadata/reset required by D0 is included unless truly outside both deployment boundaries.

Also record:
- A1 input-representation bytes/metadata
- cached weight bytes/metadata
- allocation deltas
- representation-prep launches
- consumer launches
- first-call/JIT separately.

BF16 B0 may be timed as context only if cheap and already available, but:
- B0-A1 is **not** architecture headroom;
- it is a precision/format tradeoff.

## 7. Profiling

If A1-D0 shows a stable difference or timing identity is ambiguous:
- at most one NSYS capture containing A1 and D0 separate NVTX ranges;
- at most one exact NCU target, only if needed to distinguish representation work from mandatory consumer work.

Query SM89-supported metrics first.

No NVBit/SASS.
No Blackwell FP4/TMEM claim.

## 8. Decision labels

Use exactly one:

- `R19F1_FP8_REP_MATCHED_NUMERICS_NOT_QUALIFIED`
- `R19F1_FP8_CONSUMER_IDENTITY_NOT_QUALIFIED`
- `R19F1_READY_REP_DIAGNOSTIC_NOT_QUALIFIED`
- `R19F1_FP8_READINESS_STRONG_SOFTWARE_SUFFICIENT`
- `R19F1_FP8_READINESS_RESIDUAL_PRESENT`
- `R19F1_FP8_RESULT_MIXED_NEEDS_REVIEW`

### Software sufficient

Use when same-consumer A1 vs D0 shows no stable material complete-operator difference worth architecture review.

A 5% complete measured-region improvement is the preregistered **investment screen for this Goal**, not a universal scientific law.

### Residual present

Require:
- representation-matched numerical gate passed;
- real native FP8 consumer identity proved;
- A1 and D0 use same represented values and same consumer;
- D0 improves the complete measured region by >=5%, stably across paired groups;
- the difference is localized to representation readiness rather than first-call/JIT or different GEMM math.

This is review-only.
Do not start hardware or 174 automatically.

## 9. Forbidden

Do not:
- relax the V1 elementwise gate and call it the same experiment;
- change recipe/model/shape;
- use random matrices for scientific performance;
- introduce custom FP8 GEMM;
- claim application accuracy from one linear layer;
- claim Ada FP8 result as Blackwell FP4 result;
- start node174/Accel-Sim/hardware mechanism.

## 10. Deliverables

Review pack:
`docs/vm_tlb/review_packs/AWMA_R19F1_FP8_NUMERIC_DECOMPOSITION_109_V1/`

At minimum:
- README.md
- PARENT_AUTHORITY.json
- NUMERICAL_DECOMPOSITION.md
- REPRESENTATION_RECEIPT.json
- REP_MATCHED_NUMERICS.tsv
- REPRESENTATION_DISTORTION.tsv
- CONSUMER_IDENTITY.md
- D0_QUALIFICATION.md
- TIMING.tsv if triggered
- PROFILE_SUMMARY.tsv if triggered
- FINAL_DECISION.md
- RUN_RECEIPTS.json
- RAW_DATA_INDEX.tsv
- SHA256SUMS

Large raw stays on node164.

## 11. Closure

Release GPU lock.
Commit/push/fetch-back exact SHA/tree.
Clean worktree.
STOP.

Do not auto-start a new precision path after closure.
