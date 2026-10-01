#!/usr/bin/env python3
"""CPU-only preservation of interrupted formal samples; never a performance verdict."""

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path("/data/c16/awma/r20r5_hybrid_native_20261002")
RAW = ROOT / "raw"
stdout = (RAW / "DISCOVERY_TIMING.stdout.log").read_text(errors="replace")
stderr = (RAW / "DISCOVERY_TIMING.stderr.log").read_text(errors="replace")
rows = []
for line in stdout.splitlines():
    try:
        record = json.loads(line)
    except json.JSONDecodeError:
        continue
    if all(key in record for key in ("group", "step", "arm", "phase", "repeat", "wall_ms", "event_ms", "semantic")):
        rows.append(record)
if "Formal sample semantic gate failed" not in stderr or "'niter_exact': False" not in stderr:
    raise RuntimeError("Expected exact-niter hard-gate failure not present")
if not rows or any(x["semantic"] is False for x in rows):
    raise RuntimeError("Unexpected recorded sample sequence")
with (RAW / "DISCOVERY_TIMING_PARTIAL_SAMPLES.tsv").open("w", newline="") as stream:
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
counts = Counter(x["phase"] for x in rows)
result = {
    "stage": "AWMA_R20R5_HYBRID_ACTIVE_WORLD_NATIVE_109_V1",
    "classification": "R20_ACTIVE_WORLD_LINE_CLOSED_HYBRID_NUMERICS_NOT_QUALIFIED",
    "completed_sample_rows_before_stop": len(rows),
    "completed_warmup_rows": counts["WARMUP"],
    "completed_formal_rows": counts["FORMAL"],
    "failed_sample": {"group": 2, "step": 136, "arm": "B0", "phase": "FORMAL", "repeat": 0,
                      "nefc_exact": True, "niter_exact": False, "source_stop_fail_count": 0,
                      "wall_ms": 0.726818, "cuda_event_ms": 0.719871997833252},
    "failed_output_payload_saved": False,
    "failure_authority": "DISCOVERY_TIMING.stderr.log exact exception row; preceding complete rows in stdout/partial TSV",
    "full_120_formal_protocol_completed": False,
    "performance_decision_permitted": False,
    "holdout_opened": False,
    "GPU_rerun_after_hard_gate": False,
}
(RAW / "FORMAL_SEMANTIC_STOP.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
print(json.dumps(result, sort_keys=True))
