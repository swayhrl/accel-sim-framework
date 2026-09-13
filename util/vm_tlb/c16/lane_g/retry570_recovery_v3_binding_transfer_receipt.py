#!/usr/bin/env python3
"""Close copied frozen-runtime bindings without invoking a model or GPU."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json, sha256_file, valid_sha256


SCHEMA = "C16_G_RECOVERY_V3_BINDING_TRANSFER_RECEIPT_V1"


def read(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"invalid frozen binding: {path}") from exc
    if not isinstance(value, dict):
        raise ContractError("frozen binding must be a JSON object")
    return value


def validate_manifest(root: Path, manifest: Path, expected_sha: str) -> list[str]:
    if not valid_sha256(expected_sha) or sha256_file(manifest) != expected_sha:
        raise ContractError("remote manifest SHA did not survive copyback")
    names: list[str] = []
    for line in manifest.read_text(encoding="utf-8").splitlines():
        try:
            digest, name = line.split("  ", 1)
        except ValueError as exc:
            raise ContractError("malformed remote binding manifest") from exc
        if not valid_sha256(digest) or not name or name in names:
            raise ContractError("remote binding manifest is not a unique SHA set")
        payload = root / name
        if not payload.is_file() or sha256_file(payload) != digest:
            raise ContractError(f"copied binding payload mismatch: {name}")
        names.append(name)
    if not names:
        raise ContractError("remote binding manifest has no payloads")
    return names


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binding-root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--remote-manifest-sha256", required=True)
    parser.add_argument("--deployment-id", required=True)
    parser.add_argument("--package-commit", required=True)
    parser.add_argument("--package-manifest-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ContractError("binding-transfer receipt refuses to overwrite retained evidence")
    names = validate_manifest(args.binding_root, args.manifest, args.remote_manifest_sha256)
    binding_paths = sorted(args.binding_root.glob("*/BINDING.json"))
    bindings: list[dict[str, Any]] = []
    for path in binding_paths:
        value = read(path)
        scenario, input_value = value.get("scenario", {}), value.get("input", {})
        if value.get("status") != "FROZEN_RUNTIME_BINDING_READY" or value.get("deployment_id") != args.deployment_id:
            raise ContractError(f"invalid frozen binding status/identity: {path}")
        if value.get("package_fixed_commit") != args.package_commit or value.get("package_manifest_sha256") != args.package_manifest_sha256:
            raise ContractError(f"fixed package identity mismatch: {path}")
        token = Path(str(input_value.get("derived_token_ids_path", ""))).name
        expected = f"{path.parent.name}/token_ids.json"
        if expected not in names or token != "token_ids.json":
            raise ContractError(f"binding token payload is absent from closed manifest: {path}")
        bindings.append({"scenario_id": scenario.get("scenario_id"), "input_class": input_value.get("class"),
                         "binding_path": str(path), "binding_sha256": sha256_file(path),
                         "token_ids_sha256": input_value.get("derived_token_ids_sha256")})
    if not bindings or len({(row["scenario_id"], row["input_class"]) for row in bindings}) != len(bindings):
        raise ContractError("binding set is empty or has duplicate scenario/input identities")
    atomic_json(args.output, {"schema_version": SCHEMA, "status": "FROZEN_RUNTIME_BINDINGS_REMOTE_LOCAL_SHA_CLOSED",
                              "scientific_eligible": False, "deployment_id": args.deployment_id,
                              "package_commit": args.package_commit, "package_manifest_sha256": args.package_manifest_sha256,
                              "binding_root": str(args.binding_root), "remote_manifest": {"path": str(args.manifest), "sha256": args.remote_manifest_sha256},
                              "payload_count": len(names), "all_remote_local_payload_sha256_identical": True,
                              "bindings": bindings, "binding_count": len(bindings),
                              "model_execution": False, "gpu_used": False})
    print("PASS FROZEN_RUNTIME_BINDINGS_REMOTE_LOCAL_SHA_CLOSED")


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        raise SystemExit(f"FAIL Recovery-V3 binding transfer: {exc}")
