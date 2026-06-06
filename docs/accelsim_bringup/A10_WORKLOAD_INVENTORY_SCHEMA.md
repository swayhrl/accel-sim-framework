# A10 Workload Inventory Schema

`scripts/accelsim/a10b_extract_prior_inventory.py` reads the A10A artifact inventory and emits two CSV files.

Workload inventory fields:

- `workload_id`: stable row id.
- `paper`: `Mascar`, `MeDiC`, `both`, or `unknown`.
- `source_path`, `source_line`, `source_type`: evidence location.
- `original_name`: text found in the artifact.
- `normalized_name`: normalized benchmark key such as `backprop`, `bfs`, or `srad`.
- `suite_hint`, `config_hint`, `run_mode_hint`, `args_hint`: best-effort context.
- `evidence_strength`: `high`, `medium`, or `low`.
- `notes`: extraction notes.

High evidence is limited to workload names found in scripts, stats CSVs, configs, or logs with run/config/stat context. Prose-only mentions are medium or low and are not selected by default for A10D.

Stats field inventory fields:

- `field_id`, `paper`, `source_path`
- `field_name`, `normalized_field_name`
- `field_type`
- `likely_meaning`
- `used_by_script`
- `notes`
