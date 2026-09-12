#!/usr/bin/env python3
"""Finalize completed Wave-1 curl streams without controlling their workers.

The existing raw/AWQ curl jobs own their network transfers.  This companion
only observes their final temporary paths.  A temporary shard can be promoted
only after no live curl command names it and its frozen manifest byte count and
SHA-256 both match.  It never starts, stops, or restarts a transfer.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path


WAVE1_IDS = {
    "c16_qwen25_7b_raw_reference",
    "c16_qwen25_7b_awq",
}
MANIFEST = Path(
    "docs/vm_tlb/review_packs/C16_MULTIMODEL_NATIVE/lane_a/"
    "MODEL_ASSET_MANIFEST.tsv"
)
PROGRESS_RECEIPT = Path(
    "/workspace/c16_assets/c16-a/download_logs/"
    "C16_WAVE1_SHARD_FINALIZATION_PROGRESS.json"
)


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def frozen_rows() -> list[dict[str, str]]:
    with MANIFEST.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    result = [
        row
        for row in rows
        if row["deployment_id"] in WAVE1_IDS
        and row["asset_role"] == "CHECKPOINT_FILE"
        and row["local_path"] == "NA"
    ]
    if len(result) != 5:
        raise RuntimeError(f"expected five unresolved Wave-1 shards, found {len(result)}")
    return result


def live_curl_commands() -> str:
    result = subprocess.run(
        ["ps", "-C", "curl", "-o", "args="],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.stdout


def observe(rows: list[dict[str, str]]) -> tuple[list[dict], bool]:
    live = live_curl_commands()
    records: list[dict] = []
    all_closed = True
    for row in rows:
        final = Path(row["local_path"]) if row["local_path"] != "NA" else None
        # A remote-only source row intentionally has no manifest local path.
        # Resolve its model root from its sibling metadata files instead.
        root = Path("/workspace/c16_assets/c16-a/metadata") / (
            row["source_repo"].replace("/", "__") + "__" + row["source_revision"]
        )
        target = root / row["asset_path"]
        temporary = target.with_name(target.name + ".curl.download")
        expected_size = int(row["size_bytes"])
        record = {
            "deployment_id": row["deployment_id"],
            "asset_path": row["asset_path"],
            "expected_size_bytes": expected_size,
            "expected_sha256": row["sha256"],
            "final_path": str(target),
            "temporary_path": str(temporary),
        }
        if target.is_file():
            if target.stat().st_size == expected_size and sha256_file(target) == row["sha256"]:
                record["state"] = "ALREADY_ACCEPTED"
                records.append(record)
                continue
            record["state"] = "FINAL_PATH_INVALID_DO_NOT_OVERWRITE"
            all_closed = False
            records.append(record)
            continue
        if str(temporary) in live:
            record["state"] = "TRANSFER_ACTIVE_UNACCEPTED"
            record["temporary_size_bytes"] = temporary.stat().st_size if temporary.is_file() else 0
            all_closed = False
            records.append(record)
            continue
        if not temporary.is_file():
            record["state"] = "TEMPORARY_NOT_PRESENT_UNACCEPTED"
            all_closed = False
            records.append(record)
            continue
        actual_size = temporary.stat().st_size
        record["temporary_size_bytes"] = actual_size
        if actual_size != expected_size:
            record["state"] = "TRANSFER_ENDED_SIZE_MISMATCH_UNACCEPTED"
            all_closed = False
            records.append(record)
            continue
        actual_sha256 = sha256_file(temporary)
        record["actual_sha256"] = actual_sha256
        if actual_sha256 != row["sha256"]:
            record["state"] = "TRANSFER_ENDED_SHA256_MISMATCH_UNACCEPTED"
            all_closed = False
            records.append(record)
            continue
        os.replace(temporary, target)
        record["state"] = "ACCEPTED_EXACT_SIZE_AND_SHA256"
        records.append(record)
    return records, all_closed


def write_receipt(records: list[dict], all_closed: bool) -> None:
    atomic_json(
        PROGRESS_RECEIPT,
        {
            "schema_version": "C16_WAVE1_SHARD_FINALIZATION_PROGRESS_V1",
            "updated_at_utc": now(),
            "execution_boundary": "CPU_NETWORK_DISK_ONLY_NO_GPU_PROFILER_NVBIT_SIMULATOR_SASS_OR_FULL_ROI",
            "all_unresolved_shards_closed": all_closed,
            "records": records,
            "rule": "curl-owned temporary files become local checkpoint files only after curl exits and exact frozen size plus SHA-256 match",
        },
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--watch-seconds", type=int, default=15)
    args = parser.parse_args()
    rows = frozen_rows()
    while True:
        records, all_closed = observe(rows)
        write_receipt(records, all_closed)
        if all_closed or args.once:
            return 0
        time.sleep(args.watch_seconds)


if __name__ == "__main__":
    raise SystemExit(main())
