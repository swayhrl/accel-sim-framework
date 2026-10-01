#!/usr/bin/env python3
"""Bounded CPU-only discovery and freezing of the first finalized Lane6 contract."""

import argparse
import hashlib
import json
import subprocess
import time
from pathlib import Path


FILENAME = "C16_STAGEA_DENSE_FIRST_TIER0_109_CONTRACT_V1.json"
ALLOWLIST = ["MP01", "MP02", "MP03", "MP05"]
AUTHORITIES = [
    "137e3414c9c8e59cf1b167e5acc14149fb6273d6",
    "9d5aa2f36e22a1a8fcc253d6df865160b5dba797",
    "c3f625e46adb8d5c4082ded8b61858c710e1f4e9",
    "3f62f909a474e4c56695ffacf36ddcb5d7b5f147",
    "f63d39c8d90ced038445c264fa8242c524a1aa6f",
    "8b677cfa541877f559614f7bf22a40dd11cebd56",
]


def run(repo, *args):
    return subprocess.check_output(list(args), cwd=repo, text=True)


def get_allowlist(data):
    for key in ("point_allowlist_in_order", "point_allowlist", "authorized_points", "points"):
        value = data.get(key)
        if isinstance(value, list):
            return value
    execution = data.get("execution", {})
    for key in ("point_allowlist", "authorized_points"):
        if isinstance(execution.get(key), list):
            return execution[key]
    return None


def get_cap_seconds(data):
    candidates = [
        data.get("gpu_active_cap_seconds"),
        data.get("total_gpu_active_cap_seconds"),
        data.get("gpu_active_cap_minutes", 0) * 60 if data.get("gpu_active_cap_minutes") is not None else None,
    ]
    budget = data.get("budget", {})
    candidates += [budget.get("total_gpu_active_cap_seconds"), budget.get("gpu_active_cap_seconds")]
    gpu_budget = data.get("gpu_budget", {})
    candidates += [gpu_budget.get("total_gpu_active_seconds_cap"), gpu_budget.get("total_gpu_active_cap_seconds")]
    return next((int(value) for value in candidates if value), None)


def preliminary_valid(data, raw_text):
    status = str(data.get("status", ""))
    finalized = ("FINALIZED" in status or status == "AUTHORIZED_BY_PROJECT_REVIEW"
                 or data.get("finalized") is True)
    schema_exact = data.get("schema") == "C16_STAGEA_DENSE_FIRST_TIER0_109_CONTRACT_V1"
    authorized = data.get("execution_authorized") is True or data.get("authorized_for_execution") is True
    allowlist = get_allowlist(data)
    cap = get_cap_seconds(data)
    authorities = all(value in raw_text for value in AUTHORITIES)
    return schema_exact and finalized and authorized and allowlist == ALLOWLIST and cap is not None and cap <= 540 and authorities


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--interval-seconds", type=int, default=300)
    parser.add_argument("--max-minutes", type=int, default=180)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    attempts = max(1, args.max_minutes * 60 // args.interval_seconds)
    tokens = ("stagea", "dense", "first", "tier0", "contract", "finalization")
    seen = []
    for attempt in range(attempts + 1):
        output = run(args.repo, "git", "ls-remote", "--heads", "origin")
        refs = []
        for line in output.splitlines():
            sha, ref = line.split("\t", 1)
            lowered = ref.lower()
            if all(token in lowered for token in tokens):
                refs.append((ref, sha))
        for ref, commit in sorted(refs):
            if (ref, commit) in seen:
                continue
            seen.append((ref, commit))
            subprocess.run(["git", "fetch", "origin", commit], cwd=args.repo, check=True,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            paths = run(args.repo, "git", "ls-tree", "-r", "--name-only", commit).splitlines()
            matches = [path for path in paths if path.endswith("/" + FILENAME) or path == FILENAME]
            if len(matches) != 1:
                continue
            raw = subprocess.check_output(["git", "show", f"{commit}:{matches[0]}"], cwd=args.repo)
            data = json.loads(raw)
            if not preliminary_valid(data, raw.decode("utf-8")):
                continue
            tree = run(args.repo, "git", "rev-parse", f"{commit}^{{tree}}").strip()
            digest = hashlib.sha256(raw).hexdigest()
            contract_path = args.output_dir / FILENAME
            contract_path.write_bytes(raw)
            receipt = {
                "status": "FROZEN_PRELIMINARY_FINALIZED_CONTRACT",
                "remote_ref": ref,
                "contract_commit": commit,
                "contract_tree": tree,
                "contract_path_in_commit": matches[0],
                "contract_json_sha256": digest,
                "poll_attempt": attempt,
                "full_scientific_validation_required_before_gpu": True,
            }
            (args.output_dir / "CONTRACT_DISCOVERY_RECEIPT.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
            print(json.dumps(receipt, sort_keys=True))
            return
        if attempt < attempts:
            time.sleep(args.interval_seconds)
    timeout = {"status": "CONTRACT_WAIT_TIMEOUT_STOP", "attempts": attempts + 1,
               "interval_seconds": args.interval_seconds, "max_minutes": args.max_minutes, "seen_candidates": seen}
    (args.output_dir / "CONTRACT_WAIT_TIMEOUT_STOP.json").write_text(json.dumps(timeout, indent=2, sort_keys=True) + "\n")
    print(json.dumps(timeout, sort_keys=True))
    raise SystemExit(75)


if __name__ == "__main__":
    main()
