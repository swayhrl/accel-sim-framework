#!/usr/bin/env python3
"""Bound one direct NVBit memory-record discriminator under Recovery V3.

This is deliberately diagnostic-only.  It answers whether a frozen, NVBit-
native static instruction in one exact full CUDA function emits an address
record when the immutable model workload executes.  It is not a C16 trace
producer, never contributes timing data, and cannot turn a target into a
scientific capture result.

The parent holds the only RecoveryBudgetLease and the active measurement
marker.  The injected wrapper-owned child verifies the parent receipt/token/lock
and does not open a second lease.  An external process-group guard bounds the child;
all materialized raw payloads (including a failed child stdout/map) are
accounted by the parent before its receipt is published.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import signal
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json, repo_root, sha256_file
from execution_budget import MeasurementActive
from profiler_wrapper import write_parent_lease_closeout, write_parent_lease_start
from retry570_long_watch import nvdisasm_environment_contract
from retry570_multimodel_capture import require_contract
from retry570_recovery_budget import RecoveryBudgetLease, initialize as initialize_recovery_budget
from runtime_native_runner import load_binding


SCHEMA = "C16_G_RECOVERY_V3_TARGETED_MEMORY_DISCRIMINATOR_V1"
TERM_GRACE_S = 5
RECORD_MARKER = r"C16_TARGETED_NVBIT_MEMORY_RECORD .*present=([01])"


def git_head() -> str:
    return subprocess.check_output(["git", "-C", str(repo_root()), "rev-parse", "HEAD"], text=True).strip()


def raw_tree_bytes(root: Path) -> int:
    return sum(path.stat().st_size for path in root.rglob("*") if path.is_file()) if root.is_dir() else 0


def identity(binding: dict[str, Any], args: argparse.Namespace) -> dict[str, str]:
    return {
        "deployment_id": args.recovery_deployment_id,
        "model_id": binding["model_id"],
        "model_revision": binding["model_revision"],
        "tokenizer_revision": binding["tokenizer_revision"],
        "scenario_id": binding["scenario"]["scenario_id"],
        "input_hash": binding["input"]["raw_input_sha256"],
        "implementation_key": args.implementation_key,
        "dtype": args.dtype,
        "quantization": args.quantization,
        "run_id": args.run_id,
        "code_commit": git_head(),
    }


def kill_group(process: subprocess.Popen[str]) -> dict[str, Any]:
    result = {"required": False, "term_sent": False, "kill_sent": False, "grace_s": TERM_GRACE_S}
    if process.poll() is None:
        os.killpg(process.pid, signal.SIGTERM)
        result.update(required=True, term_sent=True)
        try:
            process.wait(timeout=TERM_GRACE_S)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            result["kill_sent"] = True
            process.wait(timeout=TERM_GRACE_S)
    return result


def map_target_evidence(path: Path, target: dict[str, Any]) -> dict[str, Any]:
    """Prove the newly emitted map still contains the exact frozen target."""
    if not path.is_file() or path.stat().st_size == 0:
        raise ContractError("targeted diagnostic emitted no NVBit-native static map")
    index = str(target["target_instruction"]["nvbit_static_index"])
    function = str(target["function"]["mangled_name"])
    opcode = str(target["target_instruction"]["opcode"])
    expected_sha = str(target["function"]["libtorch_cuda_sha256"])
    rows = path.read_text(encoding="utf-8", errors="strict").splitlines()
    if not rows or not rows[0].startswith("nvbit_static_index\tvector_ordinal\tinstruction_offset\topcode\tmemory_space"):
        raise ContractError("targeted diagnostic static map has an unexpected schema")
    matches = []
    for row in rows[1:]:
        fields = row.split("\t")
        if len(fields) < 13:
            raise ContractError("targeted diagnostic static map has a malformed row")
        if fields[0] == index and fields[3] == opcode and fields[4] == "GLOBAL" and fields[10] == function and fields[12] == expected_sha:
            matches.append(fields)
    if len(matches) != 1:
        raise ContractError("new NVBit-native map does not uniquely reproduce the frozen target instruction")
    row = matches[0]
    return {
        "path": str(path), "size_bytes": path.stat().st_size, "sha256": sha256_file(path),
        "static_index": int(row[0]), "vector_ordinal": int(row[1]), "instruction_offset": int(row[2]),
        "opcode": row[3], "memory_space": row[4], "satisfies_direct_global_mref": row[7] == "1",
        "function_mangled_name": row[10], "libtorch_cuda_sha256": row[12],
    }


def marker_evidence(path: Path, target: dict[str, Any]) -> dict[str, Any]:
    if not path.is_file():
        raise ContractError("targeted diagnostic stdout evidence is absent")
    content = path.read_text(encoding="utf-8", errors="replace")
    function = str(target["function"]["mangled_name"])
    index = int(target["target_instruction"]["nvbit_static_index"])
    launches = re.findall(r"C16_TARGETED_NVBIT_FUNCTION_LAUNCH function_mangled=([^ ]+) launch_id=(\d+) nvbit_static_index=(\d+)", content)
    records = re.findall(RECORD_MARKER, content)
    exact_launches = [item for item in launches if item[0] == function and int(item[2]) == index]
    if not exact_launches:
        raise ContractError("targeted diagnostic did not prove an exact target-function launch")
    if not records:
        raise ContractError("targeted diagnostic did not reach a direct memory-record callback")
    values = [int(value) for value in records]
    return {
        "stdout_path": str(path), "stdout_sha256": sha256_file(path),
        "exact_function_launch_count": len(exact_launches),
        "memory_record_callback_count": len(values),
        "memory_record_present_values": values,
        "memory_record_present": any(values),
    }


def child_command(args: argparse.Namespace, *, raw_dir: Path, stdout_path: Path, static_map: Path) -> list[str]:
    return [
        sys.executable, str(Path(__file__).with_name("nvbit_model_qualify.py")),
        "--receipt", str(args.child_receipt), "--binding-receipt", str(args.binding),
        "--raw-dir", str(raw_dir), "--budget-ledger", str(args.recovery_ledger),
        "--mode", "TARGETED_MEMORY_TRACE", "--tool-path", str(args.tool),
        "--tool-sha256", args.tool_sha256, "--trace-evidence-glob", stdout_path.name,
        "--trace-evidence-marker", RECORD_MARKER, "--static-map-path", str(static_map),
        "--target-instruction-receipt", str(args.target_receipt), "--adapter", args.adapter,
        "--implementation-key", args.implementation_key, "--dtype", args.dtype,
        "--quantization", args.quantization, "--run-id", args.run_id,
        "--expected-output-checksum", args.expected_output_checksum,
        "--expected-attention-backend", args.expected_attention_backend,
        "--runtime-code-commit", args.runtime_code_commit, "--recovery-v3-generic",
        "--parent-lease-receipt", str(args.parent_lease_receipt),
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("binding", "target_receipt", "direct_function_binding", "recovery_ledger", "historical_ledger", "historical_archive", "tool", "nvdisasm", "receipt", "stage", "child_receipt", "parent_lease_receipt", "stdout", "stderr", "raw_dir"):
        parser.add_argument("--" + name.replace("_", "-"), type=Path, required=True)
    parser.add_argument("--historical-ledger-sha256", required=True)
    parser.add_argument("--tool-sha256", required=True)
    parser.add_argument("--recovery-deployment-id", required=True)
    parser.add_argument("--adapter", required=True)
    parser.add_argument("--implementation-key", required=True)
    parser.add_argument("--dtype", choices=("float16", "bfloat16"), required=True)
    parser.add_argument("--quantization", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--runtime-code-commit", required=True)
    parser.add_argument("--expected-output-checksum", required=True)
    parser.add_argument("--expected-attention-backend", required=True)
    parser.add_argument("--target-cap-seconds", type=int, default=180)
    args = parser.parse_args()
    try:
        if str(uuid.UUID(args.run_id)) != args.run_id:
            raise ValueError
    except ValueError:
        parser.error("--run-id must be a canonical UUID")
    if args.runtime_code_commit != git_head():
        raise ContractError("targeted diagnostic source commit differs from declared commit")
    if not 1 <= args.target_cap_seconds <= 1200:
        raise ContractError("targeted diagnostic cap must be within the 20-minute hard bound")
    if sha256_file(args.tool) != args.tool_sha256 or not args.nvdisasm.is_file():
        raise ContractError("targeted diagnostic tool/nvdisasm closure differs")
    outputs = (args.receipt, args.stage, args.child_receipt, args.parent_lease_receipt, args.stdout, args.stderr)
    if any(path.exists() for path in outputs) or args.raw_dir.exists():
        raise ContractError("targeted diagnostic refuses to overwrite a retained payload")
    binding = load_binding(args.binding, canary=False)
    target = json.loads(args.target_receipt.read_text(encoding="utf-8"))
    require_contract(binding, target, "RECOVERY_PREFILL", recovery_v3_generic=True,
                     direct_function_binding=args.direct_function_binding)
    ident = identity(binding, args)
    initialize_recovery_budget(
        recovery_ledger=args.recovery_ledger, historical_ledger=args.historical_ledger,
        expected_historical_sha256=args.historical_ledger_sha256,
        deployment_id=args.recovery_deployment_id, historical_archive=args.historical_archive,
    )
    MeasurementActive.assert_available(args.recovery_ledger)
    for path in outputs:
        path.parent.mkdir(parents=True, exist_ok=True)
    args.raw_dir.mkdir(parents=True)
    map_path = args.raw_dir / "NVBIT_TARGETED_STATIC_MAP.tsv"
    stdout_raw = args.raw_dir / "targeted_tool_stdout.log"
    started = time.monotonic(); process: subprocess.Popen[str] | None = None
    terminal = "FAILED_OR_ABORTED"; cleanup = {"required": False}; parent: dict[str, Any] | None = None
    with RecoveryBudgetLease(args.recovery_ledger, ident, "NVBIT", capture=True) as lease:
        if lease.max_elapsed_seconds < args.target_cap_seconds:
            raise ContractError("remaining Recovery V3 NVBit budget cannot cover the bounded discriminator")
        parent, token = write_parent_lease_start(args.parent_lease_receipt, {"identity": ident}, "nvbit_targeted_memory", lease)
        environment = os.environ.copy()
        environment.pop("LD_PRELOAD", None)
        environment.update(nvdisasm_environment_contract(args.nvdisasm, environment.get("PATH", "")))
        environment.update({
            "CUDA_MODULE_LOADING": "EAGER", "CUDA_INJECTION64_PATH": str(args.tool),
            "C16_NVBIT_LD_PRELOAD_DECLARATION": str(args.tool),
            "C16_G_PARENT_LEASE_RECEIPT": str(args.parent_lease_receipt),
            "C16_G_PARENT_LEASE_TOKEN": token,
            "C16_G_MEASUREMENT_ACTIVE_MARKER": str(args.recovery_ledger.parent.parent / "control" / "MEASUREMENT_ACTIVE"),
            "C16_NVBIT_TARGET_FUNCTION_MANGLED": str(target["function"]["mangled_name"]),
            "C16_NVBIT_TARGET_INSTR_INDEX": str(target["target_instruction"]["nvbit_static_index"]),
            "C16_NVBIT_STATIC_MAP_PATH": str(map_path),
            "C16_NVBIT_CODE_OBJECT_SHA256": str(target["function"]["libtorch_cuda_sha256"]),
            "ACTIVE_FROM_START": "0", "USER_DEFINED_FOLDERS": "1",
        })
        with stdout_raw.open("w", encoding="utf-8") as out, args.stderr.open("w", encoding="utf-8") as err:
            with MeasurementActive(args.recovery_ledger, ident, "NVBIT_RECOVERY_TARGETED_MEMORY_DIAGNOSTIC") as marker:
                process = subprocess.Popen(child_command(args, raw_dir=args.raw_dir, stdout_path=stdout_raw, static_map=map_path),
                                           stdout=out, stderr=err, text=True, env=environment, start_new_session=True)
                while process.poll() is None and time.monotonic() - started < args.target_cap_seconds:
                    time.sleep(0.05)
                if process.poll() is None:
                    cleanup = kill_group(process)
                    terminal = "BOUNDED_TIMEOUT"
                elif process.returncode == 0:
                    terminal = "COMPLETE"
        elapsed = time.monotonic() - started
        raw_bytes = raw_tree_bytes(args.raw_dir)
        if raw_bytes > lease.max_raw_bytes:
            raise ContractError("targeted diagnostic raw payload exceeds the Recovery V3 hard ceiling")
        lease.finish(elapsed_seconds=elapsed, raw_bytes=raw_bytes, terminal_status=terminal,
                     evidence_classification="NON_SCIENTIFIC_DIAGNOSTIC",
                     diagnostic_reason="RECOVERY_V3_EXACT_TARGET_MEMORY_RECORD_DISCRIMINATOR_NOT_FOR_TIMING_OR_FORMAL_TRACE")
    closeout = write_parent_lease_closeout(args.parent_lease_receipt, parent, terminal_status=terminal,
                                           elapsed_seconds=time.monotonic() - started,
                                           returncode=None if process is None else process.returncode)
    result: dict[str, Any] = {
        "schema_version": SCHEMA, "status": "COMPLETE" if terminal == "COMPLETE" else terminal,
        "scientific_eligible_for_timing": False, "diagnostic_only_not_for_formal_trace": True,
        "identity": ident, "runtime_code_commit": args.runtime_code_commit,
        "target_cap_seconds": args.target_cap_seconds, "target_wall_seconds": time.monotonic() - started,
        "terminal_status": terminal, "cleanup": cleanup,
        "target_receipt": {"path": str(args.target_receipt), "sha256": sha256_file(args.target_receipt)},
        "direct_function_binding": {"path": str(args.direct_function_binding), "sha256": sha256_file(args.direct_function_binding)},
        "tool": {"path": str(args.tool), "sha256": args.tool_sha256},
        "parent_lease_start": {"path": str(args.parent_lease_receipt), "sha256": sha256_file(args.parent_lease_receipt)},
        "parent_lease_closeout": {"path": str(closeout), "sha256": sha256_file(closeout)},
        "raw": {"path": str(args.raw_dir), "bytes": raw_tree_bytes(args.raw_dir)},
        "stderr": {"path": str(args.stderr), "sha256": sha256_file(args.stderr)},
    }
    if terminal == "COMPLETE":
        result["reproduced_static_target"] = map_target_evidence(map_path, target)
        result["direct_memory_record"] = marker_evidence(stdout_raw, target)
        if not result["direct_memory_record"]["memory_record_present"]:
            result["status"] = "COMPLETE_ZERO_DIRECT_MEMORY_RECORD"
    else:
        result["child_receipt"] = str(args.child_receipt) if args.child_receipt.is_file() else None
        result["stdout"] = {"path": str(stdout_raw), "sha256": sha256_file(stdout_raw)} if stdout_raw.is_file() else None
    atomic_json(args.receipt, result)
    print(f"C16_RECOVERY_TARGETED_MEMORY_DIAGNOSTIC {result['status']} {args.receipt}")
    if terminal != "COMPLETE":
        raise SystemExit(2)


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        raise SystemExit(f"FAIL recovery targeted-memory diagnostic: {exc}")
