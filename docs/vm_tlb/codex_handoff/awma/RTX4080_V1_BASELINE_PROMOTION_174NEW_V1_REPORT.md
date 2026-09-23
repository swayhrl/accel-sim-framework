# RTX4080 V1 Baseline Promotion 174-new V1 Report

Decision: `AWMA_RTX4080_SIM_BASELINE_V1_PROMOTED_WITH_SCOPE`.

The exact frozen RTX4080 platform config `de9ee8f30325c033e0de624640ffa8803f0eae40633eebaa0b3144f549f5ccb8` and frozen 10/80 / 0/80 VM overlays were used without tuning. One unified runtime-switchable binary completed all 12 T0/T1/T2 x Legacy/V1 x 10/80/0/80 points.

Every point closes target identity, instructions/CTA, accepted unique UID, full translated coverage, zero untranslated/unobserved, dormant Segment, zero duplicate application, terminal execution, and controller quiescence. Controller regressions pass 3/3.

V1 reduces modeled lookup-latency amplification versus Legacy on all three AI targets. Exact sensitivities and zero-latency comparisons are in `AI_SEMANTIC_ANALYSIS.tsv`; material >2% zero-latency differences are explicitly flagged and scoped rather than hidden.

The T0/T1 0/80 flags are explained by the frozen V1 prelaunch path issuing additional lookups while intentionally leaving READY results unapplied; full coverage, side-effect, Segment, and quiescence gates remain clean.

The promoted named baseline is `AWMA_RTX4080_SIM_BASELINE_V1`: platform `RTX4080_ADA_ACCELSIM_BASE_V1`, primary model-relative 10/80 overlay, V1 pipeline launch enabled, ready-application V2 disabled. Legacy and 0/80 remain selectable controls; V2R1 is diagnostic-only. No source-wide unconditional default was introduced.

Known scope remains `BASE_CONCURRENCY_MODEL_RESIDUAL` and `QUALIFIED_FOR_AWMA_MEMORY_TRANSLATION_STUDIES`.
