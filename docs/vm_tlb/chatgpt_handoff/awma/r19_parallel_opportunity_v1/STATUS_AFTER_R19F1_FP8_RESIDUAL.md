# R19F1 FP8 readiness residual review

Date: 2026-10-01

Execution authority:
- branch: `hrl/awma-r19f1-fp8-readiness-109-v1`
- commit: `7375abd8e86c1523c1873913e8fffccf0b4e3a96`
- tree: `7b47b1d50163d4a33704b243c1b7e797776b3594`
- formal label: `R19F1_FP8_READINESS_RESIDUAL_PRESENT`

## Accepted facts

Frozen scope:
- Qwen2.5-0.5B layer0 up_proj
- M/N/K = 256/4864/896
- TE v2.19.0
- Float8CurrentScaling(E4M3)
- RTX4080 / SM89
- same cached FP8 weight representation

Representation-matched numerical gate:
- F0 vs R0 max_abs = 0.016699
- mean_abs = 0.000310
- cosine = 0.99999845
- frozen TE E4M3 allclose passes

Historical V1 original-BF16 vs FP8 gate remains failed and is not reinterpreted.

A1/D0 identity:
- input FP8 bytes and inverse scale match exactly
- cached weight bits/metadata/pointer unchanged
- outputs bitwise identical
- both launch the same exact SM89 E4M3 cuBLAS GEMM with same geometry

Formal complete-call wall medians:
- A1 online representation readiness: 0.085846 ms
- D0 representation already ready: 0.062693 ms
- delta: 0.023153 ms / 26.97%
- all three paired-group median gaps are positive
- CUDA-event direction matches

Thus the operator-boundary residual is accepted.

## Localization

One bounded NSYS capture shows for A1:
1. zero amax
2. amax reduction
3. scale compute
4. BF16 -> E4M3 conversion
5. same FP8 GEMM as D0

The four preparation kernels total about 4.8-5.0 us GPU service per witness range.
The same GEMM is about 16 us in both A1 and D0.

The formal A1-D0 gap is about 23 us, substantially larger than the summed preparation-kernel service time.

Therefore do not interpret the residual as merely five microseconds of quantization arithmetic. The current evidence is compatible with:
- launch-chain cost
- inter-kernel dependency/scheduling gaps
- runtime/dispatch overhead
- representation preparation arithmetic

NSYS profiler gaps are not precise enough to partition these quantitatively.

## Strong-software boundary before architecture

Current Transformer Engine source already contains fused current-scaling operations in activation/bias/normalization paths. Recent FP8 dataflow work/TE development also explicitly moves quantization earlier and fuses activation+quantization / preserves quantized tensors across consumers.

Therefore the next admissible step is a bounded software/dataflow counterfactual, not hardware:

- preserve the exact same current-scaling E4M3 representation and same FP8 GEMM;
- remove the 4-kernel readiness chain using one source-supported or minimally modified fused quantize path, OR move quantization into the natural producer if the same representation can be produced there;
- compare the complete same-contract operator boundary against A1;
- separately compare to D0 to measure how much ideal readiness headroom remains.

A hardware line is admitted only if a material residual survives this strong software counterfactual and cannot be explained by ordinary launch/dataflow organization.

## Relevant nearest software capability

TE current main:
- current-scaling activation/bias paths include fused activation/amax/FP8 kernels;
- current-scaling support is being integrated into more fused paths.

FP8-Flow-MoE / TE development:
- quantize before dispatch
- keep FP8 tensors alive across downstream operations
- fused activation + quantization
- scaling-aware layout handling

These capabilities mean that "fuse amax+scale+cast" or "quantize earlier" cannot be claimed as a new architecture mechanism by itself.

## Current project decision

Accept:
`R19F1_FP8_READINESS_RESIDUAL_PRESENT`

Do not yet admit:
- cache mechanism
- new FP8 instruction
- 174/Accel-Sim
- Blackwell FP4 extrapolation

Recommended next experiment:
`R19F2_FP8_READINESS_SOFTWARE_COUNTERFACTUAL`

It should be one bounded same-shape/same-representation software/dataflow challenge. No new model/shape sweep.

Lane states:
- Lane F: STOP pending R19F2 authorization
- Lane G fast-weight: STOP
- Lane E IBP: STOP
- Lane E/174 simulator: STOP
