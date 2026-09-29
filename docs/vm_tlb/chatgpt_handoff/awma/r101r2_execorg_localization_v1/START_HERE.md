# START HERE — AWMA R101R2 Execution-Organization Localization V1

## Mission

This is a **localization round**, not a new mechanism campaign.

Accepted history:

- R101 Native: `cfbe6503585fa1b10d979db5d26fb9be3a80e563`
- R101R1 Native L2 control: `422faf4d8fcdb5ac49068dcf19a6e783954a29a8`
- Transient-L2 FULL5 simulator: `8da4057b3c168543603401b1b42a99b556d98042`
- Full5 producer: `bb902283b7ce9e1902b460383fbd3e0bedbd884d`

Latest accepted conclusion:

`R101_TRANSIENT_L2_TRAFFIC_RESPONSE_NO_CYCLE_GAIN`

The previous mechanism removed about 92% of writeback, about 71% of modeled DRAM reads and about 19% of L2 misses, but cycles improved only 0.50%.

Therefore do **not** continue cache/writeback mechanism design in this round.

Literature/localization note:

`hrl/awma-chatgpt-literature-notes-v1 @ fb4d4292b9987a693c988b9ef2115de0c92c8a1f`

Read:

`docs/vm_tlb/literature_notes/awma/rounds/2026-09-29_ROUND_14_R101R2_EXECUTION_ORGANIZATION_LOCALIZATION.md`

## New experiment hierarchy

This round formally adopts:

- **L1** directed/micro/native diagnostic;
- **L2** CONTEXT2 scientific screen;
- **L3** FULL5/holdout only for a later survivor.

No FULL5 mechanism replay is authorized here.

## Parallel lanes

### Lane F — node109 Native profile

Goal:

`CODEX_GOAL_109_R101R2_S128_NATIVE_EXECUTION_PROFILE_V1.md`

Suggested branch:

`hrl/awma-r101r2-s128-native-profile-109-v1`

Purpose:
use the already accepted same-map S128 F128/K128 pair to quantify what the fused path actually removes or reorganizes.

No new workload, no gradient regeneration, no timing claim replacement.

### Lane E — 174-new CONTEXT2 oracle

Goal:

`CODEX_GOAL_174_R101R2_CONTEXT2_MEMORY_SERVICE_ORACLE_V1.md`

Suggested branch:

`hrl/awma-r101r2-context2-memory-service-174-v1`

Purpose:
derive a zero-copy CONTEXT2 view from the accepted FULL5 trace and test one upper bound:

`O2_TRANSIENT_1C_SERVICE_ORACLE`

O2 keeps the global memory instructions and kernel decomposition, but makes legal transient-region memory service essentially ideal for the measured second iteration.

Lane G remains free.

## Joint question

Does the remaining R101 same-map fused response come from:

1. **memory service headroom** that survives after the writeback/cache experiments, or
2. **execution work / organization** such as global-memory instruction issue, kernel decomposition, scheduling, occupancy and compute dataflow?

## Joint decision

### If O2 measured-ROI cycle improvement >= 5%

`R101R2_MEMORY_SERVICE_HEADROOM_PRESENT`

A later mechanism round may study bounded producer-consumer local handoff. O2 itself is not a mechanism.

### If O2 < 5% and Native F128/K128 shows large execution-work reduction

`R101R2_EXECUTION_ORGANIZATION_DOMINANT`

Close the cache/lifetime performance line. Follow software/kernel fusion or execution/dataflow organization, not another L2 mechanism.

### Otherwise

`R101R2_MIXED_EXECUTION_RESIDUAL`

Do not expand hardware mechanism scope without a new discriminating experiment.

## Storage

174 local disk remains constrained.

Continue to use node164 mounted storage for large immutable traces and raw output.

Do not make local staging a requirement.

Efficiency comes from CONTEXT2 and matched-context ROI, not from copying data.

## Shared rules

- all new simulator features opt-in/default OFF;
- no model download;
- no new 109 capture;
- no new FULL5 replay;
- no parameter sweep;
- no holdout in this localization round;
- ordinary engineering solve-and-continue;
- deterministic derived views are P2/P3 controls, not missing science;
- scientific identity/semantics/claim change => STOP for review;
- node164 remains durable authority;
- no auto-merge.
