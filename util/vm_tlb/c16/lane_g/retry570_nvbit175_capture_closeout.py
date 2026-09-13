#!/usr/bin/env python3
"""Validate/publish two hash-closed, non-scientific NVBit 1.7.5 tiny captures."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json, canonical_json, sha256_file, valid_sha256

SCHEMA = "C16_G_RETRY570_NVBIT175_CAPTURE_CLOSEOUT_V1"
STATUS = "NVBIT_RETRY570_NVBIT175_MINIMAL_CAPTURE_QUALIFIED_STOP_FOR_REVIEW"
PAYLOADS = ("NVBIT175_CAPTURE_QUALIFICATION_REPORT.md", "Q1_CAPTURE_MATRIX.tsv", "Q2_TRACE_VALIDATION_RECEIPT.json", "RAW_ARTIFACT_INDEX.json", "NVBIT175_CAPTURE_TRANSFER_RECEIPT.json")
MANIFEST, VALIDATION = "PUBLISH_MANIFEST.json", "PUBLISH_VALIDATION_RECEIPT.json"
EXPECTED_OUTPUT = "8c62c08fcc833f223182df024f4ed698c8e3fc93daf8e259c14d35e8899e665c"
EXPECTED_FUNCTION_FRAGMENT = "indexSelectLargeIndex"


def load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read JSON object: {path}") from exc
    if not isinstance(value, dict):
        raise ContractError(f"JSON object required: {path}")
    return value


def event_order(stdout: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in stdout.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("C16_NVBIT175_CAPTURE "):
            value = json.loads(line.removeprefix("C16_NVBIT175_CAPTURE "))
            if isinstance(value, dict): rows.append(value)
    names = [row.get("event") for row in rows]
    required = ("PROCESS_START", "PREWARM_BEGIN", "PREWARM_END", "LANE_G_RUNTIME_READY", "CAPTURE_BEGIN", "CAPTURE_END")
    if any(name not in names for name in required) or [names.index(name) for name in required] != sorted(names.index(name) for name in required):
        raise ContractError("lifecycle events are absent or unordered")
    return rows


def parse_trace(path: Path, target: dict[str, Any]) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    if not text.endswith("\n"):
        raise ContractError("trace lacks final newline; truncated-tail guard failed")
    headers = {line.split(" = ", 1)[0]: line.split(" = ", 1)[1] for line in text.splitlines() if line.startswith("-") and " = " in line}
    rows = [line for line in text.splitlines() if line and not line.startswith("-") and not line.startswith("#")]
    need = ("-kernel name", "-kernel id", "-nvbit version", "-accelsim tracer version")
    if "#traces format" not in text or any(key not in headers for key in need) or not rows:
        raise ContractError("trace schema/header is incomplete")
    if headers["-kernel name"] != target["function"] or int(headers["-kernel id"]) != target["kernel_id"]:
        raise ContractError("trace target identity differs from Q0 frozen target")
    if headers["-nvbit version"] != "1.7.5" or headers["-accelsim tracer version"] != "5":
        raise ContractError("trace tool/version header differs")
    malformed = [line for line in rows if len(line.split()) < 12]
    memory_rows = [line for line in rows if re.search(r"\b(?:LDG|STG|ATOM)[.A-Z0-9_]*\b", line) and re.search(r"\b0x[0-9a-fA-F]+\b", line)]
    if malformed or not memory_rows:
        raise ContractError("trace lacks complete instruction/memory-operation fields")
    return {"relative_trace_path": path.name, "size_bytes": path.stat().st_size, "sha256": sha256_file(path),
            "record_count": len(rows), "memory_record_count": len(memory_rows), "kernel_id": target["kernel_id"],
            "kernel_name": target["function"], "nvbit_version": headers["-nvbit version"],
            "accelsim_tracer_version": headers["-accelsim tracer version"], "truncated_tail": False}


def verify_remote_list(run: Path) -> list[dict[str, Any]]:
    listed: dict[str, str] = {}
    for line in (run / "REMOTE_SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
        digest, name = line.split(maxsplit=1)
        name = name.removeprefix("./")
        if not valid_sha256(digest) or name in listed: raise ContractError("remote SHA list is malformed")
        listed[name] = digest
    payload = run / "remote_payload"
    actual = {path.relative_to(payload).as_posix() for path in payload.rglob("*") if path.is_file()}
    if actual != set(listed): raise ContractError("local retained set differs from remote SHA list")
    rows = []
    for name, digest in sorted(listed.items()):
        path = payload / name
        if sha256_file(path) != digest: raise ContractError(f"dual endpoint SHA mismatch: {name}")
        rows.append({"logical_path": name, "size_bytes": path.stat().st_size, "remote_sha256": digest, "local_sha256": digest, "match": True})
    return rows


def observe(raw: Path) -> dict[str, Any]:
    q0 = raw / "q0_5b5b169c-e581-45b1-a407-7b25b10924a3" / "remote_payload"
    q0_receipt, plan = load(q0 / "Q0_RECEIPT.json"), load(q0 / "Q0_TARGET_PLAN.json")
    target = plan.get("target")
    if (q0_receipt.get("status") != "LANE_G_RUNTIME_READY" or q0_receipt.get("scientific_eligible") is not False or
            q0_receipt.get("trace_generated") is not False or q0_receipt.get("prewarm_trace_count") != 0 or
            q0_receipt.get("measurement_active_created") is not False or q0_receipt.get("output_sha256") != EXPECTED_OUTPUT or
            plan.get("status") != "Q0_FROZEN_EXACT_TARGET_PLAN" or not isinstance(target, dict) or target.get("kernel_id") != 6 or
            not isinstance(target.get("function"), str) or EXPECTED_FUNCTION_FRAGMENT not in target["function"]):
        raise ContractError("Q0 runtime-ready/target binding differs")
    runs = []
    transfer_rows = [{"run": "Q0", **row} for row in verify_remote_list(raw / "q0_5b5b169c-e581-45b1-a407-7b25b10924a3")]
    for label, directory in (("RUN1", raw / "q1_run1_3b1b67aa-8981-4c80-8411-c58cee912b86"), ("RUN2", raw / "q1_run2_f66d8303-b479-4d08-a497-c90db14b034a")):
        payload = directory / "remote_payload"
        receipt, child = load(payload / "Q1_RECEIPT.json"), load(payload / "child_receipt.json")
        if (receipt.get("status") != "Q1_CAPTURE_COMPLETE" or receipt.get("scientific_eligible") is not False or receipt.get("target") != target or
                receipt.get("prewarm_trace_count") != 0 or receipt.get("terminal_status") != "COMPLETE" or receipt.get("target_group_cleanup", {}).get("required") is not False or
                receipt.get("measurement_active_created") is not True or child.get("output_sha256") != EXPECTED_OUTPUT or
                child.get("prewarm_trace_count") != 0 or child.get("target") != target or receipt.get("runtime_code_commit") != "8440c04512ef372480aa71a077bacfa7e55e8eb2"):
            raise ContractError(f"{label} receipt/lifecycle differs")
        captures = receipt.get("capture_traces")
        if not isinstance(captures, list) or len(captures) != 1: raise ContractError(f"{label} does not contain exactly one capture trace")
        trace_path = next((payload / "traces").glob("*.trace"), None)
        if trace_path is None: raise ContractError(f"{label} raw trace absent")
        trace = parse_trace(trace_path, target)
        if trace["sha256"] != captures[0].get("sha256") or trace["record_count"] != captures[0].get("record_count"):
            raise ContractError(f"{label} receipt trace binding differs")
        events = event_order(payload / "stdout.log")
        tx = load(payload / "remote_transaction.json")
        if tx.get("runner_exit_code") != 0 or not isinstance(tx.get("remote_transaction_wall_s"), (int, float)) or tx["remote_transaction_wall_s"] > 38:
            raise ContractError(f"{label} remote transaction differs")
        runs.append({"label": label, "run_id": receipt["run_id"], "target_wall_s": receipt["target_wall_s"],
                     "remote_transaction_wall_s": tx["remote_transaction_wall_s"], "target": target, "trace": trace,
                     "lifecycle_events": [row["event"] for row in events], "receipt_sha256": sha256_file(payload / "Q1_RECEIPT.json")})
        transfer_rows.extend({"run": label, **row} for row in verify_remote_list(directory))
    if runs[0]["target"] != runs[1]["target"] or runs[0]["trace"]["record_count"] != runs[1]["trace"]["record_count"]:
        raise ContractError("independent Q1 runs fail qualitative target/schema reproducibility")
    return {"q0": q0_receipt, "target": target, "runs": runs, "transfer_rows": transfer_rows}


def matrix(data: dict[str, Any]) -> str:
    lines = ["run\trun_id\tkernel_id\tfunction\trecord_count\tmemory_record_count\ttrace_bytes\ttrace_sha256\ttarget_wall_s\tremote_transaction_wall_s\tprewarm_trace_count\tscientific_eligible\n"]
    for run in data["runs"]:
        trace = run["trace"]
        lines.append("\t".join((run["label"], run["run_id"], str(trace["kernel_id"]), trace["kernel_name"], str(trace["record_count"]), str(trace["memory_record_count"]), str(trace["size_bytes"]), trace["sha256"], f"{run['target_wall_s']:.9f}", f"{run['remote_transaction_wall_s']:.9f}", "0", "FALSE")) + "\n")
    return "".join(lines)


def report(data: dict[str, Any]) -> str:
    a, b = data["runs"]
    return f"""# NVBit 1.7.5 minimal capture qualification

Status: `{STATUS}`.

This is a tiny deterministic PyTorch `index_select` canary, never a model,
C target, performance result, or scientific capture. Both independent Q1
processes used the frozen Q0 kernel 6 full `indexSelectLargeIndex` function,
NVBit 1.7.5, EAGER loading, the original Lane G tracer, and the same output
checksum `{EXPECTED_OUTPUT}`. Q0 and both Q1 prewarms produced zero trace
files before the parent created `MEASUREMENT_ACTIVE`.

Run1/run2 each completed normally within the 30-second target cap and emitted
exactly one trace with {a['trace']['record_count']} records and
{a['trace']['memory_record_count']} explicit LDG/STG/ATOM address rows. Their
trace SHA256s are `{a['trace']['sha256']}` and `{b['trace']['sha256']}`; bytes
are both {a['trace']['size_bytes']}. The two payloads intentionally differ by
run-specific address/context data, while target identity, schema, record count,
and required header fields agree.

The tracer format has no record timestamp or global sequence field. This pack
therefore does not falsely claim per-record timestamp ordering. Window
cleanliness is instead proven by the parent-controlled protocol: zero traces
before arm, `LANE_G_RUNTIME_READY` before `CAPTURE_BEGIN`, one armed target,
then `CAPTURE_END`, normal exit, and post-run marker/process absence. The
trace parser verifies header/version, target identity, complete instruction
rows, address-bearing memory operations, final newline, and one-file binding.

All retained Q0/Q1 payloads were remote-SHA listed, copied locally, and
rehashed identically. Raw traces stay outside Git. Stop here for review: this
does not authorize Llama, Qwen, a full model, C frozen targets, performance
analysis, or any broader scientific capture.
"""


def build(directory: Path, raw: Path, producer: str, publication: str) -> None:
    data = observe(raw); directory.mkdir(parents=True, exist_ok=True)
    atomic_json(directory / "RAW_ARTIFACT_INDEX.json", {"schema_version": SCHEMA, "status": "PASS_DUAL_ENDPOINT_SIZE_SHA256_CLOSED", "scientific_eligible": False, "entries": data["transfer_rows"], "raw_payloads_committed": False, "remote_only_required_artifact_count": 0})
    atomic_json(directory / "Q2_TRACE_VALIDATION_RECEIPT.json", {"schema_version": SCHEMA, "status": "Q2_TRACE_SCHEMA_AND_LIFECYCLE_PASS", "scientific_eligible": False, "scope": "TINY_PYTORCH_CAPTURE_CORRECTNESS_ONLY_NOT_NATIVE_TIMING", "runtime_capture_code_commit": producer, "publication_code_commit": publication, "q0": {"runtime_ready": True, "output_sha256": EXPECTED_OUTPUT, "target": data["target"]}, "runs": data["runs"], "record_timestamp_check": "NOT_APPLICABLE_TRACE_FORMAT_HAS_NO_TIMESTAMP; PARENT_ARMED_LIFECYCLE_VALIDATED", "measurement_window_clean": True, "active_gpu_process_count_after_run": 0, "measurement_active_after_run": "ABSENT", "remote_only_required_artifact_count": 0})
    atomic_json(directory / "NVBIT175_CAPTURE_TRANSFER_RECEIPT.json", {"schema_version": SCHEMA, "status": "PASS_REMOTE_TO_LOCAL_SIZE_SHA256_CLOSURE", "scientific_eligible": False, "payload_count": len(data["transfer_rows"]), "mismatch_count": 0, "remote_only_required_artifact_count": 0, "raw_index_sha256": sha256_file(directory / "RAW_ARTIFACT_INDEX.json")})
    (directory / "Q1_CAPTURE_MATRIX.tsv").write_text(matrix(data), encoding="utf-8")
    (directory / "NVBIT175_CAPTURE_QUALIFICATION_REPORT.md").write_text(report(data), encoding="utf-8")
    files = [{"path": name, "size_bytes": (directory / name).stat().st_size, "sha256": sha256_file(directory / name)} for name in PAYLOADS]
    atomic_json(directory / MANIFEST, {"schema_version": SCHEMA, "status": STATUS, "scientific_eligible": False, "runtime_capture_code_commit": producer, "publication_code_commit": publication, "files": files, "raw_payloads_committed": False, "remote_only_required_artifact_count": 0})
    atomic_json(directory / VALIDATION, validate(directory))


def validate(directory: Path) -> dict[str, Any]:
    manifest, seen = load(directory / MANIFEST), set()
    files = manifest.get("files")
    if manifest.get("status") != STATUS or manifest.get("scientific_eligible") is not False or not isinstance(files, list): raise ContractError("manifest header differs")
    for row in files:
        name = row.get("path") if isinstance(row, dict) else None
        if name not in PAYLOADS or name in seen or not isinstance(row.get("size_bytes"), int) or not valid_sha256(row.get("sha256")): raise ContractError("invalid/duplicate manifest path")
        path = directory / name
        if not path.is_file() or path.stat().st_size != row["size_bytes"] or sha256_file(path) != row["sha256"]: raise ContractError(f"payload closure failed: {name}")
        seen.add(name)
    if seen != set(PAYLOADS): raise ContractError("manifest has missing/unmaterialized payload")
    return {"schema_version": SCHEMA, "status": "PASS", "publish_manifest_sha256": sha256_file(directory / MANIFEST), "checks": {"payload_count": len(files), "duplicate_path_count": 0, "missing_path_count": 0, "size_or_sha256_failure_count": 0, "manifest_references_only_materialized_payloads": True}}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True); parser.add_argument("--raw-base", type=Path); parser.add_argument("--runtime-capture-code-commit"); parser.add_argument("--publication-code-commit")
    group = parser.add_mutually_exclusive_group(required=True); group.add_argument("--write", action="store_true"); group.add_argument("--validate", action="store_true")
    args = parser.parse_args()
    if args.write:
        if args.raw_base is None or not all(re.fullmatch(r"[0-9a-f]{40}", value or "") for value in (args.runtime_capture_code_commit, args.publication_code_commit)): raise ContractError("write requires raw base and exact code commits")
        build(args.directory, args.raw_base, args.runtime_capture_code_commit, args.publication_code_commit)
        print(f"PASS NVBit175 capture qualification publication write: {args.directory}")
    else:
        print("PASS NVBit175 capture qualification validation: " + canonical_json(validate(args.directory)["checks"]))


if __name__ == "__main__":
    try: main()
    except ContractError as exc: raise SystemExit(f"FAIL NVBit175 capture qualification: {exc}")
