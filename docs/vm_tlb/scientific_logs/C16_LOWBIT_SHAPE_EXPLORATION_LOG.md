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

---

## E1 semantic-NCU cache-state repair — 2026-09-23

**Question.** Does the frozen `up_proj` M1/M256 RAW_FP16-versus-AWQ traffic interaction persist when Nsight Compute uses application replay and preserves application-managed cache state with `--cache-control none`?

**V1 audit.** The V1 selector and arithmetic remain correct and its values are unchanged. Its preserved session commands omit explicit application replay and `cache-control none`, while every selected kernel records seven replay passes. V1 traffic is therefore retained as `COLD_CACHE_KERNEL_REPLAY_DIAGNOSTIC`, not native/warmed semantic-module traffic.

**V2 evidence.** Nsight Compute CLI 2025.1.1 accepted `--replay-mode application --cache-control none`. Each of the four application processes rebuilt the same accepted module state, executed two warmups outside its unique NVTX range, then executed exactly one selected semantic `up_proj` call. All canonical input and accepted output SHA256 gates passed. Every selected kernel records one application replay pass. RAW retained one complete target kernel; AWQ retained its complete quantized GEMM plus reduction sequence.

**V2 semantic-module traffic.** Exact byte sums from raw base-unit exports were:

| point | L1/TEX bytes | L2 bytes | DRAM bytes |
|---|---:|---:|---:|
| M1 RAW_FP16 | 272,187,392 | 137,167,040 | 138,156,416 |
| M1 AWQ_FP16_INPUT | 47,284,224 | 41,898,912 | 640 |
| M256 RAW_FP16 | 417,071,104 | 417,723,360 | 156,380,160 |
| M256 AWQ_FP16_INPUT | 1,411,252,224 | 1,266,170,592 | 178,195,840 |

M1 AWQ/RAW was 0.173719 for L1/TEX, 0.305459 for L2 and `4.63243e-6` for DRAM. M256 AWQ/RAW was 3.383721, 3.031122 and 1.139504 respectively. RAW M256/M1 scaling was 1.532294, 3.045363 and 1.131907; AWQ M256/M1 scaling was 29.846154, 30.219653 and 278431. Traffic shape-interaction ratios were 19.478086, 9.923171 and 245984.075367.

**V1/V2 classification.** L1/TEX and L2 are `SAME_DIRECTION_SIMILAR_MAGNITUDE`. DRAM is `SAME_DIRECTION_DIFFERENT_MAGNITUDE`, driven by the V2 M1 AWQ value. No metric changes its qualitative M1 or M256 AWQ-versus-RAW direction. All three V2 traffic interactions retain the accepted native timing interaction direction.

**Interpretation.** Semantic-module traffic is materially profiler-context-sensitive, especially M1 DRAM. This is a descriptive association under the registered V2 context; it does not demonstrate cache causality, TLB causality, or a specific mechanism opportunity.

**Superseded.** Only the interpretation of V1 as final warmed semantic traffic is superseded. Its selector, raw counters and arithmetic are preserved without modification.

**Next question.** Resume independent consumer verification directly from V2 raw report hashes, session commands and base-unit exports. Any mechanism study requires a separate reviewed contract.

**Stop condition.** Stop after bounded repair review/Git closure. NVBit, full address trace, cache/TLB mechanisms, shape sweeps and role reselection remain prohibited.

---

## E1 residency-intervention producer result — 2026-09-23

**Question.** Does controlled pre-target memory pressure reversibly perturb the exact accepted RAW_FP16/AWQ semantic modules in the operator/shape pattern predicted by the warm-residency hypothesis?

**Capacity census.** Actual frozen module state, not nominal geometry, gives: q_proj RAW=25,697,280 B and AWQ=6,680,576 B, both below the accepted 67,108,864 B L2; down_proj/up_proj RAW=135,790,592 B (>L2) and AWQ=35,273,728 B (<L2).

**Intervention authority.** One initialized 256 MiB FP32 CUDA allocation was reused. SPARSE read `buffer[::1024]` (one FP32 per 4096 B, 65,536 elements); DENSE read all 67,108,864 elements. Pressure stayed outside target CUDA-event intervals and semantic NVTX ranges. Shared-buffer qualification measured DENSE/SPARSE requested-traffic ratios of 128.015 for L1/TEX, 105.875 for L2, and 74.393 for DRAM. SPARSE remains only a page-footprint-oriented control and does not exclude TLB effects.

**Primary TEXT result.** For up_proj M1 AWQ, DENSE/WARM_A target timing was 1.53646, versus SPARSE/WARM_A 0.97656. Target DRAM was 80,000 B under WARM, 2,365,312 B after SPARSE, and 35,368,192 B after DENSE. RAW timing was essentially unchanged. Up_proj M256 AWQ DENSE/WARM_A was 0.99230, supporting a smaller shape-control effect.

**Dose and input holdout.** Up_proj M1 AWQ timing ratios versus 0 MiB were 1.043, 1.200, 1.644, 1.637 and 1.642 at 16/32/64/128/256 MiB; RAW remained within 0.8%. The pre-authorized 64 MiB semantic NCU point reproduced high AWQ DRAM traffic. Accepted common CODE down_proj M1 directly reused input SHA `861716...`; AWQ DENSE/WARM_A timing was 1.43558, WARM_B/WARM_A was 0.98487, and DRAM rose from 26,752 B to 35,403,136 B. CODE RAW was essentially unchanged.

**Pre-registered gates.** Primary up_proj M1 AWQ has `MATERIAL_TIMING_PERTURBATION=true`, `MATERIAL_DRAM_PERTURBATION=true`, and `DENSE_SPECIFIC=true`. Its WARM_B/WARM_A timing ratio is 0.93750, outside the strict 5% recovery tolerance, so `REVERSIBLE=false` even though down_proj/CODE controls recover.

**Scoped conclusion.** `RESIDENCY_INTERVENTION_PARTIALLY_SUPPORTED`. The operator, shape, dose, traffic, and CODE controls are consistent with cache-line residency contributing to the M1 AWQ advantage, but the failed primary recovery gate prevents strong support. The result does not prove L2 is the unique cause, does not exclude TLB effects, and does not authorize a cache/TLB mechanism.

**Next step.** Stop for independent consumer recomputation directly from raw timing samples and raw NCU BASE/SESSION/report receipts. No NVBit, full address trace, cache/TLB mechanism, new model, or shape sweep is authorized.

---

## E1 natural-reuse / residency causal-closure producer result — 2026-09-23

**Refill dynamics.** After two warmups and accepted 256 MiB dense pressure, AWQ q/down/up all show packed-state-scale K1 DRAM followed by one-call refill: q_proj 6,775,552→66,304 B, down_proj 35,406,848→78,208 B, and up_proj 35,369,856→72,576 B at K1→K2. K6/K1 native timing is 0.858, 0.534, and 0.443 respectively. RAW down/up remain nearly flat at approximately 135.8 MB DRAM, with K6/K1 timing 0.962/0.966. RAW q_proj likewise remains near its 25.7 MB state footprint despite a first-call timing drop.

**Capacity knees.** The first registered DRAM knees are q_proj=32 MiB and down/up=16 MiB. Nominal residual-L2 values are 57.63 MiB and 30.36 MiB, giving descriptive deltas of -25.63 MiB and -14.36 MiB. First material timing doses are q=32, down=24, and up=28 MiB. Capacity preserves coarse role ordering, but onset occurs materially earlier and post-knee responses are role-specific/non-monotonic; nominal capacity alone is insufficient.

**Natural AWQ authority.** Seven independent full-model runs over the accepted 2048-token S2_TEXT prefix reproduce exactly the greedy D0–D3 sequence `[23578, 11, 323, 3950]` and all 12 occurrence input/output SHA bindings. Prefill is excluded. Target events are recorded without synchronizing inside the model loop.

**Natural traffic and isolated proximity.** Layer0 up_proj natural DRAM is 49,655,552 B at D0, 49,922,944 B at D1, and 49,204,864 B at D3. These produce unclamped isolated warm fractions 1.405, 1.412, and 1.392: all lie beyond the isolated DENSE bracket. Timing fractions are also outside above DENSE (2.208 at D0 and approximately 1.398 at D1/D3). Layer0 down_proj DRAM is 37,038,720/36,648,832 B at D0/D3, slightly beyond DENSE (fractions 1.046/1.035), while timing remains inside the WARM–DENSE bracket (0.679/0.615).

**Held-out and RAW controls.** Layer14 up_proj reproduces layer0's approximately 49 MB natural DRAM and D3 timing; layer0 D0 alone has an extra first-step cost. The optional accepted RAW BF16 full model cleanly fits without offload or backend/dtype changes. Seven RAW runs reproduce the same token sequence; layer0 up_proj D0/D3 stay flat at 0.2048 ms and D0 DRAM is 136,006,784 B.

**Integrated answer.** `CASE_B_WITH_CASE_D_ROLE_DEPENDENCE`. Immediate isolated reuse repopulates compressed state, but the natural full-model interval makes AWQ layer0 up/down traffic dense-like or beyond the isolated dense bracket. Capacity matters, while role/kernel/access policy is also required to explain the observed knees and timing differences. Case A and Case C are not supported.

**Boundary.** This is a natural-reuse/residency causal diagnostic, not authorization for a mechanism. No NVBit, full address trace, cache/TLB mechanism, or mechanism simulation was started. Independent consumer recomputation from raw timing and NCU evidence is required before any next-stage decision.

---

## E1 targeted CUDA L2-persistence intervention producer result — 2026-09-23

**Capability and exact regions.** Local CUDA headers/runtime successfully qualify `cudaDeviceSetLimit(cudaLimitPersistingL2CacheSize)`, `cudaStreamSetAttribute(cudaStreamAttributeAccessPolicyWindow)`, and `cudaCtxResetPersistingL2Cache`. Runtime device values reproduce L2=67,108,864 B, max persisting=46,137,344 B, and max window=134,213,632 B. Layer0/layer14 up_proj and layer0 down_proj qweight are each independent contiguous 33,947,648-byte tensors with storage offset 0. CUDA rounds that requested full set-aside to 37,748,736 B; all receipts preserve requested/actual values and reset before/after every condition.

**Isolated qualification.** Under identical warmup→256 MiB dense pressure→target construction, qweight persistence changes median timing from 0.076544 to 0.049056 ms and target DRAM from 35,368,320 to 13,624,576 B. Selector, policy, backend and semantic identity all pass, so the CUDA policy itself is qualified.

**Natural matched controls.** Relative to SETASIDE_ONLY, exact target persistence gives material target-specific timing benefits at all primary stable occurrences: L0 up D1=48.75%, L0 up D3=46.84%, L14 up D3=49.37%, and L0 down D3=19.36%. Matched unrelated persistence gives smaller timing benefits (or a slowdown for L0 down). Reservation effects, target persistence, and unrelated persistence remain separately reported.

**Traffic caveat.** Natural target DRAM improvements do not cross the preregistered 20% threshold: L0 up D3 falls 19.51% (45,455,744→36,587,264 B), L14 up D3 falls 19.05%, and L0 down D3 falls 0.45%. Matched unrelated persistence sometimes reduces DRAM as much or more. Therefore target specificity is established on timing, not on the DRAM gate.

**Budget sensitivity.** With the full qweight window retained and hitRatio scaled to budget, 8 MiB is non-material and 16 MiB is the first tested material timing budget. The tested 32 MiB and full-qweight conditions reach the same approximately 0.043008 ms L0 up D3 median. No tested budget meets the DRAM material gate; 16 MiB is a tested point, not an exact threshold.

**Scoped state.** `MECHANISM_REQUIREMENTS_READY_FOR_DESIGN_REVIEW`. The extracted abstract requirement is selective line-level protection of a qweight-like address interval across the inter-token reuse lifetime, with bounded budget, interference resistance, and normal fallback for non-target data. Candidate identity sources remain open. No classifier, replacement algorithm, Accel-Sim mechanism, NVBit trace, full address trace, or cache/TLB simulation was implemented or started.

---

## E1 shared-residency mechanism-feasibility producer result — 2026-09-24

**Frozen upstream divergence.** The prior producer state `MECHANISM_REQUIREMENTS_READY_FOR_DESIGN_REVIEW`, strict consumer state `TARGETED_PERSISTENCE_MECHANISM_PRECONDITION_NOT_SUPPORTED`, and `METHODOLOGICAL_OPERATIONALIZATION` divergence remain unchanged. This stage operates under `DESIGN_REVIEW_AUTHORIZED_WITH_TRAFFIC_CAVEAT`.

**Critical path.** Installed NCU 2025.1.1 resolves duration, L2 TEX-read hit/miss sectors, DRAM-read bytes, long-scoreboard stall, LSU utilization and active-warps metrics. Up-proj policy duration changes occur in the quantized GEMM; reduction duration is nearly unchanged. Target persistence modestly improves L2 hit/miss behavior, but unrelated persistence can also reduce GEMM duration and long-scoreboard without the same hit/miss shift. DRAM-read bytes move much less than native timing or aggregate DRAM. L0 down's native benefit is not reproduced by profiled kernel duration/stall. Aggregate DRAM is therefore a poor standalone critical-path proxy.

**Rotating-window qualification.** Under one fixed full-qweight set-aside, A=L0 up→B=L14 up→A was executed with hitRatio=0.5 and no intermediate reset. A matched control performed the same three updates using `cudaAccessPropertyNormal` for both hit and miss. Persistent rotation changes GEMM duration 48,512→41,376 ns, long-scoreboard 43.8%→28.5%, DRAM read approximately 27.1→14.7 MB, and materially improves L2 hit/miss sectors. Rotating semantics are qualified. Median host update cost is approximately 1.57 μs per call.

**Fixed-budget sharing.** Every rotating condition uses one requested 33,947,648 B set-aside and 15 full-qweight window updates per full-model run. SHARE2_UP retains material D3 local benefits for L0 up (42.5%) and L14 up (43.0%). SHARE2_L0 retains L0 up (31.25%) and L0 down (10.96%). SHARE3 retains all three targets: 36.25%, 35.44%, and 5.48%. `MULTI_TARGET_RETAINED=true` for all three shared conditions.

**Whole decode and overhead.** Stable D1–D3 mean decode latency improves only 0.347% for SHARE2_UP and 0.381% for SHARE3 versus ROTATE_CONTROL_3; SHARE2_L0 is approximately flat/slightly worse. None reaches the registered 2% whole-decode threshold. ROTATE_CONTROL_3 itself changes stable decode by only approximately 0.028% versus SETASIDE_ONLY. Each update costs roughly 3.8 μs in the full-model harness, approximately 57 μs over 15 updates; raw per-update/per-run overhead is retained separately.

**Stage label.** `SHARED_RESIDENCY_LOCAL_ONLY`. One fixed quota can retain multiple local qweight benefits, including all three targets under SHARE3, but this bounded configuration does not produce material full decode-step benefit. No NVBit, full address trace, Accel-Sim mutation, or mechanism simulation was started.

---

## E1 fixed-budget protected-coverage scaling producer result — 2026-09-24

**Opportunity census.** Seven fresh no-persistence full-model runs close all 84 qweight-backed FFN projections and 336 D0–D3 occurrences. Stable run-aligned decode shares are gate_proj 14.76%, up_proj 16.84%, down_proj 15.78%, and all FFN projections 47.39%. Per-layer role timing is broadly uniform; each role's top four layers contribute approximately 14.4% of that role's total.

**Frozen coverage curve.** Using the preregistered nested layer sets and one fixed requested/actual set-aside, selected target share grows from 0.591% at N1 through 1.189%, 2.370%, 4.751%, 8.318%, to 16.628% at N28. Every selected layer remains `MATERIAL_LOCAL`, while median per-layer benefit dilutes from 47.5% at N1 to approximately 25% from N14 through N28.

**Run-aligned system accounting.** Whole stable-decode benefit is -0.056% at N1, then 0.331%, 0.558%, 0.689%, 0.760%, and 0.892% at N2/N4/N8/N14A/N28. N28 is positive beyond combined dispersion but remains below the frozen 2% gate. Median summed selected local saving grows to 0.567 ms at N28, while observed per-step decode saving is 0.123 ms and realization ratio falls to approximately 0.216. Formal authority uses same-run module and decode samples; no independent-median ratio substitutes are used.

**Composition holdout.** N14A and N14B closely match: selected share 8.318% versus 8.303%, median local benefit 25.0% versus 24.94%, whole-decode benefit 0.760% versus 0.739%, and realization ratio 0.368 versus 0.356. The curve is not driven by one favorable half of layers.

**Critical path and FULLHINT.** Bounded NCU shows GEMM duration/stall benefit persists at N28 even as L2-hit/miss and DRAM-read ratios dilute toward unity. The preregistered FULLHINT trigger fires because all N28 layers remain material while decode benefit is sub-2%. FULLHINT_N28 improves the curve by only 0.079 percentage points relative to FAIR_N28, below the 0.5-point extra-NCU trigger; over-subscribed intent does not materially change the result.

**Stage label.** `COVERAGE_SCALING_POSITIVE_BUT_SUBTHRESHOLD`. Full up_proj coverage produces a real but sub-2% system effect. Because measured gate/down coverage expands total FFN opportunity from 16.84% to 47.39%, `EXPAND_OPERATOR_FAMILY_BEFORE_SIMULATOR` is the leading review candidate, not an automatic authorization. No simulator, NVBit capture, full trace, or mechanism implementation was run.
