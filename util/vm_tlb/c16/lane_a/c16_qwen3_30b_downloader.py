#!/usr/bin/env python3
"""Resume-safe, CPU-only downloader for the pinned Qwen3-30B-A3B asset.

The worker intentionally runs one shard at a time.  It never treats an
``.incomplete`` file as an asset: only an exact-size file whose whole-file
SHA-256 equals the frozen immutable LFS declaration is renamed to its final
checkpoint path.  The progress receipt is outside the review package so it
cannot be mistaken for a committed cross-lane input while the download is
live.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


DEPLOYMENT_ID = "c16_qwen3_30b_a3b_native_moe"
MODEL_ID = "Qwen/Qwen3-30B-A3B"
REVISION = "ad44e777bcd18fa416d9da3bd8f70d33ebb85d39"
MIN_START_FREE_BYTES = 85 * 1024**3
PAUSE_FREE_BYTES = 15 * 1024**3
BACKGROUND_MAX_RATE = "1M"
MODEL_ROOT = Path(
    "/workspace/c16_assets/c16-a/metadata/"
    "Qwen__Qwen3-30B-A3B__ad44e777bcd18fa416d9da3bd8f70d33ebb85d39"
)
MANIFEST = Path(
    "docs/vm_tlb/review_packs/C16_MULTIMODEL_NATIVE/lane_a/"
    "MODEL_ASSET_MANIFEST.tsv"
)
PROGRESS_RECEIPT = Path(
    "/workspace/c16_assets/c16-a/download_logs/"
    "C16_QWEN3_30B_A3B_PROGRESS.json"
)


class DiskPause(RuntimeError):
    """Normal, non-destructive pause that protects the Wave-1 work set."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def free_bytes() -> int:
    return shutil.disk_usage(MODEL_ROOT).free


def frozen_shards(manifest: Path) -> list[dict[str, str]]:
    with manifest.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    shards = [
        row
        for row in rows
        if row["deployment_id"] == DEPLOYMENT_ID
        and row["asset_role"] == "CHECKPOINT_FILE"
        and row["source_repo"] == MODEL_ID
        and row["source_revision"] == REVISION
    ]
    if len(shards) != 16:
        raise RuntimeError(f"expected 16 frozen shards, found {len(shards)}")
    total = sum(int(row["size_bytes"]) for row in shards)
    if total != 61_066_575_648:
        raise RuntimeError(f"unexpected frozen byte total: {total}")
    return shards


def receipt(shards: list[dict[str, str]], state: str, detail: str) -> None:
    verified: list[dict[str, str | int]] = []
    incomplete: list[dict[str, str | int]] = []
    for row in shards:
        final = MODEL_ROOT / row["asset_path"]
        temporary = final.with_name(final.name + ".incomplete")
        expected_size = int(row["size_bytes"])
        if final.is_file() and final.stat().st_size == expected_size:
            actual_sha256 = sha256_file(final)
            if actual_sha256 == row["sha256"]:
                verified.append(
                    {
                        "asset_path": row["asset_path"],
                        "size_bytes": expected_size,
                        "sha256": actual_sha256,
                        "local_path": str(final),
                    }
                )
                continue
        if temporary.is_file():
            incomplete.append(
                {
                    "asset_path": row["asset_path"],
                    "temporary_path": str(temporary),
                    "temporary_size_bytes": temporary.stat().st_size,
                    "expected_size_bytes": expected_size,
                }
            )
    atomic_json(
        PROGRESS_RECEIPT,
        {
            "schema_version": "C16_QWEN3_30B_A3B_PROGRESS_V1",
            "updated_at_utc": now(),
            "state": state,
            "detail": detail,
            "execution_boundary": "CPU_NETWORK_DISK_ONLY_NO_GPU_PROFILER_NVBIT_SIMULATOR_SASS_OR_FULL_ROI",
            "model_id": MODEL_ID,
            "revision": REVISION,
            "tokenizer_revision": REVISION,
            "frozen_shard_count": len(shards),
            "frozen_checkpoint_total_bytes": sum(int(row["size_bytes"]) for row in shards),
            "start_guard_min_available_bytes": MIN_START_FREE_BYTES,
            "pause_guard_min_available_bytes": PAUSE_FREE_BYTES,
            "background_max_rate": BACKGROUND_MAX_RATE,
            "available_bytes_observed": free_bytes(),
            "verified_shard_count": len(verified),
            "verified_shard_total_bytes": sum(int(row["size_bytes"]) for row in verified),
            "verified_shards": verified,
            "incomplete_files_are_not_assets": True,
            "incomplete_shards": incomplete,
        },
    )


def verify_existing(row: dict[str, str]) -> bool:
    final = MODEL_ROOT / row["asset_path"]
    if not final.exists():
        return False
    expected_size = int(row["size_bytes"])
    if final.stat().st_size != expected_size:
        raise RuntimeError(f"refusing to replace malformed final path: {final}")
    actual_sha256 = sha256_file(final)
    if actual_sha256 != row["sha256"]:
        raise RuntimeError(f"refusing to replace SHA-mismatched final path: {final}")
    return True


def download_one(row: dict[str, str]) -> None:
    if free_bytes() < PAUSE_FREE_BYTES:
        raise DiskPause("available space is below the 15 GiB protection threshold")
    final = MODEL_ROOT / row["asset_path"]
    temporary = final.with_name(final.name + ".incomplete")
    expected_size = int(row["size_bytes"])
    if temporary.exists() and temporary.stat().st_size > expected_size:
        raise RuntimeError(f"temporary file exceeds frozen size: {temporary}")
    url = f"https://huggingface.co/{MODEL_ID}/resolve/{REVISION}/{row['asset_path']}"
    subprocess.run(
        [
            "curl",
            "--http1.1",
            "--continue-at",
            "-",
            "--fail",
            "--location",
            "--connect-timeout",
            "15",
            "--retry",
            "8",
            "--retry-all-errors",
            "--limit-rate",
            BACKGROUND_MAX_RATE,
            "--output",
            str(temporary),
            url,
        ],
        check=True,
    )
    if not temporary.is_file() or temporary.stat().st_size != expected_size:
        receipt(frozen_shards(MANIFEST), "REJECTED_SIZE_MISMATCH", row["asset_path"])
        raise RuntimeError(f"whole-file size mismatch; temporary remains unaccepted: {temporary}")
    actual_sha256 = sha256_file(temporary)
    if actual_sha256 != row["sha256"]:
        receipt(frozen_shards(MANIFEST), "REJECTED_SHA256_MISMATCH", row["asset_path"])
        raise RuntimeError(f"whole-file SHA-256 mismatch; temporary remains unaccepted: {temporary}")
    os.replace(temporary, final)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-start-guard", action="store_true")
    parser.add_argument("--run", action="store_true")
    args = parser.parse_args()
    if args.check_start_guard == args.run:
        parser.error("choose exactly one of --check-start-guard or --run")
    shards = frozen_shards(MANIFEST)
    available = free_bytes()
    if available < MIN_START_FREE_BYTES:
        receipt(shards, "START_GUARD_BLOCKED", "available space below 85 GiB launch threshold")
        print(f"START_GUARD_BLOCKED available={available} required={MIN_START_FREE_BYTES}")
        return 2
    if args.check_start_guard:
        receipt(shards, "START_GUARD_PASS", "85 GiB launch threshold met; worker not started by guard check")
        print(f"START_GUARD_PASS available={available} required={MIN_START_FREE_BYTES}")
        return 0
    receipt(shards, "RUNNING", "serial resumable HTTP/1.1 worker started")
    try:
        for row in shards:
            if verify_existing(row):
                receipt(shards, "RUNNING", f"already verified; no repeat download: {row['asset_path']}")
                continue
            download_one(row)
            receipt(shards, "RUNNING", f"accepted whole-file SHA-256 match: {row['asset_path']}")
    except DiskPause as exc:
        receipt(shards, "PAUSED_LOW_DISK", str(exc))
        print(f"PAUSED_LOW_DISK: {exc}", file=sys.stderr)
        return 3
    except (OSError, subprocess.CalledProcessError, RuntimeError) as exc:
        receipt(shards, "STOPPED_UNACCEPTED_OR_TRANSPORT_ERROR", str(exc))
        print(f"STOPPED: {exc}", file=sys.stderr)
        return 1
    receipt(shards, "ALL_16_VERIFIED_READY_FOR_IMMUTABLE_WAVE2_RECEIPT", "all frozen shards closed")
    print("ALL_16_VERIFIED_READY_FOR_IMMUTABLE_WAVE2_RECEIPT")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
