#!/usr/bin/env python3
"""Copy a reviewed legacy manifest only after source/destination SHA closure."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
from pathlib import Path

try:
    from .receiver_common import AdmissionError, safe_relative_path, sha256_file, utc_now
except ImportError:
    from receiver_common import AdmissionError, safe_relative_path, sha256_file, utc_now


def copy_file(source: Path, destination: Path) -> None:
    if destination.exists():
        raise FileExistsError(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with source.open("rb") as src, destination.open("xb") as dst:
        while True:
            block = src.read(1024 * 1024)
            if not block:
                break
            dst.write(block)
        dst.flush()
        os.fsync(dst.fileno())


def import_manifest(manifest_path: Path, destination_root: Path) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not manifest.get("legacy") or not isinstance(manifest.get("artifacts"), list):
        raise AdmissionError("legacy manifest with artifacts list required")
    results = []
    for item in manifest["artifacts"]:
        source = Path(item["source_path"])
        relative = safe_relative_path(item["destination_relative_path"])
        if not source.is_file() or source.is_symlink():
            raise AdmissionError(f"invalid legacy source: {source}")
        if source.stat().st_size != item["size_bytes"] or sha256_file(source) != item["sha256"]:
            raise AdmissionError(f"source closure mismatch: {source}")
        destination = destination_root / relative
        copy_file(source, destination)
        if destination.stat().st_size != item["size_bytes"] or sha256_file(destination) != item["sha256"]:
            raise AdmissionError(f"destination closure mismatch: {destination}")
        results.append({"source_path": str(source), "destination_path": str(destination), "size_bytes": item["size_bytes"], "sha256": item["sha256"], "status": "PASS"})
    return {"schema_version": 1, "legacy": True, "status": "PASS", "imported_at_utc": utc_now(), "artifacts": results}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--destination-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = import_manifest(args.manifest, args.destination_root)
        if args.output.exists():
            raise AdmissionError(f"output exists: {args.output}")
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps({"status": "PASS", "output": str(args.output)}))
        return 0
    except (AdmissionError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
