# CODEX_NEXT_STAGE

Status: **ACTIVE**

Date: 2026-09-20

Stage:

`AWMA_TRANSLATION_FRONTEND_PIPELINING_RECALIBRATION_V1`

Coordination branch:

`hrl/awma-mainline-reset-crossview-v2`

## 1. Read first

```text
docs/vm_tlb/chatgpt_handoff/awma/CURRENT_STATE.md
docs/vm_tlb/chatgpt_handoff/awma/EXECUTION_PRIORITY_POLICY_V4.md
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

## 3. 174-new — TRANSLATION FRONTEND RECALIBRATION READY

Accepted attribution execution:

`hrl/awma-174-hitpath-semantic-attribution-v1 @ f79aaa1d22d2a22912e8b71dc832bdbf31a899f7`

Accepted classification:

`MIXED_MODEL_EFFECT`

with:

```text
SERIALIZED_PRE_ADMISSION_LOOKUP_WAIT_DOMINANT
ACCESSQ_HEAD_OF_LINE_TRANSLATION_BLOCKING_DOMINANT
ZERO_LATENCY_RETRY_ORDERING_NONLINEARITY
```

T2's extra 65,899 coverage admissions at 0/80 are repeated admission attempts with the same 411,008 unique logical UIDs.

Execute now:

`CODEX_CONTINUE_174_CANONICAL_T0_INPUT_RECOVERY_V1.md`

This continuation remains within `AWMA_TRANSLATION_FRONTEND_PIPELINING_RECALIBRATION_V1`; it first recovers a clean standard top-level build, then resumes the original frontend-pipelining Goal.

First repair telemetry semantics without changing timing, then implement an opt-in single-axis pipelined accessq translation-launch candidate. Keep probe-at-completion and all PTW/MSHR semantics unchanged in V1.

Do not promote the candidate to baseline in this stage.

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

Test whether separating translation lookup latency from accessq launch serialization removes most of the legacy 53-60% sensitivity while preserving per-access translation correctness and all downstream functional invariants.

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

After diagnostic frontend recalibration completes, STOP and return to ChatGPT before promoting any candidate semantics to the accepted baseline.
