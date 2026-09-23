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

# 8. Historical RAW authority recovery failed

Bounded recovery commit:

`hrl/c16-e1-qwen25-shape-lowbit-109-v1@5563c7bc9320f6699f351307b2895093d0658d97`

Result:

`HISTORICAL_MEASUREMENT_INPUT_AUTHORITY_NOT_REPRODUCIBLE`

The known accepted V8 natural-M2048 path reproduces historical q_proj M1/M256 output SHAs but does not reproduce historical down_proj M1/M256 output SHAs.

Targeted node109/node164 search found no durable missing RAW activation authority that closes all four historical RAW points.

Therefore the old eight-point matrix is retained as:

`HISTORICAL_DEPLOYMENT_MEASUREMENT_PROVENANCE_LIMITED`

It remains useful as motivation, but is no longer the primary controlled E1 authority.

No V8/V9/AWQ activation pool was promoted to replace the missing authority.

---

# 9. New clean-baseline question

The E1 mainline now restarts under an explicit reproducible authority:

> For the same canonical semantic activation, how do operator role, M shape, dense dtype, and deployed AWQ implementation interact?

Primary matrix:

`{q_proj,down_proj,up_proj} × {M1,M256} × {RAW_BF16,RAW_FP16,AWQ_FP16_INPUT}`

New authority:

`C16_E1_CANONICAL_RAW_ACTIVATION_V1`

Source:
- one reproducible RAW Layer0 natural S2_TEXT M2048 execution;
- live module input capture for q_proj/down_proj/up_proj;
- M256 = first 256 rows;
- M1 = first row;
- activation regeneration must reproduce identical SHA.

RAW_FP16 and AWQ consume the exact same FP16 activation bytes.

This improves the comparison relative to the historical natural-state matrix by controlling the semantic input directly.

The comparison remains implementation-level, not pure quantization causality.

---

# 10. Pre-authorized execution strategy

All currently foreseeable node109 E1 work is one Goal:

1. freeze new canonical authority;
2. run the 18-point native matrix;
3. run CODE holdout if existing authority is available;
4. run bounded M1023/M1024 AWQ transition diagnostic;
5. if pre-registered materiality gates pass, automatically run a minimal NCU set;
6. stop before NVBit/full address trace/mechanism design.

174-new runs in parallel to:
- audit the contract;
- find reusable CODE/Llama assets;
- prepare an independent consumer/comparator;
- consume producer evidence if it is available by the time prep completes.



---

## Next reviewed question — semantic NCU attribution

The clean E1 producer/consumer pair is closed.

Accepted independent result:

- strongest interaction role: `up_proj`
- M1 AWQ/RAW_FP16 ≈ 0.40024
- M256 AWQ/RAW_FP16 ≈ 1.86876
- abs(I) ≈ 1.54097
- CODE down_proj holdout preserves the same qualitative small-M-fast / larger-M-slow direction
- M1023/M1024 AWQ path switches from `GEMM_QUANTIZED` to `DEQUANTIZE_PLUS_TORCH_MATMUL`

The current unresolved point is not whether timing interaction exists. It is:

> what kernel set and L1/L2/DRAM traffic belong to one exact semantic up_proj invocation under RAW_FP16 and AWQ at M1/M256?

The next stage therefore resolves semantic-module NCU attribution.

Important scientific unit:

`one exact semantic module invocation`

not one arbitrarily selected GPU kernel.

A multi-kernel AWQ module call is treated as one semantic range; additive traffic is summed only across kernels proven to belong to that range.

No NVBit/full address trace/mechanism is authorized until this semantic NCU stage is reviewed.

---

## Independent semantic-NCU V2 closure

174-new independently recomputed the application-replay / cache-control-none
semantic-module traffic directly from raw NCU BASE/SESSION/PROFILE evidence.

- RAW points contain exactly one selected kernel; AWQ points contain the GEMM
  plus reduction kernels within the unique semantic range.
- All selected kernels report one application replay pass and byte units for
  `l1tex__t_bytes.sum`, `lts__t_bytes.sum`, and `dram__bytes.sum`.
- Independent semantic sums and RAW/AWQ/shape ratios exactly match producer V2.
- V1 used default kernel replay, lacked explicit cache-control none, and used
  seven replay passes per selected kernel.
- V1/V2 L1/L2 ratios are same-direction and similar-magnitude. M1 DRAM remains
  same-direction but changes magnitude materially under V2; M256 DRAM is similar.
- AWQ packed state (35,273,728 B) is below device L2 (67,108,864 B), while RAW
  FP16 dense weight (135,790,592 B) exceeds L2. Together with M1 AWQ DRAM=640 B,
  this is consistent with a warm-cache capacity/residency hypothesis, not proof
  of cache or TLB causality.

No GPU, NVBit, full trace, or cache/TLB mechanism is authorized by this result.
