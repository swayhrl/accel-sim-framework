#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


REPO = Path(__file__).resolve().parents[4]
PACK = (
    REPO
    / "docs/vm_tlb/review_packs"
    / "AWMA_POST_COALESCING_RESEARCH_HYPOTHESES_V1"
)


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def main() -> int:
    errors: list[str] = []
    for path in PACK.glob("*.json"):
        try:
            json.loads(path.read_text())
        except Exception as error:
            errors.append(f"JSON:{path.name}:{error}")
    for path in PACK.glob("*.tsv"):
        rows = [row for row in csv.reader(path.open(), delimiter="\t") if row]
        if not rows or any(len(row) != len(rows[0]) for row in rows):
            errors.append(f"TSV:{path.name}")

    with (PACK / "RAW_INDEX.tsv").open() as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    checked = 0
    for row in rows:
        expected = row["sha256_or_commit"]
        if len(expected) != 64:
            continue
        path = Path(row["path_or_reference"])
        if not path.is_absolute():
            path = REPO / path
        if not path.is_file():
            errors.append(f"RAW_MISSING:{row['identity']}:{path}")
            continue
        checked += 1
        actual = digest(path)
        if actual != expected:
            errors.append(
                f"RAW_HASH:{row['identity']}:actual={actual}:expected={expected}"
            )

    print(f"json_tsv_pass={not errors} raw_files_checked={checked} errors={len(errors)}")
    for error in errors:
        print(error)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
