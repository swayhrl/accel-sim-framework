# A10 Trace Mapping Schema

`scripts/accelsim/a10c_build_trace_mapping.py` maps A10B prior workload rows to available Accel-Sim trace files.

Mapping fields:

- `mapping_id`
- `paper`
- `prior_workload_id`
- `prior_original_name`
- `prior_normalized_name`
- `prior_source_path`
- `evidence_strength`
- `accel_trace_id`
- `accel_app_name`
- `accel_normalized_name`
- `kernelslist_path`
- `trace_root`
- `match_type`: `exact`, `alias`, `suite_alias`, `approximate`, or `none`.
- `mapping_status`: `TRACE_AVAILABLE`, `TRACE_MISSING`, `AMBIGUOUS_MULTIPLE_TRACES`, `LOW_EVIDENCE_PRIOR_WORKLOAD`, or `UNMAPPED`.
- `runnable`: `yes` or `no`.
- `config`: direct smoke config, currently `SM7_QV100`.
- `notes`

Only `TRACE_AVAILABLE` rows with `runnable=yes` are eligible for A10D.
