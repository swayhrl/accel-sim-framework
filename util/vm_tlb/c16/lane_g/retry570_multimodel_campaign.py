#!/usr/bin/env python3
"""C0 inventory/freeze helpers for the NVBit 1.7.5 multi-model campaign.

Inventory is deliberately metadata-only: it opens model configuration/package
receipts but never imports torch, tokenizers, or model weights.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json, canonical_json, sha256_file

SCHEMA = "C16_G_RETRY570_MULTIMODEL_CAMPAIGN_V1"
ROSTER = (
    ("llama_3p2_1b", "Llama-3.2-1B", ("llama",)),
    ("qwen_0p5", "Qwen 0.5-class existing campaign target", ("qwen", "0.5")),
    ("qwen_7b_awq", "Qwen 7B AWQ existing campaign target", ("qwen", "7b", "awq")),
    ("deepseek", "DeepSeek required AI-trace target", ("deepseek",)),
    ("glm", "GLM required AI-trace target", ("glm",)),
)
LLAMA_PACKAGE = "C16_GPU_PACKAGE_P0"
LLAMA_RELATIVE = Path("packages") / LLAMA_PACKAGE
LLAMA_MODEL = "c16_llama32_1b_frozen_compatible"
LLAMA_COMMIT = "20fb38e6ca629f1a93db7939248bd1a03790724c"
LLAMA_MANIFEST = "ac59f0d2aca95021c686948d7244ce50375530bbe983c8508ca5f6954e80230f"
LLAMA_REVISION = "4e20de362430cd3b72f300e6b0f18e50e7166e08"


def git_head() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read JSON object: {path}") from exc
    if not isinstance(value, dict): raise ContractError(f"JSON object required: {path}")
    return value


def model_config_rows(root: Path) -> list[dict[str, Any]]:
    rows = []
    for config in sorted(root.rglob("config.json")):
        try:
            data = read_json(config)
        except ContractError:
            continue
        rows.append({"path": str(config), "sha256": sha256_file(config), "size_bytes": config.stat().st_size,
                     "model_type": data.get("model_type", "UNRESOLVED"), "architectures": data.get("architectures", []),
                     "directory_bytes": sum(item.stat().st_size for item in config.parent.rglob("*") if item.is_file())})
    return rows


def matches(row: dict[str, Any], tokens: tuple[str, ...]) -> bool:
    value = " ".join((str(row.get("path", "")), str(row.get("model_type", "")), canonical_json(row.get("architectures", [])))).lower()
    return all(token in value for token in tokens)


def inventory(root: Path) -> dict[str, Any]:
    if not root.is_dir(): raise ContractError("inventory root is absent")
    configs = model_config_rows(root)
    package_root = root / LLAMA_RELATIVE
    package_manifest = package_root / "package_metadata" / "C16_GPU_PACKAGE_P0_MANIFEST.json"
    token_receipt = package_root / "a_assets" / "TOKEN_RECEIPTS" / LLAMA_MODEL / "TEXT_T128.json"
    llama_model_root = package_root / "models" / LLAMA_MODEL
    roster = []
    for key, label, tokens in ROSTER:
        candidates = [row for row in configs if matches(row, tokens)]
        if key == "llama_3p2_1b":
            if (len(candidates) != 1 or candidates[0]["path"] != str(llama_model_root / "config.json") or
                    not package_manifest.is_file() or not token_receipt.is_file() or sha256_file(package_manifest) != LLAMA_MANIFEST):
                status, reason = "BLOCKED_IDENTITY_NOT_FROZEN", "P0_Llama_package_or_exact_S0_token_binding_is_not_closed"
                identity: dict[str, Any] = {"exact_model_id": "UNRESOLVED"}
            else:
                status, reason = "S0_FROZEN_READY", "P0_HASH_CLOSED_LOCAL_ASSET"
                identity = {"exact_model_id": "meta-llama/Llama-3.2-1B", "model_revision": LLAMA_REVISION,
                            "package_id": LLAMA_PACKAGE, "package_fixed_commit": LLAMA_COMMIT,
                            "package_manifest_sha256": LLAMA_MANIFEST, "model_path": str(llama_model_root),
                            "config_sha256": candidates[0]["sha256"], "token_receipt": str(token_receipt),
                            "token_receipt_sha256": sha256_file(token_receipt), "workload": "S0/B1/T128/Decode4/TEXT"}
        elif not candidates:
            status, reason, identity = "BLOCKED_ASSET_UNAVAILABLE", "NO_LOCAL_CONFIG_JSON_MATCHING_REQUIRED_ROSTER_LABEL", {"exact_model_id": "UNRESOLVED"}
        else:
            status, reason, identity = "BLOCKED_IDENTITY_NOT_FROZEN", "LOCAL_CANDIDATE_PRESENT_BUT_NO_AUTHORITATIVE_PACKAGE_IDENTITY", {"candidate_configs": candidates}
        roster.append({"model_key": key, "roster_label": label, "status": status, "reason": reason,
                       "matching_config_count": len(candidates), "exact_identity": identity})
    storage = os.statvfs(root)
    return {"schema_version": SCHEMA, "stage": "C0_CAMPAIGN_INVENTORY", "scientific_eligible": False,
            "inventory_code_commit": git_head(), "inventory_root": str(root), "storage": {"total_bytes": storage.f_blocks * storage.f_frsize, "available_bytes": storage.f_bavail * storage.f_frsize},
            "all_local_model_configs": configs, "roster": roster,
            "constraints": {"torch_imported": False, "weights_loaded": False, "network_download": False, "gpu_work": False}}


def campaign_ledger(inventory_data: dict[str, Any], producer: str) -> dict[str, Any]:
    if inventory_data.get("stage") != "C0_CAMPAIGN_INVENTORY" or inventory_data.get("scientific_eligible") is not False:
        raise ContractError("inventory is not a C0 non-scientific receipt")
    roster = inventory_data.get("roster")
    if not isinstance(roster, list) or [row.get("model_key") for row in roster] != [row[0] for row in ROSTER]:
        raise ContractError("inventory roster differs from frozen campaign roster")
    allowed = {"S0_FROZEN_READY", "BLOCKED_ASSET_UNAVAILABLE", "BLOCKED_IDENTITY_NOT_FROZEN"}
    if any(row.get("status") not in allowed for row in roster): raise ContractError("inventory contains an invalid C0 state")
    return {"schema_version": SCHEMA, "stage": "C0_CAMPAIGN_LEDGER", "scientific_eligible": False,
            "producer_code_commit": producer, "inventory_sha256": inventory_data.get("inventory_sha256"),
            "runtime_lock": {"gpu": "RTX3090", "compute_capability": "SM86", "driver": "570.124.04", "cuda_toolkit": "12.4", "pytorch": "2.5.1+cu124", "nvbit": "1.7.5", "effective_cuda_module_loading": "EAGER"},
            "models": roster, "next_model": "llama_3p2_1b", "global_invariants": {"network_model_download_forbidden": True, "raw_trace_in_git": False, "prewarm_outside_measurement": True}}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True); group.add_argument("--inventory", action="store_true"); group.add_argument("--ledger", action="store_true")
    parser.add_argument("--root", type=Path); parser.add_argument("--inventory-receipt", type=Path); parser.add_argument("--output", type=Path, required=True); parser.add_argument("--producer-code-commit")
    args = parser.parse_args()
    if args.inventory:
        if args.root is None: parser.error("--inventory requires --root")
        value = inventory(args.root); atomic_json(args.output, value); print(f"PASS C0 remote inventory: {args.output}")
    else:
        if args.inventory_receipt is None or args.producer_code_commit != git_head(): raise ContractError("ledger requires the current producer commit and an inventory receipt")
        value = read_json(args.inventory_receipt); value["inventory_sha256"] = sha256_file(args.inventory_receipt)
        atomic_json(args.output, campaign_ledger(value, args.producer_code_commit)); print(f"PASS C0 campaign ledger: {args.output}")


if __name__ == "__main__":
    try: main()
    except ContractError as exc: raise SystemExit(f"FAIL C0 campaign inventory: {exc}")
