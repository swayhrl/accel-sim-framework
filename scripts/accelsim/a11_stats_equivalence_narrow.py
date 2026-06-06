#!/usr/bin/env python3
from __future__ import annotations

import csv
import os
import re
import subprocess
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True

from accelsim_stats_parser import clean_field, normalize_key, parse_selected_stats

REPO_ROOT = Path(__file__).resolve().parents[2]
os.chdir(REPO_ROOT)
Path(".local_reports").mkdir(exist_ok=True)
Path(".local_logs").mkdir(exist_ok=True)

TS = time.strftime("%Y%m%d_%H%M%S")
START = time.time()
START_ISO = time.strftime("%Y-%m-%dT%H:%M:%S%z")
LOG = Path(f".local_logs/A11_stats_equivalence_{TS}.log")
NORMALIZED = Path(f".local_reports/A11_normalized_stats_{TS}.csv")
MATRIX = Path(f".local_reports/A11_stats_equivalence_matrix_{TS}.csv")
REPORT = Path(f".local_reports/A11_stats_equivalence_{TS}.md")


def latest(pattern: str) -> Path | None:
    files = sorted(Path(".local_reports").glob(pattern), key=lambda p: p.stat().st_mtime)
    return files[-1] if files else None


def read_csv(path: Path | None) -> list[dict[str, str]]:
    if not path or not path.exists():
        return []
    with path.open(newline="") as f:
        return [{k: clean_field(v) for k, v in row.items()} for row in csv.DictReader(f)]


def log(message: str) -> None:
    print(message)
    with LOG.open("a") as f:
        f.write(message + "\n")


stats_inventory = Path(os.environ.get("ACCELSIM_A11_STATS_INVENTORY") or latest("A10B_prior_stats_field_inventory_*.csv") or "")
trace_mapping = Path(os.environ.get("ACCELSIM_A11_TRACE_MAPPING") or latest("A10C_trace_mapping_*.csv") or "")
smoke_csv = Path(os.environ.get("ACCELSIM_A11_ALIGNED_SMOKE_CSV") or latest("A10D_aligned_smoke_*.csv") or "")
workload_spec = os.environ.get("ACCELSIM_A11_WORKLOADS", "Mascar:hotspot,MeDiC:srad")
modes = ["first", "last", "aggregate_sum", "per_kernel"]

log("A11 stats equivalence narrow")
log(f"Start: {START_ISO}")
log(f"Stats inventory: {stats_inventory}")
log(f"Trace mapping: {trace_mapping}")
log(f"Aligned smoke CSV: {smoke_csv}")

status = "PASS"
blocker = "none"
limitations = ["per_kernel mode is best-effort unless explicit kernel boundaries are present in the log"]
smoke_rows = read_csv(smoke_csv)
prior_rows = read_csv(stats_inventory)
selected: list[dict[str, str]] = []
fallbacks: list[str] = []

for item in [x for x in workload_spec.split(",") if x.strip()]:
    paper, workload = item.split(":", 1)
    paper = paper.strip()
    workload = workload.strip()
    exact = [r for r in smoke_rows if r.get("paper") == paper and (r.get("normalized_workload") or r.get("normalized_name")) == workload and r.get("status") == "PASS"]
    if exact:
        selected.append(exact[0])
        continue
    replacement = [r for r in smoke_rows if r.get("paper") == paper and r.get("status") == "PASS"]
    if not replacement:
        replacement = [r for r in smoke_rows if r.get("status") == "PASS"]
    if replacement:
        selected.append(replacement[0])
        fallbacks.append(f"{paper}:{workload} -> {replacement[0].get('paper')}:{replacement[0].get('normalized_workload') or replacement[0].get('normalized_name')}")
    else:
        status = "BLOCKED_NO_ALIGNED_SMOKE"
        blocker = "no passing A10D aligned smoke rows available"

normalized_rows: list[dict[str, str]] = []
if status == "PASS":
    for run in selected:
        log_path = clean_field(run.get("log_path"))
        parsed = parse_selected_stats(log_path, modes)
        for idx, row in enumerate(parsed, 1):
            normalized_rows.append({
                "row_id": f"N{len(normalized_rows)+1:06d}",
                "paper": run.get("paper", ""),
                "workload": run.get("prior_name", ""),
                "normalized_workload": run.get("normalized_workload") or run.get("normalized_name", ""),
                "source": "A10D_aligned_smoke_log",
                "run_id": run.get("run_id", ""),
                "log_path": log_path,
                **row,
            })

with NORMALIZED.open("w", newline="") as f:
    fields = ["row_id","paper","workload","normalized_workload","source","run_id","log_path","stats_mode","stat_key","normalized_stat_key","stat_value","stat_unit","occurrence_count","selected_occurrence","kernel_hint","notes"]
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(normalized_rows)

accel_keys = {r["normalized_stat_key"]: r for r in normalized_rows if r["stats_mode"] == "last"}
preferred = [
    "gpgpu_n_tot_w_icount",
    "gpu_tot_sim_cycle",
    "gpu_tot_ipc",
    "gpgpu_simulation_time",
    "gpgpu_simulation_rate",
    "l2_total_cache_accesses",
    "l2_total_cache_misses",
]

interesting_prior = []
seen_prior = set()
for row in prior_rows:
    norm = normalize_key(row.get("normalized_field_name") or row.get("field_name"))
    if norm in preferred and norm not in seen_prior:
        interesting_prior.append(row)
        seen_prior.add(norm)
for row in prior_rows:
    norm = normalize_key(row.get("normalized_field_name") or row.get("field_name"))
    if not norm or norm in seen_prior:
        continue
    if any(token in norm for token in ["gpgpu", "gpu_tot", "ipc", "l2", "cache", "cycle", "instruction", "icount", "simulation"]):
        interesting_prior.append(row)
        seen_prior.add(norm)
    if len(interesting_prior) >= 80:
        break

matrix_rows: list[dict[str, str]] = []
for prior in interesting_prior:
    prior_norm = normalize_key(prior.get("normalized_field_name") or prior.get("field_name"))
    accel = accel_keys.get(prior_norm)
    if accel:
        if prior_norm in {"gpgpu_n_tot_w_icount", "gpu_tot_sim_cycle", "gpu_tot_ipc"}:
            eq, confidence = "exact", "high"
        elif "l2" in prior_norm or "cache" in prior_norm:
            eq, confidence = "approximate", "medium"
        elif "simulation_time" in prior_norm:
            eq, confidence = "not_comparable", "medium"
        else:
            eq, confidence = "exact", "medium"
        accel_field = accel["stat_key"]
        accel_norm = accel["normalized_stat_key"]
    else:
        eq, confidence = "accel_missing", "low"
        accel_field = ""
        accel_norm = ""
    matrix_rows.append({
        "matrix_id": f"E{len(matrix_rows)+1:05d}",
        "paper": prior.get("paper", "unknown"),
        "workload": "Mascar/hotspot;MeDiC/srad",
        "prior_field": prior.get("field_name", ""),
        "prior_normalized_field": prior_norm,
        "accel_field": accel_field,
        "accel_normalized_field": accel_norm,
        "equivalence_class": eq,
        "conversion_needed": "yes" if eq == "derived" else "no",
        "conversion_rule": "none" if eq != "derived" else "instructions/cycles",
        "stats_mode_required": "last",
        "confidence": confidence,
        "evidence_source": prior.get("source_path", ""),
        "notes": "narrow comparison-grade parser matrix",
    })

for key in preferred:
    if key in accel_keys and not any(r["prior_normalized_field"] == key for r in matrix_rows):
        matrix_rows.append({
            "matrix_id": f"E{len(matrix_rows)+1:05d}",
            "paper": "unknown",
            "workload": "Mascar/hotspot;MeDiC/srad",
            "prior_field": "",
            "prior_normalized_field": "",
            "accel_field": accel_keys[key]["stat_key"],
            "accel_normalized_field": key,
            "equivalence_class": "prior_missing",
            "conversion_needed": "no",
            "conversion_rule": "none",
            "stats_mode_required": "last",
            "confidence": "low",
            "evidence_source": str(smoke_csv),
            "notes": "available in Accel-Sim log but not observed in prior stats inventory sample",
        })

with MATRIX.open("w", newline="") as f:
    fields = ["matrix_id","paper","workload","prior_field","prior_normalized_field","accel_field","accel_normalized_field","equivalence_class","conversion_needed","conversion_rule","stats_mode_required","confidence","evidence_source","notes"]
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(matrix_rows)

counts = {}
for row in matrix_rows:
    counts[row["equivalence_class"]] = counts.get(row["equivalence_class"], 0) + 1

end_iso = time.strftime("%Y-%m-%dT%H:%M:%S%z")
wall = int(time.time() - START)
git_status = subprocess.getoutput("git status --short")
REPORT.write_text(f"""# A11 Stats Equivalence Narrow

- Status: {status}
- Start time: {START_ISO}
- End time: {end_iso}
- Wall clock seconds: {wall}
- Command: `python3 scripts/accelsim/a11_stats_equivalence_narrow.py`
- Log: `{LOG}`
- Input stats inventory: `{stats_inventory}`
- Input trace mapping: `{trace_mapping}`
- Input aligned smoke CSV: `{smoke_csv}`
- Normalized stats CSV: `{NORMALIZED}`
- Equivalence matrix CSV: `{MATRIX}`
- Blocker: {blocker}

## Selected Workloads

```
{os.linesep.join(f"{r.get('paper')} {r.get('normalized_workload') or r.get('normalized_name')} {r.get('log_path')}" for r in selected)}
```

## Parser Modes

- first
- last
- aggregate_sum
- per_kernel: PARTIAL, best-effort boundaries

## Counts

- Normalized stat rows: {len(normalized_rows)}
- Matrix rows: {len(matrix_rows)}
- Exact fields: {counts.get('exact', 0)}
- Derived fields: {counts.get('derived', 0)}
- Approximate fields: {counts.get('approximate', 0)}
- Missing fields: {counts.get('accel_missing', 0) + counts.get('prior_missing', 0)}

## Fallbacks

```
{os.linesep.join(fallbacks) if fallbacks else "none"}
```

## Limitations

{os.linesep.join(f"- {x}" for x in limitations)}

## Git Status

```
{git_status}
```
""")

if Path("0").is_file() and Path("0").stat().st_size <= 16 and subprocess.getoutput("git status --short -- 0").startswith("??"):
    Path("0").unlink()

log(f"A11 report: {REPORT}")
log(f"A11 normalized stats: {NORMALIZED}")
log(f"A11 equivalence matrix: {MATRIX}")
log(f"A11 status: {status}")
sys.exit(0 if status in {"PASS", "BLOCKED_NO_ALIGNED_SMOKE"} else 1)
