#!/usr/bin/env python3
"""Classify terminal 2D reserved-line facts into source-followup buckets.

This is deliberately downstream of the immutable V2 observational collector.
It does not diagnose a root cause, choose a repair, or accept a FAST64 result;
it only makes the A/B/C branches in the authorized recovery procedure
mechanical. The queue-path (D) remains unclassified unless a future diagnostic
contains a source-defined outbound-queue record.
"""
from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path

SCHEMA = "FAST64_3_2DCONVOLUTION_BASE_TRANSITION_DIAGNOSTIC_V2"


def fail(message: str) -> None:
    raise RuntimeError(message)


def classify(line: dict) -> tuple[str, str]:
    owner = line.get("owner")
    if line.get("owner_state") == "OWNER_ABSENT" or owner is None:
        return ("B_OWNERLESS_RESERVED_LINE", "investigate ownership loss or premature owner erase against retained tag/MSHR reservation")
    pending = owner.get("pending_read")
    if not isinstance(pending, int) or pending < 0:
        fail("OWNER_PENDING_READ_INVALID")
    if pending > 0:
        return ("A_PENDING_SECTOR_CHILD_RESPONSE", "investigate incomplete sector-child response aggregation")
    return ("C_FINAL_FILL_OR_RETIRE_TRANSITION", "investigate final-fill/MSHR-ready/owner-retire/lower-credit-release transition")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--diagnostic", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        fail("OUTPUT_ALREADY_EXISTS")
    try:
        diagnostic = json.loads(args.diagnostic.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        fail("DIAGNOSTIC_INVALID=" + str(error))
    if diagnostic.get("schema") != SCHEMA or diagnostic.get("classification") != "NONFORMAL_DIAGNOSTIC_NOT_RESULT":
        fail("DIAGNOSTIC_SCHEMA_OR_CLASSIFICATION_INVALID")
    terminal = diagnostic.get("terminal_dump", {})
    if not terminal.get("present"):
        fail("TERMINAL_DEADLOCK_SNAPSHOT_REQUIRED")
    records = []
    for cache, state in sorted(terminal.get("l1d", {}).items()):
        for line in state.get("reserved_lines", []):
            bucket, next_source_audit = classify(line)
            records.append({"cache": cache, "block": line.get("block"), "way": line.get("way"),
                            "owner_state": line.get("owner_state"), "owner": line.get("owner"),
                            "source_followup_bucket": bucket, "source_followup": next_source_audit})
    if not records:
        fail("NO_RESERVED_L1D_LINES_IN_TERMINAL_SNAPSHOT")
    output = {"schema": "FAST64_3_2D_SOURCE_FOLLOWUP_V1",
              "classification": "NONFORMAL_DIAGNOSTIC_SOURCE_FOLLOWUP_ONLY",
              "input_diagnostic": str(args.diagnostic),
              "reserved_line_count": len(records), "reserved_lines": records,
              "queue_path_d_disposition": "UNCLASSIFIED_WITHOUT_SOURCE_DEFINED_OUTBOUND_QUEUE_SNAPSHOT",
              "repair_disposition": "NO_REPAIR_SELECTED", "promotion": "NONE"}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=args.output.parent,
                                     prefix=f".{args.output.name}.", delete=False) as stream:
        temporary = Path(stream.name)
        json.dump(output, stream, indent=2, sort_keys=True); stream.write("\n")
    try:
        os.replace(temporary, args.output)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
    print(f"FAST64_3_2D_SOURCE_FOLLOWUP_V1_CANDIDATE_PASS output={args.output}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError) as error:
        print("FAST64_3_2D_SOURCE_FOLLOWUP_V1_FAIL: " + str(error), file=__import__("sys").stderr)
        raise SystemExit(1)
