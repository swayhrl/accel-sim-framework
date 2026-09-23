# RTX4080 Platform Requalification + Mechanism Validation 174-new V1 Report

The frozen platform passed no-tuning requalification as `RTX4080_ADA_PLATFORM_QUALIFIED`: matched-heldout median error `12.2112%`, mean `22.8397%`, worst `44.1950%`, and no >2x point. Config `de9ee8f30325c033e0de624640ffa8803f0eae40633eebaa0b3144f549f5ccb8` is frozen as `RTX4080_ADA_ACCELSIM_BASE_V1`.

AWMA 10/80 M0/M1 overlay smoke passed. Exact M0-M3 contextual controls completed under the scoped `RTX4080_ADA_BASE_V1 + AWMA_MODEL_RELATIVE_VM` contract. Natural kernel-boundary L1 invalidation is reported; L2 and translation controller/TLB/PWC state persist.

Mechanism-sensitive accessq opportunity closed at sector-level cardinalities documented in the review pack. All 24 Legacy/V1/V2R1 x 10/80/0/80 points completed with exact measurement brackets, full emitted translation coverage, zero V2R1 duplicate application, and final quiescence.

Scientific classifications: `V1_EXTERNAL_SEMANTIC_SUPPORT_PARTIAL`, `V2R1_ADDS_NO_EXTERNAL_ALIGNMENT_BENEFIT`, `MECHANISM_SENSITIVE_ALIGNMENT_MIXED`, `V1_BASELINE_PROMOTION_CANDIDATE`. No platform or VM parameter was changed from any M0-M3 or A1/A8/A32/A32_W8 result.
