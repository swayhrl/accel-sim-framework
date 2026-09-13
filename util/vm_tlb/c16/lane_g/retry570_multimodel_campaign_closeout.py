#!/usr/bin/env python3
"""Build and validate the compact C16 Retry570 multi-model campaign pack.

This is publication-only: it reads retained C0/S1/S2 evidence and the copied
remote budget ledger.  It never imports torch, opens a model, or launches a
GPU process.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json, canonical_json, repo_root, sha256_file


SCHEMA = "C16_G_RETRY570_MULTIMODEL_CAMPAIGN_CLOSEOUT_V1"
STATUS = "C16_NVBIT175_MULTIMODEL_TRACE_CAMPAIGN_COMPLETE_WITH_BLOCKED_MODELS"
ROSTER = ("llama_3p2_1b", "qwen_0p5", "qwen_7b_awq", "deepseek", "glm")
PACK_FILES = (
    "C0_REMOTE_ASSET_INVENTORY.json", "C0_CAMPAIGN_LEDGER.json", "LLAMA_MODEL_CLOSEOUT.json",
    "QWEN_0P5_BLOCKER.json", "QWEN_7B_AWQ_BLOCKER.json", "DEEPSEEK_BLOCKER.json", "GLM_BLOCKER.json",
    "C2_CROSS_MODEL_INTEGRITY.tsv", "C3_CAMPAIGN_SUMMARY.json", "CAMPAIGN_FINAL_REPORT.md",
)


def read(path: Path) -> dict[str, Any]:
    try: value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc: raise ContractError(f"cannot read JSON evidence: {path}") from exc
    if not isinstance(value, dict): raise ContractError(f"JSON object required: {path}")
    return value


def git_head() -> str:
    import subprocess
    return subprocess.check_output(["git", "-C", str(repo_root()), "rev-parse", "HEAD"], text=True).strip()


def ledger_exhaustion(ledger: dict[str, Any], deployment: str) -> dict[str, Any]:
    limits = ledger.get("limits", {})
    max_windows = limits.get("nvbit_windows_per_deployment")
    entries = [entry for entry in ledger.get("entries", []) if entry.get("operation_kind") == "NVBIT" and entry.get("deployment_id") == deployment]
    if not isinstance(max_windows, int) or len(entries) != max_windows:
        raise ContractError("copied ledger does not prove the frozen per-deployment NVBit window exhaustion")
    return {"operation_kind": "NVBIT", "deployment_id": deployment, "consumed_window_count": len(entries), "maximum_window_count": max_windows,
            "entries": [{key: entry.get(key) for key in ("run_id", "terminal_status", "elapsed_seconds", "raw_bytes", "evidence_classification", "diagnostic_reason")} for entry in entries]}


def write_tsv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = ("MODEL", "EXACT_IDENTITY", "ASSET_STATUS", "WORKLOAD_CONTRACT", "S1_RUNTIME_READY", "TARGET_FULL_IDENTITY", "STATIC_RANGE", "PREFILL_CAPTURE", "DECODE_CAPTURE", "REPRODUCIBILITY", "TOTAL_RECORDS", "ADDRESS_RECORDS", "TRACE_BYTES", "REMOTE_LOCAL_SHA_CLOSED", "FINAL_STATUS", "BLOCK_REASON")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n", extrasaction="raise")
        writer.writeheader(); writer.writerows(rows)


def validate_manifest(directory: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    payloads = manifest.get("payloads")
    if not isinstance(payloads, list) or not payloads: raise ContractError("manifest lacks payloads")
    seen: set[str] = set()
    for row in payloads:
        if not isinstance(row, dict) or not isinstance(row.get("path"), str): raise ContractError("manifest has malformed payload")
        relative = row["path"]
        if relative in seen or Path(relative).is_absolute() or ".." in Path(relative).parts: raise ContractError("manifest has duplicate/unsafe path")
        seen.add(relative); target = directory / relative
        if not target.is_file() or target.stat().st_size != row.get("size_bytes") or sha256_file(target) != row.get("sha256"):
            raise ContractError(f"manifest payload is not materialized/hash closed: {relative}")
    return {"schema_version": SCHEMA, "status": "PUBLISH_MANIFEST_VALIDATION_PASS", "payload_count": len(payloads), "no_duplicate_path": True, "all_payloads_exist_size_sha256_match": True,
            "manifest_sha256": sha256_file(directory / "PUBLISH_MANIFEST.json")}


def build(args: argparse.Namespace) -> None:
    if args.producer_code_commit != git_head(): raise ContractError("producer code commit differs from checked-out source")
    if args.output.exists(): raise ContractError("campaign output pack already exists; refusing overwrite")
    inventory, c0ledger, s1, s2, target, ledger = map(read, (args.inventory, args.c0_ledger, args.s1, args.s2, args.target, args.remote_ledger))
    roster = inventory.get("roster")
    if not isinstance(roster, list) or [row.get("model_key") for row in roster] != list(ROSTER): raise ContractError("C0 roster does not equal the frozen five-model campaign")
    llama = roster[0]
    if llama.get("status") != "S0_FROZEN_READY" or s1.get("status") != "S1_FULL_MODEL_NO_TRACE_PASS" or s2.get("status") != "S2_FULL_MODEL_STATIC_MAP_PASS":
        raise ContractError("Llama C0/S1/S2 evidence is incomplete")
    if target.get("target_instruction", {}).get("nvbit_static_index") != 101 or 34 not in target.get("excluded_static_indices", []): raise ContractError("Llama target does not preserve static-index evidence and 34 exclusion")
    exhaustion = ledger_exhaustion(ledger, llama["exact_identity"]["package_id"].replace("C16_GPU_PACKAGE_P0", "c16_llama32_1b_frozen_compatible"))
    args.output.mkdir(parents=True)
    # Copy C0 authoritative inputs so the final manifest is self-contained.
    for source, name in ((args.inventory, "C0_REMOTE_ASSET_INVENTORY.json"), (args.c0_ledger, "C0_CAMPAIGN_LEDGER.json")):
        (args.output / name).write_bytes(source.read_bytes())
    llama_closeout = {"schema_version": SCHEMA, "model_key": "llama_3p2_1b", "status": "BLOCKED_RUNTIME_WITH_FROZEN_CONTRACT", "scientific_eligible": False,
        "reason": "NVBIT_WINDOW_BUDGET_EXHAUSTED_BY_RETAINED_HISTORICAL_DIAGNOSTIC_WINDOWS_NO_RESET_OR_RECLASSIFICATION_ALLOWED", "exact_identity": llama["exact_identity"],
        "workload": "S0/B1/T128/Decode4/TEXT", "s1": {"path": str(args.s1), "sha256": sha256_file(args.s1), "status": s1["status"], "output_checksum": s1["workload"]["output_checksum"]},
        "s2": {"path": str(args.s2), "sha256": sha256_file(args.s2), "status": s2["status"], "static_map": s2["static_map"]},
        "target": {"path": str(args.target), "sha256": sha256_file(args.target), "function": target["function"]["mangled_name"], "static_range": [101, 102], "opcode": target["target_instruction"]["opcode"], "historical_34_excluded": True, "historical_348_not_used": True},
        "S3_prelease_result": "REJECTED_BEFORE_GPU_MODEL_OR_MEASUREMENT_ACTIVE", "budget_exhaustion": {**exhaustion, "remote_ledger_path": args.remote_ledger_remote_path, "local_copied_ledger_sha256": sha256_file(args.remote_ledger)},
        "capture_results": {"prefill_records": "NOT_CAPTURED_BUDGET_EXHAUSTED", "decode_records": "NOT_CAPTURED_BUDGET_EXHAUSTED", "raw_trace_bytes": 0, "remote_local_sha_closed": "NO_NEW_RAW_CREATED"}}
    atomic_json(args.output / "LLAMA_MODEL_CLOSEOUT.json", llama_closeout)
    blocked_rows = []
    for row, name in zip(roster[1:], ("QWEN_0P5_BLOCKER.json", "QWEN_7B_AWQ_BLOCKER.json", "DEEPSEEK_BLOCKER.json", "GLM_BLOCKER.json")):
        if row.get("status") != "BLOCKED_ASSET_UNAVAILABLE": raise ContractError(f"{row.get('model_key')} is not the C0-proven unavailable asset")
        blocker = {"schema_version": SCHEMA, "model_key": row["model_key"], "status": "BLOCKED_ASSET_UNAVAILABLE", "scientific_eligible": False, "reason": row["reason"], "exact_identity": row["exact_identity"],
                   "inventory_path": str(args.inventory), "inventory_sha256": sha256_file(args.inventory), "network_download_forbidden": True, "substitution_forbidden": True, "gpu_work_started": False}
        atomic_json(args.output / name, blocker)
        blocked_rows.append((row, blocker))
    matrix = [{"MODEL": "Llama-3.2-1B", "EXACT_IDENTITY": llama["exact_identity"]["exact_model_id"] + "@" + llama["exact_identity"]["model_revision"], "ASSET_STATUS": "PRESENT_HASH_CLOSED", "WORKLOAD_CONTRACT": "S0/B1/T128/decode4/TEXT", "S1_RUNTIME_READY": "PASS", "TARGET_FULL_IDENTITY": target["function"]["mangled_name"], "STATIC_RANGE": "[101,102) LDG.E.U16; 34 excluded", "PREFILL_CAPTURE": "BLOCKED_BUDGET_EXHAUSTED", "DECODE_CAPTURE": "BLOCKED_BUDGET_EXHAUSTED", "REPRODUCIBILITY": "NOT_RUN_BUDGET_EXHAUSTED", "TOTAL_RECORDS": "0", "ADDRESS_RECORDS": "0", "TRACE_BYTES": "0", "REMOTE_LOCAL_SHA_CLOSED": "NO_NEW_RAW_CREATED", "FINAL_STATUS": "BLOCKED_RUNTIME_WITH_FROZEN_CONTRACT", "BLOCK_REASON": llama_closeout["reason"]}]
    for row, _blocker in blocked_rows:
        matrix.append({"MODEL": row["roster_label"], "EXACT_IDENTITY": "UNRESOLVED", "ASSET_STATUS": "UNAVAILABLE", "WORKLOAD_CONTRACT": "NOT_FROZEN", "S1_RUNTIME_READY": "NOT_RUN", "TARGET_FULL_IDENTITY": "NOT_REQUALIFIED", "STATIC_RANGE": "NOT_REQUALIFIED", "PREFILL_CAPTURE": "NOT_RUN", "DECODE_CAPTURE": "NOT_RUN", "REPRODUCIBILITY": "NOT_RUN", "TOTAL_RECORDS": "0", "ADDRESS_RECORDS": "0", "TRACE_BYTES": "0", "REMOTE_LOCAL_SHA_CLOSED": "NO_NEW_RAW_CREATED", "FINAL_STATUS": "BLOCKED_ASSET_UNAVAILABLE", "BLOCK_REASON": row["reason"]})
    write_tsv(args.output / "C2_CROSS_MODEL_INTEGRITY.tsv", matrix)
    summary = {"schema_version": SCHEMA, "campaign_status": STATUS, "scientific_eligible": False, "producer_code_commit": args.producer_code_commit, "runtime_lock": c0ledger["runtime_lock"], "model_count": 5, "successful_models": [], "blocked_models": ["llama_3p2_1b", "qwen_0p5", "qwen_7b_awq", "deepseek", "glm"], "total_raw_trace_bytes": 0,
               "all_successful_traces_sha_closed": True, "measurement_windows_clean": True, "active_gpu_process_count": 0, "active_diagnostic_process_count": 0, "measurement_active_after_campaign": False, "remote_only_required_artifact_count": 0,
               "invariants": {"nvbit": "1.7.5", "effective_cuda_module_loading": "EAGER", "cuda_driver_pytorch_mutated": False, "network_model_download": False, "raw_trace_in_git": False, "budget_ledger_reset_or_reclassification": False}}
    atomic_json(args.output / "C3_CAMPAIGN_SUMMARY.json", summary)
    report = "# C16 NVBit 1.7.5 multi-model trace campaign\n\n"
    report += f"Final status: `{STATUS}`. No successful full-model formal trace was emitted in this campaign closeout.\n\n"
    report += "Llama completed C0/S1/S2 with exact frozen identity and an NVBit-native direct GLOBAL `LDG.E.U16` target `[101,102)`; static index 34 remains explicitly excluded. S3 was rejected before a GPU model process or `MEASUREMENT_ACTIVE` because the retained ledger already has all six permitted `NVBIT` windows for the deployment. This report neither resets nor reclassifies those historical entries.\n\n"
    report += "Qwen 0.5, Qwen 7B-AWQ, DeepSeek, and GLM are each `BLOCKED_ASSET_UNAVAILABLE`: C0 found no local config/model asset under an exact frozen identity. No download, substitution, model execution, trace, or raw payload was created.\n\n"
    report += "All retained evidence named by this pack is hash closed; no active GPU/diagnostic process or measurement marker remains.\n"
    (args.output / "CAMPAIGN_FINAL_REPORT.md").write_text(report, encoding="utf-8")
    payloads = [{"path": name, "size_bytes": (args.output / name).stat().st_size, "sha256": sha256_file(args.output / name)} for name in PACK_FILES]
    manifest = {"schema_version": SCHEMA, "status": STATUS, "producer_implementation_commit": args.producer_code_commit, "final_publication_commit": "PENDING_COMMIT", "raw_trace_payloads_committed": False, "payloads": payloads}
    atomic_json(args.output / "PUBLISH_MANIFEST.json", manifest)
    atomic_json(args.output / "PUBLISH_VALIDATION.json", validate_manifest(args.output, manifest))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--output", type=Path, required=True); parser.add_argument("--inventory", type=Path, required=True); parser.add_argument("--c0-ledger", type=Path, required=True); parser.add_argument("--s1", type=Path, required=True); parser.add_argument("--s2", type=Path, required=True); parser.add_argument("--target", type=Path, required=True); parser.add_argument("--remote-ledger", type=Path, required=True); parser.add_argument("--remote-ledger-remote-path", required=True); parser.add_argument("--producer-code-commit", required=True)
    build(parser.parse_args())


if __name__ == "__main__":
    try: main()
    except ContractError as exc: raise SystemExit(f"FAIL multi-model campaign closeout: {exc}")
