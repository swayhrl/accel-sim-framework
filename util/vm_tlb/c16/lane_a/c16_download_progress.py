#!/usr/bin/env python3
"""Passive download telemetry for C16 A checkpoint workers.

This program has no signal, retry, deletion, or download capability.  It
periodically records actual process/path state so the 15-minute recovery rule
can be evaluated without disturbing an existing transfer.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path


MANIFEST = Path(
    "docs/vm_tlb/review_packs/C16_MULTIMODEL_NATIVE/lane_a/"
    "MODEL_ASSET_MANIFEST.tsv"
)
LOG_ROOT = Path("/workspace/c16_assets/c16-a/download_logs")
IMMUTABLE_RECEIPT_ROOT = LOG_ROOT / "immutable_verified_receipts"
PROGRESS_TSV = LOG_ROOT / "DOWNLOAD_PROGRESS.tsv"
STATE_JSON = LOG_ROOT / "DOWNLOAD_PROGRESS_STATE.json"
STALL_SECONDS = 15 * 60
QWEN30_DEPLOYMENT = "c16_qwen3_30b_a3b_native_moe"
WAVE1_DEPLOYMENTS = {"c16_qwen25_7b_raw_reference", "c16_qwen25_7b_awq"}


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def atomic_tsv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    os.replace(temporary, path)


def frozen_workers() -> list[dict[str, str]]:
    with MANIFEST.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    result = []
    for row in rows:
        if row["asset_role"] != "CHECKPOINT_FILE":
            continue
        if row["deployment_id"] not in WAVE1_DEPLOYMENTS | {QWEN30_DEPLOYMENT}:
            continue
        if row["deployment_id"] in WAVE1_DEPLOYMENTS and row["local_path"] != "NA":
            continue
        root = Path("/workspace/c16_assets/c16-a/metadata") / (
            row["source_repo"].replace("/", "__") + "__" + row["source_revision"]
        )
        suffix = ".incomplete" if row["deployment_id"] == QWEN30_DEPLOYMENT else ".curl.download"
        temporary = root / f"{row['asset_path']}{suffix}"
        if row["deployment_id"] == QWEN30_DEPLOYMENT and row["asset_path"] != "model-00001-of-00016.safetensors":
            continue
        result.append({**row, "temporary_path": str(temporary)})
    if len(result) != 6:
        raise RuntimeError(f"expected five Wave-1 plus one active Wave-2 worker target, found {len(result)}")
    return result


def live_curl_processes() -> dict[str, tuple[str, str]]:
    result = subprocess.run(
        ["ps", "-C", "curl", "-o", "pid=,etimes=,args="],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    value: dict[str, tuple[str, str]] = {}
    for line in result.stdout.splitlines():
        parts = line.strip().split(maxsplit=2)
        if len(parts) != 3:
            continue
        pid, elapsed, args = parts
        value[args] = (pid, elapsed)
    return value


def process_for_path(processes: dict[str, tuple[str, str]], path: str) -> tuple[str, str] | None:
    for args, identity in processes.items():
        if path in args:
            return identity
    return None


def configured_retry_count(row: dict[str, str]) -> str:
    # Wave-1 legacy commands contain no curl --retry flag.  The current 30B
    # worker has an explicit --retry 8 policy; a live retry count is only
    # recorded from explicit log evidence, never inferred from a stagnant byte
    # count.
    if row["deployment_id"] in WAVE1_DEPLOYMENTS:
        return "0_CONFIGURED_LEGACY"
    log = LOG_ROOT / "qwen3_30b_a3b.worker.log"
    if not log.is_file():
        return "0_NO_LOG_EVIDENCE"
    text = log.read_text(encoding="utf-8", errors="replace")
    return str(text.lower().count("retrying"))


def immutable_final_receipt(row: dict[str, str]) -> Path | None:
    suffix = ".incomplete" if row["deployment_id"] == QWEN30_DEPLOYMENT else ".curl.download"
    temporary = Path(row["temporary_path"])
    final = Path(str(temporary)[: -len(suffix)])
    receipt_path = IMMUTABLE_RECEIPT_ROOT / row["deployment_id"] / f"{row['asset_path']}.json"
    if not final.is_file() or not receipt_path.is_file():
        return None
    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if (
        receipt.get("status") == "IMMUTABLE_VERIFIED"
        and receipt.get("local_path") == str(final)
        and receipt.get("expected_size_bytes") == int(row["size_bytes"])
        and receipt.get("sha256") == row["sha256"]
        and final.stat().st_size == int(row["size_bytes"])
    ):
        return receipt_path
    return None


def observe_once() -> None:
    workers = frozen_workers()
    try:
        state = json.loads(STATE_JSON.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        state = {"workers": {}}
    previous = state.get("workers", {})
    observed_at = now()
    observed_epoch = time.time()
    processes = live_curl_processes()
    output: list[dict[str, str]] = []
    next_state: dict[str, dict] = {}
    for row in workers:
        key = f"{row['deployment_id']}:{row['asset_path']}"
        temporary = Path(row["temporary_path"])
        immutable_receipt = immutable_final_receipt(row)
        current = temporary.stat().st_size if temporary.is_file() else 0
        prior = previous.get(key, {})
        prior_current = int(prior.get("current_bytes", 0))
        prior_epoch = float(prior.get("observed_epoch", observed_epoch))
        elapsed_window = max(observed_epoch - prior_epoch, 0.001)
        grew = current > prior_current
        last_growth = observed_at if grew else prior.get("last_growth_timestamp", observed_at)
        rate = (current - prior_current) / elapsed_window if grew else 0.0
        process = process_for_path(processes, str(temporary))
        if immutable_receipt is not None:
            current = int(row["size_bytes"])
            pid, process_elapsed = "NA", "COMPLETE"
            state_name = "IMMUTABLE_VERIFIED_FINAL"
            restart = "NOT_APPLICABLE_IMMUTABLE_RECEIPT_CLOSED"
            last_growth = prior.get("last_growth_timestamp", observed_at)
            last_growth_epoch = float(prior.get("last_growth_epoch", observed_epoch))
            rate = 0.0
        elif process is not None:
            pid, process_elapsed = process
            state_name = "ACTIVE_GROWING" if grew else "ACTIVE_NO_NEW_BYTES_THIS_SAMPLE"
            restart = "NOT_ELIGIBLE_PROCESS_ACTIVE"
        else:
            pid, process_elapsed = "NA", "NA"
            no_growth_seconds = observed_epoch - float(prior.get("last_growth_epoch", observed_epoch))
            if no_growth_seconds >= STALL_SECONDS:
                state_name = "INACTIVE_STALLED_15_MINUTES"
                restart = "ELIGIBLE_ONLY_FOR_SINGLE_RESUME_RESTART_AFTER_OPERATOR_REVIEW"
            else:
                state_name = "INACTIVE_AWAITING_15_MINUTE_STALL_CONFIRMATION"
                restart = "NOT_YET_ELIGIBLE"
        if immutable_receipt is None:
            last_growth_epoch = observed_epoch if grew else float(prior.get("last_growth_epoch", observed_epoch))
        next_state[key] = {
            "current_bytes": current,
            "observed_epoch": observed_epoch,
            "last_growth_epoch": last_growth_epoch,
            "last_growth_timestamp": last_growth,
        }
        output.append(
            {
                "observed_at_utc": observed_at,
                "worker_id": key,
                "priority": "WAVE1_HIGHEST" if row["deployment_id"] in WAVE1_DEPLOYMENTS else "WAVE2_LOW_BACKGROUND",
                "model_id": row["source_repo"],
                "revision": row["source_revision"],
                "asset_path": row["asset_path"],
                "expected_bytes": row["size_bytes"],
                "current_bytes": str(current),
                "elapsed_seconds": process_elapsed,
                "retry_count": configured_retry_count(row),
                "recent_throughput_Bps": f"{rate:.3f}",
                "last_growth_timestamp": last_growth,
                "process_pid": pid,
                "worker_state": state_name,
                "restart_policy": restart,
                "temporary_path": str(temporary),
                "immutable_receipt_path": str(immutable_receipt) if immutable_receipt else "NA",
            }
        )
    fields = list(output[0])
    atomic_tsv(PROGRESS_TSV, fields, output)
    atomic_json(STATE_JSON, {"schema_version": "C16_DOWNLOAD_PROGRESS_STATE_V1", "workers": next_state})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--watch-seconds", type=int, default=60)
    args = parser.parse_args()
    while True:
        observe_once()
        if args.once:
            return 0
        time.sleep(args.watch_seconds)


if __name__ == "__main__":
    raise SystemExit(main())
