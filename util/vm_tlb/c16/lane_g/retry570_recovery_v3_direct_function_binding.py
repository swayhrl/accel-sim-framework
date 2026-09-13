#!/usr/bin/env python3
"""Bind Recovery V3 targets to direct NVBit identities without name guessing.

The frozen target plan supplies a profile-side launch ordinal plus launch
geometry.  A diagnostic-only NVBit launch inventory supplies the direct
function identity at every runtime launch ordinal.  This program accepts a
binding only if those independent structural fields agree exactly.  Kernel
names are retained as provenance but are never used for selection.
"""
from __future__ import annotations

import argparse
import csv
import json
import subprocess
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json, canonical_json, repo_root, sha256_file


SCHEMA = "C16_G_RECOVERY_V3_DIRECT_FUNCTION_BINDING_V1"


def producer_code_commit() -> str:
    return subprocess.check_output(
        ["git", "-C", str(repo_root()), "rev-parse", "HEAD"], text=True,
    ).strip()


def parse_inventory(path: Path) -> list[dict[str, str]]:
    required = {
        "global_launch_ordinal", "function_full_name", "function_mangled_name",
        "function_address", "grid", "block",
    }
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames is None or set(reader.fieldnames) != required:
            raise ContractError("direct launch inventory has an unexpected schema")
        rows = list(reader)
    if not rows:
        raise ContractError("direct launch inventory has no runtime launch rows")
    ordinals = [row["global_launch_ordinal"] for row in rows]
    if len(ordinals) != len(set(ordinals)):
        raise ContractError("direct launch inventory repeats a global launch ordinal")
    if any(not row["function_mangled_name"] or not row["function_full_name"] for row in rows):
        raise ContractError("direct launch inventory contains an unresolved function identity")
    return rows


def build_bindings(plan: Path, inventory: Path, inventory_receipt: Path) -> dict[str, Any]:
    rows = parse_inventory(inventory)
    by_ordinal = {int(row["global_launch_ordinal"]): row for row in rows}
    by_geometry: dict[tuple[str, str], list[dict[str, str]]] = {}
    for row in rows:
        by_geometry.setdefault((row["grid"], row["block"]), []).append(row)
    with plan.open(encoding="utf-8", newline="") as handle:
        plans = list(csv.DictReader(handle, delimiter="\t"))
    if not plans or {row.get("phase") for row in plans} != {"PREFILL", "DECODE"}:
        raise ContractError("target plan must have exactly the frozen PREFILL and DECODE rows")
    receipt = json.loads(inventory_receipt.read_text(encoding="utf-8"))
    if receipt.get("status") != "MODEL_NVBIT_QUALIFICATION_FORWARD_COMPLETE" or receipt.get("scientific_eligible") is not False:
        raise ContractError("direct inventory receipt is not a completed diagnostic-only workload")
    result: list[dict[str, Any]] = []
    for plan_row in plans:
        try:
            key = json.loads(plan_row["second_pass_validation_key"])
            ordinal = int(key["source_launch_ordinal"])
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise ContractError("target plan lacks a structural source launch ordinal") from exc
        if key.get("grid") != plan_row["grid"] or key.get("block") != plan_row["block"]:
            raise ContractError("target-plan structural validation key disagrees with row geometry")
        direct = by_ordinal.get(ordinal)
        if direct is None:
            raise ContractError(f"direct inventory lacks frozen source launch ordinal {ordinal}")
        if (direct["grid"], direct["block"]) != (plan_row["grid"], plan_row["block"]):
            raise ContractError("direct runtime ordinal exists but its grid/block differs from the frozen target")
        peers = by_geometry[(plan_row["grid"], plan_row["block"])]
        identities = {(item["function_full_name"], item["function_mangled_name"]) for item in peers}
        if len(identities) != 1:
            raise ContractError("geometry-stable direct inventory has multiple function identities; refusing ambiguous mapping")
        result.append({
            "phase": plan_row["phase"],
            "target_plan_id": plan_row["target_plan_id"],
            "deployment_id": plan_row["deployment_id"],
            "scenario_id": plan_row["scenario_id"],
            "source_profile_run_id": plan_row["source_run_id"],
            "source_profile_catalog_sha256": plan_row["source_catalog_sha256"],
            "source_launch_ordinal": ordinal,
            "grid": plan_row["grid"],
            "block": plan_row["block"],
            "direct_function_full_name": direct["function_full_name"],
            "direct_function_mangled_name": direct["function_mangled_name"],
            "direct_function_address_observed": direct["function_address"],
            "inventory_geometry_match_count": len(peers),
            "inventory_geometry_unique_function_count": len(identities),
            "mapping_method": "DIRECT_NVBIT_FUNCTION_IDENTITY_PLUS_FROZEN_ORDINAL_GRID_BLOCK",
            "kernel_name_used_for_selection": False,
            "status": "READY_FOR_NVBIT_NATIVE_STATIC_MAP",
        })
    return {
        "schema_version": SCHEMA,
        "producer_code_commit": producer_code_commit(),
        "status": "DIRECT_FUNCTION_BINDING_READY_FOR_STATIC_MAP",
        "scientific_eligible_for_timing": False,
        "inputs": {
            "target_plan": str(plan), "target_plan_sha256": sha256_file(plan),
            "direct_launch_inventory": str(inventory), "direct_launch_inventory_sha256": sha256_file(inventory),
            "inventory_qualification_receipt": str(inventory_receipt),
            "inventory_qualification_receipt_sha256": sha256_file(inventory_receipt),
            "inventory_run_identity": receipt["identity"],
        },
        "bindings": sorted(result, key=lambda item: item["phase"]),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-plan", type=Path, required=True)
    parser.add_argument("--direct-launch-inventory", type=Path, required=True)
    parser.add_argument("--inventory-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ContractError("direct-function binding refuses to overwrite a prior receipt")
    payload = build_bindings(args.target_plan, args.direct_launch_inventory, args.inventory_receipt)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    atomic_json(args.output, payload)
    print(canonical_json({"status": payload["status"], "output": str(args.output), "sha256": sha256_file(args.output)}))


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        raise SystemExit(f"FAIL direct function binding: {exc}")
