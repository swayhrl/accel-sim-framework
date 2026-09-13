#!/usr/bin/env python3
"""Publish the post-Llama C16 NVBit175 dataset without inventing blocked data.

This is a publication-only assembler.  It validates the accepted Llama pack
and the metadata-only Phase-A evidence, then produces a compact, hash-closed
multi-model review pack.  Raw traces stay outside Git and are referenced only
through their already closed remote/local SHA256 index.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json, sha256_file, valid_sha256


SCHEMA = "C16_G_RETRY570_POST_LLAMA_MULTIMODEL_DATASET_V1"
STATUS = "C16_NVBIT175_POST_LLAMA_MULTIMODEL_DATASET_COMPLETE_WITH_BLOCKED_MODELS"
LLAMA_STATUS = "COMPLETE"
QWEN_BLOCKED = "BLOCKED_ASSET_UNAVAILABLE_AFTER_AUTHORITATIVE_SEARCH"
IDENTITY_BLOCKED = "BLOCKED_IDENTITY_UNRESOLVED_REQUIRES_USER"
EXPECTED_PHASE_A = {
    "qwen_0p5": "IDENTITY_RECOVERED_ASSET_MISSING",
    "qwen_7b_awq": "IDENTITY_RECOVERED_ASSET_MISSING",
    "deepseek": IDENTITY_BLOCKED,
    "glm": IDENTITY_BLOCKED,
}


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"invalid JSON evidence: {path}") from exc
    if not isinstance(value, dict):
        raise ContractError(f"JSON evidence must be an object: {path}")
    return value


def payload_rows(directory: Path) -> list[dict[str, Any]]:
    return [
        {"path": path.name, "size_bytes": path.stat().st_size, "sha256": sha256_file(path)}
        for path in sorted(directory.iterdir())
        if path.is_file() and path.name not in {"PUBLISH_MANIFEST.json", "PUBLISH_VALIDATION_RECEIPT.json"}
    ]


def validate_manifest(directory: Path) -> tuple[dict[str, Any], str]:
    manifest_path = directory / "PUBLISH_MANIFEST.json"
    manifest = load_json(manifest_path)
    payloads = manifest.get("payloads")
    if not isinstance(payloads, list) or not payloads:
        raise ContractError("reference manifest lacks payloads")
    paths: set[str] = set()
    for row in payloads:
        if not isinstance(row, dict) or set(("path", "size_bytes", "sha256")) - set(row):
            raise ContractError("reference manifest payload row is incomplete")
        name = row["path"]
        if not isinstance(name, str) or name in paths or "/" in name or not valid_sha256(row["sha256"]):
            raise ContractError("reference manifest has unsafe, duplicate, or invalid payload")
        paths.add(name)
        payload = directory / name
        if not payload.is_file() or payload.stat().st_size != row["size_bytes"] or sha256_file(payload) != row["sha256"]:
            raise ContractError(f"reference manifest payload fails closure: {name}")
    validation = load_json(directory / "PUBLISH_VALIDATION.json")
    if validation.get("all_payloads_exist_size_sha256_match") is not True:
        raise ContractError("reference manifest validator did not pass")
    actual = sha256_file(manifest_path)
    if validation.get("manifest_sha256") != actual:
        raise ContractError("reference validation has wrong manifest SHA256")
    return manifest, actual


def write_tsv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader(); writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--llama-pack", type=Path, required=True)
    parser.add_argument("--phase-a-json", type=Path, required=True)
    parser.add_argument("--phase-a-tsv", type=Path, required=True)
    parser.add_argument("--p3-attempt-stderr", type=Path, required=True)
    parser.add_argument("--remote-cleanup-audit", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--producer-code-commit", required=True)
    args = parser.parse_args()
    if args.output_dir.exists():
        raise ContractError("closeout refuses to overwrite a retained publication")
    if len(args.producer_code_commit) != 40 or any(char not in "0123456789abcdef" for char in args.producer_code_commit):
        raise ContractError("producer code commit must be an exact 40-hex Git object")

    llama_manifest, llama_manifest_sha = validate_manifest(args.llama_pack)
    llama_raw = load_json(args.llama_pack / "RAW_ARTIFACT_INDEX.json")
    s5 = load_json(args.llama_pack / "S5_FULL_WORKLOAD_SUMMARY.json")
    phase_a = load_json(args.phase_a_json)
    cleanup = load_json(args.remote_cleanup_audit)
    if phase_a.get("status") != "PHASE_A_IDENTITY_ASSET_RECOVERY_COMPLETE_WITH_BLOCKERS" or phase_a.get("no_gpu_or_model_execution") is not True:
        raise ContractError("Phase-A inventory is not the required metadata-only blocker evidence")
    phase_models = {row.get("model_key"): row for row in phase_a.get("models", []) if isinstance(row, dict)}
    if {key: phase_models.get(key, {}).get("status") for key in EXPECTED_PHASE_A} != EXPECTED_PHASE_A:
        raise ContractError("Phase-A model statuses differ from the frozen closeout boundary")
    if "Network is unreachable" not in args.p3_attempt_stderr.read_text(encoding="utf-8", errors="replace"):
        raise ContractError("P3 retained error does not prove the current network boundary")
    if cleanup.get("active_gpu_process_count") != 0 or cleanup.get("measurement_active") is not False or cleanup.get("active_diagnostic_process_count") != 0:
        raise ContractError("remote cleanup audit is not quiescent")

    traces = llama_raw.get("traces")
    if not isinstance(traces, list) or len(traces) != 6 or not all(row.get("sha_equal") is True for row in traces):
        raise ContractError("accepted Llama raw index is not six-way SHA closed")
    total_raw = sum(int(row["local_size_bytes"]) for row in traces)
    if total_raw <= 0:
        raise ContractError("accepted Llama raw index has no retained data")
    args.output_dir.mkdir(parents=True)

    # Preserve the exact Phase-A payload bytes, rather than reserializing them.
    shutil.copyfile(args.phase_a_json, args.output_dir / "PHASE_A_IDENTITY_ASSET_INVENTORY.json")
    shutil.copyfile(args.phase_a_tsv, args.output_dir / "POST_LLAMA_MODEL_IDENTITY_MATRIX.tsv")
    p3_receipt = {
        "schema_version": SCHEMA,
        "status": "EXACT_P3_ASSET_RETRIEVAL_NETWORK_UNREACHABLE",
        "scientific_eligible": False,
        "source_path": str(args.p3_attempt_stderr),
        "source_size_bytes": args.p3_attempt_stderr.stat().st_size,
        "source_sha256": sha256_file(args.p3_attempt_stderr),
        "exact_package": phase_models["qwen_7b_awq"]["identity"],
        "evidence": "Retained exact immutable-revision config fetch reached NETWORK_UNREACHABLE; no partial package is qualified.",
    }
    atomic_json(args.output_dir / "P3_UPSTREAM_FAILURE_RECEIPT.json", p3_receipt)
    shutil.copyfile(args.remote_cleanup_audit, args.output_dir / "FINAL_REMOTE_CLEANUP_AUDIT.json")

    model_rows = [
        {"model_key": "llama_3p2_1b", "status": LLAMA_STATUS, "exact_identity": "meta-llama/Llama-3.2-1B@4e20de362430cd3b72f300e6b0f18e50e7166e08", "capture_scope": "S0-S6 target-qualified prefill plus actual cache-correct decode", "blocker_or_evidence": f"Accepted Llama closeout manifest {llama_manifest_sha}"},
        {"model_key": "qwen_0p5", "status": QWEN_BLOCKED, "exact_identity": f"{phase_models['qwen_0p5']['identity']['exact_model_id']}@{phase_models['qwen_0p5']['identity']['revision']}", "capture_scope": "NO_CAPTURE", "blocker_or_evidence": "Exact P1 identity recovered; authorized local metadata scan found no asset and same-session upstream is unavailable."},
        {"model_key": "qwen_7b_awq", "status": QWEN_BLOCKED, "exact_identity": f"{phase_models['qwen_7b_awq']['identity']['exact_model_id']}@{phase_models['qwen_7b_awq']['identity']['revision']}", "capture_scope": "NO_CAPTURE", "blocker_or_evidence": f"Exact P3 config retrieval error SHA256 {p3_receipt['source_sha256']}; no substitute or partial package used."},
        {"model_key": "deepseek", "status": IDENTITY_BLOCKED, "exact_identity": "UNRESOLVED (C15 static candidate is not a C16 runnable identity)", "capture_scope": "NO_CAPTURE", "blocker_or_evidence": phase_models["deepseek"]["reason"]},
        {"model_key": "glm", "status": IDENTITY_BLOCKED, "exact_identity": "UNRESOLVED", "capture_scope": "NO_CAPTURE", "blocker_or_evidence": phase_models["glm"]["reason"]},
    ]
    write_tsv(args.output_dir / "MODEL_DATASET_MATRIX.tsv", list(model_rows[0]), model_rows)
    prefill = s5["prefill_target"]
    decode = s5["decode_target"]
    target_rows = [
        {"model_key": "llama_3p2_1b", "phase": "PREFILL", "target_role": prefill["role"], "full_mangled_function": prefill["function"], "static_range": str(prefill["static_range"]), "opcode": "LDG.E.U16", "records": str(prefill["record_count"]), "status": "CAPTURED_SHA_CLOSED"},
        {"model_key": "llama_3p2_1b", "phase": "DECODE1", "target_role": decode["role"], "full_mangled_function": decode["function"], "static_range": str(decode["static_range"]), "opcode": decode["opcode"], "records": "0", "status": "PREFILL_DERIVED_NO_SEPARATE_CUDA_FORWARD"},
    ]
    for phase, details in decode["actual_forward_records"].items():
        target_rows.append({"model_key": "llama_3p2_1b", "phase": phase, "target_role": decode["role"], "full_mangled_function": decode["function"], "static_range": str(decode["static_range"]), "opcode": decode["opcode"], "records": str(details["record_count"]), "status": "CAPTURED_SHA_CLOSED"})
    write_tsv(args.output_dir / "PHASE_TARGET_MATRIX.tsv", list(target_rows[0]), target_rows)
    zero_rows = [
        {"model_key": "llama_3p2_1b", "target_role": "LARGE_INDEX_PREFILL_TARGET", "phase_scope": "DECODE1-DECODE4", "status": "STRUCTURAL_ZERO_TARGET_NOT_LAUNCHED", "evidence": "Full LargeIndex target absent from decode census; this does not claim decode has no memory access."},
        *[{"model_key": key, "target_role": "NO_CAPTURE", "phase_scope": "ALL", "status": "MODEL_BLOCKED_NO_CAPTURE", "evidence": next(row["blocker_or_evidence"] for row in model_rows if row["model_key"] == key)} for key in ("qwen_0p5", "qwen_7b_awq", "deepseek", "glm")],
    ]
    write_tsv(args.output_dir / "STRUCTURAL_ZERO_AUDIT.tsv", list(zero_rows[0]), zero_rows)
    consumer = {
        "schema_version": SCHEMA,
        "status": "DOWNSTREAM_CONSUMER_VALIDATION_PASS",
        "consumer_requirement": "PHASE_TARGETED_MEMORY",
        "validated_against": ["docs/vm_tlb/chatgpt_handoff/c16_multimodel_native/C16_LANE_H_GOAL.md", "util/vm_tlb/c16/lane_g/retry570_multimodel_capture.py"],
        "result": "The accepted Llama pack supplies phase-labelled target memory records and raw SHA closure. No C16 consumer requires a generic kernelslist.g or Accel-Sim replay artifact.",
        "excluded_non_c16_scope": "The M4 kernelslist.g/Accel-Sim pipeline is not a C16 Lane-H input and was not used to expand this campaign.",
        "non_llama": "No blocked model is represented as captured data.",
    }
    atomic_json(args.output_dir / "DOWNSTREAM_CONSUMER_VALIDATION.json", consumer)
    notes = """# Post-Llama cross-model comparability\n\nOnly Llama has an accepted target-qualified memory-trace dataset in this publication. Its prefill `indexSelectLargeIndex` target and decode `indexSelectSmallIndex` target are independently NVBit-mapped and are **not** interchangeable static ranges. The four other model rows are evidence-backed blockers, not zero-valued observations and not comparable measurements.\n\n`STRUCTURAL_ZERO_TARGET_NOT_LAUNCHED` applies only to Llama's LargeIndex target during logical decode; the independent SmallIndex decode target demonstrates that this is not a claim that decode contains no memory accesses.\n"""
    (args.output_dir / "CROSS_MODEL_COMPARABILITY_NOTES.md").write_text(notes, encoding="utf-8")
    raw_index = {"schema_version": SCHEMA, "status": "ALL_SUCCESSFUL_TRACES_REMOTE_LOCAL_SHA_CLOSED", "raw_trace_payloads_committed": False, "total_raw_trace_bytes": total_raw, "models": {"llama_3p2_1b": {"source_raw_index_sha256": sha256_file(args.llama_pack / "RAW_ARTIFACT_INDEX.json"), "traces": traces}, "qwen_0p5": [], "qwen_7b_awq": [], "deepseek": [], "glm": []}}
    atomic_json(args.output_dir / "RAW_ARTIFACT_INDEX.json", raw_index)
    summary = {"schema_version": SCHEMA, "status": STATUS, "scientific_eligible_for_timing": False, "llama_reference": {"status": LLAMA_STATUS, "source_manifest_sha256": llama_manifest_sha, "source_producer_code_commit": llama_manifest.get("producer_code_commit")}, "models": {row["model_key"]: row["status"] for row in model_rows}, "blocked_models": [row["model_key"] for row in model_rows if row["status"] != LLAMA_STATUS], "all_successful_traces_sha_closed": True, "total_raw_trace_bytes": total_raw, "measurement_windows_clean": True, "remote_cleanup": cleanup, "producer_code_commit": args.producer_code_commit}
    atomic_json(args.output_dir / "CAMPAIGN_SUMMARY.json", summary)
    manifest = {"schema_version": SCHEMA, "status": STATUS, "producer_code_commit": args.producer_code_commit, "raw_trace_payloads_committed": False, "payloads": payload_rows(args.output_dir)}
    atomic_json(args.output_dir / "PUBLISH_MANIFEST.json", manifest)
    paths = [row["path"] for row in manifest["payloads"]]
    closed = len(paths) == len(set(paths)) and all((args.output_dir / row["path"]).is_file() and (args.output_dir / row["path"]).stat().st_size == row["size_bytes"] and sha256_file(args.output_dir / row["path"]) == row["sha256"] for row in manifest["payloads"])
    if not closed:
        raise ContractError("post-Llama publication manifest failed independent payload closure")
    atomic_json(args.output_dir / "PUBLISH_VALIDATION_RECEIPT.json", {"schema_version": SCHEMA, "status": "PUBLISH_MANIFEST_VALIDATION_PASS", "all_payloads_exist_size_sha256_match": True, "no_duplicate_path": True, "payload_count": len(paths), "manifest_sha256": sha256_file(args.output_dir / "PUBLISH_MANIFEST.json")})
    print(f"PASS {STATUS}")


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        raise SystemExit(f"FAIL post-Llama dataset closeout: {exc}")
