# Codex Goal — Lane F / node109
## R19 Ada FP8 representation-readiness boundary V1

This is one bounded solve-and-continue Goal.

Execution branch:
`hrl/awma-r19-fp8-readiness-109-v1`

## Question

On RTX4080/SM89, using a mature native FP8 implementation, how much of a real linear/MLP operator's complete time and state is spent making the representation ready (amax/scale/quantized payload/layout) versus mandatory GEMM/consumer work?

This is **Ada FP8 evidence only**. It must not be presented as Blackwell FP4/TMEM evidence.

## F0 — runtime/source qualification

Use an isolated environment.

Pinned strong baseline:
- Transformer Engine v2.19/v2.19.0
- source commit `5e52befd5262c06289106338c308079d6adb391f`

Verify on node109:
- SM89
- CUDA/cuBLASLt requirements for Ada FP8
- TE import/runtime
- exact recipe used
- whether delayed scaling/current scaling path is supported in this exact build.

Prefer stable v2.19 packages/source; do not silently use current main after timing starts.

If native TE FP8 cannot run legally on SM89 after bounded environment repair:
`R19_FP8_RUNTIME_NOT_QUALIFIED`, STOP.

## F1 — real activation/weight input

Do not use random matrices for scientific performance.

Reuse an accepted local Qwen model/input if available, preferably the already-used Qwen2.5-0.5B authority from exact-loss/R101 assets.

Run one deterministic real prompt/model forward and hook one natural MLP projection input plus its real weight:
- prefer the first supported `up_proj` or equivalent dense linear whose dimensions are TE-compatible;
- if the first candidate is unsupported for alignment, choose the next natural projection and record why.

Freeze:
- model revision/hash
- prompt/token IDs
- layer/module name
- input tensor hash, shape, dtype
- weight tensor hash, shape, dtype.

If no accepted real asset can be recovered without inventing a workload:
`R19_FP8_REAL_INPUT_NOT_QUALIFIED`, STOP.

## F2 — arms

Use the same frozen real input and weight.

A0:
- strong BF16 linear reference using the best ordinary implementation available in the same PyTorch environment.

A1:
- TE FP8 complete operator under one pinned supported recipe.
- include all representation work intrinsic to the normal call boundary.

D0 diagnostic, only if TE public APIs allow it without changing math:
- pre-create/reuse the same quantized input/weight representation and metadata, then execute the consumer path.
- This is a diagnostic separation of representation readiness, not a deployment claim and not automatically a strict oracle.

Do not create a custom FP8 kernel in this Goal.

## F3 — correctness

Before timing:
- finite outputs
- same input/weight
- report max_abs, mean_abs, max_rel, cosine
- freeze engineering tolerance before formal timing based on TE examples/tests and FP8 characteristics.
- do not change tolerance after seeing timing.

Also verify the FP8 path is genuinely using supported FP8 execution, not a silent BF16 fallback.

## F4 — timing

All CUDA work under shared lock.

For A0/A1 and D0 if qualified:
- 3 paired groups
- 2 warmups + 5 formal repeats/group
- alternate arm order
- save every sample, median/MAD.

Primary interval:
`real input + real weight ready -> output committed`

Record:
- full operator time
- peak allocated/reserved delta
- any persistent quantized-weight cache/reuse
- representation metadata bytes
- whether first-call and steady-state semantics differ.

Do not mix compile/JIT startup into steady-state unless it is inherently per-call.

## F5 — bounded profiling

Only if A1 shows a material difference or D0 suggests a representation-readiness component worth explaining:
- at most one NSYS capture of A1 and D0 in separate NVTX ranges;
- at most one exact NCU target selected from that timeline.
- query SM89-supported metrics first.

Do not infer DRAM traffic from allocator bytes.

## Decisions

Use exactly one:

- `R19_FP8_RUNTIME_NOT_QUALIFIED`
- `R19_FP8_REAL_INPUT_NOT_QUALIFIED`
- `R19_FP8_STRONG_SOFTWARE_SUFFICIENT`
- `R19_FP8_REPRESENTATION_READINESS_RESIDUAL_PRESENT`
- `R19_FP8_RESULT_MIXED_NEEDS_REVIEW`

Residual-present requires:
- real input
- native Ada FP8 path
- numerical contract passed
- a reproducible complete-operator component tied to representation readiness rather than mandatory GEMM
- not merely first-call initialization/JIT.

No architecture or 174 work is authorized.

Review pack:
`docs/vm_tlb/review_packs/AWMA_R19_FP8_READINESS_109_V1/`

Publish exact receipts, raw hashes, branch/commit/tree, release GPU lock, clean worktree, STOP.
