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

from accelsim_stats_parser import clean_field, first_stat

REPO_ROOT = Path(__file__).resolve().parents[2]
os.chdir(REPO_ROOT)
Path(".local_reports").mkdir(exist_ok=True)
Path(".local_logs").mkdir(exist_ok=True)
Path(".local_runs").mkdir(exist_ok=True)

TS = time.strftime("%Y%m%d_%H%M%S")
START = time.time()
START_ISO = time.strftime("%Y-%m-%dT%H:%M:%S%z")
RUN_NAME = os.environ.get("ACCELSIM_A13_RUN_NAME", f"A13_matrix_{TS}")
VARIANTS = [v.strip() for v in os.environ.get("ACCELSIM_A13_VARIANTS", "baseline").split(",") if v.strip()]
MAX_RUNS = int(os.environ.get("ACCELSIM_A13_MAX_RUNS", "4"))
TIMEOUT = int(os.environ.get("ACCELSIM_A13_TIMEOUT_SEC", "900"))
DRY = os.environ.get("ACCELSIM_A13_DRY_RUN", "0") == "1"
RESUME = os.environ.get("ACCELSIM_A13_RESUME", "1") == "1"
RERUN_FAILED = os.environ.get("ACCELSIM_A13_RERUN_FAILED", "0") == "1"
STATS_MODE = os.environ.get("ACCELSIM_A13_STATS_MODE", "last")
INCLUDE_SET = os.environ.get("ACCELSIM_A13_INCLUDE_SET", "smoke")

LOG = Path(f".local_logs/A13_experiment_matrix_{TS}.log")
MATRIX = Path(f".local_reports/A13_experiment_matrix_{TS}.csv")
RESULTS = Path(f".local_reports/A13_experiment_results_{TS}.csv")
REPORT = Path(f".local_reports/A13_experiment_matrix_summary_{TS}.md")
RUN_ROOT = Path(".local_runs") / RUN_NAME


def latest(pattern: str) -> Path | None:
    files = sorted(Path(".local_reports").glob(pattern), key=lambda p: p.stat().st_mtime)
    return files[-1] if files else None


def read_csv(path: Path | None) -> list[dict[str, str]]:
    if not path or not path.exists():
        return []
    with path.open(newline="") as f:
        return [{k: clean_field(v) for k, v in row.items()} for row in csv.DictReader(f)]


def abs_path(path: str) -> Path:
    p = Path(clean_field(path))
    return p if p.is_absolute() else REPO_ROOT / p


def accelsim_env() -> dict[str, str]:
    env = os.environ.copy()
    try:
        raw = subprocess.check_output(
            ["bash", "-lc", f"cd {REPO_ROOT} && source scripts/accelsim/accelsim_env.sh >/dev/null && env -0"],
            stderr=subprocess.DEVNULL,
        )
        for item in raw.split(b"\0"):
            if not item or b"=" not in item:
                continue
            key, value = item.split(b"=", 1)
            env[key.decode()] = value.decode(errors="replace")
    except Exception:
        pass
    return env


def parse_result(row: dict[str, str], status: str, exit_code: int | str, timed_out: str, log_path: Path, notes: str) -> dict[str, str]:
    return {
        "run_id": row["run_id"],
        "run_name": row["run_name"],
        "variant": row["variant"],
        "paper": row["paper"],
        "workload": row["normalized_workload"],
        "status": status,
        "exit_code": str(exit_code),
        "timed_out": timed_out,
        "stats_mode": row["stats_mode"],
        "log_path": str(log_path),
        "gpgpu_simulation_time": first_stat(log_path, "gpgpu_simulation_time", STATS_MODE),
        "gpgpu_simulation_rate_inst_sec": "NA",
        "gpgpu_simulation_rate_cycle_sec": "NA",
        "gpgpu_n_tot_w_icount": first_stat(log_path, "gpgpu_n_tot_w_icount", STATS_MODE),
        "gpu_tot_sim_cycle": first_stat(log_path, "gpu_tot_sim_cycle", STATS_MODE),
        "gpu_tot_ipc": first_stat(log_path, "gpu_tot_ipc", STATS_MODE),
        "l2_total_cache_accesses": first_stat(log_path, "l2_total_cache_accesses", STATS_MODE),
        "l2_total_cache_misses": first_stat(log_path, "l2_total_cache_misses", STATS_MODE),
        "exit_detected": str("GPGPU-Sim: *** exit detected ***" in log_path.read_text(errors="replace")) if log_path.exists() else "False",
        "notes": notes,
    }


lockfile = Path(os.environ.get("ACCELSIM_A13_LOCKFILE") or latest("A12_workload_config_lock_*.csv") or "")
locks = read_csv(lockfile)
include_col = {"smoke": "include_smoke", "pilot": "include_pilot", "paper_candidate": "include_paper_candidate"}.get(INCLUDE_SET, "include_smoke")
selected = [r for r in locks if r.get("runnable") == "yes" and r.get(include_col) == "yes"][:MAX_RUNS]

with LOG.open("w") as f:
    f.write(f"A13 experiment matrix\nStart: {START_ISO}\nLockfile: {lockfile}\n")

matrix_rows: list[dict[str, str]] = []
for lock in selected:
    for variant in VARIANTS:
        run_id = f"R{len(matrix_rows)+1:05d}"
        run_dir = RUN_ROOT / run_id
        log_path = Path(".local_logs") / f"{RUN_NAME}_{run_id}.log"
        planned = "RUN" if variant == "baseline" else "SKIPPED_NO_VARIANT_CONFIG"
        matrix_rows.append({
            "run_id": run_id,
            "run_name": RUN_NAME,
            "variant": variant,
            "paper": lock["paper"],
            "workload": lock["workload"],
            "normalized_workload": lock["normalized_workload"],
            "lock_id": lock["lock_id"],
            "kernelslist_path": str(abs_path(lock["kernelslist_path"])),
            "trace_root": str(abs_path(lock["trace_root"])) if lock["trace_root"] else "",
            "gpgpusim_config_path": str(abs_path(lock["gpgpusim_config_path"])),
            "accelsim_trace_config_path": str(abs_path(lock["accelsim_trace_config_path"])),
            "timeout_sec": str(TIMEOUT),
            "stats_mode": STATS_MODE,
            "run_dir": str(run_dir),
            "log_path": str(log_path),
            "planned_status": planned,
            "notes": "baseline direct Accel-Sim run" if variant == "baseline" else "variant config not provided in A13",
        })

with MATRIX.open("w", newline="") as f:
    fields = ["run_id","run_name","variant","paper","workload","normalized_workload","lock_id","kernelslist_path","trace_root","gpgpusim_config_path","accelsim_trace_config_path","timeout_sec","stats_mode","run_dir","log_path","planned_status","notes"]
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(matrix_rows)

results: list[dict[str, str]] = []
sim_bin = REPO_ROOT / "gpu-simulator/bin/release/accel-sim.out"
run_env = accelsim_env()
status = "PASS"
blocker = "none"
if not matrix_rows:
    status = "BLOCKED_NO_SELECTED_RUNS"
    blocker = "lockfile has no selected runnable rows"

if DRY:
    for row in matrix_rows:
        results.append(parse_result(row, "DRY_RUN" if row["planned_status"] == "RUN" else row["planned_status"], 0, "no", Path(row["log_path"]), "dry run only"))
elif status == "PASS":
    RUN_ROOT.mkdir(parents=True, exist_ok=True)
    for row in matrix_rows:
        run_dir = Path(row["run_dir"])
        log_path = Path(row["log_path"])
        meta = run_dir / "metadata.json"
        if row["planned_status"] != "RUN":
            results.append(parse_result(row, row["planned_status"], 0, "no", log_path, row["notes"]))
            continue
        if RESUME and meta.exists():
            old = json.loads(meta.read_text())
            old_status = old.get("status")
            if old_status == "PASS" and log_path.exists():
                results.append(parse_result(row, "SKIPPED_RESUME_PASS", old.get("exit_code", 0), "no", log_path, "resume preserved pass"))
                continue
            if old_status and old_status != "PASS" and not RERUN_FAILED:
                results.append(parse_result(row, f"SKIPPED_RESUME_{old_status}", old.get("exit_code", 1), old.get("timed_out", "no"), log_path, "resume preserved failed run"))
                continue
        run_dir.mkdir(parents=True, exist_ok=True)
        trace_dir = abs_path(row["kernelslist_path"]).parent
        link = run_dir / "traces"
        if link.exists() or link.is_symlink():
            link.unlink()
        link.symlink_to(trace_dir)
        shutil.copytree(abs_path(row["gpgpusim_config_path"]).parent, run_dir, dirs_exist_ok=True, ignore=shutil.ignore_patterns("gpgpusim.config"))
        combined = run_dir / "gpgpusim.config"
        combined.write_text(abs_path(row["gpgpusim_config_path"]).read_text(errors="replace").replace("\r", "") + "\n#SASS\n#SASS-Driven Accel-Sim\n\n" + abs_path(row["accelsim_trace_config_path"]).read_text(errors="replace").replace("\r", ""))
        cmd = ["timeout", str(TIMEOUT), str(sim_bin), "-config", "./gpgpusim.config", "-trace", "./traces/kernelslist.g"]
        with log_path.open("w") as logf:
            proc = subprocess.run(cmd, cwd=run_dir, stdout=logf, stderr=subprocess.STDOUT, env=run_env)
        rc = proc.returncode
        timed_out = "yes" if rc == 124 else "no"
        text = log_path.read_text(errors="replace") if log_path.exists() else ""
        run_status = "PASS" if rc == 0 and "GPGPU-Sim: *** exit detected ***" in text else ("TIMEOUT" if rc == 124 else "FAIL")
        meta.write_text(json.dumps({"status": run_status, "exit_code": rc, "timed_out": timed_out, "log_path": str(log_path)}, indent=2))
        results.append(parse_result(row, run_status, rc, timed_out, log_path, "bounded A13 baseline matrix run"))

with RESULTS.open("w", newline="") as f:
    fields = ["run_id","run_name","variant","paper","workload","status","exit_code","timed_out","stats_mode","log_path","gpgpu_simulation_time","gpgpu_simulation_rate_inst_sec","gpgpu_simulation_rate_cycle_sec","gpgpu_n_tot_w_icount","gpu_tot_sim_cycle","gpu_tot_ipc","l2_total_cache_accesses","l2_total_cache_misses","exit_detected","notes"]
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(results)

passed = sum(1 for r in results if r["status"] == "PASS")
failed = sum(1 for r in results if r["status"] == "FAIL")
timeouts = sum(1 for r in results if r["status"] == "TIMEOUT")
skipped = sum(1 for r in results if r["status"].startswith("SKIPPED"))
if status == "PASS" and (failed or timeouts):
    status = "PARTIAL_PASS_WITH_FAILURES"
if DRY and status == "PASS":
    status = "PASS_DRY_RUN"

end_iso = time.strftime("%Y-%m-%dT%H:%M:%S%z")
wall = int(time.time() - START)
git_status = subprocess.getoutput("git status --short")
REPORT.write_text(f"""# A13 Experiment Matrix

- Status: {status}
- Start time: {START_ISO}
- End time: {end_iso}
- Wall clock seconds: {wall}
- Command: `python3 scripts/accelsim/a13_experiment_matrix_runner.py`
- Log: `{LOG}`
- Lockfile: `{lockfile}`
- Matrix CSV: `{MATRIX}`
- Results CSV: `{RESULTS}`
- Blocker: {blocker}

## Settings

- Run name: `{RUN_NAME}`
- Variants: `{','.join(VARIANTS)}`
- Include set: `{INCLUDE_SET}`
- Max runs: {MAX_RUNS}
- Timeout seconds: {TIMEOUT}
- Dry run: {int(DRY)}
- Resume: {int(RESUME)}
- Rerun failed: {int(RERUN_FAILED)}
- Stats mode: `{STATS_MODE}`

## Results

- Matrix rows: {len(matrix_rows)}
- Passed: {passed}
- Failed: {failed}
- Timed out: {timeouts}
- Skipped: {skipped}

## Limitations

A13 only executes baseline by default. Variant labels are infrastructure slots unless a paper-specific variant config is provided.

## Git Status

```
{git_status}
```
""")

if Path("0").is_file() and Path("0").stat().st_size <= 16 and subprocess.getoutput("git status --short -- 0").startswith("??"):
    Path("0").unlink()

print(f"A13 summary: {REPORT}")
print(f"A13 matrix: {MATRIX}")
print(f"A13 results: {RESULTS}")
print(f"A13 status: {status}")
sys.exit(0 if status in {"PASS", "PASS_DRY_RUN", "PARTIAL_PASS_WITH_FAILURES", "BLOCKED_NO_SELECTED_RUNS"} else 1)
