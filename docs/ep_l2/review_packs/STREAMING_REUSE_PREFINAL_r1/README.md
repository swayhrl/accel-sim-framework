# Streaming-Reuse Characterization — Prefinal r1

Status: `STREAMING_REUSE_PREFINAL_REVIEW_READY`  
Scientific final PASS: **not asserted**.  
Dataset state: **incomplete**.  The original `scan` row is actively executing and is marked `RUNNING_PENDING_FINAL_DELTA`; it is absent from every aggregate and figure in this pack.  No denominator was recomputed to conceal that absence.

This is an immediate, immutable review checkpoint from the frozen sector-aware candidate. It contains the nine completed original Motivation workloads and three selected additional workloads (12 completed rows total). The intended final population is the original 10 plus the three additions (13 rows); `scan` remains the sole pending original row.

## Frozen identities

| Role | SHA |
| --- | --- |
| Core reviewed parent | `2a6a31591bc42023e5997cca969e4b672efe0405` |
| Framework reviewed parent | `02f36816f60afcff55e910cdef2b60937e691cdc` |
| Core runtime candidate | `ca3e7bc0b8f61b5d7c052bcda2a91955a1e5c919` |
| Framework runtime candidate (all accepted runs) | `db1c90182fad02aacbd282b67ecdc57b8e4cc365` |
| Framework publication/checkpoint source | `0df22990c2a40c25a3d5bb5c3bd73d1c36b6d8eb` |

The Core candidate is a descendant of the reviewed Core parent. `db1c…` is deliberately retained as the runtime provenance because the later Framework commit contains aggregation/figure tooling only.

## Included artifacts

- `sector_reuse_summary.csv`, `sector_reuse_coverage.csv`, `sector_reuse_distance.csv`: completed-row sector telemetry.
- `line_vs_sector_reuse.csv`: direct line-reuse versus exact-sector-reuse comparison.
- `figures/FIG1V2_L2_SECTOR_TEMPORAL_REUSE.{png,svg}` and `figures/FIG1S_LINE_VS_SECTOR_REUSE.{png,svg}`: prefinal figures from completed rows only; their captions/interpretation must retain this qualifier.
- `SCREENING_CANDIDATES.csv`: all ten screened candidates, including the failed and resource-closeout records.
- `FORMAL_WORKLOAD_SELECTION.md` and `formal_workload_status.csv`: quantified selection and explicit pending slot.
- `SOURCE_MAP.md`, `FIELD_SEMANTICS.md`, `VALIDATION_SUMMARY.md`, and `PRESERVATION_MANIFEST.md`: implementation, contract, gates, and immutable-evidence proof.

Raw results are intentionally retained outside this Git review pack at `/workspace/results/ep_l2_streaming_reuse/`; `raw_log_index.tsv` points to them. Historical Motivation evidence was neither modified nor regenerated.

