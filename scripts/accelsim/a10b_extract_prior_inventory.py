#!/usr/bin/env python3
import csv
import os
import re
import sys
import time
from collections import OrderedDict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
os.chdir(REPO_ROOT)
Path(".local_reports").mkdir(exist_ok=True)
Path(".local_logs").mkdir(exist_ok=True)

ts = time.strftime("%Y%m%d_%H%M%S")
start = time.time()
start_iso = time.strftime("%Y-%m-%dT%H:%M:%S%z")
log_path = Path(f".local_logs/A10B_prior_inventory_{ts}.log")
workload_path = Path(f".local_reports/A10B_prior_workload_inventory_{ts}.csv")
stats_path = Path(f".local_reports/A10B_prior_stats_field_inventory_{ts}.csv")
report_path = Path(f".local_reports/A10B_prior_inventory_summary_{ts}.md")

def log(msg):
    print(msg)
    with log_path.open("a") as f:
        f.write(msg + "\n")

def clean(s):
    return str(s or "").replace("\r", "").replace("\n", "").strip()

def latest(pattern):
    files = sorted(Path(".local_reports").glob(pattern), key=lambda p: p.stat().st_mtime)
    return files[-1] if files else None

def normalize_name(text):
    s = clean(text).lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    parts = [p for p in s.split("_") if p]
    drop = {"rodinia", "2", "0", "3", "1", "ft", "trace", "traces", "cuda", "data", "result", "txt"}
    parts = [p for p in parts if p not in drop]
    aliases = {
        "bp": "backprop", "needle": "nw", "needleman": "nw", "lava": "lavamd",
        "lava_md": "lavamd", "mri_q": "mriq", "mriq": "mriq", "srad_v2": "srad",
    }
    joined = "_".join(parts)
    known = [
        "backprop", "bfs", "hotspot", "lud", "nw", "streamcluster", "pathfinder",
        "gaussian", "srad", "lavamd", "kmeans", "mriq", "stencil", "nn",
        "heartwall", "cutlass", "polybench", "parboil",
    ]
    for k in known:
        if k in parts or k in joined:
            return aliases.get(k, k)
    return aliases.get(joined, joined[:80])

def paper_hint(path, text, fallback):
    blob = f"{path}\n{text}"
    has_mascar = re.search(r"mascar", blob, re.I)
    has_medic = re.search(r"\bmedic\b|memory divergence correction", blob, re.I)
    if has_mascar and has_medic:
        return "both"
    if has_mascar:
        return "Mascar"
    if has_medic:
        return "MeDiC"
    return fallback or "unknown"

def suite_hint(text):
    low = text.lower()
    for suite in ["rodinia", "parboil", "polybench", "sdk", "cutlass"]:
        if suite in low:
            return suite
    return ""

def source_type(path, artifact_type):
    if artifact_type:
        return artifact_type
    suf = Path(path).suffix.lower()
    return {".sh": "script", ".py": "script", ".csv": "stats_csv", ".md": "doc", ".txt": "doc", ".log": "log"}.get(suf, "unknown_text")

workload_terms = [
    "backprop", "bfs", "hotspot", "lud", "nw", "streamcluster", "pathfinder",
    "gaussian", "srad", "srad_v2", "lavaMD", "lavamd", "lava_md", "kmeans",
    "mri-q", "mriq", "stencil", "heartwall", "nn",
]
workload_re = re.compile(r"(?i)\b(" + "|".join(re.escape(w) for w in workload_terms) + r")(?:[-_][A-Za-z0-9_.-]+)*\b")
stat_re = re.compile(r"\b(gpgpu_[A-Za-z0-9_]+|gpu_[A-Za-z0-9_]+|l2_[A-Za-z0-9_]+|dram_[A-Za-z0-9_]+|ipc|speedup|runtime|cycles?)\b", re.I)

inventory = os.environ.get("ACCELSIM_A10A_INVENTORY")
inventory_path = Path(inventory) if inventory else latest("A10A_prior_artifact_inventory_*.csv")
status = "PASS"
blocker = "none"
workloads = OrderedDict()
stats = OrderedDict()

log("A10B prior inventory extraction")
log(f"Start: {start_iso}")
log(f"Input inventory: {inventory_path}")

if not inventory_path or not inventory_path.exists():
    status = "BLOCKED_NO_A10A_INVENTORY"
    blocker = "missing A10A inventory CSV"
    artifact_rows = []
else:
    with inventory_path.open(newline="") as f:
        artifact_rows = list(csv.DictReader(f))

sources = []
for row in artifact_rows:
    paper_row = clean(row.get("paper_hint"))
    path_blob = clean(row.get("source_path")) + " " + clean(row.get("matched_terms"))
    if paper_row == "unknown" and not re.search(r"mascar|\bmedic\b", path_blob, re.I):
        continue
    for key in ["source_path", "extracted_path"]:
        value = clean(row.get(key))
        if not value:
            continue
        p = Path(value)
        if p.is_dir():
            for child in p.rglob("*"):
                if child.is_file() and child.suffix.lower() in {".md",".txt",".sh",".py",".csv",".log",".out",".config",".cfg",".ini",".list"} and child.stat().st_size <= 10_485_760:
                    sources.append((child, row))
        elif p.is_file() and p.suffix.lower() in {".md",".txt",".sh",".py",".csv",".log",".out",".config",".cfg",".ini",".list"}:
            sources.append((p, row))

for path, row in sources:
    try:
        text = path.read_text(errors="replace")
    except OSError:
        continue
    stype = source_type(path, row.get("artifact_type"))
    paper = paper_hint(path, text[:4096], row.get("paper_hint"))
    lines = text.splitlines()
    for lineno, line in enumerate(lines[:4000], 1):
        clean_line = clean(line)
        if not clean_line:
            continue
        for match in workload_re.finditer(clean_line):
            original = clean(match.group(0))
            norm = normalize_name(original)
            if not norm or len(norm) < 2:
                continue
            lower_line = clean_line.lower()
            high_cue = any(c in lower_line for c in ["run", "benchmark", "app", "kernel", "stats", "gpgpu", "rodinia", "parboil", "polybench"])
            if stype in {"script", "stats_csv", "config", "log"} and high_cue:
                strength = "high"
            elif stype in {"script", "stats_csv", "config", "log"}:
                strength = "medium"
            elif high_cue:
                strength = "medium"
            else:
                strength = "low"
            key = (paper, str(path), lineno, original, norm)
            workloads[key] = {
                "workload_id": f"W{len(workloads)+1:05d}",
                "paper": paper,
                "source_path": str(path),
                "source_line": lineno,
                "source_type": stype,
                "original_name": original,
                "normalized_name": norm,
                "suite_hint": suite_hint(clean_line),
                "config_hint": "GPGPU-Sim" if re.search(r"gpgpu|config", clean_line, re.I) else "",
                "run_mode_hint": "scripted" if stype == "script" else ("stats" if stype == "stats_csv" else ""),
                "args_hint": clean_line[:180],
                "evidence_strength": strength,
                "notes": "extracted from real A10A artifact",
            }
        if stype == "stats_csv" and lineno == 1:
            for field in next(csv.reader([clean_line])):
                if field:
                    norm = re.sub(r"[^a-z0-9]+", "_", field.lower()).strip("_")
                    stats[(paper, str(path), field)] = {
                        "field_id": f"S{len(stats)+1:05d}",
                        "paper": paper,
                        "source_path": str(path),
                        "field_name": field,
                        "normalized_field_name": norm,
                        "field_type": "unknown",
                        "likely_meaning": "CSV header from prior artifact",
                        "used_by_script": "unknown",
                        "notes": "header field",
                    }
        for sm in stat_re.finditer(clean_line):
            field = clean(sm.group(1))
            norm = re.sub(r"[^a-z0-9]+", "_", field.lower()).strip("_")
            if field.lower().startswith("gpgpu"):
                ftype = "gpgpusim_stat"
            elif field.lower().startswith("gpu"):
                ftype = "gpgpusim_stat"
            elif field.lower().startswith("l2"):
                ftype = "cache"
            elif field.lower().startswith("dram"):
                ftype = "memory"
            elif field.lower() in {"runtime", "cycles"}:
                ftype = "timing"
            elif field.lower() == "speedup":
                ftype = "speedup"
            else:
                ftype = "unknown"
            stats[(paper, str(path), field)] = {
                "field_id": f"S{len(stats)+1:05d}",
                "paper": paper,
                "source_path": str(path),
                "field_name": field,
                "normalized_field_name": norm,
                "field_type": ftype,
                "likely_meaning": "prior GPGPU-Sim/statistics reference",
                "used_by_script": "yes" if stype == "script" else "unknown",
                "notes": f"line {lineno}",
            }

with workload_path.open("w", newline="") as f:
    fields = ["workload_id","paper","source_path","source_line","source_type","original_name","normalized_name","suite_hint","config_hint","run_mode_hint","args_hint","evidence_strength","notes"]
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(workloads.values())

with stats_path.open("w", newline="") as f:
    fields = ["field_id","paper","source_path","field_name","normalized_field_name","field_type","likely_meaning","used_by_script","notes"]
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(stats.values())

if status == "PASS" and not workloads:
    status = "BLOCKED_NO_PRIOR_WORKLOADS"
    blocker = "real artifacts found but no workload evidence extracted"

end_iso = time.strftime("%Y-%m-%dT%H:%M:%S%z")
wall = int(time.time() - start)
high = sum(1 for w in workloads.values() if w["evidence_strength"] == "high")
mascar = sorted({w["normalized_name"] for w in workloads.values() if w["paper"] in {"Mascar", "both"}})
medic = sorted({w["normalized_name"] for w in workloads.values() if w["paper"] in {"MeDiC", "both"}})

report_path.write_text(f"""# A10B Prior Inventory Extraction

- Status: {status}
- Start time: {start_iso}
- End time: {end_iso}
- Wall clock seconds: {wall}
- Command: `python3 scripts/accelsim/a10b_extract_prior_inventory.py`
- Log: `{log_path}`
- A10A inventory: `{inventory_path or ''}`
- Workload inventory CSV: `{workload_path}`
- Stats field inventory CSV: `{stats_path}`
- Blocker: {blocker}

## Counts

- Source files inspected: {len(sources)}
- Workload rows: {len(workloads)}
- High evidence workload rows: {high}
- Stats field rows: {len(stats)}

## Mascar Workload Candidates

```
{os.linesep.join(mascar[:40])}
```

## MeDiC Workload Candidates

```
{os.linesep.join(medic[:40])}
```

## Git Status

```
{os.popen('git status --short').read()}
```
""")

log(f"A10B report: {report_path}")
log(f"A10B workload inventory: {workload_path}")
log(f"A10B stats inventory: {stats_path}")
log(f"A10B status: {status}")
sys.exit(0 if status in {"PASS", "BLOCKED_NO_A10A_INVENTORY", "BLOCKED_NO_PRIOR_WORKLOADS"} else 1)
