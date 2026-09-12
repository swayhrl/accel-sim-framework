#!/usr/bin/env python3
"""Promote prior C16 whole-file verification records into per-file receipts.

This migration intentionally does not hash model weights.  It consumes only
already committed C16 asset receipts whose local checkpoint row has a recorded
whole-file SHA-256, then confirms the current path's byte count before writing
the uniform immutable receipt consumed by package writers.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path


OUTPUT_ROOT = Path("docs/vm_tlb/review_packs/C16_MULTIMODEL_NATIVE/lane_a")
SOURCE_ROOT = OUTPUT_ROOT / "MODEL_ASSET_RECEIPTS"
RECEIPT_ROOT = Path("/workspace/c16_assets/c16-a/download_logs/immutable_verified_receipts")


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def main() -> int:
    migrated = 0
    retained = 0
    for source_path in sorted(SOURCE_ROOT.glob("*.json")):
        source = json.loads(source_path.read_text(encoding="utf-8"))
        for row in source.get("local_rows", []):
            if row.get("asset_role") != "CHECKPOINT_FILE" or not row.get("verification_status", "").startswith("LOCAL_SHA256_VERIFIED"):
                continue
            local_path = Path(row["local_path"])
            if not local_path.is_file() or local_path.stat().st_size != int(row["size_bytes"]):
                continue
            receipt_path = RECEIPT_ROOT / row["deployment_id"] / f"{row['asset_path']}.json"
            if receipt_path.exists():
                retained += 1
                continue
            atomic_json(
                receipt_path,
                {
                    "schema_version": "C16_IMMUTABLE_VERIFIED_CHECKPOINT_RECEIPT_V1",
                    "status": "IMMUTABLE_VERIFIED",
                    "verified_at_utc": now(),
                    "verification_method": "migrated_prior_c16_whole_file_sha256_receipt_no_rehash",
                    "source_receipt_path": str(source_path),
                    "deployment_id": row["deployment_id"],
                    "source_repo": row["source_repo"],
                    "source_revision": row["source_revision"],
                    "tokenizer_revision": row["tokenizer_revision"],
                    "asset_path": row["asset_path"],
                    "local_path": str(local_path),
                    "expected_size_bytes": int(row["size_bytes"]),
                    "sha256": row["sha256"],
                    "execution_boundary": "CPU_METADATA_AND_STAT_ONLY_NO_GPU_PROFILER_NVBIT_SIMULATOR_SASS_OR_FULL_ROI",
                },
            )
            migrated += 1
    print(f"C16A_T16 PASS migrated={migrated} retained={retained}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
