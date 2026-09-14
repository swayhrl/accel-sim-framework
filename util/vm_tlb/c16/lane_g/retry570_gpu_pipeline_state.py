#!/usr/bin/env python3
"""Atomic shared GPU-pipeline and copyback state for Recovery-V3 lanes.

Lane A/G owns fresh GPU-window publication.  Lane B advances an already
published copyback item; it must never invent a second queue.  The two JSON
documents are lock-protected and atomically replaced, so readers observe a
complete state rather than an rsync-era partial write.
"""
from __future__ import annotations

import argparse
import fcntl
import json
import os
import tempfile
import time
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, sha256_file


STATE_NAME = "GPU_PIPELINE_STATE.json"
QUEUE_NAME = "COPYBACK_QUEUE.json"
QUEUE_STATES = ("COPYBACK_READY", "COPYING", "LOCAL_SHA_CLOSED", "REMOTE_CLEANED")


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def load(path: Path, *, default: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return default
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"shared state is unreadable: {path}") from exc
    if not isinstance(value, dict):
        raise ContractError(f"shared state is not an object: {path}")
    return value


def with_lock(control: Path):
    control.mkdir(parents=True, exist_ok=True)
    return (control / ".GPU_PIPELINE_STATE.lock").open("a+", encoding="utf-8")


def refresh_state(control: Path, args: argparse.Namespace) -> Path:
    path = control / STATE_NAME
    with with_lock(control) as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            value = {
                "schema_version": "C16_GPU_PIPELINE_STATE_V1",
                "git_head": args.git_head,
                "timestamp": time.time(),
                "gpu_active_job": args.gpu_active_job,
                "gpu_ready_queue_count": args.gpu_ready_queue_count,
                "next_gpu_job": args.next_gpu_job,
                "measurement_active": args.measurement_active,
                "active_gpu_process_count": args.active_gpu_process_count,
                "gpu_idle_seconds": args.gpu_idle_seconds,
                "remote_data_free_bytes": args.remote_data_free_bytes,
                "transfer_slot_granted": args.transfer_slot_granted,
            }
            atomic_json(path, value)
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
    return path


def copyback_key(args: argparse.Namespace) -> str:
    return "|".join((args.run_id, args.stage, args.remote_path))


def queue_ready(control: Path, args: argparse.Namespace) -> Path:
    remote = Path(args.remote_path)
    if not remote.is_file():
        raise ContractError("cannot publish a copyback item for a missing remote artifact")
    actual_bytes, actual_sha = remote.stat().st_size, sha256_file(remote)
    if actual_bytes != args.bytes or actual_sha != args.remote_sha256:
        raise ContractError("copyback item remote size/SHA does not match the actual artifact")
    path = control / QUEUE_NAME
    with with_lock(control) as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            value = load(path, default={"schema_version": "C16_COPYBACK_QUEUE_V1", "items": {}})
            if value.get("schema_version") != "C16_COPYBACK_QUEUE_V1" or not isinstance(value.get("items"), dict):
                raise ContractError("copyback queue schema differs")
            key = copyback_key(args)
            existing = value["items"].get(key)
            if existing and existing.get("state") != "COPYBACK_READY":
                raise ContractError("Lane A refuses to overwrite Lane B copyback progress")
            value["items"][key] = {
                "run_id": args.run_id, "model": args.model, "scenario": args.scenario,
                "stage": args.stage, "remote_path": str(remote), "bytes": actual_bytes,
                "remote_sha256": actual_sha, "state": "COPYBACK_READY", "published_at": time.time(),
            }
            atomic_json(path, value)
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    state = sub.add_parser("state")
    state.add_argument("--control-root", type=Path, required=True)
    state.add_argument("--git-head", required=True)
    state.add_argument("--gpu-active-job", required=True)
    state.add_argument("--gpu-ready-queue-count", type=int, required=True)
    state.add_argument("--next-gpu-job", required=True)
    state.add_argument("--measurement-active", choices=("true", "false"), required=True)
    state.add_argument("--active-gpu-process-count", type=int, required=True)
    state.add_argument("--gpu-idle-seconds", type=float, required=True)
    state.add_argument("--remote-data-free-bytes", type=int, required=True)
    state.add_argument("--transfer-slot-granted", choices=("true", "false"), required=True)
    ready = sub.add_parser("copyback-ready")
    ready.add_argument("--control-root", type=Path, required=True)
    ready.add_argument("--run-id", required=True); ready.add_argument("--model", required=True)
    ready.add_argument("--scenario", required=True); ready.add_argument("--stage", required=True)
    ready.add_argument("--remote-path", required=True); ready.add_argument("--bytes", type=int, required=True)
    ready.add_argument("--remote-sha256", required=True)
    args = parser.parse_args()
    if args.command == "state":
        if (args.gpu_ready_queue_count < 0 or args.active_gpu_process_count < 0
                or args.gpu_idle_seconds < 0 or args.remote_data_free_bytes < 0):
            raise SystemExit("counts must be non-negative")
        args.measurement_active = args.measurement_active == "true"
        args.transfer_slot_granted = args.transfer_slot_granted == "true"
        print(refresh_state(args.control_root, args))
    else:
        print(queue_ready(args.control_root, args))


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        raise SystemExit(f"FAIL GPU pipeline shared state: {exc}")
