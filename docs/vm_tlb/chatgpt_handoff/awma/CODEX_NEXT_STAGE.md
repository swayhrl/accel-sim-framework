# CODEX_NEXT_STAGE

Status: **ACTIVE**

Date: 2026-09-20

Stage:

`AWMA_TRANSLATION_HITPATH_SEMANTIC_ATTRIBUTION_V1`

Coordination branch:

`hrl/awma-mainline-reset-crossview-v2`

## 1. Read first

```text
docs/vm_tlb/chatgpt_handoff/awma/CURRENT_STATE.md
docs/vm_tlb/chatgpt_handoff/awma/EXECUTION_PRIORITY_POLICY_V3.md
docs/vm_tlb/chatgpt_handoff/awma/CANDIDATE_SIDE_LANES.md
docs/vm_tlb/chatgpt_handoff/awma/CROSSVIEW_JOIN_CONTRACT_V1.md
docs/vm_tlb/chatgpt_handoff/awma/MAINLINE_GATE_UPDATE_2026-09-20.md
docs/vm_tlb/chatgpt_handoff/awma/CODEX_NEXT_STAGE.md
```

## 2. node109 — COMPLETE_WITH_SCOPE

Accepted Native execution:

`hrl/awma-109-exact-target-native-crossview-v1 @ 2122eccc7aed61d05b114075e1c3126c4308e64b`

No new 109 GPU task.

MoE/AWQ candidate side lanes remain frozen.

## 3. 174-new — HIT-PATH SEMANTIC ATTRIBUTION READY

Accepted V3R1 execution:

`hrl/awma-174-exact-f0-segment-state-v3r1 @ 7a4f2a419fe77c017cb9a9a5555b1551a2fc884c`

Cross-target validity is now closed:

```text
T0 FlashAttention  56.9995%
T1 Prefill GEMM    59.7989%
T2 Decode GEMV     53.0990%
```

All three targets have L1-TLB hit rates above 99.7%; F0 Segment is functionally dormant for all admitted runs.

Primary classification:

`HITPATH_SENSITIVITY_SYSTEMATIC_ACROSS_KERNEL_CLASSES`

Execute now:

`CODEX_NEXT_STAGE_174_HITPATH_SEMANTIC_ATTRIBUTION_V1.md`

First perform source-only critical-path audit and existing-counter decomposition. Add telemetry-only instrumentation only if existing evidence is insufficient.

Do not implement a new hit-path model in this stage.

## 4. Cross-view decision

The large L1 hit-path sensitivity persists across Attention, Prefill GEMM, and Decode GEMV.

T0/T1 are clean anchors with invariant downstream admission counts. T2 is directionally consistent but has a nonlinear downstream-admission multiplicity change under 0/80 and must retain that caveat.

Mainline consequence:

`SIMULATOR_HITPATH_MODEL_REQUIRES_SEMANTIC_RECALIBRATION_BEFORE_MECHANISM`

## 5. Historical V4 treatment

The V4 runtime-load forensic qualification remains valid.

The six historical V4 lookup-latency points are:

`PARTIAL_NOT_ADMITTED / SUPERSEDED`

Do not reconstruct or republish them as a complete scientific matrix.

## 6. Shared scientific objective

Determine which exact simulator semantics cause a 10-cycle L1 translation lookup to become a 53-60% total-cycle effect, including accessq blocking, COAL_STALL behavior, lookup overlap/throughput, and T2 admission multiplicity.

## 7. Cross-view

Both scientific tracks follow:

`CROSSVIEW_JOIN_CONTRACT_V1.md`

Cross-view synthesis waits for both tracks.

## 8. 174 publication rule

The new V2 requalification result must follow:

`174_MANDATORY_REMOTE_PUBLICATION_CONTRACT.md`

A local-only result is not complete.

The obsolete V4 full-matrix publication is no longer a prerequisite.

## 9. Global boundaries

Do not automatically start:

- TLB/PTW/cache mechanisms;
- TLB capacity/page-size/walker/PWC sweeps;
- MoE mechanism;
- AWQ optimization;
- new model download.

After semantic attribution completes, STOP and return to ChatGPT before implementing any recalibrated hit-path model.
