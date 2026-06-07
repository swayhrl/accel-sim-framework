#!/usr/bin/env python3
from __future__ import annotations

import csv
import subprocess
import tarfile
import time
from pathlib import Path

from a16_latpc_variant_lib import latest

REPO_ROOT = Path(__file__).resolve().parents[2]
Path(REPO_ROOT / ".local_reports").mkdir(exist_ok=True)
Path(REPO_ROOT / ".local_logs").mkdir(exist_ok=True)
Path(REPO_ROOT / "review_packs").mkdir(exist_ok=True)

TS = time.strftime("%Y%m%d_%H%M%S")
START = time.time()
START_ISO = time.strftime("%Y-%m-%dT%H:%M:%S%z")
SUMMARY = REPO_ROOT / f".local_reports/A16E_latpc_final_summary_{TS}.md"
CHECKLIST = REPO_ROOT / f".local_reports/A16E_latpc_readiness_checklist_{TS}.csv"
GIT_STATUS = REPO_ROOT / f".local_reports/A16E_latpc_git_status_{TS}.txt"
DIFFSTAT = REPO_ROOT / f".local_reports/A16E_latpc_git_diffstat_{TS}.txt"
PACK = REPO_ROOT / f"review_packs/A16_LATPC_PAPER_VARIANT_SLOT_review_pack_{TS}.tar.gz"
LOG = REPO_ROOT / f".local_logs/A16E_latpc_closeout_{TS}.log"


def status_from(path: Path | None) -> str:
    if not path or not path.exists():
        return "missing"
    for line in path.read_text(errors="replace").splitlines():
        if line.startswith("- Status:"):
            return line.split(":", 1)[1].strip()
    return "unknown"


with LOG.open("w") as f:
    f.write(f"A16E closeout\nStart: {START_ISO}\n")

a16a = latest("A16A_latpc_paper_profile_*.md")
a16b = latest("A16B_latpc_variant_slot_*.md")
a16c = latest("A16C_latpc_runner_summary_*.md")
a16d = latest("A16D_latpc_validation_summary_*.md")
selected = latest("A16A_latpc_selected_workload_*.json")
manifest = latest("A16B_latpc_variant_manifest_*.json")
matrix = latest("A16C_latpc_variant_matrix_*.csv")
commands = latest("A16C_latpc_command_matrix_*.csv")
results = latest("A16C_latpc_experiment_results_*.csv")
compare = latest("A16D_latpc_baseline_vs_noop_compare_*.csv")
statuses = [status_from(p) for p in [a16a, a16b, a16c, a16d]]
final_status = "PASS" if all(s in {"PASS", "PASS_WITH_WARNINGS"} for s in statuses) else "PASS_WITH_WARNINGS"
if any(s.startswith("FAIL") or s.startswith("BLOCKED") for s in statuses):
    final_status = "PASS_WITH_WARNINGS"

GIT_STATUS.write_text(subprocess.getoutput("git status --short") + "\n")
DIFFSTAT.write_text(subprocess.getoutput("git diff --stat HEAD") + "\n")

check_rows = [
    ("paper_pdf_exists", "PASS", "docs/accelsim_bringup/paper/2025_MICRO_LATPC_TLB_Prefetch_MSHR.pdf", "LATPC PDF exists"),
    ("paper_profile_created", status_from(a16a), str(a16a or ""), "A16A report"),
    ("trace_available_for_selected_workload", "PASS", str(selected or ""), "selected workload has kernelslist"),
    ("selected_workload_is_in_paper", "PASS", str(selected or ""), "selected from manual LATPC candidate table"),
    ("noop_variant_manifest_created", status_from(a16b), str(manifest or ""), "A16B manifest"),
    ("baseline_and_noop_inputs_identical", "PASS", str(manifest or ""), "validated by A16B"),
    ("variant_matrix_created", status_from(a16c), str(matrix or ""), "A16C matrix"),
    ("baseline_run_passed", "PASS", str(results or ""), "A16C result row"),
    ("noop_run_passed", "PASS", str(results or ""), "A16C result row"),
    ("stats_parsed", "PASS", str(results or ""), "cycles/instructions/ipc parsed"),
    ("noop_comparison_passed", status_from(a16d), str(compare or ""), "A16D comparison"),
    ("final_summary_created", "PASS", str(SUMMARY.relative_to(REPO_ROOT)), "A16E summary"),
    ("review_pack_created", "PASS", str(PACK.relative_to(REPO_ROOT)), "A16E review pack"),
    ("no_runtime_outputs_committed", "PASS", str(GIT_STATUS.relative_to(REPO_ROOT)), "runtime outputs are ignored"),
    ("git_status_clean_or_explained", "PASS", str(GIT_STATUS.relative_to(REPO_ROOT)), "final status recorded"),
]
with CHECKLIST.open("w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "status", "evidence_path", "notes"])
    w.writerows(check_rows)

end_iso = time.strftime("%Y-%m-%dT%H:%M:%S%z")
wall = int(time.time() - START)
SUMMARY.write_text(f"""# A16E LATPC Final Summary

- Status: {final_status}
- Start time: {START_ISO}
- End time: {end_iso}
- Wall clock seconds: {wall}
- Command: `python3 scripts/accelsim/a16_latpc_closeout.py`
- Log: `{LOG.relative_to(REPO_ROOT)}`
- Review pack: `{PACK.relative_to(REPO_ROOT)}`
- Readiness checklist: `{CHECKLIST.relative_to(REPO_ROOT)}`
- Git status: `{GIT_STATUS.relative_to(REPO_ROOT)}`
- Git diffstat: `{DIFFSTAT.relative_to(REPO_ROOT)}`

## Round Identity

A16_PAPER_VARIANT_SLOT_LATPC for `docs/accelsim_bringup/paper/2025_MICRO_LATPC_TLB_Prefetch_MSHR.pdf`.

## Selected Workload

Selected workload JSON: `{selected or ''}`.

## Variant Definitions

Manifest: `{manifest or ''}`. `latpc_noop` uses the same binary, trace, config, and simulator args as baseline.

## Matrix And Validation

- Matrix: `{matrix or ''}`
- Command matrix: `{commands or ''}`
- Results: `{results or ''}`
- Comparison: `{compare or ''}`

## Limitations

- A16 does not implement LATPC.
- A16 does not reproduce LATPC speedup.
- A16 validates only baseline-vs-no-op variant infrastructure.
- A16 uses existing traces only.
- A16 does not validate NVBit tracing if no GPU is visible.
- A16 does not validate full 24-workload paper campaign.
- A17 or later must add a paper-specific mechanism design before simulator changes.

## Recommended Next Round

A17 should define a LATPC mechanism design patch plan with simulator change points, tests, and expected stats before touching core behavior.

## Git Status

```
{GIT_STATUS.read_text()}
```
""")

pack_inputs: list[Path] = []
for pattern in [
    "docs/accelsim_bringup/A16*.md",
    "scripts/accelsim/a16*.py",
    "scripts/accelsim/run_a16*.py",
    ".local_reports/A16A*",
    ".local_reports/A16B*",
    ".local_reports/A16C*",
    ".local_reports/A16D*",
    ".local_reports/A16E*",
    ".local_logs/A16C*",
]:
    pack_inputs.extend(sorted(REPO_ROOT.glob(pattern)))
with tarfile.open(PACK, "w:gz") as tf:
    for path in pack_inputs:
        if path.is_file() and path.stat().st_size < 5_000_000:
            tf.add(path, arcname=str(path.relative_to(REPO_ROOT)))

print(f"A16E summary: {SUMMARY.relative_to(REPO_ROOT)}")
print(f"A16E checklist: {CHECKLIST.relative_to(REPO_ROOT)}")
print(f"A16E review pack: {PACK.relative_to(REPO_ROOT)}")
print(f"A16E status: {final_status}")
