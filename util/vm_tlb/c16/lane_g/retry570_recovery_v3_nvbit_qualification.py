#!/usr/bin/env python3
"""Run one Recovery-V3 diagnostic NVBit qualification under a fresh lease.

The existing model qualification child is deliberately reused: it verifies
the immutable parent lease/token/lock and never opens the historical C16
budget ledger.  This parent owns exactly one campaign-scoped NVBit lease and
the transient measurement marker.  It supports only direct launch inventory
exact-function static-map evidence, and a one-instruction MREF discriminator.
It is never a timing or formal-trace producer.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
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
from retry570_recovery_v3_campaign_budget import RecoveryV3CampaignLease, initialize
from runtime_native_runner import load_binding


SCHEMA = "C16_G_RECOVERY_V3_NVBIT_QUALIFICATION_V1"
MODES = ("NVBIT_LAUNCH_INVENTORY", "NVBIT_STATIC_MAP", "TARGETED_MEMORY_DISCRIMINATOR")
TERM_GRACE_S = 5


def git_head() -> str:
    return subprocess.check_output(["git", "-C", str(repo_root()), "rev-parse", "HEAD"], text=True).strip()


def tree_bytes(root: Path) -> int:
    return sum(item.stat().st_size for item in root.rglob("*") if item.is_file()) if root.is_dir() else 0


def verify_code_object(path: Path, expected_sha256: str) -> dict[str, str]:
    """Bind the declared loaded CUDA code object to its actual local file."""
    if not path.is_file():
        raise ContractError("declared libtorch CUDA code-object path is absent")
    actual = sha256_file(path)
    if actual != expected_sha256:
        raise ContractError("actual libtorch CUDA code-object SHA256 differs from frozen expected SHA256")
    return {"path": str(path), "sha256": actual}


def validate_static_map(path: Path, *, function: str, code_object_sha256: str) -> dict[str, Any]:
    """Validate native-map semantics; a nonempty file alone is not evidence."""
    required = ("nvbit_static_index", "vector_ordinal", "instruction_offset", "opcode", "memory_space",
                "is_load", "is_store", "has_mref", "sass", "function_full_name",
                "function_mangled_name", "function_address", "libtorch_cuda_sha256")
    if not path.is_file() or path.stat().st_size == 0:
        raise ContractError("NVBit native static map is absent or empty")
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames != list(required):
            raise ContractError("NVBit native static map schema differs")
        rows = list(reader)
    if not rows:
        raise ContractError("NVBit native static map has no static instruction rows")
    indices: list[int] = []
    for row in rows:
        if row["function_mangled_name"] != function or row["libtorch_cuda_sha256"] != code_object_sha256:
            raise ContractError("NVBit native static map function/code-object binding differs")
        try:
            index = int(row["nvbit_static_index"])
        except ValueError as exc:
            raise ContractError("NVBit native static map contains an unparsable static index") from exc
        if index < 0:
            raise ContractError("NVBit native static map contains a negative static index")
        indices.append(index)
    if len(indices) != len(set(indices)):
        raise ContractError("NVBit native static map repeats a static index")
    return {"path": str(path), "sha256": sha256_file(path), "static_instruction_count": len(rows),
            "function_mangled_name": function, "libtorch_cuda_sha256": code_object_sha256,
            "static_index_unique": True}


def kill_group(process: subprocess.Popen[str]) -> dict[str, bool | int]:
    result: dict[str, bool | int] = {"required": False, "term_sent": False, "kill_sent": False, "grace_s": TERM_GRACE_S}
    if process.poll() is None:
        os.killpg(process.pid, signal.SIGTERM); result.update(required=True, term_sent=True)
        try:
            process.wait(timeout=TERM_GRACE_S)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL); result["kill_sent"] = True; process.wait(timeout=TERM_GRACE_S)
    return result


def identity(binding: dict[str, Any], args: argparse.Namespace) -> dict[str, str]:
    return {
        "deployment_id": binding["deployment_id"], "model_id": binding["model_id"],
        "model_revision": binding["model_revision"], "tokenizer_revision": binding["tokenizer_revision"],
        "scenario_id": binding["scenario"]["scenario_id"], "input_hash": binding["input"]["raw_input_sha256"],
        "implementation_key": args.implementation_key, "dtype": args.dtype,
        "quantization": args.quantization, "run_id": args.run_id, "code_commit": git_head(),
    }


def child_command(args: argparse.Namespace, inventory: Path | None, static_map: Path | None,
                  target_log: Path | None) -> list[str]:
    command = [sys.executable, str(Path(__file__).with_name("nvbit_model_qualify.py")),
               "--receipt", str(args.child_receipt), "--binding-receipt", str(args.binding),
               "--raw-dir", str(args.raw_dir), "--budget-ledger", str(args.campaign_ledger),
               "--mode", "TARGETED_MEMORY_TRACE" if args.mode == "TARGETED_MEMORY_DISCRIMINATOR" else args.mode,
               "--tool-path", str(args.tool), "--tool-sha256", args.tool_sha256,
               "--adapter", args.adapter, "--implementation-key", args.implementation_key,
               "--dtype", args.dtype, "--quantization", args.quantization, "--run-id", args.run_id,
               "--expected-output-checksum", args.expected_output_checksum,
               "--expected-attention-backend", args.expected_attention_backend,
               "--runtime-code-commit", args.runtime_code_commit, "--recovery-v3-generic",
               "--parent-lease-receipt", str(args.parent_lease_receipt),
               "--runtime-deployment-id", args.recovery_deployment_id]
    if inventory is not None:
        command.extend(("--launch-inventory-path", str(inventory)))
    if static_map is not None and target_log is None:
        command.extend(("--static-map-path", str(static_map)))
    if target_log is not None:
        command.extend(("--trace-evidence-glob", target_log.name,
                        "--trace-evidence-marker", r"C16_TARGETED_NVBIT_MEMORY_RECORD .*present=[01]",
                        "--static-map-path", str(static_map),
                        "--target-instruction-receipt", str(args.target_receipt)))
    return command


def targeted_memory_evidence(path: Path, target: dict[str, Any]) -> dict[str, Any]:
    """Parse the one exact-target diagnostic without using timing evidence."""
    import re
    if not path.is_file():
        raise ContractError("targeted-memory child stdout is absent")
    content = path.read_text(encoding="utf-8", errors="replace")
    function = str(target["function"]["mangled_name"])
    static_index = int(target["target_instruction"]["nvbit_static_index"])
    launch_pattern = re.compile(
        r"C16_TARGETED_NVBIT_FUNCTION_LAUNCH function_mangled=([^ ]+) launch_id=(\d+) nvbit_static_index=(\d+)"
    )
    record_pattern = re.compile(
        r"C16_TARGETED_NVBIT_MEMORY_RECORD function_mangled=([^ ]+) present=([01]) "
        r"address=0x([0-9a-fA-F]+) launch_id=(\d+) nvbit_static_index=(\d+) "
        r"callback_count=(\d+) predicate_true_count=(\d+) active_lane_count=(\d+) "
        r"nonzero_mref_count=(\d+) zero_mref_count=(\d+)"
    )
    launches = [match.groups() for match in launch_pattern.finditer(content)
                if match.group(1) == function and int(match.group(3)) == static_index]
    # A predicate-false invocation leaves the device-owned record entirely
    # zeroed, including its stored static index.  The host-side launch marker
    # plus exact function identity and the freshly re-emitted map still bind
    # it to the selected static index; do not discard that decisive
    # predicate-off evidence merely because no device lane claimed the record.
    records = [match.groups() for match in record_pattern.finditer(content)
               if match.group(1) == function and
               (int(match.group(5)) == static_index or
                (match.group(2) == "0" and int(match.group(5)) == 0))]
    if not launches:
        raise ContractError("targeted-memory diagnostic did not prove exact target launch")
    if not records:
        raise ContractError("targeted-memory diagnostic did not prove target callback completion")
    totals = {
        "callback_count": sum(int(row[5]) for row in records),
        "predicate_true_count": sum(int(row[6]) for row in records),
        "active_lane_count": sum(int(row[7]) for row in records),
        "nonzero_mref_count": sum(int(row[8]) for row in records),
        "zero_mref_count": sum(int(row[9]) for row in records),
    }
    return {
        "stdout_path": str(path), "stdout_sha256": sha256_file(path),
        "exact_function_launch_count": len(launches),
        "memory_record_callback_count": len(records),
        "memory_record_present_values": [int(row[1]) for row in records],
        "observed_record_static_indices": [int(row[4]) for row in records],
        "zeroed_device_record_static_index_allowed_only_for_predicate_false": any(
            int(row[4]) == 0 and int(row[1]) == 0 for row in records),
        "representative_addresses": ["0x" + row[2] for row in records],
        **totals,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=MODES, required=True)
    parser.add_argument("--phase", choices=("PREFILL", "DECODE"), required=True)
    for name in ("binding", "campaign_ledger", "historical_ledger", "tool", "nvdisasm", "receipt", "child_receipt", "parent_lease_receipt", "stdout", "stderr", "raw_dir"):
        parser.add_argument("--" + name.replace("_", "-"), type=Path, required=True)
    parser.add_argument("--historical-ledger-sha256", required=True)
    parser.add_argument("--budget-scope", required=True)
    parser.add_argument("--tool-sha256", required=True)
    parser.add_argument("--recovery-deployment-id", required=True)
    parser.add_argument("--adapter", required=True); parser.add_argument("--implementation-key", required=True)
    parser.add_argument("--dtype", choices=("float16", "bfloat16"), required=True); parser.add_argument("--quantization", required=True)
    parser.add_argument("--run-id", required=True); parser.add_argument("--runtime-code-commit", required=True)
    parser.add_argument("--expected-output-checksum", required=True); parser.add_argument("--expected-attention-backend", required=True)
    parser.add_argument("--target-function")
    parser.add_argument("--code-object-sha256")
    parser.add_argument("--code-object-path", type=Path)
    parser.add_argument("--target-receipt", type=Path)
    parser.add_argument("--direct-function-binding", type=Path)
    parser.add_argument("--route-b-llama-s0", action="store_true",
                        help="allow only the frozen H Route-B Llama S0 inventory/map diagnostic")
    parser.add_argument("--target-cap-seconds", type=int, default=180)
    args = parser.parse_args()
    try:
        if str(uuid.UUID(args.run_id)) != args.run_id: raise ValueError
    except ValueError:
        parser.error("--run-id must be canonical UUID")
    if args.runtime_code_commit != git_head(): raise ContractError("runtime source commit differs from active checkout")
    if not 1 <= args.target_cap_seconds <= 1200: raise ContractError("diagnostic cap must be within the frozen 20-minute bound")
    if not args.tool.is_file() or sha256_file(args.tool) != args.tool_sha256 or not args.nvdisasm.is_file():
        raise ContractError("tool/nvdisasm identity closure differs")
    if any(path.exists() for path in (args.receipt, args.child_receipt, args.parent_lease_receipt, args.stdout, args.stderr)) or args.raw_dir.exists():
        raise ContractError("qualification refuses to overwrite retained evidence")
    binding = load_binding(args.binding, canary=False)
    if binding["scenario"]["scenario_id"] == "S0":
        allowed = (
            args.route_b_llama_s0 and args.mode in {"NVBIT_LAUNCH_INVENTORY", "NVBIT_STATIC_MAP"}
            and binding.get("model_id") == "meta-llama/Llama-3.2-1B"
            and binding.get("model_revision") == "4e20de362430cd3b72f300e6b0f18e50e7166e08"
            and binding["scenario"].get("batch_size") == 1
            and binding["scenario"].get("prefill_tokens") == 128
            and binding["scenario"].get("decode_tokens") == 4
        )
        if not allowed:
            raise ContractError("S0 requires the explicit frozen Route-B Llama inventory/static-map contract")
    elif args.route_b_llama_s0:
        raise ContractError("Route-B Llama S0 override cannot target a non-S0 binding")
    ident = identity(binding, args)
    if args.recovery_deployment_id != ident["deployment_id"]: raise ContractError("recovery deployment identity differs from frozen binding")
    target: dict[str, Any] | None = None
    if args.mode == "TARGETED_MEMORY_DISCRIMINATOR":
        if args.target_receipt is None or args.direct_function_binding is None:
            raise ContractError("targeted-memory mode requires closed target and direct-function binding receipts")
        try:
            target = json.loads(args.target_receipt.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ContractError("targeted-memory target receipt is unreadable") from exc
        require_contract(binding, target, "RECOVERY_PREFILL" if args.phase == "PREFILL" else "RECOVERY_DECODE", recovery_v3_generic=True,
                         direct_function_binding=args.direct_function_binding)
        target_function = str(target["function"]["mangled_name"])
        target_code_sha = str(target["function"]["libtorch_cuda_sha256"])
        if args.target_function and args.target_function != target_function:
            raise ContractError("declared target function differs from closed target receipt")
        if args.code_object_sha256 and args.code_object_sha256 != target_code_sha:
            raise ContractError("declared code-object SHA differs from closed target receipt")
        args.target_function, args.code_object_sha256 = target_function, target_code_sha
    code_object: dict[str, str] | None = None
    if args.mode in ("NVBIT_STATIC_MAP", "TARGETED_MEMORY_DISCRIMINATOR"):
        if not args.target_function or not args.code_object_sha256 or args.code_object_path is None:
            raise ContractError("static-map mode requires exact function, expected SHA256, and actual code-object path")
        code_object = verify_code_object(args.code_object_path, args.code_object_sha256)
    initialize(ledger_path=args.campaign_ledger, historical_ledger=args.historical_ledger,
               expected_historical_sha256=args.historical_ledger_sha256, identity=ident, budget_scope=args.budget_scope)
    MeasurementActive.assert_available(args.campaign_ledger)
    for path in (args.receipt, args.child_receipt, args.parent_lease_receipt, args.stdout, args.stderr): path.parent.mkdir(parents=True, exist_ok=True)
    args.raw_dir.mkdir(parents=True)
    inventory = args.raw_dir / "DIRECT_LAUNCH_INVENTORY.tsv" if args.mode == "NVBIT_LAUNCH_INVENTORY" else None
    static_map = args.raw_dir / ("NVBIT_TARGETED_STATIC_MAP.tsv" if args.mode == "TARGETED_MEMORY_DISCRIMINATOR" else "EXACT_FUNCTION_STATIC_MAP.tsv") if args.mode in ("NVBIT_STATIC_MAP", "TARGETED_MEMORY_DISCRIMINATOR") else None
    target_log = args.raw_dir / "targeted_tool_stdout.log" if args.mode == "TARGETED_MEMORY_DISCRIMINATOR" else None
    started = time.monotonic(); process: subprocess.Popen[str] | None = None; parent: dict[str, Any] | None = None; cleanup: dict[str, bool | int] = {"required": False}; terminal = "FAILED_OR_ABORTED"
    with RecoveryV3CampaignLease(args.campaign_ledger, ident, "NVBIT", capture=True, budget_scope=args.budget_scope) as lease:
        if lease.max_elapsed_seconds < args.target_cap_seconds: raise ContractError("campaign lease cannot cover diagnostic cap")
        parent, token = write_parent_lease_start(args.parent_lease_receipt, {"identity": ident}, "nvbit_diagnostic", lease)
        env = os.environ.copy(); env.pop("LD_PRELOAD", None); env.update(nvdisasm_environment_contract(args.nvdisasm, env.get("PATH", "")))
        env.update({"CUDA_MODULE_LOADING": "EAGER", "CUDA_INJECTION64_PATH": str(args.tool),
                    "C16_NVBIT_LD_PRELOAD_DECLARATION": str(args.tool), "C16_G_PARENT_LEASE_RECEIPT": str(args.parent_lease_receipt),
                    "C16_G_PARENT_LEASE_TOKEN": token, "C16_G_MEASUREMENT_ACTIVE_MARKER": str(args.campaign_ledger.parent.parent / "control" / "MEASUREMENT_ACTIVE")})
        if inventory is not None: env["C16_NVBIT_LAUNCH_INVENTORY_PATH"] = str(inventory)
        if static_map is not None:
            if not args.target_function or not args.code_object_sha256 or len(args.code_object_sha256) != 64:
                raise ContractError("static-map mode requires exact function and code-object SHA256")
            env.update({"C16_NVBIT_TARGET_FUNCTION_MANGLED": args.target_function,
                        "C16_NVBIT_STATIC_MAP_PATH": str(static_map),
                        "C16_NVBIT_CODE_OBJECT_SHA256": args.code_object_sha256})
            if args.mode == "TARGETED_MEMORY_DISCRIMINATOR":
                if target is None:
                    raise ContractError("targeted-memory target state is absent")
                env["C16_NVBIT_TARGET_INSTR_INDEX"] = str(target["target_instruction"]["nvbit_static_index"])
        # TARGETED_MEMORY_DISCRIMINATOR must retain its child output under the
        # raw directory because the child validates real callback evidence
        # there.  The parent stdout remains a compact receipt-only stream.
        child_stdout_path = target_log if target_log is not None else args.stdout
        with child_stdout_path.open("w", encoding="utf-8") as out, args.stderr.open("w", encoding="utf-8") as err:
            with MeasurementActive(args.campaign_ledger, ident, "NVBIT_RECOVERY_V3_QUALIFICATION"):
                process = subprocess.Popen(child_command(args, inventory, static_map, target_log), stdout=out, stderr=err, text=True, env=env, start_new_session=True)
                while process.poll() is None and time.monotonic() - started < args.target_cap_seconds: time.sleep(0.05)
        if process.poll() is None: cleanup = kill_group(process); terminal = "BOUNDED_TIMEOUT"
        elif process.returncode == 0: terminal = "COMPLETE"
        elapsed, raw_bytes = time.monotonic() - started, tree_bytes(args.raw_dir)
        lease.finish(elapsed_seconds=elapsed, raw_bytes=raw_bytes, terminal_status=terminal,
                     evidence_classification="NON_SCIENTIFIC_DIAGNOSTIC",
                     diagnostic_reason="RECOVERY_V3_DIRECT_NVBIT_IDENTITY_QUALIFICATION_NOT_FOR_TIMING")
    closeout = write_parent_lease_closeout(args.parent_lease_receipt, parent, terminal_status=terminal,
                                           elapsed_seconds=time.monotonic() - started, returncode=None if process is None else process.returncode)
    payload = inventory if inventory is not None else static_map
    if target_log is not None:
        atomic_json(args.stdout, {
            "schema_version": SCHEMA, "event": "PARENT_STDOUT_RECEIPT",
            "child_stdout_path": str(target_log),
            "child_stdout_sha256": sha256_file(target_log) if target_log.is_file() else None,
        })
    result = {"schema_version": SCHEMA, "status": "COMPLETE" if terminal == "COMPLETE" else terminal,
              "scientific_eligible_for_timing": False, "child_acquired_second_lease": False,
              "identity": ident, "mode": args.mode,
              "phase": args.phase,
              "budget_scope": args.budget_scope, "target_cap_seconds": args.target_cap_seconds,
              "target_wall_seconds": time.monotonic() - started, "cleanup": cleanup,
              "parent_lease_closeout": {"path": str(closeout), "sha256": sha256_file(closeout)},
              "payload": {"path": str(payload), "exists": payload.is_file(), "bytes": payload.stat().st_size if payload.is_file() else 0, "sha256": sha256_file(payload) if payload.is_file() else "NA"},
              "raw_bytes": tree_bytes(args.raw_dir), "stdout_sha256": sha256_file(args.stdout), "stderr_sha256": sha256_file(args.stderr)}
    if code_object is not None:
        result["code_object"] = code_object
    if static_map is not None and terminal == "COMPLETE":
        result["validated_static_map"] = validate_static_map(
            static_map, function=str(args.target_function), code_object_sha256=str(args.code_object_sha256))
    if args.mode == "TARGETED_MEMORY_DISCRIMINATOR":
        if target is None or target_log is None:
            raise ContractError("internal targeted-memory discriminator state is absent")
        result["target_receipt"] = {"path": str(args.target_receipt), "sha256": sha256_file(args.target_receipt)}
        result["direct_function_binding"] = {"path": str(args.direct_function_binding), "sha256": sha256_file(args.direct_function_binding)}
        if terminal == "COMPLETE":
            evidence = targeted_memory_evidence(target_log, target)
            result["targeted_memory_evidence"] = evidence
            if evidence["predicate_true_count"] == 0:
                result["status"] = "COMPLETE_PREDICATED_OFF_TARGET"
            elif evidence["nonzero_mref_count"] == 0:
                result["status"] = "COMPLETE_ZERO_ADDRESS_MREF"
            else:
                result["status"] = "COMPLETE_VALID_ADDRESS_BEARING"
    atomic_json(args.receipt, result)
    print(json.dumps({"status": result["status"], "receipt": str(args.receipt), "payload": result["payload"]}, sort_keys=True))
    if terminal != "COMPLETE" or not payload.is_file() or payload.stat().st_size == 0: raise SystemExit(2)


if __name__ == "__main__":
    try: main()
    except ContractError as exc: raise SystemExit(f"FAIL Recovery-V3 NVBit qualification: {exc}")
