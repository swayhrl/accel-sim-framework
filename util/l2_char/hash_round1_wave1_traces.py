#!/usr/bin/env python3
"""Hash only the reconciled 52-entry Wave-1 roster, never the 159-root pool."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
from concurrent.futures import ThreadPoolExecutor


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def files_for_list(kernelslist: Path) -> list[Path]:
    lines = kernelslist.read_text(errors="replace").splitlines()
    names = [line.strip() for line in lines
             if re.search(r"\.traceg(?:\.xz)?$", line.strip())]
    return [kernelslist.parent / name for name in names]


def manifest_for_row(row: dict[str, str], workers: int) -> dict:
    klist = Path(row["current_trace_path"])
    files = files_for_list(klist)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        hashes = list(pool.map(sha256, files))
    items = [{"path": str(path), "bytes": path.stat().st_size, "sha256": digest}
             for path, digest in zip(files, hashes)]
    canonical = "\n".join(
        f"{item['sha256']}  {item['bytes']}  {item['path']}" for item in items
    ).encode()
    return {
        "suite": row["suite"], "workload": row["workload"], "input": row["input"],
        "kernelslist": str(klist), "kernelslist_sha256": sha256(klist),
        "trace_file_count": len(items), "trace_tree_sha256": hashlib.sha256(canonical).hexdigest(),
        "trace_files": items,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--roster", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--jobs", type=int, default=2)
    args = parser.parse_args()
    rows = list(csv.DictReader(args.roster.open(), delimiter="\t"))
    records = []
    for index, row in enumerate(rows, 1):
        print(f"[{index}/{len(rows)}] {row['suite']}/{row['workload']}", flush=True)
        records.append(manifest_for_row(row, max(1, args.jobs)))
    payload = {"scope": "Round-1 reconciled 52-workload roster only",
               "trace_body_sha256": records}
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(f"wrote {len(records)} trace manifests to {args.out}")


if __name__ == "__main__":
    main()
