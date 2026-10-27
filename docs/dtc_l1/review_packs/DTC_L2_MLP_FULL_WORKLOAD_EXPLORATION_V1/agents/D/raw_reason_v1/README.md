# Closed-only L2 rejection-reason sidecar V1

This independent tool reads accepted **closed** logs once, preserves literal reason names, and uses only the last cumulative stats frame per CUDA stream. It never starts a model, mutates registry/controller state, changes frozen strict/consumer code, reclassifies acceptance, or overwrites a prior sidecar.

Before opening raw logs it verifies original source RESULT/proof, INTENT, natural zero-exit DONE == NATIVE_EXIT, raw SHA bindings, strict proof, qualification strict SHA, and canonical archive/native-restore receipt. The six P0 references trace to their original downstream18 cohort/UUID and archive targets, rather than pretending to be fresh L2 starts. Raw compressed and uncompressed SHA are then verified in streaming reads.

One-shot usage (choose a NEW output filename):

```sh
python3 .../agents/D/raw_reason_v1/raw_reason_sidecar.py \
  --output .../agents/D/raw_reason_v1/CLOSED_RAW_REASONS_<UTC>.json
```

Default roots are the separate L2 experiment, original downstream18 reference campaign, and the verified all-35 single-stream header evidence in `report_v1/input_stream_scope.json`. The parser stores line number, literal access/reason key, kernel UID, stream, final-frame provenance, source paths and all source SHA values. Unknown or unprinted reason fields remain None. A printed-reason sum matching an observed aggregate is reported explicitly; it does not fill absent reason fields with zero.

## Completed scan and qualification

The scan completed at 19:48:59 CST, with 129 accepted closed logs (123 new + six legal references), zero evidence errors, and 129/129 complete declared kernel/stream coverage. Thirty-six logs printed positive reason fields; all 36 sums matched observed aggregate reservation failures. Ninety-three logs printed no positive fields, which remain None. There are 911 source JSON metadata/SHA entries. This is a coherent per-file pass during a continuing campaign, not a cross-file transactional snapshot.

Parser: 38 CPU fixture checks; optional merger: 14 CPU fixture checks. Cases cover cumulative double-counting, multiple streams, repeated UID frames, None versus printed aggregate zero, ENRTY literal spelling, malformed/unbound lines, rejection before raw opens for unclosed sources, original reference ancestry, gzip/body SHA rejection, immutable UUID/result-SHA joins, and newer unscanned accepted cells. Zero simulator starts.

## Optional report overlay

```sh
python3 .../agents/D/raw_reason_v1/merge_reason_report.py \
  --sidecar .../agents/D/raw_reason_v1/CLOSED_RAW_REASONS_<UTC>.json \
  --output .../agents/D/raw_reason_v1/merged_report_<UTC> \
  --base-tool-commit <commit-of-report_v1-generator> \
  --tool-commit <commit-of-this-merger>
```

The merger imports the independent nonfrozen report generator, adds a separate reason panel and machine-readable evidence, and writes a new report directory. It does not edit that generator or the frozen result consumer. Base and merger commits/SHA are recorded in separate layers. A scanned endpoint must match cohort, UUID and immutable result SHA exactly. New accepted results beyond this sidecar are explicitly NOT_SCANNED/None.

The included 19:54:55 CST merged report joins all 129 sidecar cells, with zero identity/evidence/closure mismatches; four newer accepted cells are unscanned. `BASELINE_STRIDED3_COMPARISON.md/.json` uses the same 129 scan plus exact SHA-matched source RESULTS, with no raw rescan, to compare ATAX/MVT/BICG CH/DH P0 pressures. These retry-attempt intensities are not unique requests, queue latency or proof of a parameter speedup.

`SCAN_SUMMARY.json`, `LAST_SCAN.json`, `LAST_MERGE.json` and `REVIEW_MANIFEST.json` provide canonical artifacts and hashes. Dependency directories and raw log bodies are not included. The old V2 prototype remains unchanged in `current_results_analysis_v1/raw_reason_sidecar.py`; this qualified version is independent.

## Published snapshot reuse

`join_sidecar(report_dict, sidecar_dict)` is a pure derived-data join, so a caller may load the already published base snapshot JSON (for example A/derived_reports/checkpoint_02) and apply the sidecar without native acquisition or any raw reread. The CLI base acquisition reads only closed RESULT JSON and live PID metadata, never raw logs. Base generator commit and merger commit stay separate. The merger source listed in DELIVERY_MANIFEST is final for publication; subsequent changes require a new source revision and qualification.
