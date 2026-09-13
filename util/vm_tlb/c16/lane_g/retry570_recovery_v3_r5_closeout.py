#!/usr/bin/env python3
"""Materialize the Recovery-V3 Qwen0 R5 provenance-only closeout.

This publisher never launches a process on the GPU.  It validates retained
direct-binding/static-map evidence, validates every retained failed-selector
payload against its independent remote manifest, and records the immutable
per-deployment NVBit budget gate without rewriting its historical ledger.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json, canonical_json, repo_root, sha256_file


SCHEMA = "C16_G_RECOVERY_V3_QWEN0_R5_CLOSEOUT_V1"
STATUS = "QWEN0_S0_G3_CAPABILITY_LIMITED_BUDGET_EXHAUSTED"
DEPLOYMENT = "c16_qwen25_05b_native_reference"


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"invalid JSON evidence: {path}") from exc
    if not isinstance(value, dict):
        raise ContractError(f"JSON object required: {path}")
    return value


def ref(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ContractError(f"retained evidence missing: {path}")
    return {"path": str(path), "size_bytes": path.stat().st_size, "sha256": sha256_file(path)}


def verify_retained_raw(root: Path, manifest: Path) -> dict[str, Any]:
    """Check the remote-to-local file manifest without treating it as science."""
    if not root.is_dir() or not manifest.is_file():
        raise ContractError("retained selector-failure artifact is absent")
    lines = manifest.read_text(encoding="utf-8").splitlines()
    if not lines:
        raise ContractError("retained selector-failure manifest is empty")
    count = 0
    total = 0
    for line in lines:
        try:
            digest, relative = line.split("  ", 1)
        except ValueError as exc:
            raise ContractError("malformed retained selector-failure manifest") from exc
        if len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
            raise ContractError("malformed retained selector-failure SHA256")
        target = root / relative
        if not target.is_file() or sha256_file(target) != digest:
            raise ContractError(f"retained selector-failure payload mismatch: {relative}")
        count += 1
        total += target.stat().st_size
    return {"manifest": ref(manifest), "payload_count": count, "tree_bytes": total,
            "all_remote_local_payload_hashes_match": True}


def current_head() -> str:
    import subprocess
    return subprocess.check_output(["git", "-C", str(repo_root()), "rev-parse", "HEAD"], text=True).strip()


def verify_budget(ledger_path: Path) -> dict[str, Any]:
    ledger = read_json(ledger_path)
    limit = ledger.get("limits", {}).get("nvbit_windows_per_deployment")
    rows = [row for row in ledger.get("entries", [])
            if row.get("deployment_id") == DEPLOYMENT and row.get("operation_kind") == "NVBIT"]
    if not isinstance(limit, int) or len(rows) != limit:
        raise ContractError("ledger does not prove frozen Qwen0 NVBit-window exhaustion")
    return {"ledger": ref(ledger_path), "deployment_id": DEPLOYMENT,
            "maximum_nvbit_windows": limit, "consumed_nvbit_windows": len(rows),
            "historical_entries": [{key: row.get(key) for key in (
                "run_id", "terminal_status", "evidence_classification", "diagnostic_reason", "raw_bytes", "elapsed_seconds")}
                                  for row in rows],
            "ledger_rewritten": False, "budget_bypass": False}


def validate_pack(directory: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    seen: set[str] = set()
    for payload in manifest.get("payloads", []):
        relative = payload.get("path")
        if not isinstance(relative, str) or relative in seen or Path(relative).is_absolute() or ".." in Path(relative).parts:
            raise ContractError("unsafe/duplicate publication payload")
        seen.add(relative)
        target = directory / relative
        if not target.is_file() or target.stat().st_size != payload.get("size_bytes") or sha256_file(target) != payload.get("sha256"):
            raise ContractError(f"unmaterialized publication payload: {relative}")
    return {"schema_version": SCHEMA, "status": "PUBLISH_MANIFEST_VALIDATION_PASS",
            "payload_count": len(seen), "no_duplicate_path": True,
            "all_payloads_exist_size_sha256_match": True,
            "manifest_sha256": sha256_file(directory / "PUBLISH_MANIFEST.json")}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--target-plan", type=Path, required=True)
    parser.add_argument("--bindings", type=Path, required=True)
    parser.add_argument("--prefill-target", type=Path, required=True)
    parser.add_argument("--decode-target", type=Path, required=True)
    parser.add_argument("--failure-root", type=Path, required=True)
    parser.add_argument("--failure-manifest", type=Path, required=True)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--producer-code-commit", required=True)
    parser.add_argument("--old-tracer-sha256", required=True)
    parser.add_argument("--corrected-tracer-sha256", required=True)
    args = parser.parse_args()
    if args.producer_code_commit != current_head():
        raise ContractError("publisher source commit must equal checked-out producer implementation")
    if args.output.exists():
        raise ContractError("R5 closeout refuses to overwrite retained publication")
    bindings, prefill, decode = map(read_json, (args.bindings, args.prefill_target, args.decode_target))
    if bindings.get("status") != "DIRECT_FUNCTION_BINDING_READY_FOR_STATIC_MAP":
        raise ContractError("direct function binding is not closed")
    for phase, target in (("PREFILL", prefill), ("DECODE", decode)):
        if target.get("status") != "NVBIT_NATIVE_STATIC_INDEX_SELECTED":
            raise ContractError(f"{phase} static target is not closed")
        instruction = target.get("target_instruction", {})
        if instruction.get("memory_space") != "GLOBAL" or not isinstance(instruction.get("nvbit_static_index"), int):
            raise ContractError(f"{phase} target is not a direct GLOBAL NVBit index")
    retained_raw = verify_retained_raw(args.failure_root, args.failure_manifest)
    budget = verify_budget(args.ledger)
    args.output.mkdir(parents=True)
    closeout = {
        "schema_version": SCHEMA,
        "status": STATUS,
        "scientific_eligible": False,
        "scientific_capture_result": "NONE",
        "producer_implementation_commit": args.producer_code_commit,
        "publication_handoff_commit": "RECORDED_BY_SEPARATE_POST_PUBLICATION_STATUS_COMMIT",
        "identity": {"deployment_id": DEPLOYMENT, "scenario_id": "S0", "model_id": "Qwen/Qwen2.5-0.5B-Instruct",
                     "model_revision": "7ae557604adf67be50417f59c2c2f167def9a775", "dtype": "float16", "backend": "sdpa", "cpu_offload": False},
        "frozen_target_plan": ref(args.target_plan),
        "direct_function_bindings": ref(args.bindings),
        "native_static_map_targets": {"prefill": ref(args.prefill_target), "decode": ref(args.decode_target)},
        "failed_old_selector_attempt": {"run_id": "8c93675b-bd5c-497f-9371-a7bbd5e1a3d2", "terminal_status": "FAILED_OR_ABORTED",
            "classification": "NON_SCIENTIFIC_DIAGNOSTIC", "old_tool_sha256": args.old_tracer_sha256,
            "reason": "OLD_TRACER_BINARY_PREDATED_EXACT_ROOT_STATIC_INDEX_ROI_CONTRACT", "retained_raw": retained_raw},
        "corrected_tracer": {"sha256": args.corrected_tracer_sha256,
            "status": "BUILT_AND_PROVENANCE_CHECKED_NOT_EXECUTED", "reason": "HARD_FROZEN_PER_DEPLOYMENT_NVBIT_WINDOW_BUDGET_EXHAUSTED"},
        "budget_gate": budget,
        "measurement_state_after": {"measurement_active": False, "active_gpu_process_count": 0, "new_raw_created_after_budget_gate": False},
        "conclusion": "Direct identity and direct static-memory targets are retained for a future authorized budget namespace; no selector substitution, range change, ledger reset, or scientific result was emitted."
    }
    atomic_json(args.output / "R5_QWEN2P5_0P5B_S0_CLOSEOUT.json", closeout)
    report = "# Recovery-V3 Qwen0 S0 R5 closeout\n\n"
    report += f"Status: `{STATUS}`. The direct PREFILL and DECODE bindings/static maps are hash-closed, but no scientific capture result exists.\n\n"
    report += "The retained old-tracer attempt is a `NON_SCIENTIFIC_DIAGNOSTIC`: its binary predated the exact-root/static-index/ROI contract and produced non-target files. The corrected tracer was built and provenance-checked, but was not run because all six immutable NVBit windows for this deployment are already consumed. No range, target, shape, backend, dtype, or budget was substituted.\n\n"
    report += "The retained failed-selector payload tree is remote-to-local SHA-closed via its independent manifest. Its actual retained bytes are reported separately from the historical parent receipt's `raw_bytes=0`; the latter is preserved unchanged and is not reclassified.\n"
    (args.output / "R5_QWEN2P5_0P5B_S0_CLOSEOUT.md").write_text(report, encoding="utf-8")
    names = ("R5_QWEN2P5_0P5B_S0_CLOSEOUT.json", "R5_QWEN2P5_0P5B_S0_CLOSEOUT.md")
    manifest = {"schema_version": SCHEMA, "status": STATUS, "producer_implementation_commit": args.producer_code_commit,
                "artifact_checkpoint_commit": "RECORDED_BY_SEPARATE_POST_PUBLICATION_STATUS_COMMIT", "raw_payloads_committed": False,
                "payloads": [{"path": name, "size_bytes": (args.output / name).stat().st_size, "sha256": sha256_file(args.output / name)} for name in names]}
    atomic_json(args.output / "PUBLISH_MANIFEST.json", manifest)
    atomic_json(args.output / "PUBLISH_VALIDATION.json", validate_pack(args.output, manifest))
    print(f"PASS {STATUS}")


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        raise SystemExit(f"FAIL Recovery-V3 R5 closeout: {exc}")
