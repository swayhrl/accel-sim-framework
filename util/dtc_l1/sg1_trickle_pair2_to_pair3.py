#!/usr/bin/env python3
"""One-shot, fail-closed TRICKLE handoff from SG1 Btree Pair 2 to BICG Pair 3.

This controller is deliberately narrow: it observes two immutable Pair-2 run
directories, invokes the existing strict validator only after both naturally
terminate, records the prescribed host admission evidence, and launches at
most the two BICG control variants.  It never signals a process and it stops
on any failed validation or failed resource gate.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path("/workspace/wave-a-sg1-runs")
FRAMEWORK = Path("/workspace/worktrees/accel-sim-iscas2027-dtc-sg1-wholeline")
RUNNER = FRAMEWORK / "util/dtc_l1/sg1_campaign.py"
AUTHORITY = FRAMEWORK / "docs/dtc_l1/iscas2027/tc80/TC80_WORKLOAD_AUTHORITY.tsv"
BASE = FRAMEWORK / "configs/dtc_l1/fast64/FAST64_BASE.config"
TRACE = FRAMEWORK / "gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config"
SIMULATOR = Path("/tmp/dtc-sg1-normal-fill-6ea5b782-r2/accel-sim.out")
CORE = "b838fb6f58a90c6519b65bfaf4c680a3fbf83753"
RUNTIME_SHA = "f26dcb8831c2331c7580999d73441803118f4c624c4e46ebcff18902ee13f8fd"
PAIR2 = {
    "B16-N": ROOT / "sg1_smoke_B16-N_Btree_b081e8dd-ee25-47ed-b633-a850365e1af9",
    "TC80-N": ROOT / "sg1_smoke_TC80-N_Btree_82397f73-30d2-4862-86a6-61288ec86ca8",
}
OVERLAYS = {
    "B16-N": FRAMEWORK / "docs/dtc_l1/iscas2027/granularity/sg1/config/SG1_B16_N_OVERLAY.config",
    "TC80-N": FRAMEWORK / "docs/dtc_l1/iscas2027/granularity/sg1/config/SG1_TC80_N_OVERLAY.config",
}
MARKER = ROOT / "SG1_PAIR2_TO_PAIR3_CONTROLLER.json"


def utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def command(*args: str) -> str:
    return subprocess.check_output(args, text=True, stderr=subprocess.STDOUT)


def terminal_exit(run_dir: Path) -> int | None:
    terminal = run_dir / "RUN_TERMINAL.tsv"
    if not terminal.is_file():
        return None
    for line in terminal.read_text(encoding="utf-8").splitlines():
        key, value = line.split("\t", 1)
        if key == "simulator_exit_status":
            return int(value)
    raise RuntimeError(f"missing simulator_exit_status: {terminal}")


def validate_pair2() -> dict[str, str]:
    results: dict[str, str] = {}
    for variant, run_dir in PAIR2.items():
        cmd = [
            "python3", str(RUNNER), "validate", "--authority", str(AUTHORITY),
            "--workload", "Btree", "--variant", variant, "--run-dir", str(run_dir),
            "--expected-runtime-sha", RUNTIME_SHA, "--expected-core-source-head", CORE,
        ]
        results[variant] = command(*cmd)
    return results


def admission() -> dict[str, object]:
    free = command("free", "-h")
    vmstat = command("vmstat", "1", "5")
    psi = Path("/proc/pressure/memory").read_text(encoding="utf-8")
    df = command("df", "-B1", "/workspace")
    ps = command("ps", "-eo", "pid,ni,stat,pcpu,rss,args")
    meminfo = Path("/proc/meminfo").read_text(encoding="utf-8")
    total = int(re.search(r"MemTotal:\s+(\d+)", meminfo).group(1))
    available = int(re.search(r"MemAvailable:\s+(\d+)", meminfo).group(1))
    fields = df.splitlines()[-1].split()
    disk_avail = int(fields[3])
    psi_values = [float(v) for v in re.findall(r"avg10=(\d+\.\d+)", psi)]
    vm_lines = vmstat.splitlines()[-5:]
    iowait = [float(line.split()[-2]) for line in vm_lines if len(line.split()) >= 17]
    cm5 = any(line.split(maxsplit=5)[0] == "262080" and "accel-sim.out" in line for line in ps.splitlines() if line.split())
    sg1_sims = [line for line in ps.splitlines() if "dtc-sg1-normal-fill" in line and "accel-sim.out" in line]
    passed = (
        available >= total // 10
        and disk_avail >= 35 * 1024**3
        and max(psi_values, default=100.0) < 1.0
        and max(iowait, default=100.0) < 20.0
        and cm5
        and not sg1_sims
    )
    return {
        "timestamp_utc": utc(), "pass": passed, "free_h": free, "vmstat_1_5": vmstat,
        "memory_psi": psi, "df_b1_workspace": df, "ps_inventory": ps,
        "mem_total_kib": total, "mem_available_kib": available,
        "disk_available_bytes": disk_avail, "psi_avg10": psi_values,
        "iowait_samples": iowait, "cm5_pid_262080_healthy": cm5,
        "new_sg1_simulators": sg1_sims,
    }


def launch_pair3() -> dict[str, int]:
    pids: dict[str, int] = {}
    for variant, overlay in OVERLAYS.items():
        log = ROOT / f"pair3_{variant.lower()}_bicg.launcher.log"
        cmd = [
            "setsid", "nice", "-n", "5", "python3", str(RUNNER), "run",
            "--authority", str(AUTHORITY), "--workload", "BICG", "--variant", variant,
            "--runs-root", str(ROOT), "--base-config", str(BASE), "--overlay", str(overlay),
            "--trace-config", str(TRACE), "--simulator", str(SIMULATOR),
            "--core-source-head", CORE,
        ]
        with log.open("w", encoding="utf-8") as out:
            pids[variant] = subprocess.Popen(cmd, cwd=FRAMEWORK, stdout=out, stderr=subprocess.STDOUT).pid
    return pids


def write(state: dict[str, object]) -> None:
    MARKER.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    if MARKER.exists():
        raise SystemExit(f"refusing duplicate controller execution: {MARKER}")
    while True:
        exits = {variant: terminal_exit(path) for variant, path in PAIR2.items()}
        if all(exit_code is not None for exit_code in exits.values()):
            break
        time.sleep(30)
    state: dict[str, object] = {"controller": "SG1_PAIR2_TO_PAIR3", "pair2_exits": exits, "terminal_utc": utc()}
    if any(exit_code != 0 for exit_code in exits.values()):
        state["status"] = "STOP_PAIR2_NONZERO_EXIT"
        write(state)
        raise SystemExit(1)
    try:
        state["pair2_strict_validation"] = validate_pair2()
    except subprocess.CalledProcessError as error:
        state["status"] = "STOP_PAIR2_STRICT_VALIDATION_FAILED"
        state["validation_output"] = error.output
        write(state)
        raise SystemExit(1)
    state["pair3_admission"] = admission()
    if not state["pair3_admission"]["pass"]:
        state["status"] = "STOP_PAIR3_RESOURCE_GATE_FAILED"
        write(state)
        raise SystemExit(1)
    state["pair3_launcher_pids"] = launch_pair3()
    state["status"] = "PAIR3_LAUNCHED"
    state["launch_utc"] = utc()
    write(state)


if __name__ == "__main__":
    main()
