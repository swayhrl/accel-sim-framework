"""Derive shN V1 source-level work bounds from its fixed Git evidence only."""
import csv
import io
import json
import math
import subprocess

COMMIT = "2838e93cfc129183d7d727e80eccc1b2f577a82d"
BASE = "docs/ai_workload_research/runs/AI_ARCH_Q1_SHN_GPU_RESIDENCY_NATIVE_V1/"
CHUNK = 32768
WIDTH = 45
STEPS = 51


def fixed_text(name):
    return subprocess.check_output(["git", "show", f"{COMMIT}:{BASE}{name}"], text=True)


rows = list(csv.DictReader(io.StringIO(fixed_text("FORMAL_SAMPLES.tsv")), delimiter="\t"))
assert len(rows) == 20
out = []
for row in rows:
    if row["policy"] != "ON":
        continue
    updated = int(row["update_sum"])
    visible = int(row["visible_sum"])
    # Sum of per-step ceil(n/CHUNK); only window totals are published.
    low = math.ceil(updated / CHUNK) + math.ceil(visible / CHUNK)
    high = low + 2 * (STEPS - 1)
    out.append({
        "job": row["job"], "phase": row["phase"],
        "updated_rows": updated, "visible_rows": visible,
        "row_visits": updated + visible,
        "chunk_iterations_bound": [low, high],
        "id_age_H2D_operand_bytes": 16 * (updated + visible),
        "four_state_gather_operand_bytes": 4 * WIDTH * 4 * (updated + visible),
        "three_table_gather_operand_bytes": 3 * 4 * (updated + visible),
        "coefficient_table_creation_calls": 6 * STEPS,
        "coefficient_table_payload_bytes": 6 * 16 * 4 * STEPS,
        "prediction_cat_output_bytes": visible * WIDTH * 4,
    })
assert len(out) == 10
print(json.dumps({"source_commit": COMMIT, "basis": "source-level operands and bounds; not measured traffic, kernels or time",
                  "chunk_rows": CHUNK, "shn_width": WIDTH, "steps_per_sample": STEPS, "on_formal_samples": out}, indent=2))
