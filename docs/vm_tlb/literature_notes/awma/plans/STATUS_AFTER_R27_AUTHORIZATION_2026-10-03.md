# Status after R27 varied-batch Goal authorization

Date: 2026-10-03 (Asia/Shanghai)

This supersedes [the R26 review status](STATUS_AFTER_R26_REVIEW_2026-10-02.md) only for current task authorization. R26's accepted result and limitations remain unchanged.

## Current activity

- Lane G / node109: **R27 AUTHORIZED / HANDOFF_READY**. Publication does not establish that node109 has started.
- Sole new AWMA GPU Goal: `AWMA_R27_TIED_WEIGHT_VARIED_BATCH_CAPACITY_STABILITY_109_V1`; one gated execution branch, with automatic continuation only across passing gates.
- R26 / R25 / R24 / R23G: COMPLETE / STOP. Lane F / R22F1, Lane E / R22E: STOP. R20: CLOSED.
- No node174/Accel-Sim, profiler, hardware/PPA, all-parameter training, deployment or further-stage authorization.

Handoff branch:
`hrl/awma-r27-varied-batch-capacity-handoff-v1`

Exact handoff HEAD:
`5144bde8f9d7b399a596395e0c88ee89025b3a6f`

Exact handoff tree:
`605f0360debb3f62a1923452c91552ca1f2acaa9`

Git parent:
R26 execution `1a2485011b300cddd5137bbccb91dd6d30cfc22f`.

Execution branch to create:
`hrl/awma-r27-varied-batch-capacity-109-v1`.

Start with [START_HERE](https://github.com/swayhrl/accel-sim-framework/blob/5144bde8f9d7b399a596395e0c88ee89025b3a6f/docs/vm_tlb/chatgpt_handoff/awma/r27_varied_batch_capacity_v1/START_HERE.md), then read the accepted R26 review snapshot, parent authority, full Goal and machine contract. [R27 research plan](R27_VARIED_BATCH_CAPACITY_PLAN_2026-10-03.md) explains the combined gates.

The only new input is the SHA-pinned WikiText-2 raw train parquet. The common CPU state is the exact archived R26 snapshot; the older R25 bit-hash mismatch is preserved, not rewritten. R27 tests varied batch and step content, adjacent natural-OOM capacity and positive-only 32-step/recovery. A qualified negative result closes the Goal. No formal timing or production pilot is in scope.

All CUDA/JIT on node109 must hold `/data/c16/locks/c16_gpu_campaign.lock`. The execution report and review pack are required before a scientific review and any later decision.
