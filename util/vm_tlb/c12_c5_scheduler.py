#!/usr/bin/env python3
"""Non-semantic admission controller for the frozen C12 22-point matrix.

This supervisor deliberately delegates every actual launch and validation to
``c12_c5_replay.py``.  It never changes an experiment input and never signals a
simulator.  Its only purpose is to fill a safely available C12 worker slot with
the next arm in the already-authorized P1/P2/P3 order.
"""

from __future__ import annotations

import csv
import fcntl
import json
import os
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path("/workspace/vm-m4b-speculative")
RESULT_ROOT = ROOT / "c5-results/C11_AUTHORIZED_NOT_RUN"
RESOURCE = ROOT / "c12/RESOURCE_HISTORY_V3_TRUE_SIM.tsv"
LOCK = ROOT / "c12/C12_SCHEDULER.lock"
STATE = ROOT / "c12/C12_SCHEDULER_STATE.tsv"
REPLAY = Path(__file__).with_name("c12_c5_replay.py")

# P0/P1 arms may already be active when the scheduler starts.  This list is
# exactly the remaining C12 primary matrix priority, not a new experiment plan.
QUEUE = [
    ("decode1", "F8", "10"), ("prefill", "F8", "10"),
    ("decode1", "F9", "NONE"), ("prefill", "F9", "NONE"),
    ("decode1", "F7", "5"), ("prefill", "F7", "5"),
    ("decode1", "F7", "20"), ("prefill", "F7", "20"),
    ("decode1", "F8", "5"), ("prefill", "F8", "5"),
    ("decode1", "F8", "20"), ("prefill", "F8", "20"),
    ("decode1", "F1", "NONE"), ("prefill", "F1", "NONE"),
]


def arm_dir(roi: str, arm: str, lseg: str) -> Path:
    name = arm.lower() if lseg == "NONE" else arm.lower() + "_lseg" + lseg
    return RESULT_ROOT / roi / name


def actual_sims() -> int:
    count = 0
    for proc in Path("/proc").iterdir():
        if not proc.name.isdigit():
            continue
        try:
            if Path(os.readlink(proc / "exe")).name != "accel-sim.out":
                continue
            command = (proc / "cmdline").read_bytes().replace(b"\0", b" ").decode(errors="ignore")
        except OSError:
            continue
        if str(RESULT_ROOT) in command:
            count += 1
    return count


def latest_resource() -> dict[str, str]:
    if not RESOURCE.is_file():
        return {}
    with RESOURCE.open(newline="") as source:
        rows = list(csv.DictReader(source, delimiter="\t"))
    return rows[-1] if rows else {}


def admission_target() -> int:
    row = latest_resource()
    try:
        # C12's ordinary GREEN gate is sufficient to keep six independent
        # workers busy.  The addendum reserves the stronger memory/CPU gate
        # for *raising* (or refilling) the batch to eight.  SwapFree remains
        # informational: observed swap activity, not free swap capacity, is
        # the scheduling signal.
        green = (int(row["mem_available_kb"]) >= 32 * 1024 * 1024 and
                 float(row["memory_psi_full_avg10"]) <= 1.0 and
                 float(row["io_psi_full_avg10"]) <= 2.0 and
                 float(row["swap_in_mib_s"]) <= 4.0 and
                 float(row["swap_out_mib_s"]) <= 4.0 and
                 float(row["cpu_iowait_pct"]) <= 10.0)
        if not green:
            return 0
        eight_way = (int(row["mem_available_kb"]) >= 64 * 1024 * 1024 and
                     float(row["loadavg_1"]) <= 0.95 * os.cpu_count())
        return 8 if eight_way else 6
    except (KeyError, TypeError, ValueError):
        return 0


def state(rows: list[dict[str, str]]) -> None:
    STATE.parent.mkdir(parents=True, exist_ok=True)
    temporary = STATE.with_name(STATE.name + ".tmp." + str(os.getpid()))
    fields = ("roi", "arm", "lseg", "run_dir", "state", "child_pid", "exit_code")
    with temporary.open("w", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    os.replace(temporary, STATE)


def main() -> int:
    if os.cpu_count() is None:
        raise SystemExit("cannot determine host CPU count")
    LOCK.parent.mkdir(parents=True, exist_ok=True)
    with LOCK.open("a+") as handle:
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise SystemExit("C12 scheduler lock is already held")
        arguments = sys.argv[1:]
        children: dict[tuple[str, str, str], subprocess.Popen[bytes]] = {}
        while True:
            live: list[dict[str, str]] = []
            for point, child in list(children.items()):
                code = child.poll()
                roi, arm, lseg = point
                live.append({"roi": roi, "arm": arm, "lseg": lseg,
                             "run_dir": str(arm_dir(*point)),
                             "state": "RUNNING" if code is None else "CHILD_EXITED",
                             "child_pid": str(child.pid), "exit_code": "" if code is None else str(code)})
                if code is not None:
                    del children[point]
            used = actual_sims()
            target = admission_target()
            for point in QUEUE:
                if used >= target:
                    break
                if point in children:
                    continue
                directory = arm_dir(*point)
                if directory.exists():
                    # A real output directory is owned by an earlier attempt
                    # or completed arm; never overwrite it from a scheduler.
                    continue
                command = [sys.executable, str(REPLAY), *arguments, "--execute",
                           "--point", ":".join(point)]
                children[point] = subprocess.Popen(command)
                used += 1  # reserve admission while trace links are prepared
            state(live)
            if not children and all((arm_dir(*point) / "C12_ARM_VALIDATION.json").is_file()
                                    for point in QUEUE) and actual_sims() == 0:
                return 0
            time.sleep(15)


if __name__ == "__main__":
    raise SystemExit(main())
