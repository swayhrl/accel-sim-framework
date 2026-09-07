#!/usr/bin/env python3
"""Freeze B9's metadata-only, matched 16+16 static-mining selector.

The selector reads immutable kernel-list text and filesystem metadata only.  It
does not open, decompress, hash, or decode any trace.  The selected lists are
therefore a reproducible preflight input, not B1 mining evidence.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
from dataclasses import dataclass
from pathlib import Path


COUNT = 16
KERNEL = re.compile(r"^kernel-(\d+)-ctx_([^.]*)\.traceg\.xz$")


@dataclass(frozen=True)
class Item:
    roi: str
    index: int
    name: str
    kernel_id: int
    context: str
    size: int
    ordinal_rank: float
    size_rank: float


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_items(roi: str, trace_list: Path, trace_dir: Path) -> list[Item]:
    names = [line.strip() for line in trace_list.read_text().splitlines() if line.strip()]
    if len(names) < COUNT or len(names) != len(set(names)):
        raise SystemExit(f"FAIL {roi}: unsafe cardinality/duplicate list")
    parsed: list[tuple[int, str, int, str, int]] = []
    for index, name in enumerate(names):
        match = KERNEL.fullmatch(name)
        if not match:
            raise SystemExit(f"FAIL {roi}: unsafe trace name {name}")
        path = trace_dir / name
        if not path.is_file():
            raise SystemExit(f"FAIL {roi}: missing immutable trace {path}")
        parsed.append((index, name, int(match.group(1)), match.group(2), path.stat().st_size))
    size_order = {name: rank for rank, (_, name, *_rest) in enumerate(sorted(parsed, key=lambda row: (row[4], row[1]))) }
    total = len(parsed)
    return [Item(roi, index, name, kernel_id, context, size,
                 (index + 0.5) / total, (size_order[name] + 0.5) / total)
            for index, name, kernel_id, context, size in parsed]


def choose(items: list[Item]) -> list[tuple[Item, str, str]]:
    """Pick one unique nearest item for each common temporal/size quartile."""
    chosen: set[int] = set()
    result: list[tuple[Item, str, str]] = []
    for temporal_bin in range(4):
        for size_bin in range(4):
            ordinal_target = (temporal_bin + 0.5) / 4
            size_target = (size_bin + 0.5) / 4
            candidates = [item for item in items if item.index not in chosen]
            if not candidates:
                raise SystemExit("FAIL selector exhausted candidates")
            item = min(candidates, key=lambda candidate: (
                abs(candidate.ordinal_rank - ordinal_target) + abs(candidate.size_rank - size_target),
                hashlib.sha256(candidate.name.encode()).hexdigest(), candidate.index))
            chosen.add(item.index)
            signature = f"temporal_q{temporal_bin};compressed_size_q{size_bin}"
            result.append((item, signature, "NEAREST_UNIQUE_METADATA_SIGNATURE"))
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prefill-list", type=Path, required=True)
    parser.add_argument("--prefill-trace-dir", type=Path, required=True)
    parser.add_argument("--decode-list", type=Path, required=True)
    parser.add_argument("--decode-trace-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if bool(args.output) == args.dry_run:
        raise SystemExit("FAIL specify exactly one of --output or --dry-run")

    rows: list[dict[str, str]] = []
    for roi, listing, directory in (("prefill", args.prefill_list, args.prefill_trace_dir),
                                    ("decode1", args.decode_list, args.decode_trace_dir)):
        items = read_items(roi, listing, directory)
        for rank, (item, signature, mode) in enumerate(choose(items), start=1):
            rows.append({
                "roi": roi, "source_trace_list": str(listing), "source_trace_list_sha256": sha256(listing),
                "source_trace_count": str(len(items)), "selected_rank": str(rank),
                "semantic_kernel_index": str(item.index), "kernel_id": str(item.kernel_id),
                "trace_filename": item.name, "trace_metadata_size_bytes": str(item.size),
                "ordinal_rank_fraction": f"{item.ordinal_rank:.9f}", "size_rank_fraction": f"{item.size_rank:.9f}",
                "matching_signature": signature, "selection_mode": mode,
                "trace_content_access": "NONE_METADATA_ONLY",
            })
    fields = list(rows[0])
    if args.dry_run:
        print("PASS metadata_only_selector rows=32 per_roi=16")
        for row in rows:
            print("\t".join(row[field] for field in fields))
        return
    if args.output.exists():
        raise SystemExit(f"FAIL refusing to overwrite selector output: {args.output}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"PASS metadata_only_selector output={args.output} sha256={sha256(args.output)}")


if __name__ == "__main__":
    main()
