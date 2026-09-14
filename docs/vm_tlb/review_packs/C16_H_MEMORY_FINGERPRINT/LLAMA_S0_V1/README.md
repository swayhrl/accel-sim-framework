# C16 H Llama S0 memory fingerprint V1

This pack deliberately separates **EXPLORATORY_HISTORICAL_CAPTURE** results
from C16 formal evidence.  See `CAPTURE_ADMISSION.tsv` first.  It does not
modify the empty formal C16 H tables or declare a whole-model TLB/cache result.

- `INPUT_PROVENANCE.tsv` and `RAW_INDEX.tsv`: source identity, receipt gaps, raw paths, and SHA closure.
- `MEMORY_FINGERPRINTS.tsv`: measured selected-PC structural metrics.
- `PREFILL_DECODE_COMPARISON.tsv`: controlled presentation of the two available historical streams.
- `CROSS_DECODE_OVERLAP.tsv`: explicit `NOT_AVAILABLE` results for missing Decode2--4.
- `TRACE_SCOPE_AUDIT.md`: claim-by-claim sufficiency boundary.
- `DOWNSTREAM_CAPTURE_SCOPE_DECISION.md`: Route A/B/C decision for subsequent formal capture.
- `VALIDATION.md`: local tests, real parser canary, and raw-SHA checks.

Raw trace files remain external and are never committed.  All address metrics
are `GPU_VA_OBSERVED` structural metrics, not PA facts, hardware TLB misses, or
global cache-reuse measurements.
