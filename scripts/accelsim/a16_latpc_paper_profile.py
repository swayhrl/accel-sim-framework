#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True

REPO_ROOT = Path(__file__).resolve().parents[2]
os.chdir(REPO_ROOT)
Path(".local_reports").mkdir(exist_ok=True)
Path(".local_logs").mkdir(exist_ok=True)

TS = time.strftime("%Y%m%d_%H%M%S")
START = time.time()
START_ISO = time.strftime("%Y-%m-%dT%H:%M:%S%z")
PAPER = Path("docs/accelsim_bringup/paper/2025_MICRO_LATPC_TLB_Prefetch_MSHR.pdf")
PROFILE = Path(f".local_reports/A16A_latpc_paper_profile_{TS}.md")
CANDIDATES = Path(f".local_reports/A16A_latpc_workload_candidates_{TS}.csv")
SELECTED = Path(f".local_reports/A16A_latpc_selected_workload_{TS}.json")
TEXT = Path(f".local_reports/A16A_latpc_paper_text_{TS}.txt")
LOG = Path(f".local_logs/A16A_latpc_paper_profile_{TS}.log")


def clean(value: object) -> str:
    return str(value or "").replace("\r", "").replace("\n", "").strip()


def latest(pattern: str) -> Path | None:
    files = sorted(Path(".local_reports").glob(pattern), key=lambda p: p.stat().st_mtime)
    return files[-1] if files else None


def norm_workload(name: str) -> str:
    n = re.sub(r"[^a-z0-9]+", "_", clean(name).lower()).strip("_")
    if n in {"needle", "needleman", "needleman_wunsch", "nw"}:
        return "nw"
    if n in {"bp", "backprop"}:
        return "backprop"
    if n in {"bfr", "rodinia_bfs", "bfs"}:
        return "bfs"
    return n


def read_csv(path: Path | None) -> list[dict[str, str]]:
    if not path or not path.exists():
        return []
    with path.open(newline="") as f:
        return [{k: clean(v) for k, v in row.items()} for row in csv.DictReader(f)]


def trace_inventory() -> dict[str, list[dict[str, str]]]:
    traces: dict[str, list[dict[str, str]]] = {}
    for root in [Path(".local_traces"), Path("hw_run")]:
        if root.exists():
            for k in root.rglob("kernelslist.g"):
                key = norm_workload(k.parent.parent.parent.name)
                traces.setdefault(key, []).append({
                    "kernelslist_path": str(k),
                    "config_path": "gpu-simulator/gpgpu-sim/configs/tested-cfgs/SM7_QV100/gpgpusim.config",
                    "evidence_source": str(k),
                })
    for pattern in ["A12_workload_config_lock_*.csv", "A13_experiment_matrix_*.csv"]:
        for row in read_csv(latest(pattern)):
            key = norm_workload(row.get("normalized_workload") or row.get("workload"))
            kernels = row.get("kernelslist_path")
            if kernels:
                traces.setdefault(key, []).append({
                    "kernelslist_path": kernels,
                    "config_path": row.get("gpgpusim_config_path") or "gpu-simulator/gpgpu-sim/configs/tested-cfgs/SM7_QV100/gpgpusim.config",
                    "evidence_source": str(latest(pattern) or ""),
                })
    return traces


with LOG.open("w") as f:
    f.write(f"A16A LATPC paper profile\nStart: {START_ISO}\n")

status = "PASS"
blocker = "none"
pdf_extract = "not_attempted"
paper_text_excerpt = ""
if not PAPER.exists():
    status = "BLOCKED_NO_PDF"
    blocker = f"missing paper PDF: {PAPER}"
elif shutil.which("pdftotext"):
    try:
        subprocess.run(["pdftotext", str(PAPER), str(TEXT)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        pdf_extract = "ok"
        paper_text_excerpt = TEXT.read_text(errors="replace")[:4000]
    except subprocess.CalledProcessError as exc:
        pdf_extract = f"failed: {exc}"
        status = "PASS_WITH_WARNINGS"
elif PAPER.exists():
    pdf_extract = "skipped_pdftotext_unavailable"
    status = "PASS_WITH_WARNINGS"

manual_candidates = [
    {"paper_workload": "nw", "normalized_workload": "nw", "abbreviation": "NW", "workload_class": "Regular+High", "suite_hint": "Rodinia", "priority": 1},
    {"paper_workload": "lud", "normalized_workload": "lud", "abbreviation": "LUD", "workload_class": "Regular+High", "suite_hint": "Rodinia", "priority": 2},
    {"paper_workload": "backprop", "normalized_workload": "backprop", "abbreviation": "BP", "workload_class": "Regular+Low", "suite_hint": "Rodinia", "priority": 3},
    {"paper_workload": "rodinia-bfs", "normalized_workload": "bfs", "abbreviation": "BFR", "workload_class": "Irregular", "suite_hint": "Rodinia", "priority": 4},
    {"paper_workload": "bfs", "normalized_workload": "bfs", "abbreviation": "BFR", "workload_class": "Irregular", "suite_hint": "Rodinia alias", "priority": 5},
]
traces = trace_inventory()
rows = []
selected_row = None
for cand in manual_candidates:
    evidence = traces.get(cand["normalized_workload"], [])
    best = evidence[0] if evidence else {}
    row = {
        "paper": "LATPC",
        **cand,
        "trace_available": "yes" if evidence else "no",
        "kernelslist_path": clean(best.get("kernelslist_path")),
        "config_path": clean(best.get("config_path")),
        "evidence_source": clean(best.get("evidence_source")),
        "evidence_count": str(len(evidence)),
        "selected": "no",
        "notes": "manual LATPC paper candidate with existing trace evidence" if evidence else "no existing trace evidence found",
    }
    if selected_row is None and evidence and status != "BLOCKED_NO_PDF":
        row["selected"] = "yes"
        selected_row = row
    rows.append(row)

if status != "BLOCKED_NO_PDF" and selected_row is None:
    status = "BLOCKED_NO_TRACE"
    blocker = "no existing trace for nw/lud/backprop/bfs LATPC candidates"

with CANDIDATES.open("w", newline="") as f:
    fields = ["paper","paper_workload","normalized_workload","abbreviation","workload_class","suite_hint","priority","trace_available","kernelslist_path","config_path","evidence_source","evidence_count","selected","notes"]
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(rows)

selected_payload = {
    "paper": "LATPC",
    "round": "A16",
    "selected_workload": selected_row["normalized_workload"] if selected_row else "",
    "paper_workload": selected_row["paper_workload"] if selected_row else "",
    "abbreviation": selected_row["abbreviation"] if selected_row else "",
    "workload_class": selected_row["workload_class"] if selected_row else "",
    "suite_hint": selected_row["suite_hint"] if selected_row else "",
    "kernelslist_path": selected_row["kernelslist_path"] if selected_row else "",
    "config_path": selected_row["config_path"] if selected_row else "",
    "selection_reason": "first trace-available workload in priority nw,lud,backprop,bfs" if selected_row else "",
    "fallback_used": "no" if selected_row and selected_row["normalized_workload"] == "nw" else ("yes" if selected_row else ""),
    "timestamp": TS,
    "status": status,
}
SELECTED.write_text(json.dumps(selected_payload, indent=2))

end_iso = time.strftime("%Y-%m-%dT%H:%M:%S%z")
wall = int(time.time() - START)
PROFILE.write_text(f"""# A16A LATPC Paper Profile

- Status: {status}
- Start time: {START_ISO}
- End time: {end_iso}
- Wall clock seconds: {wall}
- Command: `python3 scripts/accelsim/a16_latpc_paper_profile.py`
- Log: `{LOG}`
- Paper PDF: `{PAPER}`
- PDF text extraction: `{pdf_extract}`
- Candidate CSV: `{CANDIDATES}`
- Selected workload JSON: `{SELECTED}`
- Blocker: {blocker}

## Paper Facts

- Title: LATPC: Accelerating GPU Address Translation Using Locality-Aware TLB Prefetching and MSHR Compression.
- LATPC is evaluated with Accel-Sim.
- The simulator is extended in the paper to model multi-level TLBs, page walk queue, page table walkers, and page walk cache.
- The evaluated system is RTX 2060-like.
- The paper evaluates 24 workloads from CUDA SDK, Lonestar, Pannotia, Parboil, Polybench, and Rodinia.
- A16 does not implement LATP or LATC and does not claim LATPC speedup reproduction.

## Selected Workload

```
{json.dumps(selected_payload, indent=2)}
```

## PDF Text Excerpt

```
{paper_text_excerpt[:1200]}
```

## Git Status

```
{subprocess.getoutput("git status --short")}
```
""")

print(f"A16A report: {PROFILE}")
print(f"A16A candidates: {CANDIDATES}")
print(f"A16A selected: {SELECTED}")
print(f"A16A status: {status}")
sys.exit(0 if status in {"PASS", "PASS_WITH_WARNINGS", "BLOCKED_NO_TRACE", "BLOCKED_NO_PDF"} else 1)
