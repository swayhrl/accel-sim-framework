# C12 operator-aware changed files

## Analysis implementation

- `util/vm_tlb/c12_operator_trace_scan.cc` — read-only all-lane trace scanner;
  counts exact intersections with sidecar object and parameter intervals
  without launching a simulator.
- `util/vm_tlb/analyze_c12_operator_aware.py` — provenance checks, direct
  taxonomy mapping, cumulative-counter differencing, KERNEL telemetry
  aggregation, terminal-PASS filtering, and typed TSV/report generation.

## Review-pack evidence

- Required review artifacts: `FINAL_REPORT.md`, `PAPER_FACING_FINDINGS.md`, `PROVENANCE.md`,
  `OBSERVABILITY_AUDIT.md`, `INDEX_ALIGNMENT_AUDIT.tsv`,
  `KERNEL_OPERATOR_MAP.tsv`, `OPERATOR_COVERAGE.tsv`,
  `F0_OPERATOR_CHARACTERIZATION.tsv`, `F0_OPERATOR_OBJECT_SUMMARY.tsv`,
  `F0_OPERATOR_TRANSLATION_SUMMARY.tsv`, `F0_OPERATOR_CACHE_SUMMARY.tsv`,
  `ARM_OPERATOR_CHARACTERIZATION.tsv`, `OPERATOR_ARM_DELTAS.tsv`,
  `LSEG_OPERATOR_SENSITIVITY.tsv`, and `PAPER_FACING_FINDINGS.md`.
- Additional audit evidence: `INTERIM_REPORT.md` (superseded historical pointer), `CONSERVATION_AUDIT.md`,
  `KV_CLASS_TRANSACTION_AUDIT.tsv`, `KV_CLASS_TRANSACTION_AUDIT.md`,
  `PARAMETER_RANGES_{prefill,decode1}.tsv`,
  `OBJECT_RANGES_{prefill,decode1}.tsv`, and
  `TRACE_SCAN_{prefill,decode1}.tsv`.

The committed trace-scan TSVs are lightweight, derived audit tables.  Raw
traces, raw logs, validation sidecars, C12 formal input tables, and temporary
worker/resume shards are not committed or modified.
