#!/usr/bin/env python3
"""Hash-close an imported C16 wheelhouse before pip is allowed to install it."""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from c16_native_common import ContractError, sha256_file, valid_sha256
from wheelhouse_manifest import FIELDS, STATUS, canonical_package, requirement_roots, target_compatible, wheel_metadata


REQUIRED = FIELDS


def read_manifest(manifest: Path) -> list[dict[str, str]]:
    try:
        with manifest.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            if tuple(reader.fieldnames or ()) != REQUIRED:
                raise ContractError("wheelhouse manifest header does not match the locked schema")
            rows = list(reader)
    except OSError as exc:
        raise ContractError(f"cannot read wheelhouse manifest: {exc}") from exc
    if not rows:
        raise ContractError("wheelhouse manifest has no imported wheels")
    return rows


def validate(wheelhouse: Path, manifest: Path, requirements: Path | None = None) -> int:
    rows = read_manifest(manifest)
    listed = {row["wheel_filename"] for row in rows}
    actual = {path.name for path in wheelhouse.glob("*.whl")}
    if listed != actual:
        raise ContractError("wheelhouse file set differs from hash-bound manifest")
    packages: dict[str, str] = {}
    count = 0
    for row in rows:
        if any(not row.get(field) for field in REQUIRED):
            raise ContractError(f"wheelhouse manifest row lacks required field: {row}")
        path = wheelhouse / row["wheel_filename"]
        if not path.is_file() or not valid_sha256(row["sha256"]) or row["status"] != STATUS:
            raise ContractError(f"wheel artifact/hash absent: {path}")
        package, version, tag = wheel_metadata(path)
        if sha256_file(path) != row["sha256"] or str(path.stat().st_size) != row["size_bytes"]:
            raise ContractError(f"wheel hash mismatch: {path}")
        if canonical_package(package) != canonical_package(row["package"]) or version != row["version"] or tag != row["compatibility_tag"]:
            raise ContractError(f"wheel metadata mismatch: {path}")
        if not target_compatible(tag):
            raise ContractError(f"wheel tag is not compatible with this CPython/Linux target: {path}")
        normalized = canonical_package(package)
        if normalized in packages:
            raise ContractError(f"wheelhouse has duplicate distribution: {package}")
        packages[normalized] = version
        count += 1
    if requirements is not None:
        for package, version in requirement_roots(requirements).items():
            if packages.get(package) != version:
                raise ContractError(f"wheelhouse root pin missing or mismatched: {package}=={version}")
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wheelhouse", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--requirements", type=Path)
    args = parser.parse_args()
    print(f"PASS C16 wheelhouse closure: {validate(args.wheelhouse, args.manifest, args.requirements)} wheels")


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        print(f"FAIL C16 wheelhouse closure: {exc}", file=sys.stderr)
        raise SystemExit(2)
