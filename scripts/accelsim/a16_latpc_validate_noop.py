#!/usr/bin/env python3
from __future__ import annotations

import csv
import math
import subprocess
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True

from a16_latpc_variant_lib import latest

REPO_ROOT = Path(__file__).resolve().parents[2]
Path(REPO_ROOT / ".local_reports").mkdir(exist_ok=True)
Path(REPO_ROOT / ".local_logs").mkdir(exist_ok=True)

TS = time.strftime("%Y%m%d_%H%M%S")
START = time.time()
START_ISO = time.strftime("%Y-%m-%dT%H:%M:%S%z")
RESULTS_COPY = REPO_ROOT / f".local_reports/A16D_latpc_baseline_vs_noop_results_{TS}.csv"
COMPARE = REPO_ROOT / f".local_reports/A16D_latpc_baseline_vs_noop_compare_{TS}.csv"
SUMMARY = REPO_ROOT / f".local_reports/A16D_latpc_validation_summary_{TS}.md"
LOG = REPO_ROOT / f".local_logs/A16D_latpc_validate_noop_{TS}.log"


def read_csv(path: Path | None) -> list[dict[str, str]]:
    if not path:
        return []
    with path.open(newline="") as f:
        return [{k: (v or "").strip() for k, v in row.items()} for row in csv.DictReader(f)]


def as_float(value: str) -> float | None:
    try:
        if value in {"", "NA"}:
            return None
        return float(value)
    except ValueError:
        return None


with LOG.open("w") as f:
    f.write(f"A16D LATPC noop validation\nStart: {START_ISO}\n")

results_path = latest("A16C_latpc_experiment_results_*.csv")
rows = read_csv(results_path)
status = "PASS"
blocker = "none"
baseline = next((r for r in rows if r.get("variant_id") == "baseline"), None)
noop = next((r for r in rows if r.get("variant_id") == "latpc_noop"), None)
compare_rows = []
if not baseline or not noop:
    status = "FAIL_NO_RESULTS"
    blocker = "missing baseline or latpc_noop row"
elif baseline.get("status") != "PASS" or noop.get("status") != "PASS":
    status = "FAIL_NO_RESULTS"
    blocker = f"baseline/noop did not both pass: {baseline.get('status')}/{noop.get('status')}"
else:
    fields = [
        ("cycles", "exact", 0.0, 0.0),
        ("instructions", "exact", 0.0, 0.0),
        ("ipc", "exact", 1e-9, 1e-6),
        ("l2_accesses", "approximate", 0.0, 0.0),
        ("l2_misses", "approximate", 0.0, 0.0),
    ]
    for field, klass, tol_abs, tol_rel in fields:
        b = as_float(baseline.get(field, ""))
        n = as_float(noop.get(field, ""))
        row_status = "PASS"
        notes = "no-op equivalence"
        if b is None or n is None:
            row_status = "MISSING"
            abs_diff = rel_diff = "NA"
        else:
            diff = abs(b - n)
            rel = diff / abs(b) if b else diff
            abs_diff = f"{diff:.12g}"
            rel_diff = f"{rel:.12g}"
            if diff > tol_abs and rel > tol_rel:
                row_status = "FAIL"
                notes = "difference exceeds tolerance"
                status = "FAIL_NOOP_MISMATCH"
        compare_rows.append({
            "paper": "LATPC",
            "workload": baseline.get("workload", ""),
            "field": field,
            "field_class": klass,
            "baseline_value": baseline.get(field, ""),
            "latpc_noop_value": noop.get(field, ""),
            "abs_diff": abs_diff,
            "rel_diff": rel_diff,
            "tolerance_abs": str(tol_abs),
            "tolerance_rel": str(tol_rel),
            "status": row_status,
            "notes": notes,
        })
    meaningful = [r for r in compare_rows if r["status"] == "PASS"]
    missing = [r for r in compare_rows if r["status"] == "MISSING"]
    if status == "PASS" and missing and meaningful:
        status = "PASS_WITH_WARNINGS"
    elif status == "PASS" and not meaningful:
        status = "FAIL_NO_RESULTS"
        blocker = "no comparable numeric fields"

with RESULTS_COPY.open("w", newline="") as f:
    if rows:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
with COMPARE.open("w", newline="") as f:
    fields = ["paper","workload","field","field_class","baseline_value","latpc_noop_value","abs_diff","rel_diff","tolerance_abs","tolerance_rel","status","notes"]
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(compare_rows)

passes = sum(1 for r in compare_rows if r["status"] == "PASS")
fails = sum(1 for r in compare_rows if r["status"] == "FAIL")
missing = sum(1 for r in compare_rows if r["status"] == "MISSING")
end_iso = time.strftime("%Y-%m-%dT%H:%M:%S%z")
wall = int(time.time() - START)
SUMMARY.write_text(f"""# A16D LATPC Baseline vs No-op Validation

- Status: {status}
- Start time: {START_ISO}
- End time: {end_iso}
- Wall clock seconds: {wall}
- Command: `python3 scripts/accelsim/a16_latpc_validate_noop.py`
- Log: `{LOG.relative_to(REPO_ROOT)}`
- Input result CSV: `{results_path or ''}`
- Results copy CSV: `{RESULTS_COPY.relative_to(REPO_ROOT)}`
- Compare CSV: `{COMPARE.relative_to(REPO_ROOT)}`
- Blocker: {blocker}

## Counts

- Fields compared: {len(compare_rows)}
- Pass: {passes}
- Fail: {fails}
- Missing: {missing}

## Scope

`latpc_noop` validates infrastructure only. It is not a LATPC mechanism implementation.

## Git Status

```
{subprocess.getoutput('git status --short')}
```
""")

print(f"A16D summary: {SUMMARY.relative_to(REPO_ROOT)}")
print(f"A16D results: {RESULTS_COPY.relative_to(REPO_ROOT)}")
print(f"A16D compare: {COMPARE.relative_to(REPO_ROOT)}")
print(f"A16D status: {status}")
sys.exit(0 if status in {"PASS", "PASS_WITH_WARNINGS"} else 1)
