#!/usr/bin/env python3
"""Low-impact Lane-C selector-freeze watcher for C16-P.

The watcher is intentionally observational: it polls only the C remote head
until that immutable head changes, then records whether an exact commit in the
new range contains a syntactically complete ``SOURCE_SHA_FROZEN_BEFORE_AWQ_UNSEAL``
event.  It never changes C, does not read AWQ payloads, and never applies a
selector.  A P release still performs its own full hash and dependency checks.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


FREEZE_PATH = "docs/vm_tlb/review_packs/C16_MULTIMODEL_NATIVE/lane_c/P_TRAIN_SELECTOR_SOURCE_FREEZE.json"
POLICY_PATH = "docs/vm_tlb/review_packs/C16_MULTIMODEL_NATIVE/lane_c/G_TARGET_SELECTION_POLICY_V1.json"


class MonitorError(RuntimeError):
    pass


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False) as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")
        temporary = Path(handle.name)
    os.replace(temporary, path)


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MonitorError(f"cannot read state: {exc}") from exc
    if not isinstance(value, dict):
        raise MonitorError("state root is not an object")
    return value


def git(repo: Path, *args: str, binary: bool = False) -> str | bytes:
    result = subprocess.run(["git", "-C", str(repo), *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if result.returncode:
        raise MonitorError(result.stderr.decode(errors="replace").strip())
    return result.stdout if binary else result.stdout.decode("utf-8")


def remote_head(repo: Path, branch: str) -> str:
    output = str(git(repo, "ls-remote", "--heads", "origin", branch))
    rows = [line.split("\t", 1) for line in output.splitlines() if line]
    if len(rows) != 1 or rows[0][1] != f"refs/heads/{branch}":
        raise MonitorError("C remote head is not uniquely resolvable")
    return rows[0][0]


def git_bytes(repo: Path, commit: str, path: str) -> bytes:
    return git(repo, "show", f"{commit}:{path}", binary=True)  # type: ignore[return-value]


def candidate(repo: Path, commit: str) -> dict[str, Any] | None:
    try:
        freeze_bytes = git_bytes(repo, commit, FREEZE_PATH)
        policy_bytes = git_bytes(repo, commit, POLICY_PATH)
        freeze, policy = json.loads(freeze_bytes), json.loads(policy_bytes)
    except (MonitorError, json.JSONDecodeError):
        return None
    if not isinstance(freeze, dict) or not isinstance(policy, dict):
        return None
    if freeze.get("state") != "SOURCE_SHA_FROZEN_BEFORE_AWQ_UNSEAL":
        return None
    if freeze.get("primary_g_target_selector") != "SELECTOR_R" or freeze.get("primary_g_target_budget") != "B48":
        return None
    if policy.get("schema_version") != "G_TARGET_SELECTION_POLICY_V1" or policy.get("PRIMARY_G_TARGET_SELECTOR") != "SELECTOR_R" or policy.get("PRIMARY_G_TARGET_BUDGET") != "B48":
        return None
    return {
        "candidate_commit": commit,
        "freeze_path": FREEZE_PATH,
        "freeze_sha256": sha256_bytes(freeze_bytes),
        "policy_path": POLICY_PATH,
        "policy_sha256": sha256_bytes(policy_bytes),
        "state": freeze["state"],
        "selector_source_commit": freeze.get("selector_source_commit"),
        "selector_source_sha256": freeze.get("selector_code_sha256"),
        "primary_selector": "SELECTOR_R",
        "primary_budget": "B48",
        "action": "P_FULL_CLOSURE_VERIFICATION_REQUIRED_NO_PAYLOAD_READ",
    }


def commits_since(repo: Path, previous: str | None, current: str) -> list[str]:
    range_value = current if previous is None else f"{previous}..{current}"
    return [line for line in str(git(repo, "rev-list", "--reverse", range_value)).splitlines() if line]


def inspect(repo: Path, branch: str, previous: str | None, advertised: str) -> dict[str, Any]:
    git(repo, "fetch", "origin", branch)
    fetched = str(git(repo, "rev-parse", "FETCH_HEAD")).strip()
    if fetched != advertised:
        raise MonitorError(f"remote moved during fetch ({advertised} -> {fetched})")
    candidates = [value for commit in commits_since(repo, previous, fetched) if (value := candidate(repo, commit)) is not None]
    return {"checked_at_utc": now(), "branch": branch, "previous_head": previous, "head": fetched, "freeze_candidates": candidates,
            "action": "NO_P_UNSEAL_WITHOUT_FULL_RECEIPT_CLOSURE"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--branch", required=True)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--audit-dir", type=Path, required=True)
    parser.add_argument("--initial-head", default=None)
    parser.add_argument("--interval-seconds", type=int, default=180)
    parser.add_argument("--duration-seconds", type=int, default=28800)
    args = parser.parse_args()
    if not 120 <= args.interval_seconds <= 300 or args.duration_seconds <= 0:
        raise SystemExit("interval must be 120..300 seconds and duration must be positive")
    repo = args.repo.resolve()
    state = read_json(args.state) if args.state.exists() else {"last_head": args.initial_head, "events": []}
    deadline = time.monotonic() + args.duration_seconds
    while time.monotonic() < deadline:
        try:
            head = remote_head(repo, args.branch)
            previous = state.get("last_head") if isinstance(state.get("last_head"), str) else None
            if head != previous:
                audit = inspect(repo, args.branch, previous, head)
                args.audit_dir.mkdir(parents=True, exist_ok=True)
                write_json(args.audit_dir / f"{head}.json", audit)
                state = {"last_head": head, "updated_at_utc": now(), "events": state.get("events", []) + [audit]}
                write_json(args.state, state)
        except MonitorError as exc:
            state["last_error"] = {"at_utc": now(), "message": str(exc)}
            write_json(args.state, state)
        time.sleep(args.interval_seconds)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
