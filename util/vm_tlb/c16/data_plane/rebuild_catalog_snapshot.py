#!/usr/bin/env python3
"""Rebuild a deterministic TSV snapshot from immutable catalog entries."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

FIELDS = ("run_id", "model", "revision", "scenario", "phase", "instrument", "target", "producer_host", "producer_commit", "raw_path", "raw_bytes", "raw_manifest_sha256", "transfer_status", "parse_status", "feature_status", "scientific_status", "legacy")


def rebuild(root: Path) -> Path:
    entries = []
    for path in sorted((root / "catalog" / "entries").glob("*.json")):
        entries.append(json.loads(path.read_text(encoding="utf-8")))
    entries.sort(key=lambda item: item["run_id"])
    lines = ["\t".join(FIELDS)]
    for entry in entries:
        values = [str(entry.get(field, "")).replace("\t", " ").replace("\n", " ") for field in FIELDS]
        lines.append("\t".join(values))
    destination = root / "catalog" / "snapshots" / "C16_TRACE_CATALOG.tsv"
    temporary = destination.with_suffix(".tsv.partial")
    if temporary.exists():
        raise FileExistsError(temporary)
    with temporary.open("x", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, destination)
    return destination


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    print(rebuild(args.root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
