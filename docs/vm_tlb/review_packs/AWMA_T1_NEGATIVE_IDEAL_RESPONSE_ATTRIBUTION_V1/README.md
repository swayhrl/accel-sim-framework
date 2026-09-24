# AWMA T1 negative ideal-response attribution V1

Status: `COMPLETE_PHASE1_NO_CAUSAL_CONTROL`

This review pack is the Phase-1 observational attribution for the accepted
`PREFILL_GEMM_PRIMARY_OCC0` T1 point.  It does not change the frozen ideal
translation mechanism, add a translation mechanism, tune VM parameters, or run
another workload.

Authorities:

- ideal control: `hrl/awma-rtx4080-v1-ideal-translation-control-v3` at
  `5e59fbcf7e5217e91d40e5ff2e38dfd3f48a97f8`
- flash extension (frozen, not used as source parent):
  `hrl/awma-rtx4080-v1-ideal-translation-flash-extension-v1` at
  `110008c766bcd96dd68bac8ae9f3ed467931aa80`
- attribution branch:
  `hrl/awma-t1-negative-ideal-response-attribution-v1`

Execution identity:

- observational binary SHA-256:
  `301921a03a7629ebac004cd720714310e5d1d7bd4f780939ab952b87a43b7b41`
- platform config SHA-256:
  `de9ee8f30325c033e0de624640ffa8803f0eae40633eebaa0b3144f549f5ccb8`
- trace config SHA-256:
  `a46fe47a14f3ca4116a35c5bf1dc156f4e861484b91278e8b3f6e09519bdd7e5b`

Files:

- `T1_NEGATIVE_IDEAL_ATTRIBUTION_REPORT.md`: decision and interpretation
- `DOWNSTREAM_TIMELINE_SUMMARY.tsv`: release/admission cycle-window and progress data
- `MEMORY_PRESSURE_SUMMARY.tsv`: cache/interconnect/partition/DRAM pressure
- `WORK_CONSERVATION.tsv`: logical and downstream work quantities
- `HYPOTHESIS_DECISION.tsv`: H1--H4 decisions
- `VALIDATION.json`: semantic and scientific closure gates
- `ATTRIBUTION_SUMMARY.json`: machine-readable parsed evidence
- `T1_ATTRIBUTION_TELEMETRY.patch`: opt-in observational instrumentation
- `RAW_LOG_INDEX.sha256`: raw/runtime evidence hashes

No `CAUSAL_CONTROL.tsv` is emitted unless Phase 1 supports a bounded,
source-justified matched-release pacing rule without changing the frozen ideal
semantic contract.

Phase 1 supports H1 (burstiness/queue pressure) with H3 as a secondary progress
effect, does not support H2 (locality/work amount), and rejects H4.  No Phase-2
control was run because no bounded pacing rule could be derived without either
replaying treatment-dependent OFF timestamps or adding a new admission-control
law.  Therefore `CAUSAL_CONTROL.tsv` is intentionally absent.
