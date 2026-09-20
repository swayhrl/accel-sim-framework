# CODEX_NEXT_STAGE

Status: **ACTIVE**

Date: 2026-09-20

Stage:

`AWMA_174_VM_MAP_SEMANTICS_AND_CROSS_TARGET_ADMISSION_V3`

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

## 3. 174-new — VM MAP SEMANTICS / ADMISSION READY

Accepted V2 execution:

`hrl/awma-174-minimal-requalified-cross-target-hitpath-v2 @ f34b53597ab7d9175f8286dde67f4313462aabb5`

T0 is requalified and remote-published:

```text
10/80 = 1,654,548
0/80  =   711,464
0/0   =   745,880
```

T1/T2 are `TARGET_NOT_ADMITTED` because their producer bundles lack target-specific VM object/segment map bindings.

Execute now:

`CODEX_NEXT_STAGE_174_VM_MAP_SEMANTICS_CROSS_TARGET_V3.md`

This stage first audits whether the map contents are functionally relevant under the exact repaired F0 runtime.

If a source-safe neutral compatibility view is proven, run the T0 neutral-map equivalence gate and then only T1/T2 `10/80` + `0/80`.

If target-specific allocation metadata is functionally required, STOP and report the exact metadata contract. Do not automatically recapture on 109.

## 4. V2 interpretation boundary

T0 shows very large modeled L1 hit-path sensitivity despite an approximately 99.89% L1-TLB hit rate.

`0/0` is slower than `0/80`; therefore zeroing L2 lookup is non-additive and is not the primary cross-target metric.

Primary cross-target metric:

`10/80 -> 0/80`

## 5. Historical V4 treatment

The V4 runtime-load forensic qualification remains valid.

The six historical V4 lookup-latency points are:

`PARTIAL_NOT_ADMITTED / SUPERSEDED`

Do not reconstruct or republish them as a complete scientific matrix.

## 6. Shared scientific objective

Determine whether repaired simulator translation hit-path sensitivity:

- persists across Attention / Prefill GEMM / Decode GEMV;
- is Attention-dominant;
- is target-dependent;
- or indicates simulator hit-path semantic recalibration is required.

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

After both scientific tracks complete, STOP and return to ChatGPT.
