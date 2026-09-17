#!/usr/bin/env python3
"""Fail-closed local audit for a V20 C16WARP1 static-MREF shard set."""
import argparse
import csv
import hashlib
import json
import struct
import sys
from pathlib import Path

MAGIC = b"C16WARP1"
HEADER = struct.Struct("<8sIIQQQ")
RECORD_BYTES = 280


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_ranges(context: dict):
    """Collect tensor ranges from both isolated and full-layer contexts."""
    out = []
    def walk(value, path=""):
        if isinstance(value, dict):
            ptr = value.get("ptr", value.get("data_ptr"))
            size = value.get("bytes", value.get("nbytes"))
            if ptr is not None and size is not None:
                try:
                    start = int(ptr, 16) if isinstance(ptr, str) else int(ptr)
                    size = int(size)
                except (TypeError, ValueError) as e:
                    raise ValueError(f"ADDRESS_CONTEXT invalid range at {path}: {e}")
                if size <= 0:
                    raise ValueError(f"ADDRESS_CONTEXT invalid range at {path}")
                category = path.rsplit(".", 1)[-1]
                out.append((category, start, start + size))
            for key, child in value.items():
                walk(child, f"{path}.{key}" if path else str(key))
        elif isinstance(value, list):
            for index, child in enumerate(value):
                walk(child, f"{path}[{index}]")
    walk(context)
    if not out:
        raise ValueError("ADDRESS_CONTEXT contains no tensor ranges")
    return out


def record_range_counts(trace: Path, ranges):
    data = trace.read_bytes()
    if len(data) < HEADER.size:
        raise ValueError("trace shorter than C16WARP1 header")
    magic, static, occ, count, overflow, keep = HEADER.unpack_from(data)
    if magic != MAGIC:
        raise ValueError("unexpected trace magic")
    if overflow != 0 or count != keep:
        raise ValueError(f"non-closed trace count={count} keep={keep} overflow={overflow}")
    expected_size = HEADER.size + keep * RECORD_BYTES
    if len(data) != expected_size:
        raise ValueError(f"trace size {len(data)} != expected {expected_size}")
    joined = {label: 0 for label, _, _ in ranges}
    # WRec begins with six uint32s then its 32 uint64 address lanes.
    for rec_off in range(HEADER.size, len(data), RECORD_BYTES):
        active_mask = struct.unpack_from("<I", data, rec_off + 4)[0]
        for lane in range(32):
            if not (active_mask & (1 << lane)):
                continue
            address = struct.unpack_from("<Q", data, rec_off + 24 + 8 * lane)[0]
            for label, start, end in ranges:
                if start <= address < end:
                    joined[label] += 1
                    break
    return static, occ, count, overflow, joined


def fail(message: str):
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--static-map", required=True, type=Path)
    ap.add_argument("--shard-root", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--expected-occurrence", required=True, type=int)
    args = ap.parse_args()

    with args.static_map.open(newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    expected = {
        int(row["nvbit_static_index"])
        for row in rows
        if row.get("memory_space") == "GLOBAL" and row.get("has_mref") == "1"
    }
    if not expected:
        fail("static map has no GLOBAL MREF entries")
    present = {
        int(p.name.split("_", 1)[1])
        for p in args.shard_root.glob("mref_*")
        if p.is_dir() and p.name.split("_", 1)[1].isdigit()
    }
    if present != expected:
        fail(f"static set mismatch missing={sorted(expected-present)} unexpected={sorted(present-expected)}")

    results = []
    for index in sorted(expected):
        shard = args.shard_root / f"mref_{index}"
        trace = shard / "trace.bin"
        stdout = shard / "stdout.log"
        context_path = shard / "ADDRESS_CONTEXT.json"
        for path in (trace, stdout, context_path):
            if not path.is_file() or path.is_symlink():
                fail(f"static {index}: missing or symlinked {path.name}")
        terminal = f"C16_WARP_TERMINAL static={index} occurrence={args.expected_occurrence}"
        if terminal not in stdout.read_text(errors="replace"):
            fail(f"static {index}: no exact terminal-close receipt")
        try:
            context = json.loads(context_path.read_text())
            ranges = parse_ranges(context)
            static, occ, count, overflow, joined = record_range_counts(trace, ranges)
        except (ValueError, OSError, json.JSONDecodeError) as e:
            fail(f"static {index}: {e}")
        if static != index or occ != args.expected_occurrence:
            fail(f"static {index}: header selector static={static} occurrence={occ}")
        results.append({
            "static_index": index,
            "terminal_status": "EXECUTED_SHARD" if count else "ZERO_EXECUTION_PROVEN",
            "record_count": count,
            "overflow": overflow,
            "address_context_sha256": sha256(context_path),
            "trace_sha256": sha256(trace),
            "same_process_address_hits_by_semantic_role": joined,
        })
    payload = {
        "format": "C16WARP1",
        "record_bytes": RECORD_BYTES,
        "expected_static_global_mref_count": len(expected),
        "present_static_global_mref_count": len(present),
        "complete_set": True,
        "shards": results,
        "notes": [
            "Each shard is independently replayed and classified; no cross-replay VA union is made.",
            "ZERO_EXECUTION_PROVEN requires exact selector and terminal-close receipt; lifecycle-positive controls are recorded separately.",
        ],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "PASS", "shards": len(results)}, sort_keys=True))


if __name__ == "__main__":
    main()
