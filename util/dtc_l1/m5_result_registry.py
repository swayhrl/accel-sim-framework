#!/usr/bin/env python3
"""Maintain a compact, identity-keyed registry of validated M5 run summaries.

The runner-facing check is intentionally independent of a simulator log, so a
batch can skip a completed valid identity before launching it.  Registration
then binds that identity to the strict parser summary and its raw-log hash.
"""

import argparse
import hashlib
import json
from pathlib import Path


SCHEMA = "dtc_l1_m5_result_registry_v1"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def identity(args):
    value = {
        "core_sha": args.core_sha,
        "framework_sha": args.framework_sha,
        "config_sha256": sha256(args.config_file),
        "workload_id": args.workload_id,
        "workload_sha256": sha256(args.workload_file),
        "ptx_sha256": sha256(args.ptx_file),
        "input_sha256": [sha256(path) for path in args.input_file],
        "parser_schema": args.parser_schema,
    }
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return value, hashlib.sha256(encoded).hexdigest()


def load_registry(path):
    if not path.exists():
        return {"schema": SCHEMA, "results": []}
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("schema") != SCHEMA or not isinstance(value.get("results"), list):
        raise SystemExit("invalid M5 result registry: " + str(path))
    return value


def common_arguments(parser):
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--core-sha", required=True)
    parser.add_argument("--framework-sha", required=True)
    parser.add_argument("--config-file", type=Path, required=True)
    parser.add_argument("--workload-id", required=True)
    parser.add_argument("--workload-file", type=Path, required=True)
    parser.add_argument("--ptx-file", type=Path, required=True)
    parser.add_argument("--input-file", type=Path, action="append", default=[])
    parser.add_argument("--parser-schema", default="dtc_l1_summary_v1")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    command = parser.add_subparsers(dest="command", required=True)
    check = command.add_parser("check", help="exit 0 only for registered VALID identity")
    common_arguments(check)
    register = command.add_parser("register", help="append one VALID parsed result")
    common_arguments(register)
    register.add_argument("--summary", type=Path, required=True)
    register.add_argument("--raw-log", type=Path, required=True)
    register.add_argument("--result-classification", required=True)
    args = parser.parse_args()

    value, digest = identity(args)
    registry = load_registry(args.registry)
    existing = next(
        (entry for entry in registry["results"] if entry["identity_sha256"] == digest),
        None,
    )
    if args.command == "check":
        if existing and existing.get("status") == "VALID":
            print("VALID " + existing["result_id"])
            return
        print("MISSING " + digest)
        raise SystemExit(1)

    summary = json.loads(args.summary.read_text(encoding="utf-8"))
    if summary.get("schema") != args.parser_schema:
        raise SystemExit("summary parser schema differs from identity")
    provenance = summary.get("provenance", {})
    for key in ("core_sha", "framework_sha", "config_sha256", "workload_id", "workload_sha256"):
        if provenance.get(key) != value[key]:
            raise SystemExit("summary provenance mismatch: " + key)
    if existing:
        if existing.get("status") != "VALID":
            raise SystemExit("identity exists but is not VALID: " + existing["result_id"])
        print("REUSED " + existing["result_id"])
        return

    entry = {
        "result_id": "M5-" + digest[:16],
        "identity_sha256": digest,
        "identity": value,
        "status": "VALID",
        "result_classification": args.result_classification,
        "summary_path": str(args.summary),
        "summary_sha256": sha256(args.summary),
        "raw_log_path": str(args.raw_log),
        "raw_log_sha256": sha256(args.raw_log),
    }
    registry["results"].append(entry)
    registry["results"].sort(key=lambda item: item["result_id"])
    args.registry.write_text(json.dumps(registry, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("REGISTERED " + entry["result_id"])


if __name__ == "__main__":
    main()
