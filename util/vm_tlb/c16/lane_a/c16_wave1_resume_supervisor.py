#!/usr/bin/env python3
"""Guarded future resume entrypoint for one stalled C16 Wave-1 curl target.

It is intentionally not a polling daemon and is never used for a live,
normally growing transfer.  An operator must explicitly confirm inactivity
after the background status has shown no byte growth for fifteen minutes.
The existing finalizer retains exclusive responsibility for size/SHA closure.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path


ROOT = Path("/workspace/c16_assets/c16-a")
STATUS = ROOT / "background/status"
IMMUTABLE = ROOT / "download_logs/immutable_verified_receipts"
SPECS = {
    "raw-1": ("c16_qwen25_7b_raw_reference", "Qwen/Qwen2.5-7B-Instruct", "a09a35458c702b33eeacc393d103063234e8bc28", "model-00001-of-00004.safetensors"),
    "raw-2": ("c16_qwen25_7b_raw_reference", "Qwen/Qwen2.5-7B-Instruct", "a09a35458c702b33eeacc393d103063234e8bc28", "model-00002-of-00004.safetensors"),
    "raw-3": ("c16_qwen25_7b_raw_reference", "Qwen/Qwen2.5-7B-Instruct", "a09a35458c702b33eeacc393d103063234e8bc28", "model-00003-of-00004.safetensors"),
    "raw-4": ("c16_qwen25_7b_raw_reference", "Qwen/Qwen2.5-7B-Instruct", "a09a35458c702b33eeacc393d103063234e8bc28", "model-00004-of-00004.safetensors"),
    "awq-1": ("c16_qwen25_7b_awq", "Qwen/Qwen2.5-7B-Instruct-AWQ", "b25037543e9394b818fdfca67ab2a00ecc7dd641", "model-00001-of-00002.safetensors"),
    "awq-2": ("c16_qwen25_7b_awq", "Qwen/Qwen2.5-7B-Instruct-AWQ", "b25037543e9394b818fdfca67ab2a00ecc7dd641", "model-00002-of-00002.safetensors"),
}


def live_command_contains(text: str) -> bool:
    output = subprocess.run(["ps", "-C", "curl", "-o", "args="], text=True, capture_output=True, check=False).stdout
    return text in output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("target", choices=sorted(SPECS))
    parser.add_argument("--confirmed-inactive", action="store_true")
    parser.add_argument("--run", action="store_true")
    args = parser.parse_args()
    deployment, repo, revision, asset = SPECS[args.target]
    receipt = IMMUTABLE / deployment / f"{asset}.json"
    if receipt.is_file():
        raise SystemExit("refuse: immutable receipt already exists; never re-download a verified shard")
    model_root = ROOT / "metadata" / (repo.replace("/", "__") + "__" + revision)
    partial = model_root / f"{asset}.curl.download"
    if live_command_contains(str(partial)):
        raise SystemExit("refuse: curl remains live; do not disturb a normal or ambiguous transfer")
    if not args.confirmed_inactive:
        raise SystemExit("refuse: pass --confirmed-inactive only after >=15m no-growth plus dead process/connection confirmation")
    url = f"https://huggingface.co/{repo}/resolve/{revision}/{asset}"
    command = ["curl", "--http1.1", "--continue-at", "-", "--fail", "--location", "--connect-timeout", "15", "--retry", "8", "--retry-all-errors", "--output", str(partial), url]
    record = {"started_at_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"), "target": args.target, "fixed_revision": revision, "partial_path": str(partial), "exact_command": command, "retry_count_bound": 8, "finalization": "delegated_to_unique_wave1_finalizer_size_then_single_sha256"}
    status = STATUS / "resume" / f"{args.target}.json"
    status.parent.mkdir(parents=True, exist_ok=True)
    status.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if not args.run:
        print(json.dumps(record, sort_keys=True))
        return 0
    return subprocess.run(command, check=False).returncode


if __name__ == "__main__":
    sys.exit(main())
