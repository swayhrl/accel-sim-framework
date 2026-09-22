#!/usr/bin/env python3
"""Fail-closed validator for one C16WARP1 P5 artifact."""
import argparse
import hashlib
import json
import re
import struct
from pathlib import Path

HEADER = struct.Struct("<8sIIQQQ")
RECORD = struct.Struct("<6I32Q")
TERMINAL = re.compile(r"C16_WARP_TERMINAL static=(\d+) occurrence=(\d+) records=(\d+) overflow=(\d+)")
ACCOUNTING = re.compile(r"C16_P5_ACCOUNTING producer=(\d+) receiver=(\d+) serialized=(\d+) overflow=(\d+)")
OCCURRENCE_SELECT = re.compile(r"C16_TARGET_OCCURRENCE observed=(\d+) action=SELECT")
OCCURRENCE_COUNT = re.compile(r"C16_TARGET_OCCURRENCE_COUNT selected=(\d+) observed=(\d+)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--trace", required=True, type=Path)
    parser.add_argument("--stdout", required=True, type=Path)
    parser.add_argument("--static-index", required=True, type=int)
    parser.add_argument("--occurrence", required=True, type=int)
    parser.add_argument("--receipt", required=True, type=Path)
    args = parser.parse_args()
    checks = []
    try:
        raw = args.trace.read_bytes()
        if len(raw) < HEADER.size:
            raise ValueError("truncated header")
        magic, static, occurrence, callback, overflow, written = HEADER.unpack_from(raw)
        checks.extend([magic == b"C16WARP1", static == args.static_index,
                       occurrence == args.occurrence, (len(raw) - HEADER.size) % RECORD.size == 0])
        records = (len(raw) - HEADER.size) // RECORD.size
        if not all(checks):
            raise ValueError("header identity or record alignment")
        if any(RECORD.unpack_from(raw, offset)[0] != static for offset in range(HEADER.size, len(raw), RECORD.size)):
            raise ValueError("per-record static identity")
        text = args.stdout.read_text(errors="replace")
        terminals = TERMINAL.findall(text)
        accounting = ACCOUNTING.findall(text)
        selected = OCCURRENCE_SELECT.findall(text)
        occurrence_counts = OCCURRENCE_COUNT.findall(text)
        if len(terminals) != 1 or len(accounting) != 1:
            raise ValueError("missing or non-unique terminal/accounting")
        if selected != [str(args.occurrence)] or occurrence_counts != [(str(args.occurrence), str(args.occurrence + 1))]:
            raise ValueError("target occurrence gate")
        ts, to, tr, tv = map(int, terminals[0])
        producer, receiver, serialized, ao = map(int, accounting[0])
        if (ts, to, tr, tv) != (static, occurrence, records, 0):
            raise ValueError("terminal mismatch")
        if overflow != 0 or ao != 0:
            raise ValueError("overflow")
        if not (callback == written == records == producer == receiver == serialized):
            raise ValueError("producer/receiver/serializer closure")
        result = {"status": "PASS", "trace": str(args.trace), "trace_sha256": hashlib.sha256(raw).hexdigest(),
                  "static_index": static, "occurrence": occurrence, "callback_records": callback,
                  "records_written": written, "record_count": records, "overflow": overflow,
                  "terminal": terminals[0], "accounting": accounting[0]}
    except Exception as error:
        result = {"status": "REJECT", "reason": str(error), "trace": str(args.trace)}
    args.receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"])
    raise SystemExit(0 if result["status"] == "PASS" else 2)


if __name__ == "__main__":
    main()
