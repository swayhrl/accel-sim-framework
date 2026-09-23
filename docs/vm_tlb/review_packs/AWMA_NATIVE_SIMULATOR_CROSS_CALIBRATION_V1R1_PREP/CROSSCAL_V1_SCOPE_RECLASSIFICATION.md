# Cross-Cal V1 scope reclassification

The original 24/24 simulator results remain valid and immutable. Their evidence class is now `CROSSCAL_V1_WARMUP_TRACE_SUPPORTING_ONLY`.

Closed facts:

- `CURRENT_M0_M3_TRACE_PHASE = WARMUP_CHASE_OCCURRENCE0`.
- `MEASURED_OCCURRENCE1_TRACE_NOT_PRESENT_IN_ACCEPTED_BUNDLE`.
- `TRACE_PERMUTATION_SEED_UNRESOLVED`.
- `M0_M3_MECHANISM_INACTIVE_CONTROL_SUITE`.
- SM89 parser admission closes for the 38-opcode trace subset; no Ada architectural-fidelity claim is made.

The V1 working-set and multi-warp numbers remain valid simulator facts for the warmup occurrence0 payloads. The comparison to Native V1R2 occurrence1/seed102 is not exact. Consequently `MIXED_NATIVE_SIMULATOR_ALIGNMENT`, `V1_NATIVE_ALIGNMENT_PARTIAL`, and `V2R1_ADDS_NO_NATIVE_ALIGNMENT_BENEFIT` are not admitted as final Native cross-calibration classifications. Exact Native disagreement, external validation/invalidation of V1/V2R1, and baseline readiness remain pending measured occurrence1 payloads with closed seed and contextual warmup→measurement replay.

No 24-point rerun, AI-target rerun, semantic change, parameter tuning, baseline promotion, or new mechanism was performed.
