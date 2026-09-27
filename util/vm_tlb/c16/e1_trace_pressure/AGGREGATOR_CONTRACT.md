# C16 E1 trace-pressure aggregation contract

`analyze_pressure.py` consumes compact scanner output only. It never opens the
qualified `.traceg.xz` corpus and does not run timing simulation.

Per-kernel input lives at `kernels/<id>/summary.json`, using scanner schema
`C16_E1_TRACE_KERNEL_SUMMARY_V1` (`decode_index`, the 28-entry
`per_target_class_references`, and `target_boundaries`). The reader also accepts
the earlier pressure-scanner schema during fixture migration. Sorted-unique
little-endian uint64 files
are `all_unique_lines.u64` and `non_target_unique_lines.u64`; full kernels also
carry dense little-endian uint64 `all_set_refs.u64`. Dense bins use
`subpartition * sets_per_subpartition + set`.

Every kernel containing a real target reference supplies a boundary object:
`prefix` is strictly before the first true target reference and `suffix` is
strictly after the last true target reference. The aggregator consumes their
sorted unique-line files and weighted `*_all_line_refs.u64` pairs,
calling the accepted mapper to form boundary set-reference histograms. Strict
complete-instruction distance is derived from the scanner's first/last target
instruction ordinals; boundary instructions themselves are excluded.
Semantic-range start/end is taken from per-kernel `semantic_layer` plus
`semantic_identity=up_proj`; joined fixtures may instead provide
`semantic_range_start_kernel` and `semantic_range_end_kernel` in the boundary.
The result preserves both last-true-reference and semantic-range gap metrics.

Phase C/D "non-target" is layer-relative: for layer L it excludes only L's
qweight and therefore includes traffic to the other 27 target classes. The
strict last-L-reference to next-first-L-reference gap asserts that no L target
reference occurs in intervening full kernels, then uses `all_*` artifacts for
set pressure. `non_target_*` artifacts remain available only for the Phase B
all-28-targets-excluded summary. This distinction prevents systematic pressure
undercounting.

Phase A accepts either a precomputed static mapping JSON or the qualified
28-row sidecar via `--sidecar`; the latter enumerates aligned region lines and
calls the accepted mapper in bounded batches. The normalized mapping contains
geometry plus 28 regions with `layer_index`, `target_class`, and
`set_line_counts`. Dynamic unique lines are mapped either by a precomputed
TSV (`line_address`, `subpartition`, `set`) or by a mapper command with that
stdin/stdout protocol. No address mapping formula exists in this aggregator.

`--mapper-cmd` is fail-closed. Before mapping, the aggregator resolves its
first token to an executable, invokes that executable with `--provenance`, and
requires the accepted schema, source-direct Core mode, Core SHA, RTX4080 config
SHA, `MODELED_L2_GET_ADDR` namespace, and identity address transform. It hashes
the executable and records the complete provenance. `--line-mapping-tsv`
requires `--mapper-authority-json`; this explicit sidecar is recorded and
marked as not independently verifying a formal mapper execution.

Example:

```bash
python3 analyze_pressure.py \
  --summary-root TRACE_REFERENCE_SUMMARY_ROOT \
  --sidecar ORACLE_QWEIGHT_L2_SIDECAR.tsv \
  --mapper-cmd '/path/to/accepted_mapper map --no-header' \
  --workers 4 \
  --output-dir results
```

Precomputed TSV mode additionally requires
`--mapper-authority-json MAPPER_AUTHORITY.json`.

`--workers` defaults to 1. Values above 1 require Linux and use an explicit
`fork` process pool so workers inherit the already loaded kernel summaries,
static mapping, and mapper state copy-on-write. Each gap owns a distinct merge
temporary directory. The parent prints one `AGGREGATE_GAP_PASS` line per
completed layer/transition and sorts all results before writing, so worker
completion order cannot affect artifact bytes.

Outputs are `QWEIGHT_L2_SET_MAPPING.json`, `QUOTA_STATIC_MAPPING.json`,
`PER_LAYER_REUSE_DISTANCE_MATRIX.{json,tsv}`,
`SET_CONFLICT_PRESSURE_ANALYSIS.json`, `D1_D2_D2_D3_STABILITY.json`, and
`AGGREGATION_PROVENANCE.json`.

Quota output includes exact global and quotient/remainder per-subpartition
lines, an explicitly even-per-set reference distribution, per-layer target-set
population relative to that reference, and a set-local admission-pressure
proxy. Per-set even quota is an interpretation aid, not a modeled hardware
allocation rule. It reports both highest- and lowest-pressure layer/gap cases.
`global_quota_sufficient_but_set_local_unfavorable_proxy` is true only under
the documented conservative compound rule; it is not observed admission
denial, eviction, or timing behavior.

Static mapping output preserves input mapper/sidecar identity and region tensor
spans. Per-region and aggregate distributions explicitly report coefficient of
variation, max/mean, and zero-set fraction. Aggregation provenance hashes the
available summary index, static mapping, sidecar identity, mapper identity, and
line-mapping TSV.
Every region pair retains support intersection/Jaccard and also reports
`weighted_intersection_lines`, `weighted_overlap_over_region_lines`,
`equal_population_set_count`, and `nine_line_set_intersection`; this exposes
placement differences even when both regions touch every set.

All dynamic address metrics are `TRACE_ADDRESS_REFERENCE` or
`128B_LINE_REFERENCE_PROXY`; set-pressure is explicitly
`SET_CONFLICT_REFERENCE_PRESSURE_PROXY`. The tool does not claim actual L2
traffic, hits, misses, LRU eviction, or a performance ranking among budgets.
