#!/usr/bin/env python3
"""Audit Recovery-V3 G1 claims without promoting incomplete profiler output."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from c16_native_common import atomic_json, sha256_file


SCHEMA = "C16_G_RECOVERY_V3_G1_AUTHORITY_AUDIT_V1"
ROWS = (
    ("Qwen0", "S1_CODE", "qwen2p5_0p5b", "PREVIOUSLY_CLAIMED_COMPLETE"),
    ("Qwen7-raw", "S2_TEXT", "qwen2p5_7b_raw", "PREVIOUSLY_CLAIMED_COMPLETE"),
    ("Qwen7-raw", "S2_CODE", "qwen2p5_7b_raw", "PREVIOUSLY_CLAIMED_COMPLETE"),
    ("Qwen7-raw", "S2_STRUCTURED", "qwen2p5_7b_raw", "PREVIOUSLY_CLAIMED_COMPLETE"),
)


def load(path: Path | None) -> dict[str, Any] | None:
    if path is None or not path.is_file():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return value if isinstance(value, dict) else None


def first(root: Path, pattern: str) -> Path | None:
    values = sorted(root.rglob(pattern)) if root.is_dir() else []
    return values[0] if values else None


def ref(path: Path | None) -> dict[str, Any]:
    return {"path": str(path) if path else "NA", "sha256": sha256_file(path) if path and path.is_file() else "NA"}


def audit_row(root: Path, model: str, scenario: str, tree: str, claimed: str) -> dict[str, Any]:
    location = root / "recovery_v3_runs" / tree / scenario
    native_path = first(location, "*NATIVE_RECEIPT.json")
    profile_path = first(location, "*G1*PROFILE*RECEIPT*.json")
    native, profile = load(native_path), load(profile_path)
    artifacts = profile.get("artifacts", {}) if profile else {}
    report_path = Path(artifacts["output_path"] + ".nsys-rep") if isinstance(artifacts.get("output_path"), str) else None
    if report_path is not None and not report_path.is_file():
        report_path = None
    catalog = first(location, "*CATALOG*.tsv")
    parent_path = first(location, "*G1*PARENT_LEASE.json")
    parent = load(parent_path)
    native_valid = bool(native and native.get("execution_mode") == "NATIVE_GPU" and native.get("scientific_eligible") is True and native.get("artifacts", {}).get("terminal_status") == "COMPLETE")
    profile_mode = profile.get("execution_mode", "NA") if profile else "NA"
    terminal = artifacts.get("terminal_status", "NA") if profile else "NA"
    parent_authority = bool(parent and isinstance(parent.get("ledger_path"), str) and "RECOVERY_V3_CAMPAIGN" in parent["ledger_path"])
    catalog_valid = bool(catalog and catalog.stat().st_size > 0)
    valid = native_valid and profile_mode == "NATIVE_GPU" and terminal == "COMPLETE" and report_path is not None and catalog_valid and parent_authority
    return {
        "model": model, "scenario": scenario, "previous_claimed_status": claimed,
        "native_baseline_valid": native_valid, "native_baseline_receipt": ref(native_path),
        "profile_receipt": ref(profile_path), "execution_mode": profile_mode,
        "terminal_status": terminal, "nsys_rep_exists": report_path is not None,
        "nsys_rep_bytes": report_path.stat().st_size if report_path else 0,
        "nsys_rep_sha256": sha256_file(report_path) if report_path else "NA",
        "catalog_exists": catalog is not None, "catalog_sha256": sha256_file(catalog) if catalog else "NA",
        "catalog_validation_status": "PRESENT_UNVALIDATED" if catalog_valid else "ABSENT_OR_EMPTY",
        "parent_lease_authority": "RECOVERY_V3_CAMPAIGN" if parent_authority else "MISSING_OR_NON_CAMPAIGN",
        "campaign_namespace": parent.get("ledger_path", "NA") if parent else "NA",
        "final_disposition": "G1_AUTHORITY_VALID" if valid else "SUPERSEDED_NON_AUTHORITATIVE_REQUIRES_CAMPAIGN_G1",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit("refuses to overwrite G1 authority audit")
    rows = [audit_row(args.runtime_root, *row) for row in ROWS]
    atomic_json(args.output, {"schema_version": SCHEMA, "status": "COMPLETE", "rows": rows,
                              "valid_row_count": sum(row["final_disposition"] == "G1_AUTHORITY_VALID" for row in rows),
                              "superseded_row_count": sum(row["final_disposition"] != "G1_AUTHORITY_VALID" for row in rows)})
    print(args.output)


if __name__ == "__main__":
    main()
