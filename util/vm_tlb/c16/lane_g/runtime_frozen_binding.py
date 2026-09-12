#!/usr/bin/env python3
"""Bind one immutable A rolling-package scenario to fixed target token IDs.

The accepted G runner consumes a JSON list of IDs, whereas A's immutable
receipt stores that list together with its derivation and hashes.  This helper
checks the receipt and writes only the already-frozen ``target_token_ids`` to
a separate runtime file; it never tokenizes, truncates, pads, or changes an
input on the GPU instance.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json, canonical_json, sha256_file


SCENARIO_FIELDS = (
    "scenario_id", "batch_size", "prefill_tokens", "decode_tokens",
    "frozen_input_classes", "input_derivation", "feature_policy", "wave_scope", "status",
)


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read immutable JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError(f"immutable JSON root must be an object: {path}")
    return value


def read_scenario(path: Path, scenario_id: str) -> dict[str, str]:
    try:
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            if tuple(reader.fieldnames or ()) != SCENARIO_FIELDS:
                raise ContractError("A scenario matrix schema is not the bound rolling-package schema")
            rows = [row for row in reader if row["scenario_id"] == scenario_id]
    except OSError as exc:
        raise ContractError(f"cannot read immutable scenario matrix: {exc}") from exc
    if len(rows) != 1:
        raise ContractError(f"immutable package has {len(rows)} rows for scenario {scenario_id}")
    row = rows[0]
    if row["status"] != "FROZEN_NOT_EXECUTED":
        raise ContractError("scenario package state is not eligible for first execution")
    return row


def required_string(value: dict[str, Any], key: str) -> str:
    item = value.get(key)
    if not isinstance(item, str) or not item:
        raise ContractError(f"token receipt lacks {key}")
    return item


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-root", type=Path, required=True)
    parser.add_argument("--deployment-id", required=True)
    parser.add_argument("--scenario-id", required=True)
    parser.add_argument("--input-class", required=True, choices=("TEXT", "CODE", "STRUCTURED"))
    parser.add_argument("--token-ids-output", type=Path, required=True)
    parser.add_argument("--binding-receipt", type=Path, required=True)
    parser.add_argument("--canary", action="store_true")
    args = parser.parse_args()
    package_json_paths = list((args.package_root / "package_metadata").glob("C16_GPU_PACKAGE_*_MANIFEST.json"))
    if len(package_json_paths) != 1:
        raise ContractError("rolling package has no unique package manifest JSON")
    package = read_json(package_json_paths[0])
    if package.get("deployment_id") != args.deployment_id:
        raise ContractError("requested deployment differs from immutable package deployment")
    if not isinstance(package.get("model_revision"), str) or not isinstance(package.get("tokenizer_revision"), str):
        raise ContractError("immutable package does not close model/tokenizer revisions")
    scenario = read_scenario(args.package_root / "a_assets" / "SCENARIO_MATRIX.tsv", args.scenario_id)
    try:
        prefill_tokens = int(scenario["prefill_tokens"])
        decode_tokens = int(scenario["decode_tokens"])
        batch_size = int(scenario["batch_size"])
    except ValueError as exc:
        raise ContractError("immutable scenario has noninteger dimensions") from exc
    if args.input_class not in scenario["frozen_input_classes"].split(","):
        raise ContractError("chosen input class is outside this frozen scenario")
    if args.canary and (args.scenario_id, batch_size, prefill_tokens, decode_tokens, args.input_class) != ("S0", 1, 128, 4, "TEXT"):
        raise ContractError("C16 G0 canary must bind exactly S0/B1/T128/Decode4/TEXT")
    token_path = args.package_root / "a_assets" / "TOKEN_RECEIPTS" / args.deployment_id / f"{args.input_class}_T{prefill_tokens}.json"
    token_receipt = read_json(token_path)
    for field, expected in {
        "deployment_id": args.deployment_id,
        "model_revision": package.get("model_revision"),
        "input_class": args.input_class,
        "target_prefill_tokens": prefill_tokens,
    }.items():
        if token_receipt.get(field) != expected:
            raise ContractError(f"token receipt mismatch for {field}")
    token_ids = token_receipt.get("target_token_ids")
    if not isinstance(token_ids, list) or len(token_ids) != prefill_tokens or any(not isinstance(token, int) or token < 0 for token in token_ids):
        raise ContractError("token receipt target IDs are not an exact nonnegative frozen sequence")
    token_sha = hashlib.sha256(canonical_json(token_ids).encode("utf-8")).hexdigest()
    if token_sha != required_string(token_receipt, "target_token_ids_sha256"):
        raise ContractError("target token IDs do not match their immutable receipt SHA256")
    args.token_ids_output.parent.mkdir(parents=True, exist_ok=True)
    args.token_ids_output.write_text(canonical_json(token_ids) + "\n", encoding="utf-8")
    model_path = args.package_root / "models" / args.deployment_id
    if not model_path.is_dir():
        raise ContractError("immutable model directory is absent")
    receipt = {
        "schema_version": "C16_G_RUNTIME_FROZEN_BINDING_V1",
        "stage_id": "C16-1.2",
        "execution_mode": "LOCAL_FROZEN_INPUT_BINDING",
        "scientific_eligible": False,
        "package_id": package.get("package_id"),
        "package_manifest_sha256": sha256_file(package_json_paths[0]),
        "deployment_id": args.deployment_id,
        "model_id": required_string(token_receipt, "model_id"),
        "model_revision": package.get("model_revision"),
        "tokenizer_revision": package.get("tokenizer_revision"),
        "scenario": {
            "scenario_id": args.scenario_id,
            "batch_size": batch_size,
            "prefill_tokens": prefill_tokens,
            "decode_tokens": decode_tokens,
            "feature_policy": scenario["feature_policy"],
        },
        "input": {
            "class": args.input_class,
            "token_receipt_path": str(token_path),
            "token_receipt_sha256": sha256_file(token_path),
            "raw_input_sha256": required_string(token_receipt, "raw_sha256"),
            "target_token_ids_sha256": token_sha,
            "derived_token_ids_path": str(args.token_ids_output),
            "derived_token_ids_sha256": sha256_file(args.token_ids_output),
        },
        "model_path": str(model_path),
        "checks": {
            "no_tokenizer_execution": True,
            "no_context_resize": True,
            "canary_shape_exact": args.canary,
            "tokenizer_revision_bound_by_package_manifest": True,
        },
        "status": "FROZEN_RUNTIME_BINDING_READY",
    }
    atomic_json(args.binding_receipt, receipt)
    print(f"PASS C16 frozen runtime binding: {args.binding_receipt}")


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        print(f"FAIL C16 frozen runtime binding: {exc}", file=sys.stderr)
        raise SystemExit(2)
