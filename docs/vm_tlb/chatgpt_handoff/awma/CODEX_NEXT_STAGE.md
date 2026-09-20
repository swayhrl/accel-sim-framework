# CODEX_NEXT_STAGE

Status: **ACTIVE**

Date: 2026-09-20

Stage:

`AWMA_ASYMMETRIC_CROSS_TARGET_MAINLINE_V1`

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

## 2. node109 — RELEASED NOW

Verified pause:

`hrl/awma-109-moe-causal-closure-scale-20h-v1 @ 0e32ac01b0237d94b39e45b288263e87e1960ccf`

The MoE candidate side lane is paused and published.

Execute now:

`CODEX_NEXT_STAGE_109_EXACT_TARGET_NATIVE_CROSSVIEW_V1.md`

Target set:

```text
T0 Q05_PREFILL_ATTN_FLASH
T1 PREFILL_GEMM_PRIMARY_OCC0
T2 DECODE_GEMV_PRIMARY_STEP16
```

Do not wait for 174 storage recovery.

No MoE/AWQ continuation.

## 3. 174-new — INFRASTRUCTURE RECOVERY FIRST

Current blocker:

`/root/share/mnt164 -> Transport endpoint is not connected`

Execute now:

`CODEX_RECOVER_174_NODE164_MOUNT_V1.md`

This is infrastructure-only.

No simulation.

If mount recovery PASS:

immediately continue:

`CODEX_REPAIR_174_V4_REMOTE_PUBLICATION_V2.md`

Only after:

`AWMA_174_V4_REMOTE_PUBLICATION_CLOSED_VERIFIED_V2`

may 174 execute:

`CODEX_NEXT_STAGE_174_CROSS_TARGET_HITPATH_VALIDITY_V1.md`

## 4. If node164 recovery requires external credentials

Return:

`BLOCKED_EXTERNAL_NODE164_CREDENTIAL_OR_MOUNT_AUTHORITY_REQUIRED`

with the exact non-secret mount/account/config requirement.

Do not repeatedly re-audit publication while storage remains unavailable.

109 continues independently.

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

Every 174 result must follow:

`174_MANDATORY_REMOTE_PUBLICATION_CONTRACT.md`

A local-only result is not complete.

## 8. Global boundaries

Do not automatically start:

- TLB/PTW/cache mechanisms;
- TLB capacity/page-size/walker/PWC sweeps;
- MoE mechanism;
- AWQ optimization;
- new model download.

After both scientific tracks complete, STOP and return to ChatGPT.
