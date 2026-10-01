#!/usr/bin/env python3
"""Mechanical raw SHA/index closure for R19F1; no GPU operations."""

import csv
import hashlib
from pathlib import Path

root = Path("/data/c16/awma/r19f1_fp8_numeric_decomposition_20261001")
pack = Path("/home/huangrulin/workspace/worktrees/accel-sim-awma-r19f1-fp8-readiness-109-v1/docs/vm_tlb/review_packs/AWMA_R19F1_FP8_NUMERIC_DECOMPOSITION_109_V1")
node164 = "/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/r19f1_fp8_numeric_decomposition_109_v1_20261001"
rows = []
for path in sorted((root / "raw").iterdir()):
    if not path.is_file():
        continue
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1048576), b""):
            h.update(chunk)
    rows.append({"relative_path": f"raw/{path.name}", "bytes": path.stat().st_size, "sha256": h.hexdigest(), "node164_path": f"{node164}/raw/{path.name}"})

with (pack / "RAW_DATA_INDEX.tsv").open("w", newline="", encoding="utf-8") as stream:
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]), delimiter="\t")
    writer.writeheader()
    writer.writerows(rows)
with (root / "RAW_SHA256SUMS").open("w", encoding="utf-8") as stream:
    for row in rows:
        stream.write(f"{row['sha256']}  {row['relative_path']}\n")
print(f"indexed {len(rows)} raw files")
