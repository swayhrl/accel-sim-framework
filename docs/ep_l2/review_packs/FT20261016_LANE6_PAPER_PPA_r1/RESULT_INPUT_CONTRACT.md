# Future Lane-4/5 result ingestion

This is a Lane-6 adapter format, not a replacement for Lane-1 runtime or
Lane-5 runner contracts. Preserve original producer manifests/CSVs unchanged;
translate only in a separate adapter. A later pack can adapt to the actual
published schema by an explicit reviewed change. r1 has consumed zero new
implementation and zero new ideal result rows.

`plot_verified_results.py ADAPTER.json --framework-repo REPO --output-dir NEW_PACK`
expects an adapter with:

```json
{
  "schema": "EP_L2_LANE6_VERIFIED_RESULT_ADAPTER_V1",
  "coordination_commit": "6c136e2a56a008695f8c8b815723bf8f1a760db9",
  "evidence_kind": "FUNCTIONAL_IMPLEMENTATION",
  "source_lane": 5,
  "publication_commit": "FULL_40_HEX_UPSTREAM_PUBLICATION_COMMIT",
  "receipt_repository_path": "docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/lane5/RECEIPT.json",
  "receipt_sha256": "FULL_SHA256",
  "bundle_repository_path": "UPSTREAM_PUBLISHED_BUNDLE_JSON_PATH",
  "bundle_sha256": "FULL_SHA256",
  "results_csv": "LOCAL_UNMODIFIED_PRODUCER_CSV",
  "run_manifests": {"RUN_ID": "LOCAL_UNMODIFIED_PRODUCER_MANIFEST"},
  "baseline_mode": "B16_BANKED",
  "candidate_mode": "U_WB16",
  "cohort": "development"
}
```

Relative local paths resolve against the adapter directory. No example
placeholder is a valid digest. The receipt and bundle are read with `git show`
at the exact publication commit and hashed. The receipt must name the bundle
in `artifacts`. Bundle normalized keys are `results_csv_sha256` and
`run_manifest_sha256s` keyed by run ID. It binds every unchanged scientific
input used by this plot. If the upstream bundle has another format, provide
a reviewable adapter update; never invent a binding that it does not contain.

CSV columns: `run_id,workload,mode,evidence_kind,status,cycles,instructions`.
One complete baseline/candidate pair is required for every predeclared cohort
workload; extras, duplicates and missing rows are rejected rather than hidden.
Cohorts are development (five), validation (btree/dwt2d), or scan (one).

Each normalized runtime manifest must retain full `core_source_commit`,
`framework_source_commit`, `binary_sha256`, `config_sha256`, `trace_sha256`,
`raw_log_sha256`, `epoch_range`, `feature_vector`, `ideal_vector`,
`effective_config`, `status`, `evidence_kind`, `run_id`, `workload`, `mode`,
`cycles`, `instructions` and `validation`. Normalized fields must be emitted
or unambiguously mapped from the hash-bound producer payload, not inferred
from a filename. Required feature bits are `unified_wb,tvd,ro,oracle_ro`;
ideal bits are `I_WB,I_META,I_READ_HIT`. Preserve additional producer bits.
Every bit is explicit boolean, including false. Effective config excludes
feature/ideal selectors only and retains every other effective setting;
the full original runtime config digest remains recorded separately.

For functional/oracle pairs require identical source/binary/trace/epoch and
effective base config, one explicit feature transition matching the declared
comparison, no enabled ideal bit, 4 Banks, one line-op/Bank/cycle, and
1168 or 1160 total data slots. Allowed first comparisons are B16/U_WB16 and
B8/U_WB8. TVD/RO/strong-partition comparisons require their own reviewed
comparison contract rather than being silently accepted by this first-WB tool.
Oracle-assisted and ideal results have separate plots/datasets. This tool
does not calculate speedups from shadow observations or historical rows.

Validation booleans required true: `normal_exit,parser_success,terminal_clean,
payload_consistent,request_identity_check,data_version_check`. An upstream
`COMPLETE_VALID` label alone is insufficient. No Lane-6 plot substitutes for
independent scientific review, and passing this schema does not certify
unexamined producer semantics.
