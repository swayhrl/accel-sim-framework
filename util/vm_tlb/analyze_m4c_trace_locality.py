#!/usr/bin/env python3
"""Exact, offline M4C locality/footprint analysis of immutable traceg inputs."""

from __future__ import annotations

import argparse
import csv
import hashlib
import sqlite3
import sys
from bisect import bisect_right
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "util" / "llm_trace_capture"))
from analyze_trace_address_coverage import decode  # exact frozen-trace decoder


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def object_map(path: Path) -> tuple[list[tuple[int, int, str]], list[int]]:
    ranges: list[tuple[int, int, str]] = []
    for raw in path.read_text().splitlines():
        fields = raw.split("\t")
        if len(fields) == 4 and fields[0] == "range":
            kind, start, end = fields[1:]
            if kind not in ("WEIGHT", "KV_CACHE"):
                raise ValueError(f"unknown object kind: {kind}")
            ranges.append((int(start, 0), int(end, 0), kind))
    if not ranges:
        raise ValueError("object map contains no ranges")
    ranges.sort()
    for (_, previous_end, _), (start, _, _) in zip(ranges, ranges[1:]):
        if previous_end >= start:
            raise ValueError("object-map ranges overlap")
    return ranges, [entry[0] for entry in ranges]


def classify(address: int, width: int, ranges: list[tuple[int, int, str]], starts: list[int]) -> str:
    index = bisect_right(starts, address) - 1
    if index >= 0:
        begin, end, kind = ranges[index]
        if begin <= address and address + width - 1 <= end:
            return kind
        if address <= end and address + width - 1 >= begin:
            return "UNKNOWN"
    if index + 1 < len(ranges):
        begin, end, _ = ranges[index + 1]
        if address <= end and address + width - 1 >= begin:
            return "UNKNOWN"
    return "UNKNOWN"


def quantile(values: list[int], fraction: float) -> int:
    if not values:
        return 0
    values.sort()
    return values[min(len(values) - 1, int((len(values) - 1) * fraction))]


def add_range(target: set[int], address: int, width: int, unit: int) -> None:
    for value in range(address // unit, (address + width - 1) // unit + 1):
        target.add(value)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--roi", choices=("prefill", "decode1"), required=True)
    parser.add_argument("--trace-list", type=Path, required=True)
    parser.add_argument("--trace-dir", type=Path, required=True)
    parser.add_argument("--object-map", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--work-db", type=Path, required=True)
    parser.add_argument("--max-kernels", type=int, default=0)
    args = parser.parse_args()
    if args.max_kernels < 0 or args.output.exists() or args.work_db.exists():
        raise SystemExit("FAIL: output/work-db must be fresh and max-kernels nonnegative")
    names = [line.strip() for line in args.trace_list.read_text().splitlines() if line.strip()]
    if args.max_kernels:
        names = names[:args.max_kernels]
    if not names:
        raise SystemExit("FAIL: selected trace list is empty")
    ranges, starts = object_map(args.object_map)
    args.work_db.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(str(args.work_db))
    connection.execute("CREATE TABLE prior (kind TEXT, line INTEGER, PRIMARY KEY(kind,line))")
    connection.execute("CREATE TABLE current (kind TEXT, line INTEGER, PRIMARY KEY(kind,line))")

    provenance = [args.roi, digest(args.trace_list), digest(args.object_map)]
    header = ["roi", "trace_list_sha256", "object_map_sha256", "semantic_kernel_index",
              "trace_filename", "trace_sha256", "object_class", "row_kind",
              "memory_instructions", "lane_references", "requested_bytes",
              "unique_128b_lines", "unique_32b_sectors", "unique_64kb_pages",
              "unique_2mb_pages", "line_access_max", "line_access_p50",
              "line_access_p90", "line_access_p99", "prior_kernel_line_overlap"]
    with args.output.open("w", newline="") as output:
        writer = csv.writer(output, delimiter="\t", lineterminator="\n")
        writer.writerow(header)
        for kernel_index, name in enumerate(names):
            if Path(name).name != name or not name.endswith(".traceg.xz"):
                raise RuntimeError(f"unsafe trace-list entry: {name}")
            trace = args.trace_dir / name
            if not trace.is_file():
                raise RuntimeError(f"missing immutable trace: {trace}")
            metrics = {kind: {"inst": 0, "lanes": 0, "bytes": 0,
                              "lines": set(), "sectors": set(),
                              "pages64": set(), "pages2": set(),
                              "hot": Counter()}
                       for kind in ("WEIGHT", "KV_CACHE", "UNKNOWN")}
            import lzma
            with lzma.open(trace, "rt", errors="strict") as source:
                for raw in source:
                    try:
                        record = decode(raw)
                    except ValueError as error:
                        raise RuntimeError(f"{trace}: malformed trace record: {error}") from error
                    if record is None or record[1] == 0:
                        continue
                    _, width, addresses, _ = record
                    instruction_classes: set[str] = set()
                    for address in addresses:
                        kind = classify(address, width, ranges, starts)
                        item = metrics[kind]
                        instruction_classes.add(kind)
                        item["lanes"] += 1
                        item["bytes"] += width
                        for line in range(address // 128, (address + width - 1) // 128 + 1):
                            item["lines"].add(line)
                            item["hot"][line] += 1
                        add_range(item["sectors"], address, width, 32)
                        add_range(item["pages64"], address, width, 64 * 1024)
                        add_range(item["pages2"], address, width, 2 * 1024 * 1024)
                    for kind in instruction_classes:
                        metrics[kind]["inst"] += 1
            trace_sha = digest(trace)
            for kind, item in metrics.items():
                connection.execute("DELETE FROM current")
                connection.executemany("INSERT INTO current VALUES (?,?)",
                                       ((kind, line) for line in item["lines"]))
                overlap = connection.execute(
                    "SELECT COUNT(*) FROM current JOIN prior USING(kind,line)").fetchone()[0]
                connection.execute("INSERT OR IGNORE INTO prior SELECT kind,line FROM current")
                connection.commit()
                frequencies = list(item["hot"].values())
                writer.writerow([
                    *provenance, kernel_index, name, trace_sha, kind, "FOOTPRINT",
                    item["inst"], item["lanes"], item["bytes"], len(item["lines"]),
                    len(item["sectors"]), len(item["pages64"]), len(item["pages2"]),
                    max(frequencies, default=0), quantile(frequencies, .50),
                    quantile(frequencies, .90), quantile(frequencies, .99), overlap,
                ])
            print(f"offline-locality kernel={kernel_index} trace={name}", flush=True)
    connection.close()
    print("PASS trace_locality=" + str(args.output))


if __name__ == "__main__":
    main()
