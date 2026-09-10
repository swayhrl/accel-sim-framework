#!/usr/bin/env python3
"""Parse only the post-deadlock DTC resource state of a nonformal replay."""

import argparse
import json
import pathlib
import re

IO = re.compile(
    r"^DTC_L1_IO_DEADLOCK sm=(?P<sm>\d+) pib=(?P<pib>\d+) "
    r"frontend=(?P<frontend>\d+) head_uid=(?P<head_uid>\d+) "
    r"head_ready=(?P<head_ready>[01]) free_phys=(?P<free_phys>\d+) "
    r"allocated_phys=(?P<allocated_phys>\d+) partial_entries=(?P<partial_entries>\d+) "
    r"partial_lines_held=(?P<partial_lines_held>\d+) lower_create=(?P<lower_create>\d+) "
    r"lower_issue=(?P<lower_issue>\d+) inflight=(?P<inflight>\d+) "
    r"last_progress_cycle=(?P<last_progress_cycle>\d+)$"
)
OO = re.compile(
    r"^DTC_L1_OO_DEADLOCK sm=(?P<sm>\d+) pib=(?P<pib>\d+) "
    r"frontend=(?P<frontend>\d+) allocated_phys=(?P<allocated_phys>\d+) "
    r"active_refs=(?P<active_refs>\d+) lower_create=(?P<lower_create>\d+) "
    r"lower_issue=(?P<lower_issue>\d+) inflight=(?P<inflight>\d+)$"
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=pathlib.Path, required=True)
    parser.add_argument("--mode", choices=("IO", "OO"), required=True)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    args = parser.parse_args()
    if not args.input.is_file() or args.output.exists():
        raise ValueError("input missing or output already exists")
    matcher = IO if args.mode == "IO" else OO
    rows = []
    for line in args.input.read_text(encoding="utf-8", errors="replace").splitlines():
        match = matcher.match(line)
        if match:
            rows.append({key: int(value) for key, value in match.groupdict().items()})
    if not rows:
        raise ValueError("no mode-matching post-deadlock DTC resource state")
    result = {
        "schema": "FAST64_6_PHYSICAL16P5_DIAGNOSTIC_V1",
        "classification": "NONFORMAL_DIAGNOSTIC_NOT_RESULT",
        "mode": args.mode,
        "resource_state": rows,
        "interpretation": (
            "OBSERVATION_ONLY: IO may be compared to its frozen partial-allocation "
            "invariant; OO state must not be assigned IO FIFO semantics. This output "
            "does not promote a sensitivity result or select a Core repair."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temp = args.output.with_name(args.output.name + ".tmp")
    if temp.exists():
        raise ValueError("temporary output exists")
    temp.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temp.replace(args.output)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as error:
        raise SystemExit(f"FAST64_6_PHYSICAL16P5_DIAG_ANALYZE_FAIL: {error}")
