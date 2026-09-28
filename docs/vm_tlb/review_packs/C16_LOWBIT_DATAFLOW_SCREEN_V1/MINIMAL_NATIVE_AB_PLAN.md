# Minimal native A/B plan: fixed split-K=8 versus no-split

Status: `DESIGN_ONLY_NOT_EXECUTED`. This plan is not execution authorization.

## Question

Does the accepted fixed `split_k_iters=8` policy provide net value at the clean up_proj/down_proj M1/M256 shapes after accounting for its eight-plane FP16 scratch and separate global reduction?

This A/B tests the complete split policy bundle. It cannot by itself separate lost/gained K-parallelism from reduction, scratch, or launch overhead, and it does not test cross-token weight residence, activation caching, or QUICK-style layout conversion.

## Exact arms

A — `ACCEPTED_SPLIT8`

- Historical source: `AutoAWQ_kernels@c7b0e88c327694c715b0a758d9ce8fd414a1fa21`.
- Same `gemm_forward_4bit_cuda_m16n128k32` path.
- `split_k_iters=8`.
- Output scratch shape `[8,M,N]`, followed by `sum(0)`.
- This must reproduce the accepted output SHA for A before comparison.

B — `NO_SPLIT1_DIRECT_OUTPUT`

- Fork only the exact historical source into an isolated extension name; never replace the accepted `.so`.
- Set `split_k_iters=1` for the same kernel and return/select the sole `[1,M,N]` plane directly instead of launching `sum(0)`.
- Do not change qweight layout, dequantization math, CTA tile, K32 loop, datatype, group size, model asset, allocator policy, or backend.
- This is one conceptual control: the K-split policy. Direct selection is required to avoid measuring a semantically unnecessary one-plane reduction.

Expected launch/scratch checks:

| Point | A GEMM grid | B GEMM grid | A scratch B | B scratch B | A reduction | B reduction |
|---|---:|---:|---:|---:|---|---|
| up_proj M1 | 1184 | 148 | 303104 | 37888 | present | absent |
| up_proj M256 | 18944 | 2368 | 77594624 | 9699328 | present | absent |
| down_proj M1 | 224 | 28 | 57344 | 7168 | present | absent |
| down_proj M256 | 3584 predicted | 448 | 14680064 | 1835008 | present | absent |

The down_proj M256 A grid is a preregistered source prediction, not accepted dynamic evidence. A launch audit must verify it before any timing interpretation.

## Frozen inputs and invariants

Use only the clean producer authority at `8988d6108ff8bdca180a14cec2fe769df45b099f1`:

- model `Qwen/Qwen2.5-7B-Instruct-AWQ`, revision `b25037543e9394b818fdfca67ab2a00ecc7dd641`;
- exact Layer0 `mlp.up_proj` and `mlp.down_proj` qweight/qzeros/scales bytes;
- exact canonical FP16 input tensors and SHAs for M1/M256;
- RTX 4080 / SM89 and the frozen c16-awq-v6 software stack;
- one process, one CUDA stream, unchanged clocks/power policy, and no other GPU workload.

No re-quantization, model download, backend installation, full-model execution, full timing, simulator compilation, trace recapture, or Lane 4 access is part of this design.

## Correctness gate before timing

For every point and arm:

1. require identical input and qweight/qzeros/scales SHA to the clean authority;
2. require identical shape/dtype and all-finite output;
3. require A output SHA to equal the accepted clean output SHA;
4. compare B with A using elementwise `rtol=1e-2, atol=5e-2`, and record max_abs, mean_abs, relative-L2, changed element count, and output SHA;
5. fail closed on any point outside tolerance; do not time a failed point.

Exact B equality is not required because changing the split changes FP32 accumulation grouping and the final FP16 conversion order. The tolerance is frozen here before execution.

## Short measurement set

Only after a separate authorization and the correctness gate:

1. Run 10 untimed warmups per arm/point.
2. Run 50 CUDA-event module samples per arm/point in deterministic ABBA blocks; synchronize at sample boundaries. Report all samples, median/min/max/CV, and paired block deltas. This is a bounded module microbenchmark, not full timing.
3. Capture one short profiler launch inventory per arm/point to verify the preregistered grids and GEMM/reduction presence. Do not collect a full-model trace.
4. For up_proj M256 only, collect the same three V2 additive metrics (`l1tex__t_bytes.sum`, `lts__t_bytes.sum`, `dram__bytes.sum`) under application replay and cache-control none, separated by kernel. Preserve raw units and rows.
5. If available in that same bounded profile, record registers/thread, static/dynamic shared memory, achieved occupancy, and kernel duration. A missing metric remains `UNKNOWN`; do not expand the metric sweep.

Do not label any profiler replay value as native wall time. Do not infer tensor-level bytes from the totals.

## Decision rule

`H1_SUPPORTED_BOUNDED` requires all of:

- correctness PASS for all four points;
- B has no reduction launch and observed grids/scratch match the table;
- B improves median module time by at least 5% and by more than the larger arm CV at both M256 points;
- neither M1 point regresses by more than 5%;
- up_proj M256 B lowers semantic-range L2 or DRAM bytes in the expected direction without a contradictory GEMM-duration increase that erases the module benefit.

Otherwise:

- correctness failure -> `NUMERICAL_ORDER_CHANGE_REJECTS_AB`;
- valid but no material M256 gain -> `NO_NEW_OPPORTUNITY_FIXED_SPLIT8_NOT_MATERIAL`;
- gain at only one operator -> `OPERATOR_SPECIFIC_SPLIT_POLICY_ONLY`, with no general mechanism claim;
- ambiguous/missing profiler counters but material clean timing -> `TIMING_SIGNAL_ONLY_NEEDS_NO_AUTOMATIC_EXPANSION`.

No result from this A/B may be called the unique E1 cause. The four points were used to select this diagnostic and are not an independent holdout.

## Stop boundary

One isolated source variant, four clean points, one bounded launch audit, and one up_proj M256 traffic pair are the entire design. After the decision, stop. Do not add MARLIN/QUICK/FLUTE backends, new quantization, new shapes, model-level timing, D1-D3 rescans, simulator work, or Lane 4 inputs.
