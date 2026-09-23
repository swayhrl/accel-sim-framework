# C16 Low-Bit / Shape Exploration Log

> Living scientific log for C16 low-bit implementation and tensor-shape characterization.

## 0. Current question

We want to determine whether GPU execution/memory behavior for AI linear operators is driven mainly by:
- tensor shape;
- deployed low-bit implementation;
- dtype/backend choice;
- semantic operator role.

The current comparison is **deployment-level**, not pure quantization causality.

---

# 1. Existing RAW/AWQ matched semantic-module evidence

Accepted C16 pair closure:

`hrl/c16-qwen25-7b-pair-closure-109-v10@57ca798c851a3b9d4a2c787c01f4e2b3a16fcdea`

Frozen interpretation:

`MATCHED_SEMANTIC_MODULE_REPLAY_DEPLOYMENT_COMPARISON`

The accepted pair gate closes a matched semantic `mlp.down_proj` replay for Qwen2.5-7B RAW and AWQ, while preserving the boundary that RAW/AWQ are different deployment implementations.

Historical static audit:
- RAW direct MREF paths: 243
- AWQ direct MREF paths: 43

This is already evidence that the implementation path changes substantially.

---

# 2. Existing eight-point shape matrix

Accepted upstream experimental asset:

`hrl/awma-e1-shape-oracle-moe-harness-109-v2@56096d32bd5cd783286e1b5e5e612b6019f926d0`

Matrix:

`{q_proj, down_proj} × {M1, M256} × {RAW, AWQ}`

Native timing medians:

| role | M | RAW ms | AWQ ms | AWQ/RAW |
|---|---:|---:|---:|---:|
| q_proj | 1 | 0.023456 | 0.035680 | 1.521 |
| q_proj | 256 | 0.096480 | 0.132096 | 1.369 |
| down_proj | 1 | 0.214016 | 0.060992 | 0.285 |
| down_proj | 256 | 0.378880 | 0.472064 | 1.246 |

## Interpretation

The data do **not** support one simple statement such as “AWQ is faster” or “AWQ is slower”.

Instead they show a strong interaction:

- q_proj: AWQ slower at M1 and M256;
- down_proj M1: AWQ substantially faster;
- down_proj M256: AWQ slower.

Therefore:
> implementation effect depends on semantic operator and shape.

This is the main reason E1 remains scientifically interesting.

---

# 3. Known AWQ shape-dependent path behavior

Accepted AWQ runtime source contract records:

- M1: `GEMM_QUANTIZED`
- M256: `GEMM_QUANTIZED`
- M2048: `DEQUANTIZE_PLUS_TORCH_MATMUL`

Thus tensor shape can change not only launch dimensions but the deployed AWQ execution path itself.

This makes “shape” a first-class architecture variable.

---

# 4. Important unresolved confound: dtype

Existing RAW points are BF16.

The AWQ path must be explicitly re-audited for actual input/weight/output dtype at each core point.

Therefore the current eight-point result is a valid deployment comparison, but it does not isolate low-bit implementation from dtype/backend differences.

Next controlled bridge:

`RAW_FP16_DTYPE_BRIDGE`

for:
- q_proj M1
- q_proj M256
- down_proj M1
- down_proj M256

The bridge uses dense RAW weights/input cast to FP16 and a direct FP16 oracle.

It is not itself a new deployment model.

---

# 5. Planned holdouts

## Operator holdout

`up_proj × {M1,M256} × {RAW,AWQ}`

Purpose:
test whether the shape × implementation interaction is specific to q_proj/down_proj or extends to another MLP projection.

## Input holdout

Preferred:
`down_proj × M1 × {RAW,AWQ}` on a CODE input.

Run only if an exact paired semantic-module CODE authority is available without opening a new large capture campaign.

Do not use unmatched RAW/AWQ natural states as a causal holdout.

---

# 6. Current claim boundary

Allowed:
- RAW and AWQ deployments show materially different shape/operator timing behavior.
- AWQ runtime path is shape-sensitive.
- existing results motivate a controlled dtype bridge.

Not yet allowed:
- quantization alone causes the timing differences;
- low-bit always improves/worsens memory behavior;
- the timing interaction is caused by cache/TLB behavior;
- end-to-end model speedup follows from these module points.

---

# 7. Next step

Execute the lightweight E1 extension defined in:

`docs/vm_tlb/chatgpt_handoff/c16/e1_shape_lowbit_v1/E1_SHAPE_LOWBIT_DIAGNOSTIC_DESIGN_V1.md`

Stop before deep profiling.

A later deep memory diagnostic is justified only if:
- the interaction remains after the RAW-FP16 bridge;
- holdout evidence supports it;
- a concrete runtime-path/memory question remains.



---

## E1 clean-baseline result — 2026-09-23

**Question.** How do operator role, M shape, dense dtype and frozen AWQ implementation interact under one canonical same-input authority?

**Evidence.** Fresh-process RAW canonical activation regeneration passed for Layer0 q/down/up. The 18-point RAW_BF16/RAW_FP16/AWQ_FP16_INPUT matrix used byte-identical FP16 inputs for the latter pair. M1023/M1024 transition and common S2_CODE down_proj holdout completed. Historical eight-point evidence is retained separately as `HISTORICAL_DEPLOYMENT_MEASUREMENT_PROVENANCE_LIMITED`.

**Result.** All three roles show material shape-dependent AWQ/RAW_FP16 interaction; up_proj has the largest registered abs(I). Finite FP16 rounding is explicitly audited. The NCU entry gate passed, but semantic kernel selection was not uniquely resolvable, so status is `NCU_SELECTOR_UNRESOLVED` and no traffic values are claimed.

**Interpretation.** Low-bit deployment behavior is operator- and shape-dependent; it cannot be summarized as universally faster/slower or attributed purely to quantization. The clean comparison isolates identical activation bytes but still compares different weight representations and implementations.

**Superseded.** The old eight-point RAW activation authority is not used for clean ratios.

**Next question.** A future reviewed stage may establish a unique semantic NCU selector for the selected role.

**Stop condition.** Stop after review/Git closure; do not launch NVBit, full address trace or TLB/cache mechanisms.

---

## E1 semantic-NCU result — 2026-09-23

**Question.** For the frozen `up_proj` role, do the accepted M1/M256 RAW_FP16 and AWQ_FP16_INPUT semantic-module invocations show traffic interactions that can be measured without selecting a single representative kernel?

**Evidence.** Four exact standalone replays consumed the accepted canonical FP16 activation bytes and reproduced all four clean-baseline output SHA256 values. Two warmups remained outside a single named NVTX push/pop range. With Nsight Compute CLI 2025.1.1.0, the qualified selector form was `--nvtx --nvtx-include <range>/`: each process contained one selected semantic range, RAW retained one kernel, and AWQ retained both its quantized GEMM and reduction kernels. L1/TEX, L2 and DRAM requested-byte counters had base unit `byte`; occupancy, SM throughput and tensor-cycle activity had unit `%` and were retained per kernel rather than summed.

**Result.** Semantic-module byte sums were:

| point | L1/TEX bytes | L2 bytes | DRAM bytes |
|---|---:|---:|---:|
| M1 RAW_FP16 | 272,187,392 | 137,179,776 | 137,814,656 |
| M1 AWQ_FP16_INPUT | 47,284,224 | 41,677,408 | 35,665,664 |
| M256 RAW_FP16 | 417,071,104 | 417,756,928 | 152,253,440 |
| M256 AWQ_FP16_INPUT | 1,411,252,224 | 1,264,454,400 | 168,477,056 |

At M1, AWQ/RAW was 0.174 for L1/TEX, 0.304 for L2 and 0.259 for DRAM, alongside the accepted timing ratio 0.400. At M256, AWQ/RAW was 3.384 for L1/TEX, 3.027 for L2 and 1.107 for DRAM, alongside the accepted timing ratio 1.869. The timing interaction ratio was 4.669; the corresponding traffic interaction ratios were 19.478, 9.963 and 4.276. All three byte families therefore changed in the same directional pattern as timing across the two shapes.

**Interpretation.** The previously unresolved conditional-NCU step is now closed at the full semantic-module boundary. The data establish a descriptive association between shape-dependent deployed timing and requested traffic. They do not establish cache, TLB, quantization alone, or any other mechanism as causal. AWQ packed-storage normalization uses the exact accepted `up_proj` state-dict footprint of 35,273,728 bytes; dense RAW normalization uses 135,790,592 FP16 weight bytes.

**Superseded.** The clean-baseline marker `NCU_SELECTOR_UNRESOLVED` is superseded only for these four frozen `up_proj` points by `SEMANTIC_MODULE_RANGE_QUALIFIED`. The clean activation, backend, timing, and role authorities are unchanged.

**Next question.** Any mechanism-specific cache/TLB study requires a separately reviewed scientific contract; it is not inferred or started here.

**Stop condition.** Stop after semantic-NCU review-pack and Git closure. NVBit, full address trace and TLB/cache mechanisms remain prohibited in this stage.
