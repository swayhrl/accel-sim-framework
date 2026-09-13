#!/usr/bin/env python3
"""Publish Retry570's non-scientific NVBit nvdisasm-path repair gate."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json, canonical_json, sha256_file, valid_sha256

STATUS = "NVBIT_NVDISASM_PATH_CONTRACT_FIXED_RUNTIME_SMOKE_NOT_QUALIFIED"
RUNTIME_COMMIT = "26a24b07f922df259dcc6823d1915c69b6f0f02a"
NORMALIZATION_COMMIT = "c9b0be4435b31f389d34854a937a6dff2e42eb1d"
OFFICIAL_TOOL_SHA = "9751365928a740e86ae421f09ed0f9b0ba38eafa19ee0ac424ae5fd1fead114d"
RAW_INDEX, RECEIPT, TRANSFER, README, MANIFEST, VALIDATION = "RAW_ARTIFACT_INDEX.json", "NVBIT_NVDISASM_PATH_REPAIR_RECEIPT.json", "NVBIT_NVDISASM_PATH_REPAIR_TRANSFER_RECEIPT.json", "README.md", "PUBLISH_MANIFEST.json", "PUBLISH_VALIDATION_RECEIPT.json"
PAYLOADS = (README, RECEIPT, RAW_INDEX, TRANSFER)
REQUIRED_RAW = (
    "ENVIRONMENT_AUDIT_POST_GATE.log", "GATE_A_NVDISASM_VERSION.log", "GATE_B_INPUT_SHA256.txt", "GATE_B_OFFICIAL_NVBIT_RECEIPT.json", "GATE_B_OFFICIAL_NVBIT_STDERR.log", "GATE_B_OFFICIAL_NVBIT_STDOUT.log", "GATE_B_VECTORADD_BUILD.log", "GATE_C_RUNTIME_FIRST_KERNEL_RECEIPT.json", "GATE_C_RUNTIME_FIRST_KERNEL_SAMPLES.jsonl", "GATE_C_RUNTIME_FIRST_KERNEL_STAGE.json", "GATE_C_RUNTIME_FIRST_KERNEL_STDERR.log", "GATE_C_RUNTIME_FIRST_KERNEL_STDOUT.log",
)


def load(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read JSON {path}") from exc
    if not isinstance(payload, dict):
        raise ContractError(f"JSON payload is not object: {path}")
    return payload


def file_index(root: Path) -> list[dict[str, Any]]:
    files = sorted(path for path in root.rglob("*") if path.is_file()) if root.is_dir() else []
    if tuple(str(path.relative_to(root)) for path in files) != REQUIRED_RAW:
        raise ContractError("raw path-repair payload set is incomplete or unexpected")
    return [{"local_relative_path": str(path.relative_to(root)), "size_bytes": path.stat().st_size, "sha256": sha256_file(path)} for path in files]


def digest(rows: list[dict[str, Any]]) -> str:
    hasher = hashlib.sha256()
    for row in rows:
        hasher.update(f"{row['local_relative_path']}\0{row['size_bytes']}\0{row['sha256']}\n".encode())
    return hasher.hexdigest()


def identity_from_stdout(path: Path) -> dict[str, Any]:
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("C16_LONG_WATCH_STAGE "):
            try:
                candidate = json.loads(line.removeprefix("C16_LONG_WATCH_STAGE "))
            except json.JSONDecodeError:
                continue
            if isinstance(candidate.get("runtime_identity"), dict):
                return candidate["runtime_identity"]
    raise ContractError("runtime smoke stdout lacks a closed runtime identity")


def observe(raw: Path, ledger_path: Path) -> dict[str, Any]:
    rows = file_index(raw)
    gate_a = (raw / "GATE_A_NVDISASM_VERSION.log").read_text(encoding="utf-8", errors="replace")
    audit = (raw / "ENVIRONMENT_AUDIT_POST_GATE.log").read_text(encoding="utf-8", errors="replace")
    gate_b, gate_c = load(raw / "GATE_B_OFFICIAL_NVBIT_RECEIPT.json"), load(raw / "GATE_C_RUNTIME_FIRST_KERNEL_RECEIPT.json")
    c_stdout = (raw / "GATE_C_RUNTIME_FIRST_KERNEL_STDOUT.log").read_text(encoding="utf-8", errors="replace")
    if "resolved=/usr/local/cuda-12.4/bin/nvdisasm" not in gate_a or "release 12.4" not in gate_a:
        raise ContractError("Gate A did not resolve CUDA 12.4 nvdisasm")
    for marker in ("NVIDIA GeForce RTX 3090", "570.124.04", "/usr/local/cuda-12.4/bin/nvdisasm", "CUDA version:", "CUDA driver version:"):
        if marker not in audit:
            raise ContractError("environment audit lacks required GPU/CUDA/NVBit evidence")
    contract = gate_b.get("nvdisasm_environment_contract")
    if gate_b.get("status") != "NVBIT_OFFICIAL_VECTORADD_SMOKE_PASS" or gate_b.get("runtime_code_commit") != RUNTIME_COMMIT or gate_b.get("tool", {}).get("sha256") != OFFICIAL_TOOL_SHA or not all(gate_b.get("official_instrumentation_evidence", {}).values()):
        raise ContractError("Gate B official instrumentation pass is not closed")
    if not isinstance(contract, dict) or contract.get("NVDISASM") != "nvdisasm" or contract.get("C16_NVBIT_NVDISASM_ABSOLUTE_PATH") != "/usr/local/cuda-12.4/bin/nvdisasm" or not str(contract.get("PATH", "")).startswith("/usr/local/cuda-12.4/bin:"):
        raise ContractError("Gate B lacks fixed harness PATH contract")
    if gate_c.get("mode") != "NVBIT_PATH_SMOKE" or gate_c.get("runtime_code_commit") != RUNTIME_COMMIT or gate_c.get("wall_limit_seconds") != 60 or gate_c.get("terminal_status") != "BOUNDED_TIMEOUT_NO_FIRST_KERNEL":
        raise ContractError("Gate C binding or terminal state differs")
    if gate_c.get("first_cuda_kernel_completed_elapsed_seconds") is not None or gate_c.get("tool_evidence_marker_observed") is not False or gate_c.get("trace_generated") is not False or gate_c.get("raw_trace_bytes") != 0:
        raise ContractError("Gate C overclaims a kernel, marker, or trace")
    if "not found on PATH" in c_stdout or "NVBit (NVidia Binary Instrumentation Tool v1.8) Loaded" not in c_stdout or "FIRST_CUDA_KERNEL_SUBMISSION_BEGIN" not in c_stdout:
        raise ContractError("Gate C did not pass old nvdisasm startup boundary")
    entries = load(ledger_path).get("entries")
    if not isinstance(entries, list):
        raise ContractError("ledger lacks entries")
    matches = [item for item in entries if item.get("operation_kind") in {"NVBIT_OFFICIAL_VECTORADD_SMOKE_DIAGNOSTIC", "NVBIT_PATH_SMOKE_DIAGNOSTIC"}]
    if len(matches) != 2 or {item.get("operation_kind") for item in matches} != {"NVBIT_OFFICIAL_VECTORADD_SMOKE_DIAGNOSTIC", "NVBIT_PATH_SMOKE_DIAGNOSTIC"} or any(item.get("raw_bytes") != 0 or item.get("evidence_classification") != "NON_SCIENTIFIC_DIAGNOSTIC" for item in matches):
        raise ContractError("smoke ledger must retain exactly two non-capture diagnostic rows")
    return {"rows": rows, "tree_sha256": digest(rows), "ledger_sha256": sha256_file(ledger_path), "gate_c": gate_c, "runtime_identity": identity_from_stdout(raw / "GATE_C_RUNTIME_FIRST_KERNEL_STDOUT.log")}


def publication_receipt(index_path: Path, data: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "C16_G_RETRY570_NVDISASM_PATH_REPAIR_CLOSEOUT_V1", "status": STATUS, "scientific_eligible": False,
        "scope": "TOOL_STARTUP_REPAIR_AND_SMOKE_ONLY_NOT_LONG_WATCH_NOT_MODEL_NOT_TRACE_NOT_C_TARGET",
        "path_contract_runtime_source_commit": RUNTIME_COMMIT, "post_run_timeout_normalization_source_commit": NORMALIZATION_COMMIT,
        "root_cause": "CUDA_12_4_NVDISASM_INSTALLED_BUT_ABSENT_FROM_HARNESS_CHILD_PATH",
        "repair": {"absolute_nvdisasm": "/usr/local/cuda-12.4/bin/nvdisasm", "child_path_prefix": "/usr/local/cuda-12.4/bin", "nvbit_command_value": "nvdisasm", "not_a_shell_only_export": True},
        "version_matrix": {"gpu": "NVIDIA GeForce RTX 3090 / SM86", "driver": "570.124.04", "cuda_toolkit": "12.4 (nvcc 12.4.131; nvdisasm 12.4.127)", "torch": data["runtime_identity"], "nvbit": {"version": "1.8", "archive_sha256": "72a2b827f9531dcb86b6be13844f267640fb440929d92944177029da6da2b9e1", "official_instr_count_bb_sha256": OFFICIAL_TOOL_SHA}, "nvbit_documented_requirements": "Linux/x86_64, SM 3.5..12.1, CUDA >=12.0, driver <=575.xx, nvdisasm in PATH"},
        "gates": {"A_nvdisasm_version": "PASS", "B_official_vectoradd_instruction_count": "PASS", "C_lane_g_runtime_first_kernel": "FAIL_TIMEOUT_BEFORE_FIRST_KERNEL_NO_OFFICIAL_KERNEL_MARKER"},
        "c_gate_boundary": {"old_nvdisasm_not_found_on_path_error": "ABSENT", "nvbit_banner": "OBSERVED", "first_cuda_kernel_submission": "OBSERVED", "first_cuda_kernel_completion": "NOT_OBSERVED_WITHIN_60_SECONDS", "official_instrumentation_kernel_marker": "NOT_OBSERVED", "historical_raw_receipt_status": data["gate_c"].get("status"), "normalized_interpretation": "60_SECOND_PATH_SMOKE_TIMEOUT_NOT_A_300_SECOND_STARTUP_DIAGNOSIS"},
        "formal_long_watch_reapplication": "NOT_QUALIFIED", "prohibited_next_steps": ["300s_long_watch", "6_plus_6_window_rerun", "Llama", "Qwen", "C_target", "trace", "scientific_capture"],
        "raw_artifact_index": {"path": str(index_path), "sha256": sha256_file(index_path)}, "terminal_state": "PATH_FAILURE_CLOSED_SEPARATE_PYTORCH_NVBIT_FIRST_KERNEL_GATE_REMAINS_BLOCKED",
    }


def readme() -> str:
    return "\n".join((
        "# Retry570 NVBit nvdisasm path-repair closeout", "", f"Status: `{STATUS}`.", "",
        "`nvdisasm` was installed at `/usr/local/cuda-12.4/bin/nvdisasm`; CUDA was not reinstalled or upgraded. The original child inherited a PATH without that directory. The fixed Lane G contract validates and records the absolute file, prefixes its parent directory into each injected child PATH, and supplies `NVDISASM=nvdisasm`; it is not an interactive-shell-only fix.", "",
        "Gate A resolved/runs nvdisasm 12.4.127. Gate B passed NVBit 1.8 official `instr_count_bb` plus vectoradd, including its banner, instruction-count kernel row, and app terminal result. Gate C used the same exact contract and official tool in Lane G's PyTorch microreproducer. It passed the old PATH error (NVBit banner and first CUDA-work submission observed), but no first CUDA-kernel completion or official kernel marker appeared before 60 seconds.", "",
        "The historical C raw label is retained but normalized only as a 60-second path-smoke timeout, not a 300-second long-watch diagnosis. Thus the startup configuration failure is closed, but the separate PyTorch/NVBit first-kernel gate remains blocked. Formal long-watch reapplication is not qualified. No model, C target, trace, scientific capture, or 6+6 rerun occurred. Raw files are outside Git and locally SHA-closed.", "",
    ))


def manifest(directory: Path) -> dict[str, Any]:
    return {"schema_version": "C16_G_RETRY570_NVDISASM_PATH_REPAIR_PUBLISH_V1", "status": STATUS, "scientific_eligible": False, "files": [{"path": name, "size_bytes": (directory / name).stat().st_size, "sha256": sha256_file(directory / name)} for name in PAYLOADS], "raw_profiler_payloads_committed": False, "remote_only_required_artifact_count": 0}


def validate(directory: Path) -> dict[str, Any]:
    payload, seen = load(directory / MANIFEST), set()
    rows = payload.get("files")
    if payload.get("status") != STATUS or payload.get("scientific_eligible") is not False or not isinstance(rows, list):
        raise ContractError("publication manifest malformed")
    for row in rows:
        if not isinstance(row, dict):
            raise ContractError("publication manifest row malformed")
        name, size, digest_value = row.get("path"), row.get("size_bytes"), row.get("sha256")
        path = directory / name if isinstance(name, str) else directory
        if not isinstance(name, str) or name not in PAYLOADS or name in seen or not isinstance(size, int) or not valid_sha256(digest_value) or not path.is_file() or path.stat().st_size != size or sha256_file(path) != digest_value:
            raise ContractError("publication payload fails existence/size/SHA closure")
        seen.add(name)
    if seen != set(PAYLOADS) or load(directory / RECEIPT).get("formal_long_watch_reapplication") != "NOT_QUALIFIED":
        raise ContractError("publication payload set or readiness verdict invalid")
    return {"schema_version": "C16_G_RETRY570_NVDISASM_PATH_REPAIR_PUBLISH_VALIDATION_V1", "status": "PASS", "publish_manifest": {"path": MANIFEST, "sha256": sha256_file(directory / MANIFEST)}, "checks": {"payload_count": len(rows), "duplicate_path_count": 0, "missing_path_count": 0, "size_or_sha256_failure_count": 0, "manifest_references_only_materialized_payloads": True, "formal_long_watch_reapplication": "NOT_QUALIFIED"}}


def write(directory: Path, raw: Path, ledger: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    data = observe(raw, ledger)
    atomic_json(directory / RAW_INDEX, {"schema_version": "C16_G_RETRY570_NVDISASM_PATH_REPAIR_RAW_INDEX_V1", "status": "LOCAL_HASH_CLOSED_NONSCIENTIFIC_SMOKE_ONLY", "scientific_eligible": False, "local_raw_root": str(raw), "entries": data["rows"], "tree_sha256": data["tree_sha256"], "execution_budget_ledger": {"path": str(ledger), "sha256": data["ledger_sha256"]}, "remote_only_required_artifact_count": 0})
    atomic_json(directory / RECEIPT, publication_receipt(directory / RAW_INDEX, data))
    atomic_json(directory / TRANSFER, {"schema_version": "C16_G_RETRY570_NVDISASM_PATH_REPAIR_TRANSFER_V1", "status": "PASS_REMOTE_TO_LOCAL_CHECKSUM_CLOSURE", "scientific_eligible": False, "remote_raw_root": "/root/autodl-tmp/c16_retry570/raw/nvdisasm_path_repair_20260913", "local_raw_root": str(raw), "rsync_checksum_dry_run": "NO_DIFFERENCES", "local_tree_sha256": data["tree_sha256"], "file_count": len(data["rows"]), "total_bytes": sum(int(item["size_bytes"]) for item in data["rows"]), "remote_only_required_artifact_count": 0, "active_gpu_process_count_at_closeout": 0, "raw_payloads_committed": False})
    (directory / README).write_text(readme(), encoding="utf-8")
    atomic_json(directory / MANIFEST, manifest(directory))
    atomic_json(directory / VALIDATION, validate(directory))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--raw-root", type=Path, required=True)
    parser.add_argument("--ledger", type=Path, required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--validate", action="store_true")
    args = parser.parse_args()
    if args.write:
        write(args.directory, args.raw_root, args.ledger)
        print(f"PASS Retry570 nvdisasm path-repair closeout write: {args.directory}")
    else:
        print("PASS Retry570 nvdisasm path-repair closeout validation: " + canonical_json(validate(args.directory)["checks"]))


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        raise SystemExit(f"FAIL Retry570 nvdisasm path-repair closeout: {exc}")
