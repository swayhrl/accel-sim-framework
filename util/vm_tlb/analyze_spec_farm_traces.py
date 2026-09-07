#!/usr/bin/env python3
"""Parallel, deterministic offline trace mining for Window-B.

The workers only read immutable ``.traceg.xz`` files.  They emit compressed
per-kernel partials into caller-owned scratch; a single ordered reducer computes
cross-kernel results so parallelism cannot change ROI ordering semantics.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import lzma
import os
import pickle
import sys
from bisect import bisect_right
from collections import Counter, deque
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "util" / "llm_trace_capture"))
from analyze_trace_address_coverage import decode

OBJECTS = ("WEIGHT", "KV_CACHE", "UNKNOWN")
UNITS = {"sectors": 32, "lines": 128, "pages64": 64 * 1024, "pages2": 2 * 1024 * 1024}


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def object_ranges(path: Path) -> tuple[list[tuple[int, int, str]], list[int]]:
    ranges: list[tuple[int, int, str]] = []
    for raw in path.read_text().splitlines():
        fields = raw.split("\t")
        if len(fields) == 4 and fields[0] == "range":
            kind, start, end = fields[1:]
            if kind not in OBJECTS[:2]:
                raise ValueError(f"unsupported object kind {kind}")
            ranges.append((int(start, 0), int(end, 0), kind))
    ranges.sort()
    if not ranges:
        raise ValueError("object map contains no ranges")
    for (_, prior_end, _), (start, _, _) in zip(ranges, ranges[1:]):
        if prior_end >= start:
            raise ValueError("object-map ranges overlap")
    return ranges, [start for start, _, _ in ranges]


def classify(address: int, width: int, ranges: list[tuple[int, int, str]], starts: list[int]) -> str:
    index = bisect_right(starts, address) - 1
    for candidate in (index, index + 1):
        if 0 <= candidate < len(ranges):
            begin, end, kind = ranges[candidate]
            if begin <= address and address + width - 1 <= end:
                return kind
            if max(address, begin) <= min(address + width - 1, end):
                return "UNKNOWN"
    return "UNKNOWN"


def add_units(target: set[int], address: int, width: int, unit: int) -> None:
    target.update(range(address // unit, (address + width - 1) // unit + 1))


def quantile(values: list[int], fraction: float) -> int:
    if not values:
        return 0
    values.sort()
    return values[min(len(values) - 1, int((len(values) - 1) * fraction))]


def op_class(opcode: str) -> str:
    upper = opcode.upper()
    if "ATOM" in upper:
        return "ATOMIC"
    if upper.startswith("ST"):
        return "STORE"
    if upper.startswith("LD"):
        return "LOAD"
    return "OTHER_MEMORY"


def blank_object() -> dict[str, Any]:
    return {
        "lane_references": 0, "requested_bytes": 0,
        "sectors": set(), "lines": set(), "pages64": set(), "pages2": set(),
        "line_hot": Counter(), "page_hot": Counter(),
    }


def finalize_object(item: dict[str, Any]) -> dict[str, Any]:
    line_hot = list(item.pop("line_hot").values())
    page_hot = list(item.pop("page_hot").values())
    item["line_hot_max"] = max(line_hot, default=0)
    item["line_hot_p50"] = quantile(line_hot, .50)
    item["line_hot_p90"] = quantile(line_hot, .90)
    item["line_hot_p99"] = quantile(line_hot, .99)
    item["page_hot_max"] = max(page_hot, default=0)
    item["page_hot_p50"] = quantile(page_hot, .50)
    item["page_hot_p90"] = quantile(page_hot, .90)
    item["page_hot_p99"] = quantile(page_hot, .99)
    return item


def analyze_one(task: tuple[int, str, str, tuple[tuple[int, int, str], ...], tuple[int, ...], int, str]) -> str:
    index, trace_name, trace_dir, ranges_tuple, starts_tuple, sample_stride, partial_path = task
    trace = Path(trace_dir) / trace_name
    ranges, starts = list(ranges_tuple), list(starts_tuple)
    metrics = {kind: blank_object() for kind in OBJECTS}
    global_stats: dict[str, Any] = {
        "memory_instructions": 0, "lane_references": 0, "requested_bytes": 0,
        "instruction_object_class": Counter(), "op_class": Counter(),
        "lane_adjacent_pairs": 0, "lane_adjacent_equal_width": 0,
        "lane_adjacent_zero_stride": 0, "lane_adjacent_positive_other": 0,
        "lane_adjacent_negative": 0,
    }
    samples: list[int] = []
    lane_ordinal = 0
    with lzma.open(trace, "rt", errors="strict") as stream:
        for raw in stream:
            try:
                record = decode(raw)
            except ValueError as error:
                raise RuntimeError(f"{trace}: decoder failure: {error}") from error
            if record is None or record[1] == 0:
                continue
            opcode, width, addresses, _ = record
            global_stats["memory_instructions"] += 1
            global_stats["op_class"][op_class(opcode)] += 1
            classes: set[str] = set()
            for address in addresses:
                kind = classify(address, width, ranges, starts)
                classes.add(kind)
                item = metrics[kind]
                item["lane_references"] += 1
                item["requested_bytes"] += width
                for key, unit in UNITS.items():
                    add_units(item[key], address, width, unit)
                for line in range(address // 128, (address + width - 1) // 128 + 1):
                    item["line_hot"][line] += 1
                for page in range(address // (64 * 1024), (address + width - 1) // (64 * 1024) + 1):
                    item["page_hot"][page] += 1
                if lane_ordinal % sample_stride == 0:
                    samples.append(address // (64 * 1024))
                lane_ordinal += 1
                global_stats["lane_references"] += 1
                global_stats["requested_bytes"] += width
            bucket = next(iter(classes)) if len(classes) == 1 else "MIXED"
            global_stats["instruction_object_class"][bucket] += 1
            for before, after in zip(addresses, addresses[1:]):
                difference = after - before
                global_stats["lane_adjacent_pairs"] += 1
                if difference == width:
                    global_stats["lane_adjacent_equal_width"] += 1
                elif difference == 0:
                    global_stats["lane_adjacent_zero_stride"] += 1
                elif difference > 0:
                    global_stats["lane_adjacent_positive_other"] += 1
                else:
                    global_stats["lane_adjacent_negative"] += 1
    result = {
        "schema": "VM_SPEC_FARM_TRACE_PARTIAL_V1", "index": index, "trace": trace_name,
        "trace_sha256": digest(trace), "sample_stride_lane_references": sample_stride,
        "sampled_64kb_pages": samples, "global": global_stats,
        "objects": {kind: finalize_object(item) for kind, item in metrics.items()},
    }
    target = Path(partial_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(target.suffix + ".tmp")
    with lzma.open(temporary, "wb", preset=6) as output:
        pickle.dump(result, output, protocol=5)
    os.replace(temporary, target)
    return str(target)


def load_partial(path: Path) -> dict[str, Any]:
    with lzma.open(path, "rb") as stream:
        return pickle.load(stream)


def union_sets(partials: list[dict[str, Any]], kind: str, key: str) -> set[int]:
    result: set[int] = set()
    for partial in partials:
        if kind == "ALL":
            for object_kind in OBJECTS:
                result.update(partial["objects"][object_kind][key])
        else:
            result.update(partial["objects"][kind][key])
    return result


def sampled_lru(pages: list[int]) -> dict[str, int]:
    """Exact stack distance over the deterministic sampled reference stream."""
    size = len(pages) + 2
    tree = [0] * size

    def add(index: int, value: int) -> None:
        while index < size:
            tree[index] += value
            index += index & -index

    def total(index: int) -> int:
        answer = 0
        while index:
            answer += tree[index]
            index -= index & -index
        return answer

    previous: dict[int, int] = {}
    distances: list[int] = []
    for position, page in enumerate(pages, 1):
        if page in previous:
            distances.append(total(position - 1) - total(previous[page]))
            add(previous[page], -1)
        previous[page] = position
        add(position, 1)
    return {
        "sampled_references": len(pages), "sampled_cold_references": len(pages) - len(distances),
        "sampled_reuses": len(distances), "sampled_lru_distance_p50": quantile(distances, .50),
        "sampled_lru_distance_p90": quantile(distances, .90),
        "sampled_lru_distance_p99": quantile(distances, .99),
        "sampled_lru_distance_max": max(distances, default=0),
    }


def write_rows(path: Path, header: list[str], rows: list[list[Any]]) -> None:
    with path.open("w", newline="") as stream:
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)


def reduce_all(args: argparse.Namespace, names: list[str], partial_root: Path) -> None:
    provenance = [args.roi, digest(args.trace_list), digest(args.object_map)]
    total_instructions = total_lanes = total_bytes = object_lanes = object_bytes = 0
    header = [
        "roi", "trace_list_sha256", "object_map_sha256", "semantic_kernel_index", "trace_filename",
        "trace_sha256", "object_class", "memory_instructions", "lane_references", "requested_bytes",
        "unique_32b_sectors", "unique_128b_lines", "unique_64kb_pages", "unique_2mb_pages",
        "load_memory_instructions", "store_memory_instructions", "atomic_memory_instructions",
        "other_memory_instructions", "weight_only_memory_instructions", "kv_only_memory_instructions",
        "unknown_only_memory_instructions", "mixed_object_memory_instructions", "lane_adjacent_pairs",
        "lane_adjacent_equal_width", "lane_adjacent_zero_stride", "lane_adjacent_positive_other",
        "lane_adjacent_negative", "line_hot_max", "line_hot_p50", "line_hot_p90", "line_hot_p99",
        "page_hot_max", "page_hot_p50", "page_hot_p90", "page_hot_p99",
    ]
    overlap_header = [
        "roi", "trace_list_sha256", "object_map_sha256", "semantic_kernel_index", "trace_filename",
        "object_class", "previous_kernel_line_overlap", "previous_kernel_64kb_page_overlap",
        "prior_cumulative_line_overlap", "prior_cumulative_64kb_page_overlap", "new_lines_vs_prior",
        "new_64kb_pages_vs_prior",
    ]
    wss_header = [
        "roi", "trace_list_sha256", "object_map_sha256", "window_kernels", "first_kernel_index",
        "last_kernel_index", "object_class", "unique_128b_lines", "unique_64kb_pages", "unique_2mb_pages",
    ]
    prior = {kind: {"lines": set(), "pages64": set()} for kind in ("ALL", *OBJECTS)}
    cumulative = {kind: {"lines": set(), "pages64": set()} for kind in ("ALL", *OBJECTS)}
    recent: deque[dict[str, Any]] = deque(maxlen=64)
    samples: list[int] = []
    bucket_total = 0
    with (args.output_dir / "TRACE_STATIC_KERNEL_STATS.tsv").open("w", newline="") as static_stream, \
         (args.output_dir / "TRACE_CROSS_KERNEL_OVERLAP.tsv").open("w", newline="") as overlap_stream, \
         (args.output_dir / "TRACE_KERNEL_WINDOW_WSS.tsv").open("w", newline="") as wss_stream:
        static_writer = csv.writer(static_stream, delimiter="\t", lineterminator="\n")
        overlap_writer = csv.writer(overlap_stream, delimiter="\t", lineterminator="\n")
        wss_writer = csv.writer(wss_stream, delimiter="\t", lineterminator="\n")
        static_writer.writerow(header)
        overlap_writer.writerow(overlap_header)
        wss_writer.writerow(wss_header)
        for index, expected_name in enumerate(names):
            partial = load_partial(partial_root / f"{index:05d}.pkl.xz")
            if partial["trace"] != expected_name:
                raise RuntimeError("partial ordering does not match immutable trace list")
            global_stats = partial["global"]
            total_instructions += global_stats["memory_instructions"]
            total_lanes += global_stats["lane_references"]
            total_bytes += global_stats["requested_bytes"]
            bucket_total += sum(global_stats["instruction_object_class"].values())
            samples.extend(partial["sampled_64kb_pages"])
            all_lines = union_sets([partial], "ALL", "lines")
            all_sectors = union_sets([partial], "ALL", "sectors")
            all_pages64 = union_sets([partial], "ALL", "pages64")
            all_pages2 = union_sets([partial], "ALL", "pages2")
            static_writer.writerow([
                *provenance, index, partial["trace"], partial["trace_sha256"], "ALL",
                global_stats["memory_instructions"], global_stats["lane_references"], global_stats["requested_bytes"],
                len(all_sectors), len(all_lines), len(all_pages64), len(all_pages2),
                global_stats["op_class"].get("LOAD", 0), global_stats["op_class"].get("STORE", 0),
                global_stats["op_class"].get("ATOMIC", 0), global_stats["op_class"].get("OTHER_MEMORY", 0),
                global_stats["instruction_object_class"].get("WEIGHT", 0), global_stats["instruction_object_class"].get("KV_CACHE", 0),
                global_stats["instruction_object_class"].get("UNKNOWN", 0), global_stats["instruction_object_class"].get("MIXED", 0),
                global_stats["lane_adjacent_pairs"], global_stats["lane_adjacent_equal_width"], global_stats["lane_adjacent_zero_stride"],
                global_stats["lane_adjacent_positive_other"], global_stats["lane_adjacent_negative"], "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA",
            ])
            for kind in OBJECTS:
                item = partial["objects"][kind]
                object_lanes += item["lane_references"]
                object_bytes += item["requested_bytes"]
                static_writer.writerow([
                    *provenance, index, partial["trace"], partial["trace_sha256"], kind, "NA", item["lane_references"],
                    item["requested_bytes"], len(item["sectors"]), len(item["lines"]), len(item["pages64"]), len(item["pages2"]),
                    "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", item["line_hot_max"],
                    item["line_hot_p50"], item["line_hot_p90"], item["line_hot_p99"], item["page_hot_max"], item["page_hot_p50"],
                    item["page_hot_p90"], item["page_hot_p99"],
                ])
            for kind in ("ALL", *OBJECTS):
                lines = all_lines if kind == "ALL" else partial["objects"][kind]["lines"]
                pages = all_pages64 if kind == "ALL" else partial["objects"][kind]["pages64"]
                overlap_writer.writerow([
                    *provenance, index, partial["trace"], kind, len(lines & prior[kind]["lines"]),
                    len(pages & prior[kind]["pages64"]), len(lines & cumulative[kind]["lines"]),
                    len(pages & cumulative[kind]["pages64"]), len(lines - cumulative[kind]["lines"]),
                    len(pages - cumulative[kind]["pages64"]),
                ])
                cumulative[kind]["lines"].update(lines)
                cumulative[kind]["pages64"].update(pages)
                prior[kind]["lines"], prior[kind]["pages64"] = lines, pages
            recent.append(partial)
            window_items = list(recent)
            for width in (1, 4, 16, 64):
                if len(window_items) >= width:
                    window = window_items[-width:]
                    for kind in ("ALL", *OBJECTS):
                        wss_writer.writerow([
                            *provenance, width, index - width + 1, index, kind,
                            len(union_sets(window, kind, "lines")), len(union_sets(window, kind, "pages64")),
                            len(union_sets(window, kind, "pages2")),
                        ])
    reuse = sampled_lru(samples)
    write_rows(args.output_dir / "TRACE_REUSE_DISTANCE_SUMMARY.tsv", [
        "roi", "trace_list_sha256", "object_map_sha256", "method", "sample_stride_lane_references",
        "sampled_references", "sampled_cold_references", "sampled_reuses", "sampled_lru_distance_p50",
        "sampled_lru_distance_p90", "sampled_lru_distance_p99", "sampled_lru_distance_max",
    ], [[*provenance, "SAMPLED_TRANSLATION_REUSE_DISTANCE_LRU", args.sample_stride, *reuse.values()]])

    write_rows(args.output_dir / "TRACE_MINING_CONSERVATION.tsv", ["check", "expected", "observed", "result"], [
        ["lane_references_by_object", total_lanes, object_lanes, "PASS" if total_lanes == object_lanes else "FAIL"],
        ["requested_bytes_by_object", total_bytes, object_bytes, "PASS" if total_bytes == object_bytes else "FAIL"],
        ["memory_instructions_exclusive_object_bucket", total_instructions, bucket_total,
         "PASS" if total_instructions == bucket_total else "FAIL"],
    ])
    if total_lanes != object_lanes or total_bytes != object_bytes:
        raise RuntimeError("object conservation failure")
    (args.output_dir / "TRACE_MINING_SCHEMA.md").write_text(
        "# Window-B immutable trace mining schema\n\n"
        "All lane references are decoded with the frozen exact decoder and classified against the read-only runtime range map. "
        "Instruction object buckets are exclusive (`WEIGHT`, `KV_CACHE`, `UNKNOWN`, `MIXED`) so they conserve across classes. "
        "Stride counts are exact lane-adjacent address deltas within each decoded memory instruction. "
        "The reuse-distance table is exact only for every Nth lane reference (N recorded in the table), and is therefore explicitly a sampled approximation of the complete translation-reference stream.\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--roi", choices=("prefill", "decode1"), required=True)
    parser.add_argument("--trace-list", type=Path, required=True)
    parser.add_argument("--trace-dir", type=Path, required=True)
    parser.add_argument("--object-map", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=32)
    parser.add_argument("--sample-stride", type=int, default=1024)
    parser.add_argument("--max-kernels", type=int, default=0)
    parser.add_argument("--resume", action="store_true", help="reuse only atomically completed B-owned partials")
    parser.add_argument("--partials-only", action="store_true",
                        help="finish only requested atomic partials; do not create reduced outputs")
    args = parser.parse_args()
    if ((args.output_dir.exists() and not args.resume) or args.workers < 1 or args.sample_stride < 1 or
            args.max_kernels < 0):
        raise SystemExit("FAIL output must be fresh unless --resume; workers/sample-stride positive; max-kernels nonnegative")
    if args.resume and any(args.output_dir.glob("TRACE_*.tsv")):
        raise SystemExit("FAIL --resume permits partials only, never replaces reduced outputs")
    names = [line.strip() for line in args.trace_list.read_text().splitlines() if line.strip()]
    if args.max_kernels:
        names = names[:args.max_kernels]
    if not names or any(Path(name).name != name or not name.endswith(".traceg.xz") for name in names):
        raise SystemExit("FAIL unsafe or empty immutable trace list")
    if any(not (args.trace_dir / name).is_file() for name in names):
        raise SystemExit("FAIL listed immutable trace missing")
    ranges, starts = object_ranges(args.object_map)
    args.output_dir.mkdir(parents=True, exist_ok=args.resume)
    partial_root = args.output_dir / "partials"
    tasks = [
        (index, name, str(args.trace_dir), tuple(ranges), tuple(starts), args.sample_stride,
         str(partial_root / f"{index:05d}.pkl.xz"))
        for index, name in enumerate(names) if not (partial_root / f"{index:05d}.pkl.xz").is_file()
    ]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(analyze_one, task) for task in tasks]
        for future in as_completed(futures):
            future.result()
    if args.partials_only:
        print(f"PARTIALS roi={args.roi} requested_kernels={len(names)} newly_completed={len(tasks)} "
              f"output={args.output_dir}")
        return
    reduce_all(args, names, partial_root)
    print(f"PASS roi={args.roi} kernels={len(names)} output={args.output_dir}")


if __name__ == "__main__":
    main()
