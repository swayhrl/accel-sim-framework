# ChatGPT Scientific Review — 109 E1 V2 and 20h Unattended Decision

Date: 2026-09-20

Reviewed execution branch:

`hrl/awma-e1-shape-oracle-moe-harness-109-v2`

Reviewed final HEAD:

`56096d32bd5cd783286e1b5e5e612b6019f926d0`

Parent:

`137157d3a22c1b70e3bafa64ac9b56c3309fdcd9`

Ancestry:

exactly one execution commit ahead of the expected parent.

## 1. E1 V2 decision

Accepted status:

`E1_SHAPE_SPECIFIC_CORE_ACCEPTED_WITH_DEPLOYMENT_LEVEL_SCOPE`

Frozen AWQ runtime:

- gemm.py SHA256 = `7cdf8fb01dabbfcd7f8be8bb58dcaf68a76073f2f91fc0e7c96881094e6a2913`
- awq_ext SHA256 = `9e8d38a04c28770338fcef8ae0f9a90a984b7a8f95bcb98a407738594e1c08d7`
- dispatch condition = `x.shape[0] * x.shape[1] >= 1024`

Accepted path classification:

- M2048 -> `DEQUANTIZE_PLUS_TORCH_MATMUL`
- M256 -> `GEMM_QUANTIZED`
- M1 -> `GEMM_QUANTIZED`

Therefore:

`CROSS_SHAPE_OUTPUT_ORACLE_INVALID_CONFIRMED`

The former M2048-output-slice versus M256 direct-replay mismatch is retired as a replay-failure interpretation.

## 2. E1 core descriptive results

These are deployment-derived activation measurements, not a same-numeric-input semantic comparison.

Median native module times:

```text
q_proj M256:
raw 0.096480 ms
AWQ 0.132096 ms
AWQ/raw = 1.369

q_proj M1:
raw 0.023456 ms
AWQ 0.035680 ms
AWQ/raw = 1.521

down_proj M256:
raw 0.378880 ms
AWQ 0.472064 ms
AWQ/raw = 1.246

down_proj M1:
raw 0.214016 ms
AWQ 0.060992 ms
AWQ/raw = 0.285
```

The down_proj M1 contrast is the strongest reversal:
AWQ module latency is about 71.5% lower, or raw/AWQ about 3.51x.

This asymmetry makes implementation-path/resource diagnosis scientifically useful.

Do not describe these values as pure quantization speedups because raw and AWQ natural deployment activations/dtypes are not proven identical semantic inputs.

## 3. Why a 20h unattended stage is now appropriate

The previous short Goals were useful for contract repair, but several stops were caused by the workflow treating missing pre-existing engineering artifacts as scientific blockers.

For the next stage:

- missing helper/harness = implement and qualify it under the frozen contract;
- missing profiler selector = build an isolated replay/range canary;
- moved but hash-identical authority = recover/rebind it;
- absent derived table = reconstruct from accepted evidence;
- task-local scientific failure = freeze only that task and continue the queue.

A whole-Goal STOP is reserved for a shared identity/authority failure that invalidates every remaining task, or unsafe GPU ownership.

## 4. E3 decision

Current E3 status:

`HARNESS_NOT_MATERIALIZED`

This is not a negative scientific result.

The 20h stage explicitly authorizes materializing a test-only direct-experts harness from the exact frozen Q30 source, provided:

- natural N canary reproduces the accepted boundary;
- expert modules/weights/backend/residency are unchanged;
- dispatch/group/weight/combine semantics match the frozen source;
- P inverse-equivalence is required before U-active interpretation.

## 5. Next 109 stage

`AWMA_109_20H_UNATTENDED_E1_E3_CHARACTERIZATION_V3`

Mandatory scientific priorities:

1. E1 threshold-transition characterization around M=1024;
2. reliable module-level profiling/resource diagnosis of the strongest E1 contrasts;
3. Q30 direct-experts harness materialization and N/P/U-active light diagnostic;
4. same-quantized-weight implementation decomposition if runtime paths can be invoked exactly.

Authorized opportunity queue after mandatory closure:

- Qwen0.5B long-context/batch native scenario extension;
- Llama3.2-1B raw shape holdout;
- bounded NCU protocol sensitivity;
- optional detailed capture of the AWQ down_proj M1023/M1024 threshold pair if its exact module selection and storage gates pass.

No new model download or architecture mechanism is authorized.
