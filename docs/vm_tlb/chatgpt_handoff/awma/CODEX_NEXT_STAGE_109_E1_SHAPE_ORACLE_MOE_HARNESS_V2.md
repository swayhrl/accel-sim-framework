# CODEX NEXT STAGE — 109 E1 Shape-Specific Oracle + MoE Harness V2

Date: 2026-09-20

Status: ACTIVE AFTER USER LAUNCH

Mode:

`GOAL MODE / solve-and-continue`

Node:

`109 / RTX4080`

Stage:

`AWMA_E1_SHAPE_SPECIFIC_ORACLE_AND_MOE_HARNESS_109_V2`

Coordination branch:

`hrl/awma-109-e1-shape-oracle-moe-harness-handoff-v2`

Read first:

1. `docs/vm_tlb/chatgpt_handoff/awma/REVIEW_109_REPLAY_MOE_V1_2026-09-20.md`
2. prior execution review packs under:
   - `AWMA_E1_AUTHORITY_AND_MOE_DIAGNOSTICS_109_V1`
   - `AWMA_E1_REPLAY_REPEATABILITY_AND_MOE_CONTROL_HOOK_109_V1`
3. this Goal

Accepted parent execution:

`hrl/awma-e1-repeatability-moe-hook-109-v1`

`137157d3a22c1b70e3bafa64ac9b56c3309fdcd9`

Suggested execution branch:

`hrl/awma-e1-shape-oracle-moe-harness-109-v2`

Create from the accepted parent.

Do not rewrite the previous review packs.

## 0. Goal

Resolve the E1 cross-shape-oracle mistake if confirmed by the frozen runtime, then complete the intended shape/implementation experiment.

Independently, materialize and qualify a provenance-bound Q30 experts-control harness and run N/P/U-active only if its natural canary closes.

## 1. GPU ownership

Use:

`/data/c16/locks/c16_gpu_campaign.lock`

Verify expected RTX4080 identity.

Never kill/bypass another owner.

No environment/package upgrade is authorized.

## 2. E1-S0 — Frozen AWQ source/runtime audit

Using the exact environment that produced the accepted AWQ activation authority, record:

- `python -c` resolved path of `awq.modules.linear.gemm`;
- SHA256 of the installed `gemm.py`;
- package version if defined;
- package/wheel/source receipt if available;
- `awq_ext` shared-library path and SHA256;
- torch/CUDA versions;
- `WQLinear_GEMM.forward` and underlying function source text needed to prove shape dispatch.

Do not use public upstream source as the execution authority.

Public AutoAWQ may be cited only as background after the local source is frozen.

Create:

`AWQ_FROZEN_RUNTIME_SOURCE_CONTRACT.md`

## 3. E1-S1 — Prove the actual shape-path mapping

For both:

- layer0 q_proj
- layer0 down_proj

use the same accepted quantized module buffers and real activation source.

Execute:

- M=2048 with shape `[1,2048,K]`
- M=256 with shape `[1,256,K]`
- M=1 with shape `[1,1,K]`

Use lightweight NSYS/CUPTI/kernel logging or another low-overhead exact method to record the kernel sequence.

No NCU is required yet.

For each shape classify the module implementation path, for example:

- quantized GEMM;
- dequantize + torch matmul;
- other exact frozen path.

If local source and kernel fingerprint show that M2048 and M256 are different implementation paths:

record:

`CROSS_SHAPE_OUTPUT_ORACLE_INVALID_CONFIRMED`

and proceed to E1-S2.

If they are the same path:

do NOT reclassify the old mismatch.
Diagnose:
- input bytes/stride;
- hook timing/copy semantics;
- saved pool bytes;
- module-call boundary;
- stream/synchronization.

If no exact cause closes:

`STOP_SCIENTIFIC_E1_ORACLE_UNRESOLVED`

but continue E3 work.

## 4. E1-S2 — Corrected authority model

Separate:

### A. Real activation input authority

For each implementation/role:

- obtain the exact natural S2 M=2048 module input;
- bind token/model/module/runtime identity;
- freeze first 256 rows as M256 input;
- freeze first row as M1 input.

The input pool must retain natural rank and exact bytes.

### B. Shape-specific output authority

For each experimental shape:

- invoke the exact module at that exact shape;
- save output;
- immediately replay same shape/input;
- require the qualified repeatability contract for that shape.

For AWQ:
- M256 direct replay contract is already BITWISE_EQUAL and may be reused if exact input/module/runtime SHA matches;
- establish M1 repeatability separately.

Do NOT compare M1/M256 output to the natural M2048 output slice.

## 5. E1-S3 — Close raw q_proj/down_proj authority

Raw model:

`Qwen/Qwen2.5-7B-Instruct`

revision:

`a09a35458c702b33eeacc393d103063234e8bc28`

Common token SHA:

`0ab5bfe82130720edcbeac23c83b44b16cd8d21e4ccd5b4ee41c465c9159b4f9`

Target module paths:

- `model.layers.0.self_attn.q_proj`
- `model.layers.0.mlp.down_proj`

Use exact live module hooks to capture the natural M2048 inputs.

Derive:

- M256 `[1,256,K]`
- M1 `[1,1,K]`

Then establish shape-specific raw output replay authority at M256 and M1.

Reuse historical selective-loader utilities only with source attribution.

## 6. E1-S4 — Core 8-point experiment

Once shape-specific input/output authority closes, execute:

```text
raw q_proj M1
raw q_proj M256
AWQ q_proj M1
AWQ q_proj M256

raw down_proj M1
raw down_proj M256
AWQ down_proj M1
AWQ down_proj M256
```

For every point:

- 2 warmups;
- 5 CUDA-event measured repetitions;
- retain all samples;
- median + dispersion;
- exact module input SHA;
- output oracle SHA;
- kernel sequence;
- grid/block where available;
- implementation-path classification;
- output dtype.

Measure the complete module call.

Model loading is outside timing.

## 7. E1-S5 — Comparison scope

### Always valid

Within implementation:

- M1 vs M256 shape response;
- implementation path changes;
- kernel/resource behavior.

Natural deployment comparison:

- raw deployment result;
- AWQ deployment result;
- explicitly note that live activation distributions may differ.

### Cross-implementation same-input semantic comparison

Only if an exact raw/AWQ input semantic mapping is separately proven.

Otherwise:

`IMPLEMENTATION_LEVEL_ONLY`

Do not force one numeric activation into both and call it same-function semantics.

## 8. E1-S6 — Bounded profiling

Only after native timing and kernel fingerprint close.

Use standalone shape-specific module replay.

First prove a selector/range canary selects the intended semantic kernels.

Then collect only available metrics needed for:

- L1/TEX bytes;
- L2 bytes;
- DRAM bytes;
- tensor/math utilization;
- occupancy/warp activity;
- relevant stall/instruction evidence.

Zero selected kernels:

`SELECTOR_UNRESOLVED`

not `COUNTER_UNAVAILABLE`.

## 9. E1-T — Conditional implementation-transition diagnostic

Entry gate:

- local frozen AWQ source proves a deterministic shape threshold/path transition;
- E1 core is accepted;
- time budget remains.

Preferred role:

`down_proj`

If the threshold for preserved rank is M=1024, run:

- AWQ M1023
- AWQ M1024
- optionally raw M1023/M1024 as a control if cheap

Use the same real activation pool prefix.

Record path/timing/fingerprint.

Do not broaden into an arbitrary M sweep.

This diagnostic asks whether the implementation switch itself explains a discontinuity.

## 10. E3-S0 — Freeze exact Q30 local source/runtime

Authority:

`ee67225edc8fc5868de585d38e0391cbeb755d9f`

Use the exact accepted S2/T2048 Prefill target-layer state.

Record:

- local transformers/model source path;
- source file SHA256;
- model revision;
- target layer;
- hidden-state SHA;
- router/gate source;
- expert module source;
- accepted expert backend/weight residency policy.

Create:

`E3_FROZEN_SOURCE_CONTRACT.md`

## 11. E3-S1 — Materialize a diagnostic experts harness

The harness may be newly implemented, but only as an exact extraction/wrapper of the frozen model's expert execution semantics.

Allowed approaches:

A. call an existing exact experts function if the frozen runtime exposes one;

B. if the expert loop is inline, create a local diagnostic wrapper that reproduces the exact frozen token-grouping, expert-call, routing-weight application and combine operations using the same expert module objects.

Forbidden:

- changing expert math;
- changing weight format;
- replacing the backend;
- batching experts differently for performance;
- changing residency/loading policy;
- fusing/unfusing operations for convenience.

Record source diff and rationale.

## 12. E3-S2 — Natural N canary

From the exact accepted hidden state:

1. execute the exact natural gate/router;
2. capture natural `routing_weights` and `selected_experts`;
3. execute the diagnostic experts harness with those exact tensors;
4. compare against the natural expert-path output at the same boundary.

First evaluate repeatability of the natural expert-path output if needed.

N harness passes only under a separately documented numerical-repeatability contract.

If N cannot reproduce:

`STOP_SCIENTIFIC_HARNESS_CANARY_FAIL`

Do not run P/U.

## 13. E3-S3 — P histogram-preserving permutation

Freeze a deterministic permutation before timing.

Jointly permute token dimension of:

- hidden states;
- selected_experts;
- routing_weights.

Run the exact harness.

Inverse-permute the result.

Require:

- expert histogram exactly unchanged;
- routing weights follow their token;
- output matches N after inverse permutation under the qualified numerical contract.

P is primarily a harness/control validity test.

If P fails:
do not interpret U-active timing.

## 14. E3-S4 — U-active balanced routing

Only after N and P pass.

Let A be the sorted naturally active expert set.

Keep:

- M=2048;
- exact top-k;
- total assignments M*k;
- same experts/weights/backend;
- same hidden states;
- same per-token routing-weight vector values in rank order.

Construct deterministic balanced selected expert IDs within A such that:

- each token receives k distinct expert IDs;
- all expert IDs belong to A;
- global expert-count max-min <= 1 when mathematically possible.

Record exact construction and hash.

Label:

`SYNTHETIC_ROUTING`

No model-quality/equivalence claim.

## 15. E3-S5 — Light timing

For accepted N/P/U-active:

Measure exact expert execution region including the frozen dispatch/group/expert/weighted-combine semantics.

Use:

- 2 warmups;
- 5 measurements;
- all raw samples;
- active expert set;
- assignment histogram/CV;
- kernel sequence/shapes.

Router/gate timing is reported separately for N.

No detailed NVBit/SASS trace.

## 16. Scheduling

E1 and E3 are scientifically independent.

Recommended order:

1. E1-S0/S1 because the path-switch audit is very cheap and may immediately unblock E1;
2. E1-S2/S3/S4;
3. E3-S0/S1/S2;
4. whichever accepted followups remain.

If E1 reaches a scientific STOP, continue E3.

If E3 harness canary fails, finish E1.

GPU remains physically serial.

## 17. Solve-and-continue

Routine engineering issues:
solve and continue.

Scientific task-local failures:
freeze that task only.

Whole Goal STOP only for:

- GPU ownership/identity failure;
- shared model/storage corruption;
- exact runtime/source authority cannot be established.

## 18. Forbidden

No:

- new model download;
- package/runtime upgrade;
- random activation substitute;
- launch-order semantic binding;
- new quantization backend;
- modified expert backend;
- OLMoE/DeepSeek expansion;
- detailed trace campaign;
- architecture mechanism.

## 19. Deliverables

Report:

`docs/vm_tlb/codex_handoff/awma/E1_SHAPE_SPECIFIC_ORACLE_AND_MOE_HARNESS_109_V2_REPORT.md`

Review pack:

`docs/vm_tlb/review_packs/AWMA_E1_SHAPE_SPECIFIC_ORACLE_AND_MOE_HARNESS_109_V2/`

At minimum:

```text
README.md
SOURCE_ANCHORS.md
AWQ_FROZEN_RUNTIME_SOURCE_CONTRACT.md
AWQ_SHAPE_PATH_MATRIX.tsv
E1_INPUT_AUTHORITY_INDEX.tsv
E1_SHAPE_OUTPUT_ORACLE.tsv
RAW_ACTIVATION_AUTHORITY_INDEX.tsv
RAW_REPLAY_EQUIVALENCE.tsv
E1_CORE_MATRIX.tsv
E1_NATIVE_TIMING.tsv
E1_IMPLEMENTATION_FINGERPRINT.tsv
E1_RESOURCE_DIAGNOSIS.tsv
E1_TRANSITION_DIAGNOSTIC.tsv
E3_FROZEN_SOURCE_CONTRACT.md
E3_HARNESS_SOURCE_AUDIT.md
E3_N_CANARY.tsv
E3_P_EQUIVALENCE.tsv
E3_U_ACTIVE_CONSTRUCTION.json
E3_ROUTING_CASES.tsv
E3_NATIVE_TIMING.tsv
RUN_RECEIPTS.json
RAW_DATA_INDEX.tsv
SHA256SUMS
```

Use explicit SKIPPED/STOP status receipts where an optional task does not run.

Success marker:

`AWMA_E1_SHAPE_SPECIFIC_ORACLE_AND_MOE_HARNESS_109_V2_COMPLETE_WITH_SCOPE`

Then:

node164 ACK -> report -> review pack -> hashes -> commit -> push -> remote verify -> clean -> release GPU lock -> STOP.
