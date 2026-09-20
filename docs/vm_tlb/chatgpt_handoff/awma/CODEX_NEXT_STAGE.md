# CODEX_NEXT_STAGE

Status: **ACTIVE**

Date: 2026-09-20

Stage:

`AWMA_174_MINIMAL_REQUALIFIED_CROSS_TARGET_HITPATH_V2`

Coordination branch:

`hrl/awma-mainline-reset-crossview-v2`

## 1. Read first

```text
docs/vm_tlb/chatgpt_handoff/awma/CURRENT_STATE.md
docs/vm_tlb/chatgpt_handoff/awma/EXECUTION_PRIORITY_POLICY_V2.md
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

## 3. 174-new — SCIENTIFIC REQUALIFICATION READY

node164 access is restored.

Review commit:

`46de0c35e2c26fdabd9fc691370bedf0cc5974f5`

establishes that the old six-point V4 lookup matrix is incomplete and not admissible.

Do NOT continue V4 publication repair.

Execute now:

`CODEX_NEXT_STAGE_174_MINIMAL_REQUALIFIED_CROSS_TARGET_V2.md`

This Goal is explicitly authorized to run a minimal scientific requalification.

Target set:

```text
T0 Q05_PREFILL_ATTN_FLASH
T1 PREFILL_GEMM_PRIMARY_OCC0
T2 DECODE_GEMV_PRIMARY_STEP16
```

Common matrix:

```text
10/80
0/80
0/0
```

T0 fresh 10/80 control must exactly reproduce the accepted isolated repaired R0 authority before T0 latency diagnostics or T1/T2 proceed.

## 4. Historical V4 treatment

The V4 runtime-load forensic qualification remains valid.

The six historical V4 lookup-latency points are:

`PARTIAL_NOT_ADMITTED / SUPERSEDED`

Do not reconstruct or republish them as a complete scientific matrix.

## 5. Shared scientific objective

Determine whether repaired simulator translation hit-path sensitivity:

- persists across Attention / Prefill GEMM / Decode GEMV;
- is Attention-dominant;
- is target-dependent;
- or indicates simulator hit-path semantic recalibration is required.

## 6. Cross-view

Both scientific tracks follow:

`CROSSVIEW_JOIN_CONTRACT_V1.md`

Cross-view synthesis waits for both tracks.

## 7. 174 publication rule

The new V2 requalification result must follow:

`174_MANDATORY_REMOTE_PUBLICATION_CONTRACT.md`

A local-only result is not complete.

The obsolete V4 full-matrix publication is no longer a prerequisite.

## 8. Global boundaries

Do not automatically start:

- TLB/PTW/cache mechanisms;
- TLB capacity/page-size/walker/PWC sweeps;
- MoE mechanism;
- AWQ optimization;
- new model download.

After both scientific tracks complete, STOP and return to ChatGPT.
