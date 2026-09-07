#!/usr/bin/env python3
"""Exact, offline M4C locality/footprint analysis of immutable traceg inputs."""

from __future__ import annotations

import argparse
import csv
import hashlib
import os
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


def durable_rows(path: Path, rows: list[list[object]], mode: str) -> None:
    """Write CSV rows durably; used to make kernel checkpoints recoverable."""
    with path.open(mode, newline="") as destination:
        csv.writer(destination, delimiter="\t", lineterminator="\n").writerows(rows)
        destination.flush()
        os.fsync(destination.fileno())


def read_rows(path: Path) -> list[list[str]]:
    with path.open(newline="") as source:
        return list(csv.reader(source, delimiter="\t"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--roi", choices=("prefill", "decode1"), required=True)
    parser.add_argument("--trace-list", type=Path, required=True)
    parser.add_argument("--trace-dir", type=Path, required=True)
    parser.add_argument("--object-map", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--work-db", type=Path, required=True)
    parser.add_argument("--max-kernels", type=int, default=0)
    parser.add_argument("--resume", action="store_true",
                        help="resume only from a verified complete output/SQLite prefix")
    args = parser.parse_args()
    if args.max_kernels < 0:
        raise SystemExit("FAIL: max-kernels must be nonnegative")
    if args.resume:
        if not args.output.is_file() or not args.work_db.is_file():
            raise SystemExit("FAIL: resume requires existing output and work-db")
    elif args.output.exists() or args.work_db.exists():
        raise SystemExit("FAIL: output/work-db must be fresh")
    all_names = [line.strip() for line in args.trace_list.read_text().splitlines() if line.strip()]
    if not all_names:
        raise SystemExit("FAIL: selected trace list is empty")
    ranges, starts = object_map(args.object_map)
    provenance = [args.roi, digest(args.trace_list), digest(args.object_map)]
    header = ["roi", "trace_list_sha256", "object_map_sha256", "semantic_kernel_index",
              "trace_filename", "trace_sha256", "object_class", "row_kind",
              "memory_instructions", "lane_references", "requested_bytes",
              "unique_128b_lines", "unique_32b_sectors", "unique_64kb_pages",
              "unique_2mb_pages", "line_access_max", "line_access_p50",
              "line_access_p90", "line_access_p99", "prior_kernel_line_overlap"]
    start_index = 0
    pending = args.output.with_name(args.output.name + ".pending")
    args.work_db.parent.mkdir(parents=True, exist_ok=True)
    if args.resume:
        connection = sqlite3.connect(str(args.work_db))
        try:
            committed = [row[0] for row in connection.execute(
                "SELECT kernel_index FROM completed_kernel ORDER BY kernel_index")]
        except sqlite3.OperationalError as error:
            raise SystemExit("FAIL: resume requires durable completed_kernel checkpoint schema") from error
        if committed != list(range(len(committed))):
            raise SystemExit("FAIL: unsafe completed_kernel checkpoint sequence")
        completed = len(committed) - 1
        rows = read_rows(args.output)
        if not rows or rows[0] != header:
            raise SystemExit("FAIL: resume output header mismatch")
        data = rows[1:]
        if pending.exists():
            journal = read_rows(pending)
            if len(journal) != 3 or any(len(row) != len(header) for row in journal):
                raise SystemExit("FAIL: malformed pending locality journal")
            try:
                journal_index = int(journal[0][3])
            except ValueError as error:
                raise SystemExit("FAIL: malformed pending locality journal index") from error
            if any(row[3] != str(journal_index) for row in journal):
                raise SystemExit("FAIL: mixed pending locality journal index")
            # Remove any interrupted append before reconciling the durable journal.
            data = [row for row in data if int(row[3]) < journal_index]
            if journal_index <= completed:
                data.extend(journal)
            elif journal_index != completed + 1:
                raise SystemExit("FAIL: pending journal/checkpoint discontinuity")
            durable_rows(args.output, [header, *data], "w")
            pending.unlink()
        expected_rows = (completed + 1) * 3
        if len(data) != expected_rows:
            raise SystemExit("FAIL: resume TSV/checkpoint length mismatch")
        classes = {"WEIGHT", "KV_CACHE", "UNKNOWN"}
        by_index: dict[int, set[str]] = {}
        prior_counts = Counter()
        for values in data:
            if values[:3] != provenance:
                raise SystemExit("FAIL: resume output provenance mismatch")
            try:
                index = int(values[3])
                unique = int(values[11])
                overlap = int(values[19])
            except (IndexError, ValueError) as error:
                raise SystemExit(f"FAIL: malformed resume row: {error}") from error
            kind = values[6] if len(values) > 6 else ""
            if index < 0 or index >= len(all_names) or kind not in classes:
                raise SystemExit("FAIL: unsafe resume row identity")
            if kind in by_index.setdefault(index, set()):
                raise SystemExit("FAIL: duplicate resume object row")
            by_index[index].add(kind)
            prior_counts[kind] += unique - overlap
        if set(by_index) != set(range(completed + 1)) or any(
                values != classes for values in by_index.values()):
            raise SystemExit("FAIL: resume output is not a complete kernel prefix")
        for kind in classes:
            actual = connection.execute(
                "SELECT COUNT(*) FROM prior WHERE kind = ?", (kind,)).fetchone()[0]
            if actual != prior_counts[kind]:
                raise SystemExit(f"FAIL: resume SQLite/output mismatch for {kind}")
        start_index = completed + 1
        if start_index >= len(all_names):
            raise SystemExit("FAIL: resume prefix already covers all kernels")
    else:
        connection = sqlite3.connect(str(args.work_db))
        connection.execute("CREATE TABLE prior (kind TEXT, line INTEGER, PRIMARY KEY(kind,line))")
        connection.execute("CREATE TABLE current (kind TEXT, line INTEGER, PRIMARY KEY(kind,line))")
        connection.execute("CREATE TABLE completed_kernel (kernel_index INTEGER PRIMARY KEY)")
        durable_rows(args.output, [header], "w")
    names = all_names[start_index:]
    if args.max_kernels:
        names = names[:args.max_kernels]
    if not names:
        raise SystemExit("FAIL: selected trace range is empty")
    for kernel_index, name in enumerate(names, start_index):
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
            kernel_rows: list[list[object]] = []
            for kind, item in metrics.items():
                connection.execute("DELETE FROM current")
                connection.executemany("INSERT INTO current VALUES (?,?)",
                                       ((kind, line) for line in item["lines"]))
                overlap = connection.execute(
                    "SELECT COUNT(*) FROM current JOIN prior USING(kind,line)").fetchone()[0]
                connection.execute("INSERT OR IGNORE INTO prior SELECT kind,line FROM current")
                frequencies = list(item["hot"].values())
                kernel_rows.append([
                    *provenance, kernel_index, name, trace_sha, kind, "FOOTPRINT",
                    item["inst"], item["lanes"], item["bytes"], len(item["lines"]),
                    len(item["sectors"]), len(item["pages64"]), len(item["pages2"]),
                    max(frequencies, default=0), quantile(frequencies, .50),
                    quantile(frequencies, .90), quantile(frequencies, .99), overlap,
                ])
            # Journal before checkpointing: a terminated run can always reconcile
            # the durable TSV and the SQLite prior set without guessing.
            durable_rows(pending, kernel_rows, "w")
            connection.execute("INSERT INTO completed_kernel VALUES (?)", (kernel_index,))
            connection.commit()
            durable_rows(args.output, kernel_rows, "a")
            pending.unlink()
            print(f"offline-locality kernel={kernel_index} trace={name}", flush=True)
    connection.close()
    print("PASS trace_locality=" + str(args.output))


if __name__ == "__main__":
    main()
