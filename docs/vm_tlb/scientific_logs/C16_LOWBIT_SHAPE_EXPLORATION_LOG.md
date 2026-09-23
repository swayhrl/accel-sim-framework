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


---

## Next reviewed question — controlled residency intervention

The semantic-NCU V2 producer/consumer pair is closed.

Accepted state:

- up_proj M1 AWQ/RAW timing ≈ 0.400
- up_proj M256 AWQ/RAW timing ≈ 1.869
- application-replay/cache-control-none traffic:
  - M1 AWQ/RAW L1=0.174, L2=0.305, DRAM≈4.63e-6
  - M256 AWQ/RAW L1=3.384, L2=3.031, DRAM=1.140
- AWQ up_proj packed state 35.27 MiB-equivalent bytes < 64 MiB L2
- RAW FP16 up_proj dense weight 135.79 MB > L2

Current interpretation remains:
`CONSISTENT_WITH_WARM_CACHE_CAPACITY_RESIDENCY_HYPOTHESIS_NOT_CAUSAL_PROOF`

The next stage holds the target operator/input/backend fixed and intervenes only on pre-target memory state using:

- WARM
- SPARSE_PAGE_PRESSURE
- DENSE_MEMORY_PRESSURE
- WARM_RECOVERY

The same 256 MiB buffer is used for sparse and dense pressure. SPARSE touches one FP32 every 4 KiB across the full range; DENSE reads the full buffer.

The stage also includes:
- exact q/down/up capacity census;
- M1 q/down/up operator controls;
- up_proj M256 shape control;
- bounded pressure-dose timing;
- optional accepted CODE down_proj holdout;
- semantic NCU under application replay/cache-control none.

No NVBit/full trace/mechanism is authorized before independent consumer closure.

## E1 residency intervention independent consumer closure (174-new)

Producer `22d1b98d7f0c213950654fc754be4e7388836de3` was consumed from raw timing rows and raw NCU BASE+SESSION+PROFILE triples. Independent gates: MATERIAL_TIMING_PERTURBATION=True, MATERIAL_DRAM_PERTURBATION=True, REVERSIBLE=False, DENSE_SPECIFIC=True; scoped label `RESIDENCY_INTERVENTION_PARTIALLY_SUPPORTED`. WARM_B/WARM_A≈0.9375000 is an over-recovery/baseline-drift gate failure, not persistent DENSE slowdown. No GPU work or mechanism authorization occurred on 174-new.


---

## Next reviewed question — natural reuse interval and refill dynamics

The residency-intervention producer/consumer pair is independently closed at:

- producer `22d1b98d7f0c213950654fc754be4e7388836de3`
- consumer `5b11dd41e98044fcad76da4a906c7ba8609eb828`

Scoped result:

`RESIDENCY_INTERVENTION_PARTIALLY_SUPPORTED`

Primary up_proj M1 AWQ:
- dense pressure materially increases timing and DRAM;
- sparse page-footprint pressure does not reproduce the same timing effect;
- q_proj and M256 controls are much less sensitive;
- CODE down_proj reproduces the dense AWQ effect;
- the strict primary recovery gate is false only because WARM_B over-recovers and is ~6.25% faster than WARM_A.

The next stage asks three stronger questions:

1. Does a pressured AWQ target repopulate over immediate K1..K6 reuse?
2. Does pressure-dose DRAM onset align descriptively with nominal residual L2 capacity across q/down/up?
3. Does the isolated warm state survive the real full-model decode interval between consecutive uses of the same target module?

The third question determines whether the observed residency benefit is already naturally captured by current hardware or whether realistic model interference evicts the compressed state before reuse.

No residency mechanism is authorized before this natural-reuse stage and independent consumer closure.

---

## E1 natural-reuse / residency independent consumer closure (174-new)

Producer `ccfdc89d517766d12588ee131818efe341c7e17c` was consumed directly from raw timing and NCU BASE+SESSION+PROFILE evidence. The independent classification is `CASE_B_WITH_CASE_D_ROLE_DEPENDENCE`: AWQ shows clear immediate refill, natural layer-0 traffic is dense-like or beyond the isolated dense bracket, and capacity/role responses differ. Capacity observations are first tested triggers with tested brackets, not exact physical knees. Layer 14 remains `NO_EXACT_ISOLATED_AUTHORITY`; layer-0 isolated evidence was not borrowed. The optional RAW result is a BF16 full-model control, not isolated RAW_FP16 authority. No GPU, NVBit, full trace, cache/TLB mechanism, or mechanism simulation was used or authorized.


---

## Next reviewed question — targeted real-hardware L2 persistence

The natural-reuse producer/consumer pair is independently closed:

- producer: `ccfdc89d517766d12588ee131818efe341c7e17c`
- consumer: `4f9242d177220721cb9e669aad5dd9e29f04407d`

Accepted framing:

`CASE_B_WITH_CASE_D_ROLE_DEPENDENCE`

The key architectural observation is now:

- immediate reuse rapidly repopulates AWQ q/down/up compressed state;
- natural full-model token reuse does not preserve that state;
- natural target DRAM becomes dense-like or exceeds the isolated dense bracket;
- capacity alone is insufficient to explain all role behavior.

Accepted RTX4080 raw device attributes also show:

- L2 = 67,108,864 B
- max persisting-L2 set-aside = 46,137,344 B
- max access-policy window = 134,213,632 B

The dominant up/down AWQ qweight tensor is 33,947,648 B, within the observed persisting-L2 and access-window limits.

The next stage therefore performs a direct CUDA persisting-L2 policy intervention on exact qweight address ranges during the same natural full-model decode.

The goal is to determine whether selectively preserving the target compressed weight region reduces natural target DRAM/timing relative to:
- baseline;
- set-aside-only;
- matched unrelated-region persistence.

This is a mechanism-precondition experiment only. No new cache mechanism, NVBit trace, or simulator implementation is authorized yet.

---

## E1 targeted L2-persistence consumer prep (174-new)

CPU-only independent consumer prep is complete on handoff `b2301f9ede7e4d4b6adcd3f08d4be169058f318f`. Policy receipts, isolated qualification, five natural conditions, raw four-source NCU closure, matched controls, materiality, conditional budget sensitivity, and four final-state labels are frozen and covered by 48 new tests. The producer ref was unavailable in the one-shot fetch window, so status is `READY_FOR_E1_L2_PERSISTENCE_INTERVENTION_109`; no scientific persistence result or mechanism authorization is asserted.

---

## E1 targeted L2-persistence independent consumer closure (174-new)

Producer `4c0e6b998528e425578cacf5912bbcc4ff3bfaf6` was independently consumed from raw capability, per-run timing/policy, and BASE+SESSION+PROFILE+policy evidence. CUDA policy qualification and five real-artifact canaries pass. All four primary natural points have material target-specific timing benefit, but none crosses the frozen 20%+4MiB DRAM gate. The first tested timing-material budget is 16 MiB; it is not an exact threshold. Producer scoped state remains `MECHANISM_REQUIREMENTS_READY_FOR_DESIGN_REVIEW`; the frozen strict consumer state is `TARGETED_PERSISTENCE_MECHANISM_PRECONDITION_NOT_SUPPORTED`. The divergence is methodological operationalization, not a raw-data mismatch, and project authorization remains `REVIEW_REQUIRED`. No GPU/NVBit/full trace/mechanism work was used or authorized.


---

## Project review after targeted L2-persistence closure

Producer:
`4c0e6b998528e425578cacf5912bbcc4ff3bfaf6`

Independent consumer:
`1dcab9c8d932973399c5811dc817802bfb3b9dfe`

Raw evidence:
`PASS`

Frozen decision-rule divergence remains:

- producer scoped state:
  `MECHANISM_REQUIREMENTS_READY_FOR_DESIGN_REVIEW`
- strict consumer state:
  `TARGETED_PERSISTENCE_MECHANISM_PRECONDITION_NOT_SUPPORTED`

The divergence is methodological operationalization, not a data mismatch.

Project-level action:

`DESIGN_REVIEW_AUTHORIZED_WITH_TRAFFIC_CAVEAT`

Reason:
- all primary natural targets show material, target-specific timing benefit;
- isolated policy efficacy is strong in both timing and DRAM;
- producer mechanism-requirement dimensions are independently found descriptively supported;
- the strict consumer READY gate fails only because no primary natural point crosses the frozen >=20% DRAM threshold.

The traffic caveat remains binding:
- aggregate target DRAM is not target-specific;
- matched unrelated persistence may reduce DRAM equally or more;
- mechanism review must not be framed as simply “reducing DRAM bytes.”

The next stage therefore tests:
1. which per-kernel L2/stall behavior explains the latency/traffic decoupling;
2. whether one fixed persistence budget can be shared across multiple qweight regions;
3. whether shared residency produces a whole-decode benefit;
4. which minimal L2 replacement/quota mechanism best matches the evidence.

No simulator implementation or full trace is authorized yet.

---

## E1 shared-residency design review and consumer prep (174-new)

The upstream producer/strict-consumer divergence remains frozen and project action remains `DESIGN_REVIEW_AUTHORIZED_WITH_TRAFFIC_CAVEAT`. CPU-only prep implemented shared-policy and category-aware critical-path consumers. Static mapping of accepted Core `57bb71e` supports an address-based oracle tag but finds no kernel UID/CTA ID at L2 and no reliable PC on sector-split children. The recommended first mechanism is M1 elastic protected quota with oracle/software-region tagging; M0 is a static-partition control and M2 is deferred. Existing artifacts are insufficient for the natural reuse replacement experiment, so `BOUNDED_ADDITIONAL_TRACE_REQUIRED` specifies only a two-stable-decode minimum scope and does not authorize capture. The shared-hardware producer ref was absent in the one-shot fetch window; status is `READY_FOR_E1_SHARED_RESIDENCY_FEASIBILITY_109`.
