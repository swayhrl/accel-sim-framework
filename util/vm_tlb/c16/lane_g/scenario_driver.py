#!/usr/bin/env python3
"""Validate a frozen A-owned scenario before it becomes a native run request."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json, require_exact_keys


SCENARIO_FIELDS = (
    "scenario_id", "batch", "requested_prompt_tokens", "decode_tokens", "input_corpus_id",
    "input_hash", "seed", "prefix_caching", "speculative_decoding", "continuous_batching",
    "tensor_parallel", "pipeline_parallel", "expert_parallel",
)
DISABLED_FIELDS = ("prefix_caching", "speculative_decoding", "continuous_batching")


def read_scenario(path: Path) -> dict[str, Any]:
    try:
        scenario = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read frozen scenario JSON: {exc}") from exc
    if not isinstance(scenario, dict):
        raise ContractError("scenario JSON must be an object")
    return scenario


def validate_scenario(scenario: dict[str, Any], *, canary: bool) -> dict[str, Any]:
    require_exact_keys(scenario, SCENARIO_FIELDS, "scenario")
    if any(scenario[field] is not False for field in DISABLED_FIELDS):
        raise ContractError("first C16 scenario must explicitly disable prefix/speculative/continuous batching")
    if any(scenario[field] not in (0, "0", "NONE") for field in ("tensor_parallel", "pipeline_parallel", "expert_parallel")):
        raise ContractError("first C16 scenario must be single-GPU and no parallelism")
    if not isinstance(scenario["batch"], int) or scenario["batch"] < 1:
        raise ContractError("scenario batch must be a positive integer")
    if canary and (scenario["scenario_id"], scenario["batch"], scenario["requested_prompt_tokens"], scenario["decode_tokens"]) != ("S0", 1, 128, 4):
        raise ContractError("G0 canary must be the frozen S0 B1/T128/Decode4 scenario")
    return {
        "scenario": scenario,
        "scientific_eligible": True,
        "requires_a_fixed_commit_manifest": True,
        "runtime_mutation_forbidden": True,
    }


def fixture() -> dict[str, Any]:
    return {
        "scenario_id": "S0", "batch": 1, "requested_prompt_tokens": 128, "decode_tokens": 4,
        "input_corpus_id": "OFFLINE_FIXTURE_ONLY", "input_hash": "0" * 64, "seed": 0,
        "prefix_caching": False, "speculative_decoding": False, "continuous_batching": False,
        "tensor_parallel": 0, "pipeline_parallel": 0, "expert_parallel": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--scenario-json", type=Path)
    group.add_argument("--fixture", action="store_true", help="non-scientific C16-0.4 schema fixture")
    parser.add_argument("--canary", action="store_true")
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    scenario = fixture() if args.fixture else read_scenario(args.scenario_json)
    receipt = validate_scenario(scenario, canary=args.canary)
    if args.fixture:
        receipt["scientific_eligible"] = False
        receipt["fixture_only"] = True
    atomic_json(args.receipt, receipt)
    print(f"PASS C16 scenario driver: {args.receipt}")


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        print(f"FAIL C16 scenario driver: {exc}", file=sys.stderr)
        raise SystemExit(2)
