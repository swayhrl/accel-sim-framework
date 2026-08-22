#!/usr/bin/env python3
"""Summarize C2P replay wall time, host memory, and trace footprint.

The C2P runner writes host_profile.txt for new runs.  Older directories lack
that file, so their elapsed time is explicitly labelled as the conservative
interval from copied simulator binary to summary.txt.  The latter is useful
for planning but is not a replacement for a measured host profile.
"""

import argparse
import csv
import re
import sys
from pathlib import Path


SIM_TIME_RE = re.compile(r"gpgpu_simulation_time = .*\((\d+) sec\)")
TRACE_SUFFIXES = (".traceg", ".traceg.xz", ".traceg.gz")


def read_key_values(path):
    values = {}
    if not path.is_file():
        return values
    for line in path.read_text(errors="replace").splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def simulator_elapsed_sec(run_out):
    if not run_out.is_file():
        return ""
    for line in run_out.read_text(errors="replace").splitlines():
        match = SIM_TIME_RE.search(line)
        if match:
            return match.group(1)
    return ""


def trace_payload_bytes(run_dir):
    kernels = run_dir / "traces" / "kernelslist.g"
    if not kernels.is_file():
        return ""
    total = 0
    seen = set()
    trace_dir = kernels.resolve().parent
    for line in kernels.read_text(errors="replace").splitlines():
        name = line.strip().split(",", 1)[0]
        if not name.endswith(TRACE_SUFFIXES):
            continue
        candidate = trace_dir / name
        if candidate.is_file() and candidate not in seen:
            total += candidate.stat().st_size
            seen.add(candidate)
    return str(total)


def row_for(summary, root):
    run_dir = summary.parent
    rel = run_dir.relative_to(root)
    mode = rel.parts[-1]
    case = "/".join(rel.parts[:-1])
    values = read_key_values(summary)
    profile = read_key_values(run_dir / "host_profile.txt")
    profile_source = "host_profile" if profile else "legacy_file_mtime_estimate"
    elapsed = profile.get("wall_elapsed_sec", "")
    if not elapsed:
        binary = run_dir / "accel-sim.out"
        if binary.is_file():
            elapsed = f"{summary.stat().st_mtime - binary.stat().st_mtime:.3f}"
    return {
        "case": case,
        "mode": mode,
        "status": "complete",
        "wall_elapsed_sec": elapsed,
        "wall_time_source": profile_source,
        "max_rss_kib": profile.get("max_rss_kib", ""),
        "user_cpu_sec": profile.get("user_cpu_sec", ""),
        "sys_cpu_sec": profile.get("sys_cpu_sec", ""),
        "cpu_percent": profile.get("cpu_percent", ""),
        "exit_status": profile.get("exit_status", ""),
        "simulator_elapsed_sec": simulator_elapsed_sec(run_dir / "run.out"),
        "gpu_tot_sim_cycle": values.get("gpu_tot_sim_cycle", ""),
        "gpu_sim_insn": values.get("gpu_sim_insn", ""),
        "trace_payload_bytes": trace_payload_bytes(run_dir),
        "run_dir": str(run_dir),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="campaign result root")
    parser.add_argument("--format", choices=("csv", "markdown"), default="csv")
    parser.add_argument("--output", type=Path, help="write instead of stdout")
    args = parser.parse_args()

    root = args.root.resolve()
    rows = [row_for(path, root) for path in sorted(root.glob("**/summary.txt"))]
    fields = list(rows[0]) if rows else [
        "case", "mode", "status", "wall_elapsed_sec", "wall_time_source",
        "max_rss_kib", "user_cpu_sec", "sys_cpu_sec", "cpu_percent",
        "exit_status", "simulator_elapsed_sec", "gpu_tot_sim_cycle",
        "gpu_sim_insn", "trace_payload_bytes", "run_dir",
    ]
    stream = args.output.open("w", newline="") if args.output else sys.stdout
    try:
        if args.format == "csv":
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
        else:
            stream.write("# C2P replay resource summary\n\n")
            stream.write("`host_profile` is an exact runner measurement. "
                         "`legacy_file_mtime_estimate` is only a planning estimate.\n\n")
            columns = ["case", "mode", "wall_elapsed_sec", "wall_time_source",
                       "max_rss_kib", "simulator_elapsed_sec", "trace_payload_bytes"]
            stream.write("| " + " | ".join(columns) + " |\n")
            stream.write("|" + "|".join("---" for _ in columns) + "|\n")
            for row in rows:
                stream.write("| " + " | ".join(row[column] for column in columns) + " |\n")
    finally:
        if args.output:
            stream.close()


if __name__ == "__main__":
    main()
