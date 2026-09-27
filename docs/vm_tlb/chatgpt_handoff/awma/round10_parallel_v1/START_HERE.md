# START HERE — AWMA Round10 Parallel Exploration V1

## 0. Frozen authority

Execution base:
`d6ef29505de75985181afc74dffc3cf1b652afc2`

Coordination branch:
`hrl/awma-round10-parallel-exploration-handoff-v1`

Literature authority:
`hrl/awma-chatgpt-literature-notes-v1 @ 1dcf2cc9e4409010ec7f49d8afbefe0194ba0a8f`

Read:
`docs/vm_tlb/literature_notes/awma/rounds/2026-09-27_ROUND_10_HORIZONTAL_REVIEW_AND_NEXT.md`

Accepted Round08 results:
- R81: `69e74fe74e18d1f3a71bfac0d097ce49234327a9`
  -> `R81_SOFTWARE_OPPORTUNITY_NO_ARCH_CLAIM`
- R82: `385f38271466a01e7f9cedfe638355195057b7c8`
  -> `R82_CURRENT_SOFTWARE_SUFFICIENT_IN_SCOPE`

Do not rerun or reopen R81/R82.

## 1. Two independent lanes

### Lane H / R101
Goal:
`CODEX_GOAL_109_R101_FIXED_NS_INTERMEDIATE_LIFECYCLE_V1.md`

Suggested execution branch:
`hrl/awma-r101-fixed-ns-intermediate-lifecycle-v1`

Question:
for a fixed finite Newton–Schulz map, do intermediate matrices that cannot remain in one CTA's on-chip state create a material GPU-local lifecycle cost after the author's cross-layer batching, torch.compile and CUDA-graph software baseline?

### Lane I / R102
Goal:
`CODEX_GOAL_109_R102_PRECISION_GATED_UPDATE_ENCODING_V1.md`

Suggested execution branch:
`hrl/awma-r102-precision-gated-update-encoding-v1`

Question:
for an exact low-precision before/after model-weight update, does change detection + sparse payload compaction remain expensive after a bounded fused software implementation?

R102 is **input-authority gated**. It may finish without any GPU timing if no real update authority exists.

## 2. Parallel execution rules

Lane H and Lane I are independent Codex windows.

They may parallelize:
- literature/source audit;
- environment preparation;
- CPU tests;
- parsers;
- code review;
- raw/index/hash publication work that does not touch CUDA.

Every CUDA operation on node109 must hold:

`/data/c16/locks/c16_gpu_campaign.lock`

This includes:
- model load to GPU;
- Triton/CUDA JIT;
- warmup;
- canary;
- formal timing;
- NSYS;
- NCU.

Use separate:
- branch/worktree;
- Python environment;
- Triton/CUDA/HF caches when mutable;
- TMPDIR;
- raw/provenance staging.

Before releasing the GPU lock:
1. synchronize relevant CUDA streams/device;
2. stop the lane's GPU subprocesses;
3. release model/tensor allocations;
4. verify this lane leaves no resident CUDA process/allocation;
5. then unlock.

Do not kill or modify another lane's process.
Waiting for the GPU is not a scientific failure.
Do CPU work while waiting, or block on the existing lock without high-frequency polling.

## 3. Scientific rules

- Negative/not-qualified outcomes are valid.
- Small prototypes may be used to discover mechanism response.
- Final architecture promotion requires a real workload, strong software baseline, material stable effect, causal localization, and closest-work differentiation.
- Do not choose inputs/configurations after observing favorable performance.
- Do not replace missing scientific payload with synthetic data unless the Goal explicitly defines a labeled control.
- Do not silently relax correctness contracts.
- Do not use a software/algorithm change as a hardware gain.
- Do not start node174/Accel-Sim from these Goals.
- A READY_FOR_ARCH_REVIEW state only asks for later ChatGPT review.

## 4. Shared prohibited actions

- no new large model downloads;
- no driver/system-CUDA change;
- no full NVBit trace;
- no parameter sweep;
- no R81/R82 rerun;
- no automatic merge;
- no third GPU research lane inside these Goals.

## 5. Publication

node164 remains durable authority.

Each lane must:
`science/engineering -> node164 -> compact review pack -> hashes -> commit -> push -> fetch-back -> exact remote SHA/tree verification -> clean worktree -> GPU release -> STOP`.

Git transport failure is publication-only; never rerun science because push fails.
