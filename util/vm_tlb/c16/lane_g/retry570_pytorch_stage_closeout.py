#!/usr/bin/env python3
"""Publish the bounded, non-scientific Retry570 C0--C4 NVBit isolator."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json, canonical_json, sha256_file, valid_sha256


SCHEMA = "C16_G_RETRY570_PYTORCH_STAGE_CLOSEOUT_V1"
STATUS = "NVBIT_PYTORCH_FIRST_KERNEL_STAGE_DIAGNOSTIC_COMPLETE"
RUNTIME_COMMIT = "982135c3a7d946f4d4be8705239d4b332802330b"
TOOL_SHA = "07ba183f1f27f231af249ad6f2329a70b84d3de75e0bff8974696e5b8c59b845"
REMOTE_MANIFEST = "REMOTE_ARTIFACT_MANIFEST.json"
RAW_INDEX = "RAW_ARTIFACT_INDEX.json"
RECEIPT = "PYTORCH_NVBIT_FIRST_KERNEL_STAGE_RECEIPT.json"
TRANSFER = "PYTORCH_NVBIT_FIRST_KERNEL_STAGE_TRANSFER_RECEIPT.json"
MATRIX = "PYTORCH_NVBIT_FIRST_KERNEL_STAGE_MATRIX.tsv"
REPORT = "NVBIT_PYTORCH_FIRST_KERNEL_STAGE_REPORT.md"
MANIFEST = "PUBLISH_MANIFEST.json"
VALIDATION = "PUBLISH_VALIDATION_RECEIPT.json"
PAYLOADS = (REPORT, MATRIX, RECEIPT, RAW_INDEX, TRANSFER)
CASES = (
    "C0_TORCH_CUDA_INIT",
    "C1_GPU_ALLOCATION",
    "C2_TENSOR_FILL_FIRST_KERNEL",
    "C3_ELEMENTWISE_FIRST_KERNEL",
    "C4_SMALL_GEMM_LIBRARY_KERNEL",
)


def _load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read JSON {path}") from exc
    if not isinstance(value, dict):
        raise ContractError(f"expected JSON object: {path}")
    return value


def _tree_sha(rows: list[dict[str, Any]]) -> str:
    value = hashlib.sha256()
    for row in rows:
        value.update(f"{row['relative_path']}\0{row['size_bytes']}\0{row['sha256']}\n".encode())
    return value.hexdigest()


def _events(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.startswith("C16_NVBIT_TIMING ts_us="):
            continue
        row = dict(re.findall(r"(\w+)=([^ ]+)", line))
        if "ts_us" in row and "stage" in row:
            rows.append(row)
    return rows


def _first(events: list[dict[str, str]], stage: str) -> dict[str, str]:
    for row in events:
        if row.get("stage") == stage:
            return row
    raise ContractError(f"NVBit timing stream lacks {stage}")


def _microseconds(events: list[dict[str, str]], start: str, end: str) -> int:
    return int(_first(events, end)["ts_us"]) - int(_first(events, start)["ts_us"])


def _aggregate_microseconds(events: list[dict[str, str]], start: str, end: str) -> int:
    """Sum ordered per-function discovery intervals; C4 has 88 of them."""
    starts = [int(row["ts_us"]) for row in events if row.get("stage") == start]
    ends = [int(row["ts_us"]) for row in events if row.get("stage") == end]
    if not starts or len(starts) != len(ends):
        raise ContractError(f"NVBit timing stream has unmatched {start}/{end} intervals")
    return sum(finish - begin for begin, finish in zip(starts, ends))


def _observed_case(raw: Path, mode: str, testcase: str) -> dict[str, Any]:
    directory = raw / f"{mode.lower()}_{testcase.lower()}"
    receipt = _load(directory / "receipt.json")
    if receipt.get("status") != "COMPLETE" or receipt.get("terminal_status") != "COMPLETE":
        raise ContractError(f"{mode}/{testcase} did not complete")
    if receipt.get("scientific_eligible") is not False or receipt.get("trace_generated") is not False or receipt.get("raw_trace_bytes") != 0:
        raise ContractError(f"{mode}/{testcase} is not a non-capture diagnostic")
    if receipt.get("runtime_code_commit") != RUNTIME_COMMIT or receipt.get("testcase") != testcase or receipt.get("mode") != mode:
        raise ContractError(f"{mode}/{testcase} source or identity binding differs")
    result: dict[str, Any] = {
        "receipt": receipt,
        "directory": directory,
        "first_submission_seconds": receipt.get("first_cuda_submission_elapsed_seconds"),
        "first_completion_seconds": receipt.get("first_cuda_completion_elapsed_seconds"),
        "elapsed_seconds": receipt.get("elapsed_seconds"),
        "events": [],
    }
    if testcase in CASES[:2]:
        if result["first_submission_seconds"] is not None or result["first_completion_seconds"] is not None:
            raise ContractError(f"{mode}/{testcase} incorrectly claims a workload kernel")
    else:
        if not all(isinstance(result[key], (int, float)) and result[key] > 0 for key in ("first_submission_seconds", "first_completion_seconds")):
            raise ContractError(f"{mode}/{testcase} lacks first-kernel timestamps")
    if mode == "NVBIT":
        tool = receipt.get("nvbit_tool")
        if not isinstance(tool, dict) or tool.get("sha256") != TOOL_SHA:
            raise ContractError(f"{testcase} uses a different timing-probe tool")
        events = _events(directory / "stdout.log")
        result["events"] = events
        if testcase in CASES[:2]:
            if any(event.get("stage") == "LAUNCH_CALLBACK_ENTER" for event in events):
                raise ContractError(f"{testcase} unexpectedly launched an instrumented CUDA kernel")
        else:
            for stage in ("LAUNCH_CALLBACK_ENTER", "RELATED_FUNCTIONS_END", "GET_INSTRS_BEGIN", "GET_INSTRS_END", "INSERTION_BEGIN", "INSERTION_END", "ENABLE_INSTRUMENTED_BEGIN", "ENABLE_INSTRUMENTED_END", "KERNEL_LAUNCH_RETURN", "CUDA_SYNCHRONIZE_END"):
                _first(events, stage)
    return result


def observe(raw: Path) -> dict[str, Any]:
    remote_manifest = _load(raw / REMOTE_MANIFEST)
    rows = remote_manifest.get("entries")
    if (remote_manifest.get("runtime_source_commit") != RUNTIME_COMMIT or remote_manifest.get("scientific_eligible") is not False
            or not isinstance(rows, list) or remote_manifest.get("tree_sha256") != _tree_sha(rows)):
        raise ContractError("remote artifact manifest is malformed")
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("relative_path"), str) or not isinstance(row.get("size_bytes"), int) or not valid_sha256(row.get("sha256")):
            raise ContractError("remote artifact manifest row malformed")
        path = raw / row["relative_path"]
        if not path.is_file() or path.stat().st_size != row["size_bytes"] or sha256_file(path) != row["sha256"]:
            raise ContractError(f"local payload fails remote existence/size/SHA closure: {row['relative_path']}")
    if len(rows) != 75 or sum(int(row["size_bytes"]) for row in rows) != 772515:
        raise ContractError("unexpected diagnostic payload count or byte total")
    native = {case: _observed_case(raw, "NATIVE", case) for case in CASES}
    nvbit = {case: _observed_case(raw, "NVBIT", case) for case in CASES}
    summaries: dict[str, dict[str, Any]] = {}
    for case in CASES[2:]:
        events = nvbit[case]["events"]
        related = _first(events, "RELATED_FUNCTIONS_END")
        gets = [event for event in events if event.get("stage") == "GET_INSTRS_END"]
        if not gets:
            raise ContractError(f"{case} lacks static instruction enumeration")
        summaries[case] = {
            "first_problematic_kernel": _first(events, "LAUNCH_CALLBACK_ENTER").get("function"),
            "related_function_count": int(related["related_count"]),
            "enumerated_function_count": len(gets),
            "total_static_instruction_count": sum(int(row["static_instruction_count"]) for row in gets),
            "instruction_discovery_seconds": _aggregate_microseconds(events, "GET_INSTRS_BEGIN", "GET_INSTRS_END") / 1_000_000,
            "insertion_seconds": _microseconds(events, "INSERTION_BEGIN", "INSERTION_END") / 1_000_000,
            "enable_seconds": _microseconds(events, "ENABLE_INSTRUMENTED_BEGIN", "ENABLE_INSTRUMENTED_END") / 1_000_000,
            "launch_return_to_sync_complete_seconds": _microseconds(events, "KERNEL_LAUNCH_RETURN", "CUDA_SYNCHRONIZE_END") / 1_000_000,
            "full_probe_seconds": (int(events[-1]["ts_us"]) - int(events[0]["ts_us"])) / 1_000_000,
        }
    c4 = summaries["C4_SMALL_GEMM_LIBRARY_KERNEL"]
    if c4["related_function_count"] != 89 or c4["enumerated_function_count"] != 88 or c4["instruction_discovery_seconds"] <= 19 or c4["instruction_discovery_seconds"] >= 60:
        raise ContractError("C4 does not establish the bounded related-function instruction-discovery boundary")
    if any(summaries[case]["related_function_count"] != 1 for case in CASES[2:4]):
        raise ContractError("C2/C3 no longer establish the single-related-function comparison")
    return {
        "remote_manifest": remote_manifest,
        "remote_manifest_sha256": sha256_file(raw / REMOTE_MANIFEST),
        "native": native,
        "nvbit": nvbit,
        "summaries": summaries,
        "tree_sha256": _tree_sha(rows),
        "rows": rows,
        "ledger_sha256": sha256_file(raw / "EXECUTION_BUDGET_LEDGER_AFTER.json"),
    }


def _fmt(value: Any) -> str:
    return "NA" if value is None else f"{float(value):.6f}"


def matrix(data: dict[str, Any]) -> str:
    header = ("testcase\tnative_status\tnative_submission_seconds\tnative_completion_seconds\tnative_elapsed_seconds\t"
              "nvbit_status\tnvbit_submission_seconds\tnvbit_completion_seconds\tnvbit_elapsed_seconds\t"
              "first_kernel_or_na\trelated_function_count\tenumerated_function_count\ttotal_static_instruction_count\t"
              "instruction_discovery_seconds\tinsertion_seconds\tenable_seconds\tlaunch_return_to_sync_complete_seconds\tscientific_eligible\n")
    lines = [header]
    for case in CASES:
        n, v = data["native"][case], data["nvbit"][case]
        metric = data["summaries"].get(case, {})
        lines.append("\t".join((
            case, str(n["receipt"]["status"]), _fmt(n["first_submission_seconds"]), _fmt(n["first_completion_seconds"]), _fmt(n["elapsed_seconds"]),
            str(v["receipt"]["status"]), _fmt(v["first_submission_seconds"]), _fmt(v["first_completion_seconds"]), _fmt(v["elapsed_seconds"]),
            str(metric.get("first_problematic_kernel", "NA")), str(metric.get("related_function_count", "NA")), str(metric.get("enumerated_function_count", "NA")), str(metric.get("total_static_instruction_count", "NA")),
            _fmt(metric.get("instruction_discovery_seconds")), _fmt(metric.get("insertion_seconds")), _fmt(metric.get("enable_seconds")), _fmt(metric.get("launch_return_to_sync_complete_seconds")), "FALSE",
        )) + "\n")
    return "".join(lines)


def receipt(data: dict[str, Any], raw_index_path: Path) -> dict[str, Any]:
    c2, c3, c4 = (data["summaries"][case] for case in CASES[2:])
    return {
        "schema_version": SCHEMA,
        "status": STATUS,
        "scientific_eligible": False,
        "scope": "PYTORCH_C0_TO_C4_NVBIT_INSTRUMENTATION_ISOLATION_ONLY_NOT_TRACE_NOT_MODEL_NOT_C_TARGET_NOT_TIMING",
        "runtime_source_commit": RUNTIME_COMMIT,
        "nvbit_timing_probe_sha256": TOOL_SHA,
        "environment": {"gpu": "NVIDIA GeForce RTX 3090 / SM86", "driver": "570.124.04", "torch": "2.5.1+cu124", "cuda": "12.4", "libtorch_cuda_sha256": "761b14acafb8b02011e32d11bd437b63cca3fe882b9c4a02c89fd01d738ccb6a"},
        "test_matrix": {"independent_processes": 10, "native_completed": 5, "nvbit_completed": 5, "timeout_count": 0, "trace_generated": False, "raw_trace_bytes": 0},
        "first_problematic_kernel": {"testcase": "C4_SMALL_GEMM_LIBRARY_KERNEL", "function": c4["first_problematic_kernel"]},
        "timing_boundary": {"C2": c2, "C3": c3, "C4": c4, "slowest_specific_stage": "NVBIT_GET_INSTRS_RELATED_FUNCTION_DISCOVERY", "slowest_specific_stage_seconds": c4["instruction_discovery_seconds"]},
        "classification": {"A_legitimate_extreme_first_instrumentation_latency": "NOT_SUPPORTED_BY_C2_OR_C3; C4_COMPLETED_WITHIN_60_SECONDS", "B_instrumentation_size_explosion": "SUPPORTED_FOR_C4_RELATED_FUNCTION_DISCOVERY", "C_nvbit_pytorch_compatibility_issue": "NOT_SUPPORTED_BY_MINIMAL_PYTORCH_C2_C4_COMPLETION", "D_synchronization_deadlock": "NOT_SUPPORTED_BY_COMPLETION_AND_PROGRESSING_GET_INSTRS_MARKERS"},
        "stack_snapshot_evidence": {"C4_snapshot_count": 5, "main_thread_wchan": "do_wait", "process_cpu_percent_samples": [97.8, 53.8, 37.2, 28.5], "marker_progress": "GET_INSTRS_BEGIN_END_ADVANCED_DURING_SNAPSHOTS", "kernel_stack_access": "DENIED_BY_NODE_PERMISSION_POLICY; WCHAN_AND_SYSCALL_RETAINED"},
        "long_watch": {"requested_by_this_diagnostic": False, "authorized_by_this_diagnostic": False, "technical_readiness": "LONGER_WATCH_MAY_BE_WORTH_REQUESTING_ONLY_FOR_A_FRESH_EXPLICITLY_AUTHORIZED_EXACT_FUNCTION_OR_RELATED_FUNCTION_BOUNDED_DIAGNOSTIC; EXISTING_ONE_SHOT_LONG_WATCH_REMAINS_CLOSED"},
        "raw_artifact_index": {"path": str(raw_index_path), "sha256": sha256_file(raw_index_path)},
        "terminal_state": "PYTORCH_NVBIT_FIRST_KERNEL_BOUNDARY_LOCALIZED_NO_MODEL_OR_C_TARGET_AUTHORIZATION",
    }


def report(data: dict[str, Any]) -> str:
    c4 = data["summaries"]["C4_SMALL_GEMM_LIBRARY_KERNEL"]
    c3 = data["summaries"]["C3_ELEMENTWISE_FIRST_KERNEL"]
    return f"""# Retry570 PyTorch/NVBit first-kernel stage diagnostic

Status: `{STATUS}`.

This is a bounded diagnostic-only C0--C4 matrix: no trace, model, Llama,
Qwen, C target, or scientific timing/capture was run. All ten independent
processes completed before their fixed 60-second wall limit. The old 300-second
one-shot watch remains closed and was not rerun.

The minimal reproducible slow case is `C4_SMALL_GEMM_LIBRARY_KERNEL`. Its first
launch was `{c4['first_problematic_kernel']}`. NVBit reported 89 related
functions and enumerated 88 distinct functions through `nvbit_get_instrs()`.
That instruction-discovery stage took {c4['instruction_discovery_seconds']:.6f}
seconds for {c4['total_static_instruction_count']} total static instructions;
insertion took {c4['insertion_seconds']:.6f} seconds, enable took
{c4['enable_seconds']:.6f} seconds, and launch-return through synchronized
completion took {c4['launch_return_to_sync_complete_seconds']:.6f} seconds.
The complete C4 probe duration was {c4['full_probe_seconds']:.6f} seconds and
the PyTorch child completed at {data['nvbit']['C4_SMALL_GEMM_LIBRARY_KERNEL']['first_completion_seconds']:.6f} seconds.

By contrast, C3's single-related-function add kernel completed NVBit discovery
in {c3['instruction_discovery_seconds']:.6f} seconds and its full probe in
{c3['full_probe_seconds']:.6f} seconds. C2/C3/C4 all emitted launch,
instruction-discovery, insertion, enable, and synchronization markers.

The C4 five-second snapshots saw a live GPU-attached process, advancing
`GET_INSTRS` markers and host CPU samples of 97.8%, 53.8%, 37.2%, and 28.5%.
The main thread's `wchan` was `do_wait`, consistent with a child-process wait
during tool-side instruction discovery; most other threads were in futex wait.
The node denied `/proc/.../stack` reads even as root, so the retained evidence
uses non-destructive `wchan` and syscall snapshots rather than claiming a
symbolized native stack.

Conclusion: this supports B, an NVBit related-function/static-instruction
discovery expansion in the GEMM library universe. It does not support a
deadlock (D) or a general minimal PyTorch/NVBit incompatibility (C), because
the C2--C4 first kernels all completed. It also does not establish a need to
run longer: a future, separately authorized long diagnostic could be useful
only if it retains an exact and bounded function/related-function scope. This
publication grants no such authorization and does not reopen the closed
one-shot long-watch, model, trace, or C-target paths.
"""


def manifest(directory: Path) -> dict[str, Any]:
    return {"schema_version": "C16_G_RETRY570_PYTORCH_STAGE_PUBLISH_V1", "status": STATUS, "scientific_eligible": False, "runtime_source_commit": RUNTIME_COMMIT, "files": [{"path": item, "size_bytes": (directory / item).stat().st_size, "sha256": sha256_file(directory / item)} for item in PAYLOADS], "raw_profiler_payloads_committed": False, "remote_only_required_artifact_count": 0}


def validate(directory: Path) -> dict[str, Any]:
    publication = _load(directory / MANIFEST)
    rows, seen = publication.get("files"), set()
    if publication.get("status") != STATUS or publication.get("scientific_eligible") is not False or not isinstance(rows, list):
        raise ContractError("stage-diagnostic publication manifest malformed")
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("path"), str) or row["path"] not in PAYLOADS or row["path"] in seen:
            raise ContractError("stage-diagnostic manifest path malformed or duplicate")
        path = directory / row["path"]
        if not isinstance(row.get("size_bytes"), int) or not valid_sha256(row.get("sha256")) or not path.is_file() or path.stat().st_size != row["size_bytes"] or sha256_file(path) != row["sha256"]:
            raise ContractError("stage-diagnostic manifest payload fails existence/size/SHA closure")
        seen.add(row["path"])
    if seen != set(PAYLOADS) or _load(directory / RECEIPT).get("status") != STATUS:
        raise ContractError("stage-diagnostic publication set or receipt is incomplete")
    return {"schema_version": "C16_G_RETRY570_PYTORCH_STAGE_PUBLISH_VALIDATION_V1", "status": "PASS", "publish_manifest": {"path": MANIFEST, "sha256": sha256_file(directory / MANIFEST)}, "checks": {"payload_count": len(rows), "duplicate_path_count": 0, "missing_path_count": 0, "size_or_sha256_failure_count": 0, "manifest_references_only_materialized_payloads": True, "scientific_eligible": False}}


def write(directory: Path, raw: Path) -> None:
    data = observe(raw)
    directory.mkdir(parents=True, exist_ok=True)
    atomic_json(directory / RAW_INDEX, {"schema_version": "C16_G_RETRY570_PYTORCH_STAGE_RAW_INDEX_V1", "status": "LOCAL_HASH_CLOSED_NONSCIENTIFIC_DIAGNOSTIC_ONLY", "scientific_eligible": False, "remote_raw_root": "/root/autodl-tmp/c16_retry570/raw/pytorch_stage_isolation_20260913_982135c", "local_raw_root": str(raw), "remote_manifest_sha256": data["remote_manifest_sha256"], "entries": data["rows"], "tree_sha256": data["tree_sha256"], "execution_budget_ledger_after": {"relative_path": "EXECUTION_BUDGET_LEDGER_AFTER.json", "sha256": data["ledger_sha256"]}, "remote_only_required_artifact_count": 0})
    atomic_json(directory / RECEIPT, receipt(data, directory / RAW_INDEX))
    atomic_json(directory / TRANSFER, {"schema_version": "C16_G_RETRY570_PYTORCH_STAGE_TRANSFER_V1", "status": "PASS_REMOTE_TO_LOCAL_CHECKSUM_CLOSURE", "scientific_eligible": False, "remote_raw_root": "/root/autodl-tmp/c16_retry570/raw/pytorch_stage_isolation_20260913_982135c", "local_raw_root": str(raw), "remote_manifest_sha256": data["remote_manifest_sha256"], "local_tree_sha256": data["tree_sha256"], "file_count": len(data["rows"]), "total_bytes": sum(int(row["size_bytes"]) for row in data["rows"]), "rsync_checksum_dry_run": "NO_DIFFERENCES", "remote_only_required_artifact_count": 0, "active_gpu_process_count_at_closeout": 0, "raw_payloads_committed": False})
    (directory / MATRIX).write_text(matrix(data), encoding="utf-8")
    (directory / REPORT).write_text(report(data), encoding="utf-8")
    atomic_json(directory / MANIFEST, manifest(directory))
    atomic_json(directory / VALIDATION, validate(directory))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--raw-root", type=Path, required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--validate", action="store_true")
    args = parser.parse_args()
    if args.write:
        write(args.directory, args.raw_root)
        print(f"PASS Retry570 PyTorch/NVBit stage closeout write: {args.directory}")
    else:
        print("PASS Retry570 PyTorch/NVBit stage closeout validation: " + canonical_json(validate(args.directory)["checks"]))


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        raise SystemExit(f"FAIL Retry570 PyTorch/NVBit stage closeout: {exc}")
