#!/usr/bin/env python3
"""C16-1.2 manifest/hash closure gate; it refuses incomplete upstream assets."""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from c16_native_common import ContractError, atomic_json, sha256_file, valid_sha256


EXPECTED_FIELDS = ("artifact_id", "kind", "path_or_commit", "sha256", "required_for", "closure_status", "note")


def read_rows(path: Path) -> list[dict[str, str]]:
    try:
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            if tuple(reader.fieldnames or ()) != EXPECTED_FIELDS:
                raise ContractError("EXPECTED_HASHES.tsv header is not the frozen C16 schema")
            return list(reader)
    except OSError as exc:
        raise ContractError(f"cannot read expected-hashes manifest: {exc}") from exc


def preconditions(rows: list[dict[str, str]]) -> list[str]:
    return [row["artifact_id"] for row in rows if row["closure_status"] != "LOCAL_HASH_CLOSED" or not valid_sha256(row["sha256"])]


def verify(rows: list[dict[str, str]], root: Path) -> list[dict[str, str]]:
    blocked = preconditions(rows)
    if blocked:
        raise ContractError("cannot enter C16-1.2; hash closure missing for: " + ", ".join(blocked))
    receipt_rows = []
    for row in rows:
        path = root / row["path_or_commit"]
        if not path.is_file():
            raise ContractError(f"expected transferred artifact is absent: {path}")
        actual = sha256_file(path)
        if actual != row["sha256"]:
            raise ContractError(f"transferred artifact hash mismatch: {row['artifact_id']}")
        receipt_rows.append({"artifact_id": row["artifact_id"], "path": str(path), "sha256": actual, "status": "PASS"})
    return receipt_rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expected-hashes", type=Path, required=True)
    parser.add_argument("--transfer-root", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    rows = read_rows(args.expected_hashes)
    if args.dry_run:
        blocked = preconditions(rows)
        receipt = {"stage_id": "C16-1.2", "execution_mode": "DRY_RUN", "scientific_eligible": False, "expected_row_count": len(rows), "unclosed_artifacts": blocked, "status": "BLOCKED_UPSTREAM_HASH_CLOSURE" if blocked else "READY_FOR_VERIFY"}
    else:
        receipt = {"stage_id": "C16-1.2", "execution_mode": "TRANSFER_HASH_VERIFY", "scientific_eligible": False, "rows": verify(rows, args.transfer_root), "status": "TRANSFER_HASH_CLOSED"}
    atomic_json(args.receipt, receipt)
    print(f"PASS C16 transfer verifier: {args.receipt} ({receipt['status']})")


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        print(f"FAIL C16 transfer verifier: {exc}", file=sys.stderr)
        raise SystemExit(2)
