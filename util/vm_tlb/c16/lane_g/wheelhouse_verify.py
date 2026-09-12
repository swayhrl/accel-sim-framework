#!/usr/bin/env python3
"""Hash-close an imported C16 wheelhouse before pip is allowed to install it."""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from c16_native_common import ContractError, sha256_file, valid_sha256


REQUIRED = ("wheel_filename", "package", "version", "sha256", "status")


def validate(wheelhouse: Path, manifest: Path) -> int:
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
    count = 0
    for row in rows:
        if any(not row.get(field) for field in REQUIRED):
            raise ContractError(f"wheelhouse manifest row lacks required field: {row}")
        path = wheelhouse / row["wheel_filename"]
        if not path.is_file() or not valid_sha256(row["sha256"]):
            raise ContractError(f"wheel artifact/hash absent: {path}")
        if sha256_file(path) != row["sha256"]:
            raise ContractError(f"wheel hash mismatch: {path}")
        count += 1
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wheelhouse", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    print(f"PASS C16 wheelhouse closure: {validate(args.wheelhouse, args.manifest)} wheels")


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        print(f"FAIL C16 wheelhouse closure: {exc}", file=sys.stderr)
        raise SystemExit(2)
