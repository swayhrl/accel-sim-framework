#!/usr/bin/env python3
"""Independently rehash a Pipeline V1 inbox bundle without admitting it."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

try:  # package import for tests
    from .receiver_common import AdmissionError, canonical_json_sha256, enumerate_regular_artifacts, load_json, sha256_file, utc_now, validate_manifest
    from .quarantine import quarantine_bundle
except ImportError:  # direct CLI execution
    from receiver_common import AdmissionError, canonical_json_sha256, enumerate_regular_artifacts, load_json, sha256_file, utc_now, validate_manifest
    from quarantine import quarantine_bundle


def verify_partial(root: Path, run_id: str) -> dict:
    partial = root / "inbox" / f"{run_id}.partial"
    manifest_path = partial / "RUN_MANIFEST.json"
    if not partial.is_dir() or partial.is_symlink():
        raise AdmissionError(f"partial bundle absent or invalid: {partial}")
    manifest = load_json(manifest_path)
    validate_manifest(manifest)
    if manifest["run_id"] != run_id:
        raise AdmissionError("RUN_ID does not match partial directory")
    expected = sorted(manifest["artifacts"], key=lambda item: item["relative_path"])
    actual = enumerate_regular_artifacts(partial)
    if expected != actual:
        raise AdmissionError("destination artifact inventory differs from source RUN_MANIFEST")
    return {
        "schema_version": 1,
        "run_id": run_id,
        "verification_status": "PASS",
        "verified_at_utc": utc_now(),
        "source_manifest_sha256": sha256_file(manifest_path),
        "source_manifest_canonical_sha256": canonical_json_sha256(manifest),
        "file_count": len(actual),
        "total_bytes": sum(item["size_bytes"] for item in actual),
        "artifacts": actual,
        "partial_path": str(partial),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output", type=Path, required=True, help="new receipt path; never overwritten")
    parser.add_argument("--quarantine-on-fail", action="store_true", help="move the unadmitted partial bundle into quarantine after a verification failure")
    args = parser.parse_args()
    try:
        receipt = verify_partial(args.root, args.run_id)
        if args.output.exists():
            raise AdmissionError(f"receipt already exists: {args.output}")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps({"verification_status": "PASS", "output": str(args.output)}, sort_keys=True))
        return 0
    except (AdmissionError, OSError) as exc:
        result = {"verification_status": "FAIL", "error": str(exc)}
        if args.quarantine_on_fail:
            partial = args.root / "inbox" / f"{args.run_id}.partial"
            try:
                result["quarantine_path"] = str(quarantine_bundle(args.root, partial, args.run_id, str(exc)))
            except (AdmissionError, OSError) as quarantine_error:
                result["quarantine_error"] = str(quarantine_error)
        print(json.dumps(result, sort_keys=True))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
