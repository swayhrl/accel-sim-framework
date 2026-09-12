#!/usr/bin/env python3
"""Publish/validate a hash-closed runtime checkpoint without raw profiler payloads."""
from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, sha256_file, valid_sha256


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False) as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")
        temporary = Path(handle.name)
    os.replace(temporary, path)


def payloads(directory: Path) -> list[dict[str, Any]]:
    return [
        {"path": item.name, "sha256": sha256_file(item), "size_bytes": item.stat().st_size}
        for item in sorted(directory.iterdir())
        if item.is_file() and item.name != "PUBLISH_MANIFEST.json"
    ]


def validate(directory: Path) -> list[dict[str, Any]]:
    manifest_path = directory / "PUBLISH_MANIFEST.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read runtime publish manifest: {exc}") from exc
    entries = manifest.get("files")
    if not isinstance(entries, list):
        raise ContractError("runtime publish manifest has no file list")
    seen: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise ContractError("runtime publish manifest has malformed file entry")
        name, digest, size = entry.get("path"), entry.get("sha256"), entry.get("size_bytes")
        if not isinstance(name, str) or Path(name).name != name or not name or name in seen:
            raise ContractError("runtime publish manifest has unsafe or duplicate payload path")
        if not isinstance(digest, str) or not valid_sha256(digest) or not isinstance(size, int) or isinstance(size, bool) or size < 0:
            raise ContractError("runtime publish manifest has malformed payload metadata")
        seen.add(name)
        path = directory / name
        if not path.is_file() or path.stat().st_size != size or sha256_file(path) != digest:
            raise ContractError(f"runtime publish payload differs from manifest: {name}")
    actual = {item.name for item in directory.iterdir() if item.is_file() and item.name != "PUBLISH_MANIFEST.json"}
    if actual != seen:
        raise ContractError(f"runtime publish payload set mismatch: unlisted={sorted(actual - seen)} stale={sorted(seen - actual)}")
    if manifest.get("raw_profiler_payloads_committed") is not False:
        raise ContractError("runtime checkpoint must explicitly exclude raw profiler payloads")
    return entries


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--runtime-code-commit")
    parser.add_argument("--validation-code-commit")
    args = parser.parse_args()
    if args.write == args.validate:
        parser.error("choose exactly one of --write or --validate")
    if args.write:
        if not args.runtime_code_commit or not args.validation_code_commit:
            parser.error("--write requires runtime and validation code commits")
        atomic_json(args.directory / "PUBLISH_MANIFEST.json", {
            "schema_version": "C16_G_RUNTIME_NATIVE_CHECKPOINT_V1",
            "status": "C16_G_WAVE1_LLAM A_NATIVE_G1_CENSUS_EARLY_CHECKPOINT".replace(" ", ""),
            "planning_sha": "f222e66f49af56cfd4ded671c4a50c6811237cc2",
            "accepted_offline_g_commit": "45e293b84940ef59b7b134bcda48aca7d0b99b2f",
            "runtime_code_commit": args.runtime_code_commit,
            "validation_code_commit": args.validation_code_commit,
            "a_p0_package_commit": "20fb38e6ca629f1a93db7939248bd1a03790724c",
            "a_p0_package_manifest_sha256": "ac59f0d2aca95021c686948d7244ce50375530bbe983c8508ca5f6954e80230f",
            "scientific_evidence": "NATIVE_BASELINE_AND_NSYS_PROFILED_LLAM A_ONLY".replace(" ", ""),
            "raw_profiler_payloads_committed": False,
            "files": payloads(args.directory),
        })
        print(f"PASS C16 runtime checkpoint manifest write: {args.directory / 'PUBLISH_MANIFEST.json'}")
    else:
        entries = validate(args.directory)
        print(f"PASS C16 runtime checkpoint manifest validation: {len(entries)} payloads")


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        print(f"FAIL C16 runtime checkpoint manifest validation: {exc}", file=__import__("sys").stderr)
        raise SystemExit(2)
