#!/usr/bin/env python3
"""Require an exact behavioral-stat log match for M4C telemetry OFF vs ON."""

import argparse
import hashlib
from pathlib import Path


def canonical(path: Path) -> bytes:
    lines = path.read_text(errors="strict").splitlines()
    try:
        begin = next(i for i, line in enumerate(lines)
                     if line.startswith("Processing kernel "))
    except StopIteration as exc:
        raise SystemExit(f"{path}: missing trace-processing marker") from exc
    kept = []
    for line in lines[begin:]:
        if line.startswith("m4c_telemetry"):
            continue
        if line.startswith("-gpgpu_memory_telemetry_level"):
            continue
        if line.startswith("gpu_total_sim_rate="):
            continue
        if line.startswith("WALL_SECONDS="):
            continue
        if line.startswith("gpgpu_simulation_time ="):
            continue
        if line.startswith("gpgpu_simulation_rate ="):
            continue
        if line.startswith("gpgpu_silicon_slowdown ="):
            continue
        # Each isolated run directory owns a symlink to the same immutable
        # trace.  The directory name is provenance, not simulator behavior;
        # retain the trace basename so a different trace would still fail the
        # comparison while ON/OFF directory spelling cannot mask equivalence.
        if line.startswith("Processing kernel "):
            line = "Processing kernel " + Path(line[len("Processing kernel "):]).name
        elif line.startswith("Header info loaded for kernel command : "):
            prefix = "Header info loaded for kernel command : "
            line = prefix + Path(line[len(prefix):]).name
        elif line.startswith("-trace "):
            # The isolated scratch list has identical contents but a distinct
            # run-directory pathname in the two arms.
            line = "-trace <isolated-selected-list>"
        kept.append(line)
    return ("\n".join(kept) + "\n").encode()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--off", required=True, type=Path)
    parser.add_argument("--on", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    off = canonical(args.off)
    on = canonical(args.on)
    if off != on:
        raise SystemExit("FAIL: telemetry changed a simulator behavioral-stat log")
    digest = hashlib.sha256(off).hexdigest()
    args.output.write_text(
        "# M4C telemetry behavior-neutrality validation\n"
        "Status: PASS\n\n"
        "The canonical post-trace simulator logs are byte-identical after only "
        "removing telemetry records and host-time-derived rate fields.  Thus "
        "cycles, instructions, IPC, architectural cache/memory/TLB counters, "
        "PTE conservation, and printed execution order are identical.\n\n"
        f"- telemetry OFF log: `{args.off}`\n"
        f"- telemetry ON log: `{args.on}`\n"
        f"- canonical behavioral-stat SHA256: `{digest}`\n"
    )
    print(f"PASS canonical_behavioral_stat_sha256={digest}")


if __name__ == "__main__":
    main()
