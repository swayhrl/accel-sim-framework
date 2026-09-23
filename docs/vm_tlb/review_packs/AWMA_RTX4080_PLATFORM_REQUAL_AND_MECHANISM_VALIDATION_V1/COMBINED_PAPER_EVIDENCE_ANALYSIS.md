# Combined paper-evidence analysis

## Platform

`RTX4080_ADA_PLATFORM_QUALIFIED` with median matched-heldout error `12.2112%`. The unchanged config is `RTX4080_ADA_ACCELSIM_BASE_V1`; H_CACHE is a bounded outlier.

## M0-M3 contextual controls

Controls preserve warmup->measurement process ordering, with natural L1 invalidation and preserved L2/TLB/PWC/controller state. They remain mechanism-inactive and are not tuning data.

## Mechanism-sensitive probes

A1/A8/A32/A32_W8 realize actual multi-entry accessq opportunities under the simulator coalescing contract. Native-relative classification: `V1_EXTERNAL_SEMANTIC_SUPPORT_PARTIAL` and `V2R1_ADDS_NO_EXTERNAL_ALIGNMENT_BENEFIT`. Candidate status: `V1_BASELINE_PROMOTION_CANDIDATE`.

## Existing AI evidence

Historical T0/T1/T2 evidence remains simulator-internal causal support only. No SM86 AI cycle is reused as RTX4080 external calibration evidence, and no expensive AI target is rerun here.
