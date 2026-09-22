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

