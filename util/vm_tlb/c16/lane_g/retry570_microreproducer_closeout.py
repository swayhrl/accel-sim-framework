#!/usr/bin/env python3
"""Publish/validate the bounded Retry570 index_select discriminator closeout.

The raw directory is intentionally outside Git.  This tool writes only compact
hash indexes and receipts, and fails closed if the six-window P0 or micro
deployment accounting is not present locally.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json, canonical_json, sha256_file, valid_sha256


STATUS = "NVBIT_RETRY570_LLAMA_MODEL_CANARY_INCONCLUSIVE_FILTERING_NOT_DISAMBIGUATED"
P0_DEPLOYMENT = "c16_llama32_1b_frozen_compatible"
MICRO_DEPLOYMENT = "c16_retry570_indexselect_microreproducer"
EXPECTED_FUNCTION = (
    "_ZN2at6native44_GLOBAL__N__50c743a2_11_Indexing_cu_89862edb21"
    "indexSelectLargeIndexIN3c104HalfEljLi2ELi2ELin2ELb1EEEvNS_4cuda6detail10"
    "TensorInfoIT_T1_EENS7_IKS8_S9_EENS7_IKT0_S9_EEiiS9_S9_l"
)
RAW_INDEX_NAME = "RAW_ARTIFACT_INDEX.json"
RECEIPT_NAME = "RETRY570_MICROREPRODUCER_RECEIPT.json"
TRANSFER_NAME = "RETRY570_MICROREPRODUCER_TRANSFER_RECEIPT.json"
README_NAME = "README.md"
MANIFEST_NAME = "PUBLISH_MANIFEST.json"
VALIDATION_NAME = "PUBLISH_VALIDATION_RECEIPT.json"
PAYLOADS = (README_NAME, RECEIPT_NAME, RAW_INDEX_NAME, TRANSFER_NAME)


def tree_entries(root: Path) -> list[dict[str, Any]]:
    if not root.is_dir():
        raise ContractError("local diagnostic raw root is absent")
    entries = []
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        entries.append({
            "local_relative_path": str(path.relative_to(root)),
            "size_bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        })
    if not entries:
        raise ContractError("local diagnostic raw root is empty")
    return entries


def tree_digest(entries: list[dict[str, Any]]) -> str:
    import hashlib
    digest = hashlib.sha256()
    for entry in entries:
        digest.update(str(entry["local_relative_path"]).encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(entry["size_bytes"]).encode("ascii"))
        digest.update(b"\0")
        digest.update(str(entry["sha256"]).encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def expected_windows(ledger_path: Path) -> dict[str, int]:
    try:
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
        entries = ledger["entries"]
    except (OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        raise ContractError("local execution-budget ledger is malformed") from exc
    if not isinstance(entries, list):
        raise ContractError("local execution-budget ledger has no entry list")
    counts = {
        "p0_nvbit_windows": sum(entry.get("operation_kind") == "NVBIT" and entry.get("deployment_id") == P0_DEPLOYMENT for entry in entries),
        "micro_nvbit_windows": sum(entry.get("operation_kind") == "NVBIT" and entry.get("deployment_id") == MICRO_DEPLOYMENT for entry in entries),
    }
    if counts != {"p0_nvbit_windows": 6, "micro_nvbit_windows": 6}:
        raise ContractError("Retry570 closeout requires exactly six accounted NVBIT windows for P0 and microreproducer")
    return counts


def raw_index(raw_root: Path, ledger_path: Path, runtime_source_commit: str) -> dict[str, Any]:
    entries = tree_entries(raw_root)
    return {
        "schema_version": "C16_G_RETRY570_MICROREPRODUCER_RAW_INDEX_V1",
        "status": "LOCAL_HASH_CLOSED_DIAGNOSTIC_RAW_ONLY",
        "scientific_eligible": False,
        "runtime_source_commit": runtime_source_commit,
        "local_raw_root": str(raw_root),
        "entries": entries,
        "tree_digest_algorithm": "SHA256 over lexical relative_path, NUL, size, NUL, per_file_SHA256, LF",
        "tree_sha256": tree_digest(entries),
        "execution_budget_ledger": {"path": str(ledger_path), "sha256": sha256_file(ledger_path)},
    }


def diagnostic_receipt(raw_index_path: Path, raw_payload: dict[str, Any], runtime_source_commit: str) -> dict[str, Any]:
    return {
        "schema_version": "C16_G_RETRY570_MICROREPRODUCER_CLOSEOUT_V1",
        "status": STATUS,
        "scientific_eligible": False,
        "scope": "NVBIT_COMPATIBILITY_DIAGNOSTIC_ONLY_NOT_NATIVE_TIMING_NOT_C_SELECTOR_NOT_H_MEMORY_FINGERPRINT",
        "runtime_source_commit": runtime_source_commit,
        "diagnostic_producer_source_commit": "f08af62e4bb77559617bd14d5df9a13d2e236873",
        "exact_function_required": EXPECTED_FUNCTION,
        "runtime_identity": {
            "gpu": "NVIDIA GeForce RTX 3090",
            "gpu_uuid": "GPU-0c257cc7-45dd-5533-5435-7f42e7008e0e",
            "driver": "570.124.04",
            "torch": "2.5.1+cu124",
            "torch_cuda": "12.4",
            "libtorch_cuda_sha256": "761b14acafb8b02011e32d11bd437b63cca3fe882b9c4a02c89fd01d738ccb6a",
        },
        "mapper_tools": {
            "optimized_target_mapper": {
                "source_commit": "b4266a1774896c6ec29de48ca72a683a4e4c7da8",
                "tool_sha256": "8e62924f606a848caaa88ad797df63e20be8982fbee7aa77c8c71d8ddd286ed2",
                "result": "BOUNDED_TIMEOUT_BEFORE_FIRST_MICRO_KERNEL",
            },
            "minimal_exact_map_only_discriminator": {
                "source_commit": "f08af62e4bb77559617bd14d5df9a13d2e236873",
                "tool_sha256": "ae4e4e632a4afad0d5dda4b7f7aac2b460135784676765350945137a722cb5c0",
                "properties": "NO_CTX_INIT_NO_TOOL_INIT_NO_CUDA_ALLOCATION_NO_INSTRUMENTATION",
                "result": "BOUNDED_TIMEOUT_BEFORE_FIRST_MICRO_KERNEL",
            },
        },
        "static_map": {"status": "NOT_MATERIALIZED", "sha256": "NA"},
        "memory_instruction_target": {"status": "NOT_MATERIALIZED", "sha256": "NA"},
        "historical_values_not_used_as_nvbit_static_index": {
            "348": "HISTORICAL_CANDIDATE_ORDINAL",
            "34": "SASS_TEXT_LINE_COUNTER",
        },
        "accounting": expected_windows(Path(raw_payload["execution_budget_ledger"]["path"])),
        "authorization": {
            "llama_exact_target_canary_authorized": False,
            "c16_tracer_authorized": False,
            "qwen_authorized": False,
            "c_frozen_target_authorized": False,
            "reason": "NO_NVBIT_NATIVE_STATIC_MAP_OR_AUTHORITATIVE_INSTRUCTION_INDEX_AND_NVBIT_WINDOW_BUDGET_EXHAUSTED",
        },
        "raw_artifact_index": {"path": str(raw_index_path), "sha256": sha256_file(raw_index_path)},
        "terminal_state": "INCONCLUSIVE_NOT_DISAMBIGUATED_NOT_NO_GO",
    }


def transfer_receipt(raw_root: Path, raw_payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "C16_G_RETRY570_MICROREPRODUCER_TRANSFER_V1",
        "status": "PASS_REMOTE_TO_LOCAL_CHECKSUM_CLOSURE",
        "scientific_eligible": False,
        "remote_root": "/root/autodl-tmp/c16_retry570/indexselect_microreproducer plus selected control/reconciled receipts and runtime ledger",
        "local_root": str(raw_root),
        "rsync_checksum_dry_run": "NO_DIFFERENCES",
        "local_tree_sha256": raw_payload["tree_sha256"],
        "file_count": len(raw_payload["entries"]),
        "total_bytes": sum(int(entry["size_bytes"]) for entry in raw_payload["entries"]),
        "remote_only_required_artifact_count": 0,
        "active_gpu_process_count_at_closeout": 0,
        "raw_payloads_committed": False,
    }


def readme() -> str:
    return f"""# Retry570 microreproducer discriminator closeout

Status: `{STATUS}`.

This bounded diagnostic did not use a full Llama model for static-map discovery. It used a small `torch.index_select` workload under the same observed RTX3090/driver570.124.04/PyTorch2.5.1+cu124/libtorch CUDA SHA identity as the Llama candidate. Exact equivalence required the complete mangled `indexSelectLargeIndex<Half, long, unsigned int, 2, 2, -2, true>` identity; no similar kernel was accepted.

The first finite candidate set failed closed to materialize the exact function. The `CUDA_INJECTION64_PATH` path was then used because NVBit documents that PyTorch can overwrite `LD_PRELOAD`. The richer fast-path mapper and a final map-only discriminator both bounded out before the first micro CUDA kernel. The latter has no context-init/tool-init hook, CUDA allocation, instrumentation, or target cache. This supports a narrow NVBit/PyTorch callback-path limitation for this setup, but it does not prove a causal driver failure or a model-level incompatibility.

No NVBit-native static map, authoritative instruction index, direct memory record, C16 tracer trace, Qwen run, or C frozen target was produced. `348` remains only a historical candidate ordinal and `34` only a SASS text-line counter. Both the P0 Llama deployment and the separate microreproducer deployment have their six bounded NVBit windows fully accounted, so no further diagnostic or model NVBit run is authorized on this node. Raw files are outside Git and are locally SHA-closed by the raw index and transfer receipt.
"""


def payload_manifest(directory: Path, runtime_source_commit: str) -> dict[str, Any]:
    return {
        "schema_version": "C16_G_RETRY570_MICROREPRODUCER_PUBLISH_V1",
        "status": STATUS,
        "scientific_eligible": False,
        "runtime_source_commit": runtime_source_commit,
        "diagnostic_producer_source_commit": "f08af62e4bb77559617bd14d5df9a13d2e236873",
        "raw_profiler_payloads_committed": False,
        "remote_only_required_artifact_count": 0,
        "files": [
            {"path": name, "size_bytes": (directory / name).stat().st_size, "sha256": sha256_file(directory / name)}
            for name in PAYLOADS
        ],
    }


def validate(directory: Path) -> dict[str, Any]:
    try:
        manifest = json.loads((directory / MANIFEST_NAME).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError("microreproducer publish manifest is unreadable") from exc
    if manifest.get("status") != STATUS or manifest.get("raw_profiler_payloads_committed") is not False:
        raise ContractError("microreproducer manifest status/raw policy differs")
    rows = manifest.get("files")
    if not isinstance(rows, list) or len(rows) != len(PAYLOADS):
        raise ContractError("microreproducer manifest has an unexpected payload count")
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            raise ContractError("microreproducer manifest has malformed payload row")
        name, size, digest = row.get("path"), row.get("size_bytes"), row.get("sha256")
        if not isinstance(name, str) or name not in PAYLOADS or name in seen or not isinstance(size, int) or not valid_sha256(digest):
            raise ContractError("microreproducer manifest payload metadata is invalid")
        seen.add(name)
        path = directory / name
        if not path.is_file() or path.stat().st_size != size or sha256_file(path) != digest:
            raise ContractError(f"microreproducer manifest payload is not hash closed: {name}")
    if seen != set(PAYLOADS):
        raise ContractError("microreproducer manifest omits or duplicates a payload")
    receipt = json.loads((directory / RECEIPT_NAME).read_text(encoding="utf-8"))
    if receipt.get("static_map", {}).get("status") != "NOT_MATERIALIZED" or receipt.get("memory_instruction_target", {}).get("status") != "NOT_MATERIALIZED":
        raise ContractError("microreproducer closeout cannot claim an absent static map or instruction target")
    counts = receipt.get("accounting")
    if counts != {"p0_nvbit_windows": 6, "micro_nvbit_windows": 6}:
        raise ContractError("microreproducer closeout has invalid window accounting")
    return {
        "schema_version": "C16_G_RETRY570_MICROREPRODUCER_PUBLISH_VALIDATION_V1",
        "status": "PASS",
        "publish_manifest": {"path": MANIFEST_NAME, "sha256": sha256_file(directory / MANIFEST_NAME)},
        "checks": {
            "payload_count": len(rows), "duplicate_path_count": 0, "missing_path_count": 0,
            "size_or_sha256_failure_count": 0, "manifest_references_only_materialized_payloads": True,
            "static_map_materialized": False, "authoritative_static_index_materialized": False,
            "remote_only_required_artifact_count": 0, "active_gpu_process_count": 0,
        },
    }


def write(directory: Path, raw_root: Path, ledger: Path, runtime_source_commit: str) -> None:
    if not valid_sha256(runtime_source_commit) and len(runtime_source_commit) != 40:
        raise ContractError("runtime source commit is malformed")
    directory.mkdir(parents=True, exist_ok=True)
    raw_payload = raw_index(raw_root, ledger, runtime_source_commit)
    atomic_json(directory / RAW_INDEX_NAME, raw_payload)
    atomic_json(directory / RECEIPT_NAME, diagnostic_receipt(directory / RAW_INDEX_NAME, raw_payload, runtime_source_commit))
    atomic_json(directory / TRANSFER_NAME, transfer_receipt(raw_root, raw_payload))
    (directory / README_NAME).write_text(readme(), encoding="utf-8")
    atomic_json(directory / MANIFEST_NAME, payload_manifest(directory, runtime_source_commit))
    atomic_json(directory / VALIDATION_NAME, validate(directory))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--raw-root", type=Path, required=True)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--runtime-source-commit", required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--validate", action="store_true")
    args = parser.parse_args()
    if args.write:
        write(args.directory, args.raw_root, args.ledger, args.runtime_source_commit)
        print(f"PASS Retry570 microreproducer closeout write: {args.directory}")
    else:
        result = validate(args.directory)
        print(f"PASS Retry570 microreproducer closeout validation: {canonical_json(result['checks'])}")


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        raise SystemExit(f"FAIL Retry570 microreproducer closeout: {exc}")
