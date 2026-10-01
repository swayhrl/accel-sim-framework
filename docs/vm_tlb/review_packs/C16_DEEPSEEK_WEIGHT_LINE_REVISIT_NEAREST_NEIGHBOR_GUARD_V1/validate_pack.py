#!/usr/bin/env python3
"""Read-only deterministic document and schema validation; no experiments."""
import csv
import json
from pathlib import Path

p = Path(__file__).resolve().parent
required = [
    "GEMV_WEIGHT_REVISIT_NEIGHBORS.md",
    "CAPABILITY_MATRIX.tsv",
    "NOVELTY_BOUNDARY.md",
    "FINAL_DECISION.json",
]
assert all((p / x).is_file() and (p / x).stat().st_size > 0 for x in required)
with (p / "CAPABILITY_MATRIX.tsv").open(encoding="utf-8", newline="") as f:
    rows = list(csv.DictReader(f, delimiter="\t"))
assert len(rows) >= 8 and all(None not in r for r in rows)
assert len({r["source_id"] for r in rows}) == len(rows)
assert all(r["primary_source"].startswith("https://") for r in rows)
assert {"CUBLAS_GEMV", "CUTLASS_GEMV", "AWQ_GEMV", "MARLIN", "QUICK", "FLUTE", "GEMLITE", "VLLM_MARLIN_MOE"}.issubset({r["source_id"] for r in rows})
d = json.loads((p / "FINAL_DECISION.json").read_text(encoding="utf-8"))
assert d["classification"] in {"NEAREST_NEIGHBOR_CROWDED", "RESIDUAL_CAPABILITY_GAP_POSSIBLE", "INSUFFICIENT_LITERATURE_EVIDENCE"}
assert d["classification"] == "NEAREST_NEIGHBOR_CROWDED"
assert set(d["address_classification"]) == {"same_line_different_sector", "same_sector_duplicate", "same_byte_duplicate"}
assert all(not d[k] for k in ("author_artifacts_run", "gpu_used", "ncu_used", "nvbit_used", "sass_used", "simulator_used", "new_trace_created", "new_mechanism_implemented", "experiment_authorized", "lr12_project_decision_changed"))
print(f"PASS capability_rows={len(rows)} classification={d['classification']} CPU_literature_only=true")
