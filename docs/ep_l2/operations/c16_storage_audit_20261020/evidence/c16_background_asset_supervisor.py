#!/usr/bin/env python3
"""Non-scientific, detached C16 A asset-download telemetry and readiness markers.

This program deliberately does *not* start, stop, retry, or reconfigure any
checkpoint download.  Download lifecycle belongs to a separately launched
worker; this supervisor only records the process/file state and writes local
READY markers once immutable receipts already exist.  It never touches Git or
the review-pack package directories.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path


ASSET_ROOT = Path("/workspace/c16_assets/c16-a")
BACKGROUND = ASSET_ROOT / "background"
LOGS = BACKGROUND / "logs"
PIDS = BACKGROUND / "pids"
STATUS = BACKGROUND / "status"
RECEIPTS = BACKGROUND / "receipts"
STATE = STATUS / ".telemetry_state.json"
HEARTBEAT = STATUS / "C16_A_BACKGROUND_STATUS.json"
IMMUTABLE = ASSET_ROOT / "download_logs" / "immutable_verified_receipts"

RAW_DEPLOYMENT = "c16_qwen25_7b_raw_reference"
AWQ_DEPLOYMENT = "c16_qwen25_7b_awq"
Q30_DEPLOYMENT = "c16_qwen3_30b_a3b_native_moe"
RAW_ROOT = ASSET_ROOT / "metadata" / "Qwen__Qwen2.5-7B-Instruct__a09a35458c702b33eeacc393d103063234e8bc28"
AWQ_ROOT = ASSET_ROOT / "metadata" / "Qwen__Qwen2.5-7B-Instruct-AWQ__b25037543e9394b818fdfca67ab2a00ecc7dd641"
Q30_ROOT = ASSET_ROOT / "metadata" / "Qwen__Qwen3-30B-A3B__ad44e777bcd18fa416d9da3bd8f70d33ebb85d39"

RAW = {
    "model-00001-of-00004.safetensors": 3945441440,
    "model-00002-of-00004.safetensors": 3864726352,
    "model-00003-of-00004.safetensors": 3864726424,
    "model-00004-of-00004.safetensors": 3556377672,
}
AWQ = {
    "model-00001-of-00002.safetensors": 3996422976,
    "model-00002-of-00002.safetensors": 1574406784,
}
Q30_FIRST = "model-00001-of-00016.safetensors"
Q30_FIRST_SIZE = 3999417504


def utcnow() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def atomic_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def read_json(path: Path, default: object) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def proc_rows() -> list[dict[str, str]]:
    output = subprocess.run(
        ["ps", "-eo", "pid=,ppid=,sid=,tty=,stat=,etimes=,args="],
        check=True,
        text=True,
        capture_output=True,
    ).stdout
    rows = []
    for line in output.splitlines():
        parts = line.strip().split(None, 6)
        if len(parts) == 7:
            pid, ppid, sid, tty, state, elapsed, command = parts
            rows.append({"pid": pid, "ppid": ppid, "sid": sid, "tty": tty, "process_state": state, "elapsed_seconds": elapsed, "command": command})
    return rows


def matching_process(rows: list[dict[str, str]], needle: str) -> dict[str, str] | None:
    return next((row for row in rows if needle in row["command"]), None)


def immutable_receipt(deployment: str, filename: str) -> Path | None:
    path = IMMUTABLE / deployment / f"{filename}.json"
    value = read_json(path, {})
    if isinstance(value, dict) and value.get("status") == "IMMUTABLE_VERIFIED":
        return path
    return None


def file_bytes(root: Path, filename: str) -> tuple[Path, int]:
    final = root / filename
    temporary = root / f"{filename}.curl.download"
    incomplete = root / f"{filename}.incomplete"
    for candidate in (final, temporary, incomplete):
        if candidate.is_file():
            return candidate, candidate.stat().st_size
    return temporary, 0


def update_measurement(previous: dict[str, object], worker_id: str, current: int, now: float) -> tuple[float, str]:
    before = previous.get(worker_id, {})
    if not isinstance(before, dict):
        before = {}
    prior_bytes = int(before.get("current_bytes", 0))
    prior_at = float(before.get("observed_epoch", now))
    last_growth = str(before.get("last_growth_timestamp", utcnow()))
    if current > prior_bytes:
        last_growth = utcnow()
    elapsed = max(now - prior_at, 0.001)
    throughput = max(current - prior_bytes, 0) / elapsed
    previous[worker_id] = {"current_bytes": current, "observed_epoch": now, "last_growth_timestamp": last_growth}
    return throughput, last_growth


def worker_record(
    previous: dict[str, object], rows: list[dict[str, str]], worker_id: str, root: Path, filename: str,
    expected: int, deployment: str, process_needle: str | None,
) -> dict[str, object]:
    now = time.time()
    receipt = immutable_receipt(deployment, filename)
    path, current = file_bytes(root, filename)
    # A curl command may name a model root containing both shards; a completed
    # immutable shard must not inherit the still-live sibling's PID.
    process = None if receipt else (matching_process(rows, process_needle) if process_needle else None)
    throughput, growth = update_measurement(previous, worker_id, current, now)
    if receipt:
        state = "IMMUTABLE_VERIFIED"
    elif process:
        state = "ACTIVE_GROWING_OR_OBSERVED"
    elif current:
        state = "PARTIAL_NO_LIVE_PROCESS_REQUIRES_15_MIN_OPERATOR_GATE"
    else:
        state = "NOT_STARTED_OR_NOT_OBSERVED"
    result: dict[str, object] = {
        "worker_id": worker_id,
        "deployment_id": deployment,
        "asset": filename,
        "path": str(path),
        "expected_bytes": expected,
        "current_bytes": current,
        "recent_throughput_Bps": round(throughput, 3),
        "last_growth_timestamp": growth,
        "retry_count": 0,
        "state": state,
        "immutable_receipt_path": str(receipt) if receipt else None,
        "restart_policy": "NO_ACTION_WHILE_PROCESS_ACTIVE; resume same partial only after ~15m no growth and confirmed dead connection/process",
    }
    if process:
        result["process"] = process
        (PIDS / f"{worker_id}.pid").write_text(process["pid"] + "\n", encoding="utf-8")
    atomic_json(STATUS / "workers" / f"{worker_id}.json", {"observed_at_utc": utcnow(), **result})
    return result


def write_ready_marker(name: str, deployment: str, revision: str, receipts: list[Path], package_id: str) -> None:
    marker = RECEIPTS / name
    if marker.exists():
        return
    atomic_json(marker, {
        "schema_version": "C16_A_BACKGROUND_READY_MARKER_V1",
        "operational_only": True,
        "deployment_id": deployment,
        "fixed_revision": revision,
        "immutable_receipt_paths": [str(path) for path in receipts],
        "expected_package_identity": package_id,
        "created_at_utc": utcnow(),
        "prohibitions": ["NO_GIT_COMMIT", "NO_GIT_PUSH", "NO_GPU", "NO_PROFILER", "NO_NVBIT", "NO_SIMULATOR"],
    })


def observe_once() -> None:
    for directory in (LOGS, PIDS, STATUS, RECEIPTS, STATUS / "workers"):
        directory.mkdir(parents=True, exist_ok=True)
    previous = read_json(STATE, {})
    if not isinstance(previous, dict):
        previous = {}
    rows = proc_rows()
    workers = [
        worker_record(previous, rows, f"raw_{name}", RAW_ROOT, name, size, RAW_DEPLOYMENT, None)
        for name, size in RAW.items()
    ]
    workers.extend(
        worker_record(previous, rows, f"awq_{name}", AWQ_ROOT, name, size, AWQ_DEPLOYMENT, str(AWQ_ROOT))
        for name, size in AWQ.items()
    )
    workers.append(worker_record(previous, rows, "qwen3_30b_shard_01", Q30_ROOT, Q30_FIRST, Q30_FIRST_SIZE, Q30_DEPLOYMENT, "Qwen3-30B-A3B"))
    raw_receipts = [immutable_receipt(RAW_DEPLOYMENT, name) for name in RAW]
    awq_receipts = [immutable_receipt(AWQ_DEPLOYMENT, name) for name in AWQ]
    q30_receipts = list((IMMUTABLE / Q30_DEPLOYMENT).glob("*.json"))
    if all(raw_receipts):
        write_ready_marker("P2_READY.json", RAW_DEPLOYMENT, "a09a35458c702b33eeacc393d103063234e8bc28", [p for p in raw_receipts if p], "C16_GPU_PACKAGE_P2")
    if all(awq_receipts):
        write_ready_marker("P3_READY.json", AWQ_DEPLOYMENT, "b25037543e9394b818fdfca67ab2a00ecc7dd641", [p for p in awq_receipts if p], "C16_GPU_PACKAGE_P3")
    if len(q30_receipts) == 16:
        write_ready_marker("QWEN3_30B_WAVE2_READY.json", Q30_DEPLOYMENT, "ad44e777bcd18fa416d9da3bd8f70d33ebb85d39", sorted(q30_receipts), "C16_QWEN3_30B_WAVE2_IMMUTABLE_PACKAGE")
    disk = os.statvfs(ASSET_ROOT)
    finalizer = matching_process(rows, "c16_wave1_shard_finalizer.py")
    q30 = matching_process(rows, "c16_qwen3_30b_downloader.py --run")
    (PIDS / "c16_background_asset_supervisor.pid").write_text(f"{os.getpid()}\\n", encoding="utf-8")
    if finalizer:
        (PIDS / "c16_wave1_shard_finalizer.pid").write_text(finalizer["pid"] + "\\n", encoding="utf-8")
    if q30:
        (PIDS / "c16_qwen3_30b_downloader.pid").write_text(q30["pid"] + "\\n", encoding="utf-8")
    status = {
        "schema_version": "C16_A_BACKGROUND_STATUS_V1",
        "operational_only_not_scientific_artifact": True,
        "observed_at_utc": utcnow(),
        "available_disk_bytes": disk.f_bavail * disk.f_frsize,
        "workers": workers,
        "finalizer": finalizer,
        "qwen3_downloader": q30,
        "verified_shard_count": sum(1 for worker in workers if worker["state"] == "IMMUTABLE_VERIFIED"),
        "p2_ready": (RECEIPTS / "P2_READY.json").is_file(),
        "p3_ready": (RECEIPTS / "P3_READY.json").is_file(),
        "qwen3_30b_verified_shard_count": len(q30_receipts),
        "last_error": None,
        "limits": {"qwen3_start_gate_bytes": 85 * 1024**3, "qwen3_pause_gate_bytes": 15 * 1024**3, "qwen3_max_concurrency_before_p2_p3": 1},
    }
    atomic_json(HEARTBEAT, status)
    atomic_json(STATE, previous)


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
