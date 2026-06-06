#!/usr/bin/env python3
from __future__ import annotations

import csv
import os
import subprocess
import sys
import time
from pathlib import Path

from accelsim_stats_parser import clean_field

REPO_ROOT = Path(__file__).resolve().parents[2]
os.chdir(REPO_ROOT)
Path(".local_reports").mkdir(exist_ok=True)
Path(".local_logs").mkdir(exist_ok=True)

TS = time.strftime("%Y%m%d_%H%M%S")
START = time.time()
START_ISO = time.strftime("%Y-%m-%dT%H:%M:%S%z")
LOG = Path(f".local_logs/A12_workload_config_lock_{TS}.log")
LOCK = Path(f".local_reports/A12_workload_config_lock_{TS}.csv")
REPORT = Path(f".local_reports/A12_workload_config_lock_summary_{TS}.md")


def latest(pattern: str) -> Path | None:
    files = sorted(Path(".local_reports").glob(pattern), key=lambda p: p.stat().st_mtime)
    return files[-1] if files else None


def read_csv(path: Path | None) -> list[dict[str, str]]:
    if not path or not path.exists():
        return []
    with path.open(newline="") as f:
        return [{k: clean_field(v) for k, v in row.items()} for row in csv.DictReader(f)]


def priority_value(value: str) -> int:
    return {"high": 3, "medium": 2, "low": 1}.get(value, 0)


workload_path = Path(os.environ.get("ACCELSIM_A12_WORKLOAD_INVENTORY") or latest("A10B_prior_workload_inventory_*.csv") or "")
mapping_path = Path(os.environ.get("ACCELSIM_A12_TRACE_MAPPING") or latest("A10C_trace_mapping_*.csv") or "")
equiv_path = Path(os.environ.get("ACCELSIM_A12_EQUIVALENCE_MATRIX") or latest("A11_stats_equivalence_matrix_*.csv") or "")
workloads = read_csv(workload_path)
mappings = read_csv(mapping_path)
equivs = read_csv(equiv_path)

with LOG.open("w") as f:
    f.write(f"A12 workload config lockdown\nStart: {START_ISO}\n")
    f.write(f"Workload inventory: {workload_path}\nMapping: {mapping_path}\nEquivalence: {equiv_path}\n")

by_id = {w.get("workload_id"): w for w in workloads}
exact_fields = sum(1 for e in equivs if e.get("equivalence_class") == "exact")
partial_fields = sum(1 for e in equivs if e.get("equivalence_class") in {"approximate", "derived"})

groups: dict[tuple[str, ...], dict[str, object]] = {}
for m in mappings:
    wid = m.get("prior_workload_id")
    w = by_id.get(wid, {})
    paper = m.get("paper") or w.get("paper") or "unknown"
    norm = m.get("prior_normalized_name") or w.get("normalized_name")
    key = (
        paper,
        norm,
        w.get("suite_hint", ""),
        w.get("config_hint", ""),
        w.get("args_hint", "")[:120],
        m.get("kernelslist_path", ""),
    )
    entry = groups.setdefault(key, {
        "paper": paper,
        "workload": m.get("prior_original_name") or w.get("original_name") or norm,
        "normalized_workload": norm,
        "suite": w.get("suite_hint", ""),
        "prior_config_hint": w.get("config_hint", ""),
        "prior_args_hint": w.get("args_hint", "")[:180],
        "prior_run_mode_hint": w.get("run_mode_hint", ""),
        "evidence_strength": "low",
        "evidence_count": 0,
        "evidence_sources": [],
        "accel_trace_id": m.get("accel_trace_id", ""),
        "accel_app_name": m.get("accel_app_name", ""),
        "kernelslist_path": m.get("kernelslist_path", ""),
        "trace_root": m.get("trace_root", ""),
        "mapping_status": m.get("mapping_status", ""),
        "match_type": m.get("match_type", ""),
        "runnable": m.get("runnable", "no"),
    })
    entry["evidence_count"] = int(entry["evidence_count"]) + 1
    sources = entry["evidence_sources"]
    assert isinstance(sources, list)
    source = w.get("source_path") or m.get("prior_source_path")
    if source and source not in sources:
        sources.append(source)
    if priority_value(w.get("evidence_strength", "")) > priority_value(str(entry["evidence_strength"])):
        entry["evidence_strength"] = w.get("evidence_strength", "")
        entry["workload"] = w.get("original_name") or entry["workload"]
        entry["prior_args_hint"] = w.get("args_hint", "")[:180]
        entry["prior_run_mode_hint"] = w.get("run_mode_hint", "")

rows = []
for entry in groups.values():
    runnable = entry["runnable"] == "yes" and entry["mapping_status"] == "TRACE_AVAILABLE"
    norm = str(entry["normalized_workload"])
    paper = str(entry["paper"])
    is_p0 = (paper == "Mascar" and norm == "hotspot") or (paper == "MeDiC" and norm == "srad")
    stats_readiness = "exact_fields_available" if exact_fields else ("partial_fields_available" if partial_fields else "smoke_only")
    config_equivalence = "approximate_qv100_sass" if runnable else "prior_config_unknown"
    priority = "P0" if is_p0 and runnable else ("P1" if runnable and entry["evidence_strength"] == "high" else ("P2" if runnable else "P3"))
    rows.append({
        "lock_id": "",
        "paper": paper,
        "workload": entry["workload"],
        "normalized_workload": norm,
        "suite": entry["suite"] or ("rodinia" if entry["kernelslist_path"] and "rodinia" in str(entry["kernelslist_path"]).lower() else ""),
        "prior_config_hint": entry["prior_config_hint"],
        "prior_args_hint": entry["prior_args_hint"],
        "prior_run_mode_hint": entry["prior_run_mode_hint"],
        "evidence_strength": entry["evidence_strength"],
        "evidence_count": entry["evidence_count"],
        "evidence_sources": ";".join(entry["evidence_sources"][:20]),
        "accel_trace_id": entry["accel_trace_id"],
        "accel_app_name": entry["accel_app_name"],
        "kernelslist_path": entry["kernelslist_path"],
        "trace_root": entry["trace_root"],
        "accel_config_name": "SM7_QV100",
        "gpgpusim_config_path": "gpu-simulator/gpgpu-sim/configs/tested-cfgs/SM7_QV100/gpgpusim.config",
        "accelsim_trace_config_path": "gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config",
        "mapping_status": entry["mapping_status"],
        "match_type": entry["match_type"],
        "runnable": "yes" if runnable else "no",
        "stats_readiness": stats_readiness,
        "config_equivalence": config_equivalence,
        "include_smoke": "yes" if priority == "P0" else "no",
        "include_pilot": "yes" if priority in {"P0", "P1"} else "no",
        "include_paper_candidate": "yes" if runnable and entry["evidence_strength"] == "high" else "no",
        "priority": priority,
        "notes": "deduplicated from A10 row-level evidence",
    })

rows.sort(key=lambda r: ({"P0": 0, "P1": 1, "P2": 2, "P3": 3}[r["priority"]], r["paper"], r["normalized_workload"], r["kernelslist_path"]))
for idx, row in enumerate(rows, 1):
    row["lock_id"] = f"L{idx:05d}"

with LOCK.open("w", newline="") as f:
    fields = ["lock_id","paper","workload","normalized_workload","suite","prior_config_hint","prior_args_hint","prior_run_mode_hint","evidence_strength","evidence_count","evidence_sources","accel_trace_id","accel_app_name","kernelslist_path","trace_root","accel_config_name","gpgpusim_config_path","accelsim_trace_config_path","mapping_status","match_type","runnable","stats_readiness","config_equivalence","include_smoke","include_pilot","include_paper_candidate","priority","notes"]
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)

status = "PASS" if rows else "BLOCKED_NO_LOCK_ROWS"
blocker = "none" if rows else "no mapping rows available"
end_iso = time.strftime("%Y-%m-%dT%H:%M:%S%z")
wall = int(time.time() - START)
p0 = [r for r in rows if r["priority"] == "P0"]
trace_missing = sum(1 for r in rows if r["mapping_status"] == "TRACE_MISSING")
config_unknown = sum(1 for r in rows if r["config_equivalence"] == "prior_config_unknown")
git_status = subprocess.getoutput("git status --short")
REPORT.write_text(f"""# A12 Workload Config Lockdown

- Status: {status}
- Start time: {START_ISO}
- End time: {end_iso}
- Wall clock seconds: {wall}
- Command: `python3 scripts/accelsim/a12_workload_config_lockdown.py`
- Log: `{LOG}`
- Workload inventory: `{workload_path}`
- Trace mapping: `{mapping_path}`
- Equivalence matrix: `{equiv_path}`
- Lockfile CSV: `{LOCK}`
- Blocker: {blocker}

## Counts

- Row-level workload count: {len(workloads)}
- Mapping rows: {len(mappings)}
- Unique lockfile rows: {len(rows)}
- P0 rows: {len(p0)}
- Trace-missing rows: {trace_missing}
- Config-unknown rows: {config_unknown}

## P0 Rows

```
{os.linesep.join(f"{r['lock_id']} {r['paper']} {r['normalized_workload']} {r['kernelslist_path']}" for r in p0)}
```

## Limitations

- Config equivalence is conservative and defaults to approximate QV100 SASS for runnable traces.
- The lockfile does not prove paper mechanism equivalence.

## Git Status

```
{git_status}
```
""")

print(f"A12 report: {REPORT}")
print(f"A12 lockfile: {LOCK}")
print(f"A12 status: {status}")
sys.exit(0 if status in {"PASS", "BLOCKED_NO_LOCK_ROWS"} else 1)
