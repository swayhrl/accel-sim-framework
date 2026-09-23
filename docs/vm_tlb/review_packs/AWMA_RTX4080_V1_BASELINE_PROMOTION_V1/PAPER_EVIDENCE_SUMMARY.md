# Paper evidence summary

## Platform

Frozen `RTX4080_ADA_ACCELSIM_BASE_V1`, scoped to AWMA memory/translation studies.

## External semantic evidence

V1 has `V1_EXTERNAL_SEMANTIC_SUPPORT_PARTIAL`; V2R1 adds no external alignment benefit. The base-concurrency residual is frozen.

## AI regression

All 12 T0/T1/T2 Legacy/V1 x 10/80/0/80 points pass identity, coverage, Segment-dormancy, duplicate, and quiescence gates. V1 reduces lookup-latency sensitivity versus Legacy on every target. Zero-latency flags, if present, are reported in `AI_SEMANTIC_ANALYSIS.tsv` and do not hide correctness results.

T0/T1 zero-latency flags are attributed to the frozen V1 prelaunch-ready-unapplied ordering path; exact lookup/READY counts are in `ZERO_LATENCY_DIVERGENCE_ANALYSIS.tsv`.

## Decision

`AWMA_RTX4080_SIM_BASELINE_V1_PROMOTED_WITH_SCOPE`. V1 is selected through a named runtime manifest, not an unconditional source default.
