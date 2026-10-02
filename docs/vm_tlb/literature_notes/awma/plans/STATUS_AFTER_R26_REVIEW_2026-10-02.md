# Status after R26 integrated-capacity review

Date: 2026-10-02 (Asia/Shanghai)

This supersedes [the R26 authorization status](STATUS_AFTER_R26_PRODUCTION_CAPACITY_AUTHORIZATION_2026-10-02.md) for current activity. Its authorization and launch details remain historical evidence.

## Current state

- Lane G / node109: R26 **COMPLETE / REVIEW ACCEPTED / STOP**. Accepted decision: `R26_INTEGRATED_BATCH_CAPACITY_EXTENSION_SUPPORTED`, scoped to the frozen tied-W repeated-sequence, five-step physical-batch experiment.
- R25 / R24 / R23G: COMPLETE / STOP. Lane F / R22F1 and Lane E / R22E: STOP. R20: CLOSED.
- No active new AWMA GPU authorization; no R27, node174/Accel-Sim, profiler, hardware/PPA or deployment task follows automatically.

Execution branch `hrl/awma-r26-tied-weight-production-capacity-109-v1` closed at `1a2485011b300cddd5137bbccb91dd6d30cfc22f` (tree `cce37bbbd368b545bea92c7b86cb429d8da4f48b`). The [R26 review](../empirical/R26_TIED_WEIGHT_CAPACITY_REVIEW_2026-10-02.md) records verification, limitations and evidence provenance; the [execution review pack](https://github.com/swayhrl/accel-sim-framework/tree/1a2485011b300cddd5137bbccb91dd6d30cfc22f/docs/vm_tlb/review_packs/AWMA_R26_TIED_WEIGHT_PRODUCTION_CAPACITY_BOUNDARY_109_V1) contains the frozen results.

C1 PASS B70/OOM B71 and S2 PASS B71/OOM B72 were confirmed 3/3; same-B B71 is C1 OOM versus S2 five-step PASS. B70 whole-step median peak allocated is 3.828 MiB *higher* for S2, while formal TARGET_REGION and COMPLETE_TRAIN_STEP timing are both MIXED. The R25 parent start-state hash was not bitwise reproduced; all R26 arms used one disclosed and frozen same-semantics CPU start. Batch content consists of repeated copies of one input sequence.

The execution node reports 207 archive/checkpoint manifest items checked, lock released and no campaign CUDA process. This review independently checked the 31 Git pack SHA256 values and recomputed tabular summaries, without node164 raw/traceback access or a new GPU run. Future claims must retain that distinction.

A possible separate next decision is limited capacity-oriented hardening with varied batches and longer training-history checks. This status creates no launch authority.
