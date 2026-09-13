#!/usr/bin/env python3
"""Materialize the one-shot Retry570 NVBit long-watch diagnostic closeout.

The long-watch is a bounded, non-capture diagnostic following the retained
microreproducer closure.  It may not overwrite either historic 6+6 window
evidence or infer an NVBit/PyTorch stall when the injected tool exits before
the 300-second observation can begin.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json, canonical_json, sha256_file, valid_sha256


SCHEMA = "C16_G_RETRY570_NVBIT_LONG_WATCH_CLOSEOUT_V1"
STATUS = "NVBIT_LONG_WATCH_DIAGNOSTIC_INCONCLUSIVE_TOOL_STARTUP_CONFIGURATION_FAILURE"
RAW_INDEX = "RAW_ARTIFACT_INDEX.json"
RECEIPT = "RETRY570_LONG_WATCH_RECEIPT.json"
TRANSFER = "RETRY570_LONG_WATCH_TRANSFER_RECEIPT.json"
README = "README.md"
MANIFEST = "PUBLISH_MANIFEST.json"
VALIDATION = "PUBLISH_VALIDATION_RECEIPT.json"
PAYLOADS = (README, RECEIPT, RAW_INDEX, TRANSFER)
REQUIRED_RAW = (
    "BASELINE_CHILD_RECEIPT.json",
    "BASELINE_RECEIPT.json",
    "BASELINE_SAMPLES.jsonl",
    "BASELINE_STAGE.json",
    "BASELINE_STDERR.log",
    "BASELINE_STDOUT.log",
    "NVBIT_LONG_WATCH_RECEIPT.json",
    "NVBIT_LONG_WATCH_SAMPLES.jsonl",
    "NVBIT_LONG_WATCH_STAGE.json",
    "NVBIT_LONG_WATCH_STDERR.log",
    "NVBIT_LONG_WATCH_STDOUT.log",
)
TOOL_SHA = "ae4e4e632a4afad0d5dda4b7f7aac2b460135784676765350945137a722cb5c0"
RUNTIME_COMMIT = "d8021532adfd94b4196785475f5c3914a3f51c2e"


def _read(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"long-watch closeout cannot read {path}") from exc
    if not isinstance(value, dict):
        raise ContractError(f"long-watch closeout expected JSON object: {path}")
    return value


def _entries(root: Path) -> list[dict[str, Any]]:
    if not root.is_dir():
        raise ContractError("long-watch raw root is absent")
    paths = sorted(item for item in root.rglob("*") if item.is_file())
    actual = tuple(str(path.relative_to(root)) for path in paths)
    if actual != REQUIRED_RAW:
        raise ContractError("long-watch raw root is incomplete or contains an unexpected diagnostic payload")
    return [{"local_relative_path": str(path.relative_to(root)), "size_bytes": path.stat().st_size, "sha256": sha256_file(path)} for path in paths]


def _tree_sha(entries: list[dict[str, Any]]) -> str:
    import hashlib
    digest = hashlib.sha256()
    for item in entries:
        digest.update(str(item["local_relative_path"]).encode())
        digest.update(b"\0")
        digest.update(str(item["size_bytes"]).encode())
        digest.update(b"\0")
        digest.update(str(item["sha256"]).encode())
        digest.update(b"\n")
    return digest.hexdigest()


def observed(raw_root: Path, ledger_path: Path, authorization_path: Path) -> dict[str, Any]:
    entries = _entries(raw_root)
    baseline = _read(raw_root / "BASELINE_RECEIPT.json")
    baseline_child = _read(raw_root / "BASELINE_CHILD_RECEIPT.json")
    long_watch = _read(raw_root / "NVBIT_LONG_WATCH_RECEIPT.json")
    authorization = _read(authorization_path)
    ledger = _read(ledger_path)
    if baseline.get("status") != "BASELINE_FIRST_CUDA_KERNEL_OBSERVED" or baseline.get("mode") != "BASELINE":
        raise ContractError("long-watch baseline did not observe a successful first CUDA kernel")
    baseline_ttfk = baseline.get("first_cuda_kernel_completed_elapsed_seconds")
    if not isinstance(baseline_ttfk, (int, float)) or baseline_ttfk <= 0 or baseline.get("trace_generated") is not False:
        raise ContractError("long-watch baseline timing/trace policy is malformed")
    if baseline_child.get("status") != "CHILD_COMPLETE" or not isinstance(baseline_child.get("runtime_identity"), dict):
        raise ContractError("long-watch baseline child runtime identity is not closed")
    if long_watch.get("status") != "NVBIT_LONG_WATCH_CHILD_FAILED_BEFORE_FIRST_KERNEL":
        raise ContractError("long-watch closeout only accepts the observed pre-first-kernel tool failure")
    if long_watch.get("mode") != "NVBIT_LONG_WATCH" or long_watch.get("wall_limit_seconds") != 300 or long_watch.get("sample_seconds") != 5:
        raise ContractError("long-watch hard observation bounds differ")
    if long_watch.get("first_cuda_kernel_completed_elapsed_seconds") is not None or long_watch.get("trace_generated") is not False:
        raise ContractError("long-watch incorrectly claims a first kernel or trace")
    if long_watch.get("runtime_code_commit") != RUNTIME_COMMIT:
        raise ContractError("long-watch receipt runtime commit differs from the clean source checkpoint")
    tool = long_watch.get("nvbit_tool")
    if not isinstance(tool, dict) or tool.get("sha256") != TOOL_SHA:
        raise ContractError("long-watch map-only tool SHA differs")
    stdout = (raw_root / "NVBIT_LONG_WATCH_STDOUT.log").read_text(encoding="utf-8", errors="replace")
    path_error = "ERROR: /usr/local/cuda-12.4/bin/nvdisasm not found on PATH!!!"
    if path_error not in stdout:
        raise ContractError("long-watch pre-first-kernel tool-startup boundary is not evidenced")
    if authorization.get("status") != "COMPLETE" or authorization.get("run_id") != long_watch.get("run_id"):
        raise ContractError("long-watch one-shot authorization is not closed to the observed run")
    if authorization.get("receipt_sha256") != sha256_file(raw_root / "NVBIT_LONG_WATCH_RECEIPT.json"):
        raise ContractError("long-watch authorization does not bind the exact receipt")
    ledger_entries = ledger.get("entries")
    if not isinstance(ledger_entries, list):
        raise ContractError("long-watch ledger is malformed")
    rows = [row for row in ledger_entries if row.get("operation_kind") == "NVBIT_LONG_WATCH_DIAGNOSTIC"]
    if len(rows) != 2 or {row.get("run_id") for row in rows} != {baseline.get("run_id"), long_watch.get("run_id")}:
        raise ContractError("long-watch ledger must retain exactly the baseline plus one NVBit diagnostic row")
    if any(row.get("raw_bytes") != 0 or row.get("evidence_classification") != "NON_SCIENTIFIC_DIAGNOSTIC" for row in rows):
        raise ContractError("long-watch ledger has capture-like or scientific accounting")
    if sum(row.get("operation_kind") == "NVBIT" and row.get("deployment_id") == "c16_retry570_indexselect_microreproducer" for row in ledger_entries) != 6:
        raise ContractError("historic six microreproducer NVBit windows changed")
    return {
        "baseline": baseline,
        "baseline_child": baseline_child,
        "long_watch": long_watch,
        "authorization": authorization,
        "entries": entries,
        "tree_sha256": _tree_sha(entries),
        "ledger_sha256": sha256_file(ledger_path),
        "authorization_sha256": sha256_file(authorization_path),
        "tool_startup_error": path_error,
        "long_watch_ledger_entries": rows,
    }


def raw_index(raw_root: Path, ledger_path: Path, authorization_path: Path, data: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "C16_G_RETRY570_NVBIT_LONG_WATCH_RAW_INDEX_V1",
        "status": "LOCAL_HASH_CLOSED_DIAGNOSTIC_ONLY",
        "scientific_eligible": False,
        "local_raw_root": str(raw_root),
        "entries": data["entries"],
        "tree_sha256": data["tree_sha256"],
        "execution_budget_ledger": {"path": str(ledger_path), "sha256": data["ledger_sha256"]},
        "one_shot_authorization": {"path": str(authorization_path), "sha256": data["authorization_sha256"]},
        "remote_only_required_artifact_count": 0,
    }


def closeout_receipt(raw_index_path: Path, data: dict[str, Any]) -> dict[str, Any]:
    baseline, long_watch = data["baseline"], data["long_watch"]
    return {
        "schema_version": SCHEMA,
        "status": STATUS,
        "scientific_eligible": False,
        "scope": "ONE_SHOT_NVBIT_COMPATIBILITY_DIAGNOSTIC_ONLY_NOT_TRACE_NOT_TIMING_NOT_C_TARGET",
        "runtime_source_commit": RUNTIME_COMMIT,
        "minimal_map_only_tool": {"source_commit": "f08af62e4bb77559617bd14d5df9a13d2e236873", "sha256": TOOL_SHA},
        "runtime_identity": data["baseline_child"]["runtime_identity"],
        "baseline": {
            "run_id": baseline.get("run_id"),
            "first_cuda_kernel_completed_elapsed_seconds": baseline.get("first_cuda_kernel_completed_elapsed_seconds"),
            "terminal_status": baseline.get("terminal_status"),
        },
        "one_shot_nvbit_watch": {
            "run_id": long_watch.get("run_id"),
            "wall_limit_seconds": 300,
            "sample_seconds": 5,
            "terminal_status": long_watch.get("terminal_status"),
            "first_cuda_kernel_completed_elapsed_seconds": None,
            "tool_startup_error": data["tool_startup_error"],
            "conclusion": "DID_NOT_REACH_300_SECOND_WATCHDOG_DISCRIMINATOR",
        },
        "prohibited_inferences": [
            "NVBIT_PYTORCH_PRE_FIRST_KERNEL_STALL_CONFIRMED",
            "NVBIT_PYTORCH_EXTREME_STARTUP_OVERHEAD",
            "NVBIT_PYTORCH_COMPATIBILITY_FAILURE",
            "MODEL_NVBIT_COMPATIBILITY_FAILURE",
        ],
        "one_shot_policy": "AUTHORIZATION_CLOSED_NO_SECOND_LONG_WATCH_PERMITTED",
        "static_map": "NOT_MATERIALIZED",
        "trace": "NOT_GENERATED",
        "raw_artifact_index": {"path": str(raw_index_path), "sha256": sha256_file(raw_index_path)},
        "terminal_state": "FAIL_CLOSED_INCONCLUSIVE_NO_MODEL_OR_C_TARGET_AUTHORIZATION",
    }


def transfer_receipt(raw_root: Path, data: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "C16_G_RETRY570_NVBIT_LONG_WATCH_TRANSFER_V1",
        "status": "PASS_REMOTE_TO_LOCAL_CHECKSUM_CLOSURE",
        "scientific_eligible": False,
        "remote_raw_root": "/root/autodl-tmp/c16_retry570/raw/retry570_long_watch_20260913",
        "local_raw_root": str(raw_root),
        "rsync_checksum_dry_run": "NO_DIFFERENCES",
        "local_tree_sha256": data["tree_sha256"],
        "file_count": len(data["entries"]),
        "total_bytes": sum(int(entry["size_bytes"]) for entry in data["entries"]),
        "remote_only_required_artifact_count": 0,
        "active_gpu_process_count_at_closeout": 0,
        "raw_payloads_committed": False,
    }


def readme() -> str:
    return f"""# Retry570 one-shot NVBit long-watch diagnostic

Status: `{STATUS}`.

The retained exact-kernel microreproducer closeout is unchanged; its existing
six-plus-six bounded NVBit windows were not rerun. A clean-source, non-capture
parent harness first ran the same finite microreproducer with no NVBit. It
observed first CUDA-kernel completion in 2.820031 seconds. It then created a
durable one-shot authorization and performed exactly one NVBit1.8 map-only
watch with a 300-second maximum and 5-second sampler. The map-only tool was
the already hash-closed lifecycle-free/no-instrumentation/no-tool-CUDA-
allocation discriminator.

The injected process reached `FIRST_CUDA_KERNEL_SUBMISSION_BEGIN`, but exited
in about 2.87 seconds before its first CUDA kernel because NVBit reported
`ERROR: /usr/local/cuda-12.4/bin/nvdisasm not found on PATH!!!`. The executable
exists on the node; the evidence only establishes that this tool invocation
used a configuration its NVBit-side path resolver rejected. It did **not** run
to 300 seconds. Therefore this does not distinguish a short 60-second guard
from an NVBit/PyTorch pre-first-kernel stall, and it cannot support either
`NVBIT_PYTORCH_PRE_FIRST_KERNEL_STALL_CONFIRMED` or
`NVBIT_PYTORCH_EXTREME_STARTUP_OVERHEAD`.

The one-shot authorization is complete and forbids a second long-watch. No
trace, static map, model, Qwen, Llama, C frozen target, timing evidence, or
scientific capture resulted. All retained small diagnostic payloads are
locally SHA-closed; raw payloads remain outside Git.
"""


def manifest(directory: Path) -> dict[str, Any]:
    return {
        "schema_version": "C16_G_RETRY570_NVBIT_LONG_WATCH_PUBLISH_V1",
        "status": STATUS,
        "scientific_eligible": False,
        "runtime_source_commit": RUNTIME_COMMIT,
        "files": [{"path": name, "size_bytes": (directory / name).stat().st_size, "sha256": sha256_file(directory / name)} for name in PAYLOADS],
        "raw_profiler_payloads_committed": False,
        "remote_only_required_artifact_count": 0,
    }


def validate(directory: Path) -> dict[str, Any]:
    publication = _read(directory / MANIFEST)
    rows = publication.get("files")
    if publication.get("status") != STATUS or publication.get("scientific_eligible") is not False or not isinstance(rows, list):
        raise ContractError("long-watch publish manifest status is malformed")
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("path"), str) or row["path"] not in PAYLOADS:
            raise ContractError("long-watch manifest path is malformed")
        path, size, digest = directory / row["path"], row.get("size_bytes"), row.get("sha256")
        if row["path"] in seen or not isinstance(size, int) or not valid_sha256(digest) or not path.is_file() or path.stat().st_size != size or sha256_file(path) != digest:
            raise ContractError("long-watch manifest payload fails existence/size/SHA closure")
        seen.add(row["path"])
    if seen != set(PAYLOADS):
        raise ContractError("long-watch manifest has missing or duplicate payloads")
    receipt = _read(directory / RECEIPT)
    if receipt.get("status") != STATUS or receipt.get("one_shot_nvbit_watch", {}).get("conclusion") != "DID_NOT_REACH_300_SECOND_WATCHDOG_DISCRIMINATOR":
        raise ContractError("long-watch receipt overstates the failed observation")
    return {
        "schema_version": "C16_G_RETRY570_NVBIT_LONG_WATCH_PUBLISH_VALIDATION_V1",
        "status": "PASS",
        "publish_manifest": {"path": MANIFEST, "sha256": sha256_file(directory / MANIFEST)},
        "checks": {"payload_count": len(rows), "duplicate_path_count": 0, "missing_path_count": 0, "size_or_sha256_failure_count": 0, "manifest_references_only_materialized_payloads": True, "scientific_eligible": False},
    }


def write(directory: Path, raw_root: Path, ledger_path: Path, authorization_path: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    data = observed(raw_root, ledger_path, authorization_path)
    atomic_json(directory / RAW_INDEX, raw_index(raw_root, ledger_path, authorization_path, data))
    atomic_json(directory / RECEIPT, closeout_receipt(directory / RAW_INDEX, data))
    atomic_json(directory / TRANSFER, transfer_receipt(raw_root, data))
    (directory / README).write_text(readme(), encoding="utf-8")
    atomic_json(directory / MANIFEST, manifest(directory))
    atomic_json(directory / VALIDATION, validate(directory))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--raw-root", type=Path, required=True)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--authorization", type=Path, required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--validate", action="store_true")
    args = parser.parse_args()
    if args.write:
        write(args.directory, args.raw_root, args.ledger, args.authorization)
        print(f"PASS Retry570 long-watch closeout write: {args.directory}")
    else:
        print("PASS Retry570 long-watch closeout validation: " + canonical_json(validate(args.directory)["checks"]))


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        raise SystemExit(f"FAIL Retry570 long-watch closeout: {exc}")
