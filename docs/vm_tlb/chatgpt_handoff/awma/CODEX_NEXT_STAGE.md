# CODEX_NEXT_STAGE

Status: **ACTIVE**

Date: 2026-09-20

Stage:

`AWMA_174_EXACT_F0_SEGMENT_STATE_CLOSURE_V3R1`

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

## 3. 174-new — EXACT F0 RUNTIME-STATE CLOSURE READY

Accepted V2 execution:

`hrl/awma-174-minimal-requalified-cross-target-hitpath-v2 @ f34b53597ab7d9175f8286dde67f4313462aabb5`

V3 source/config audit:

`hrl/awma-174-vm-map-semantics-cross-target-v3 @ b3310731956d0f731da47bb324cc22d661002dfc`

V3 correctly proved an active Segment descriptor can affect functional translation, but it did not close the post-parse F0 runtime state.

Accepted repaired F0 evidence already reports:

```text
vm_weight_segmentation_enabled = 0
segment lookup attempts = 0
segment hits = 0
segment suppression counters = 0
```

Therefore do NOT authorize node109 recapture yet.

Execute now:

`CODEX_NEXT_STAGE_174_EXACT_F0_SEGMENT_STATE_V3R1.md`

Phase A is zero-science: inspect exact V2 T0 immutable logs and fair-arm post-parse source state.

If exact V2 T0 confirms Segment functionally dormant, reuse the exact accepted T0 compatibility assets as model-generic dormant F0 configuration and admit T1/T2 with a hard zero-Segment-activity gate.

Only if exact V2 T0 has nonzero Segment participation does `TARGET_SPECIFIC_VM_METADATA_REQUIRED` become confirmed.

## 4. V3 correction boundary

T0 still shows very large modeled L1 hit-path sensitivity despite an approximately 99.89% L1-TLB hit rate.

V3's `TARGET_SPECIFIC_VM_METADATA_REQUIRED` is provisional until exact V2 T0 runtime Segment state is closed.

The exact T0 compatibility-map SHA values correspond to whole-VA compatibility views, not target-precise runtime allocation maps.

Primary cross-target metric remains:

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
