#!/usr/bin/env python3
"""Capture a compact, read-only post-C3 resource-release snapshot."""

from __future__ import annotations

import argparse
import os
import time
from pathlib import Path


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def meminfo() -> dict[str, int]:
    result: dict[str, int] = {}
    for line in Path("/proc/meminfo").read_text().splitlines():
        key, value, *_ = line.replace(":", "").split()
        result[key] = int(value) * 1024
    return result


def vmstat() -> dict[str, int]:
    fields = Path("/proc/vmstat").read_text().split()
    return {fields[index]: int(fields[index + 1]) for index in range(0, len(fields), 2)}


def cpu_totals() -> tuple[int, int, int]:
    parts = Path("/proc/stat").read_text().splitlines()[0].split()
    values = [int(value) for value in parts[1:]]
    total = sum(values)
    idle = values[3] + (values[4] if len(values) > 4 else 0)
    iowait = values[4] if len(values) > 4 else 0
    return total, idle, iowait


def c3_simulator_processes(c3_root: Path) -> list[str]:
    """Return live C3 simulator/supervisor processes, not ordinary analyzers."""
    matches: list[str] = []
    root = str(c3_root)
    for proc in Path("/proc").glob("[0-9]*"):
        try:
            command = (proc / "cmdline").read_bytes().replace(b"\0", b" ").decode()
        except (FileNotFoundError, PermissionError, UnicodeDecodeError):
            continue
        if root not in command:
            continue
        if any(token in command for token in ("gpgpu-sim", "run_m4c", "run_simulations.py")):
            matches.append(f"{proc.name}:{command}")
    return sorted(matches)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--c3-root", type=Path, required=True)
    parser.add_argument("--interval-seconds", type=float, default=10.0)
    args = parser.parse_args()
    if args.output.exists():
        fail(f"refusing to overwrite snapshot: {args.output}")
    if args.interval_seconds <= 0:
        fail("interval must be positive")

    before_mem = meminfo()
    before_vm = vmstat()
    before_cpu = cpu_totals()
    before_c3 = c3_simulator_processes(args.c3_root)
    time.sleep(args.interval_seconds)
    after_mem = meminfo()
    after_vm = vmstat()
    after_cpu = cpu_totals()
    after_c3 = c3_simulator_processes(args.c3_root)

    total_delta = after_cpu[0] - before_cpu[0]
    idle_delta = after_cpu[1] - before_cpu[1]
    iowait_delta = after_cpu[2] - before_cpu[2]
    if total_delta <= 0:
        fail("non-positive CPU sampling interval")
    rows = [
        ("captured_at_utc", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "timestamp"),
        ("sample_interval_seconds", f"{args.interval_seconds:.3f}", "seconds"),
        ("MemAvailable", str(after_mem["MemAvailable"]), "bytes"),
        ("SwapFree", str(after_mem["SwapFree"]), "bytes"),
        ("pswpin_delta", str(after_vm.get("pswpin", 0) - before_vm.get("pswpin", 0)), "pages"),
        ("pswpout_delta", str(after_vm.get("pswpout", 0) - before_vm.get("pswpout", 0)), "pages"),
        ("cpu_idle_fraction", f"{idle_delta / total_delta:.9f}", "fraction"),
        ("cpu_iowait_fraction", f"{iowait_delta / total_delta:.9f}", "fraction"),
        ("c3_simulator_processes_before", str(len(before_c3)), "count"),
        ("c3_simulator_processes_after", str(len(after_c3)), "count"),
        ("c3_heavy_resources_released", "PASS" if not before_c3 and not after_c3 else "FAIL", "C3-only assertion"),
    ]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as output:
        output.write("field\tvalue\tunit_or_scope\n")
        for field, value, unit in rows:
            output.write(f"{field}\t{value}\t{unit}\n")
    print(f"PASS resource_snapshot={args.output}")


if __name__ == "__main__":
    main()
