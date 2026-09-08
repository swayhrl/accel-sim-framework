#!/usr/bin/env python3
"""Run one resumable M4C locality analyzer under the bounded host-pressure gate.

This utility is intentionally separate from an already-running supervisor.  It
does not change a simulator, a C3 artifact, or an analyzer result; it only
decides when a *future* resumable offline-locality child may start or be
paused.  The child itself is the exact disk-backed analyzer and always uses
``--resume``.

Policy (M4C C4 final locality): launch only in a GREEN ten-second observation
window.  Once running, tolerate GREEN and YELLOW windows.  Terminate a child
only after two consecutive RED windows, avoiding the former ``pswpout > 0``
false-positive rule.  A normal analyzer exit is never relabelled as success:
the caller must still validate complete row coverage.
"""

from __future__ import annotations

import argparse
import os
import re
import signal
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path


MIB = 1024 * 1024


@dataclass(frozen=True)
class Snapshot:
    mem_available: int
    mem_full: float
    io_full: float
    pswpin: int
    pswpout: int
    cpu_total: int
    cpu_iowait: int
    oom_kill: int


@dataclass(frozen=True)
class Window:
    mem_available_gib: float
    mem_full: float
    io_full: float
    swapin_mib_s: float
    swapout_mib_s: float
    iowait_percent: float
    oom_kill_delta: int


def _read_first(pattern: str, path: Path) -> str:
    expression = re.compile(pattern)
    for line in path.read_text().splitlines():
        match = expression.match(line)
        if match:
            return match.group(1)
    raise RuntimeError(f"missing {pattern!r} in {path}")


def snapshot(proc_root: Path = Path("/proc")) -> Snapshot:
    meminfo = proc_root / "meminfo"
    mem_available = int(_read_first(r"^MemAvailable:\s+(\d+)", meminfo)) * 1024
    memory_pressure = proc_root / "pressure" / "memory"
    io_pressure = proc_root / "pressure" / "io"
    mem_full = float(_read_first(r"^full .*avg10=([0-9.]+)", memory_pressure))
    io_full = float(_read_first(r"^full .*avg10=([0-9.]+)", io_pressure))
    vmstat = (proc_root / "vmstat").read_text().splitlines()
    values = dict(line.split(maxsplit=1) for line in vmstat if " " in line)
    stat = (proc_root / "stat").read_text().splitlines()[0].split()
    if stat[0] != "cpu" or len(stat) < 6:
        raise RuntimeError("unexpected /proc/stat aggregate CPU record")
    counters = [int(value) for value in stat[1:]]
    return Snapshot(
        mem_available=mem_available,
        mem_full=mem_full,
        io_full=io_full,
        pswpin=int(values["pswpin"]),
        pswpout=int(values["pswpout"]),
        cpu_total=sum(counters),
        cpu_iowait=counters[4],
        oom_kill=int(values.get("oom_kill", "0")),
    )


def window(before: Snapshot, after: Snapshot, seconds: float, page_size: int) -> Window:
    if seconds <= 0 or after.cpu_total < before.cpu_total:
        raise RuntimeError("non-monotonic resource snapshot")
    total_delta = after.cpu_total - before.cpu_total
    return Window(
        mem_available_gib=after.mem_available / (1024**3),
        mem_full=after.mem_full,
        io_full=after.io_full,
        swapin_mib_s=(after.pswpin - before.pswpin) * page_size / MIB / seconds,
        swapout_mib_s=(after.pswpout - before.pswpout) * page_size / MIB / seconds,
        iowait_percent=(100.0 * (after.cpu_iowait - before.cpu_iowait) / total_delta
                         if total_delta else 0.0),
        oom_kill_delta=after.oom_kill - before.oom_kill,
    )


def is_green(value: Window) -> bool:
    return (value.mem_available_gib >= 16.0 and value.mem_full <= 2.0 and
            value.io_full <= 5.0 and value.iowait_percent <= 20.0 and
            value.swapin_mib_s <= 8.0 and value.swapout_mib_s <= 8.0 and
            value.oom_kill_delta == 0)


def is_red(value: Window) -> bool:
    return (value.mem_available_gib < 8.0 or value.mem_full > 5.0 or
            value.swapin_mib_s > 32.0 or value.swapout_mib_s > 32.0 or
            value.oom_kill_delta > 0)


def render(value: Window) -> str:
    state = "GREEN" if is_green(value) else "RED" if is_red(value) else "YELLOW"
    return (f"state={state} mem_available_gib={value.mem_available_gib:.2f} "
            f"memory_full_avg10={value.mem_full:.2f} io_full_avg10={value.io_full:.2f} "
            f"swapin_mib_s={value.swapin_mib_s:.3f} swapout_mib_s={value.swapout_mib_s:.3f} "
            f"iowait_pct={value.iowait_percent:.3f} oom_kill_delta={value.oom_kill_delta}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--analysis-root", type=Path, required=True)
    parser.add_argument("--roi", required=True)
    parser.add_argument("--trace-list", type=Path, required=True)
    parser.add_argument("--trace-dir", type=Path, required=True)
    parser.add_argument("--object-map", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--work-db", type=Path, required=True)
    parser.add_argument("--max-kernels", type=int, default=10)
    parser.add_argument("--interval-seconds", type=float, default=10.0)
    parser.add_argument("--log", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.interval_seconds <= 0:
        raise SystemExit("--interval-seconds must be positive")
    page_size = os.sysconf("SC_PAGE_SIZE")
    analyzer = args.analysis_root / "util/vm_tlb/analyze_m4c_trace_locality.py"
    if not analyzer.is_file():
        raise SystemExit(f"missing analyzer: {analyzer}")
    args.log.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "python3", str(analyzer), "--roi", args.roi, "--trace-list", str(args.trace_list),
        "--trace-dir", str(args.trace_dir), "--object-map", str(args.object_map),
        "--output", str(args.output), "--work-db", str(args.work_db), "--resume",
        "--max-kernels", str(args.max_kernels),
    ]
    with args.log.open("a", encoding="utf-8") as log:
        while True:
            before = snapshot()
            time.sleep(args.interval_seconds)
            admission = window(before, snapshot(), args.interval_seconds, page_size)
            log.write(f"PREFLIGHT {render(admission)}\n")
            log.flush()
            if not is_green(admission):
                continue
            child = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
            log.write(f"CHILD_START pid={child.pid}\n")
            log.flush()
            previous = snapshot()
            red_windows = 0
            paused_by_policy = False
            while child.poll() is None:
                time.sleep(args.interval_seconds)
                current = snapshot()
                observation = window(previous, current, args.interval_seconds, page_size)
                previous = current
                red_windows = red_windows + 1 if is_red(observation) else 0
                log.write(f"CHILD_WINDOW pid={child.pid} red_windows={red_windows} {render(observation)}\n")
                log.flush()
                if red_windows >= 2:
                    log.write(f"CHILD_PAUSE pid={child.pid} reason=two_consecutive_red_windows\n")
                    log.flush()
                    child.send_signal(signal.SIGTERM)
                    paused_by_policy = True
                    break
            rc = child.wait()
            log.write(f"CHILD_END pid={child.pid} rc={rc}\n")
            log.flush()
            if rc == 0:
                return 0
            if not paused_by_policy:
                return rc


if __name__ == "__main__":
    raise SystemExit(main())
