#!/usr/bin/env python3
"""Revalidate a capture target against a second-pass catalog observation."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json, require_exact_keys


TARGET_FIELDS = (
    "run_id", "deployment_id", "scenario_id", "phase", "decode_step_bin", "device",
    "context", "stream", "correlation_id", "kernel_name", "implementation_key", "grid",
    "block", "operator_class", "layer_id", "shape_key", "dtype_key", "semantic_evidence",
)


def read_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"invalid identity JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError(f"identity JSON root is not an object: {path}")
    return value


def validate_target_pair(expected: dict[str, Any], observed: dict[str, Any]) -> dict[str, Any]:
    require_exact_keys(expected, TARGET_FIELDS, "requested target")
    require_exact_keys(observed, TARGET_FIELDS, "observed target")
    mismatches = {field: {"expected": expected[field], "observed": observed[field]} for field in TARGET_FIELDS if expected[field] != observed[field]}
    if mismatches:
        raise ContractError(f"target identity mismatch: {json.dumps(mismatches, sort_keys=True)}")
    return {
        "selection_key": {field: expected[field] for field in TARGET_FIELDS},
        "launch_ordinal": observed.get("launch_ordinal", "NOT_A_JOIN_KEY"),
        "identity_verified": True,
        "naked_launch_ordinal_join_forbidden": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--requested", type=Path, required=True)
    parser.add_argument("--observed", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    receipt = validate_target_pair(read_object(args.requested), read_object(args.observed))
    atomic_json(args.receipt, receipt)
    print(f"PASS C16 target second-pass identity guard: {args.receipt}")


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        print(f"FAIL C16 target identity guard: {exc}", file=sys.stderr)
        raise SystemExit(2)
