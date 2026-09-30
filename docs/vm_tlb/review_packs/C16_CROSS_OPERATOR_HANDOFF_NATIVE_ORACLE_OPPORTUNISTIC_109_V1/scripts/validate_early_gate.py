#!/usr/bin/env python3
"""CPU-only structural validator for a Lane 6 early native-oracle gate."""

import argparse
import hashlib
import json
from pathlib import Path
import re

REQUIRED = (
    "candidate_id", "DISCOVERY_TARGET", "VALIDATION_TARGET",
    "producer_identity", "intermediate_identity", "consumer_identity",
    "natural_scenario", "baseline_implementation", "oracle_conditions",
    "correctness_contract", "measurement_protocol", "STOP_rule",
    "expected_authority_hashes",
)
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--gate", type=Path, required=True)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    gate = json.loads(args.gate.read_text())
    missing = [key for key in REQUIRED if key not in gate]
    conditions = gate.get("oracle_conditions", {})
    missing_conditions = [key for key in ("B0", "O1") if key not in conditions]
    bad_hashes = {k: v for k, v in gate.get("expected_authority_hashes", {}).items()
                  if not isinstance(v, str) or not HEX64.fullmatch(v)}
    discovery = gate.get("DISCOVERY_TARGET")
    validation = gate.get("VALIDATION_TARGET")
    passed = not missing and not missing_conditions and not bad_hashes and discovery is not None and validation is not None
    result = {"status": "PASS_STRUCTURE_ONLY" if passed else "FAIL",
              "gate_sha256": sha(args.gate), "missing_fields": missing,
              "missing_conditions": missing_conditions, "invalid_sha256": bad_hashes,
              "candidate_id": gate.get("candidate_id"),
              "gpu_discovery_authorized": False,
              "note": "Structural pass never authorizes GPU; immutable commit/fetch-back and source feasibility are separate gates."}
    if args.output:
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))
    if not passed:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
