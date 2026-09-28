# C16 Lane 7 Handoff — Low-bit Split-K Native A/B on node109

**Date:** 2026-09-28  
**Execution node:** `109`  
**Lane:** `Lane 7`  
**Role:** C16 native GPU producer / bounded experiment executor  
**GPU:** RTX 4080 / SM89  
**GPU lock:** REQUIRED for every command that creates a CUDA context or runs GPU work  
**GPU lock path:** `/data/c16/locks/c16_gpu_campaign.lock`  
**Can run in parallel with:** Lane 4 on 174-new, Lane 6 on 174-new  
**Must not access:** Lane 4 active outputs / partial timing  
**Goal:** `C16_LOWBIT_SPLITK_NATIVE_AB_109_V1`

## 1. Why this lane exists

Lane 5 on 174-new completed a read-only screen of the existing accepted E1 evidence and retained exactly one bounded hypothesis:

> The deployed fixed `split_k_iters=8` policy may be net-costly at `M=256`, because it creates eight FP16 partial-output planes plus a separate global reduction. A no-split path may reduce module time enough to outweigh the loss of K-parallelism.

This is **not** an accepted cause of E1 and is **not** a novelty claim.

The accepted low-bit execution already shows:
- `up_proj` M1: AWQ faster than RAW FP16.
- `up_proj` M256: AWQ slower than RAW FP16.
- `down_proj` M1: AWQ faster than RAW FP16.
- `down_proj` M256: AWQ slower than RAW FP16.
- In accepted `up_proj M256` Semantic NCU V2 evidence, the separate reduction kernel contributes a material fraction of semantic-range traffic, including about 42.65% of DRAM bytes.
- The executed AWQ source uses a `16x128x32` CTA tile and fixed `split_k_iters=8` for accepted `up_proj` M1/M256 launches.
- The wrapper allocates `[split_k_iters, M, N]` FP16 partial output and then runs a separate `sum(0)` reduction.

Lane 7 is authorized to execute **one bounded native A/B** that tests this split-policy bundle. It does not investigate cross-token qweight residency and does not depend on Lane 4.

## 2. Read-only authorities

### 2.1 Lane 5 design authority

Repository: `swayhrl/accel-sim-framework`  
Branch: `hrl/c16-lowbit-dataflow-screen-v1`  
HEAD: `dcbd60f98753ec678642bd4be745469409ffb734`

Read first:
- `docs/vm_tlb/review_packs/C16_LOWBIT_DATAFLOW_SCREEN_V1/DATAFLOW_EVIDENCE.tsv`
- `docs/vm_tlb/review_packs/C16_LOWBIT_DATAFLOW_SCREEN_V1/HYPOTHESIS_SCREEN.md`
- `docs/vm_tlb/review_packs/C16_LOWBIT_DATAFLOW_SCREEN_V1/MINIMAL_NATIVE_AB_PLAN.md`

Do not silently modify the preregistered A/B question, arms, correctness tolerance, measurement set, or decision rule.

### 2.2 Accepted E1 clean producer

Branch: `hrl/c16-e1-clean-baseline-109-v1`  
HEAD: `8988d6108ff8bdca180a14cec2fe769df45b09f1`  
Accepted consumer authority: `59ddb8ba2a33ef12b73bfc859f3a994e0b4ef4ca`

Use the producer pack and local `/data/c16/e1_clean_baseline_v1` authority to bind inputs and accepted A-arm behavior. Do not regenerate the clean workload.

### 2.3 Semantic NCU V2

Producer branch: `hrl/c16-e1-semantic-ncu-cache-state-repair-109-v1`  
HEAD: `8d1f62229cae15199793ba5569327cf1e83596f3`  
Independent consumer: `cdd3ec7afbb1611cc52a4b74d32b38a3edabd131`

Accepted profiler contract:
- `--replay-mode application`
- `--cache-control none`
- metrics only: `l1tex__t_bytes.sum,lts__t_bytes.sum,dram__bytes.sum`
- two warmups outside selected NVTX range
- Nsight Compute 2025.1.1.0

Do not broaden the metric sweep.

### 2.4 Historical deployed AWQ implementation

Accepted runtime environment: `/data/c16/env/c16-awq-v6`

Historical source:
`AutoAWQ_kernels@c7b0e88c327694c715b0a758d9ce8fd414a1fa21`

Recorded source tree:
`5450e7dd4e00bc4010c3ec83411f5b9877f49af7`

Earlier receipts bind:
- `awq_ext` SHA256: `9e8d38a04c28770338fcef8ae0f9a90a984b7a8f95bcb98a407738594e1c08d7`
- wheel SHA256: `746976c45a3f12ebe6a1e20706b8ba7b94071e03b9c3f9bc4bd4f0cf495c223e`

Never overwrite the accepted `awq_ext`, wheel, or `c16-awq-v6` environment.

## 3. Exact four experiment points

Model: `Qwen/Qwen2.5-7B-Instruct-AWQ`  
Revision: `b25037543e9394b818fdfca67ab2a00ecc7dd641`  
Layer: `model.layers.0`

| Point | Accepted FP16 input SHA256 | Accepted A output SHA256 |
|---|---|---|
| `up_proj_M1` | `b3999f6fe161d47efdff4c7d88aa044e2cec3396f9c69fde63c53f2ba208f82e` | `5618125fc9563f42860d5df37ae9b4b6569dfc4af1d995eeb7922d9f60b31d99` |
| `up_proj_M256` | `eeae491edfdbee761de47aa6c4ea35b293bb2796227927778fa51c9e58ef1b41` | `59b56af85d0480542fa396a655f23179f879eccaa9ab32a7b98ba88e8cb33d50` |
| `down_proj_M1` | `e39ee4d42396f044115b2ec20734c5a0b7d41958c642ad264b1cbbe597aa2c59` | `ccfcd3eb82b4f60eabf13950b9739a6a2098ee23f6bbe347a12492520fc71689` |
| `down_proj_M256` | `a1f158a113f56314f4ee5f4a5f10ee41ac9afe732a4f1735b88a1c01b25b9aff` | `34dfa2432bd3598dcbd694b576d52b74f08b43e38f231d44f6a10a949f0de477` |

Before timing, derive these again from committed authority and fail on disagreement.

## 4. A/B definition

### Arm A — `ACCEPTED_SPLIT8`
- exact historical AWQ source/runtime;
- same `gemm_forward_4bit_cuda_m16n128k32`;
- `split_k_iters=8`;
- scratch `[8,M,N]`;
- separate `sum(0)` reduction;
- no modification to accepted environment.

A must reproduce accepted output SHA exactly for all four points.

### Arm B — `NO_SPLIT1_DIRECT_OUTPUT`
Build an isolated variant from the exact historical source. Only:
- set `split_k_iters=1`;
- preserve qweight layout, qzeros/scales, dequant math, CTA tile, K32 loop, datatype, group size, model asset and backend;
- return/select the sole `[1,M,N]` plane directly while preserving public output shape/dtype;
- no separate one-plane reduction.

Never overwrite the accepted `.so`.

Record source commit/tree, source SHAs, exact patch, compiler/nvcc, build command, produced binary SHA, import/runtime path.

## 5. Expected launch/scratch contract

| Point | A GEMM grid | B GEMM grid | A scratch bytes | B scratch bytes | A reduction | B reduction |
|---|---:|---:|---:|---:|---|---|
| `up_proj_M1` | 1184 | 148 | 303104 | 37888 | present | absent |
| `up_proj_M256` | 18944 | 2368 | 77594624 | 9699328 | present | absent |
| `down_proj_M1` | 224 | 28 | 57344 | 7168 | present | absent |
| `down_proj_M256` | **3584 predicted** | 448 | 14680064 | 1835008 | present | absent |

`down_proj_M256` A grid=3584 is a preregistered source prediction, not prior accepted dynamic evidence; verify it before interpretation.

## 6. GPU lock discipline

Every CUDA execution must hold `/data/c16/locks/c16_gpu_campaign.lock` using the established outer-flock pattern.

Rules:
1. never steal/delete/bypass the lock;
2. never kill another process to obtain GPU access;
3. if occupied, continue CPU-only prep if safe and wait/retry later;
4. pure CPU compilation/prep may run outside lock only if it creates no CUDA context;
5. emit `GPU_LOCK_RECEIPT.json` with lock path, start/end UTC, GPU model/UUID, driver, CUDA/runtime, pre/post `nvidia-smi`, acquisition/release state;
6. do not change clocks, power limit, persistence mode or driver settings;
7. stop before timing if current 109 platform materially differs from accepted authority.

## 7. New branch/worktree

Base on Lane 5 HEAD:
`dcbd60f98753ec678642bd4be745469409ffb734`

Suggested branch:
`hrl/c16-lowbit-splitk-native-ab-109-v1`

Suggested worktree:
`/home/huangrulin/workspace/worktrees/accel-sim-c16-lowbit-splitk-native-ab-109-v1`

Suggested raw root:
`/data/c16/e1_lowbit_splitk_native_ab_v1`

Never reuse old output directories.

## 8. Execution sequence

### Stage 0 — authority/preflight
Verify Lane 5, clean E1 producer, Semantic NCU V2, historical AWQ source, model/revision, accepted inputs and A outputs. Locate exact historical source and create isolated B build. Create run manifest before execution.

No model download, no requantization, no input regeneration.

### Stage 1 — build B
Surgical patch only. Ordinary build fixes may be solved-and-continue if math/experiment semantics do not change.

Stop if B requires changing qweight representation, dequantization arithmetic, CTA tile, dtype, group size or CUDA algorithm family.

### Stage 2 — A reproduction
Acquire GPU lock. For all four points:
- exact input hash;
- unmodified A execution;
- exact output hash;
- exact accepted output SHA required;
- launch inventory recorded.

Failure => `A_AUTHORITY_REPRODUCTION_FAIL`, stop before B timing.

### Stage 3 — B correctness
Same input/weights, same output shape/dtype, all finite.

Frozen tolerance:
- `rtol=1e-2`
- `atol=5e-2`

Record max_abs, mean_abs, relative_L2, changed element count, A/B SHA.

Any failure => `NUMERICAL_ORDER_CHANGE_REJECTS_AB`, do not time failed conditions.

### Stage 4 — launch audit
For A/B all points record kernel names, grid/block, launch order/count, scratch and reduction presence.

B must:
- use preregistered split1 grids;
- have no separate reduction;
- not fall back to another backend.

### Stage 5 — bounded timing
For each valid point:
- 10 untimed warmups per arm;
- 50 CUDA-event module samples per arm;
- 25 deterministic `A,B,B,A` blocks;
- synchronize sample boundaries;
- same process when safe;
- no unrelated CUDA work.

Report raw samples, median/min/max/mean/CV, paired/block deltas and B-vs-A fraction.

This is a bounded module microbenchmark, not full-model timing.

### Stage 6 — one bounded NCU pair
Only `up_proj_M256`, after correctness and launch gates.

Use accepted mode:
- NVTX
- `--target-processes application-only`
- `--replay-mode application`
- `--cache-control none`
- metrics exactly `l1tex__t_bytes.sum,lts__t_bytes.sum,dram__bytes.sum`
- two warmups outside NVTX

A: retain GEMM and reduction rows separately.  
B: verify reduction absent.

Do not infer tensor-level bytes from totals. Do not add a broad metric sweep.

If registers/shared/occupancy/kernel duration are already exposed without expanding the replay contract, record them; otherwise `UNKNOWN`.

## 9. Pre-registered interpretation

The four points selected the diagnostic; they are not an independent holdout.

`H1_SUPPORTED_BOUNDED` requires all:
1. correctness PASS all four;
2. B launch/scratch/reduction contract PASS;
3. B median module time improves >=5% at both M256 points;
4. improvement exceeds the larger A/B arm CV at each M256 point;
5. neither M1 point regresses >5%;
6. `up_proj_M256` B lowers semantic-range L2 or DRAM bytes in expected direction;
7. no available per-kernel evidence contradicts module result.

Other allowed decisions:
- `A_AUTHORITY_REPRODUCTION_FAIL`
- `NUMERICAL_ORDER_CHANGE_REJECTS_AB`
- `NO_NEW_OPPORTUNITY_FIXED_SPLIT8_NOT_MATERIAL`
- `OPERATOR_SPECIFIC_SPLIT_POLICY_ONLY`
- `TIMING_SIGNAL_ONLY_NEEDS_NO_AUTOMATIC_EXPANSION`
- `H1_SUPPORTED_BOUNDED`

Do not invent post-result thresholds. Do not call H1 the unique cause of E1 or a new split-K algorithm.

## 10. Required review pack

Create:
`docs/vm_tlb/review_packs/C16_LOWBIT_SPLITK_NATIVE_AB_109_V1/`

At minimum:
- `README.md`
- `SOURCE_AUTHORITY.json`
- `GPU_LOCK_RECEIPT.json`
- `BUILD_AND_BINARY_RECEIPT.json`
- `EXPERIMENT_MANIFEST.json`
- `INPUT_AND_WEIGHT_BINDINGS.tsv`
- `A_AUTHORITY_REPRODUCTION.tsv`
- `CORRECTNESS.tsv`
- `LAUNCH_AUDIT.tsv`
- `TIMING_SAMPLES.tsv`
- `TIMING_SUMMARY.tsv`
- `NCU_UP_M256_KERNEL_ROWS.tsv`
- `NCU_UP_M256_SUMMARY.json`
- `SOURCE_PATCH.diff`
- `FINAL_DECISION.json`
- `SCIENTIFIC_INTERPRETATION.md`
- `OPEN_ISSUES.md`
- `RAW_LOG_INDEX.tsv`
- `SHA256SUMS`

Commit scientifically relevant small raw timing/profiler exports. Large `.ncu-rep` may remain under `/data/c16/...` if path/size/SHA are recorded.

## 11. Claim boundary

Allowed:
- bounded Layer0 up/down M1/M256 native result;
- split8 vs split1 module timing;
- reduction traffic in the profiled scope.

Not allowed:
- unique E1 cause;
- full-model decode speedup;
- new split-K mechanism claim;
- Lane 4 explanation;
- L2 mechanism proof.

## 12. Absolute prohibitions

No:
- Lane 4 partial reading/modification;
- Accel-Sim;
- full-model timing;
- D1-D3 recapture/rescan;
- NVBit;
- requantization;
- MARLIN/QUICK/FLUTE installation/comparison;
- extra M values/operators/models;
- q_proj;
- split2/4/16 tuning;
- qweight/layout/dequant/tile changes;
- accepted `.so` replacement;
- clocks/power changes;
- GPU use without campaign lock.

This Goal is exactly split8 vs split1.

## 13. Solve-and-continue / STOP

Ordinary engineering problems may be fixed if the scientific contract is unchanged.

Stop for review if:
1. accepted source/binary/model/input authority cannot be reproduced;
2. A output SHA fails;
3. B needs changes beyond split policy;
4. 109 platform materially differs;
5. correctness fails;
6. GPU lock cannot be safely acquired;
7. extra shapes/operators/backends become necessary;
8. provenance cannot close.

A correctness failure should still publish the negative receipt and stop; do not “repair” B by changing the scientific arm.

## 14. Publication

`validate -> git diff --check -> SHA256SUMS -> commit -> push -> fetch-back verify exact commit/tree -> clean -> report -> STOP`

Do not amend/rewrite a correct scientific commit because of transport failure.

## 15. Persistent Lane 7 role

After this Goal, keep this Codex window as the persistent `node109 / RTX4080` GPU lane. Future C16 tasks requiring the 4080 and campaign lock should normally reuse Lane 7.

Do not autonomously start another GPU experiment after this Goal.
