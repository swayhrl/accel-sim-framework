#!/usr/bin/env python3
"""Publish the bounded Retry570 RAW/EMPTY callback-causality diagnostic."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json, canonical_json, sha256_file, valid_sha256

SCHEMA = "C16_G_RETRY570_CALLBACK_BOOKKEEPING_CLOSEOUT_V1"
STATUS = "NVBIT_CORE_MODULE_BOOKKEEPING_PATHOLOGY_CONFIRMED"
RUNTIME_COMMIT = "e27ce12addcea5b9da27b4fa02f0f6e6a462be09"
HANDOFF_COMMIT = "43c50becb8b3bc41673f77f5674bf15308954440"
RAW_NAME = "module_firstuse_P1_true_raw_lazy_e27ce12a"
EMPTY_NAME = "module_firstuse_P2_empty_callback_lazy_e27ce12a"
REPORT = "NVBIT_CALLBACK_BOOKKEEPING_ROOT_CAUSE_REPORT.md"
MATRIX = "NVBIT_CALLBACK_BOOKKEEPING_DECISION_MATRIX.tsv"
RECEIPT = "NVBIT_CALLBACK_BOOKKEEPING_ROOT_CAUSE_RECEIPT.json"
RAW_INDEX = "RAW_ARTIFACT_INDEX.json"
TRANSFER = "NVBIT_CALLBACK_BOOKKEEPING_TRANSFER_RECEIPT.json"
MANIFEST = "PUBLISH_MANIFEST.json"
VALIDATION = "PUBLISH_VALIDATION_RECEIPT.json"
PAYLOADS = (REPORT, MATRIX, RECEIPT, RAW_INDEX, TRANSFER)


def load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot load JSON object: {path}") from exc
    if not isinstance(value, dict):
        raise ContractError(f"JSON object required: {path}")
    return value


def listed_files(root: Path) -> list[dict[str, Any]]:
    return [{"relative_path": path.relative_to(root).as_posix(), "size_bytes": path.stat().st_size,
             "sha256": sha256_file(path)} for path in sorted(root.rglob("*")) if path.is_file()]


def stack_contains(root: Path, *symbols: str) -> bool:
    for path in sorted((root / "snapshots").glob("*.json")):
        output = load(path).get("native_backtrace", {}).get("output", "")
        if all(symbol in output for symbol in symbols):
            return True
    return False


def observe_attempt(root: Path, mode: str, tool_sha: str) -> dict[str, Any]:
    receipt = load(root / "receipt.json")
    analysis = load(root / "analysis.json")
    transaction = load(root / "remote_transaction.json")
    if (receipt.get("runtime_code_commit") != RUNTIME_COMMIT or receipt.get("mode") != mode or
            receipt.get("terminal_status") != "BOUNDED_TIMEOUT" or receipt.get("scientific_eligible") is not False or
            receipt.get("trace_generated") is not False or receipt.get("raw_trace_bytes") != 0 or
            receipt.get("target_hard_budget_s") != 25 or receipt.get("tool", {}).get("sha256") != tool_sha):
        raise ContractError(f"bounded {mode} attempt contract differs: {root}")
    if receipt.get("target_group_cleanup") != {"grace_seconds": 2, "kill_sent": False, "required": True, "term_sent": True}:
        raise ContractError(f"external target-group cleanup receipt differs: {root}")
    if transaction.get("remote_transaction_cap_s") != 32 or not isinstance(transaction.get("remote_transaction_wall_s"), (int, float)) or transaction["remote_transaction_wall_s"] > 32:
        raise ContractError(f"remote transaction bound differs: {root}")
    events = {row.get("event") for row in analysis.get("app_events", []) if isinstance(row, dict)}
    if "EXACT_TARGET_SUBMISSION_BEGIN" not in events or "EXACT_OPERATION_RETURN" in events:
        raise ContractError(f"exact submission/return boundary differs: {root}")
    if len(list((root / "snapshots").glob("*.json"))) != 3:
        raise ContractError(f"expected three bounded snapshots: {root}")
    return {"root": root, "receipt": receipt, "analysis": analysis, "transaction": transaction, "files": listed_files(root)}


def observe(raw_base: Path, raw_local_wall: float, empty_local_wall: float) -> dict[str, Any]:
    raw = observe_attempt(raw_base / RAW_NAME, "NVBIT_CALLBACK_CENSUS_RAW", "ac81952450a60121e15e76883d09f1fafb4764c06393f10e06e529e606168e19")
    empty = observe_attempt(raw_base / EMPTY_NAME, "NVBIT_EMPTY_CALLBACK_TOOL", "6a255fad202548af45b446597c8a3a9052907b199f3c38a90b5e0b87c3fe0823")
    decoded = load(raw["root"] / "raw_decode.json")
    if (decoded.get("write_count") != 196 or decoded.get("dropped_count") != 0 or decoded.get("max_callback_depth") != 1 or
            decoded.get("reentrant_callback_count") != 0 or decoded.get("last_event", [None] * 5)[3:] != [682, 0]):
        raise ContractError("RAW callback does not prove fixed-POD collection through cuLibraryGetModule entry")
    if not stack_contains(raw["root"], "Nvbit::module_loaded", "nvbitToolsCallbackFunc"):
        raise ContractError("RAW stack lacks the NVBit module-loaded path")
    if not stack_contains(empty["root"], "std::_Hash_bytes", "Nvbit::module_loaded", "nvbitToolsCallbackFunc"):
        raise ContractError("EMPTY stack lacks the decisive NVBit hash/module-loaded path")
    if raw_local_wall > 40 or empty_local_wall > 40:
        raise ContractError("local SSH transaction exceeded its declared 40-second cap")
    return {"raw": raw, "empty": empty, "decoded": decoded, "raw_local_wall": raw_local_wall, "empty_local_wall": empty_local_wall}


def raw_index(data: dict[str, Any], raw_base: Path) -> dict[str, Any]:
    return {"schema_version": "C16_G_RETRY570_CALLBACK_BOOKKEEPING_RAW_INDEX_V1", "status": "LOCAL_HASH_CLOSED_NONSCIENTIFIC_DIAGNOSTIC_ONLY",
            "scientific_eligible": False, "local_raw_base": str(raw_base), "attempts": [
                {"attempt": "TRUE_RAW_CALLBACK_CENSUS", "remote_raw_root": "/root/autodl-tmp/c16_retry570/raw/" + RAW_NAME,
                 "local_raw_root": str(data["raw"]["root"]), "entries": data["raw"]["files"]},
                {"attempt": "EMPTY_CALLBACK", "remote_raw_root": "/root/autodl-tmp/c16_retry570/raw/" + EMPTY_NAME,
                 "local_raw_root": str(data["empty"]["root"]), "entries": data["empty"]["files"]}],
            "remote_only_required_artifact_count": 0, "raw_payloads_committed": False}


def matrix(data: dict[str, Any]) -> str:
    raw, empty = data["raw"], data["empty"]
    return ("control\tstatus\thot_stack\towner\ttarget_wall_s\tremote_transaction_wall_s\tlocal_ssh_wall_s\tscientific_eligible\n"
            "OLD_CALLBACK_CENSUS\tHANG\tNvbit::module_loaded->elfModuleHashMap::operator[]\tUNRESOLVED_BEFORE_CONTROLS\tHISTORICAL\tHISTORICAL\tHISTORICAL\tFALSE\n"
            "TRUE_RAW_CALLBACK_CENSUS\tHANG\tNvbit::module_loaded->vendor_core\tNOT_OUR_RAW_CALLBACK\t"
            f"{raw['receipt']['target_wall_s']:.6f}\t{raw['transaction']['remote_transaction_wall_s']:.6f}\t{data['raw_local_wall']:.6f}\tFALSE\n"
            "EMPTY_CALLBACK\tHANG\tstd::_Hash_bytes->elfModuleHashMap::operator[]->Nvbit::module_loaded\tNVBIT_CORE\t"
            f"{empty['receipt']['target_wall_s']:.6f}\t{empty['transaction']['remote_transaction_wall_s']:.6f}\t{data['empty_local_wall']:.6f}\tFALSE\n")


def closeout_receipt(data: dict[str, Any], raw_index_path: Path) -> dict[str, Any]:
    raw, empty = data["raw"], data["empty"]
    return {"schema_version": SCHEMA, "status": STATUS, "scientific_eligible": False,
            "scope": "EXACT_PYTORCH_INDEXSELECT_CALLBACK_CAUSALITY_ONLY_NOT_MODEL_NOT_TRACE_NOT_C_TARGET_NOT_SCIENTIFIC_CAPTURE_NOT_TIMING",
            "diagnostic_handoff_commit": HANDOFF_COMMIT, "runtime_source_commit": RUNTIME_COMMIT,
            "environment": {"gpu": "RTX3090/SM86", "driver": "570.124.04", "torch": "2.5.1+cu124", "cuda": "12.4", "nvbit": "1.8",
                            "nvbit_core_archive_sha256": "db221829106673bcd69d1e05766136f80e2df4497fb8415d8c2f298b96c302f7"},
            "decision": {"old_callback_census": "HANG", "true_raw_callback_census": "HANG", "empty_callback": "HANG",
                         "reproducing_hot_stack": "std::_Hash_bytes -> elfModuleHashMap::operator[] -> Nvbit::module_loaded -> nvbitToolsCallbackFunc",
                         "ownership": "NVBIT_1_8_PRECOMPILED_CORE_NOT_OUR_RAW_CALLBACK_NOT_LANE_G_TARGETED_MEMORY_TOOL", "classification": STATUS,
                         "one_time_or_repeated": "NOT_DETERMINED_WITHIN_25_SECOND_TARGET_BUDGET", "measurement_active_prewarm_ready": False},
            "raw_callback_contract": {"fixed_preallocated_pod_only": True, "write_count": data["decoded"]["write_count"], "dropped_count": data["decoded"]["dropped_count"],
                                      "max_callback_depth": data["decoded"]["max_callback_depth"], "reentrant_callback_count": data["decoded"]["reentrant_callback_count"],
                                      "callback_names_decoded_offline": True, "last_callback": "cuLibraryGetModule ENTRY"},
            "vendor_provenance": {"archive_member_module_loaded": "core/libnvbit.a:nvbit_imp.o", "archive_member_map": "core/libnvbit.a:tools_shared_readelf_caches.o",
                                  "embedded_source_name_only": "nvbit.cpp", "vendor_dwarf": "NOT_DISTRIBUTED_NO_SOURCE_LINE_CLAIM"},
            "wall_contract": {"target_hard_budget_s": 25, "remote_transaction_cap_s": 32, "local_ssh_cap_s": 40,
                              "true_raw": {"target_wall_s": raw["receipt"]["target_wall_s"], "remote_transaction_wall_s": raw["transaction"]["remote_transaction_wall_s"], "local_ssh_wall_s": data["raw_local_wall"], "cleanup": raw["receipt"]["target_group_cleanup"]},
                              "empty": {"target_wall_s": empty["receipt"]["target_wall_s"], "remote_transaction_wall_s": empty["transaction"]["remote_transaction_wall_s"], "local_ssh_wall_s": data["empty_local_wall"], "cleanup": empty["receipt"]["target_group_cleanup"]}},
            "raw_artifact_index": {"path": RAW_INDEX, "sha256": sha256_file(raw_index_path)}, "remote_only_required_artifact_count": 0,
            "active_gpu_process_count_at_closeout": 0,
            "forbidden_without_new_authorization": ["model", "Llama", "Qwen", "C_target", "trace", "scientific_capture", "300s_long_watch", "historical_6_plus_6_rerun"],
            "terminal_state": "CORE_PATH_CONFIRMED_BUT_ONE_TIME_VS_REPEATED_NOT_YET_ESTABLISHED"}


def report(data: dict[str, Any]) -> str:
    raw, empty = data["raw"], data["empty"]
    lines = ["# Retry570 NVBit callback-bookkeeping root cause\n", f"Status: `{STATUS}`.\n",
             "This publication ran only the exact diagnostic `torch.index_select` reproducer. No model/Llama/Qwen, trace, C target, scientific capture, timing result, 300-second watch, or historical 6+6 window ran.\n",
             "The decisive table is `old census = HANG`, `TRUE RAW = HANG`, and `EMPTY = HANG`. TRUE RAW records only preallocated POD events: 196 entries, zero drops, maximum callback depth 1, zero reentrancy, and final retained event `cuLibraryGetModule` entry. Callback names were decoded after process exit.\n",
             "EMPTY contains only `nvbit_at_cuda_event(...) { return; }`. Its 5-second GDB snapshot is `std::_Hash_bytes -> elfModuleHashMap::operator[] -> Nvbit::module_loaded -> nvbitToolsCallbackFunc` in injected NVBit 1.8 core. The hot path is neither the RAW recorder nor Lane G's targeted memory tool.\n",
             "Vendor provenance: `core/libnvbit.a` SHA256 `db221829106673bcd69d1e05766136f80e2df4497fb8415d8c2f298b96c302f7`; `Nvbit::module_loaded` is `nvbit_imp.o`, and `elfModuleHashMap` is `tools_shared_readelf_caches.o`. The vendor archive exposes only embedded name `nvbit.cpp`, not DWARF source lines; this report makes no FILE:LINE or private-STL-layout claim.\n",
             f"TRUE RAW wall accounting: target {raw['receipt']['target_wall_s']:.6f}s; remote transaction {raw['transaction']['remote_transaction_wall_s']:.6f}s; local SSH {data['raw_local_wall']:.6f}s. EMPTY: target {empty['receipt']['target_wall_s']:.6f}s; remote transaction {empty['transaction']['remote_transaction_wall_s']:.6f}s; local SSH {data['empty_local_wall']:.6f}s. Each child process group received TERM at 25s and exited during 2s grace; no KILL was needed.\n",
             "One-time versus repeated is not determined within this 25-second authorization: the exact first use never returned, while historical EAGER callback-only shifted work before exact marker and also did not complete under short cap. EAGER/prewarm is therefore not ready before `MEASUREMENT_ACTIVE`; a separately authorized bounded finite-completion characterization is required.\n"]
    return "\n".join(lines)


def manifest(directory: Path) -> dict[str, Any]:
    return {"schema_version": "C16_G_RETRY570_CALLBACK_BOOKKEEPING_PUBLISH_V1", "status": STATUS, "scientific_eligible": False, "runtime_source_commit": RUNTIME_COMMIT,
            "files": [{"path": item, "size_bytes": (directory / item).stat().st_size, "sha256": sha256_file(directory / item)} for item in PAYLOADS],
            "raw_profiler_payloads_committed": False, "remote_only_required_artifact_count": 0}


def validate(directory: Path) -> dict[str, Any]:
    publication, seen = load(directory / MANIFEST), set()
    rows = publication.get("files")
    if publication.get("status") != STATUS or publication.get("scientific_eligible") is not False or not isinstance(rows, list):
        raise ContractError("callback-bookkeeping manifest header differs")
    for row in rows:
        path = row.get("path") if isinstance(row, dict) else None
        if path not in PAYLOADS or path in seen or not isinstance(row.get("size_bytes"), int) or not valid_sha256(row.get("sha256")):
            raise ContractError("callback-bookkeeping manifest row differs or duplicates")
        payload = directory / path
        if not payload.is_file() or payload.stat().st_size != row["size_bytes"] or sha256_file(payload) != row["sha256"]:
            raise ContractError(f"manifest payload fails existence/size/SHA closure: {path}")
        seen.add(path)
    if seen != set(PAYLOADS) or load(directory / RECEIPT).get("status") != STATUS:
        raise ContractError("callback-bookkeeping payload set is incomplete")
    return {"schema_version": "C16_G_RETRY570_CALLBACK_BOOKKEEPING_PUBLISH_VALIDATION_V1", "status": "PASS", "publish_manifest": {"path": MANIFEST, "sha256": sha256_file(directory / MANIFEST)},
            "checks": {"payload_count": len(rows), "duplicate_path_count": 0, "missing_path_count": 0, "size_or_sha256_failure_count": 0,
                       "manifest_references_only_materialized_payloads": True, "scientific_eligible": False}}


def write(directory: Path, raw_base: Path, raw_local_wall: float, empty_local_wall: float) -> None:
    data = observe(raw_base, raw_local_wall, empty_local_wall)
    directory.mkdir(parents=True, exist_ok=True)
    atomic_json(directory / RAW_INDEX, raw_index(data, raw_base))
    atomic_json(directory / RECEIPT, closeout_receipt(data, directory / RAW_INDEX))
    atomic_json(directory / TRANSFER, {"schema_version": "C16_G_RETRY570_CALLBACK_BOOKKEEPING_TRANSFER_V1", "status": "PASS_REMOTE_TO_LOCAL_SHA256_CLOSURE", "scientific_eligible": False,
                                        "raw_artifact_index": {"path": RAW_INDEX, "sha256": sha256_file(directory / RAW_INDEX)}, "remote_only_required_artifact_count": 0,
                                        "active_gpu_process_count_at_closeout": 0, "raw_payloads_committed": False})
    (directory / MATRIX).write_text(matrix(data), encoding="utf-8")
    (directory / REPORT).write_text(report(data), encoding="utf-8")
    atomic_json(directory / MANIFEST, manifest(directory))
    atomic_json(directory / VALIDATION, validate(directory))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--raw-base", type=Path, required=True)
    parser.add_argument("--raw-local-ssh-wall-s", type=float, required=True)
    parser.add_argument("--empty-local-ssh-wall-s", type=float, required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--validate", action="store_true")
    args = parser.parse_args()
    if args.write:
        write(args.directory, args.raw_base, args.raw_local_ssh_wall_s, args.empty_local_ssh_wall_s)
        print(f"PASS Retry570 callback-bookkeeping closeout write: {args.directory}")
    else:
        print("PASS Retry570 callback-bookkeeping closeout validation: " + canonical_json(validate(args.directory)["checks"]))


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        raise SystemExit(f"FAIL Retry570 callback-bookkeeping closeout: {exc}")
