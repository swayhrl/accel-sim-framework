#!/usr/bin/env python3
"""Materialize a hash-closed Recovery-V3 runtime binding at a new model root.

The immutable A package binding names the package's original model directory.
Recovery V3 keeps a separately hash-closed model copy under the bulk root, so
the runner needs a binding whose *locations* point at that copy.  This helper
is deliberately narrow: every non-location identity field is retained from
the immutable binding, every model payload is revalidated by byte size and
SHA256, and it refuses to overwrite either retained evidence output.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json, sha256_file, valid_sha256


SCHEMA = "C16_G_RECOVERY_V3_RELOCATED_RUNTIME_BINDING_V1"
RUNTIME_SCHEMA = "C16_G_RUNTIME_FROZEN_BINDING_V1"


def read_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read JSON object: {path}") from exc
    if not isinstance(value, dict):
        raise ContractError(f"JSON root is not an object: {path}")
    return value


def required_binding(path: Path) -> dict[str, Any]:
    value = read_object(path)
    needed = ("schema_version", "status", "scientific_eligible", "deployment_id",
              "model_id", "model_revision", "tokenizer_revision", "scenario", "input",
              "model_path", "model_files", "package_id", "package_fixed_commit",
              "package_manifest_sha256", "wheelhouse_manifest_sha256")
    if (value.get("schema_version") != RUNTIME_SCHEMA or
            value.get("status") != "FROZEN_RUNTIME_BINDING_READY" or
            value.get("scientific_eligible") is not False or
            any(key not in value for key in needed)):
        raise ContractError("source binding is not an eligible frozen runtime binding")
    if not isinstance(value["input"], dict) or not isinstance(value["model_files"], list):
        raise ContractError("source binding input/model_files are malformed")
    return value


def verify_token_ids(binding: dict[str, Any], token_ids: Path) -> str:
    input_value = binding["input"]
    expected = input_value.get("derived_token_ids_sha256")
    if not isinstance(expected, str) or not valid_sha256(expected):
        raise ContractError("source binding lacks a valid derived-token SHA256")
    if not token_ids.is_file() or sha256_file(token_ids) != expected:
        raise ContractError("candidate token IDs differ from immutable frozen binding")
    return expected


def verify_model_root(binding: dict[str, Any], model_root: Path) -> list[dict[str, Any]]:
    if not model_root.is_dir():
        raise ContractError("relocated model root is absent")
    closed: list[dict[str, Any]] = []
    names: set[str] = set()
    for row in binding["model_files"]:
        if not isinstance(row, dict):
            raise ContractError("bound model-file row is malformed")
        rel = row.get("path")
        expected_size, expected_sha = row.get("size_bytes"), row.get("sha256")
        if not isinstance(rel, str) or not isinstance(expected_size, int) or not valid_sha256(expected_sha):
            raise ContractError("bound model-file identity is malformed")
        # The immutable path is package-relative (models/<deployment>/<name>).
        # A basename collision would make a location-only relocation ambiguous.
        name = Path(rel).name
        if not name or name in names:
            raise ContractError("bound model-file names are ambiguous for relocation")
        names.add(name)
        actual = model_root / name
        if not actual.is_file() or actual.stat().st_size != expected_size or sha256_file(actual) != expected_sha:
            raise ContractError(f"relocated model payload differs from immutable binding: {name}")
        closed.append({"relative_path": name, "path": str(actual),
                       "size_bytes": expected_size, "sha256": expected_sha})
    if not closed:
        raise ContractError("source binding has no model payloads")
    return closed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-binding", type=Path, required=True)
    parser.add_argument("--source-token-ids", type=Path, required=True)
    parser.add_argument("--model-root", type=Path, required=True)
    parser.add_argument("--output-token-ids", type=Path, required=True)
    parser.add_argument("--output-binding", type=Path, required=True)
    parser.add_argument("--closure-receipt", type=Path, required=True)
    args = parser.parse_args()
    if args.output_binding.exists() or args.closure_receipt.exists():
        raise ContractError("relocation refuses to overwrite retained binding evidence")
    binding = required_binding(args.source_binding)
    token_sha = verify_token_ids(binding, args.source_token_ids)
    model_files = verify_model_root(binding, args.model_root)
    args.output_token_ids.parent.mkdir(parents=True, exist_ok=True)
    if args.output_token_ids.exists() and sha256_file(args.output_token_ids) != token_sha:
        raise ContractError("existing relocated token IDs differ from immutable binding")
    if not args.output_token_ids.exists():
        args.output_token_ids.write_bytes(args.source_token_ids.read_bytes())
    if sha256_file(args.output_token_ids) != token_sha:
        raise ContractError("written relocated token IDs did not preserve SHA256")

    relocated = copy.deepcopy(binding)
    relocated["model_path"] = str(args.model_root)
    relocated["input"]["derived_token_ids_path"] = str(args.output_token_ids)
    relocated["input"]["derived_token_ids_sha256"] = token_sha
    relocated["recovery_v3_relocation"] = {
        "schema_version": SCHEMA,
        "source_binding_path": str(args.source_binding),
        "source_binding_sha256": sha256_file(args.source_binding),
        "relocation_semantics": "LOCATION_ONLY_MODEL_AND_TOKEN_PATH_REBIND",
        "validated_model_files": model_files,
        "model_root": str(args.model_root),
    }
    atomic_json(args.output_binding, relocated)
    receipt = {
        "schema_version": SCHEMA,
        "status": "REMOTE_RUNTIME_BINDING_LOCATION_REBOUND_HASH_CLOSED",
        "scientific_eligible": False,
        "deployment_id": binding["deployment_id"],
        "model_id": binding["model_id"],
        "model_revision": binding["model_revision"],
        "scenario_id": binding["scenario"]["scenario_id"],
        "input_class": binding["input"].get("class"),
        "source_binding": {"path": str(args.source_binding), "sha256": sha256_file(args.source_binding)},
        "relocated_binding": {"path": str(args.output_binding), "sha256": sha256_file(args.output_binding)},
        "token_ids": {"path": str(args.output_token_ids), "sha256": token_sha},
        "model_root": str(args.model_root),
        "model_files": model_files,
        "package": {key: binding[key] for key in ("package_id", "package_fixed_commit", "package_manifest_sha256", "wheelhouse_manifest_sha256")},
        "model_execution": False,
        "gpu_used": False,
    }
    atomic_json(args.closure_receipt, receipt)
    print("PASS REMOTE_RUNTIME_BINDING_LOCATION_REBOUND_HASH_CLOSED")


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        raise SystemExit(f"FAIL Recovery-V3 binding relocation: {exc}")
