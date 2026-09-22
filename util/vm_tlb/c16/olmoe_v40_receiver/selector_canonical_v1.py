#!/usr/bin/env python3
"""Independent 174-new implementation of C16_SELECTOR_CANONICAL_V1."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
from typing import Any

SCHEMA = "C16_SELECTOR_CANONICAL_V1"


class SelectorError(ValueError):
    """A literal selector TSV cannot be an authority input."""


def _index(value: str) -> int:
    try:
        return int(value, 0)
    except ValueError as exc:
        raise SelectorError(f"static_index is not int(value, 0): {value!r}") from exc


def canonicalize_tsv(path: Path) -> tuple[bytes, dict[str, Any]]:
    """Return precisely specified canonical bytes and structural metadata."""
    try:
        handle = path.open("r", encoding="utf-8", newline="")
    except OSError as exc:
        raise SelectorError(f"cannot open selector TSV: {exc}") from exc
    with handle:
        reader = csv.reader(handle, delimiter="\t", strict=True)
        try:
            columns = next(reader)
        except StopIteration as exc:
            raise SelectorError("selector TSV is empty") from exc
        except csv.Error as exc:
            raise SelectorError(f"invalid TSV header: {exc}") from exc
        if not columns or any(column == "" for column in columns):
            raise SelectorError("selector TSV has an empty column name")
        if len(columns) != len(set(columns)):
            raise SelectorError("selector TSV has duplicate column names")
        if "static_index" not in columns:
            raise SelectorError("selector TSV lacks static_index")
        rows: list[dict[str, str]] = []
        seen: set[int] = set()
        for line_number, fields in enumerate(reader, 2):
            if len(fields) != len(columns):
                raise SelectorError(f"line {line_number}: field count differs from header")
            row = dict(zip(columns, fields, strict=True))
            static_index = _index(row["static_index"])
            if static_index in seen:
                raise SelectorError(f"line {line_number}: duplicate static_index")
            seen.add(static_index)
            rows.append(row)
    columns = sorted(columns)
    rows.sort(key=lambda row: _index(row["static_index"]))
    obj = {"schema": SCHEMA, "columns": columns,
           "rows": [{column: row[column] for column in columns} for row in rows]}
    canonical = (json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    return canonical, {"schema": SCHEMA, "row_count": len(rows), "column_count": len(columns),
                       "unique_static_count": len(seen), "static_indices": sorted(seen),
                       "raw_tsv_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                       "canonical_sha256": hashlib.sha256(canonical).hexdigest()}


def write_new(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    try:
        written = 0
        while written < len(payload):
            written += os.write(fd, payload[written:])
        os.fsync(fd)
    finally:
        os.close(fd)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selector-tsv", type=Path, required=True)
    parser.add_argument("--canonical-output", type=Path)
    parser.add_argument("--receipt-output", type=Path)
    args = parser.parse_args()
    try:
        canonical, receipt = canonicalize_tsv(args.selector_tsv)
        receipt.update({"status": "PASS", "selector_tsv": str(args.selector_tsv)})
        if args.canonical_output:
            write_new(args.canonical_output, canonical)
            receipt["canonical_output"] = str(args.canonical_output)
        if args.receipt_output:
            write_new(args.receipt_output, (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode("utf-8"))
        print(json.dumps(receipt, sort_keys=True))
        return 0
    except (SelectorError, OSError, csv.Error) as exc:
        print(json.dumps({"status": "REJECT", "error": str(exc)}, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
