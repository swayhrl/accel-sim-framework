#!/usr/bin/env python3
"""Bounded, low-impact watcher for C16-P's hash-closed G events.

The watcher polls only ``git ls-remote`` while the G head is unchanged.  Once a
new immutable head appears, it fetches that exact head, reads the runtime status
and changed event manifests, and writes a local audit ledger.  It never creates
Git commits, exports reports, or treats an in-progress transfer as an event.
Those actions remain available only to the P1/P2/P3 handlers after their
complete input contracts have been proved.
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


STATUS_PATH = "docs/vm_tlb/codex_handoff/c16/autodl_wave1/LATEST_RUNTIME_STATUS.md"
TERMINAL_MARKERS = ("BLOCKED", "SKIPPED_RESOURCE")
TERMINAL_VALUE_KEYS = {"status", "terminal_status", "outcome", "result", "classification"}


class MonitorError(RuntimeError):
    """Remote state cannot be safely audited."""


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MonitorError(f"cannot read state {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise MonitorError(f"state root is not an object: {path}")
    return value


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False) as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")
        temporary = Path(handle.name)
    os.replace(temporary, path)


def git(repo: Path, *arguments: str, text: bool = True) -> str | bytes:
    result = subprocess.run(["git", "-C", str(repo), *arguments], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if result.returncode:
        raise MonitorError(result.stderr.decode(errors="replace").strip())
    return result.stdout.decode("utf-8") if text else result.stdout


def remote_head(repo: Path, branch: str) -> str:
    output = git(repo, "ls-remote", "--heads", "origin", branch)
    rows = [line.split("\t", 1) for line in str(output).splitlines() if line]
    if len(rows) != 1 or len(rows[0]) != 2 or rows[0][1] != f"refs/heads/{branch}":
        raise MonitorError(f"cannot resolve exactly one remote head for {branch}")
    return rows[0][0]


def git_bytes(repo: Path, commit: str, path: str) -> bytes:
    return git(repo, "show", f"{commit}:{path}", text=False)  # type: ignore[return-value]


def event_manifest(repo: Path, commit: str, path: str) -> dict[str, Any]:
    payload = git_bytes(repo, commit, path)
    try:
        value = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise MonitorError(f"invalid JSON event manifest {path}") from exc
    if not isinstance(value, dict):
        raise MonitorError(f"event manifest root is not an object: {path}")
    result: dict[str, Any] = {
        "path": path,
        "sha256": sha256_bytes(payload),
        "schema_version": value.get("schema_version", "UNKNOWN"),
        "status": value.get("status", "UNKNOWN"),
        "classification": value.get("classification", "UNKNOWN"),
        "identity": value.get("identity", {}),
    }
    external = value.get("external_hash_closed_payloads", [])
    external_ok = isinstance(external, list) and bool(external)
    checked = []
    if isinstance(external, list):
        for item in external:
            if not isinstance(item, dict):
                external_ok = False
                continue
            path_value, size, digest = item.get("path"), item.get("size_bytes"), item.get("sha256")
            local_path = Path(path_value) if isinstance(path_value, str) else None
            exists = local_path is not None and local_path.is_file()
            actual = None
            if exists:
                actual = hashlib.sha256(local_path.read_bytes()).hexdigest()
            item_ok = exists and isinstance(size, int) and local_path.stat().st_size == size and actual == digest
            external_ok = external_ok and item_ok
            checked.append({"artifact_id": item.get("artifact_id", "UNKNOWN"), "path": path_value, "hash_closed_local": item_ok})
    result["external_payloads"] = checked
    result["hash_closed_local"] = external_ok
    result["handler_state"] = "P2_HANDLER_REQUIRED" if external_ok and str(value.get("schema_version", "")).startswith("C16_G_DIRECT_SEMANTIC") else "NOT_A_COMPLETE_P2_EVENT"
    return result


def changed_paths(repo: Path, old: str | None, new: str) -> list[str]:
    if old is None:
        return []
    try:
        output = git(repo, "diff", "--name-only", old, new)
    except MonitorError:
        return []
    return [line for line in str(output).splitlines() if line]


def candidate_receipts(repo: Path, commit: str, paths: list[str]) -> list[dict[str, str]]:
    """Hash receipt candidates without pretending that a partial one is usable.

    P1 and P3 publishers use different receipt names, so this intentionally
    indexes their changed manifest/receipt/index files.  A later handler still
    has to enforce its own complete contract before exporting anything.
    """
    suffixes = ("_RECEIPT.json", "_MANIFEST.json", "RAW_ARTIFACT_INDEX.tsv")
    candidates = [path for path in paths if path.endswith(suffixes) and not path.endswith("/SEMANTIC_PUBLISH_MANIFEST.json")]
    return [{"path": path, "sha256": sha256_bytes(git_bytes(repo, commit, path))} for path in candidates]


def terminal_marker(value: str) -> str | None:
    """Return an explicit terminal marker, never infer one from prose."""
    upper = value.upper()
    return next((marker for marker in TERMINAL_MARKERS if marker in upper), None)


def deployment_id(value: dict[str, Any]) -> str | None:
    """Find an exact deployment identifier in a structured G receipt."""
    candidates = (value.get("deployment_id"), value.get("identity", {}).get("deployment_id") if isinstance(value.get("identity"), dict) else None)
    for candidate in candidates:
        if isinstance(candidate, str) and candidate.startswith("c16_"):
            return candidate
    return None


def receipt_terminal_declarations(path: str, payload: dict[str, Any]) -> list[dict[str, str]]:
    """Extract only scoped terminal declarations from structured changed receipts.

    A historical `SKIPPED_RESOURCE` mention elsewhere in LATEST_RUNTIME_STATUS is
    not a declaration about the new event.  Likewise, an instructional line such
    as "an OOM is SKIPPED_RESOURCE" is not a terminal result.  The receipt must
    have an exact deployment identity and a terminal-valued status-like field.
    """
    declarations: list[dict[str, str]] = []

    def walk(item: Any, pointer: str, inherited_deployment: str | None) -> None:
        if isinstance(item, dict):
            scoped_deployment = deployment_id(item) or inherited_deployment
            for key, child in item.items():
                child_pointer = f"{pointer}.{key}" if pointer else key
                if key.lower() in TERMINAL_VALUE_KEYS and isinstance(child, str):
                    marker = terminal_marker(child)
                    if marker is not None and scoped_deployment is not None:
                        declarations.append({
                            "path": path,
                            "deployment_id": scoped_deployment,
                            "json_pointer": child_pointer,
                            "terminal_marker": marker,
                            "value": child,
                        })
                walk(child, child_pointer, scoped_deployment)
        elif isinstance(item, list):
            for index, child in enumerate(item):
                walk(child, f"{pointer}[{index}]", inherited_deployment)

    walk(payload, "", deployment_id(payload))
    return declarations


def changed_terminal_declarations(repo: Path, previous: str | None, current: str, paths: list[str]) -> list[dict[str, str]]:
    """Read terminal state only from changed structured receipts at this head.

    Markdown status is intentionally excluded from terminal classification: it
    contains policy and history in addition to the current deployment result.
    An unscoped wording there is retained by the immutable status hash, but can
    never suppress a future P event or label an unrelated package as skipped.
    """
    if previous is None:
        return []
    declarations: list[dict[str, str]] = []
    for path in paths:
        if not path.endswith(".json") or path == STATUS_PATH:
            continue
        try:
            payload = json.loads(git_bytes(repo, current, path))
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            declarations.extend(receipt_terminal_declarations(path, payload))
    return declarations


def inspect_changed_head(repo: Path, branch: str, previous: str | None, advertised: str) -> dict[str, Any]:
    git(repo, "fetch", "origin", branch)
    fetched = str(git(repo, "rev-parse", "FETCH_HEAD")).strip()
    if fetched != advertised:
        raise MonitorError(f"remote moved during fetch ({advertised} -> {fetched}); no event consumed")
    paths = changed_paths(repo, previous, fetched)
    status_bytes = git_bytes(repo, fetched, STATUS_PATH)
    manifests = [path for path in paths if path.endswith("/SEMANTIC_PUBLISH_MANIFEST.json")]
    events = [event_manifest(repo, fetched, path) for path in manifests]
    terminal_declarations = changed_terminal_declarations(repo, previous, fetched, paths)
    return {
        "schema_version": "C16_P_UNATTENDED_HEAD_AUDIT_V2",
        "observed_at_utc": now(),
        "branch": branch,
        "previous_head": previous,
        "head": fetched,
        "latest_runtime_status": {"path": STATUS_PATH, "sha256": sha256_bytes(status_bytes)},
        "changed_paths": paths,
        "semantic_events": events,
        "p1_p3_receipt_candidates": candidate_receipts(repo, fetched, paths),
        "terminal_declarations": terminal_declarations,
        "deployment_blocked_or_skipped": bool(terminal_declarations),
        "action": "RECORD_BLOCKED_OR_SKIPPED_AND_CONTINUE_MONITORING" if terminal_declarations else "WAIT_FOR_HANDLER_OR_NEXT_HASH_CLOSED_EVENT",
    }


def poll(repo: Path, branch: str, state_path: Path, audit_dir: Path, *, bootstrap: bool) -> bool:
    state = read_json(state_path) if state_path.is_file() else {}
    head = remote_head(repo, branch)
    prior = state.get("last_seen_head") if isinstance(state.get("last_seen_head"), str) else None
    if bootstrap and prior is None:
        write_json(state_path, {"schema_version": "C16_P_UNATTENDED_MONITOR_STATE_V1", "branch": branch, "last_seen_head": head, "bootstrapped_at_utc": now(), "last_poll_utc": now()})
        print(f"BOOTSTRAP {head}")
        return False
    if head == prior:
        state["last_poll_utc"] = now()
        state["branch"] = branch
        state.setdefault("schema_version", "C16_P_UNATTENDED_MONITOR_STATE_V1")
        write_json(state_path, state)
        print(f"IDLE {head}")
        return False
    audit = inspect_changed_head(repo, branch, prior, head)
    audit_path = audit_dir / f"HEAD_{audit['head']}.json"
    write_json(audit_path, audit)
    write_json(state_path, {"schema_version": "C16_P_UNATTENDED_MONITOR_STATE_V1", "branch": branch, "last_seen_head": audit["head"], "last_poll_utc": now(), "last_head_audit": str(audit_path), "unhandled_hash_closed_semantic_events": [event["path"] for event in audit["semantic_events"] if event["hash_closed_local"]]})
    print(f"HEAD_CHANGED {audit['head']} audit={audit_path}")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--branch", default="hrl/vm-c16-g-autodl-wave1-v0")
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--audit-dir", type=Path, required=True)
    parser.add_argument("--interval-seconds", type=int, default=180)
    parser.add_argument("--duration-seconds", type=int, default=28800)
    parser.add_argument("--bootstrap-current", action="store_true")
    args = parser.parse_args()
    if not 120 <= args.interval_seconds <= 300:
        raise MonitorError("interval must be bounded to 120–300 seconds")
    if args.duration_seconds <= 0:
        raise MonitorError("duration must be positive")
    started = time.monotonic()
    first = True
    while time.monotonic() - started < args.duration_seconds:
        poll(args.repo, args.branch, args.state, args.audit_dir, bootstrap=args.bootstrap_current and first)
        first = False
        remaining = args.duration_seconds - (time.monotonic() - started)
        if remaining <= 0:
            break
        time.sleep(min(args.interval_seconds, remaining))


if __name__ == "__main__":
    try:
        main()
    except MonitorError as exc:
        print(f"FAIL C16 P unattended monitor: {exc}", file=sys.stderr)
        raise SystemExit(2)
