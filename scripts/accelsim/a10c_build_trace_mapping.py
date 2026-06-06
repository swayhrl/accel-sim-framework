#!/usr/bin/env python3
import csv
import os
import re
import time
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
os.chdir(REPO_ROOT)
Path(".local_reports").mkdir(exist_ok=True)
Path(".local_logs").mkdir(exist_ok=True)

ts = time.strftime("%Y%m%d_%H%M%S")
start = time.time()
start_iso = time.strftime("%Y-%m-%dT%H:%M:%S%z")
log_path = Path(f".local_logs/A10C_trace_mapping_{ts}.log")
mapping_path = Path(f".local_reports/A10C_trace_mapping_{ts}.csv")
summary_path = Path(f".local_reports/A10C_mapping_summary_{ts}.md")

def clean(s):
    return str(s or "").replace("\r", "").replace("\n", "").strip()

def latest(pattern):
    files = sorted(Path(".local_reports").glob(pattern), key=lambda p: p.stat().st_mtime)
    return files[-1] if files else None

aliases = {
    "bp": "backprop", "backprop": "backprop", "bfs": "bfs", "hotspot": "hotspot",
    "lud": "lud", "nw": "nw", "needle": "nw", "needleman": "nw",
    "srad": "srad", "srad_v2": "srad", "pathfinder": "pathfinder",
    "streamcluster": "streamcluster", "gaussian": "gaussian", "lavamd": "lavamd",
    "lava_md": "lavamd", "lavamd": "lavamd", "kmeans": "kmeans",
    "mri_q": "mriq", "mriq": "mriq", "stencil": "stencil", "nn": "nn",
    "heartwall": "heartwall",
}

def normalize(text):
    s = clean(text).lower()
    s = re.sub(r"[^a-z0-9]+", "_", s).strip("_")
    parts = [p for p in s.split("_") if p]
    joined = "_".join(parts)
    for key, val in aliases.items():
        if key in parts or key in joined:
            return val
    return joined

def trace_info(kernelslist):
    p = Path(clean(kernelslist))
    trace_dir = p.parent
    args_dir = trace_dir.parent
    app_dir = args_dir.parent
    app_name = clean(app_dir.name)
    root = app_dir.parent
    low = str(p).lower()
    suite = "rodinia" if "rodinia" in low else ("parboil" if "parboil" in low else ("polybench" if "polybench" in low else ""))
    cuda = ""
    m = re.search(r"/(\d+\.\d+)/", str(p))
    if m:
        cuda = m.group(1)
    return {
        "trace_id": re.sub(r"[^A-Za-z0-9_.-]", "_", app_name)[:80],
        "trace_root": str(root),
        "kernelslist_path": str(p),
        "app_name": app_name,
        "normalized_name": normalize(app_name),
        "suite_hint": suite,
        "cuda_version_hint": cuda,
        "device_hint": "unknown",
        "arg_hint": clean(args_dir.name),
    }

workload_input = Path(os.environ.get("ACCELSIM_A10B_WORKLOAD_INVENTORY") or latest("A10B_prior_workload_inventory_*.csv") or "")
stats_input = Path(os.environ.get("ACCELSIM_A10B_STATS_INVENTORY") or latest("A10B_prior_stats_field_inventory_*.csv") or "")
trace_root_env = clean(os.environ.get("ACCELSIM_TRACE_ROOT"))

with log_path.open("w") as log:
    log.write(f"A10C trace mapping\nStart: {start_iso}\n")
    log.write(f"Workload inventory: {workload_input}\nStats inventory: {stats_input}\n")

workloads = []
if workload_input.exists():
    with workload_input.open(newline="") as f:
        workloads = list(csv.DictReader(f))

trace_candidates = []
roots = []
if trace_root_env:
    roots.append(Path(trace_root_env))
roots.extend([Path(".local_traces"), Path("hw_run")])
if not trace_root_env:
    roots.append(Path("."))
seen = set()
for root in roots:
    if not root.exists():
        continue
    for k in root.rglob("kernelslist.g"):
        if any(part in {".git", "build", ".local_runs"} for part in k.parts):
            continue
        sp = str(k)
        if sp in seen:
            continue
        seen.add(sp)
        trace_candidates.append(trace_info(k))

by_norm = defaultdict(list)
for t in trace_candidates:
    by_norm[t["normalized_name"]].append(t)

rows = []
for w in workloads:
    prior_norm = normalize(w.get("normalized_name") or w.get("original_name"))
    evidence = clean(w.get("evidence_strength"))
    matches = by_norm.get(prior_norm, [])
    if evidence == "low":
        status = "LOW_EVIDENCE_PRIOR_WORKLOAD"
        match_type = "none"
        runnable = "no"
        chosen = {}
    elif len(matches) == 1:
        status = "TRACE_AVAILABLE"
        match_type = "exact" if prior_norm == matches[0]["normalized_name"] else "alias"
        runnable = "yes"
        chosen = matches[0]
    elif len(matches) > 1:
        status = "AMBIGUOUS_MULTIPLE_TRACES"
        match_type = "exact"
        runnable = "no"
        chosen = matches[0]
    else:
        status = "TRACE_MISSING"
        match_type = "none"
        runnable = "no"
        chosen = {}
    rows.append({
        "mapping_id": f"M{len(rows)+1:05d}",
        "paper": clean(w.get("paper")),
        "prior_workload_id": clean(w.get("workload_id")),
        "prior_original_name": clean(w.get("original_name")),
        "prior_normalized_name": prior_norm,
        "prior_source_path": clean(w.get("source_path")),
        "evidence_strength": evidence,
        "accel_trace_id": clean(chosen.get("trace_id")),
        "accel_app_name": clean(chosen.get("app_name")),
        "accel_normalized_name": clean(chosen.get("normalized_name")),
        "kernelslist_path": clean(chosen.get("kernelslist_path")),
        "trace_root": clean(chosen.get("trace_root")),
        "match_type": match_type,
        "mapping_status": status,
        "runnable": runnable,
        "config": "SM7_QV100",
        "notes": "mapped from real prior workload row" if runnable == "yes" else "not runnable in current trace inventory",
    })

with mapping_path.open("w", newline="") as f:
    fields = ["mapping_id","paper","prior_workload_id","prior_original_name","prior_normalized_name","prior_source_path","evidence_strength","accel_trace_id","accel_app_name","accel_normalized_name","kernelslist_path","trace_root","match_type","mapping_status","runnable","config","notes"]
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)

exact = sum(1 for r in rows if r["match_type"] == "exact" and r["mapping_status"] == "TRACE_AVAILABLE")
alias = sum(1 for r in rows if r["match_type"] == "alias" and r["mapping_status"] == "TRACE_AVAILABLE")
missing = sum(1 for r in rows if r["mapping_status"] == "TRACE_MISSING")
runnable = [r for r in rows if r["runnable"] == "yes"]
status = "PASS" if rows else "BLOCKED_NO_PRIOR_WORKLOADS"
blocker = "none" if rows else "missing prior workload rows"
end_iso = time.strftime("%Y-%m-%dT%H:%M:%S%z")
wall = int(time.time() - start)

summary_path.write_text(f"""# A10C Trace Mapping

- Status: {status}
- Start time: {start_iso}
- End time: {end_iso}
- Wall clock seconds: {wall}
- Command: `python3 scripts/accelsim/a10c_build_trace_mapping.py`
- Log: `{log_path}`
- Prior workload inventory: `{workload_input}`
- Prior stats inventory: `{stats_input}`
- Mapping CSV: `{mapping_path}`
- Blocker: {blocker}

## Counts

- Trace candidates: {len(trace_candidates)}
- Mapping rows: {len(rows)}
- Exact mapped rows: {exact}
- Alias mapped rows: {alias}
- Missing rows: {missing}
- Runnable rows: {len(runnable)}

## Recommended A10D Set

```
{os.linesep.join(f"{r['paper']} {r['prior_normalized_name']} {r['kernelslist_path']}" for r in runnable[:10])}
```

## Git Status

```
{os.popen('git status --short').read()}
```
""")

print(f"A10C summary: {summary_path}")
print(f"A10C mapping: {mapping_path}")
print(f"A10C status: {status}")
raise SystemExit(0 if status in {"PASS", "BLOCKED_NO_PRIOR_WORKLOADS"} else 1)
