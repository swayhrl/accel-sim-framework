#!/usr/bin/env python3
"""Mechanical node164 raw/scene/source-anchor index and SHA closure."""

import csv
import hashlib
from pathlib import Path


ROOT = Path("/data/c16/awma/r20_active_world_native_v1")
PACK = Path("/home/huangrulin/workspace/worktrees/accel-sim-awma-r20-active-world-native-109-v1/docs/vm_tlb/review_packs/AWMA_R20_ACTIVE_WORLD_NATIVE_109_V1")
NODE164 = "/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/r20_active_world_native_109_v1"


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1048576), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    rows = []
    for subtree in ("raw", "scene", "source_anchor"):
        for path in sorted((ROOT / subtree).rglob("*")):
            if not path.is_file():
                continue
            relative = path.relative_to(ROOT).as_posix()
            rows.append({
                "relative_path": relative,
                "bytes": path.stat().st_size,
                "sha256": sha(path),
                "node164_path": f"{NODE164}/{relative}",
            })
    with (PACK / "RAW_DATA_INDEX.tsv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    with (ROOT / "RAW_SHA256SUMS").open("w", encoding="utf-8") as stream:
        for row in rows:
            stream.write(f"{row['sha256']}  {row['relative_path']}\n")
    print(f"indexed {len(rows)} raw/scene/source-anchor files")


if __name__ == "__main__":
    main()
