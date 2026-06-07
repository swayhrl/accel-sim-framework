#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True

from accelsim_stats_parser import first_stat, parse_log
from a16_latpc_variant_lib import latest

REPO_ROOT = Path(__file__).resolve().parents[2]
os.chdir(REPO_ROOT)
Path(".local_reports").mkdir(exist_ok=True)
Path(".local_logs").mkdir(exist_ok=True)
Path(".local_runs").mkdir(exist_ok=True)

TS = time.strftime("%Y%m%d_%H%M%S")
START = time.time()
START_ISO = time.strftime("%Y-%m-%dT%H:%M:%S%z")
RUN_NAME = f"A16C_latpc_variant_matrix_{TS}"
MATRIX = Path(f".local_reports/A16C_latpc_variant_matrix_{TS}.csv")
COMMANDS = Path(f".local_reports/A16C_latpc_command_matrix_{TS}.csv")
RESULTS = Path(f".local_reports/A16C_latpc_experiment_results_{TS}.csv")
SUMMARY = Path(f".local_reports/A16C_latpc_runner_summary_{TS}.md")
LOG = Path(f".local_logs/A16C_latpc_runner_{TS}.log")
TIMEOUT = int(os.environ.get("ACCELSIM_A16C_TIMEOUT_SEC", "900"))


def accelsim_env(variant_id: str) -> dict[str, str]:
    env = os.environ.copy()
    try:
        raw = subprocess.check_output(
            ["bash", "-lc", f"cd {REPO_ROOT} && source scripts/accelsim/accelsim_env.sh >/dev/null && env -0"],
            stderr=subprocess.DEVNULL,
        )
        for item in raw.split(b"\0"):
            if item and b"=" in item:
                k, v = item.split(b"=", 1)
                env[k.decode()] = v.decode(errors="replace")
    except Exception:
        pass
    env["ACCELSIM_PAPER"] = "LATPC"
    env["ACCELSIM_VARIANT"] = variant_id
    env["ACCELSIM_ROUND"] = "A16"
    return env


def abs_path(value: str) -> Path:
    p = Path(str(value).replace("\r", "").replace("\n", "").strip())
    return p if p.is_absolute() else REPO_ROOT / p


with LOG.open("w") as f:
    f.write(f"A16C LATPC variant matrix\nStart: {START_ISO}\n")

manifest_path = latest("A16B_latpc_variant_manifest_*.json")
status = "PASS"
blocker = "none"
manifest = {}
if not manifest_path:
    status = "BLOCKED_NO_A16B"
    blocker = "missing A16B manifest"
else:
    manifest = json.loads(manifest_path.read_text())

matrix_rows: list[dict[str, str]] = []
command_rows: list[dict[str, str]] = []
result_rows: list[dict[str, str]] = []
if status == "PASS":
    for idx, variant in enumerate(manifest["variants"], 1):
        command_id = f"A16C_{idx:02d}_{variant['variant_id']}"
        log_path = Path(f".local_logs/A16C_{TS}_{variant['variant_id']}.log")
        matrix_rows.append({
            "paper": "LATPC",
            "workload": manifest["selected_workload"],
            "variant_id": variant["variant_id"],
            "variant_kind": variant["variant_kind"],
            "kernelslist_path": variant["kernelslist_path"],
            "config_path": variant["config_path"],
            "simulator_binary": variant["simulator_binary"],
            "command_id": command_id,
            "expected_equivalence": variant["expected_stats_relation_to_baseline"],
            "status": "PLANNED",
        })
        run_dir = Path(".local_runs") / RUN_NAME / variant["variant_id"]
        run_dir.mkdir(parents=True, exist_ok=True)
        trace_dir = abs_path(variant["kernelslist_path"]).parent
        link = run_dir / "traces"
        if link.exists() or link.is_symlink():
            link.unlink()
        link.symlink_to(trace_dir)
        config_dir = abs_path(variant["config_path"]).parent
        shutil.copytree(config_dir, run_dir, dirs_exist_ok=True, ignore=shutil.ignore_patterns("gpgpusim.config"))
        combined = run_dir / "gpgpusim.config"
        combined.write_text(abs_path(variant["config_path"]).read_text(errors="replace").replace("\r", "") + "\n#SASS\n#SASS-Driven Accel-Sim\n\n" + abs_path(variant["trace_config_path"]).read_text(errors="replace").replace("\r", ""))
        cmd = ["timeout", str(TIMEOUT), variant["simulator_binary"], "-config", "./gpgpusim.config", "-trace", "./traces/kernelslist.g"]
        start = time.time()
        start_iso = time.strftime("%Y-%m-%dT%H:%M:%S%z")
        with log_path.open("w") as logf:
            proc = subprocess.run(cmd, cwd=run_dir, stdout=logf, stderr=subprocess.STDOUT, env=accelsim_env(variant["variant_id"]))
        end_iso = time.strftime("%Y-%m-%dT%H:%M:%S%z")
        wall = int(time.time() - start)
        command_rows.append({
            "command_id": command_id,
            "variant_id": variant["variant_id"],
            "cwd": str(run_dir),
            "command": " ".join(cmd),
            "log_path": str(log_path),
            "start_time": start_iso,
            "end_time": end_iso,
            "wall_seconds": str(wall),
            "return_code": str(proc.returncode),
        })
        text = log_path.read_text(errors="replace")
        row_status = "PASS" if proc.returncode == 0 and "GPGPU-Sim: *** exit detected ***" in text else ("TIMEOUT" if proc.returncode == 124 else "FAIL")
        if row_status != "PASS":
            status = "FAIL_RUNNER"
            blocker = f"{variant['variant_id']} returned {proc.returncode}"
        result_rows.append({
            "paper": "LATPC",
            "workload": manifest["selected_workload"],
            "variant_id": variant["variant_id"],
            "status": row_status,
            "log_path": str(log_path),
            "stats_path": str(log_path),
            "cycles": first_stat(log_path, "gpu_tot_sim_cycle", "last"),
            "instructions": first_stat(log_path, "gpgpu_n_tot_w_icount", "last"),
            "ipc": first_stat(log_path, "gpu_tot_ipc", "last"),
            "l2_accesses": first_stat(log_path, "l2_total_cache_accesses", "last"),
            "l2_misses": first_stat(log_path, "l2_total_cache_misses", "last"),
            "raw_stats_fields_count": str(len(parse_log(log_path))),
            "notes": "same simulator inputs; variant differs only by metadata env",
        })

for path, rows, fields in [
    (MATRIX, matrix_rows, ["paper","workload","variant_id","variant_kind","kernelslist_path","config_path","simulator_binary","command_id","expected_equivalence","status"]),
    (COMMANDS, command_rows, ["command_id","variant_id","cwd","command","log_path","start_time","end_time","wall_seconds","return_code"]),
    (RESULTS, result_rows, ["paper","workload","variant_id","status","log_path","stats_path","cycles","instructions","ipc","l2_accesses","l2_misses","raw_stats_fields_count","notes"]),
]:
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

if status == "PASS" and not any(r.get("cycles") != "NA" or r.get("instructions") != "NA" or r.get("ipc") != "NA" for r in result_rows):
    status = "PASS_WITH_WARNINGS"
    blocker = "commands passed but only partial stats parsed"

end_iso = time.strftime("%Y-%m-%dT%H:%M:%S%z")
wall = int(time.time() - START)
SUMMARY.write_text(f"""# A16C LATPC Variant Matrix Runner

- Status: {status}
- Start time: {START_ISO}
- End time: {end_iso}
- Wall clock seconds: {wall}
- Command: `python3 scripts/accelsim/run_a16_latpc_variant_matrix.py`
- Log: `{LOG}`
- Manifest: `{manifest_path or ''}`
- Matrix CSV: `{MATRIX}`
- Command matrix CSV: `{COMMANDS}`
- Results CSV: `{RESULTS}`
- Blocker: {blocker}

## Command Pattern

Verified against A13 direct runner: `accel-sim.out -config ./gpgpusim.config -trace ./traces/kernelslist.g`.

## Limitations

Only the selected workload is run. `latpc_noop` is metadata only and does not implement LATPC.

## Git Status

```
{subprocess.getoutput('git status --short')}
```
""")

print(f"A16C summary: {SUMMARY}")
print(f"A16C matrix: {MATRIX}")
print(f"A16C commands: {COMMANDS}")
print(f"A16C results: {RESULTS}")
print(f"A16C status: {status}")
sys.exit(0 if status in {"PASS", "PASS_WITH_WARNINGS", "BLOCKED_NO_A16B"} else 1)
